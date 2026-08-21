import json

from contact import canonical_clerical_record_diagnostic as subject


def provider(content: str):
    return 200, json.dumps({
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 9, "completion_tokens": 4},
    }).encode()


def request_record(body: bytes):
    envelope = json.loads(body)
    user = envelope["messages"][1]["content"]
    return envelope, user, json.loads(user.split("\n", 1)[1].rsplit("\n", 1)[0])


def state_for_device(device_id: str):
    return next(
        case.state
        for lineage in subject.LINEAGE_DATA.values()
        for case in lineage.cases.values()
        if case.state.device == device_id
    )


def fake_transport(body: bytes):
    envelope, user, record = request_record(body)
    if envelope["model"] == subject.learned.INSTRUMENT_MODEL:
        transcript = json.loads(record["normalized_sensory_transcript"])
        first_increases = (
            transcript["observed_actuator"] == "first"
        ) == (
            transcript["observed_effect"] == subject.learned.INCREASES
        )
        return provider(json.dumps({
            "first_control_effect": (
                subject.learned.INCREASES if first_increases else subject.learned.DECREASES
            ),
            "second_control_effect": (
                subject.learned.DECREASES if first_increases else subject.learned.INCREASES
            ),
        }))

    device = record["device"]
    state = state_for_device(device["device"])
    material = record["retained_material"]
    action = state.controls[0]
    if material.startswith("The first displayed control") and "\n" not in material:
        first_increases = "first displayed control increases" in material
        wants_increase = state.target > state.position
        action = state.controls[0 if wants_increase == first_increases else 1]
    return provider(json.dumps({"action": action}))


def test_source_is_verified_and_schedule_is_frozen():
    artifacts = subject.load_source_artifacts()
    assert all(set(value["transcriptions"]) == {"a", "b"} for value in artifacts.values())
    assert all(set(value["normalizations"]) == set(subject.CASES) for value in artifacts.values())
    assert subject.PLANNED_LOGICAL_CALLS == 340
    assert subject.PHYSICAL_CALL_CEILING == 348
    assert len(subject.schedule()) == 336


def test_record_request_contains_no_participant_action_fields():
    artifacts = subject.load_source_artifacts()
    lineage = subject.LINEAGE_DATA[subject.LINEAGES[0]]
    transcription = artifacts[lineage.name]["transcriptions"]["a"]
    envelope, _, record = request_record(subject.record_body(transcription))
    assert envelope["model"] == subject.learned.INSTRUMENT_MODEL
    assert record == {"normalized_sensory_transcript": transcription}
    record_bytes = subject.base.canonical_json_bytes(record).decode()
    for case in lineage.cases.values():
        assert case.state.device not in record_bytes
        assert all(control not in record_bytes for control in case.state.controls)
        assert str(case.state.target) not in record_bytes


def test_fake_diagnostic_reaches_pipeline_candidate():
    packet = subject.execute(fake_transport)
    assert packet["logical_calls"] == 340
    assert packet["physical_attempts"] == 340
    assert packet["canonical_records"]["exact"] == 4
    assert packet["canonical_records"]["rendered_exact"] == 4
    assert packet["normalized_selection"]["exact"] == 10
    assert packet["normalized_selection"]["false_selections"] == 0
    assert packet["matching_scores"][subject.NORMALIZED_RENDERED] == 28
    assert packet["matching_scores"][subject.ORACLE_STATIC] == 32
    assert packet["instrument_verdict"]["class"] == "pipeline_candidate"
    assert packet["formation_verdict"] is None


def test_exact_replay(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet


def test_invalid_record_is_not_resampled():
    record_calls = 0

    def invalid_transport(body: bytes):
        nonlocal record_calls
        envelope = json.loads(body)
        if envelope["model"] == subject.learned.INSTRUMENT_MODEL:
            record_calls += 1
            return provider('{"first_control_effect":"unknown"}')
        return fake_transport(body)

    packet = subject.execute(invalid_transport)
    assert record_calls == 4
    assert packet["canonical_records"]["exact"] == 0
    assert packet["retries"] == 0
    assert packet["instrument_verdict"]["class"] == "null"


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
