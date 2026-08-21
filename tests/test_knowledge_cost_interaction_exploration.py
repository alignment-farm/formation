import json

from contact import knowledge_cost_interaction_exploration as subject
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
    for (device_class, candidate_cost), state in subject.STATES.items():
        if state.device == device_id and candidate_cost == cost_mode:
            return device_class, state
    raise AssertionError(device_id)


def fake_transport(body: bytes):
    envelope, record = request_record(body)
    assert envelope["messages"][0]["content"] == subject.PARTICIPANT_SYSTEM
    device = record["device"]
    device_class, state = state_for_device(
        device["device"], device["diagnostic_cost"]
    )
    material = record["retained_material"]

    if record["action_number"] == 1:
        catalog_covers = (
            material.startswith("SIGNAL RECORD CATALOG")
            and all(signal in material for signal in device["diagnostic_alphabet"])
        )
        action = (
            state.diagnostic_control
            if device["diagnostic_cost"] == domain.FREE or catalog_covers
            else domain.HOLD
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


def test_specimen_freezes_question_model_schedule_budget_and_sources():
    specimen = subject.specimen()
    assert specimen["model"] == subject.base.MODEL
    assert specimen["model_digest"] == subject.base.MODEL_DIGEST
    assert specimen["instrument_packet_sha256"] == subject.INSTRUMENT_PACKET_SHA256
    assert specimen["receipt_packet_sha256"] == subject.RECEIPT_PACKET_SHA256
    assert specimen["frozen_predictions"] == list(subject.instrument.FROZEN_PREDICTIONS)
    assert subject.EPISODES == 72
    assert subject.LOGICAL_CALL_CEILING == 144
    assert subject.PHYSICAL_CALL_CEILING == 156
    assert len(subject.schedule()) == 72


def test_public_state_exposes_alphabet_and_cost_but_not_hidden_answer():
    for state in subject.STATES.values():
        public = subject.public_state(state)
        assert public["diagnostic_alphabet"] == list(state.diagnostic_alphabet)
        assert public["diagnostic_cost"] == state.diagnostic_cost
        assert "profile" not in public
        assert "valid_task_slot" not in public
        assert public["observed_signal"] is None


def test_initial_catalog_and_post_probe_receipt_boundaries():
    _, _, learned = subject.load_sources()
    learned_material = subject.render_catalog(learned)
    assert learned_material == subject.render_catalog(subject.supplied_records())
    assert "APPLICABILITY MATCH RECEIPT" not in learned_material
    covered, ids = subject.receipt_material(
        subject.instrument.COVERED_ALPHABET[0], learned
    )
    assert len(ids) == 1
    assert "MATCHING RETAINED SIGNAL RECORDS" in covered
    uncovered, ids = subject.receipt_material(
        subject.instrument.UNCOVERED_ALPHABET[0], learned
    )
    assert ids == []
    assert "MATCHING RETAINED SIGNAL RECORDS" not in uncovered
    assert "task control" not in uncovered


def test_fake_contact_supports_knowledge_cost_interaction():
    packet = subject.execute(fake_transport)
    assert packet["episode_count"] == 72
    assert packet["logical_calls"] == 114
    assert packet["physical_attempts"] == 114
    assert packet["exploration_verdict"]["class"] == "supported"
    covered = subject.COVERED
    uncovered = subject.UNCOVERED
    outcomes = packet["outcomes"]
    assert outcomes[subject.LEARNED_COSTLY][covered]["probed_first"] == 6
    assert outcomes[subject.REMOVAL_COSTLY][covered]["probed_first"] == 0
    assert outcomes[subject.SUPPLIED_COSTLY][covered]["probed_first"] == 6
    assert outcomes[subject.REVERSED_COSTLY][covered]["probed_first"] == 6
    assert outcomes[subject.REVERSED_COSTLY][covered]["failed"] == 6
    assert outcomes[subject.LEARNED_COSTLY][uncovered]["probed_first"] == 0
    assert outcomes[subject.REMOVAL_FREE][covered]["probed_first"] == 6
    assert outcomes[subject.REMOVAL_FREE][uncovered]["probed_first"] == 6
    assert packet["formation_verdict"] is None


def test_first_and_second_action_scores_remain_separate():
    packet = subject.execute(fake_transport)
    for branch in subject.BRANCHES:
        for device_class in subject.DEVICE_CLASSES:
            outcome = packet["outcomes"][branch][device_class]
            assert set(outcome) == {
                "completed",
                "direct_task_first",
                "failed",
                "held_first",
                "post_probe_task_attempts",
                "probed_first",
                "service_windows_consumed",
                "trials",
                "unfinished",
            }
            assert outcome["trials"] == 6


def test_request_identities_and_exact_replay(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert packet["request_identity"] == {
        "learned_supplied_initial_pairs": 12
    }
    assert subject.replay_evidence(evidence_dir) == packet


def test_default_cli_makes_no_contact(monkeypatch, capsys):
    monkeypatch.setattr(
        subject.clerk.learned,
        "collect_provider_receipt",
        lambda: (_ for _ in ()).throw(AssertionError("contact")),
    )
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "episode_count": 72,
        "logical_call_ceiling": 144,
        "mode": "smoke_no_contact",
        "side_effects_entered": False,
    }
