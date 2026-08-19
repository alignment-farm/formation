"""Pure phase-coupled opaque-control transition environment."""

from dataclasses import dataclass


HOLD = "hold"
INCREASED = "increased"
DECREASED = "decreased"
UNCHANGED = "unchanged"


class PhaseControlRefusal(ValueError):
    """The supplied profile, public state, or action is outside the specimen."""


def _require_text(value: object, refusal: str) -> str:
    if type(value) is not str or value == "":
        raise PhaseControlRefusal(refusal)
    return value


def _require_integer(value: object, refusal: str) -> int:
    if type(value) is not int:
        raise PhaseControlRefusal(refusal)
    return value


def _require_pair(value: object, refusal: str) -> tuple[str, str]:
    if type(value) is not tuple or len(value) != 2:
        raise PhaseControlRefusal(refusal)
    first = _require_text(value[0], refusal)
    second = _require_text(value[1], refusal)
    if first == second:
        raise PhaseControlRefusal(refusal)
    return first, second


@dataclass(frozen=True, slots=True)
class PhaseProfile:
    """Environment-private profile plus its two public phase identifiers."""

    controller_family: str
    phases: tuple[str, str]
    phase_zero_increasing_slot: int

    def __post_init__(self) -> None:
        _require_text(self.controller_family, "controller_family_must_be_text")
        _require_pair(self.phases, "phases_must_be_distinct_text_pair")
        if type(self.phase_zero_increasing_slot) is not int or (
            self.phase_zero_increasing_slot not in (0, 1)
        ):
            raise PhaseControlRefusal("increasing_slot_must_be_zero_or_one")


@dataclass(frozen=True, slots=True)
class PhaseState:
    """The complete public state before one environment action."""

    controller_family: str
    device: str
    phase: str
    position: int
    target: int
    controls: tuple[str, str]

    def __post_init__(self) -> None:
        _require_text(self.controller_family, "controller_family_must_be_text")
        _require_text(self.device, "device_must_be_text")
        _require_text(self.phase, "phase_must_be_text")
        _require_integer(self.position, "position_must_be_integer")
        _require_integer(self.target, "target_must_be_integer")
        controls = _require_pair(
            self.controls, "controls_must_be_distinct_text_pair"
        )
        if HOLD in controls:
            raise PhaseControlRefusal("control_token_is_reserved")


@dataclass(frozen=True, slots=True)
class PhaseActionResult:
    """One factual consequence without a selected-slot or profile field."""

    action: str
    before: PhaseState
    position_after: int
    movement_direction: str
    phase_after: str
    target_reached: bool

    def next_state(self) -> PhaseState:
        return PhaseState(
            controller_family=self.before.controller_family,
            device=self.before.device,
            phase=self.phase_after,
            position=self.position_after,
            target=self.before.target,
            controls=self.before.controls,
        )


def apply_phase_action(
    state: object, profile: object, action: object
) -> PhaseActionResult:
    """Apply one listed control or hold to an exact public state."""

    if type(state) is not PhaseState:
        raise PhaseControlRefusal("exact_phase_state_required")
    if type(profile) is not PhaseProfile:
        raise PhaseControlRefusal("exact_phase_profile_required")
    if profile.controller_family != state.controller_family:
        raise PhaseControlRefusal("profile_family_mismatch")
    if state.phase not in profile.phases:
        raise PhaseControlRefusal("state_phase_not_in_profile")
    if type(action) is not str or action not in (*state.controls, HOLD):
        raise PhaseControlRefusal("action_not_permitted_for_device")

    if action == HOLD:
        after = state.position
        direction = UNCHANGED
        phase_after = state.phase
    else:
        phase_index = profile.phases.index(state.phase)
        selected_slot = state.controls.index(action)
        increasing_slot = profile.phase_zero_increasing_slot ^ phase_index
        increases = selected_slot == increasing_slot
        after = state.position + 1 if increases else state.position - 1
        direction = INCREASED if increases else DECREASED
        phase_after = profile.phases[1 - phase_index]

    return PhaseActionResult(
        action=action,
        before=state,
        position_after=after,
        movement_direction=direction,
        phase_after=phase_after,
        target_reached=after == state.target,
    )


def apply_phase_commitment(
    state: object, profile: object, actions: object
) -> tuple[PhaseActionResult, PhaseActionResult]:
    """Execute an already committed two-control pair without feedback."""

    if type(state) is not PhaseState:
        raise PhaseControlRefusal("exact_phase_state_required")
    if type(actions) is not tuple or len(actions) != 2:
        raise PhaseControlRefusal("commitment_must_be_exact_action_pair")
    if any(type(action) is not str or action not in state.controls for action in actions):
        raise PhaseControlRefusal("commitment_action_not_permitted")

    first = apply_phase_action(state, profile, actions[0])
    second = apply_phase_action(first.next_state(), profile, actions[1])
    return first, second
