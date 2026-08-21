import json

from contact import learned_clerical_instrument_validation as subject


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
                return {
                    "beacon_class": design.beacon,
                    "housing_class": design.housing,
                }
        for case in lineage.cases.values():
            if case.description == description:
                return case.scope
    raise AssertionError(description)


def state_for_device(device_id: str):
    for lineage in subject.LINEAGE_DATA.values():
        for state in lineage.acquisitions.values():
            if state.device == device_id:
                return state
        for case in lineage.cases.values():
            if case.state.device == device_id:
                return case.state
    raise AssertionError(device_id)


def fake_transport(body: bytes):
    envelope, user, record = request_record(body)
    if envelope["model"] == subject.learned.INSTRUMENT_MODEL:
        if user.startswith("SENSORY REPORT"):
            observed = (
                subject.learned.INCREASES
                if "rose" in record["gauge_report"]
                else subject.learned.DECREASES
                if "fell" in record["gauge_report"]
                else "unavailable"
            )
            selected = (
                "first" if "first displayed" in record["actuator_report"] else "second"
            )
            return provider(json.dumps({
                "observed_actuator": selected,
                "observed_effect": observed,
                "scope": scope_for_description(record["device_report"]),
            }))
        if user.startswith("RECORD REQUEST"):
            transcript = json.loads(record["normalized_sensory_transcript"])
            if transcript.get("observed_effect") not in {
                subject.learned.INCREASES, subject.learned.DECREASES
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


def test_frozen_schedule_balance_and_information_separation():
    assert subject.PLANNED_LOGICAL_CALLS == 728
    assert subject.PHYSICAL_CALL_CEILING == 740
    assert len(subject.later_schedule()) == 648
    for feature_position in subject.DESIGN_POSITIONS:
        slots = [
            lineage.designs[feature_position].increasing_slot
            for lineage in subject.LINEAGE_DATA.values()
        ]
        assert slots.count(subject.FIRST_INCREASES) == 2
        assert slots.count(subject.SECOND_INCREASES) == 2

    lineage = subject.LINEAGE_DATA[subject.LINEAGES[0]]
    report = {
        "actuator_report": "The first displayed actuator was engaged.",
        "device_report": lineage.designs["a"].source_description,
        "gauge_report": "The position gauge rose by one mark.",
    }
    envelope, _, record = request_record(subject.staged.transcription_body(report))
    assert envelope["model"] == subject.learned.INSTRUMENT_MODEL
    encoded = subject.base.canonical_json_bytes(record).decode()
    for case in lineage.cases.values():
        assert case.state.device not in encoded
        assert all(control not in encoded for control in case.state.controls)
        assert str(case.state.target) not in encoded


def test_fake_validation_is_supported():
    packet = subject.execute(fake_transport)
    assert packet["logical_calls"] == 728
    assert packet["physical_attempts"] == 728
    assert packet["components"]["exposed_exact_transcriptions"] == 8
    assert packet["components"]["exposed_exact_prose"] == 8
    assert packet["components"]["exposed_exact_records"] == 8
    assert packet["components"]["exposed_exact_rendered"] == 8
    assert packet["components"]["hidden_exact_records"] == 0
    assert packet["components"]["later_exact_normalizations"] == 24
    assert packet["normalized_selection"]["exact"] == 24
    assert packet["normalized_selection"]["false_selections"] == 0
    assert packet["matching_scores"][subject.FULL] == 48
    assert packet["matching_scores"][subject.ORACLE_STATIC] == 48
    assert packet["instrument_verdict"]["class"] == "supported"
    assert packet["formation_verdict"] is None


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
