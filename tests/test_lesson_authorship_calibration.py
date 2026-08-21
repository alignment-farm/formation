import json

from contact import lesson_authorship_calibration as subject


def provider(content):
    return 200, json.dumps({"choices": [{"message": {"content": content}}], "usage": {"prompt_tokens": 9, "completion_tokens": 3}}).encode()


def fake_transport(body):
    envelope = json.loads(body)
    user = envelope["messages"][1]["content"]
    record = json.loads(user.split("\n", 1)[1].rsplit("\n", 1)[0])
    if user.startswith("AUTHORSHIP REQUEST"):
        world = next(w for w in subject.WORLD_DATA.values() if w.profile.controller_family == record["occurrence"]["public_device"]["controller_family"])
        fmt = next(f for f in subject.FORMATS if f"REPRESENTATION_FORMAT: {f}" in envelope["messages"][0]["content"])
        return provider(subject.expected(world, fmt, opposite=record["external_result"] == subject.forms.WITHHELD_SENTINEL))
    world = next(w for w in subject.WORLD_DATA.values() if w.acquisition.device == record["device"]["device"])
    state = world.acquisition
    action = state.controls[0] if state.target > state.position else state.controls[1]
    return provider(json.dumps({"action": action}))


def test_schedule_and_forms_are_frozen():
    assert subject.PLANNED_LOGICAL_CALLS == 104
    assert len(subject.authorship_schedule()) == 96
    assert all(sum(row[1:] == (name, fmt, exposure) for row in subject.authorship_schedule()) == 3 for name in subject.WORLDS for fmt in subject.FORMATS for exposure in subject.EXPOSURES)


def test_fake_packet_finds_both_candidates_and_replays(tmp_path):
    directory = tmp_path / "evidence"
    packet = subject.execute(fake_transport, directory)
    assert packet["logical_calls"] == packet["physical_attempts"] == 104
    assert packet["selected_slot_counts"] == {"first": 4, "second": 4}
    assert packet["authorship_verdict"]["class"] == "candidate_found"
    assert all(row["status"] == "authorship_candidate" for row in packet["authorship_findings"].values())
    assert packet["formation_verdict"] is None
    assert subject.replay_evidence(directory) == packet


def test_malformed_output_is_null(tmp_path):
    packet = subject.execute(lambda body: provider("not-json"), tmp_path / "invalid")
    assert packet["authorship_verdict"]["class"] == "not_engaged"
    assert all(row["status"] == "not_reliable" for row in packet["authorship_findings"].values())


def test_retry_replays(tmp_path):
    first = True
    def flaky(body):
        nonlocal first
        if first:
            first = False
            raise ConnectionError("temporary")
        return fake_transport(body)
    directory = tmp_path / "retry"
    packet = subject.execute(flaky, directory)
    assert packet["physical_attempts"] == 105 and packet["retries"] == 1
    assert subject.replay_evidence(directory) == packet


def test_default_cli_is_no_contact(capsys):
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {"mode": "smoke_no_contact", "planned_logical_calls": 104, "side_effects_entered": False}
