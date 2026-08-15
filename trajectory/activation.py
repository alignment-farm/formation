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
