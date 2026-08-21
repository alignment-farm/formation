import json

from contact import asymmetric_probe_clerical_contact as subject
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
    return envelope, user, record


def state_for_device(device_id: str):
    for state in subject.LATER_STATES.values():
        if state.device == device_id:
            return state
    raise AssertionError(device_id)


def fake_transport(body: bytes):
    envelope, user, record = request_record(body)
    if envelope["model"] == subject.learned.INSTRUMENT_MODEL:
        if user.startswith("DIAGNOSTIC RESULT"):
            return provider(json.dumps({
                "diagnostic_signal": record["diagnostic_signal"],
            }))
        if user.startswith("TASK RESULT"):
            return provider(json.dumps({
                "selected_task_slot": domain.FIRST_SLOT,
                "task_outcome": (
                    domain.COMPLETED
                    if record["observation"] == domain.TASK_COMPLETED
                    else domain.FAILED
                ),
            }))
        if user.startswith("SIGNAL RECORD REQUEST"):
            signal = json.loads(record["diagnostic_transcript"])[
                "diagnostic_signal"
            ]
            task = json.loads(record["task_transcript"])
            valid_slot = task["selected_task_slot"]
            if task["task_outcome"] == domain.FAILED:
                valid_slot = (
                    domain.SECOND_SLOT
                    if valid_slot == domain.FIRST_SLOT
                    else domain.FIRST_SLOT
                )
            return provider(json.dumps({
                "diagnostic_signal": signal,
                "valid_task_slot": valid_slot,
            }))
        raise AssertionError(user)

    state = state_for_device(record["device"]["device"])
    material = record["retained_material"]
    action = state.task_controls[0]
    if "second displayed task control completes" in material:
        action = state.task_controls[1]
    return provider(json.dumps({"action": action}))


def test_specimen_has_frozen_budget_and_publicly_identical_world_pairs():
    specimen = subject.specimen()
    assert specimen["domain_packet_sha256"] == subject.DOMAIN_PACKET_SHA256
    assert subject.PLANNED_LOGICAL_CALLS == 222
    assert subject.PHYSICAL_CALL_CEILING == 234
    assert len(subject.post_schedule()) == 216
    assert len(subject.MATCHING_CASES) == 4
    assert len(subject.HELD_CASES) == 2
    for case in specimen["cases"].values():
        assert len(set(case["world_expected_task_actions"].values())) == 2


def test_gate_rejects_a_bad_model_record():
    world = subject.PROFILE_0
    artifact = subject.expected_record(world)
    bad = {**artifact, "valid_task_slot": domain.SECOND_SLOT}
    decision = subject.admission_decision(
        {"diagnostic_signal": subject.WORLD_SIGNALS[world]},
        {
            "action_role": "first_task_control",
            "observation": domain.TASK_COMPLETED,
        },
        {"diagnostic_signal": subject.WORLD_SIGNALS[world]},
        {
            "selected_task_slot": domain.FIRST_SLOT,
            "task_outcome": domain.COMPLETED,
        },
        bad,
    )
    assert decision["status"] == "quarantined"
    assert decision["reasons"] == ["record_valid_slot_mismatch"]


def test_fake_contact_supports_the_signal_record_mechanism():
    packet = subject.execute(fake_transport)
    assert packet["logical_calls"] == 222
    assert packet["physical_attempts"] == 222
    assert packet["components"] == {
        "admitted_signal_records": 2,
        "exact_later_assignments": 216,
        "exact_later_diagnostics": 8,
        "exact_later_holds": 4,
        "exact_signal_records": 2,
        "exact_signal_transcriptions": 2,
        "exact_source_results": 4,
        "exact_task_transcriptions": 2,
        "held_cases_without_selection": 4,
        "matching_signal_selections": 8,
        "opposite_signal_records": True,
    }
    assert packet["request_identity"] == {
        "held_no_signal_groups": 12,
        "learned_supplied_matching_pairs": 24,
    }
    assert packet["matching_completions"] == {
        subject.COLD: 12,
        subject.RAW: 12,
        subject.LEARNED: 24,
        subject.REMOVED: 12,
        subject.SUPPLIED: 24,
        subject.OPPOSITE: 0,
    }
    assert packet["matching_failures"][subject.LEARNED] == 0
    assert packet["held_failure_delta"] == 0
    assert packet["validation_verdict"]["class"] == "supported"
    assert packet["formation_verdict"] is None


def test_matching_and_held_request_identities_are_real():
    packet = subject.execute(fake_transport)
    rows = [
        row for row in packet["calls"]
        if row["responsibility"] == "participant_task_action"
    ]
    for repeat in range(1, subject.REPEATS + 1):
        for world in subject.WORLDS:
            for case in subject.MATCHING_CASES:
                hashes = {
                    row["request_sha256"] for row in rows
                    if row["repeat"] == repeat
                    and row["world"] == world
                    and row["case"] == case
                    and row["branch"] in {subject.LEARNED, subject.SUPPLIED}
                }
                assert len(hashes) == 1
            for case in subject.HELD_CASES:
                hashes = {
                    row["request_sha256"] for row in rows
                    if row["repeat"] == repeat
                    and row["world"] == world
                    and row["case"] == case
                    and row["branch"] in {
                        subject.LEARNED,
                        subject.REMOVED,
                        subject.SUPPLIED,
                        subject.OPPOSITE,
                    }
                }
                assert len(hashes) == 1


def test_exact_replay(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet


def test_default_cli_makes_no_contact(monkeypatch, capsys):
    monkeypatch.setattr(
        subject.learned,
        "collect_provider_receipt",
        lambda: (_ for _ in ()).throw(AssertionError("contact")),
    )
    assert subject.main([]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output == {
        "mode": "smoke_no_contact",
        "planned_logical_calls": 222,
        "side_effects_entered": False,
    }
