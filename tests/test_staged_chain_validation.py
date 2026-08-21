import json

from contact import representation_class_exploration as forms
from contact import staged_chain_validation as subject


def provider(content: str):
    return 200, json.dumps({
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 9, "completion_tokens": 3},
    }).encode()


def request_record(body: bytes):
    envelope = json.loads(body)
    user = envelope["messages"][1]["content"]
    return user, json.loads(user.split("\n", 1)[1].rsplit("\n", 1)[0])


def world_for_family(controller_family: str):
    return next(
        world for world in subject.WORLD_DATA.values()
        if world.profile.controller_family == controller_family
    )


def fake_transport(body: bytes):
    user, record = request_record(body)
    if user.startswith("OBSERVATION REQUEST"):
        world = world_for_family(record["occurrence"]["public_device"]["controller_family"])
        if record["external_result"] == forms.WITHHELD_SENTINEL:
            return provider(subject.staged.expected_observation(world, "first", "increased"))
        result = record["external_result"]
        return provider(subject.staged.expected_observation(
            world, result["selected_slot"], result["movement_direction"]
        ))
    if user.startswith("TABLE REQUEST"):
        public_device = record.get("public_device") or record["occurrence"]["public_device"]
        world = world_for_family(public_device["controller_family"])
        if "authored_observation" in record:
            correct = '"observed_slot":"second","observed_effect":"increases_position"' in record["authored_observation"]
            return provider(subject.expected_table(world, opposite=not correct))
        return provider(subject.expected_table(world, opposite=True))

    state = next(
        state
        for world in subject.WORLD_DATA.values()
        for state in (world.acquisition, *world.cases.values())
        if state.device == record["device"]["device"]
    )
    material = record["retained_material"]
    second_increases = (
        '"second_displayed_control_effect":"increases_position"' in material
    )
    if second_increases:
        action = state.controls[1] if state.target > state.position else state.controls[0]
    else:
        action = state.controls[0] if state.target > state.position else state.controls[1]
    return provider(json.dumps({"action": action}))


def test_frozen_schedule_and_budget():
    assert subject.AUTHORSHIP_CALLS == 24
    assert subject.LATER_CALLS == 512
    assert subject.PLANNED_LOGICAL_CALLS == 536
    assert subject.PHYSICAL_CALL_CEILING == 544
    assert len(subject.later_schedule()) == 512
    assert len(set(subject.later_schedule())) == 512


def test_withheld_observation_has_no_consequence():
    world = subject.WORLD_DATA[subject.WORLDS[0]]
    proposal = subject.ProposalReceipt(True, world.acquisition.controls[1])
    result = subject.apply_committed_action(world.acquisition, world.profile, proposal)
    exposed = request_record(subject.observation_body(world, proposal, result, True))[1]
    withheld = request_record(subject.observation_body(world, proposal, result, False))[1]
    assert exposed["occurrence"] == withheld["occurrence"]
    assert exposed["external_result"] != forms.WITHHELD_SENTINEL
    assert withheld["external_result"] == forms.WITHHELD_SENTINEL


def test_fake_packet_supports_and_replays(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert packet["validation_verdict"]["class"] == "supported"
    assert packet["logical_calls"] == packet["physical_attempts"] == 536
    assert packet["matching_scores"][subject.EXPOSED] == 32
    assert packet["matching_scores"][subject.RAW] == 0
    assert packet["unrelated_loss"] == 0
    assert packet["scope_errors_prevented"] == 32
    assert subject.replay_evidence(evidence_dir) == packet


def test_malformed_output_is_retained_as_not_engaged(tmp_path):
    packet = subject.execute(lambda body: provider("bad"), tmp_path / "bad")
    assert packet["validation_verdict"]["class"] == "not_engaged"
    assert packet["logical_calls"] == 536


def test_one_retry_remains_replayable(tmp_path):
    calls = 0

    def flaky(body: bytes):
        nonlocal calls
        calls += 1
        if calls == 1:
            return 500, b"temporary"
        return fake_transport(body)

    evidence_dir = tmp_path / "retry"
    packet = subject.execute(flaky, evidence_dir)
    assert packet["validation_verdict"]["class"] == "supported"
    assert packet["physical_attempts"] == 537
    assert packet["retries"] == 1
    assert subject.replay_evidence(evidence_dir) == packet


def test_smoke_path_makes_no_contact(capsys):
    assert subject.main([]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output == {
        "mode": "smoke_no_contact",
        "planned_logical_calls": 536,
        "side_effects_entered": False,
    }
