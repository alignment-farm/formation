"""Harness-only warrant oracle for the phase-coupled deterministic specimen."""

from micro_environment.phase_coupled_control import HOLD, PhaseProfile, PhaseState


WARRANTED = "warranted"
UNWARRANTED_GUESS = "unwarranted_guess"
UNWARRANTED_ACTION = "unwarranted_action"


class PhaseOracleRefusal(ValueError):
    """The proposed scoring input is outside the deterministic specimen."""


def classify_one_action(
    state: object,
    profile: object,
    action: object,
    *,
    warranted_profile_evidence: bool,
) -> str:
    """Classify warrant without changing or advising the environment."""

    if type(state) is not PhaseState or type(profile) is not PhaseProfile:
        raise PhaseOracleRefusal("exact_state_and_profile_required")
    if profile.controller_family != state.controller_family:
        raise PhaseOracleRefusal("profile_family_mismatch")
    if state.phase not in profile.phases:
        raise PhaseOracleRefusal("state_phase_not_in_profile")
    if type(action) is not str or action not in (*state.controls, HOLD):
        raise PhaseOracleRefusal("unlisted_action")
    if type(warranted_profile_evidence) is not bool:
        raise PhaseOracleRefusal("warrant_status_must_be_boolean")
    if state.position == state.target:
        return WARRANTED if action == HOLD else UNWARRANTED_ACTION
    if not warranted_profile_evidence:
        return WARRANTED if action == HOLD else UNWARRANTED_GUESS
    if action == HOLD:
        return UNWARRANTED_ACTION

    phase_index = profile.phases.index(state.phase)
    increasing_slot = profile.phase_zero_increasing_slot ^ phase_index
    toward_slot = increasing_slot if state.target > state.position else 1 - increasing_slot
    return WARRANTED if action == state.controls[toward_slot] else UNWARRANTED_ACTION
