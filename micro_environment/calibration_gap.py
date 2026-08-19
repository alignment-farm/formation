"""Pure opaque-control calibration transition for the information-gap problem."""

from dataclasses import dataclass


FIRST_INCREASES = "first_increases"
SECOND_INCREASES = "second_increases"
REQUEST_CALIBRATION = "request_calibration"
HOLD = "hold"

TARGET_REACHED = "target_reached"
TARGET_NOT_REACHED = "target_not_reached"
CALIBRATION_REVEALED = "calibration_revealed"
HELD_AT_TARGET = "held_at_target"
HELD_OFF_TARGET = "held_off_target"


class CalibrationRefusal(ValueError):
    """The supplied profile, public state, or action is outside the specimen."""


def _require_text(value: object, refusal: str) -> str:
    if type(value) is not str or value == "":
        raise CalibrationRefusal(refusal)
    return value


def _require_position(value: object) -> int:
    if type(value) is not int:
        raise CalibrationRefusal("position_must_be_integer")
    return value


@dataclass(frozen=True, slots=True)
class CalibrationProfile:
    controller_family: str
    increasing_slot: str

    def __post_init__(self) -> None:
        _require_text(self.controller_family, "controller_family_must_be_text")
        if self.increasing_slot not in (FIRST_INCREASES, SECOND_INCREASES):
            raise CalibrationRefusal("unknown_increasing_slot")


@dataclass(frozen=True, slots=True)
class CalibrationState:
    controller_family: str
    device_id: str
    position: int
    target: int
    first_control: str
    second_control: str

    def __post_init__(self) -> None:
        _require_text(self.controller_family, "controller_family_must_be_text")
        _require_text(self.device_id, "device_id_must_be_text")
        _require_position(self.position)
        _require_position(self.target)
        first = _require_text(self.first_control, "first_control_must_be_text")
        second = _require_text(self.second_control, "second_control_must_be_text")
        if first == second:
            raise CalibrationRefusal("control_strings_must_differ")
        if first in (REQUEST_CALIBRATION, HOLD) or second in (
            REQUEST_CALIBRATION,
            HOLD,
        ):
            raise CalibrationRefusal("control_string_is_reserved")


@dataclass(frozen=True, slots=True)
class CalibrationResult:
    action: str
    controller_family: str
    device_id: str
    position_before: int
    position_after: int
    target: int
    observation: str
    increasing_slot: str | None


def apply_calibration_action(
    state: object, profile: object, action: object
) -> CalibrationResult:
    """Apply one factual movement, calibration request, or hold operation."""

    if type(state) is not CalibrationState:
        raise CalibrationRefusal("exact_calibration_state_required")
    if type(profile) is not CalibrationProfile:
        raise CalibrationRefusal("exact_calibration_profile_required")
    if profile.controller_family != state.controller_family:
        raise CalibrationRefusal("profile_family_mismatch")
    permitted = (
        state.first_control,
        state.second_control,
        REQUEST_CALIBRATION,
        HOLD,
    )
    if type(action) is not str or action not in permitted:
        raise CalibrationRefusal("action_not_permitted_for_device")

    before = _require_position(state.position)
    target = _require_position(state.target)
    increasing_slot: str | None = None
    if action == REQUEST_CALIBRATION:
        after = before
        observation = CALIBRATION_REVEALED
        increasing_slot = profile.increasing_slot
    elif action == HOLD:
        after = before
        observation = HELD_AT_TARGET if before == target else HELD_OFF_TARGET
    else:
        first_selected = action == state.first_control
        increases = (
            first_selected and profile.increasing_slot == FIRST_INCREASES
        ) or (
            not first_selected and profile.increasing_slot == SECOND_INCREASES
        )
        after = before + 1 if increases else before - 1
        observation = TARGET_REACHED if after == target else TARGET_NOT_REACHED

    return CalibrationResult(
        action=action,
        controller_family=state.controller_family,
        device_id=state.device_id,
        position_before=before,
        position_after=after,
        target=target,
        observation=observation,
        increasing_slot=increasing_slot,
    )
