from dataclasses import replace
import json

import pytest

from contact import source_grounded_revision_admission as subject


def retained_pair(condition: str = "revised"):
    packet, requests = subject.load_source()
    call = next(
        row
        for row in packet["calls"]
        if row["responsibility"] == "revision_transcription"
        and row["consequence_condition"] == condition
    )
    return subject.build_pair(packet, requests, call)


def test_retained_source_diagnostic_conforms_without_model_calls():
    packet = subject.execute()
    assert packet["model_calls"] == 0
    assert packet["exposed_admitted"] == 4
    assert packet["hidden_quarantined"] == 4
    assert packet["bindings_complete"] is True
    assert packet["verdict"]["class"] == "conforms"
    assert packet["formation_verdict"] is None
    assert all(
        item["active_version"] == (2 if item["condition"] == "revised" else 1)
        for item in packet["decisions"]
    )


def test_same_claim_depends_on_source_completeness_not_helpfulness():
    packet = subject.execute()
    source_comparator = packet["same_claim_source_comparator"]
    assert source_comparator["complete_source_status"] == subject.ADMITTED
    assert source_comparator["missing_movement_status"] == subject.QUARANTINED
    assert source_comparator["missing_movement_reasons"] == [
        "movement_direction_missing"
    ]
    semantic_comparator = packet["semantic_blindness_comparator"]
    assert semantic_comparator["original_claim_status"] == subject.ADMITTED
    assert semantic_comparator["inverted_claim_status"] == subject.ADMITTED
    assert semantic_comparator["original_claim_sha256"] != semantic_comparator[
        "inverted_claim_sha256"
    ]


def test_exact_request_and_occurrence_bindings_are_required():
    receipt, proposal = retained_pair()
    assert subject.decide(receipt, proposal)["status"] == subject.ADMITTED

    wrong_request = replace(proposal, sensory_request_sha256="0" * 64)
    request_decision = subject.decide(receipt, wrong_request)
    assert request_decision["status"] == subject.QUARANTINED
    assert request_decision["reasons"] == ["sensory_request_mismatch"]

    wrong_occurrence = replace(proposal, source_occurrence_sha256="1" * 64)
    occurrence_decision = subject.decide(receipt, wrong_occurrence)
    assert occurrence_decision["status"] == subject.QUARANTINED
    assert occurrence_decision["reasons"] == ["source_occurrence_mismatch"]


def test_missing_measurement_and_incomplete_record_cannot_supersede_old_version():
    hidden_receipt, hidden_proposal = retained_pair("hidden")
    hidden_decision = subject.decide(hidden_receipt, hidden_proposal)
    assert hidden_decision["status"] == subject.QUARANTINED
    assert hidden_decision["active_version"] == 1
    assert hidden_decision["active_record_version_id"] == hidden_proposal.old_record_version_id

    exposed_receipt, exposed_proposal = retained_pair()
    malformed = replace(exposed_proposal, record={"first_control_effect": subject.learned.INCREASES})
    malformed_decision = subject.decide(exposed_receipt, malformed)
    assert malformed_decision["status"] == subject.QUARANTINED
    assert malformed_decision["reasons"] == ["record_structure_incomplete"]
    assert malformed_decision["active_version"] == 1


def test_evidence_write_and_exact_replay(tmp_path):
    output_dir = tmp_path / "evidence"
    packet = subject.execute()
    subject.write_evidence(output_dir, packet)
    assert subject.replay_evidence(output_dir) == packet

    retained = json.loads((output_dir / "packet.json").read_bytes())
    retained["hidden_quarantined"] = 3
    (output_dir / "packet.json").write_bytes(subject.canonical(retained))
    with pytest.raises(subject.AdmissionDiagnosticRefusal, match="deterministic_replay_mismatch"):
        subject.replay_evidence(output_dir)
