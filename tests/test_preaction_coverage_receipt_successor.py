import json

from contact import preaction_coverage_receipt_successor as subject
from micro_environment import knowledge_cost_interaction as domain


def provider(content: str):
    return 200, json.dumps({
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 15, "completion_tokens": 5},
    }).encode()


def request_record(body: bytes):
    envelope = json.loads(body)
    user = envelope["messages"][1]["content"]
    record = json.loads(user.split("\n", 1)[1].rsplit("\n", 1)[0])
    return envelope, record


def state_for_device(device_id: str, cost_mode: str):
    for (device_class, candidate_cost), state in subject.parent.STATES.items():
        if state.device == device_id and candidate_cost == cost_mode:
            return device_class, state
    raise AssertionError(device_id)


def fake_transport(body: bytes):
    envelope, record = request_record(body)
    assert envelope["messages"][0]["content"] == subject.parent.PARTICIPANT_SYSTEM
    device = record["device"]
    _, state = state_for_device(device["device"], device["diagnostic_cost"])
    material = record["retained_material"]

    if record["action_number"] == 1:
        if "PRE-ACTION COVERAGE RECEIPT" in material:
            receipt = json.loads(material.split("PRE-ACTION COVERAGE RECEIPT\n\n")[1])
            action = (
                state.diagnostic_control
                if not receipt["uncovered_signals"]
                else domain.HOLD
            )
        else:
            action = (
                state.diagnostic_control
                if device["diagnostic_cost"] == domain.FREE or material
                else state.task_controls[0]
            )
        return provider(json.dumps({"action": action}))

    lines = material.splitlines()
    receipt = json.loads(lines[1])
    if not receipt["applicable_record_ids"]:
        return provider(json.dumps({"action": domain.HOLD}))
    signal = receipt["observed_signal"]
    line = next(line for line in lines if f"signal is {signal}" in line)
    slot = (
        domain.FIRST_SLOT
        if "first displayed task control completes" in line
        else domain.SECOND_SLOT
    )
    return provider(json.dumps({
        "action": state.task_controls[0 if slot == domain.FIRST_SLOT else 1]
    }))


def test_specimen_freezes_parent_model_schedule_budget_and_stopping():
    specimen = subject.specimen()
    assert specimen["parent_packet_sha256"] == subject.PARENT_PACKET_SHA256
    assert specimen["parent_verdict"]["class"] == "harmful"
    assert specimen["model"] == subject.base.MODEL
    assert specimen["model_digest"] == subject.base.MODEL_DIGEST
    assert subject.EPISODES == 96
    assert subject.LOGICAL_CALL_CEILING == 192
    assert subject.PHYSICAL_CALL_CEILING == 204
    assert len(subject.schedule()) == 96


def test_coverage_receipt_is_exact_and_contains_no_action_advice():
    _, learned = subject.load_parent()
    covered_state = subject.parent.STATES[(subject.COVERED, domain.COSTLY)]
    uncovered_state = subject.parent.STATES[(subject.UNCOVERED, domain.COSTLY)]
    covered = subject.coverage_value(covered_state.diagnostic_alphabet, learned)
    uncovered = subject.coverage_value(uncovered_state.diagnostic_alphabet, learned)
    removed = subject.coverage_value(covered_state.diagnostic_alphabet, [])
    assert covered["uncovered_signals"] == []
    assert uncovered["uncovered_signals"] == list(uncovered_state.diagnostic_alphabet)
    assert removed["uncovered_signals"] == list(covered_state.diagnostic_alphabet)
    material = subject.coverage_material(uncovered_state, learned)
    receipt_text = material.split("PRE-ACTION COVERAGE RECEIPT\n\n")[1]
    assert "diagnostic_control" not in receipt_text
    assert "task_control" not in receipt_text
    assert "hold" not in receipt_text
    assert "recommend" not in receipt_text


def test_reversed_records_are_fully_covering_before_action():
    state = subject.parent.STATES[(subject.COVERED, domain.COSTLY)]
    correct = subject.coverage_value(
        state.diagnostic_alphabet, subject.parent.supplied_records()
    )
    reversed_value = subject.coverage_value(
        state.diagnostic_alphabet, subject.parent.reversed_records()
    )
    assert correct["uncovered_signals"] == reversed_value["uncovered_signals"] == []
    assert set(correct["matching_record_ids_by_signal"]) == set(
        reversed_value["matching_record_ids_by_signal"]
    )


def test_fake_successor_supports_selective_costly_probing():
    packet = subject.execute(fake_transport)
    assert packet["episode_count"] == 96
    assert packet["logical_calls"] == 150
    assert packet["physical_attempts"] == 150
    assert packet["exploration_verdict"]["class"] == "supported"
    outcomes = packet["outcomes"]
    for branch in {
        subject.LEARNED_RECEIPT,
        subject.SUPPLIED_RECEIPT,
        subject.REVERSED_RECEIPT,
    }:
        assert outcomes[branch][subject.COVERED]["probed_first"] == 6
        assert outcomes[branch][subject.UNCOVERED]["held_first"] == 6
    assert outcomes[subject.REMOVAL_RECEIPT][subject.COVERED]["held_first"] == 6
    assert outcomes[subject.REMOVAL_RECEIPT][subject.UNCOVERED]["held_first"] == 6
    assert outcomes[subject.LEARNED_RECEIPT][subject.COVERED]["completed"] == 6
    assert outcomes[subject.REVERSED_RECEIPT][subject.COVERED]["failed"] == 6
    assert packet["formation_verdict"] is None


def test_parent_controls_and_new_request_identities_are_exact():
    packet = subject.execute(fake_transport)
    assert packet["components"] == {
        "exact_coverage_assignments": 48,
        "exact_learned_records": 2,
        "exact_parent_first_request_hashes": 48,
    }
    assert packet["request_identity"] == {
        "learned_supplied_receipt_pairs": 12
    }


def test_exact_replay(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet


def test_default_cli_makes_no_contact(monkeypatch, capsys):
    monkeypatch.setattr(
        subject.parent.clerk.learned,
        "collect_provider_receipt",
        lambda: (_ for _ in ()).throw(AssertionError("contact")),
    )
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "episode_count": 96,
        "logical_call_ceiling": 192,
        "mode": "smoke_no_contact",
        "side_effects_entered": False,
    }
