import json

from contact import explicit_applicability_receipt_contact as subject
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
    assert user.startswith("POST-DIAGNOSTIC ACTION REQUEST")
    state = state_for_device(record["device"]["device"])
    signal = record["diagnostic_result"]["diagnostic_signal"]
    material = record["retained_material"]
    receipt = record["applicability_receipt"]

    if receipt is not None and not receipt["applicable_record_ids"]:
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
    action = state.task_controls[0 if slot == domain.FIRST_SLOT else 1]
    return provider(json.dumps({"action": action}))


def test_specimen_freezes_cases_and_budget():
    specimen = subject.specimen()
    assert specimen["predecessor_packet_sha256"] == subject.PREDECESSOR_PACKET_SHA256
    assert subject.PLANNED_LOGICAL_CALLS == 144
    assert subject.PHYSICAL_CALL_CEILING == 156
    assert len(subject.schedule()) == 144
    assert len(specimen["learned_catalog"]) == 2
    for case in specimen["cases"].values():
        assert len(set(
            world["expected_task_action"] for world in case["worlds"].values()
        )) == 2


def test_exact_match_receipt_names_no_action_and_can_be_empty():
    _, records = subject.clerk_packet_and_records()
    state = subject.STATES[subject.UNMAPPED_CASES[0]]
    result = subject.exposed_result(domain.apply_action(
        state,
        subject.profile_for(state, subject.prior.UNMAPPED_0),
        state.diagnostic_control,
    ))
    material, receipt, selected = subject.branch_input(
        subject.RECEIPT, result["diagnostic_signal"], records
    )
    assert material == ""
    assert selected == []
    assert receipt == {
        "applicable_record_ids": [],
        "observed_signal": domain.UNMAPPED,
    }
    assert all("action" not in key for key in receipt)


def test_fake_contact_supports_explicit_empty_receipt():
    packet = subject.execute(fake_transport)
    assert packet["logical_calls"] == 144
    assert packet["physical_attempts"] == 144
    assert packet["components"] == {
        "exact_record_assignments": 144,
        "exact_retained_records": 2,
        "exact_shared_diagnostics": 8,
    }
    assert packet["request_identity"] == {
        "learned_supplied_receipt_pairs": 24,
        "unmapped_receipt_groups": 6,
        "unmapped_silent_pairs": 6,
    }
    assert {
        branch: outcome["completed"]
        for branch, outcome in packet["matching_outcomes"].items()
    } == {
        subject.FULL: 18,
        subject.SELECTED_SILENT: 18,
        subject.RECEIPT: 18,
        subject.REMOVED: 9,
        subject.SUPPLIED_RECEIPT: 18,
        subject.REVERSED_RECEIPT: 0,
    }
    assert packet["matching_outcomes"][subject.REVERSED_RECEIPT]["failed"] == 18
    assert packet["unmapped_outcomes"][subject.FULL]["task_attempts"] == 6
    assert packet["unmapped_outcomes"][subject.SELECTED_SILENT]["task_attempts"] == 6
    assert packet["unmapped_outcomes"][subject.RECEIPT] == {
        "completed": 0,
        "diagnostic": 0,
        "failed": 0,
        "hold": 6,
        "task_attempts": 0,
    }
    assert packet["validation_verdict"]["class"] == "supported"
    assert packet["formation_verdict"] is None


def test_silent_and_receipt_request_identities_are_real():
    packet = subject.execute(fake_transport)
    calls = packet["calls"]
    for repeat in range(1, subject.REPEATS + 1):
        for case_name in subject.CASES:
            for world in subject.worlds_for(case_name):
                learned_supplied = {
                    row["request_sha256"] for row in calls
                    if row["repeat"] == repeat
                    and row["case"] == case_name
                    and row["world"] == world
                    and row["branch"] in {subject.RECEIPT, subject.SUPPLIED_RECEIPT}
                }
                assert len(learned_supplied) == 1
    for repeat in range(1, subject.REPEATS + 1):
        for case_name in subject.UNMAPPED_CASES:
            for world in subject.worlds_for(case_name):
                receipt_hashes = {
                    row["request_sha256"] for row in calls
                    if row["repeat"] == repeat
                    and row["case"] == case_name
                    and row["world"] == world
                    and row["branch"] in {
                        subject.RECEIPT,
                        subject.SUPPLIED_RECEIPT,
                        subject.REVERSED_RECEIPT,
                    }
                }
                silent_hashes = {
                    row["request_sha256"] for row in calls
                    if row["repeat"] == repeat
                    and row["case"] == case_name
                    and row["world"] == world
                    and row["branch"] in {
                        subject.SELECTED_SILENT,
                        subject.REMOVED,
                    }
                }
                assert len(receipt_hashes) == 1
                assert len(silent_hashes) == 1


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
