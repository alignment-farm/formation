import json
from contact import staged_observation_authorship as subject


def provider(content):
    return 200, json.dumps({"choices": [{"message": {"content": content}}], "usage": {"prompt_tokens": 9, "completion_tokens": 3}}).encode()


def fake_transport(body):
    env = json.loads(body); user = env["messages"][1]["content"]; record = json.loads(user.split("\n", 1)[1].rsplit("\n", 1)[0])
    if user.startswith("ACTION REQUEST"):
        world = next(w for w in subject.WORLD_DATA.values() if w.acquisition.device == record["device"]["device"]); state = world.acquisition; action = state.controls[0] if state.target > state.position else state.controls[1]; return provider(json.dumps({"action": action}))
    if user.startswith("OBSERVATION REQUEST"):
        world = next(w for w in subject.WORLD_DATA.values() if w.profile.controller_family == record["occurrence"]["public_device"]["controller_family"]); result = record["external_result"]; return provider(subject.expected_observation(world, result["selected_slot"], result["movement_direction"]))
    family = (record.get("public_device") or record["occurrence"]["public_device"])["controller_family"]
    world = next(w for w in subject.WORLD_DATA.values() if w.profile.controller_family == family)
    if "authored_observation" in record:
        return provider(subject.expected_table(world) if record["authored_observation"] else subject.expected_table(world, opposite=True))
    selected = record["external_result"]["selected_slot"]
    return provider(subject.expected_table(world, opposite=selected == "second"))


def test_schedule_is_frozen():
    assert subject.PLANNED_LOGICAL_CALLS == 88
    assert len(subject.final_schedule()) == 72
    assert all(sum(row[1:] == (name, condition) for row in subject.final_schedule()) == 3 for name in subject.WORLDS for condition in subject.CONDITIONS)


def test_fake_packet_supports_staged_mechanism_and_replays(tmp_path):
    directory = tmp_path / "evidence"; packet = subject.execute(fake_transport, directory)
    assert packet["logical_calls"] == packet["physical_attempts"] == 88
    assert packet["exact_observations"] == 8
    assert packet["selected_slot_counts"] == {"first": 4, "second": 4}
    assert packet["staged_authorship_verdict"]["class"] == "candidate_found"
    assert subject.replay_evidence(directory) == packet


def test_malformed_is_not_engaged(tmp_path):
    packet = subject.execute(lambda body: provider("bad"), tmp_path / "bad")
    assert packet["staged_authorship_verdict"]["class"] == "not_engaged"


def test_default_cli_no_contact(capsys):
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {"mode": "smoke_no_contact", "planned_logical_calls": 88, "side_effects_entered": False}
