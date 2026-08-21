"""Pure costly-information episode transitions with a public signal alphabet."""

from dataclasses import dataclass


FIRST_ACTION = "first_action"
POST_DIAGNOSTIC = "post_diagnostic"
TERMINAL = "terminal"
PHASES = (FIRST_ACTION, POST_DIAGNOSTIC, TERMINAL)

INTACT = "intact"
COMPLETED = "completed"
FAILED = "failed"
HELD = "held"
TASK_STATUSES = (INTACT, COMPLETED, FAILED, HELD)

AVAILABLE = "available"
CONSUMED = "consumed"
WINDOW_STATES = (AVAILABLE, CONSUMED)

COSTLY = "consume_service_window"
FREE = "free"
COST_MODES = (COSTLY, FREE)

FIRST_SLOT = "first"
SECOND_SLOT = "second"
SLOTS = (FIRST_SLOT, SECOND_SLOT)

HOLD = "hold"
APPLIED = "applied"
REFUSED = "refused"
TASK_COMPLETED = "task_completed"
TASK_FAILED = "task_failed"
DIAGNOSTIC_OBSERVED = "diagnostic_observed"
EPISODE_HELD = "episode_held"


class KnowledgeCostRefusal(ValueError):
    pass


def _text(value: object, refusal: str) -> str:
    if type(value) is not str or not value:
        raise KnowledgeCostRefusal(refusal)
    return value


@dataclass(frozen=True, slots=True)
class KnowledgeCostState:
    device: str
    task_controls: tuple[str, str]
    diagnostic_control: str
    diagnostic_alphabet: tuple[str, str]
    diagnostic_cost: str
    service_window: str = AVAILABLE
    task_status: str = INTACT
    phase: str = FIRST_ACTION
    observed_signal: str | None = None

    def __post_init__(self) -> None:
        _text(self.device, "device_must_be_text")
        if type(self.task_controls) is not tuple or len(self.task_controls) != 2:
            raise KnowledgeCostRefusal("task_controls_must_be_exact_pair")
        first = _text(self.task_controls[0], "task_controls_must_be_text")
        second = _text(self.task_controls[1], "task_controls_must_be_text")
        diagnostic = _text(
            self.diagnostic_control, "diagnostic_control_must_be_text"
        )
        if len({first, second, diagnostic}) != 3 or HOLD in {
            first,
            second,
            diagnostic,
        }:
            raise KnowledgeCostRefusal("controls_must_be_distinct_and_not_hold")
        if (
            type(self.diagnostic_alphabet) is not tuple
            or len(self.diagnostic_alphabet) != 2
        ):
            raise KnowledgeCostRefusal("diagnostic_alphabet_must_be_exact_pair")
        signal_a = _text(
            self.diagnostic_alphabet[0], "diagnostic_alphabet_must_be_text"
        )
        signal_b = _text(
            self.diagnostic_alphabet[1], "diagnostic_alphabet_must_be_text"
        )
        if signal_a == signal_b:
            raise KnowledgeCostRefusal("diagnostic_signals_must_be_distinct")
        if self.diagnostic_cost not in COST_MODES:
            raise KnowledgeCostRefusal("unknown_diagnostic_cost")
        if self.service_window not in WINDOW_STATES:
            raise KnowledgeCostRefusal("unknown_service_window")
        if self.task_status not in TASK_STATUSES:
            raise KnowledgeCostRefusal("unknown_task_status")
        if self.phase not in PHASES:
            raise KnowledgeCostRefusal("unknown_phase")
        if self.phase == FIRST_ACTION:
            if (
                self.task_status != INTACT
                or self.service_window != AVAILABLE
                or self.observed_signal is not None
            ):
                raise KnowledgeCostRefusal("invalid_first_action_state")
        elif self.phase == POST_DIAGNOSTIC:
            if self.task_status != INTACT:
                raise KnowledgeCostRefusal("post_diagnostic_task_must_be_intact")
            if self.observed_signal not in self.diagnostic_alphabet:
                raise KnowledgeCostRefusal("post_diagnostic_signal_not_in_alphabet")
            expected_window = CONSUMED if self.diagnostic_cost == COSTLY else AVAILABLE
            if self.service_window != expected_window:
                raise KnowledgeCostRefusal("post_diagnostic_window_mismatch")
        else:
            if self.task_status not in (COMPLETED, FAILED, HELD):
                raise KnowledgeCostRefusal("terminal_state_requires_terminal_status")
            if (
                self.observed_signal is not None
                and self.observed_signal not in self.diagnostic_alphabet
            ):
                raise KnowledgeCostRefusal("terminal_signal_not_in_alphabet")


@dataclass(frozen=True, slots=True)
class KnowledgeCostProfile:
    device: str
    profile_id: str
    valid_task_slot: str
    diagnostic_signal: str

    def __post_init__(self) -> None:
        _text(self.device, "profile_device_must_be_text")
        _text(self.profile_id, "profile_id_must_be_text")
        if self.valid_task_slot not in SLOTS:
            raise KnowledgeCostRefusal("unknown_valid_task_slot")
        _text(self.diagnostic_signal, "diagnostic_signal_must_be_text")


@dataclass(frozen=True, slots=True)
class KnowledgeCostResult:
    action: str
    disposition: str
    phase_before: str
    phase_after: str
    task_status_before: str
    task_status_after: str
    task_outcome: str | None
    information_acquired: bool
    diagnostic_signal: str | None
    service_window_before: str
    service_window_after: str
    service_window_consumed: bool
    abstained: bool
    reason: str | None
    state_after: KnowledgeCostState


def apply_action(
    state: object, profile: object, action: object
) -> KnowledgeCostResult:
    if type(state) is not KnowledgeCostState:
        raise KnowledgeCostRefusal("exact_knowledge_cost_state_required")
    if type(profile) is not KnowledgeCostProfile:
        raise KnowledgeCostRefusal("exact_knowledge_cost_profile_required")
    action_text = _text(action, "action_must_be_text")
    if profile.device != state.device:
        raise KnowledgeCostRefusal("profile_device_mismatch")
    if profile.diagnostic_signal not in state.diagnostic_alphabet:
        raise KnowledgeCostRefusal("profile_signal_not_in_public_alphabet")
    allowed = (*state.task_controls, state.diagnostic_control, HOLD)
    if action_text not in allowed:
        raise KnowledgeCostRefusal("unknown_action")
    if state.phase == TERMINAL:
        return KnowledgeCostResult(
            action_text,
            REFUSED,
            TERMINAL,
            TERMINAL,
            state.task_status,
            state.task_status,
            None,
            False,
            None,
            state.service_window,
            state.service_window,
            False,
            False,
            "terminal_episode",
            state,
        )
    if state.phase == POST_DIAGNOSTIC and action_text == state.diagnostic_control:
        return KnowledgeCostResult(
            action_text,
            REFUSED,
            POST_DIAGNOSTIC,
            POST_DIAGNOSTIC,
            INTACT,
            INTACT,
            None,
            False,
            None,
            state.service_window,
            state.service_window,
            False,
            False,
            "diagnostic_already_used",
            state,
        )
    if action_text == HOLD:
        after = KnowledgeCostState(
            state.device,
            state.task_controls,
            state.diagnostic_control,
            state.diagnostic_alphabet,
            state.diagnostic_cost,
            state.service_window,
            HELD,
            TERMINAL,
            state.observed_signal,
        )
        return KnowledgeCostResult(
            action_text,
            APPLIED,
            state.phase,
            TERMINAL,
            INTACT,
            HELD,
            EPISODE_HELD,
            False,
            None,
            state.service_window,
            state.service_window,
            False,
            True,
            None,
            after,
        )
    if action_text == state.diagnostic_control:
        window_after = CONSUMED if state.diagnostic_cost == COSTLY else AVAILABLE
        after = KnowledgeCostState(
            state.device,
            state.task_controls,
            state.diagnostic_control,
            state.diagnostic_alphabet,
            state.diagnostic_cost,
            window_after,
            INTACT,
            POST_DIAGNOSTIC,
            profile.diagnostic_signal,
        )
        return KnowledgeCostResult(
            action_text,
            APPLIED,
            FIRST_ACTION,
            POST_DIAGNOSTIC,
            INTACT,
            INTACT,
            None,
            True,
            profile.diagnostic_signal,
            AVAILABLE,
            window_after,
            window_after == CONSUMED,
            False,
            None,
            after,
        )
    selected_slot = (
        FIRST_SLOT if action_text == state.task_controls[0] else SECOND_SLOT
    )
    valid = selected_slot == profile.valid_task_slot
    status_after = COMPLETED if valid else FAILED
    task_outcome = TASK_COMPLETED if valid else TASK_FAILED
    after = KnowledgeCostState(
        state.device,
        state.task_controls,
        state.diagnostic_control,
        state.diagnostic_alphabet,
        state.diagnostic_cost,
        state.service_window,
        status_after,
        TERMINAL,
        state.observed_signal,
    )
    return KnowledgeCostResult(
        action_text,
        APPLIED,
        state.phase,
        TERMINAL,
        INTACT,
        status_after,
        task_outcome,
        False,
        None,
        state.service_window,
        state.service_window,
        False,
        False,
        None,
        after,
    )
