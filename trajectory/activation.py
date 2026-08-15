"""Trajectory witnesses for the two-root positive activation decision."""

from __future__ import annotations

from dataclasses import dataclass

from formation.activation import (
    ActivatedDecisionRoot,
    RuntimePositiveActivationAuthority,
    WithheldDecisionRoot,
)
from formation.condition_append import baseline_condition, treatment_condition
from formation.foreground import foreground_values
from trajectory.encounter import EncounterOpeningController, EncounterOpeningWitness


class ActivationWitnessRefusal(ValueError):
    """The harness cannot witness this activation decision chain."""


@dataclass(frozen=True, slots=True)
class ActivationDecisionWitness:
    encounter_witness: EncounterOpeningWitness
    decision_root: WithheldDecisionRoot | ActivatedDecisionRoot
    _issuer: object


class PositiveActivationController:
    """Harness-only join for baseline withholding and governed activation."""

    def __init__(
        self,
        encounters: EncounterOpeningController,
        runtime: RuntimePositiveActivationAuthority,
        permit: object,
    ) -> None:
        encounters._claim_activation_controller(self, runtime, permit)
        self._encounters = encounters
        self.runtime = runtime
        self._issuer = object()
        self._witnesses: list[ActivationDecisionWitness] = []
        self._snapshots: list[tuple[object, ...]] = []
        self._practice_runtime: object | None = None
        self._practice_controller: object | None = None
        self._practice_permit = runtime._take_practice_factory_permit(self)

    def witness(
        self,
        encounter_witness: object,
        decision_root: object,
    ) -> ActivationDecisionWitness:
        encounter_witness = self._encounters.require_witness(encounter_witness)
        root = self.runtime.require_root(decision_root)
        if root.predecessor is not encounter_witness.encounter_root:
            raise ActivationWitnessRefusal("activation_witness_chain_mismatch")
        if (
            root.considered.situation is not root.predecessor.situation
            or foreground_values(root.considered.situation)
            != foreground_values(root.predecessor.situation)
            or any(item.decision_root is root for item in self._witnesses)
        ):
            raise ActivationWitnessRefusal("activation_witness_chain_mismatch")
        if type(root) is WithheldDecisionRoot:
            if (
                root.considered.formation_condition != baseline_condition()
                or root.considered.eligible_versions != ()
                or hasattr(root, "handoff_binding")
            ):
                raise ActivationWitnessRefusal("activation_witness_chain_mismatch")
        elif (
            type(root) is not ActivatedDecisionRoot
            or root.considered.formation_condition != treatment_condition()
            or root.considered.eligible_versions != (root.selected_admission,)
            or root.result.selected_admission is not root.selected_admission
            or root.selected_admission.proposal is not root.proposal
            or self.runtime.require_handoff_binding(
                root.handoff_binding, root
            ) is not root.handoff_binding
        ):
            raise ActivationWitnessRefusal("activation_witness_chain_mismatch")
        witness = ActivationDecisionWitness(encounter_witness, root, self._issuer)
        self._witnesses.append(witness)
        self._snapshots.append(
            (
                witness,
                witness.encounter_witness,
                witness.decision_root,
                witness._issuer,
            )
        )
        return witness

    def require_witness(self, witness: object) -> ActivationDecisionWitness:
        snapshot = next(
            (item for item in self._snapshots if item[0] is witness), None
        )
        if (
            type(witness) is not ActivationDecisionWitness
            or snapshot is None
            or witness.encounter_witness is not snapshot[1]
            or witness.decision_root is not snapshot[2]
            or witness._issuer is not snapshot[3]
        ):
            raise ActivationWitnessRefusal("exact_activation_witness_required")
        self._encounters.require_witness(witness.encounter_witness)
        self.runtime.require_root(witness.decision_root)
        return witness

    def require_complete_witnesses(self) -> tuple[ActivationDecisionWitness, ...]:
        if len(self._witnesses) != 2:
            raise ActivationWitnessRefusal("two_activation_witnesses_required")
        current = tuple(self.require_witness(item) for item in self._witnesses)
        types = {type(item.decision_root) for item in current}
        predecessors = {id(item.decision_root.predecessor) for item in current}
        if types != {WithheldDecisionRoot, ActivatedDecisionRoot} or len(predecessors) != 2:
            raise ActivationWitnessRefusal("activation_witness_set_mismatch")
        return current

    def open_positive_practice_request_controller(self) -> object:
        if self._practice_controller is not None:
            raise ActivationWitnessRefusal("practice_request_controller_already_opened")
        witnesses = self.require_complete_witnesses()
        verifiers = tuple(
            self.runtime.root_verifier(witness.decision_root) for witness in witnesses
        )
        from formation.practice_request import RuntimePositivePracticeRequestAuthority
        from trajectory.practice_request import PositivePracticeRequestController

        runtime = RuntimePositivePracticeRequestAuthority(
            verifiers, self.runtime, self, self._practice_permit
        )
        controller = PositivePracticeRequestController(
            self, runtime, self._practice_permit
        )
        self._practice_controller = controller
        return controller

    def _claim_practice_runtime(
        self, runtime: object, permit: object, verifiers: tuple[object, object]
    ) -> None:
        if permit is not self._practice_permit:
            raise ActivationWitnessRefusal("practice_request_controller_factory_required")
        if self._practice_runtime is not None:
            raise ActivationWitnessRefusal("practice_request_controller_already_opened")
        roots = {id(item.decision_root) for item in self.require_complete_witnesses()}
        if (
            len(verifiers) != 2
            or {id(item.root) for item in verifiers} != roots
            or any(
                self.runtime._require_root_verifier(verifier) is not verifier
                for verifier in verifiers
            )
        ):
            raise ActivationWitnessRefusal("exact_positive_request_pair_required")
        self._practice_runtime = runtime

    def _preflight_practice_runtime(
        self, permit: object, verifiers: tuple[object, object]
    ) -> None:
        if permit is not self._practice_permit:
            raise ActivationWitnessRefusal("practice_request_controller_factory_required")
        if self._practice_runtime is not None:
            raise ActivationWitnessRefusal("practice_request_controller_already_opened")
        roots = {id(item.decision_root) for item in self.require_complete_witnesses()}
        if (
            len(verifiers) != 2
            or {id(item.root) for item in verifiers} != roots
            or any(
                self.runtime._require_root_verifier(verifier) is not verifier
                for verifier in verifiers
            )
        ):
            raise ActivationWitnessRefusal("exact_positive_request_pair_required")

    def _claim_practice_controller(
        self, controller: object, runtime: object, permit: object
    ) -> None:
        if permit is not self._practice_permit or runtime is not self._practice_runtime:
            raise ActivationWitnessRefusal("exact_practice_request_runtime_required")
        if self._practice_controller is not None:
            raise ActivationWitnessRefusal("practice_request_controller_already_opened")
        self._practice_controller = controller
