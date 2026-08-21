import json

import pytest

from contact import scoped_candidate_continuation as subject


def provider(content):
    return 200, json.dumps({
        "choices": [{"message": {"content": content}}],
        "usage": {"completion_tokens": 3, "prompt_tokens": 10},
    }).encode()


def request_record(body):
    value = json.loads(body)
    user = value["messages"][1]["content"]
    return json.loads(user.split("\n", 1)[1].rsplit("\n", 1)[0])


def fake_transport(body):
    record = request_record(body)
    device = record["device"]
    state = next(value for value in subject.CASE_STATES.values() if value.device == device["device"])
    case = next(name for name, value in subject.CASE_STATES.items() if value == state)
    if record["retained_material"] == subject.CANDIDATE:
        if case == "other_family_up":
            action = state.controls[1]
        else:
            action = subject.oracle_action(state, subject.profile_for(case))
    else:
        action = state.controls[0] if state.target > state.position else state.controls[1]
    return provider(json.dumps({"action": action}))


def test_source_candidate_and_family_are_bound_to_retained_evidence():
    packet = json.loads((subject.SOURCE_EVIDENCE / "packet.json").read_bytes())
    specimen = json.loads((subject.SOURCE_EVIDENCE / "specimen.json").read_bytes())
    assert subject.CANDIDATE == packet["authored_intermediate"]["content"]
    assert subject.SOURCE_FAMILY == specimen["acquisition"]["controller_family"]
    assert subject.SOURCE_PACKET_SHA256 == subject.base.sha256((subject.SOURCE_EVIDENCE / "packet.json").read_bytes())
    assert subject.SOURCE_FAMILY in subject.CANDIDATE


def test_gate_uses_only_exact_public_family_match():
    for case in ("same_family_up", "same_family_down"):
        state = subject.CASE_STATES[case]
        assert subject.delivered_material(subject.SCOPED, state) == subject.CANDIDATE
    other = subject.CASE_STATES["other_family_up"]
    assert subject.delivered_material(subject.SCOPED, other) == ""
    assert subject.delivered_material(subject.UNGATED, other) == subject.CANDIDATE
    assert subject.delivered_material(subject.ABLATION, other) == ""


def test_schedule_balances_conditions_cases_and_repeats():
    rows = subject.schedule()
    assert len(rows) == subject.PLANNED_LOGICAL_CALLS == 72
    assert {(case, condition): sum(row[1:] == (case, condition) for row in rows) for case in subject.CASES for condition in subject.CONDITIONS} == {
        (case, condition): 8 for case in subject.CASES for condition in subject.CONDITIONS
    }


def test_execute_separates_scoped_delivery_from_negative_transfer(tmp_path):
    packet = subject.execute(fake_transport, tmp_path / "evidence")
    assert packet["logical_calls"] == packet["physical_attempts"] == 72
    distributions = packet["request_distributions"]
    assert [distributions[subject.ABLATION][case]["correct_actions"] for case in subject.CASES] == [0, 0, 8]
    assert [distributions[subject.UNGATED][case]["correct_actions"] for case in subject.CASES] == [8, 8, 0]
    assert [distributions[subject.SCOPED][case]["correct_actions"] for case in subject.CASES] == [8, 8, 8]
    scoped_ablation = packet["comparisons"]["scoped_minus_ablation"]
    assert [scoped_ablation[case]["correct_action_delta"] for case in subject.CASES] == [8, 8, 0]
    scoped_ungated = packet["comparisons"]["scoped_minus_ungated"]
    assert [scoped_ungated[case]["correct_action_delta"] for case in subject.CASES] == [0, 0, 8]
    for case in subject.CASES:
        for condition in subject.CONDITIONS:
            assert len({row["request_sha256"] for row in packet["calls"] if row["case"] == case and row["condition"] == condition}) == 1
    assert packet["formation_verdict"] is packet["validation_verdict"] is None


def test_raw_evidence_replays(tmp_path):
    directory = tmp_path / "evidence"
    packet = subject.execute(fake_transport, directory)
    assert subject.replay_evidence(directory) == packet


def test_retry_invalid_and_overwrite_paths(tmp_path):
    first = True

    def transient(body):
        nonlocal first
        if first:
            first = False
            raise ConnectionError("temporary")
        return fake_transport(body)

    retried = subject.execute(transient, tmp_path / "retried")
    assert retried["physical_attempts"] == 73
    assert retried["retries"] == 1
    assert subject.replay_evidence(tmp_path / "retried") == retried

    invalid = subject.execute(lambda body: provider("not-json"), tmp_path / "invalid")
    assert invalid["physical_attempts"] == 72
    assert all(
        row["invalid_or_unavailable"] == 8
        for condition in invalid["request_distributions"].values()
        for row in condition.values()
    )

    destination = tmp_path / "existing"
    destination.mkdir()
    with pytest.raises(FileExistsError):
        subject.execute(fake_transport, destination)


def test_default_cli_is_no_contact_smoke(capsys):
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "mode": "smoke_no_contact",
        "planned_logical_calls": 72,
        "side_effects_entered": False,
    }
