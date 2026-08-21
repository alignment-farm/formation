import json

import pytest

from contact import composed_clerical_record_admission as subject


def source_items(pair_class: str):
    packet, _ = subject.load_projection_evidence()
    _, pairs, cases, transcriptions = subject.source_material()
    call = next(row for row in packet["calls"] if row["pair_class"] == pair_class)
    pair = pairs[call["pair_id"]]
    case = cases[call["pair_id"]]
    transcript = transcriptions[pair.sensory_request_sha256]["content"]
    return pair, case, transcript, call["model_effect"]


def test_retained_composition_conforms_without_model_calls():
    packet = subject.execute()
    assert packet["model_calls"] == 0
    assert packet["bindings_complete"] is True
    assert packet["verdict"]["class"] == "conforms"
    assert packet["formation_verdict"] is None
    assert packet["class_scores"]["old_supported"] == {
        "admitted": 12, "assigned": 12, "correct": 12, "quarantined": 0,
    }
    assert packet["class_scores"]["revision_supported"] == {
        "admitted": 12, "assigned": 12, "correct": 12, "quarantined": 0,
    }
    assert packet["class_scores"]["stale_contradicted"] == {
        "admitted": 0, "assigned": 12, "correct": 12, "quarantined": 12,
    }
    assert packet["class_scores"]["missing_movement"] == {
        "admitted": 0, "assigned": 12, "correct": 12, "quarantined": 12,
    }


def test_stale_and_missing_proposals_fail_different_checks():
    packet = subject.execute()
    stale_reasons = {
        tuple(item["reasons"])
        for item in packet["decisions"]
        if item["pair_class"] == "stale_contradicted"
    }
    hidden_reasons = {
        tuple(item["reasons"])
        for item in packet["decisions"]
        if item["pair_class"] == "missing_movement"
    }
    assert stale_reasons == {("claimed_effect_mismatch",)}
    assert hidden_reasons == {("movement_direction_missing",)}
    assert all(
        item["active_version"] == 1
        for item in packet["decisions"]
        if item["status"] == subject.QUARANTINED
    )


def test_projector_and_transcription_mismatches_are_quarantined():
    pair, case, transcript, effect = source_items("revision_supported")
    opposite = (
        subject.learned.DECREASES
        if effect == subject.learned.INCREASES
        else subject.learned.INCREASES
    )
    projected = subject.compose_decision(pair, case, transcript, opposite)
    assert projected["status"] == subject.QUARANTINED
    assert "projected_field_mismatch" in projected["reasons"]

    transcript_value = json.loads(transcript)
    transcript_value["observed_effect"] = opposite
    changed_transcript = subject.base.canonical_json_bytes(transcript_value).decode()
    transcribed = subject.compose_decision(pair, case, changed_transcript, effect)
    assert transcribed["status"] == subject.QUARANTINED
    assert "transcribed_effect_mismatch" in transcribed["reasons"]


def test_evidence_write_and_exact_replay(tmp_path):
    output_dir = tmp_path / "evidence"
    packet = subject.execute()
    subject.write_evidence(output_dir, packet)
    assert subject.replay_evidence(output_dir) == packet

    retained = json.loads((output_dir / "packet.json").read_bytes())
    retained["bindings_complete"] = False
    (output_dir / "packet.json").write_bytes(subject.admission.canonical(retained))
    with pytest.raises(subject.CompositionRefusal, match="deterministic_replay_mismatch"):
        subject.replay_evidence(output_dir)
