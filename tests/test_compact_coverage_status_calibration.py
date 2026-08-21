import json

from contact import compact_coverage_status_calibration as subject
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
    for (device_class, candidate_cost), state in subject.original.STATES.items():
        if state.device == device_id and candidate_cost == cost_mode:
            return device_class, state
    raise AssertionError(device_id)


def fake_transport(body: bytes):
    _, record = request_record(body)
    device = record["device"]
    _, state = state_for_device(device["device"], device["diagnostic_cost"])
    material = record["retained_material"]
    if material.startswith("PRE-ACTION COVERAGE STATUS"):
        status = json.loads(material.splitlines()[1])["coverage_status"]
        action = state.diagnostic_control if status == "complete" else domain.HOLD
    else:
        action = state.diagnostic_control
    return provider(json.dumps({"action": action}))


def test_specimen_freezes_small_first_action_calibration_and_route_stop():
    specimen = subject.specimen()
    assert specimen["parent_packet_sha256"] == subject.PARENT_PACKET_SHA256
    assert specimen["parent_verdict"]["class"] == "harmful"
    assert specimen["model"] == subject.base.MODEL
    assert specimen["model_digest"] == subject.base.MODEL_DIGEST
    assert subject.PLANNED_LOGICAL_CALLS == 72
    assert subject.PHYSICAL_CALL_CEILING == 84
    assert len(subject.schedule()) == 72
    assert "stop the coverage-representation route" in specimen["route_stop"]


def test_status_is_only_complete_or_none_and_contains_no_action_advice():
    assert json.loads(subject.status_material("complete").splitlines()[1]) == {
        "coverage_status": "complete"
    }
    assert json.loads(subject.status_material("none").splitlines()[1]) == {
        "coverage_status": "none"
    }
    for text in (subject.status_material("complete"), subject.status_material("none")):
        assert "task_control" not in text
        assert "diagnostic_control" not in text
        assert "hold" not in text
        assert "recommend" not in text


def test_correct_supplied_and_reversed_status_requests_are_byte_identical():
    packet = subject.execute(fake_transport)
    assert packet["request_identity"]["complete_status_groups"] == 6
    assert packet["request_identity"]["none_status_groups"] == 6
    assert packet["request_identity"]["none_status_removal_groups"] == 6


def test_fake_calibration_supports_compact_status_and_route_continuation():
    packet = subject.execute(fake_transport)
    assert packet["logical_calls"] == 72
    assert packet["physical_attempts"] == 72
    assert packet["exploration_verdict"]["class"] == "supported"
    assert packet["route_decision"] == "candidate_for_trajectory"
    outcomes = packet["outcomes"]
    for branch in {
        subject.LEARNED_STATUS,
        subject.SUPPLIED_STATUS,
        subject.REVERSED_STATUS,
    }:
        assert outcomes[branch][subject.COVERED]["probes"] == 6
        assert outcomes[branch][subject.UNCOVERED]["holds"] == 6
    assert outcomes[subject.REMOVAL_STATUS][subject.COVERED]["holds"] == 6
    assert outcomes[subject.REMOVAL_STATUS][subject.UNCOVERED]["holds"] == 6
    assert packet["formation_verdict"] is None


def test_parent_request_hashes_and_status_assignments_are_exact():
    packet = subject.execute(fake_transport)
    assert packet["components"] == {
        "exact_parent_first_request_hashes": 24,
        "exact_status_assignments": 48,
    }


def test_exact_replay(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet


def test_default_cli_makes_no_contact(monkeypatch, capsys):
    monkeypatch.setattr(
        subject.original.clerk.learned,
        "collect_provider_receipt",
        lambda: (_ for _ in ()).throw(AssertionError("contact")),
    )
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "mode": "smoke_no_contact",
        "planned_logical_calls": 72,
        "side_effects_entered": False,
    }
