import json

from contact import self_directed_probe_contact as subject
from micro_environment import asymmetric_suspension as domain


def provider(content: str):
    return 200, json.dumps({
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 15, "completion_tokens": 5},
    }).encode()


def request_record(body: bytes):
    envelope = json.loads(body)
    user = envelope["messages"][1]["content"]
    record = json.loads(user.split("\n", 1)[1].rsplit("\n", 1)[0])
    return user, record


def state_for_device(device_id: str):
    for state in subject.STATES.values():
        if state.device == device_id:
            return state
    raise AssertionError(device_id)


def fake_transport(body: bytes):
    user, record = request_record(body)
    assert user.startswith("DEVICE ACTION REQUEST")
    state = state_for_device(record["device"]["device"])
    material = record["retained_material"]

    if record["action_number"] == 1:
        action = (
            state.diagnostic_control
            if material.startswith("SIGNAL RECORD CATALOG")
            else state.task_controls[0]
        )
        return provider(json.dumps({"action": action}))

    signal = record["prior_external_results"][-1]["diagnostic_signal"]
    if signal == domain.UNMAPPED:
        return provider(json.dumps({"action": domain.HOLD}))
    line = next(
        line for line in material.splitlines() if f"signal is {signal}" in line
    )
    slot = (
        domain.FIRST_SLOT
        if "first displayed task control completes" in line
        else domain.SECOND_SLOT
    )
    action = state.task_controls[0 if slot == domain.FIRST_SLOT else 1]
    return provider(json.dumps({"action": action}))


def test_specimen_freezes_episode_and_call_ceilings():
    specimen = subject.specimen()
    assert specimen["predecessor_packet_sha256"] == subject.PREDECESSOR_PACKET_SHA256
    assert subject.EPISODES == 144
    assert subject.LOGICAL_CALL_CEILING == 288
    assert subject.PHYSICAL_CALL_CEILING == 300
    assert len(subject.episode_schedule()) == 144
    assert len(subject.MATCHING_CASES) == 3
    assert len(subject.UNMAPPED_CASES) == 1
    for case in specimen["cases"].values():
        assert len(set(
            world["expected_task_action"] for world in case["worlds"].values()
        )) == 2


def test_unmapped_signal_preserves_state_without_naming_a_task_slot():
    state = subject.STATES[subject.UNMAPPED_CASES[0]]
    for world in subject.UNMAPPED_WORLDS:
        result = domain.apply_action(
            state, subject.profile_for(state, world), state.diagnostic_control
        )
        assert result.status_after == domain.INTACT
        assert result.diagnostic_signal == domain.UNMAPPED
        assert result.observation == domain.DIAGNOSTIC_OBSERVED


def test_fake_contact_supports_self_directed_probe_use():
    packet = subject.execute(fake_transport)
    assert packet["episode_count"] == 144
    assert packet["logical_calls"] == 216
    assert packet["physical_attempts"] == 216
    assert packet["components"] == {
        "applied_environment_results": 216,
        "exact_environment_results": 216,
        "exact_predecessor_records": 2,
        "public_profile_pair_identities": 4,
    }
    assert packet["initial_request_identity"] == {
        "cold_removal_pairs": 24,
        "learned_supplied_pairs": 24,
    }
    assert {
        branch: {
            key: value for key, value in outcome.items()
            if key in {"completed", "diagnostic_first", "failed", "unfinished"}
        }
        for branch, outcome in packet["matching_outcomes"].items()
    } == {
        subject.COLD: {
            "completed": 9, "diagnostic_first": 0, "failed": 9, "unfinished": 0
        },
        subject.RAW: {
            "completed": 9, "diagnostic_first": 0, "failed": 9, "unfinished": 0
        },
        subject.LEARNED: {
            "completed": 18, "diagnostic_first": 18, "failed": 0, "unfinished": 0
        },
        subject.REMOVED: {
            "completed": 9, "diagnostic_first": 0, "failed": 9, "unfinished": 0
        },
        subject.SUPPLIED: {
            "completed": 18, "diagnostic_first": 18, "failed": 0, "unfinished": 0
        },
        subject.REVERSED: {
            "completed": 0, "diagnostic_first": 18, "failed": 18, "unfinished": 0
        },
    }
    assert packet["unmapped_outcomes"][subject.LEARNED] == {
        "completed": 0,
        "diagnostic_first": 6,
        "failed": 0,
        "post_signal_task_attempts": 0,
        "unfinished": 6,
    }
    assert packet["validation_verdict"]["class"] == "supported"
    assert packet["formation_verdict"] is None


def test_terminal_first_actions_stop_while_probes_receive_a_second_call():
    packet = subject.execute(fake_transport)
    episodes = packet["episodes"]
    assert all(
        row["call_count"] == 1
        for row in episodes
        if row["branch"] in {subject.COLD, subject.RAW, subject.REMOVED}
    )
    assert all(
        row["call_count"] == 2
        for row in episodes
        if row["branch"] in {subject.LEARNED, subject.SUPPLIED, subject.REVERSED}
    )


def test_initial_request_identities_are_real():
    packet = subject.execute(fake_transport)
    calls = [row for row in packet["calls"] if row["action_number"] == 1]
    for repeat in range(1, subject.REPEATS + 1):
        for case_name in subject.CASES:
            for world in subject.worlds_for(case_name):
                learned_supplied = {
                    row["request_sha256"] for row in calls
                    if row["repeat"] == repeat
                    and row["case"] == case_name
                    and row["world"] == world
                    and row["branch"] in {subject.LEARNED, subject.SUPPLIED}
                }
                cold_removed = {
                    row["request_sha256"] for row in calls
                    if row["repeat"] == repeat
                    and row["case"] == case_name
                    and row["world"] == world
                    and row["branch"] in {subject.COLD, subject.REMOVED}
                }
                assert len(learned_supplied) == 1
                assert len(cold_removed) == 1


def test_exact_replay_and_no_contact_default(tmp_path, monkeypatch, capsys):
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet

    monkeypatch.setattr(
        subject.predecessor.learned,
        "collect_provider_receipt",
        lambda: (_ for _ in ()).throw(AssertionError("contact")),
    )
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "episode_count": 144,
        "logical_call_ceiling": 288,
        "mode": "smoke_no_contact",
        "side_effects_entered": False,
    }
