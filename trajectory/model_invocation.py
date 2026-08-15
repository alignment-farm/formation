"""Trajectory witnesses for deterministic positive model invocations."""

from dataclasses import dataclass

from formation.model_invocation import (
    ActivatedInvocationRoot,
    RuntimePositiveModelInvocationAuthority,
    WithheldInvocationRoot,
)
from trajectory.practice_request import PositivePracticeRequestController, PracticeRequestWitness


class ModelInvocationWitnessRefusal(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ModelInvocationWitness:
    request_witness: PracticeRequestWitness
    invocation_root: WithheldInvocationRoot | ActivatedInvocationRoot
    _issuer: object


class PositiveModelInvocationController:
    def __init__(self, requests: PositivePracticeRequestController, runtime: RuntimePositiveModelInvocationAuthority, permit: object) -> None:
        requests._claim_invocation_controller(self, runtime, permit)
        self._requests = requests
        self.runtime = runtime
        self._issuer = object()
        self._witnesses: list[ModelInvocationWitness] = []

    def witness(self, request_witness: object, root: object) -> ModelInvocationWitness:
        request_witness = self._requests.require_witness(request_witness)
        current = self.runtime.require_root(root)
        if current.predecessor is not request_witness.request_root or any(item.invocation_root is current for item in self._witnesses):
            raise ModelInvocationWitnessRefusal("model_invocation_witness_chain_mismatch")
        witness = ModelInvocationWitness(request_witness, current, self._issuer)
        self._witnesses.append(witness)
        return witness

    def require_witness(self, witness: object) -> ModelInvocationWitness:
        if type(witness) is not ModelInvocationWitness or not any(item is witness for item in self._witnesses) or witness._issuer is not self._issuer:
            raise ModelInvocationWitnessRefusal("exact_model_invocation_witness_required")
        self._requests.require_witness(witness.request_witness)
        self.runtime.require_root(witness.invocation_root)
        return witness

    def require_complete_witnesses(self) -> tuple[ModelInvocationWitness, ...]:
        if len(self._witnesses) != 2:
            raise ModelInvocationWitnessRefusal("two_model_invocation_witnesses_required")
        current = tuple(self.require_witness(item) for item in self._witnesses)
        if {type(item.invocation_root) for item in current} != {WithheldInvocationRoot, ActivatedInvocationRoot} or len({id(item.invocation_root.predecessor) for item in current}) != 2:
            raise ModelInvocationWitnessRefusal("model_invocation_witness_set_mismatch")
        if len({id(item.invocation_root.invocation.actor) for item in current}) != 1:
            raise ModelInvocationWitnessRefusal("model_invocation_actor_mismatch")
        return current
