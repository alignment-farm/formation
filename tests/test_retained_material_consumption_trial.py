import json

import pytest

from contact import retained_material_consumption_trial as subject


def provider(content):
    return 200, json.dumps({
        "choices": [{"message": {"content": content}}],
        "usage": {"completion_tokens": 3, "prompt_tokens": 10},
    }).encode()


def request_parts(body):
    value = json.loads(body)
    system = value["messages"][0]["content"]
    user = value["messages"][1]["content"]
    record = json.loads(user.split("\n", 1)[1].rsplit("\n", 1)[0])
    return system, record


def fake_transport(body):
    system, record = request_parts(body)
    device = record["device"]
    state = next(value for value in subject.CASE_STATES.values() if value.device == device["device"])
    case = next(name for name, value in subject.CASE_STATES.items() if value == state)
    explicit_static = system == subject.EXPLICIT_SYSTEM and record["retained_material"] == subject.static_instruction()
    if explicit_static and case != "other_family_up":
        action = subject.oracle_action(state, subject.profile_for(case))
    else:
        action = state.controls[0] if state.target > state.position else state.controls[1]
    return provider(json.dumps({"action": action}))


def test_specimen_is_fresh_and_instruction_is_generic():
    states = tuple(subject.CASE_STATES.values())
    identifiers = [subject.PRIMARY_PROFILE.controller_family, subject.OTHER_PROFILE.controller_family]
    for state in states:
        identifiers.extend((state.device, *state.controls))
    assert len(identifiers) == len(set(identifiers)) == 11
    assert subject.static_instruction() not in subject.EXPLICIT_SYSTEM
    assert subject.PRIMARY_PROFILE.controller_family not in subject.EXPLICIT_SYSTEM
    assert all(control not in subject.EXPLICIT_SYSTEM for state in states for control in state.controls)
    assert subject.OTHER_PROFILE.controller_family not in subject.static_instruction()


def test_schedule_balances_conditions_cases_and_repeats():
    rows = subject.schedule()
    assert len(rows) == subject.PLANNED_LOGICAL_CALLS == 96
    assert {(case, condition): sum(row[1:] == (case, condition) for row in rows) for case in subject.CASES for condition in subject.CONDITIONS} == {
        (case, condition): 8 for case in subject.CASES for condition in subject.CONDITIONS
    }
    assert [row[2] for row in rows[:4]] == list(subject.CONDITIONS)
    assert [row[2] for row in rows[12:16]] == list(subject.CONDITIONS[1:] + subject.CONDITIONS[:1])


def test_execute_scores_the_interface_content_interaction(tmp_path):
    packet = subject.execute(fake_transport, tmp_path / "evidence")
    assert packet["logical_calls"] == packet["physical_attempts"] == 96
    assert packet["retries"] == 0
    comparison = packet["comparisons"]["explicit_static_minus_empty"]
    assert comparison["same_family_up"] == {"correct_action_delta": 8, "total_variation_distance": 1.0}
    assert comparison["same_family_down"] == {"correct_action_delta": 8, "total_variation_distance": 1.0}
    assert comparison["other_family_up"] == {"correct_action_delta": 0, "total_variation_distance": 0.0}
    assert all(
        row == {"correct_action_delta": 0, "total_variation_distance": 0.0}
        for row in packet["comparisons"]["explicit_empty_minus_implicit_empty"].values()
    )
    for case in subject.CASES:
        for condition in subject.CONDITIONS:
            hashes = {row["request_sha256"] for row in packet["calls"] if row["case"] == case and row["condition"] == condition}
            assert len(hashes) == 1
    assert all(row["external_result"]["application_status"] == "applied" for row in packet["calls"])
    assert packet["formation_verdict"] is packet["validation_verdict"] is None


def test_raw_evidence_replays(tmp_path):
    directory = tmp_path / "evidence"
    packet = subject.execute(fake_transport, directory)
    assert subject.replay_evidence(directory) == packet


def test_retry_and_invalid_output_paths_are_bounded(tmp_path):
    first = True

    def transient(body):
        nonlocal first
        if first:
            first = False
            raise ConnectionError("temporary")
        return fake_transport(body)

    retried = subject.execute(transient, tmp_path / "retried")
    assert retried["physical_attempts"] == 97
    assert retried["retries"] == 1
    assert subject.replay_evidence(tmp_path / "retried") == retried

    invalid = subject.execute(lambda body: provider("not-json"), tmp_path / "invalid")
    assert invalid["physical_attempts"] == 96
    assert invalid["retries"] == 0
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
        "planned_logical_calls": 96,
        "side_effects_entered": False,
    }
