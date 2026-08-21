import json

from contact import clerical_prose_parser_diagnostic as subject


def provider(content: str):
    return 200, json.dumps({
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 8, "completion_tokens": 4},
    }).encode()


def request_record(body: bytes):
    envelope = json.loads(body)
    user = envelope["messages"][1]["content"]
    return envelope, json.loads(user.split("\n", 1)[1].rsplit("\n", 1)[0])


def state_for_device(device_id: str):
    return next(
        case.state
        for lineage in subject.LINEAGE_DATA.values()
        for case in lineage.cases.values()
        if case.state.device == device_id
    )


def fake_transport(body: bytes):
    envelope, record = request_record(body)
    if envelope["model"] == subject.learned.INSTRUMENT_MODEL:
        parsed = subject.parse_explicit_sentence(record["explicit_effect_account"])
        return provider(json.dumps(parsed))
    state = state_for_device(record["device"]["device"])
    material = record["retained_material"]
    action = state.controls[0]
    if material.startswith("The first displayed control") and "\n" not in material:
        first_increases = "first displayed control increases" in material
        wants_increase = state.target > state.position
        action = state.controls[0 if wants_increase == first_increases else 1]
    return provider(json.dumps({"action": action}))


def test_source_sentences_are_explicit_and_schedule_is_frozen():
    artifacts = subject.load_source_artifacts()
    assert subject.PLANNED_LOGICAL_CALLS == 340
    assert subject.PHYSICAL_CALL_CEILING == 348
    assert all(
        subject.parse_explicit_sentence(sentence) is not None
        for artifact in artifacts.values()
        for sentence in artifact["transcriptions"].values()
    )


def test_parser_request_has_no_participant_action_fields():
    artifacts = subject.load_source_artifacts()
    lineage = subject.LINEAGE_DATA[subject.LINEAGES[0]]
    sentence = artifacts[lineage.name]["transcriptions"]["a"]
    envelope, record = request_record(subject.parser_body(sentence))
    assert envelope["model"] == subject.learned.INSTRUMENT_MODEL
    assert record == {"explicit_effect_account": sentence}
    record_bytes = subject.base.canonical_json_bytes(record).decode()
    for case in lineage.cases.values():
        assert case.state.device not in record_bytes
        assert all(control not in record_bytes for control in case.state.controls)
        assert str(case.state.target) not in record_bytes


def test_fake_parser_reaches_pipeline_candidate_and_restores_wrapped_module():
    old_protocol = subject.canonical.PROTOCOL_VERSION
    old_data = subject.canonical.LINEAGE_DATA
    packet = subject.execute(fake_transport)
    assert subject.canonical.PROTOCOL_VERSION == old_protocol
    assert subject.canonical.LINEAGE_DATA is old_data
    assert packet["logical_calls"] == 340
    assert packet["parser_records"]["exact"] == 4
    assert packet["parser_records"]["rendered_exact"] == 4
    assert packet["normalized_selection"]["exact"] == 10
    assert packet["normalized_selection"]["false_selections"] == 0
    assert packet["matching_scores"][subject.canonical.NORMALIZED_RENDERED] == 28
    assert packet["instrument_verdict"]["class"] == "pipeline_candidate"
    assert packet["instrument_verdict"]["scope"] == "clerical_prose_parser_diagnostic"
    assert packet["formation_verdict"] is None


def test_exact_replay(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet


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
