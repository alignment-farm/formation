"""Pure asymmetric task, hold, and diagnostic transitions."""

from dataclasses import dataclass


INTACT = "intact"
COMPLETED = "completed"
FAILED = "failed"
STATUSES = (INTACT, COMPLETED, FAILED)

FIRST_SLOT = "first"
SECOND_SLOT = "second"
SLOTS = (FIRST_SLOT, SECOND_SLOT)

STEADY = "steady_pattern"
PULSED = "pulsed_pattern"
UNMAPPED = "unmapped_pattern"
SIGNALS = (STEADY, PULSED, UNMAPPED)

HOLD = "hold"
APPLIED = "applied"
REFUSED = "refused"
TASK_COMPLETED = "task_completed"
TASK_FAILED = "task_failed"
DIAGNOSTIC_OBSERVED = "diagnostic_observed"
HELD = "held"


class AsymmetricSuspensionRefusal(ValueError):
    pass


def _text(value: object, refusal: str) -> str:
    if type(value) is not str or not value:
        raise AsymmetricSuspensionRefusal(refusal)
    return value


@dataclass(frozen=True, slots=True)
class SuspensionState:
    device: str
    task_controls: tuple[str, str]
    diagnostic_control: str
    status: str = INTACT

    def __post_init__(self) -> None:
        _text(self.device, "device_must_be_text")
        if type(self.task_controls) is not tuple or len(self.task_controls) != 2:
            raise AsymmetricSuspensionRefusal("task_controls_must_be_exact_pair")
        first = _text(self.task_controls[0], "task_controls_must_be_text")
        second = _text(self.task_controls[1], "task_controls_must_be_text")
        diagnostic = _text(self.diagnostic_control, "diagnostic_control_must_be_text")
        if len({first, second, diagnostic}) != 3 or HOLD in {
            first, second, diagnostic
        }:
            raise AsymmetricSuspensionRefusal("controls_must_be_distinct_and_not_hold")
        if self.status not in STATUSES:
            raise AsymmetricSuspensionRefusal("unknown_status")


@dataclass(frozen=True, slots=True)
class SuspensionProfile:
    device: str
    profile_id: str
    valid_task_slot: str
    diagnostic_signal: str

    def __post_init__(self) -> None:
        _text(self.device, "profile_device_must_be_text")
        _text(self.profile_id, "profile_id_must_be_text")
        if self.valid_task_slot not in SLOTS:
            raise AsymmetricSuspensionRefusal("unknown_valid_task_slot")
        if self.diagnostic_signal not in SIGNALS:
            raise AsymmetricSuspensionRefusal("unknown_diagnostic_signal")


@dataclass(frozen=True, slots=True)
class SuspensionResult:
    action: str
    disposition: str
    status_before: str
    status_after: str
    observation: str | None
    diagnostic_signal: str | None
    step_cost: int
    reason: str | None


def apply_action(
    state: object, profile: object, action: object
) -> SuspensionResult:
    if type(state) is not SuspensionState:
        raise AsymmetricSuspensionRefusal("exact_suspension_state_required")
    if type(profile) is not SuspensionProfile:
        raise AsymmetricSuspensionRefusal("exact_suspension_profile_required")
    action_text = _text(action, "action_must_be_text")
    if profile.device != state.device:
        raise AsymmetricSuspensionRefusal("profile_device_mismatch")
    allowed = (*state.task_controls, state.diagnostic_control, HOLD)
    if action_text not in allowed:
        raise AsymmetricSuspensionRefusal("unknown_action")
    if state.status != INTACT:
        return SuspensionResult(
            action_text,
            REFUSED,
            state.status,
            state.status,
            None,
            None,
            0,
            "terminal_state",
        )
    if action_text == HOLD:
        return SuspensionResult(
            action_text, APPLIED, INTACT, INTACT, HELD, None, 1, None
        )
    if action_text == state.diagnostic_control:
        return SuspensionResult(
            action_text,
            APPLIED,
            INTACT,
            INTACT,
            DIAGNOSTIC_OBSERVED,
            profile.diagnostic_signal,
            1,
            None,
        )
    selected_slot = (
        FIRST_SLOT if action_text == state.task_controls[0] else SECOND_SLOT
    )
    valid = selected_slot == profile.valid_task_slot
    return SuspensionResult(
        action_text,
        APPLIED,
        INTACT,
        COMPLETED if valid else FAILED,
        TASK_COMPLETED if valid else TASK_FAILED,
        None,
        1,
        None,
    )
