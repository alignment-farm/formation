import json

from contact import representation_consumption_calibration as subject


def provider(content):
    return 200, json.dumps({
        "choices": [{"message": {"content": content}}],
        "usage": {"completion_tokens": 3, "prompt_tokens": 11},
    }).encode()


def request_record(body):
    envelope = json.loads(body)
    return json.loads(envelope["messages"][1]["content"].split("\n", 1)[1].rsplit("\n", 1)[0])


def fake_transport(body):
    record = request_record(body)
    state = next(
        state for source in subject.SOURCE_DATA.values() for state in source.cases.values()
        if state.device == record["device"]["device"]
    )
    if record["retained_material"]:
        action = state.controls[1] if state.target > state.position else state.controls[0]
    else:
        action = state.controls[0] if state.target > state.position else state.controls[1]
    return provider(json.dumps({"action": action}))


def test_specimen_and_schedule_are_frozen():
    assert subject.PLANNED_LOGICAL_CALLS == 256
    assert len(subject.schedule()) == 256
    assert len(subject.SOURCE_DATA) == 4
    assert all(
        sum(row[1:] == (name, case, condition) for row in subject.schedule()) == 4
        for name in subject.SOURCES for case in subject.CASES for condition in subject.CONDITIONS
    )


def test_forms_bind_family_without_device_action_tokens():
    for source in subject.SOURCE_DATA.values():
        for representation_format in subject.FORMATS:
            content = subject.representation(source, representation_format)
            assert source.profile.controller_family in content
            assert all(action not in content for state in source.cases.values() for action in state.controls)


def test_exact_family_gate_removes_nonmatching_material():
    for source in subject.SOURCE_DATA.values():
        for case in subject.NONMATCHING_CASES:
            state = source.cases[case]
            for representation_format in subject.FORMATS:
                assert subject.material(source, representation_format)
                assert subject.scoped_material(source, state, representation_format) == ""


def test_fake_packet_finds_consumable_forms_that_require_gate_and_replays(tmp_path):
    directory = tmp_path / "evidence"
    packet = subject.execute(fake_transport, directory)
    assert packet["logical_calls"] == packet["physical_attempts"] == 256
    assert packet["retries"] == 0
    assert packet["consumption_calibration_verdict"] == {
        "class": "candidate_found",
        "scope": "representation_consumption_calibration",
    }
    assert packet["formation_verdict"] is None
    assert all(row["status"] == "consumable_requires_gate" for row in packet["form_findings"].values())
    assert all(len(row["harmful_cells"]) == 8 for row in packet["form_findings"].values())
    assert subject.replay_evidence(directory) == packet


def test_malformed_outputs_leave_all_forms_not_consumable(tmp_path):
    packet = subject.execute(lambda body: provider("not-json"), tmp_path / "invalid")
    assert packet["consumption_calibration_verdict"]["class"] == "null"
    assert all(row["status"] == "not_consumable" for row in packet["form_findings"].values())
    assert packet["logical_calls"] == 256


def test_one_transport_retry_is_replayed(tmp_path):
    first = True

    def flaky(body):
        nonlocal first
        if first:
            first = False
            raise ConnectionError("temporary")
        return fake_transport(body)

    directory = tmp_path / "retry"
    packet = subject.execute(flaky, directory)
    assert packet["physical_attempts"] == 257
    assert packet["retries"] == 1
    assert subject.replay_evidence(directory) == packet


def test_default_cli_is_no_contact_smoke(capsys):
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "mode": "smoke_no_contact",
        "planned_logical_calls": 256,
        "side_effects_entered": False,
    }
