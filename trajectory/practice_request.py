"""Trajectory witnesses for positive semantic practice requests."""

from __future__ import annotations

from dataclasses import dataclass

from formation.practice_request import (
    ActivatedRequestRoot,
    RuntimePositivePracticeRequestAuthority,
    WithheldRequestRoot,
)
from trajectory.activation import ActivationDecisionWitness, PositiveActivationController


class PracticeRequestWitnessRefusal(ValueError):
    """The harness cannot witness this practice-request chain."""


@dataclass(frozen=True, slots=True)
class PracticeRequestWitness:
    decision_witness: ActivationDecisionWitness
    request_root: WithheldRequestRoot | ActivatedRequestRoot
    _issuer: object


class PositivePracticeRequestController:
    """Harness-only join for withheld and activated request roots."""

    def __init__(
        self,
        decisions: PositiveActivationController,
        runtime: RuntimePositivePracticeRequestAuthority,
        permit: object,
    ) -> None:
        decisions._claim_practice_controller(self, runtime, permit)
        self._decisions = decisions
        self.runtime = runtime
        self._issuer = object()
        self._witnesses: list[PracticeRequestWitness] = []
        self._snapshots: list[tuple[object, ...]] = []
        self._invocation_runtime: object | None = None
        self._invocation_controller: object | None = None
        self._invocation_permit = runtime._take_invocation_factory_permit(self)

    def witness(
        self, decision_witness: object, request_root: object
    ) -> PracticeRequestWitness:
        decision_witness = self._decisions.require_witness(decision_witness)
        root = self.runtime.require_root(request_root)
        if (
            root.predecessor is not decision_witness.decision_root
            or any(item.request_root is root for item in self._witnesses)
        ):
            raise PracticeRequestWitnessRefusal("practice_request_witness_chain_mismatch")
        if type(root) is WithheldRequestRoot:
            for forbidden in (
                "intervention",
                "handoff_binding",
                "selected_admission",
                "proposal",
            ):
                if hasattr(root, forbidden) or hasattr(root.request, forbidden):
                    raise PracticeRequestWitnessRefusal(
                        "practice_request_witness_chain_mismatch"
                    )
        elif (
            type(root) is not ActivatedRequestRoot
            or root.request.intervention is not root.intervention
        ):
            raise PracticeRequestWitnessRefusal("practice_request_witness_chain_mismatch")
        witness = PracticeRequestWitness(decision_witness, root, self._issuer)
        self._witnesses.append(witness)
        self._snapshots.append(
            (witness, witness.decision_witness, witness.request_root, witness._issuer)
        )
        return witness

    def require_witness(self, witness: object) -> PracticeRequestWitness:
        snapshot = next(
            (item for item in self._snapshots if item[0] is witness), None
        )
        if (
            type(witness) is not PracticeRequestWitness
            or snapshot is None
            or witness.decision_witness is not snapshot[1]
            or witness.request_root is not snapshot[2]
            or witness._issuer is not snapshot[3]
        ):
            raise PracticeRequestWitnessRefusal("exact_practice_request_witness_required")
        self._decisions.require_witness(witness.decision_witness)
        self.runtime.require_root(witness.request_root)
        return witness

    def require_complete_witnesses(self) -> tuple[PracticeRequestWitness, ...]:
        if len(self._witnesses) != 2:
            raise PracticeRequestWitnessRefusal("two_practice_request_witnesses_required")
        current = tuple(self.require_witness(item) for item in self._witnesses)
        if (
            {type(item.request_root) for item in current}
            != {WithheldRequestRoot, ActivatedRequestRoot}
            or len({id(item.request_root.predecessor) for item in current}) != 2
        ):
            raise PracticeRequestWitnessRefusal("practice_request_witness_set_mismatch")
        return current

    def open_positive_model_invocation_controller(self) -> object:
        if self._invocation_controller is not None:
            raise PracticeRequestWitnessRefusal("invocation_controller_already_opened")
        witnesses = self.require_complete_witnesses()
        verifiers = tuple(
            self.runtime.root_verifier(item.request_root) for item in witnesses
        )
        from formation.model_invocation import (
            RuntimePositiveModelInvocationAuthority,
            fixture_blind_commit_actor,
        )
        from trajectory.model_invocation import PositiveModelInvocationController

        runtime = RuntimePositiveModelInvocationAuthority(
            verifiers,
            fixture_blind_commit_actor(),
            self.runtime,
            self,
            self._invocation_permit,
        )
        controller = PositiveModelInvocationController(
            self, runtime, self._invocation_permit
        )
        self._invocation_controller = controller
        return controller

    def _preflight_invocation_runtime(
        self, permit: object, verifiers: tuple[object, object]
    ) -> None:
        if permit is not self._invocation_permit:
            raise PracticeRequestWitnessRefusal("invocation_controller_factory_required")
        if self._invocation_runtime is not None:
            raise PracticeRequestWitnessRefusal("invocation_controller_already_opened")
        roots = {id(item.request_root) for item in self.require_complete_witnesses()}
        if (
            len(verifiers) != 2
            or {id(item.root) for item in verifiers} != roots
            or any(self.runtime._require_root_verifier(item) is not item for item in verifiers)
        ):
            raise PracticeRequestWitnessRefusal("exact_positive_invocation_pair_required")

    def _claim_invocation_runtime(
        self, runtime: object, permit: object, verifiers: tuple[object, object]
    ) -> None:
        self._preflight_invocation_runtime(permit, verifiers)
        self._invocation_runtime = runtime

    def _claim_invocation_controller(
        self, controller: object, runtime: object, permit: object
    ) -> None:
        if permit is not self._invocation_permit or runtime is not self._invocation_runtime:
            raise PracticeRequestWitnessRefusal("exact_invocation_runtime_required")
        if self._invocation_controller is not None:
            raise PracticeRequestWitnessRefusal("invocation_controller_already_opened")
        self._invocation_controller = controller
