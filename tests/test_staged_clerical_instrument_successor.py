import json

from contact import staged_clerical_instrument_successor as subject


def provider(content: str):
    return 200, json.dumps({
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 13, "completion_tokens": 5},
    }).encode()


def request_record(body: bytes):
    envelope = json.loads(body)
    user = envelope["messages"][1]["content"]
    return envelope, user, json.loads(user.split("\n", 1)[1].rsplit("\n", 1)[0])


def design_for_description(description: str):
    return next(
        design
        for designs in subject.learned.DESIGN_SETS
        for design in designs.values()
        if design.source_description == description
    )


def scope_for_description(description: str):
    for lineage in subject.LINEAGE_DATA.values():
        for design in lineage.designs.values():
            if description in {design.source_description, design.later_description}:
                return {
                    "beacon_class": design.beacon,
                    "housing_class": design.housing,
                }
        for later in lineage.cases.values():
            if later.description == description:
                return later.scope
    raise AssertionError(description)


def state_for_device(device_id: str):
    for lineage in subject.LINEAGE_DATA.values():
        for state in lineage.acquisitions.values():
            if state.device == device_id:
                return state
        for later in lineage.cases.values():
            if later.state.device == device_id:
                return later.state
    raise AssertionError(device_id)


def fake_transport(body: bytes):
    envelope, user, record = request_record(body)
    if envelope["model"] == subject.learned.INSTRUMENT_MODEL:
        if user.startswith("SENSORY REPORT"):
            selected = "first" if "first displayed" in record["actuator_report"] else "second"
            observed = (
                subject.learned.INCREASES
                if "rose" in record["gauge_report"]
                else subject.learned.DECREASES
            )
            return provider(json.dumps({
                "observed_actuator": selected,
                "observed_effect": observed,
                "scope": scope_for_description(record["device_report"]),
            }))
        if user.startswith("RECORD REQUEST"):
            transcript = json.loads(record["normalized_sensory_transcript"])
            first_increases = (
                transcript["observed_actuator"] == "first"
            ) == (
                transcript["observed_effect"] == subject.learned.INCREASES
            )
            design = type("DesignView", (), {
                "increasing_slot": (
                    subject.FIRST_INCREASES if first_increases else subject.SECOND_INCREASES
                )
            })()
            return provider(subject.expected_sentence(design))
        if user.startswith("NORMALIZATION REQUEST"):
            return provider(json.dumps({
                "scope": scope_for_description(record["current_device_description"])
            }))
        current_scope = scope_for_description(record["current_device_description"])
        selected = [
            row["record_id"]
            for row in record["record_scope_catalog"]
            if row["scope"] == current_scope
        ]
        return provider(json.dumps({"applicable_record_ids": selected}))

    device = record["device"]
    state = state_for_device(device["device"])
    material = record["retained_material"]
    action = state.controls[0]
    if material.startswith("The first displayed control") and "\n" not in material:
        first_increases = "first displayed control increases" in material
        wants_increase = state.target > state.position
        action = state.controls[0 if wants_increase == first_increases else 1]
    return provider(json.dumps({"action": action}))


def test_frozen_counts_and_information_separation():
    assert subject.PLANNED_LOGICAL_CALLS == 420
    assert subject.PHYSICAL_CALL_CEILING == 428
    assert len(subject.classification_schedule()) == 24
    assert len(subject.later_schedule()) == 384

    lineage = subject.LINEAGE_DATA[subject.LINEAGES[0]]
    design = lineage.designs["a"]
    report = {
        "actuator_report": "The first displayed actuator was engaged.",
        "device_report": design.source_description,
        "gauge_report": "The position gauge rose by one mark.",
    }
    encoder_envelope, _, encoder_record = request_record(
        subject.transcription_body(report)
    )
    assert encoder_envelope["model"] == subject.learned.INSTRUMENT_MODEL
    assert encoder_record == report
    source = lineage.acquisitions["a"]
    encoded_bytes = subject.base.canonical_json_bytes(encoder_record).decode()
    forbidden = {source.controller_family, source.device, *source.controls, str(source.target)}
    assert all(value not in encoded_bytes for value in forbidden)

    later = lineage.cases["a_up"]
    normalizer_envelope, _, normalizer_record = request_record(
        subject.normalizer_body(later.description)
    )
    assert normalizer_envelope["model"] == subject.learned.INSTRUMENT_MODEL
    normalizer_bytes = subject.base.canonical_json_bytes(normalizer_record).decode()
    assert later.state.device not in normalizer_bytes
    assert all(control not in normalizer_bytes for control in later.state.controls)
    assert str(later.state.target) not in normalizer_bytes
    assert subject.learned.INCREASES not in normalizer_bytes


def test_fake_successor_reaches_pipeline_candidate():
    packet = subject.execute(fake_transport)
    assert packet["logical_calls"] == 420
    assert packet["physical_attempts"] == 420
    assert packet["encoding"]["exact_transcriptions"] == 4
    assert packet["encoding"]["exact_sentences"] == 4
    assert packet["normalization"]["exact"] == 12
    assert packet["selection_scores"]["normalized_model_scopes"]["exact"] == 12
    assert packet["matching_scores"][subject.NORMALIZED_PIPELINE] == 32
    assert packet["matching_scores"][subject.ORACLE_STATIC] == 32
    assert packet["instrument_verdict"]["class"] == "pipeline_candidate"
    assert packet["formation_verdict"] is None


def test_exact_replay(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet


def test_invalid_normalization_is_retained_without_resampling():
    normalization_calls = 0

    def invalid_transport(body: bytes):
        nonlocal normalization_calls
        envelope = json.loads(body)
        user = envelope["messages"][1]["content"]
        if user.startswith("NORMALIZATION REQUEST"):
            normalization_calls += 1
            return provider('{"scope":{"unknown":"value"}}')
        return fake_transport(body)

    packet = subject.execute(invalid_transport)
    rows = [
        row for row in packet["calls"]
        if row["responsibility"] == "later_scope_normalization"
    ]
    assert normalization_calls == 12
    assert len(rows) == 12
    assert all(not row["valid"] for row in rows)
    assert packet["retries"] == 0
    assert packet["instrument_verdict"]["class"] == "encoding_only"


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
