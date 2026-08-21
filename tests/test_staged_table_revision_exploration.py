import json

from contact import representation_class_exploration as forms
from contact import staged_table_revision_exploration as subject
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
    profile = LineageProfile(
        controller_family,
        FIRST_INCREASES if first_increases else SECOND_INCREASES,
    )
    return subject.table_for_profile(profile)


def fake_transport(body: bytes):
    user, record = request_record(body)
    if user.startswith("OBSERVATION REQUEST"):
        family = record["occurrence"]["public_device"]["controller_family"]
        world = world_for_family(family)
        if record["external_result"] == forms.WITHHELD_SENTINEL:
            return provider(subject.prior.staged.expected_observation(
                world, "first", "increased"
            ))
        result = record["external_result"]
        return provider(subject.prior.staged.expected_observation(
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


def test_frozen_schedules_and_budget():
    assert subject.LINEAGE_CALLS == 32
    assert subject.PRE_ACTION_CALLS == 48
    assert subject.POST_ACTION_CALLS == 384
    assert subject.PLANNED_LOGICAL_CALLS == 464
    assert subject.PHYSICAL_CALL_CEILING == 472
    assert len(subject.pre_schedule()) == 48
    assert len(subject.post_schedule()) == 384


def test_fake_packet_finds_revision_candidate_and_replays(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert packet["revision_verdict"]["class"] == "candidate_found"
    assert packet["logical_calls"] == packet["physical_attempts"] == 464
    assert packet["pre_change_scores"][subject.PRE_OLD] == 24
    assert packet["counter_actions_old_policy_consistent"] == 4
    assert packet["post_matching_scores"][subject.REVISED] == 24
    assert packet["post_matching_scores"][subject.STALE] == 0
    assert packet["post_matching_scores"][subject.HIDDEN] == 12
    assert subject.replay_evidence(evidence_dir) == packet


def test_stale_and_revision_removed_requests_are_identical(tmp_path):
    packet = subject.execute(fake_transport, tmp_path / "identical")
    rows = [row for row in packet["calls"] if row["responsibility"] == "post_change_action"]
    for world in subject.WORLDS:
        for case in subject.POST_CASES:
            stale = {
                row["request_sha256"] for row in rows
                if row["world"] == world and row["case"] == case
                and row["branch"] == subject.STALE
            }
            removed = {
                row["request_sha256"] for row in rows
                if row["world"] == world and row["case"] == case
                and row["branch"] == subject.REMOVED
            }
            assert stale == removed


def test_malformed_output_is_not_engaged(tmp_path):
    packet = subject.execute(lambda body: provider("bad"), tmp_path / "bad")
    assert packet["revision_verdict"]["class"] == "not_engaged"
    assert packet["logical_calls"] == 464


def test_smoke_path_makes_no_contact(capsys):
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "mode": "smoke_no_contact",
        "planned_logical_calls": 464,
        "side_effects_entered": False,
    }
