import json

import pytest

from contact import retained_rule_clause_order_trial as subject


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
    material = record["retained_material"]
    if case == "other_family_up" or material == "":
        action = state.controls[0] if state.target > state.position else state.controls[1]
    elif material == subject.retained_material(subject.INCREASE_FIRST):
        action = state.controls[1]
    else:
        action = state.controls[0]
    return provider(json.dumps({"action": action}))


def test_specimen_is_fresh_and_rules_are_semantically_equal():
    states = tuple(subject.CASE_STATES.values())
    identifiers = [subject.PRIMARY_PROFILE.controller_family, subject.OTHER_PROFILE.controller_family]
    for state in states:
        identifiers.extend((state.device, *state.controls))
    assert len(identifiers) == len(set(identifiers)) == 11
    increasing = subject.retained_material(subject.INCREASE_FIRST)
    decreasing = subject.retained_material(subject.DECREASE_FIRST)
    assert increasing != decreasing
    for phrase in ("second displayed control increases", "first displayed control decreases"):
        assert phrase in increasing and phrase in decreasing
    assert subject.OTHER_PROFILE.controller_family not in increasing + decreasing
    assert all(control not in increasing + decreasing for state in states for control in state.controls)


def test_schedule_balances_three_conditions_and_cases():
    rows = subject.schedule()
    assert len(rows) == subject.PLANNED_LOGICAL_CALLS == 72
    assert {(case, condition): sum(row[1:] == (case, condition) for row in rows) for case in subject.CASES for condition in subject.CONDITIONS} == {
        (case, condition): 8 for case in subject.CASES for condition in subject.CONDITIONS
    }
    assert [row[2] for row in rows[:3]] == list(subject.CONDITIONS)
    assert [row[2] for row in rows[9:12]] == list(subject.CONDITIONS[1:] + subject.CONDITIONS[:1])


def test_execute_distinguishes_clause_order_from_mapping_use(tmp_path):
    packet = subject.execute(fake_transport, tmp_path / "evidence")
    assert packet["logical_calls"] == packet["physical_attempts"] == 72
    distributions = packet["request_distributions"]
    assert distributions[subject.INCREASE_FIRST]["same_family_up"]["correct_actions"] == 8
    assert distributions[subject.INCREASE_FIRST]["same_family_down"]["correct_actions"] == 0
    assert distributions[subject.DECREASE_FIRST]["same_family_up"]["correct_actions"] == 0
    assert distributions[subject.DECREASE_FIRST]["same_family_down"]["correct_actions"] == 8
    contrast = packet["comparisons"]["decrease_first_minus_increase_first"]
    assert contrast["same_family_up"] == {"correct_action_delta": -8, "total_variation_distance": 1.0}
    assert contrast["same_family_down"] == {"correct_action_delta": 8, "total_variation_distance": 1.0}
    assert contrast["other_family_up"] == {"correct_action_delta": 0, "total_variation_distance": 0.0}
    for case in subject.CASES:
        for condition in subject.CONDITIONS:
            assert len({row["request_sha256"] for row in packet["calls"] if row["case"] == case and row["condition"] == condition}) == 1
    assert packet["formation_verdict"] is packet["validation_verdict"] is None


def test_raw_evidence_replays(tmp_path):
    directory = tmp_path / "evidence"
    packet = subject.execute(fake_transport, directory)
    assert subject.replay_evidence(directory) == packet


def test_retry_and_invalid_outputs_are_preserved(tmp_path):
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
    assert all(row["external_result"]["application_status"] == "refused" for row in invalid["calls"])


def test_existing_destination_refuses_overwrite(tmp_path):
    destination = tmp_path / "evidence"
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
