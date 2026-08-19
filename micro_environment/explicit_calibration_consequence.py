"""Environment-issued factual rendering of an opaque calibration transition."""

from dataclasses import dataclass

from micro_environment.calibration_gap import (
    HOLD,
    REQUEST_CALIBRATION,
    CalibrationProfile,
    CalibrationRefusal,
    CalibrationState,
    apply_calibration_action,
)


FIRST_SLOT = "first"
SECOND_SLOT = "second"
INCREASED = "increased"
DECREASED = "decreased"
UNCHANGED = "unchanged"


@dataclass(frozen=True, slots=True)
class ExplicitCalibrationResult:
    action: str
    controller_family: str
    device_id: str
    position_before: int
    position_after: int
    target: int
    observation: str
    selected_slot: str | None
    movement_direction: str
    increasing_slot: str | None


def apply_explicit_calibration_action(
    state: object, profile: object, action: object
) -> ExplicitCalibrationResult:
    """Apply v0 and expose only factual slot selection and observed movement."""

    if type(state) is not CalibrationState:
        raise CalibrationRefusal("exact_calibration_state_required")
    if type(profile) is not CalibrationProfile:
        raise CalibrationRefusal("exact_calibration_profile_required")
    result = apply_calibration_action(state, profile, action)
    if action == state.first_control:
        selected_slot = FIRST_SLOT
    elif action == state.second_control:
        selected_slot = SECOND_SLOT
    else:
        selected_slot = None
    if result.position_after > result.position_before:
        direction = INCREASED
    elif result.position_after < result.position_before:
        direction = DECREASED
    else:
        direction = UNCHANGED
    if action in (REQUEST_CALIBRATION, HOLD):
        selected_slot = None
    return ExplicitCalibrationResult(
        action=result.action,
        controller_family=result.controller_family,
        device_id=result.device_id,
        position_before=result.position_before,
        position_after=result.position_after,
        target=result.target,
        observation=result.observation,
        selected_slot=selected_slot,
        movement_direction=direction,
        increasing_slot=result.increasing_slot,
    )
