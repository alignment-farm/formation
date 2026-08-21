import json

import pytest

from contact import selective_longer_lineage_revision as subject


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
    for name, continuation in subject.LINEAGE_DATA.items():
        parent = subject.PARENT_LINEAGES[name]
        for design in parent.designs.values():
            if description in {design.source_description, design.later_description}:
                return {"beacon_class": design.beacon, "housing_class": design.housing}
        for case in (*continuation.pre_cases.values(), *continuation.post_cases.values()):
            if case.description == description:
                return case.scope
    raise AssertionError(description)


def state_for_device(device_id: str):
    for continuation in subject.LINEAGE_DATA.values():
        if continuation.third_source.device == device_id:
            return continuation.third_source
        for case in (*continuation.pre_cases.values(), *continuation.post_cases.values()):
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
            if transcript["observed_effect"] not in {
                subject.learned.INCREASES,
                subject.learned.DECREASES,
            }:
                return provider("No complete effect account.")
            first_increases = (
                (transcript["observed_actuator"] == "first")
                == (transcript["observed_effect"] == subject.learned.INCREASES)
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
        if user.startswith("FIELD PROJECTION REQUEST"):
            field = f"{record['observed_actuator']}_control_effect"
            effect = record["proposed_effect_record"].get(field)
            return provider(json.dumps({"claimed_selected_effect": effect}))
        if user.startswith("NORMALIZATION REQUEST"):
            return provider(json.dumps({
                "scope": scope_for_description(record["current_device_description"]),
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


def test_parent_binding_fresh_cases_and_schedule():
    _, retained = subject.load_parent()
    specimen = subject.specimen()
    assert specimen["parent_packet_sha256"] == subject.PARENT_PACKET_SHA256
    assert len(subject.pre_schedule()) == 48
    assert len(subject.post_schedule()) == 576
    assert subject.PLANNED_LOGICAL_CALLS == 688
    assert subject.PHYSICAL_CALL_CEILING == 700
    for name in subject.LINEAGES:
        parent = subject.PARENT_LINEAGES[name]
        assert retained[name]["a"]["version"] == 2
        assert retained[name]["a"]["record"] != subject.canonical.expected_record(
            parent.designs["a"]
        )
        for case in subject.LINEAGE_DATA[name].post_cases.values():
            assert case.state.device not in {
                prior.state.device
                for prior in parent.post_cases.values()
            }


def test_fake_continuation_is_supported_and_selective():
    packet = subject.execute(fake_transport)
    assert packet["logical_calls"] == 688
    assert packet["physical_attempts"] == 688
    assert packet["components"] == {
        "counteractions_contradicting_version_2": 4,
        "counteractions_version_2_policy_consistent": 4,
        "current_version_assignments_exact": 72,
        "exact_later_normalizations": 24,
        "exact_third_version_projections": 4,
        "exact_third_version_records": 4,
        "parent_admitted_version_2_records": 8,
        "precontinuation_correct_actions": 48,
    }
    assert packet["admission_counts"]["revised"]["admitted"] == 4
    assert packet["admission_counts"]["stale"]["quarantined"] == 4
    assert packet["admission_counts"]["hidden"]["quarantined"] == 4
    assert packet["matching_scores"][subject.CURRENT] == 48
    assert packet["design_scores"][subject.CURRENT] == {"a": 24, "b": 24}
    assert packet["matching_scores"][subject.REMOVED] == 24
    assert packet["normalized_selection"] == {
        "exact": 24, "false_selections": 0, "total": 24,
    }
    assert packet["validation_verdict"]["class"] == "supported"
    assert packet["formation_verdict"] is None


def test_parent_hash_mismatch_refuses(monkeypatch):
    monkeypatch.setattr(subject, "PARENT_PACKET_SHA256", "0" * 64)
    with pytest.raises(subject.ContinuationRefusal, match="parent_packet_hash_mismatch"):
        subject.load_parent()


def test_exact_replay(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet


def test_default_cli_makes_no_contact(monkeypatch, capsys):
    monkeypatch.setattr(
        subject.learned,
        "collect_provider_receipt",
        lambda: (_ for _ in ()).throw(AssertionError("contact")),
    )
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out)["side_effects_entered"] is False
