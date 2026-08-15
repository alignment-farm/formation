"""Runtime-owned positive action commitments before environment application."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from formation.model_invocation import (
    ActivatedInvocationRoot,
    ActorProposal,
    ModelInvocation,
    RuntimePositiveModelInvocationAuthority,
    WithheldInvocationRoot,
)


COMMIT_POLICY = "commit-model-proposal-v0"
_COMMITMENT_ISSUER = object()
_BINDING_ISSUER = object()
_HANDOFF_ISSUER = object()
_ROOT_ISSUER = object()


class ActionCommitmentRefusal(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ActionCommitted:
    run_id: str
    policy: str
    invocation: ModelInvocation
    proposal: ActorProposal
    action_value: str
    _issuer: object


@dataclass(frozen=True, slots=True)
class EnvironmentActionBinding:
    run_id: str
    token: object
    _issuer: object


@dataclass(frozen=True, slots=True)
class EnvironmentActionHandoff:
    run_id: str
    commitment: ActionCommitted
    action_value: str
    _issuer: object


@dataclass(frozen=True, slots=True)
class WithheldActionRoot:
    run_id: str
    predecessor: WithheldInvocationRoot
    commitment: ActionCommitted
    environment_binding: EnvironmentActionBinding
    _issuer: object


@dataclass(frozen=True, slots=True)
class ActivatedActionRoot:
    run_id: str
    predecessor: ActivatedInvocationRoot
    commitment: ActionCommitted
    environment_binding: EnvironmentActionBinding
    _issuer: object


class InvocationVerifier(Protocol):
    root: WithheldInvocationRoot | ActivatedInvocationRoot

    def require(
        self, root: object
    ) -> WithheldInvocationRoot | ActivatedInvocationRoot: ...


class _CommitUse:
    def __init__(self, verifier: InvocationVerifier) -> None:
        self.verifier = verifier
        self._verifier = verifier
        self.root = verifier.require(verifier.root)
        self.used = False
        self.action_root: WithheldActionRoot | ActivatedActionRoot | None = None
        self._commitments: list[object] = []

    def require(
        self, root: object
    ) -> WithheldInvocationRoot | ActivatedInvocationRoot:
        if (
            root is not self.root
            or self.verifier is not self._verifier
            or self.verifier.require(root) is not root
        ):
            raise ActionCommitmentRefusal("exact_invocation_root_required")
        return self.root


class _EnvironmentUse:
    def __init__(
        self,
        binding: EnvironmentActionBinding,
        handoff: EnvironmentActionHandoff,
        root: WithheldActionRoot | ActivatedActionRoot,
        commitment_use: _CommitUse,
    ) -> None:
        self.binding = binding
        self.handoff = handoff
        self.root = root
        self.commitment_use = commitment_use
        self._snapshot = (
            binding.run_id,
            id(binding.token),
            id(binding._issuer),
            handoff.run_id,
            id(handoff.commitment),
            handoff.action_value,
            id(handoff._issuer),
        )

    def require(
        self, binding: object, root: object
    ) -> EnvironmentActionBinding:
        handoff = self.handoff
        current = (
            self.binding.run_id,
            id(self.binding.token),
            id(self.binding._issuer),
            handoff.run_id,
            id(handoff.commitment),
            handoff.action_value,
            id(handoff._issuer),
        )
        if (
            binding is not self.binding
            or root is not self.root
            or not self.commitment_use.used
            or self.commitment_use.action_root is not root
            or self.commitment_use._commitments != [root]
            or current != self._snapshot
        ):
            raise ActionCommitmentRefusal(
                "exact_environment_action_binding_required"
            )
        return self.binding


class RuntimePositiveActionCommitmentAuthority:
    def __init__(
        self,
        verifiers: tuple[InvocationVerifier, InvocationVerifier],
        policy: str,
        invocations: RuntimePositiveModelInvocationAuthority,
        owner: object,
        permit: object,
    ) -> None:
        if (
            len(verifiers) != 2
            or verifiers[0].root is verifiers[1].root
            or {type(item.root) for item in verifiers}
            != {WithheldInvocationRoot, ActivatedInvocationRoot}
            or policy != COMMIT_POLICY
        ):
            raise ActionCommitmentRefusal("exact_positive_action_pair_required")
        roots = tuple(item.require(item.root) for item in verifiers)
        if len({id(root.invocation.actor) for root in roots}) != 1 or any(
            root.proposal is not root.invocation.proposal
            or root.proposal.request is not root.invocation.request
            for root in roots
        ):
            raise ActionCommitmentRefusal("exact_actor_proposal_required")
        owner._preflight_action_runtime(permit, verifiers)
        invocations._claim_action_authority(self, owner, permit)
        owner._claim_action_runtime(self, permit, verifiers)
        self.policy = policy
        self._invocations = invocations
        self._uses = tuple(_CommitUse(item) for item in verifiers)
        self._roots: list[WithheldActionRoot | ActivatedActionRoot] = []
        self._snapshots: list[tuple[object, ...]] = []
        self._root_verifiers: list[_ActionRootVerifier] = []
        self._environment_uses: list[_EnvironmentUse] = []

    def _use_for(self, root: object) -> _CommitUse:
        use = next((item for item in self._uses if item.root is root), None)
        if use is None:
            raise ActionCommitmentRefusal("exact_invocation_root_required")
        return use

    def commit(self, root: object) -> WithheldActionRoot | ActivatedActionRoot:
        use = self._use_for(root)
        if (
            use.used
            or use.action_root is not None
            or use._commitments
            or any(existing.predecessor is root for existing in self._roots)
        ):
            raise ActionCommitmentRefusal("invocation_already_committed")
        current = use.require(root)
        self._invocations.require_root(current)
        proposal = current.proposal
        if (
            proposal is not current.invocation.proposal
            or proposal.request is not current.invocation.request
        ):
            raise ActionCommitmentRefusal("exact_actor_proposal_required")
        commitment = ActionCommitted(
            current.run_id,
            self.policy,
            current.invocation,
            proposal,
            proposal.value,
            _COMMITMENT_ISSUER,
        )
        binding = EnvironmentActionBinding(
            current.run_id, object(), _BINDING_ISSUER
        )
        handoff = EnvironmentActionHandoff(
            current.run_id, commitment, proposal.value, _HANDOFF_ISSUER
        )
        root_type = (
            WithheldActionRoot
            if type(current) is WithheldInvocationRoot
            else ActivatedActionRoot
        )
        action_root = root_type(
            current.run_id, current, commitment, binding, _ROOT_ISSUER
        )
        use.used = True
        use.action_root = action_root
        use._commitments.append(action_root)
        self._roots.append(action_root)
        self._snapshots.append(self._snapshot(action_root))
        self._environment_uses.append(
            _EnvironmentUse(binding, handoff, action_root, use)
        )
        return action_root

    @staticmethod
    def _snapshot(
        root: WithheldActionRoot | ActivatedActionRoot,
    ) -> tuple[object, ...]:
        commitment = root.commitment
        binding = root.environment_binding
        return (
            id(root),
            root.run_id,
            id(root.predecessor),
            id(commitment),
            id(binding),
            id(root._issuer),
            commitment.run_id,
            commitment.policy,
            id(commitment.invocation),
            id(commitment.proposal),
            commitment.action_value,
            id(commitment._issuer),
            binding.run_id,
            id(binding.token),
            id(binding._issuer),
        )

    def require_root(
        self, root: object
    ) -> WithheldActionRoot | ActivatedActionRoot:
        snapshot = next(
            (item for item in self._snapshots if item[0] == id(root)), None
        )
        if snapshot is None or type(root) not in (
            WithheldActionRoot,
            ActivatedActionRoot,
        ):
            raise ActionCommitmentRefusal("exact_action_root_required")
        if self._snapshot(root) != snapshot:
            raise ActionCommitmentRefusal("action_root_changed")
        use = self._use_for(root.predecessor)
        if (
            not use.used
            or use.action_root is not root
            or use._commitments != [root]
        ):
            raise ActionCommitmentRefusal("action_root_changed")
        use.require(root.predecessor)
        self.require_binding(root.environment_binding, root)
        return root

    def require_predecessor_current(
        self, root: object
    ) -> WithheldActionRoot | ActivatedActionRoot:
        current = self.require_root(root)
        self._invocations.require_root(current.predecessor)
        return current

    def root_verifier(self, root: object) -> _ActionRootVerifier:
        verifier = _ActionRootVerifier(self.require_root(root))
        self._root_verifiers.append(verifier)
        return verifier

    def _require_root_verifier(self, verifier: object) -> _ActionRootVerifier:
        if (
            type(verifier) is not _ActionRootVerifier
            or not any(item is verifier for item in self._root_verifiers)
            or verifier.require(verifier.root) is not verifier.root
        ):
            raise ActionCommitmentRefusal("exact_action_root_verifier_required")
        return verifier

    def require_binding(
        self, binding: object, root: object
    ) -> EnvironmentActionBinding:
        use = next(
            (item for item in self._environment_uses if item.binding is binding),
            None,
        )
        if use is None:
            raise ActionCommitmentRefusal(
                "exact_environment_action_binding_required"
            )
        return use.require(binding, root)


class _ActionRootVerifier:
    def __init__(self, root: WithheldActionRoot | ActivatedActionRoot) -> None:
        self.root = root
        self._snapshot = RuntimePositiveActionCommitmentAuthority._snapshot(root)

    def require(
        self, root: object
    ) -> WithheldActionRoot | ActivatedActionRoot:
        if root is not self.root or type(root) not in (
            WithheldActionRoot,
            ActivatedActionRoot,
        ):
            raise ActionCommitmentRefusal("exact_action_root_required")
        if RuntimePositiveActionCommitmentAuthority._snapshot(root) != self._snapshot:
            raise ActionCommitmentRefusal("action_root_changed")
        return self.root
