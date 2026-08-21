import json

from contact import staged_table_accumulation_exploration as subject
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


def profile_for_family(controller_family: str):
    return next(
        profile
        for lineage in subject.LINEAGE_DATA.values()
        for profile in lineage.profiles.values()
        if profile.controller_family == controller_family
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
    return subject.table_for(LineageProfile(
        controller_family,
        FIRST_INCREASES if first_increases else SECOND_INCREASES,
    ))


def selected_table(material: str, controller_family: str) -> str:
    if not material:
        return ""
    parsed = json.loads(material)
    if "retained_effect_tables" in parsed:
        for table in parsed["retained_effect_tables"]:
            if json.loads(table)["controller_family"] == controller_family:
                return table
        return ""
    if "raw_experiences" in parsed:
        return ""
    return material if parsed.get("controller_family") == controller_family else ""


def fake_transport(body: bytes):
    user, record = request_record(body)
    if user.startswith("OBSERVATION REQUEST"):
        family = record["occurrence"]["public_device"]["controller_family"]
        profile = profile_for_family(family)
        view = type("WorldView", (), {"profile": profile})()
        result = record["external_result"]
        return provider(subject.prior.staged.expected_observation(
            view, result["selected_slot"], result["movement_direction"]
        ))
    if user.startswith("TABLE REQUEST"):
        family = record["public_device"]["controller_family"]
        return provider(table_from_observation(family, record["authored_observation"]))

    state = next(
        state
        for lineage in subject.LINEAGE_DATA.values()
        for state in (*lineage.acquisitions.values(), *lineage.cases.values())
        if state.device == record["device"]["device"]
    )
    material = selected_table(
        record["retained_material"], record["device"]["controller_family"]
    )
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
    assert subject.LATER_CALLS == 576
    assert subject.PLANNED_LOGICAL_CALLS == 600
    assert subject.PHYSICAL_CALL_CEILING == 608
    assert len(subject.schedule()) == 576
    assert len(set(subject.schedule())) == 576


def test_fake_packet_finds_accumulation_candidate_and_replays(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert packet["accumulation_verdict"]["class"] == "candidate_found"
    assert packet["logical_calls"] == packet["physical_attempts"] == 600
    assert packet["exact_observations"] == packet["exact_tables"] == 8
    assert packet["matching_scores"][subject.GATED] == 48
    assert packet["matching_scores"][subject.JOINT] == 48
    assert packet["matching_scores"][subject.COLD] == 24
    assert subject.replay_evidence(evidence_dir) == packet


def test_joint_material_contains_both_exact_tables():
    lineage = subject.LINEAGE_DATA[subject.LINEAGES[0]]
    material = subject.joint_material(
        subject.table_for(lineage.profiles["a"]),
        subject.table_for(lineage.profiles["b"]),
    )
    parsed = json.loads(material)
    assert len(parsed["retained_effect_tables"]) == 2
    assert {
        json.loads(table)["controller_family"]
        for table in parsed["retained_effect_tables"]
    } == {profile.controller_family for profile in lineage.profiles.values()}


def test_malformed_output_is_not_engaged(tmp_path):
    packet = subject.execute(lambda body: provider("bad"), tmp_path / "bad")
    assert packet["accumulation_verdict"]["class"] == "not_engaged"
    assert packet["logical_calls"] == 600


def test_smoke_path_makes_no_contact(capsys):
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "mode": "smoke_no_contact",
        "planned_logical_calls": 600,
        "side_effects_entered": False,
    }
