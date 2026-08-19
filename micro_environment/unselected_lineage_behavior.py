"""Pure opaque-control physics for the unselected-lineage specimen."""

from dataclasses import dataclass


FIRST_INCREASES = "first_increases"
SECOND_INCREASES = "second_increases"
FIRST_SLOT = "first"
SECOND_SLOT = "second"
HOLD = "hold"

APPLIED = "applied"
HELD = "held"
REFUSED = "refused"
NOT_APPLIED = "not_applied"
INCREASED = "increased"
DECREASED = "decreased"
UNCHANGED = "unchanged"


class LineageBehaviorRefusal(ValueError):
    """An environment input is outside the deterministic specimen."""


def _text(value: object, refusal: str, *, empty: bool = False) -> str:
    if type(value) is not str or (not empty and value == ""):
        raise LineageBehaviorRefusal(refusal)
    return value


def _integer(value: object, refusal: str) -> int:
    if type(value) is not int:
        raise LineageBehaviorRefusal(refusal)
    return value


@dataclass(frozen=True, slots=True)
class LineageProfile:
    controller_family: str
    increasing_slot: str

    def __post_init__(self) -> None:
        _text(self.controller_family, "controller_family_must_be_text")
        if self.increasing_slot not in (FIRST_INCREASES, SECOND_INCREASES):
            raise LineageBehaviorRefusal("unknown_increasing_slot")


@dataclass(frozen=True, slots=True)
class LineageState:
    controller_family: str
    device: str
    position: int
    target: int
    controls: tuple[str, str]

    def __post_init__(self) -> None:
        _text(self.controller_family, "controller_family_must_be_text")
        _text(self.device, "device_must_be_text")
        _integer(self.position, "position_must_be_integer")
        _integer(self.target, "target_must_be_integer")
        if type(self.controls) is not tuple or len(self.controls) != 2:
            raise LineageBehaviorRefusal("controls_must_be_exact_pair")
        first = _text(self.controls[0], "controls_must_be_text")
        second = _text(self.controls[1], "controls_must_be_text")
        if first == second:
            raise LineageBehaviorRefusal("controls_must_differ")
        if HOLD in self.controls:
            raise LineageBehaviorRefusal("control_is_reserved")


@dataclass(frozen=True, slots=True)
class ProposalReceipt:
    available: bool
    content: str

    def __post_init__(self) -> None:
        if type(self.available) is not bool:
            raise LineageBehaviorRefusal("proposal_available_must_be_boolean")
        _text(self.content, "proposal_content_must_be_text", empty=True)
        if not self.available and self.content != "":
            raise LineageBehaviorRefusal("unavailable_proposal_must_be_empty")


@dataclass(frozen=True, slots=True)
class LineageActionResult:
    status: str
    proposal: ProposalReceipt
    before: LineageState
    selected_slot: str | None
    position_after: int | None
    movement_direction: str | None
    target_reached: bool | None
    reason: str | None


def apply_committed_action(
    state: object, profile: object, proposal: object
) -> LineageActionResult:
    """Apply an already committed proposal under hidden environment physics."""

    if type(state) is not LineageState:
        raise LineageBehaviorRefusal("exact_lineage_state_required")
    if type(profile) is not LineageProfile:
        raise LineageBehaviorRefusal("exact_lineage_profile_required")
    if type(proposal) is not ProposalReceipt:
        raise LineageBehaviorRefusal("exact_proposal_receipt_required")
    if profile.controller_family != state.controller_family:
        raise LineageBehaviorRefusal("profile_family_mismatch")

    if not proposal.available:
        return LineageActionResult(
            status=NOT_APPLIED,
            proposal=proposal,
            before=state,
            selected_slot=None,
            position_after=None,
            movement_direction=None,
            target_reached=None,
            reason="proposal_unavailable",
        )

    action = proposal.content
    if action not in (*state.controls, HOLD):
        return LineageActionResult(
            status=REFUSED,
            proposal=proposal,
            before=state,
            selected_slot=None,
            position_after=None,
            movement_direction=None,
            target_reached=None,
            reason="action_not_permitted_for_device",
        )

    if action == HOLD:
        return LineageActionResult(
            status=HELD,
            proposal=proposal,
            before=state,
            selected_slot=None,
            position_after=state.position,
            movement_direction=UNCHANGED,
            target_reached=state.position == state.target,
            reason=None,
        )

    selected_index = state.controls.index(action)
    increasing_index = 0 if profile.increasing_slot == FIRST_INCREASES else 1
    increases = selected_index == increasing_index
    after = state.position + 1 if increases else state.position - 1
    return LineageActionResult(
        status=APPLIED,
        proposal=proposal,
        before=state,
        selected_slot=FIRST_SLOT if selected_index == 0 else SECOND_SLOT,
        position_after=after,
        movement_direction=INCREASED if increases else DECREASED,
        target_reached=after == state.target,
        reason=None,
    )
