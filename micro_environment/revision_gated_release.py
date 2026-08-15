"""Pure revision-gated release transition from the pre-contact charter."""

from dataclasses import dataclass


RELEASE = "release"
REBUILD_THEN_RELEASE = "rebuild_then_release"
ACCEPTED = "accepted"
REJECTED = "rejected"
RELEASED = "released"
STALE_DEPENDENCY = "stale_dependency"


class TransitionRefusal(ValueError):
    """The supplied state or action is outside the closed transition language."""


def _require_revision(value: object) -> int:
    if type(value) is not int:
        raise TransitionRefusal("revision_must_be_integer")
    return value


@dataclass(frozen=True, slots=True)
class RevisionState:
    artifact_revision: int
    authority_revision: int

    def __post_init__(self) -> None:
        _require_revision(self.artifact_revision)
        _require_revision(self.authority_revision)


@dataclass(frozen=True, slots=True)
class RevisionResult:
    action: str
    artifact_revision_before: int
    artifact_revision_after: int
    authority_revision: int
    disposition: str
    observation: str


def apply_revision_gated_release(
    state: object, action: object
) -> RevisionResult:
    """Apply ``revision-gated-release-v0`` without cross-case state."""

    if type(state) is not RevisionState:
        raise TransitionRefusal("exact_revision_state_required")
    if type(action) is not str or action not in (RELEASE, REBUILD_THEN_RELEASE):
        raise TransitionRefusal("exact_release_action_required")

    artifact_before = _require_revision(state.artifact_revision)
    authority = _require_revision(state.authority_revision)
    artifact_after = (
        authority if action == REBUILD_THEN_RELEASE else artifact_before
    )
    accepted = artifact_after == authority
    return RevisionResult(
        action=action,
        artifact_revision_before=artifact_before,
        artifact_revision_after=artifact_after,
        authority_revision=authority,
        disposition=ACCEPTED if accepted else REJECTED,
        observation=RELEASED if accepted else STALE_DEPENDENCY,
    )
