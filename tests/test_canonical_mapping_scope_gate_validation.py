import json

from contact import canonical_mapping_scope_gate_validation as subject


def provider(content):
    return 200, json.dumps({"choices": [{"message": {"content": content}}], "usage": {"completion_tokens": 3}}).encode()


def fake_transport(body):
    value = json.loads(body)
    record = json.loads(value["messages"][1]["content"].split("\n", 1)[1].rsplit("\n", 1)[0])
    state = next(state for cases in subject.CASE_STATES.values() for state in cases.values() if state.device == record["device"]["device"])
    if record["retained_material"]:
        action = state.controls[1] if state.target > state.position else state.controls[0]
    else:
        action = state.controls[0] if state.target > state.position else state.controls[1]
    return provider(json.dumps({"action": action}))


def test_sources_gate_and_schedule_are_frozen():
    assert set(subject.CANDIDATES) == set(subject.WORLDS)
    assert len(subject.schedule()) == subject.PLANNED_LOGICAL_CALLS == 96
    for name in subject.WORLDS:
        assert subject.delivered(name, "same_up", subject.SCOPED) == subject.CANDIDATES[name]
        assert subject.delivered(name, "other_up", subject.SCOPED) == ""
        assert subject.delivered(name, "other_down", subject.UNGATED) == subject.CANDIDATES[name]
    assert all(
        sum(row[1:] == (name, case, condition) for row in subject.schedule()) == 4
        for name in subject.WORLDS for case in subject.CASES for condition in subject.CONDITIONS
    )


def test_fake_packet_supports_scope_gate_and_replays(tmp_path):
    directory = tmp_path / "evidence"
    packet = subject.execute(fake_transport, directory)
    assert packet["logical_calls"] == packet["physical_attempts"] == 96
    assert packet["scope_gate_validation_verdict"] == {"class": "supported", "scope": "candidate_scope_gate"}
    assert packet["formation_verdict"] is None
    for name in subject.WORLDS:
        rows = packet["request_distributions"][name]
        assert [rows[subject.SCOPED][case]["correct_actions"] for case in subject.CASES] == [4, 4, 4, 4]
        assert [rows[subject.UNGATED][case]["correct_actions"] for case in subject.CASES] == [4, 4, 0, 0]
        assert [rows[subject.ABLATION][case]["correct_actions"] for case in subject.CASES] == [0, 0, 4, 4]
    assert subject.replay_evidence(directory) == packet


def test_invalid_outputs_do_not_promote_verdict(tmp_path):
    packet = subject.execute(lambda body: provider("not-json"), tmp_path / "invalid")
    assert packet["scope_gate_validation_verdict"]["class"] == "not_engaged"
    assert packet["physical_attempts"] == 96


def test_default_cli_is_no_contact_smoke(capsys):
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "mode": "smoke_no_contact",
        "planned_logical_calls": 96,
        "side_effects_entered": False,
    }
