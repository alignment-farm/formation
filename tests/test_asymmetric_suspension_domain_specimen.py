from dataclasses import asdict

import pytest

from contact import asymmetric_suspension_domain_specimen as subject
from micro_environment import asymmetric_suspension as domain


def test_same_task_action_completes_one_profile_and_fails_the_other():
    first = subject.PUBLIC_STATE.task_controls[0]
    profile_0 = domain.apply_action(
        subject.PUBLIC_STATE, subject.PROFILES["profile_0"], first
    )
    profile_1 = domain.apply_action(
        subject.PUBLIC_STATE, subject.PROFILES["profile_1"], first
    )
    assert profile_0.status_after == domain.COMPLETED
    assert profile_1.status_after == domain.FAILED
    assert profile_0.observation == domain.TASK_COMPLETED
    assert profile_1.observation == domain.TASK_FAILED


def test_probe_preserves_state_and_emits_profile_signal():
    results = {
        name: domain.apply_action(
            subject.PUBLIC_STATE, profile, subject.PUBLIC_STATE.diagnostic_control
        )
        for name, profile in subject.PROFILES.items()
    }
    assert results["profile_0"].diagnostic_signal == domain.STEADY
    assert results["profile_1"].diagnostic_signal == domain.PULSED
    assert all(result.status_after == domain.INTACT for result in results.values())
    assert all(result.step_cost == 1 for result in results.values())


def test_hold_preserves_state_without_information():
    result = domain.apply_action(
        subject.PUBLIC_STATE, subject.PROFILES["profile_0"], domain.HOLD
    )
    assert result.status_after == domain.INTACT
    assert result.observation == domain.HELD
    assert result.diagnostic_signal is None


@pytest.mark.parametrize("status", [domain.COMPLETED, domain.FAILED])
def test_terminal_state_refuses_without_mutation(status):
    terminal = domain.SuspensionState(
        subject.PUBLIC_STATE.device,
        subject.PUBLIC_STATE.task_controls,
        subject.PUBLIC_STATE.diagnostic_control,
        status,
    )
    result = domain.apply_action(
        terminal, subject.PROFILES["profile_0"], subject.PUBLIC_STATE.diagnostic_control
    )
    assert result.disposition == domain.REFUSED
    assert result.status_before == result.status_after == status
    assert result.step_cost == 0


def test_profile_mismatch_and_unknown_action_refuse():
    wrong_profile = domain.SuspensionProfile(
        "other", "profile", domain.FIRST_SLOT, domain.STEADY
    )
    with pytest.raises(domain.AsymmetricSuspensionRefusal, match="profile_device"):
        domain.apply_action(subject.PUBLIC_STATE, wrong_profile, domain.HOLD)
    with pytest.raises(domain.AsymmetricSuspensionRefusal, match="unknown_action"):
        domain.apply_action(
            subject.PUBLIC_STATE, subject.PROFILES["profile_0"], "unknown"
        )


def test_controls_are_distinct_and_cannot_reuse_hold():
    with pytest.raises(domain.AsymmetricSuspensionRefusal, match="distinct"):
        domain.SuspensionState("device", ("same", "same"), "diagnostic")
    with pytest.raises(domain.AsymmetricSuspensionRefusal, match="distinct"):
        domain.SuspensionState("device", (domain.HOLD, "second"), "diagnostic")


def test_specimen_conforms_and_preserves_public_identity():
    packet = subject.build_packet()
    assert packet["task_matrix"] == {
        "profile_0": [domain.COMPLETED, domain.FAILED],
        "profile_1": [domain.FAILED, domain.COMPLETED],
    }
    assert packet["scores"] == {
        "diagnostic_transitions_exact": 1,
        "distinct_repeat_objects": 1,
        "hold_transitions_exact": 1,
        "input_immutable": 1,
        "order_independent": 1,
        "probe_trajectories_exact": 1,
        "public_state_identities": 1,
        "refusals_exact": 8,
        "repeat_values_equal": 1,
        "task_transitions_exact": 1,
        "terminal_refusals_exact": 1,
    }
    assert packet["specimen_verdict"]["class"] == "conforms"
    assert packet["formation_verdict"] is None


def test_probe_then_interpreted_action_completes_both_profiles():
    packet = subject.build_packet()
    assert all(
        row["probe"]["status_after"] == domain.INTACT
        and row["task"]["status_after"] == domain.COMPLETED
        and row["total_step_cost"] == 2
        for row in packet["probe_trajectories"].values()
    )


def test_input_state_is_immutable_and_repeat_results_are_distinct():
    before = asdict(subject.PUBLIC_STATE)
    first = domain.apply_action(
        subject.PUBLIC_STATE,
        subject.PROFILES["profile_0"],
        subject.PUBLIC_STATE.diagnostic_control,
    )
    second = domain.apply_action(
        subject.PUBLIC_STATE,
        subject.PROFILES["profile_0"],
        subject.PUBLIC_STATE.diagnostic_control,
    )
    assert asdict(subject.PUBLIC_STATE) == before
    assert first == second
    assert first is not second


def test_exact_replay(tmp_path):
    evidence_dir = tmp_path / "evidence"
    packet = subject.write_evidence(evidence_dir)
    assert subject.replay_evidence(evidence_dir) == packet
