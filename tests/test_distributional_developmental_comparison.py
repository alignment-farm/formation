import json

import pytest

from contact import distributional_developmental_comparison as subject


GUIDANCE = (
    f"For controller family {subject.PRIMARY_PROFILE.controller_family}, the second displayed "
    "control increases position and the first displayed control decreases position."
)


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
    def __init__(self):
        self.counts = {}

    def __call__(self, body):
        system, record = request_parts(body)
        if system == subject.AUTHORSHIP_SYSTEM:
            return provider(GUIDANCE)
        device = record["device"]
        actions = device["allowed_actions"]
        if device["device"] == subject.ACQUISITION.device:
            return provider(json.dumps({"action": actions[0]}))
        retained = record["retained_material"]
        key = subject.sha256(body)
        self.counts[key] = self.counts.get(key, 0) + 1
        if retained == "":
            action = actions[self.counts[key] % 2]
        elif retained == GUIDANCE or retained == subject.static_instruction():
            state = next(value for value in subject.CASE_STATES.values() if value.device == device["device"])
            case = next(name for name, value in subject.CASE_STATES.items() if value == state)
            action = subject.oracle_action(state, subject.profile_for(case))
        else:
            action = actions[1]
        return provider(json.dumps({"action": action}))


def test_specimen_has_fresh_opaque_ids_and_frozen_semantics():
    states = (subject.ACQUISITION, *subject.CASE_STATES.values())
    identifiers = [subject.PRIMARY_PROFILE.controller_family, subject.OTHER_PROFILE.controller_family]
    for state in states:
        identifiers.extend((state.device, *state.controls))
    assert len(identifiers) == len(set(identifiers)) == 14
    assert subject.oracle_action(subject.ACQUISITION, subject.PRIMARY_PROFILE) == subject.ACQUISITION.controls[1]
    assert subject.oracle_action(subject.CASE_STATES["same_family_up"], subject.PRIMARY_PROFILE) == subject.CASE_STATES["same_family_up"].controls[1]
    assert subject.oracle_action(subject.CASE_STATES["same_family_down"], subject.PRIMARY_PROFILE) == subject.CASE_STATES["same_family_down"].controls[0]
    assert subject.oracle_action(subject.CASE_STATES["other_family_up"], subject.OTHER_PROFILE) == subject.CASE_STATES["other_family_up"].controls[0]
    assert subject.OTHER_PROFILE.controller_family not in subject.static_instruction()
    assert all(state.device not in subject.static_instruction() for state in states)


def test_schedule_balances_every_branch_case_across_eight_interleaved_repeats():
    rows = subject.schedule()
    assert len(rows) == 96
    assert subject.PLANNED_LOGICAL_CALLS == 98
    assert {(case, branch): sum(row[1:] == (case, branch) for row in rows) for case in subject.CASES for branch in subject.BRANCHES} == {
        (case, branch): 8 for case in subject.CASES for branch in subject.BRANCHES
    }
    assert [row[2] for row in rows[:4]] == list(subject.BRANCHES)
    assert [row[2] for row in rows[12:16]] == list(subject.BRANCHES[1:] + subject.BRANCHES[:1])


def test_execute_compares_repeated_distributions_and_exact_requests(tmp_path):
    packet = subject.execute(FakeTransport(), tmp_path / "evidence")
    assert packet["logical_calls"] == 98
    assert packet["physical_attempts"] == 98
    assert packet["retries"] == 0
    assert packet["acquisition"]["correct_action"] is False
    assert packet["authored_intermediate"]["content"] == GUIDANCE
    authored = packet["request_distributions"][subject.AUTHORED_DELIVERY]
    assert [authored[case]["correct_actions"] for case in subject.CASES] == [8, 8, 8]
    ablated = packet["request_distributions"][subject.AUTHORED_ABLATION]
    assert [ablated[case]["correct_actions"] for case in subject.CASES] == [4, 4, 4]
    comparison = packet["comparisons"][f"{subject.AUTHORED_DELIVERY}_minus_{subject.AUTHORED_ABLATION}"]
    assert all(row == {"correct_action_delta": 4, "total_variation_distance": 0.5} for row in comparison.values())
    later = [row for row in packet["calls"] if row["responsibility"] == "later_action"]
    assert all(row["external_result"]["application_status"] == "applied" for row in later)
    for case in subject.CASES:
        for branch in subject.BRANCHES:
            hashes = {row["request_sha256"] for row in later if row["case"] == case and row["branch"] == branch}
            assert len(hashes) == 1
    assert packet["formation_verdict"] is packet["validation_verdict"] is None


def test_evidence_replays_from_raw_attempts(tmp_path):
    directory = tmp_path / "evidence"
    packet = subject.execute(FakeTransport(), directory)
    assert subject.replay_evidence(directory) == packet


def test_transport_failure_retries_but_invalid_outputs_do_not(tmp_path):
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
    assert invalid["retries"] == 0
    assert invalid["acquisition"]["proposal"] == {"available": True, "content": "not-json"}
    assert all(
        row["proposal"] == {"available": True, "content": "not-json"}
        and row["external_result"]["application_status"] == "refused"
        for row in invalid["calls"]
        if row["responsibility"] == "later_action"
    )
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
    receipt = json.loads(capsys.readouterr().out)
    assert receipt == {
        "mode": "smoke_no_contact",
        "planned_logical_calls": 98,
        "side_effects_entered": False,
    }
