from dataclasses import asdict

import pytest

from contact import governed_diagnostic_policy_specimen as subject
from formation import diagnostic_policy as policy
from micro_environment import knowledge_cost_interaction as domain


def test_policy_uses_only_public_state_and_admitted_records():
    state, records = subject.CONDITION_INPUTS[subject.LEARNED]
    public = policy.public_state_value(state)
    decision = policy.decide_diagnostic(state, records)
    assert public["diagnostic_alphabet"] == list(state.diagnostic_alphabet)
    assert public["diagnostic_cost"] == domain.COSTLY
    assert "profile_id" not in public
    assert "valid_task_slot" not in public
    assert "observed_signal" not in public
    assert decision.authority == policy.RUNTIME_GOVERNOR
    assert decision.policy_version == policy.POLICY_VERSION


def test_learned_records_are_bound_to_the_retained_admitted_source():
    packet = subject.build_packet()
    assert packet["retained_source_packet_sha256"] == (
        subject.prior.PREDECESSOR_PACKET_SHA256
    )
    assert packet["retained_source_records"] == list(subject.RETAINED_SOURCE_RECORDS)
    assert tuple(record.diagnostic_signal for record in subject.LEARNED_RECORDS) == tuple(
        record["diagnostic_signal"] for record in subject.RETAINED_SOURCE_RECORDS
    )


@pytest.mark.parametrize(
    "condition", [subject.LEARNED, subject.SUPPLIED, subject.REVERSED]
)
def test_complete_coverage_authorizes_without_inspecting_correctness(condition):
    state, records = subject.CONDITION_INPUTS[condition]
    decision = policy.decide_diagnostic(state, records)
    assert decision.disposition == policy.AUTHORIZE
    assert decision.reason == policy.COMPLETE_COVERAGE
    assert decision.missing_signals == ()
    assert tuple(signal for signal, _record_id in decision.exact_matches) == (
        state.diagnostic_alphabet
    )
    assert policy.authorized_diagnostic_control(decision, state, records) == (
        state.diagnostic_control
    )


@pytest.mark.parametrize("condition", [subject.REMOVAL, subject.UNCOVERED])
def test_missing_coverage_withholds_without_an_environment_action(condition):
    state, records = subject.CONDITION_INPUTS[condition]
    before = asdict(state)
    decision = policy.decide_diagnostic(state, records)
    assert decision.disposition == policy.WITHHOLD
    assert decision.reason == policy.INCOMPLETE_COVERAGE
    assert decision.missing_signals == state.diagnostic_alphabet
    assert policy.authorized_diagnostic_control(decision, state, records) is None
    assert asdict(state) == before
    assert state.service_window == domain.AVAILABLE


def test_record_order_does_not_change_the_decision():
    state, records = subject.CONDITION_INPUTS[subject.LEARNED]
    assert policy.decide_diagnostic(state, records) == policy.decide_diagnostic(
        state, tuple(reversed(records))
    )


def test_authorization_binds_state_and_complete_record_set():
    state, records = subject.CONDITION_INPUTS[subject.LEARNED]
    decision = policy.decide_diagnostic(state, records)
    with pytest.raises(policy.DiagnosticPolicyRefusal, match="stale_or_mismatched"):
        policy.authorized_diagnostic_control(
            decision, state, subject.REVERSED_RECORDS
        )
    with pytest.raises(policy.DiagnosticPolicyRefusal, match="initial_public_state"):
        profile = subject.parent.PROFILES[(subject.parent.COVERED, subject.parent.PROFILE_0)]
        result = domain.apply_action(state, profile, state.diagnostic_control)
        policy.authorized_diagnostic_control(decision, result.state_after, records)


@pytest.mark.parametrize("profile_name", subject.parent.PROFILE_NAMES)
def test_environment_emits_signal_then_exactly_one_considered_record_is_selected(
    profile_name,
):
    state, records = subject.CONDITION_INPUTS[subject.LEARNED]
    profile = subject.parent.PROFILES[(subject.parent.COVERED, profile_name)]
    decision = policy.decide_diagnostic(state, records)
    control = policy.authorized_diagnostic_control(decision, state, records)
    result = domain.apply_action(state, profile, control)
    selected = policy.select_observed_record(decision, state, records, result)
    assert result.information_acquired
    assert result.service_window_consumed
    assert selected.observed_signal == result.diagnostic_signal
    assert selected.record.record_id in decision.considered_record_ids
    assert selected.record.diagnostic_signal == result.diagnostic_signal


def test_correctness_changes_later_outcome_but_not_authorization():
    packet = subject.build_packet()
    dispositions = {
        condition: packet["decisions"][condition]["decision"]["disposition"]
        for condition in (subject.LEARNED, subject.SUPPLIED, subject.REVERSED)
    }
    assert set(dispositions.values()) == {policy.AUTHORIZE}
    for profile in subject.parent.PROFILE_NAMES:
        assert packet["trajectories"][f"{subject.LEARNED}:{profile}"][
            "task_result_from_deterministic_interpreter"
        ]["task_status_after"] == domain.COMPLETED
        assert packet["trajectories"][f"{subject.REVERSED}:{profile}"][
            "task_result_from_deterministic_interpreter"
        ]["task_status_after"] == domain.FAILED


def test_ambiguous_malformed_stale_and_mismatched_inputs_fail_closed():
    witnesses = subject.refusal_witnesses()
    assert len(witnesses) == 9
    assert all(witnesses.values())


def test_specimen_conforms_without_model_or_formation_claim():
    packet = subject.build_packet()
    assert packet["logical_model_calls"] == 0
    assert packet["formation_verdict"] is None
    assert packet["specimen_verdict"] == {
        "class": "conforms",
        "finding": "governed_diagnostic_encounter_mechanism_available",
        "scope": "governed_diagnostic_policy_specimen",
    }
    assert packet["scores"] == {
        "authorization_collapse": 1,
        "correct_later_outcomes": 1,
        "costly_transitions": 1,
        "input_immutable": 1,
        "no_hidden_fields": 1,
        "order_independent": 1,
        "refusals_exact": 9,
        "reversed_later_outcomes": 1,
        "withholding_exact": 1,
    }


def test_exact_replay(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.write_evidence(evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet
