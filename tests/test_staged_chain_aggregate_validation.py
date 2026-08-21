import json

from contact import representation_class_exploration as forms
from contact import staged_chain_aggregate_validation as subject
from micro_environment.unselected_lineage_behavior import FIRST_INCREASES, SECOND_INCREASES


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


def table_from_observation(world, observation: str):
    fields = json.loads(observation)
    first_increases = (
        fields["observed_slot"] == "first"
        and fields["observed_effect"] == "increases_position"
    ) or (
        fields["observed_slot"] == "second"
        and fields["observed_effect"] == "decreases_position"
    )
    return subject.prior.expected_table(world, opposite=(
        first_increases != (world.profile.increasing_slot == FIRST_INCREASES)
    ))


def fake_transport(body: bytes):
    user, record = request_record(body)
    if user.startswith("OBSERVATION REQUEST"):
        world = world_for_family(record["occurrence"]["public_device"]["controller_family"])
        if record["external_result"] == forms.WITHHELD_SENTINEL:
            return provider(subject.prior.staged.expected_observation(
                world, "first", "increased"
            ))
        result = record["external_result"]
        return provider(subject.prior.staged.expected_observation(
            world, result["selected_slot"], result["movement_direction"]
        ))
    if user.startswith("TABLE REQUEST"):
        public_device = record.get("public_device") or record["occurrence"]["public_device"]
        world = world_for_family(public_device["controller_family"])
        if "authored_observation" in record:
            return provider(table_from_observation(world, record["authored_observation"]))
        return provider(subject.prior.expected_table(
            world,
            opposite=world.profile.increasing_slot == SECOND_INCREASES,
        ))

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


def test_balanced_worlds_and_frozen_budget():
    counts = {FIRST_INCREASES: 0, SECOND_INCREASES: 0}
    for world in subject.WORLD_DATA.values():
        counts[world.profile.increasing_slot] += 1
    assert counts == {FIRST_INCREASES: 4, SECOND_INCREASES: 4}
    assert subject.AUTHORSHIP_CALLS == 48
    assert subject.LATER_CALLS == 768
    assert subject.PLANNED_LOGICAL_CALLS == 816
    assert subject.PHYSICAL_CALL_CEILING == 824


def test_fake_packet_supports_and_replays(tmp_path):
    original_worlds = subject.prior.WORLDS
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert subject.prior.WORLDS == original_worlds
    assert packet["validation_verdict"]["class"] == "supported"
    assert packet["logical_calls"] == packet["physical_attempts"] == 816
    assert packet["matching_scores"][subject.prior.EXPOSED] == 48
    assert packet["matching_scores"][subject.prior.WITHHELD] == 24
    assert packet["scope_errors_prevented"] == 24
    assert subject.replay_evidence(evidence_dir) == packet


def test_correct_hidden_lessons_collapse_support(tmp_path):
    def leaked_hidden(body: bytes):
        user, record = request_record(body)
        if (
            user.startswith("OBSERVATION REQUEST")
            and record["external_result"] == forms.WITHHELD_SENTINEL
        ):
            world = world_for_family(
                record["occurrence"]["public_device"]["controller_family"]
            )
            if world.profile.increasing_slot == FIRST_INCREASES:
                return provider(subject.prior.staged.expected_observation(
                    world, "first", "increased"
                ))
            return provider(subject.prior.staged.expected_observation(
                world, "second", "increased"
            ))
        return fake_transport(body)

    packet = subject.execute(leaked_hidden, tmp_path / "collapsed")
    assert packet["matching_scores"][subject.prior.WITHHELD] == 48
    assert packet["validation_verdict"]["class"] == "null"


def test_malformed_output_is_not_engaged(tmp_path):
    packet = subject.execute(lambda body: provider("bad"), tmp_path / "bad")
    assert packet["validation_verdict"]["class"] == "not_engaged"
    assert packet["logical_calls"] == 816


def test_smoke_path_makes_no_contact(capsys):
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "mode": "smoke_no_contact",
        "planned_logical_calls": 816,
        "side_effects_entered": False,
    }
