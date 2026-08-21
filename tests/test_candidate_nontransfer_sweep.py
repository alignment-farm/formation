import json

from contact import candidate_nontransfer_sweep as subject


def provider(content):
    return 200, json.dumps({"choices": [{"message": {"content": content}}], "usage": {"completion_tokens": 3}}).encode()


def fake_transport(body):
    value = json.loads(body)
    record = json.loads(value["messages"][1]["content"].split("\n", 1)[1].rsplit("\n", 1)[0])
    state = next(item for item in subject.CASE_STATES.values() if item.device == record["device"]["device"])
    if record["retained_material"]:
        action = state.controls[1] if state.target > state.position else state.controls[0]
    else:
        action = state.controls[0] if state.target > state.position else state.controls[1]
    return provider(json.dumps({"action": action}))


def test_sources_and_fresh_nontransfer_cases_are_bound():
    packet = json.loads((subject.SOURCE_EVIDENCE / "packet.json").read_bytes())
    exposed = [row["content"] for row in packet["candidates"] if row["exposure"] == "result_exposed"]
    assert list(subject.CANDIDATES.values()) == exposed
    identifiers = []
    for case, state in subject.CASE_STATES.items():
        identifiers.extend((subject.PROFILES[case].controller_family, state.device, *state.controls))
        assert subject.oracle_action(state, subject.PROFILES[case]) == (
            state.controls[0] if state.target > state.position else state.controls[1]
        )
    assert len(identifiers) == len(set(identifiers)) == 32


def test_schedule_and_fake_harmful_cells(tmp_path):
    assert len(subject.schedule()) == subject.PLANNED_LOGICAL_CALLS == 96
    packet = subject.execute(fake_transport, tmp_path / "evidence")
    assert packet["logical_calls"] == packet["physical_attempts"] == 96
    assert packet["harmful_cells"] == {
        subject.CANDIDATE_A: list(subject.CASES),
        subject.CANDIDATE_B: list(subject.CASES),
    }
    assert all(packet["request_distributions"][subject.EMPTY][case]["correct_actions"] == 4 for case in subject.CASES)
    assert all(packet["request_distributions"][subject.CANDIDATE_A][case]["correct_actions"] == 0 for case in subject.CASES)
    assert subject.replay_evidence(tmp_path / "evidence") == packet


def test_retry_and_invalid_paths(tmp_path):
    first = True

    def transient(body):
        nonlocal first
        if first:
            first = False
            raise ConnectionError("temporary")
        return fake_transport(body)

    packet = subject.execute(transient, tmp_path / "retried")
    assert packet["physical_attempts"] == 97
    assert packet["retries"] == 1
    assert subject.replay_evidence(tmp_path / "retried") == packet

    invalid = subject.execute(lambda body: provider("not-json"), tmp_path / "invalid")
    assert invalid["physical_attempts"] == 96
    assert invalid["harmful_cells"] == {subject.CANDIDATE_A: [], subject.CANDIDATE_B: []}


def test_default_cli_is_no_contact_smoke(capsys):
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "mode": "smoke_no_contact",
        "planned_logical_calls": 96,
        "side_effects_entered": False,
    }
