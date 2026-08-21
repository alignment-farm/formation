from dataclasses import asdict

import pytest

from contact import knowledge_cost_interaction_specimen as subject
from micro_environment import knowledge_cost_interaction as domain


@pytest.mark.parametrize("device_class", subject.DEVICE_CLASSES)
@pytest.mark.parametrize("cost_mode", domain.COST_MODES)
def test_public_state_is_identical_across_hidden_profiles(device_class, cost_mode):
    state = subject.STATES[(device_class, cost_mode)]
    hashes = {
        subject.base.sha256(subject.base.canonical_json_bytes(asdict(state)))
        for _profile_name in subject.PROFILE_NAMES
    }
    assert len(hashes) == 1
    assert state.diagnostic_alphabet == (
        subject.COVERED_ALPHABET
        if device_class == subject.COVERED
        else subject.UNCOVERED_ALPHABET
    )


@pytest.mark.parametrize("device_class", subject.DEVICE_CLASSES)
@pytest.mark.parametrize("cost_mode", domain.COST_MODES)
def test_task_controls_have_opposite_terminal_results(device_class, cost_mode):
    state = subject.STATES[(device_class, cost_mode)]
    first_results = [
        domain.apply_action(
            state, subject.PROFILES[(device_class, profile_name)], state.task_controls[0]
        ).task_status_after
        for profile_name in subject.PROFILE_NAMES
    ]
    second_results = [
        domain.apply_action(
            state, subject.PROFILES[(device_class, profile_name)], state.task_controls[1]
        ).task_status_after
        for profile_name in subject.PROFILE_NAMES
    ]
    assert first_results == [domain.COMPLETED, domain.FAILED]
    assert second_results == [domain.FAILED, domain.COMPLETED]


@pytest.mark.parametrize("device_class", subject.DEVICE_CLASSES)
@pytest.mark.parametrize("cost_mode", domain.COST_MODES)
def test_first_action_hold_is_terminal_and_free(device_class, cost_mode):
    state = subject.STATES[(device_class, cost_mode)]
    result = domain.apply_action(
        state, subject.PROFILES[(device_class, subject.PROFILE_0)], domain.HOLD
    )
    assert result.phase_after == domain.TERMINAL
    assert result.task_status_after == domain.HELD
    assert result.abstained
    assert not result.information_acquired
    assert not result.service_window_consumed
    assert result.service_window_after == domain.AVAILABLE


@pytest.mark.parametrize(
    ("cost_mode", "expected_window", "expected_consumed"),
    [
        (domain.COSTLY, domain.CONSUMED, True),
        (domain.FREE, domain.AVAILABLE, False),
    ],
)
def test_probe_cost_is_an_exact_window_transition(
    cost_mode, expected_window, expected_consumed
):
    state = subject.STATES[(subject.COVERED, cost_mode)]
    result = domain.apply_action(
        state,
        subject.PROFILES[(subject.COVERED, subject.PROFILE_0)],
        state.diagnostic_control,
    )
    assert result.information_acquired
    assert result.task_status_after == domain.INTACT
    assert result.service_window_after == expected_window
    assert result.service_window_consumed is expected_consumed


def test_covered_receipts_match_and_uncovered_receipts_are_empty():
    for signal in subject.COVERED_ALPHABET:
        receipt = subject.exact_match_receipt(signal)
        assert len(receipt["applicable_record_ids"]) == 1
    for signal in subject.UNCOVERED_ALPHABET:
        receipt = subject.exact_match_receipt(signal)
        assert receipt["applicable_record_ids"] == []


def test_post_diagnostic_allows_one_terminal_action_and_refuses_second_probe():
    state = subject.STATES[(subject.COVERED, domain.COSTLY)]
    profile = subject.PROFILES[(subject.COVERED, subject.PROFILE_0)]
    probe = domain.apply_action(state, profile, state.diagnostic_control)
    repeated = domain.apply_action(
        probe.state_after, profile, state.diagnostic_control
    )
    assert repeated.disposition == domain.REFUSED
    assert repeated.reason == "diagnostic_already_used"
    task = domain.apply_action(
        probe.state_after, profile, state.task_controls[0]
    )
    assert task.task_status_after == domain.COMPLETED
    after_terminal = domain.apply_action(task.state_after, profile, domain.HOLD)
    assert after_terminal.disposition == domain.REFUSED
    assert after_terminal.reason == "terminal_episode"


def test_cost_mode_and_semantics_are_equal_across_device_classes():
    for cost_mode in domain.COST_MODES:
        covered = subject.STATES[(subject.COVERED, cost_mode)]
        uncovered = subject.STATES[(subject.UNCOVERED, cost_mode)]
        assert covered.diagnostic_cost == uncovered.diagnostic_cost == cost_mode
        covered_result = domain.apply_action(
            covered,
            subject.PROFILES[(subject.COVERED, subject.PROFILE_0)],
            covered.diagnostic_control,
        )
        uncovered_result = domain.apply_action(
            uncovered,
            subject.PROFILES[(subject.UNCOVERED, subject.PROFILE_0)],
            uncovered.diagnostic_control,
        )
        assert covered_result.service_window_after == uncovered_result.service_window_after
        assert covered_result.service_window_consumed == uncovered_result.service_window_consumed


def test_malformed_states_profiles_actions_and_receipts_refuse():
    witnesses = subject.refusal_witnesses()
    assert len(witnesses) == 10
    assert all(witnesses.values())


def test_specimen_conforms_with_frozen_predictions_and_separate_scores():
    packet = subject.build_packet()
    assert packet["frozen_predictions"] == list(subject.FROZEN_PREDICTIONS)
    assert packet["proposed_contact_conditions"] == list(subject.PROPOSED_CONDITIONS)
    assert packet["scores"] == {
        "cost_equal_across_devices": 1,
        "cost_transitions_exact": 1,
        "distinct_outcome_fields": 1,
        "distinct_repeat_objects": 1,
        "first_action_holds_terminal": 1,
        "input_immutable": 1,
        "order_independent": 1,
        "post_diagnostic_rules_exact": 1,
        "profile_public_identities": 4,
        "receipt_assignments_exact": 1,
        "refusals_exact": 10,
        "repeat_values_equal": 1,
        "task_outcomes_exact": 1,
    }
    assert packet["specimen_verdict"]["class"] == "conforms"
    assert packet["formation_verdict"] is None
    assert packet["logical_model_calls"] == 0


def test_input_is_immutable_and_repeat_results_are_distinct():
    state = subject.STATES[(subject.COVERED, domain.COSTLY)]
    profile = subject.PROFILES[(subject.COVERED, subject.PROFILE_0)]
    before = asdict(state)
    first = domain.apply_action(state, profile, state.diagnostic_control)
    second = domain.apply_action(state, profile, state.diagnostic_control)
    assert asdict(state) == before
    assert first == second
    assert first is not second
    assert first.state_after is not second.state_after


def test_exact_replay(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.write_evidence(evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet
