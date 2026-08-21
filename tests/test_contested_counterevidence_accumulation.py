import pytest

from contact import contested_counterevidence_accumulation as subject


def test_all_four_histories_reach_distinct_frozen_states():
    packet = subject.build_packet()
    assert packet["scores"] == {
        "exact_governance_states": 4,
        "exact_ordered_lineages": 4,
        "total_histories": 4,
    }
    assert {
        name: decision["governance_state"]
        for name, decision in packet["decisions"].items()
    } == subject.EXPECTED
    assert packet["specimen_verdict"]["class"] == "conforms"
    assert packet["formation_verdict"] is None
    assert packet["logical_model_calls"] == 0


def test_decisions_preserve_sources_instead_of_only_counts():
    packet = subject.build_packet()
    repeated = packet["decisions"]["repeated_contradiction"]
    corrected = packet["decisions"]["self_correcting"]
    contested = packet["decisions"]["contested_movement"]
    assert repeated["contradicting_occurrence_ids"] == ["repeat:1", "repeat:2"]
    assert repeated["active_record"] == subject.OPPOSITE
    assert corrected["closed_uncorroborated_occurrence_ids"] == ["corrected:1"]
    assert corrected["supporting_current_occurrence_ids"] == ["corrected:2"]
    assert contested["unresolved_occurrence_ids"] == ["contested:1"]
    assert contested["active_record"] is None


def test_noncontiguous_order_refuses():
    history = [dict(subject.HISTORIES["repeated_contradiction"][0], order=2)]
    with pytest.raises(subject.AccumulationRefusal, match="noncontiguous_occurrence_order"):
        subject.decide(history)


def test_exact_replay(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.write_evidence(evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet
