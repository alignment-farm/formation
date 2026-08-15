"""Trajectory witnesses for positive runtime action commitments."""

from dataclasses import dataclass

from formation.action_commitment import (
    ActivatedActionRoot,
    COMMIT_POLICY,
    RuntimePositiveActionCommitmentAuthority,
    WithheldActionRoot,
)
from trajectory.model_invocation import (
    ModelInvocationWitness,
    PositiveModelInvocationController,
)


class ActionCommitmentWitnessRefusal(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ActionCommitmentWitness:
    invocation_witness: ModelInvocationWitness
    action_root: WithheldActionRoot | ActivatedActionRoot
    _issuer: object


class PositiveActionCommitmentController:
    def __init__(
        self,
        invocations: PositiveModelInvocationController,
        runtime: RuntimePositiveActionCommitmentAuthority,
        permit: object,
    ) -> None:
        invocations._claim_action_controller(self, runtime, permit)
        self._invocations = invocations
        self.runtime = runtime
        self._issuer = object()
        self._witnesses: list[ActionCommitmentWitness] = []

    def witness(self, invocation_witness: object, root: object) -> ActionCommitmentWitness:
        invocation_witness = self._invocations.require_witness(invocation_witness)
        current = self.runtime.require_root(root)
        if current.predecessor is not invocation_witness.invocation_root or any(
            item.action_root is current for item in self._witnesses
        ):
            raise ActionCommitmentWitnessRefusal("action_witness_chain_mismatch")
        commitment = current.commitment
        predecessor = current.predecessor
        if (
            commitment.policy != COMMIT_POLICY
            or commitment.invocation is not predecessor.invocation
            or commitment.proposal is not predecessor.proposal
            or commitment.action_value != predecessor.proposal.value
            or self.runtime.require_binding(current.environment_binding, current)
            is not current.environment_binding
        ):
            raise ActionCommitmentWitnessRefusal("action_witness_chain_mismatch")
        witness = ActionCommitmentWitness(invocation_witness, current, self._issuer)
        self._witnesses.append(witness)
        return witness

    def require_witness(self, witness: object) -> ActionCommitmentWitness:
        if (
            type(witness) is not ActionCommitmentWitness
            or not any(item is witness for item in self._witnesses)
            or witness._issuer is not self._issuer
        ):
            raise ActionCommitmentWitnessRefusal("exact_action_witness_required")
        self._invocations.require_witness(witness.invocation_witness)
        self.runtime.require_root(witness.action_root)
        return witness

    def require_complete_witnesses(self) -> tuple[ActionCommitmentWitness, ...]:
        if len(self._witnesses) != 2:
            raise ActionCommitmentWitnessRefusal("two_action_witnesses_required")
        current = tuple(self.require_witness(item) for item in self._witnesses)
        if (
            {type(item.action_root) for item in current}
            != {WithheldActionRoot, ActivatedActionRoot}
            or len({id(item.action_root.predecessor) for item in current}) != 2
        ):
            raise ActionCommitmentWitnessRefusal("action_witness_set_mismatch")
        return current
