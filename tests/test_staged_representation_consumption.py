import json

from contact import staged_representation_consumption as subject
from micro_environment.unselected_lineage_behavior import FIRST_INCREASES


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


def observed_first_increases(observation: str) -> bool:
    fields = json.loads(observation)
    return (
        fields["observed_slot"] == "first"
        and fields["observed_effect"] == "increases_position"
    ) or (
        fields["observed_slot"] == "second"
        and fields["observed_effect"] == "decreases_position"
    )


def fake_transport(body: bytes):
    user, record = request_record(body)
    if user.startswith("OBSERVATION REQUEST"):
        world = world_for_family(record["occurrence"]["public_device"]["controller_family"])
        result = record["external_result"]
        return provider(subject.prior.staged.expected_observation(
            world, result["selected_slot"], result["movement_direction"]
        ))
    if user.startswith("SENTENCE REQUEST"):
        world = world_for_family(record["public_device"]["controller_family"])
        first_increases = observed_first_increases(record["authored_observation"])
        return provider(subject.forms.expected_representation(
            world,
            "relation_sentence",
            opposite=first_increases != (
                world.profile.increasing_slot == FIRST_INCREASES
            ),
        ))
    if user.startswith("TABLE REQUEST"):
        world = world_for_family(record["public_device"]["controller_family"])
        first_increases = observed_first_increases(record["authored_observation"])
        return provider(subject.forms.expected_representation(
            world,
            "effect_table",
            opposite=first_increases != (
                world.profile.increasing_slot == FIRST_INCREASES
            ),
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
        or "second displayed control increases position" in material
    )
    if second_increases:
        action = state.controls[1] if state.target > state.position else state.controls[0]
    else:
        action = state.controls[0] if state.target > state.position else state.controls[1]
    return provider(json.dumps({"action": action}))


def test_frozen_schedule_and_budget():
    assert subject.AUTHORSHIP_CALLS == 24
    assert subject.LATER_CALLS == 576
    assert subject.PLANNED_LOGICAL_CALLS == 600
    assert subject.PHYSICAL_CALL_CEILING == 608
    assert len(subject.later_schedule()) == 576
    assert len(set(subject.later_schedule())) == 576


def test_fake_packet_finds_both_forms_usable_and_replays(tmp_path):
    original_ceiling = subject.prior.PHYSICAL_CALL_CEILING
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert subject.prior.PHYSICAL_CALL_CEILING == original_ceiling
    assert packet["representation_verdict"]["class"] == "both_usable"
    assert packet["logical_calls"] == packet["physical_attempts"] == 600
    assert packet["matching_scores"][subject.SENTENCE] == 36
    assert packet["matching_scores"][subject.TABLE] == 36
    assert packet["format_results"]["sentence"]["family_check_errors_prevented"] == 18
    assert packet["format_results"]["table"]["family_check_errors_prevented"] == 18
    assert subject.replay_evidence(evidence_dir) == packet


def test_authored_and_supplied_exact_forms_make_identical_requests(tmp_path):
    packet = subject.execute(fake_transport, tmp_path / "identical")
    later = [row for row in packet["calls"] if row["responsibility"] == "later_action"]
    for authored, supplied in (
        (subject.SENTENCE, subject.STATIC_SENTENCE),
        (subject.TABLE, subject.STATIC_TABLE),
    ):
        for world in subject.WORLDS:
            for case in ("same_up", "same_down"):
                authored_hashes = {
                    row["request_sha256"] for row in later
                    if row["world"] == world and row["case"] == case
                    and row["branch"] == authored
                }
                supplied_hashes = {
                    row["request_sha256"] for row in later
                    if row["world"] == world and row["case"] == case
                    and row["branch"] == supplied
                }
                assert authored_hashes == supplied_hashes


def test_malformed_output_is_not_engaged(tmp_path):
    packet = subject.execute(lambda body: provider("bad"), tmp_path / "bad")
    assert packet["representation_verdict"]["class"] == "not_engaged"
    assert packet["logical_calls"] == 600


def test_smoke_path_makes_no_contact(capsys):
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "mode": "smoke_no_contact",
        "planned_logical_calls": 600,
        "side_effects_entered": False,
    }
