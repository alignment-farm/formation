"""External oracle for the frozen revision-gated release charter."""

from micro_environment import (
    ACCEPTED,
    REBUILD_THEN_RELEASE,
    REJECTED,
    RELEASED,
    STALE_DEPENDENCY,
    RevisionResult,
    RevisionState,
)


class ConformanceRefusal(ValueError):
    pass


def require_conforming(
    state: RevisionState, action: str, result: object
) -> RevisionResult:
    if type(result) is not RevisionResult:
        raise ConformanceRefusal("exact_revision_result_required")
    artifact_after = (
        state.authority_revision
        if action == REBUILD_THEN_RELEASE
        else state.artifact_revision
    )
    accepted = artifact_after == state.authority_revision
    expected = RevisionResult(
        action=action,
        artifact_revision_before=state.artifact_revision,
        artifact_revision_after=artifact_after,
        authority_revision=state.authority_revision,
        disposition=ACCEPTED if accepted else REJECTED,
        observation=RELEASED if accepted else STALE_DEPENDENCY,
    )
    if result != expected:
        raise ConformanceRefusal("revision_transition_mismatch")
    return result
