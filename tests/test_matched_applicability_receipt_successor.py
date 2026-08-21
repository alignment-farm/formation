import json

from contact import matched_applicability_receipt_successor as subject
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
    return envelope, record


def state_for_device(device_id: str):
    for state in subject.prior.STATES.values():
        if state.device == device_id:
            return state
    raise AssertionError(device_id)


def fake_transport(body: bytes):
    envelope, record = request_record(body)
    assert envelope["messages"][0]["content"] == subject.prior.PARTICIPANT_SYSTEM
    state = state_for_device(record["device"]["device"])
    signal = record["prior_external_results"][-1]["diagnostic_signal"]
    material = record["retained_material"]

    if material.startswith("APPLICABILITY MATCH RECEIPT"):
        receipt = json.loads(material.splitlines()[1])
        if not receipt["applicable_record_ids"]:
            return provider(json.dumps({"action": domain.HOLD}))

    matching_lines = [
        line for line in material.splitlines() if f"signal is {signal}" in line
    ]
    if not matching_lines:
        return provider(json.dumps({"action": state.task_controls[0]}))
    slot = (
        domain.FIRST_SLOT
        if "first displayed task control completes" in matching_lines[0]
        else domain.SECOND_SLOT
    )
    return provider(json.dumps({
        "action": state.task_controls[0 if slot == domain.FIRST_SLOT else 1]
    }))


def test_specimen_binds_both_parents_and_exact_interface():
    specimen = subject.specimen()
    assert specimen["harmful_parent_packet_sha256"] == (
        subject.first_receipt.PREDECESSOR_PACKET_SHA256
    )
    assert specimen["not_engaged_parent_packet_sha256"] == subject.RECEIPT_PACKET_SHA256
    assert subject.PLANNED_LOGICAL_CALLS == 144
    assert subject.PHYSICAL_CALL_CEILING == 156
    assert len(subject.schedule()) == 144


def test_empty_receipt_material_contains_no_action_or_record_text():
    material = subject.receipt_material(domain.UNMAPPED, [])
    lines = material.splitlines()
    assert lines[0] == "APPLICABILITY MATCH RECEIPT"
    assert json.loads(lines[1]) == {
        "applicable_record_ids": [],
        "observed_signal": domain.UNMAPPED,
    }
    assert "MATCHING RETAINED SIGNAL RECORDS" not in material
    assert "task control" not in material


def test_fake_successor_supports_matched_empty_receipt():
    packet = subject.execute(fake_transport)
    assert packet["logical_calls"] == 144
    assert packet["physical_attempts"] == 144
    assert packet["components"] == {
        "exact_parent_control_request_hashes": 72,
        "exact_record_assignments": 144,
        "exact_retained_records": 2,
        "exact_shared_diagnostics": 8,
    }
    assert packet["request_identity"] == {
        "learned_supplied_receipt_pairs": 24,
        "silent_no_record_pairs": 24,
        "unmapped_receipt_groups": 6,
    }
    assert {
        branch: outcome["completed"]
        for branch, outcome in packet["matching_outcomes"].items()
    } == {
        subject.FULL: 18,
        subject.SILENT: 9,
        subject.RECEIPT: 18,
        subject.NO_RECORD: 9,
        subject.SUPPLIED_RECEIPT: 18,
        subject.REVERSED_RECEIPT: 0,
    }
    assert packet["matching_outcomes"][subject.REVERSED_RECEIPT]["failed"] == 18
    assert packet["unmapped_outcomes"][subject.FULL]["task_attempts"] == 6
    assert packet["unmapped_outcomes"][subject.SILENT]["task_attempts"] == 6
    assert packet["unmapped_outcomes"][subject.RECEIPT] == {
        "completed": 0,
        "diagnostic": 0,
        "failed": 0,
        "hold": 6,
        "task_attempts": 0,
    }
    assert packet["validation_verdict"]["class"] == "supported"
    assert packet["formation_verdict"] is None


def test_parent_control_hashes_match_retained_requests():
    packet = subject.execute(fake_transport)
    controls = [
        row for row in packet["calls"]
        if row["expected_parent_request_sha256"] is not None
    ]
    assert len(controls) == 72
    assert all(
        row["request_sha256"] == row["expected_parent_request_sha256"]
        for row in controls
    )


def test_exact_replay(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.execute(fake_transport, evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet


def test_default_cli_makes_no_contact(monkeypatch, capsys):
    monkeypatch.setattr(
        subject.clerk_contact.learned,
        "collect_provider_receipt",
        lambda: (_ for _ in ()).throw(AssertionError("contact")),
    )
    assert subject.main([]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "mode": "smoke_no_contact",
        "planned_logical_calls": 144,
        "side_effects_entered": False,
    }
