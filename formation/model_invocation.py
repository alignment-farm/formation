"""Deterministic cold-actor invocation over exact semantic practice requests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from formation.foreground import foreground_values
from formation.practice_request import (
    ActivatedPracticeRequest,
    ActivatedRequestRoot,
    PRACTICE_ACTOR,
    RuntimePositivePracticeRequestAuthority,
    WithheldPracticeRequest,
    WithheldRequestRoot,
)


_ACTOR_ISSUER = object()
_PROPOSAL_ISSUER = object()
_INVOCATION_ISSUER = object()
_ROOT_ISSUER = object()


class ModelInvocationRefusal(ValueError):
    """The deterministic actor cannot be invoked from this request lineage."""


@dataclass(frozen=True, slots=True)
class BlindCommitActor:
    version: str
    output_authority: str
    _issuer: object

    def invoke(self, request: object) -> ActorProposal:
        if type(request) is WithheldPracticeRequest:
            if hasattr(request, "intervention"):
                raise ModelInvocationRefusal("withheld_intervention_must_be_absent")
            value = request.situation.commit_action
        elif type(request) is ActivatedPracticeRequest:
            if request.intervention.intervention_procedure != "revision-check-intervention-v0":
                raise ModelInvocationRefusal("exact_fixture_intervention_required")
            value = (
                request.situation.commit_action
                if request.situation.artifact_revision
                == request.situation.authority_revision
                else request.situation.refresh_action
            )
        else:
            raise ModelInvocationRefusal("exact_practice_request_required")
        foreground_values(request.situation)
        return ActorProposal(self, request, self.output_authority, value, _PROPOSAL_ISSUER)


@dataclass(frozen=True, slots=True)
class ActorProposal:
    actor: BlindCommitActor
    request: WithheldPracticeRequest | ActivatedPracticeRequest
    output_authority: str
    value: str
    _issuer: object


@dataclass(frozen=True, slots=True)
class ModelInvocation:
    run_id: str
    actor: BlindCommitActor
    request: WithheldPracticeRequest | ActivatedPracticeRequest
    proposal: ActorProposal
    _issuer: object


@dataclass(frozen=True, slots=True)
class WithheldInvocationRoot:
    run_id: str
    predecessor: WithheldRequestRoot
    invocation: ModelInvocation
    proposal: ActorProposal
    _issuer: object


@dataclass(frozen=True, slots=True)
class ActivatedInvocationRoot:
    run_id: str
    predecessor: ActivatedRequestRoot
    invocation: ModelInvocation
    proposal: ActorProposal
    _issuer: object


_FIXTURE_ACTOR = BlindCommitActor(PRACTICE_ACTOR, "cold_model", _ACTOR_ISSUER)


def fixture_blind_commit_actor() -> BlindCommitActor:
    return _FIXTURE_ACTOR


class RequestRootVerifier(Protocol):
    root: WithheldRequestRoot | ActivatedRequestRoot
    def require(self, root: object) -> WithheldRequestRoot | ActivatedRequestRoot: ...


class _InvocationUse:
    def __init__(self, verifier: RequestRootVerifier) -> None:
        self.verifier = verifier
        self._verifier = verifier
        self.root = verifier.require(verifier.root)
        self.used = False
        self.invocation_root: WithheldInvocationRoot | ActivatedInvocationRoot | None = None
        self._invocations: list[object] = []

    def require(self, root: object) -> WithheldRequestRoot | ActivatedRequestRoot:
        if (
            root is not self.root
            or self.verifier is not self._verifier
            or self.verifier.require(root) is not root
        ):
            raise ModelInvocationRefusal("exact_invocation_request_root_required")
        return self.root


class RuntimePositiveModelInvocationAuthority:
    def __init__(
        self,
        verifiers: tuple[RequestRootVerifier, RequestRootVerifier],
        actor: BlindCommitActor,
        requests: RuntimePositivePracticeRequestAuthority,
        owner: object,
        permit: object,
    ) -> None:
        if (
            len(verifiers) != 2
            or verifiers[0].root is verifiers[1].root
            or {type(item.root) for item in verifiers}
            != {WithheldRequestRoot, ActivatedRequestRoot}
            or actor is not _FIXTURE_ACTOR
            or actor._issuer is not _ACTOR_ISSUER
        ):
            raise ModelInvocationRefusal("exact_positive_invocation_pair_required")
        roots = tuple(item.require(item.root) for item in verifiers)
        if any(root.request.actor != actor.version for root in roots):
            raise ModelInvocationRefusal("request_actor_mismatch")
        owner._preflight_invocation_runtime(permit, verifiers)
        requests._claim_invocation_authority(self, owner, permit)
        owner._claim_invocation_runtime(self, permit, verifiers)
        self.actor = actor
        self._requests = requests
        self._uses = tuple(_InvocationUse(item) for item in verifiers)
        self._roots: list[WithheldInvocationRoot | ActivatedInvocationRoot] = []
        self._snapshots: list[tuple[object, ...]] = []

    def _use_for(self, root: object) -> _InvocationUse:
        use = next((item for item in self._uses if item.root is root), None)
        if use is None:
            raise ModelInvocationRefusal("exact_invocation_request_root_required")
        return use

    def invoke(self, root: object) -> WithheldInvocationRoot | ActivatedInvocationRoot:
        use = self._use_for(root)
        if use.used or use.invocation_root is not None or use._invocations:
            raise ModelInvocationRefusal("request_already_invoked")
        current = use.require(root)
        self._requests.require_root(current)
        if current.request.actor != self.actor.version:
            raise ModelInvocationRefusal("request_actor_mismatch")
        proposal = self.actor.invoke(current.request)
        if (
            proposal.actor is not self.actor
            or proposal.request is not current.request
            or proposal.output_authority != "cold_model"
            or proposal._issuer is not _PROPOSAL_ISSUER
        ):
            raise ModelInvocationRefusal("exact_actor_proposal_required")
        invocation = ModelInvocation(
            current.run_id, self.actor, current.request, proposal, _INVOCATION_ISSUER
        )
        root_type = WithheldInvocationRoot if type(current) is WithheldRequestRoot else ActivatedInvocationRoot
        invocation_root = root_type(
            current.run_id, current, invocation, proposal, _ROOT_ISSUER
        )
        use.used = True
        use.invocation_root = invocation_root
        use._invocations.append(invocation_root)
        self._roots.append(invocation_root)
        self._snapshots.append(self._snapshot(invocation_root))
        return invocation_root

    @staticmethod
    def _snapshot(root: WithheldInvocationRoot | ActivatedInvocationRoot) -> tuple[object, ...]:
        invocation = root.invocation
        proposal = root.proposal
        return (
            id(root), root.run_id, id(root.predecessor), id(invocation), id(proposal), id(root._issuer),
            invocation.run_id, id(invocation.actor), id(invocation.request), id(invocation.proposal), id(invocation._issuer),
            id(proposal.actor), id(proposal.request), proposal.output_authority, proposal.value, id(proposal._issuer),
        )

    def require_root(self, root: object) -> WithheldInvocationRoot | ActivatedInvocationRoot:
        snapshot = next((item for item in self._snapshots if item[0] == id(root)), None)
        if snapshot is None or type(root) not in (WithheldInvocationRoot, ActivatedInvocationRoot):
            raise ModelInvocationRefusal("exact_model_invocation_root_required")
        if self._snapshot(root) != snapshot:
            raise ModelInvocationRefusal("model_invocation_root_changed")
        use = self._use_for(root.predecessor)
        if not use.used or use.invocation_root is not root or use._invocations != [root]:
            raise ModelInvocationRefusal("model_invocation_root_changed")
        use.require(root.predecessor)
        return root
