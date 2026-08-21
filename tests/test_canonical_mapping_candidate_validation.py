import json

import pytest

from contact import canonical_mapping_candidate_validation as subject


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
        if system == subject.authorship.AUTHORSHIP_SYSTEM:
            family = record["occurrence"]["public_device"]["controller_family"]
            world = next(value for value in subject.WORLD_DATA.values() if value.profile.controller_family == family)
            if isinstance(record["external_result"], dict):
                content = subject.static_mapping(world)
            else:
                content = (
                    f"For controller family {family}, the first displayed control increases position "
                    "and the second displayed control decreases position."
                )
            return provider(content)
        device = record["device"]
        state = None
        world = None
        case = None
        for candidate_world in subject.WORLD_DATA.values():
            if candidate_world.acquisition.device == device["device"]:
                state, world = candidate_world.acquisition, candidate_world
                break
            for candidate_case, candidate_state in candidate_world.cases.items():
                if candidate_state.device == device["device"]:
                    state, world, case = candidate_state, candidate_world, candidate_case
                    break
        assert state is not None and world is not None
        if case is None:
            action = state.controls[0] if state.target > state.position else state.controls[1]
        else:
            material = record["retained_material"]
            if "first displayed control decreases" in material:
                action = state.controls[1] if state.target > state.position else state.controls[0]
            else:
                action = state.controls[0] if state.target > state.position else state.controls[1]
        return provider(json.dumps({"action": action}))


def test_specimen_is_fresh_mirrored_and_leakage_free():
    identifiers = []
    for world in subject.WORLD_DATA.values():
        identifiers.extend((world.profile.controller_family, world.other_profile.controller_family))
        for state in (world.acquisition, *world.cases.values()):
            identifiers.extend((state.device, *state.controls))
    assert len(identifiers) == len(set(identifiers)) == 28
    assert subject.WORLD_DATA["world_a"].acquisition.target > subject.WORLD_DATA["world_a"].acquisition.position
    assert subject.WORLD_DATA["world_b"].acquisition.target < subject.WORLD_DATA["world_b"].acquisition.position
    for world in subject.WORLD_DATA.values():
        proposal = subject.ProposalReceipt(True, world.acquisition.controls[0])
        result = subject.apply_committed_action(world.acquisition, world.profile, proposal)
        body = subject.authorship_body(world, proposal, result, subject.EXPOSED)
        assert subject.static_mapping(world).encode() not in body
        assert all(control.encode() not in body for state in world.cases.values() for control in state.controls)


def test_schedule_has_every_world_branch_case_six_times():
    rows = subject.later_schedule()
    assert subject.PLANNED_LOGICAL_CALLS == 258
    assert len(rows) == 252
    assert {
        (world, branch, case): sum(row[1:] == (world, case, branch) for row in rows)
        for world in subject.WORLDS for branch in subject.BRANCHES for case in subject.CASES
    } == {
        (world, branch, case): 6
        for world in subject.WORLDS for branch in subject.BRANCHES for case in subject.CASES
    }


def test_branch_material_applies_public_scope_without_reading_mapping():
    world = subject.WORLD_DATA["world_a"]
    proposal = subject.ProposalReceipt(True, world.acquisition.controls[0])
    result = subject.apply_committed_action(world.acquisition, world.profile, proposal)
    candidates = {
        (world.name, subject.EXPOSED): "candidate-exposed",
        (world.name, subject.WITHHELD): "candidate-withheld",
    }
    assert subject.branch_material(world, "same_family_up", subject.GOVERNED, proposal, result, candidates) == "candidate-exposed"
    assert subject.branch_material(world, "other_family_up", subject.GOVERNED, proposal, result, candidates) == ""
    assert subject.branch_material(world, "other_family_up", subject.AUTHORED_UNGATED, proposal, result, candidates) == "candidate-exposed"
    assert subject.branch_material(world, "same_family_up", subject.DELIVERY_ABLATION, proposal, result, candidates) == ""


def test_fake_packet_passes_frozen_candidate_validation(tmp_path):
    packet = subject.execute(FakeTransport(), tmp_path / "evidence")
    assert packet["logical_calls"] == packet["physical_attempts"] == 258
    assert packet["candidate_validation_verdict"] == {
        "class": "supported",
        "scope": "acquisition_transfer_selectivity",
    }
    assert packet["formation_verdict"] is None
    assert all(
        candidate["exact_static_match"] is (candidate["exposure"] == subject.EXPOSED)
        for candidate in packet["candidates"]
    )
    for world in subject.WORLDS:
        distributions = packet["request_distributions"][world]
        assert [distributions[subject.GOVERNED][case]["correct_actions"] for case in subject.CASES] == [6, 6, 6]
        assert [distributions[subject.COLD][case]["correct_actions"] for case in subject.CASES] == [0, 0, 6]
        assert [distributions[subject.AUTHORED_UNGATED][case]["correct_actions"] for case in subject.CASES] == [6, 6, 0]
        assert [distributions[subject.WITHHELD_GOVERNED][case]["correct_actions"] for case in subject.CASES] == [0, 0, 6]
    assert all(
        len({row["request_sha256"] for row in packet["calls"] if row.get("world") == world and row.get("branch") == branch and row.get("case") == case}) == 1
        for world in subject.WORLDS for branch in subject.BRANCHES for case in subject.CASES
    )


def test_raw_evidence_replays(tmp_path):
    directory = tmp_path / "evidence"
    packet = subject.execute(FakeTransport(), directory)
    assert subject.replay_evidence(directory) == packet


def test_retry_invalid_and_overwrite_paths(tmp_path):
    fake = FakeTransport()
    first = True

    def transient(body):
        nonlocal first
        if first:
            first = False
            raise ConnectionError("temporary")
        return fake(body)

    retried = subject.execute(transient, tmp_path / "retried")
    assert retried["physical_attempts"] == 259
    assert retried["retries"] == 1
    assert subject.replay_evidence(tmp_path / "retried") == retried

    invalid = subject.execute(lambda body: provider("not-json"), tmp_path / "invalid")
    assert invalid["candidate_validation_verdict"]["class"] == "not_engaged"
    assert invalid["physical_attempts"] == 258

    destination = tmp_path / "existing"
    destination.mkdir()
    with pytest.raises(FileExistsError):
        subject.execute(fake, destination)


def test_default_cli_is_no_contact_smoke(capsys):
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "mode": "smoke_no_contact",
        "planned_logical_calls": 258,
        "side_effects_entered": False,
    }
