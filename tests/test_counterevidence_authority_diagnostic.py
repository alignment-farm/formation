import pytest

from contact import counterevidence_authority_diagnostic as subject


def test_two_runtime_visible_policies_are_distinct():
    packet = subject.build_packet()
    assert packet["scores"] == {
        "action_attributed_admissions": 3,
        "action_attribution_labels_exact": 4,
        "complete_sources": 4,
        "contradicted_selected_effect_claims": 4,
        "observation_grounded_admissions": 4,
        "total": 4,
    }
    assert packet["diagnostic_verdict"]["class"] == "conforms"
    assert packet["formation_verdict"] is None
    assert packet["logical_model_calls"] == 0


def test_only_nonattributed_occurrence_changes_policy_decision():
    rows = {row["lineage"]: row for row in subject.build_packet()["rows"]}
    assert all(row["source_complete"] for row in rows.values())
    assert all(row["claim_contradicted"] for row in rows.values())
    assert all(
        row["observation_grounded_policy"] == "admitted"
        for row in rows.values()
    )
    assert rows["engagement_04"]["action_attributed"] is False
    assert rows["engagement_04"]["action_attributed_policy"] == "quarantined"
    assert all(
        row["action_attributed_policy"] == "admitted"
        for name, row in rows.items() if name != "engagement_04"
    )


def test_source_hash_mismatch_refuses(monkeypatch):
    monkeypatch.setattr(subject, "SOURCE_PACKET_SHA256", "0" * 64)
    with pytest.raises(
        subject.AuthorityDiagnosticRefusal,
        match="source_packet_hash_mismatch",
    ):
        subject.source_material()


def test_exact_replay(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.write_evidence(evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet
