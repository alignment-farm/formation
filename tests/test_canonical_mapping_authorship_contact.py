import json

import pytest

from contact import canonical_mapping_authorship_contact as subject


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


class FakeTransport:
    def __call__(self, body):
        system, record = request_parts(body)
        if system == subject.AUTHORSHIP_SYSTEM:
            return provider(subject.static_instruction())
        device = record["device"]
        state = subject.ACQUISITION if device["device"] == subject.ACQUISITION.device else next(
            value for value in subject.CASE_STATES.values() if value.device == device["device"]
        )
        if state == subject.ACQUISITION:
            action = state.controls[0]
        else:
            case = next(name for name, value in subject.CASE_STATES.items() if value == state)
            material = record["retained_material"]
            if material in (subject.static_instruction(),) and case != "other_family_up":
                action = subject.oracle_action(state, subject.profile_for(case))
            elif material.startswith("{"):
                action = state.controls[1]
            else:
                action = state.controls[0] if state.target > state.position else state.controls[1]
        return provider(json.dumps({"action": action}))


def test_specimen_is_fresh_and_authorship_prompt_does_not_supply_mapping():
    states = (subject.ACQUISITION, *subject.CASE_STATES.values())
    identifiers = [subject.PRIMARY_PROFILE.controller_family, subject.OTHER_PROFILE.controller_family]
    for state in states:
        identifiers.extend((state.device, *state.controls))
    assert len(identifiers) == len(set(identifiers)) == 14
    proposal = subject.ProposalReceipt(True, subject.ACQUISITION.controls[0])
    result = subject.apply_committed_action(subject.ACQUISITION, subject.PRIMARY_PROFILE, proposal)
    body = subject.authorship_body(subject.ACQUISITION, proposal, result)
    assert subject.static_instruction().encode() not in body
    assert all(
        control.encode() not in body
        for state in subject.CASE_STATES.values()
        for control in state.controls
    )
    assert "first displayed control" in subject.AUTHORSHIP_SYSTEM
    assert "second displayed control" in subject.AUTHORSHIP_SYSTEM


def test_schedule_balances_every_branch_case_for_eight_repeats():
    rows = subject.schedule()
    assert len(rows) == 96
    assert subject.PLANNED_LOGICAL_CALLS == 98
    assert {(case, branch): sum(row[1:] == (case, branch) for row in rows) for case in subject.CASES for branch in subject.BRANCHES} == {
        (case, branch): 8 for case in subject.CASES for branch in subject.BRANCHES
    }


def test_execute_scores_unrepaired_authored_mapping_and_distributions(tmp_path):
    packet = subject.execute(FakeTransport(), tmp_path / "evidence")
    assert packet["logical_calls"] == packet["physical_attempts"] == 98
    assert packet["acquisition"]["correct_action"] is False
    assert packet["acquisition"]["external_result"]["selected_slot"] == "first"
    assert packet["authored_intermediate"]["content"] == subject.static_instruction()
    assert packet["authored_intermediate"]["exact_static_match"] is True
    authored = packet["request_distributions"][subject.AUTHORED_DELIVERY]
    assert [authored[case]["correct_actions"] for case in subject.CASES] == [8, 8, 8]
    ablated = packet["request_distributions"][subject.AUTHORED_ABLATION]
    assert [ablated[case]["correct_actions"] for case in subject.CASES] == [0, 0, 8]
    comparison = packet["comparisons"][f"{subject.AUTHORED_DELIVERY}_minus_{subject.AUTHORED_ABLATION}"]
    assert [comparison[case]["correct_action_delta"] for case in subject.CASES] == [8, 8, 0]
    for case in subject.CASES:
        for branch in subject.BRANCHES:
            hashes = {
                row["request_sha256"]
                for row in packet["calls"]
                if row.get("case") == case and row.get("branch") == branch
            }
            assert len(hashes) == 1
    assert packet["formation_verdict"] is packet["validation_verdict"] is None


def test_raw_evidence_replays(tmp_path):
    directory = tmp_path / "evidence"
    packet = subject.execute(FakeTransport(), directory)
    assert subject.replay_evidence(directory) == packet


def test_retry_and_invalid_outputs_are_preserved(tmp_path):
    fake = FakeTransport()
    first = True

    def transient(body):
        nonlocal first
        if first:
            first = False
            raise ConnectionError("temporary")
        return fake(body)

    retried = subject.execute(transient, tmp_path / "retried")
    assert retried["physical_attempts"] == 99
    assert retried["retries"] == 1
    assert subject.replay_evidence(tmp_path / "retried") == retried

    invalid = subject.execute(lambda body: provider("not-json"), tmp_path / "invalid")
    assert invalid["physical_attempts"] == 98
    assert all(
        row["invalid_or_unavailable"] == 8
        for branch in invalid["request_distributions"].values()
        for row in branch.values()
    )


def test_existing_destination_refuses_overwrite(tmp_path):
    destination = tmp_path / "evidence"
    destination.mkdir()
    with pytest.raises(FileExistsError):
        subject.execute(FakeTransport(), destination)


def test_default_cli_is_no_contact_smoke(capsys):
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "mode": "smoke_no_contact",
        "planned_logical_calls": 98,
        "side_effects_entered": False,
    }
