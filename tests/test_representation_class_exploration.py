import json

from contact import representation_class_exploration as subject


def provider(content):
    return 200, json.dumps({
        "choices": [{"message": {"content": content}}],
        "usage": {"completion_tokens": 3, "prompt_tokens": 11},
    }).encode()


def request_record(body):
    envelope = json.loads(body)
    return envelope, json.loads(envelope["messages"][1]["content"].split("\n", 1)[1].rsplit("\n", 1)[0])


def fake_transport(body):
    envelope, record = request_record(body)
    system = envelope["messages"][0]["content"]
    if "AUTHORSHIP REQUEST" in envelope["messages"][1]["content"]:
        world = next(
            world for world in subject.WORLD_DATA.values()
            if world.profile.controller_family == record["occurrence"]["public_device"]["controller_family"]
        )
        representation_format = next(key for key in subject.FORMATS if f"REPRESENTATION_FORMAT: {key}" in system)
        opposite = record["external_result"] == subject.WITHHELD_SENTINEL
        return provider(subject.expected_representation(world, representation_format, opposite=opposite))

    containing_world = next(
        world for world in subject.WORLD_DATA.values()
        if record["device"]["device"] in {
            world.acquisition.device,
            *(state.device for state in subject.all_cases(world).values()),
        }
    )
    state = next(
        (state for state in subject.all_cases(containing_world).values() if state.device == record["device"]["device"]),
        containing_world.acquisition,
    )
    material = record["retained_material"]
    opposite = any(
        material == subject.expected_representation(containing_world, representation_format, opposite=True)
        for representation_format in subject.FORMATS
    )
    if material and not opposite:
        action = state.controls[1] if state.target > state.position else state.controls[0]
    else:
        action = state.controls[0] if state.target > state.position else state.controls[1]
    return provider(json.dumps({"action": action}))


def test_frozen_surfaces_and_schedule():
    assert subject.PLANNED_LOGICAL_CALLS == 190
    assert len(subject.later_schedule()) == 176
    assert set(subject.FORMATS) == {"relation_sentence", "effect_table", "target_policy"}
    assert all(
        sum(row[1:] == (name, case, condition) for row in subject.later_schedule()) == 4
        for name in subject.WORLDS
        for case, conditions in (
            *((case, subject.MATCHING_CONDITIONS) for case in subject.MATCHING_CASES),
            *((case, subject.NONMATCHING_CONDITIONS) for case in subject.NONMATCHING_CASES),
        )
        for condition in conditions
    )


def test_expected_forms_contain_no_device_action_tokens():
    for world in subject.WORLD_DATA.values():
        for representation_format in subject.FORMATS:
            content = subject.expected_representation(world, representation_format)
            assert world.profile.controller_family in content
            assert all(action not in content for state in subject.all_cases(world).values() for action in state.controls)
        assert subject.expected_representation(world, "effect_table").startswith("{")
        assert subject.expected_representation(world, "target_policy").startswith("{")


def test_scope_gate_can_remove_every_nonmatching_candidate_byte():
    candidates = {
        (name, exposure, representation_format): subject.expected_representation(
            subject.WORLD_DATA[name], representation_format, opposite=exposure == subject.WITHHELD
        )
        for name in subject.WORLDS for exposure in (subject.EXPOSED, subject.WITHHELD)
        for representation_format in subject.FORMATS
    }
    for name in subject.WORLDS:
        world = subject.WORLD_DATA[name]
        for state in world.nonmatching_cases.values():
            assert state.controller_family != world.profile.controller_family
            assert all(
                "" == (candidates[(name, subject.EXPOSED, representation_format)] if state.controller_family == world.profile.controller_family else "")
                for representation_format in subject.FORMATS
            )


def test_fake_packet_finds_all_three_bidirectional_candidates_and_replays(tmp_path):
    directory = tmp_path / "evidence"
    packet = subject.execute(fake_transport, directory)
    assert packet["logical_calls"] == packet["physical_attempts"] == 190
    assert packet["retries"] == 0
    assert packet["representation_trial_verdict"] == {
        "class": "candidate_found",
        "scope": "representation_class_exploration",
    }
    assert packet["formation_verdict"] is None
    assert all(row["status"] == "bidirectional_candidate" for row in packet["representation_findings"].values())
    assert all(len(row["ungated_harmful_cells"]) == 4 for row in packet["representation_findings"].values())
    assert subject.replay_evidence(directory) == packet


def test_malformed_outputs_do_not_create_a_candidate(tmp_path):
    packet = subject.execute(lambda body: provider("not-json"), tmp_path / "invalid")
    assert packet["representation_trial_verdict"]["class"] == "null"
    assert all(row["status"] == "not_authored" for row in packet["representation_findings"].values())
    assert packet["logical_calls"] == 190


def test_transport_retry_is_bounded_and_replayable(tmp_path):
    first = True

    def flaky(body):
        nonlocal first
        if first:
            first = False
            raise ConnectionError("temporary")
        return fake_transport(body)

    directory = tmp_path / "retry"
    packet = subject.execute(flaky, directory)
    assert packet["logical_calls"] == 190
    assert packet["physical_attempts"] == 191
    assert packet["retries"] == 1
    assert subject.replay_evidence(directory) == packet


def test_default_cli_is_no_contact_smoke(capsys):
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "mode": "smoke_no_contact",
        "planned_logical_calls": 190,
        "side_effects_entered": False,
    }
