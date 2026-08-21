import pytest

from contact import uncertain_consequence_policy_specimen as subject


def test_specimen_exposes_frozen_tradeoff():
    packet = subject.build_packet()
    assert {
        policy: result["aggregate"]
        for policy, result in packet["policy_results"].items()
    } == subject.EXPECTED_AGGREGATE
    assert packet["source_preservation"] == {
        subject.IMMEDIATE: 5,
        subject.TWO_CONFIRMATION: 5,
    }
    assert packet["specimen_verdict"] == {
        "class": "conforms",
        "finding": "tradeoff_exposed",
        "scope": "uncertain_consequence_policy_specimen",
    }
    assert packet["logical_model_calls"] == 0
    assert packet["formation_verdict"] is None


def test_hidden_truth_is_absent_from_governor_receipts():
    for rows in subject.HISTORIES.values():
        public = subject.public_receipts(rows)
        assert all("hidden_relation_for_scoring" not in row for row in public)
        for policy in subject.POLICIES:
            transitions = subject.apply_policy(policy, public)
            assert transitions[-1]["considered_occurrence_ids"] == [
                row["event_id"] for row in rows
            ]


def test_clean_change_and_unresolved_interruption_have_declared_delays():
    packet = subject.build_packet()["policy_results"]
    assert packet[subject.IMMEDIATE]["histories"]["clean_lasting_change"][
        "scores"
    ]["adaptation_delay"] == 0
    assert packet[subject.TWO_CONFIRMATION]["histories"]["clean_lasting_change"][
        "scores"
    ]["adaptation_delay"] == 1
    assert packet[subject.TWO_CONFIRMATION]["histories"][
        "change_interrupted_unresolved"
    ]["scores"]["adaptation_delay"] == 3


def test_noncontiguous_history_refuses():
    rows = subject.public_receipts(subject.HISTORIES["clean_lasting_change"])
    rows[1] = {**rows[1], "order": 3}
    with pytest.raises(subject.PolicySpecimenRefusal, match="noncontiguous"):
        subject.apply_policy(subject.TWO_CONFIRMATION, rows)


def test_exact_replay(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.write_evidence(evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet
