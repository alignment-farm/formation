import json

from contact import representation_class_exploration as forms
from contact import staged_table_revision_validation as subject
from micro_environment.unselected_lineage_behavior import (
    FIRST_INCREASES,
    SECOND_INCREASES,
    LineageProfile,
)


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


def table_from_observation(controller_family: str, observation: str) -> str:
    fields = json.loads(observation)
    first_increases = (
        fields["observed_slot"] == "first"
        and fields["observed_effect"] == "increases_position"
    ) or (
        fields["observed_slot"] == "second"
        and fields["observed_effect"] == "decreases_position"
    )
    return subject.revision.table_for_profile(LineageProfile(
        controller_family,
        FIRST_INCREASES if first_increases else SECOND_INCREASES,
    ))


def fake_transport(body: bytes):
    user, record = request_record(body)
    if user.startswith("OBSERVATION REQUEST"):
        family = record["occurrence"]["public_device"]["controller_family"]
        world = world_for_family(family)
        if record["external_result"] == forms.WITHHELD_SENTINEL:
            return provider(subject.revision.prior.staged.expected_observation(
                world, "first", "increased"
            ))
        result = record["external_result"]
        return provider(subject.revision.prior.staged.expected_observation(
            world, result["selected_slot"], result["movement_direction"]
        ))
    if user.startswith("TABLE REQUEST") or user.startswith("REVISION REQUEST"):
        family = record["public_device"]["controller_family"]
        return provider(table_from_observation(family, record["authored_observation"]))

    state = next(
        state
        for world in subject.WORLD_DATA.values()
        for state in (
            world.acquisition,
            *world.pre_cases.values(),
            world.counter_state,
            *world.post_cases.values(),
        )
        if state.device == record["device"]["device"]
    )
    material = record["retained_material"]
    if material and "prior_effect_table" in material:
        material = json.loads(material)["prior_effect_table"]
    second_increases = (
        '"second_displayed_control_effect":"increases_position"' in material
    )
    if second_increases:
        action = state.controls[1] if state.target > state.position else state.controls[0]
    else:
        action = state.controls[0] if state.target > state.position else state.controls[1]
    return provider(json.dumps({"action": action}))


def test_balanced_worlds_and_frozen_budget():
    changed = {FIRST_INCREASES: 0, SECOND_INCREASES: 0}
    for world in subject.WORLD_DATA.values():
        changed[world.new_profile.increasing_slot] += 1
    assert changed == {FIRST_INCREASES: 4, SECOND_INCREASES: 4}
    assert subject.LINEAGE_CALLS == 64
    assert subject.PRE_ACTION_CALLS == 96
    assert subject.POST_ACTION_CALLS == 768
    assert subject.PLANNED_LOGICAL_CALLS == 928
    assert subject.PHYSICAL_CALL_CEILING == 936


def test_fake_packet_supports_and_replays(tmp_path):
    original_worlds = subject.revision.WORLDS
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert subject.revision.WORLDS == original_worlds
    assert packet["revision_verdict"]["class"] == "supported"
    assert packet["logical_calls"] == packet["physical_attempts"] == 928
    assert packet["pre_change_scores"][subject.revision.PRE_OLD] == 48
    assert packet["counter_actions_old_policy_consistent"] == 8
    assert packet["post_matching_scores"][subject.revision.REVISED] == 48
    assert packet["post_matching_scores"][subject.revision.HIDDEN] == 24
    assert subject.replay_evidence(evidence_dir) == packet


def test_correct_hidden_revisions_collapse_support(tmp_path):
    def leaked_hidden(body: bytes):
        user, record = request_record(body)
        if (
            user.startswith("OBSERVATION REQUEST")
            and record["external_result"] == forms.WITHHELD_SENTINEL
        ):
            family = record["occurrence"]["public_device"]["controller_family"]
            world = world_for_family(family)
            if world.new_profile.increasing_slot == FIRST_INCREASES:
                return provider(subject.revision.prior.staged.expected_observation(
                    world, "first", "increased"
                ))
            return provider(subject.revision.prior.staged.expected_observation(
                world, "second", "increased"
            ))
        return fake_transport(body)

    packet = subject.execute(leaked_hidden, tmp_path / "collapsed")
    assert packet["post_matching_scores"][subject.revision.HIDDEN] == 48
    assert packet["revision_verdict"]["class"] == "null"


def test_malformed_output_is_not_engaged(tmp_path):
    packet = subject.execute(lambda body: provider("bad"), tmp_path / "bad")
    assert packet["revision_verdict"]["class"] == "not_engaged"
    assert packet["logical_calls"] == 928


def test_smoke_path_makes_no_contact(capsys):
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "mode": "smoke_no_contact",
        "planned_logical_calls": 928,
        "side_effects_entered": False,
    }
