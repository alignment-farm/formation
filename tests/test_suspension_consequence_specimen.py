from contact import suspension_consequence_specimen as subject


def test_specimen_exposes_symmetric_action_information_equivalence():
    packet = subject.build_packet()
    assert packet["scores"] == {
        "cold_second_control_actions": 12,
        "exact_strategy_outcomes": 6,
        "non_hold_hit_distributions_distinct": True,
        "public_mirror_identities": 2,
    }
    assert packet["specimen_verdict"] == {
        "class": "conforms",
        "finding": "symmetric_action_information_equivalence",
        "scope": "suspension_consequence_specimen",
    }
    assert packet["logical_model_calls"] == 0
    assert packet["formation_verdict"] is None


def test_all_non_hold_responses_share_aggregate_cost():
    outcomes = subject.build_packet()["outcomes"]
    for strategy in (
        subject.CURRENT, subject.NEWEST, subject.COLD, subject.EXPLORE
    ):
        assert outcomes[strategy] == {
            "holds": 0,
            "informative_action_moves_away": 6,
            "informative_action_target_hits": 6,
            "relations_resolved": 12,
            "total_actions_to_target": 24,
            "trials": 12,
            "unfinished_trials": 0,
        }


def test_non_hold_responses_allocate_risk_to_different_cells():
    hit_cells = subject.build_packet()["strategy_hit_cells"]
    distributions = {
        tuple(map(tuple, hit_cells[strategy]))
        for strategy in (
            subject.CURRENT, subject.NEWEST, subject.COLD, subject.EXPLORE
        )
    }
    assert len(distributions) == 4


def test_hold_has_no_information_and_hold_then_explore_adds_one_step_each():
    outcomes = subject.build_packet()["outcomes"]
    assert outcomes[subject.HOLD_ONLY]["relations_resolved"] == 0
    assert outcomes[subject.HOLD_ONLY]["unfinished_trials"] == 12
    assert outcomes[subject.HOLD_EXPLORE]["total_actions_to_target"] == 36
    assert outcomes[subject.EXPLORE]["total_actions_to_target"] == 24


def test_exact_replay(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.write_evidence(evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet
