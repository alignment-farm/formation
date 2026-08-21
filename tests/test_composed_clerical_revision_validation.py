import json

from contact import composed_clerical_revision_validation as subject


def provider(content: str):
    return 200, json.dumps({
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 15, "completion_tokens": 5},
    }).encode()


def request_record(body: bytes):
    envelope = json.loads(body)
    user = envelope["messages"][1]["content"]
    return envelope, user, json.loads(user.split("\n", 1)[1].rsplit("\n", 1)[0])


def scope_for_description(description: str):
    for lineage in subject.LINEAGE_DATA.values():
        for design in lineage.designs.values():
            if description in {design.source_description, design.later_description}:
                return {"beacon_class": design.beacon, "housing_class": design.housing}
        for case in lineage.post_cases.values():
            if case.description == description:
                return case.scope
    raise AssertionError(description)


def state_for_device(device_id: str):
    for lineage in subject.LINEAGE_DATA.values():
        for state in (*lineage.old_sources.values(), *lineage.counter_sources.values()):
            if state.device == device_id:
                return state
        for case in (*lineage.pre_cases.values(), *lineage.post_cases.values()):
            if case.state.device == device_id:
                return case.state
    raise AssertionError(device_id)


def fake_transport(body: bytes):
    envelope, user, record = request_record(body)
    if envelope["model"] == subject.learned.INSTRUMENT_MODEL:
        if user.startswith("SENSORY REPORT"):
            selected = "first" if "first displayed" in record["actuator_report"] else "second"
            observed = (
                subject.learned.INCREASES if "rose" in record["gauge_report"]
                else subject.learned.DECREASES if "fell" in record["gauge_report"]
                else "unavailable"
            )
            return provider(json.dumps({
                "observed_actuator": selected,
                "observed_effect": observed,
                "scope": scope_for_description(record["device_report"]),
            }))
        if user.startswith("RECORD REQUEST"):
            transcript = json.loads(record["normalized_sensory_transcript"])
            if transcript["observed_effect"] not in {subject.learned.INCREASES, subject.learned.DECREASES}:
                return provider("No complete effect account.")
            first_increases = (transcript["observed_actuator"] == "first") == (transcript["observed_effect"] == subject.learned.INCREASES)
            first = "increases" if first_increases else "decreases"
            second = "decreases" if first_increases else "increases"
            return provider(f"The second displayed control {second} position. The first displayed control {first} position.")
        if user.startswith("PROSE PARSE REQUEST"):
            parsed = subject.prose_parser.parse_explicit_sentence(record["explicit_effect_account"])
            return provider(json.dumps(parsed))
        if user.startswith("FIELD PROJECTION REQUEST"):
            field = f"{record['observed_actuator']}_control_effect"
            effect = record["proposed_effect_record"].get(field)
            return provider(json.dumps({"claimed_selected_effect": effect}))
        if user.startswith("NORMALIZATION REQUEST"):
            return provider(json.dumps({"scope": scope_for_description(record["current_device_description"])}))
        raise AssertionError(user)
    state = state_for_device(record["device"]["device"])
    material = record["retained_material"]
    action = state.controls[0]
    if material.startswith("The first displayed control") and "\n" not in material:
        first_increases = "first displayed control increases" in material
        wants_increase = state.target > state.position
        action = state.controls[0 if wants_increase == first_increases else 1]
    return provider(json.dumps({"action": action}))


def test_frozen_schedule_and_fresh_lineages():
    assert subject.PLANNED_LOGICAL_CALLS == 768
    assert subject.PHYSICAL_CALL_CEILING == 780
    assert len(subject.pre_schedule()) == 48
    assert len(subject.post_schedule()) == 576
    assert set(subject.LINEAGE_DATA) == set(subject.LINEAGES)
    lineage = subject.LINEAGE_DATA[subject.LINEAGES[0]]
    record = subject.canonical.expected_record(lineage.designs["a"])
    body = subject.projector_body("first", record)
    _, user, request = request_record(body)
    assert set(request) == {"observed_actuator", "proposed_effect_record"}
    for case in lineage.post_cases.values():
        assert case.state.device not in user
        assert all(control not in user for control in case.state.controls)
        assert str(case.state.target) not in user


def test_fake_validation_is_supported_and_quarantines_controls():
    packet = subject.execute(fake_transport)
    assert packet["logical_calls"] == 768
    assert packet["physical_attempts"] == 768
    assert packet["components"]["exact_old_records"] == 8
    assert packet["components"]["prechange_correct_actions"] == 48
    assert packet["components"]["counter_actions_old_policy_consistent"] == 8
    assert packet["components"]["counter_actions_contradicting_old_records"] == 8
    assert packet["components"]["exact_revised_records"] == 8
    assert packet["components"]["exact_revised_projections"] == 8
    assert packet["admission_counts"]["old"]["admitted"] == 8
    assert packet["admission_counts"]["revised"]["admitted"] == 8
    assert packet["admission_counts"]["stale"]["quarantined"] == 8
    assert packet["admission_counts"]["hidden"]["quarantined"] == 8
    assert packet["matching_scores"][subject.ADMITTED] == 48
    assert packet["matching_scores"][subject.STALE] == 0
    assert packet["matching_scores"][subject.HIDDEN] == 0
    assert packet["matching_scores"][subject.SUPPLIED] == 48
    assert packet["validation_verdict"]["class"] == "supported"
    assert packet["formation_verdict"] is None
    assert all(
        set(lineage[position]) == {"old", "revised", "stale", "hidden"}
        for lineage in packet["proposals"].values()
        for position in subject.DESIGN_POSITIONS
    )


def test_exact_replay_and_recorder_restoration(tmp_path):
    old_ceiling = subject.verifier.PHYSICAL_CALL_CEILING
    old_retries = subject.verifier.MAX_RETRIES
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet
    assert subject.verifier.PHYSICAL_CALL_CEILING == old_ceiling
    assert subject.verifier.MAX_RETRIES == old_retries


def test_default_cli_makes_no_contact(monkeypatch, capsys):
    monkeypatch.setattr(subject.learned, "collect_provider_receipt", lambda: (_ for _ in ()).throw(AssertionError("contact")))
    assert subject.main([]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["side_effects_entered"] is False
