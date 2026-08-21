import json

from contact import learned_clerical_revision_exploration as subject


def provider(content: str):
    return 200, json.dumps({
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 15, "completion_tokens": 5},
    }).encode()


def request_record(body: bytes):
    envelope = json.loads(body)
    user = envelope["messages"][1]["content"]
    record = json.loads(user.split("\n", 1)[1].rsplit("\n", 1)[0])
    return envelope, user, record


def scope_for_description(description: str):
    for lineage in subject.LINEAGE_DATA.values():
        for design in lineage.designs.values():
            if description in {design.source_description, design.later_description}:
                return {
                    "beacon_class": design.beacon,
                    "housing_class": design.housing,
                }
        for case in lineage.post_cases.values():
            if case.description == description:
                return case.scope
    raise AssertionError(description)


def state_for_device(device_id: str):
    for lineage in subject.LINEAGE_DATA.values():
        for state in lineage.old_sources.values():
            if state.device == device_id:
                return state
        for case in lineage.pre_cases.values():
            if case.state.device == device_id:
                return case.state
        for state in lineage.counter_sources.values():
            if state.device == device_id:
                return state
        for case in lineage.post_cases.values():
            if case.state.device == device_id:
                return case.state
    raise AssertionError(device_id)


def fake_transport(body: bytes):
    envelope, user, record = request_record(body)
    if envelope["model"] == subject.learned.INSTRUMENT_MODEL:
        if user.startswith("SENSORY REPORT"):
            selected = (
                "first" if "first displayed" in record["actuator_report"] else "second"
            )
            observed = (
                subject.learned.INCREASES
                if "rose" in record["gauge_report"]
                else subject.learned.DECREASES
                if "fell" in record["gauge_report"]
                else "unavailable"
            )
            return provider(json.dumps({
                "observed_actuator": selected,
                "observed_effect": observed,
                "scope": scope_for_description(record["device_report"]),
            }))
        if user.startswith("RECORD REQUEST"):
            transcript = json.loads(record["normalized_sensory_transcript"])
            if transcript["observed_effect"] not in {
                subject.learned.INCREASES,
                subject.learned.DECREASES,
            }:
                return provider("No complete effect account.")
            first_increases = (
                transcript["observed_actuator"] == "first"
            ) == (
                transcript["observed_effect"] == subject.learned.INCREASES
            )
            first = "increases" if first_increases else "decreases"
            second = "decreases" if first_increases else "increases"
            return provider(
                f"The second displayed control {second} position. "
                f"The first displayed control {first} position."
            )
        if user.startswith("PROSE PARSE REQUEST"):
            parsed = subject.prose_parser.parse_explicit_sentence(
                record["explicit_effect_account"]
            )
            return provider(json.dumps(parsed))
        if user.startswith("NORMALIZATION REQUEST"):
            return provider(json.dumps({
                "scope": scope_for_description(record["current_device_description"])
            }))
        raise AssertionError(user)

    state = state_for_device(record["device"]["device"])
    material = record["retained_material"]
    action = state.controls[0]
    if material.startswith("The first displayed control") and "\n" not in material:
        first_increases = "first displayed control increases" in material
        wants_increase = state.target > state.position
        action = state.controls[0 if wants_increase == first_increases else 1]
    return provider(json.dumps({"action": action}))


def test_frozen_schedule_version_selection_and_information_separation():
    assert subject.PLANNED_LOGICAL_CALLS == 404
    assert subject.PHYSICAL_CALL_CEILING == 412
    assert len(subject.pre_schedule()) == 24
    assert len(subject.post_schedule()) == 324

    lineage = subject.LINEAGE_DATA[subject.LINEAGES[0]]
    selected = [lineage.record_ids["a"]]
    old = {"a": "old", "b": "old-b"}
    new = {"a": "new", "b": "new-b"}
    incomplete = {"a": "", "b": ""}
    assert subject.newest_eligible_sentence(
        lineage, selected, ((1, old), (2, new))
    ) == "new"
    assert subject.newest_eligible_sentence(
        lineage, selected, ((1, old), (2, incomplete))
    ) == "old"

    report = {
        "actuator_report": "The first displayed actuator was engaged.",
        "device_report": lineage.designs["a"].source_description,
        "gauge_report": "The position gauge fell by one mark.",
    }
    envelope, _, record = request_record(subject.staged.transcription_body(report))
    assert envelope["model"] == subject.learned.INSTRUMENT_MODEL
    encoded = subject.base.canonical_json_bytes(record).decode()
    for case in lineage.post_cases.values():
        assert case.state.device not in encoded
        assert all(control not in encoded for control in case.state.controls)
        assert str(case.state.target) not in encoded


def test_fake_revision_reaches_candidate_with_old_lineage_preserved():
    packet = subject.execute(fake_transport)
    assert packet["logical_calls"] == 404
    assert packet["physical_attempts"] == 404
    assert packet["components"]["exact_old_records"] == 4
    assert packet["components"]["prechange_correct_actions"] == 24
    assert packet["components"]["counter_actions_old_policy_consistent"] == 4
    assert packet["components"]["counter_actions_contradicting_old_records"] == 4
    assert packet["components"]["exact_revised_records"] == 4
    assert packet["components"]["exact_hidden_revision_records"] == 0
    assert packet["components"]["exact_later_normalizations"] == 12
    assert packet["normalized_selection"] == {
        "exact": 12,
        "false_selections": 0,
        "total": 12,
    }
    assert packet["matching_scores"][subject.REVISED] == 24
    assert packet["matching_scores"][subject.STALE] == 0
    assert packet["matching_scores"][subject.HIDDEN] == 0
    assert packet["matching_scores"][subject.REMOVED] == 0
    assert packet["matching_scores"][subject.SUPPLIED] == 24
    assert packet["revision_verdict"]["class"] == "revision_candidate"
    assert packet["formation_verdict"] is None

    for lineage_versions in packet["record_versions"].values():
        for versions in lineage_versions.values():
            assert [item["version"] for item in versions] == [1, 2]
            assert versions[1]["supersedes_record_version_id"] == versions[0]["record_version_id"]
            assert versions[0]["record"] is not None
            assert versions[1]["record"] is not None
            assert versions[0]["source_occurrence"]["responsibility"] == "old_source_action"
            assert versions[1]["source_occurrence"]["responsibility"] == "counter_action"


def test_exact_replay_and_global_restoration(tmp_path):
    old_ceiling = subject.prior.PHYSICAL_CALL_CEILING
    old_retries = subject.prior.MAX_RETRIES
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet
    assert subject.prior.PHYSICAL_CALL_CEILING == old_ceiling
    assert subject.prior.MAX_RETRIES == old_retries


def test_default_cli_makes_no_contact(monkeypatch, capsys):
    monkeypatch.setattr(
        subject.learned,
        "collect_provider_receipt",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("contact")),
    )
    assert subject.main([]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["mode"] == "smoke_no_contact"
    assert output["side_effects_entered"] is False
