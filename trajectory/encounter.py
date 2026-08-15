"""Harness witness for fixture-local positive encounter opening."""

from __future__ import annotations

from dataclasses import dataclass

from formation.encounter import (
    EncounterBranchRoot,
    EncounterOpeningBinding,
    RuntimeEncounterOpener,
)
from formation.foreground import RuntimeForegroundConsumer, foreground_values
from trajectory.foreground import (
    ForegroundDeliveryController,
    PositiveCaseAssignment,
    ReceivedForegroundWitness,
)


class EncounterWitnessRefusal(ValueError):
    """The harness cannot witness this encounter-opening chain."""


@dataclass(frozen=True, slots=True)
class EncounterOpeningWitness:
    case_assignment: PositiveCaseAssignment
    foreground_witness: ReceivedForegroundWitness
    opening_binding: EncounterOpeningBinding
    encounter_root: EncounterBranchRoot
    _issuer: object


class EncounterOpeningController:
    """Trajectory-only join over runtime-authored encounter roots."""

    def __init__(
        self,
        foreground: ForegroundDeliveryController,
        runtime: RuntimeEncounterOpener,
        permit: object,
    ) -> None:
        if type(foreground) is not ForegroundDeliveryController:
            raise EncounterWitnessRefusal("encounter_controller_factory_required")
        foreground._claim_encounter_controller(self, runtime, permit)
        self._foreground = foreground
        self.runtime = runtime
        self._issuer = object()
        self._witnesses: list[EncounterOpeningWitness] = []
        self._snapshots: list[tuple[object, ...]] = []

    def witness(
        self,
        assignment: object,
        foreground_witness: object,
        consumer: object,
        handoff: object,
        binding: object,
        root: object,
    ) -> EncounterOpeningWitness:
        assignment = self._foreground._require_assignment(assignment)
        foreground_witness = self._foreground.require_witness(foreground_witness)
        if (
            type(consumer) is not RuntimeForegroundConsumer
            or type(root) is not EncounterBranchRoot
            or foreground_witness.case_assignment is not assignment
            or foreground_witness.handoff is not handoff
            or assignment.recipient is not root.predecessor
        ):
            raise EncounterWitnessRefusal("encounter_witness_chain_mismatch")
        current = self.runtime.require_root(root)
        self.runtime.require_binding(
            binding,
            consumer,
            handoff,
            current.predecessor,
            opened=True,
        )
        freeze = assignment.freeze
        if (
            current.opening_binding is not binding
            or current.situation is not handoff.foreground
            or current.situation is not freeze.foreground
            or foreground_values(current.situation)
            != foreground_values(freeze.foreground)
            or any(item.encounter_root is current for item in self._witnesses)
            or any(item.opening_binding is binding for item in self._witnesses)
        ):
            raise EncounterWitnessRefusal("encounter_witness_chain_mismatch")
        witness = EncounterOpeningWitness(
            assignment, foreground_witness, binding, current, self._issuer
        )
        self._witnesses.append(witness)
        self._snapshots.append(
            (
                witness,
                witness.case_assignment,
                witness.foreground_witness,
                witness.opening_binding,
                witness.encounter_root,
                witness._issuer,
                consumer,
                handoff,
            )
        )
        return witness

    def require_witness(self, witness: object) -> EncounterOpeningWitness:
        snapshot = next(
            (item for item in self._snapshots if item[0] is witness), None
        )
        if (
            type(witness) is not EncounterOpeningWitness
            or snapshot is None
            or witness.case_assignment is not snapshot[1]
            or witness.foreground_witness is not snapshot[2]
            or witness.opening_binding is not snapshot[3]
            or witness.encounter_root is not snapshot[4]
            or witness._issuer is not snapshot[5]
        ):
            raise EncounterWitnessRefusal("exact_encounter_witness_required")
        assignment = self._foreground._require_assignment(witness.case_assignment)
        self._foreground.require_witness(witness.foreground_witness)
        root = self.runtime.require_root(witness.encounter_root)
        self.runtime.require_binding(
            witness.opening_binding,
            snapshot[6],
            snapshot[7],
            root.predecessor,
            opened=True,
        )
        if (
            root.predecessor is not assignment.recipient
            or root.situation is not assignment.freeze.foreground
        ):
            raise EncounterWitnessRefusal("encounter_witness_chain_mismatch")
        return witness

    def require_complete_witnesses(self) -> tuple[EncounterOpeningWitness, ...]:
        if len(self._witnesses) != 3:
            raise EncounterWitnessRefusal("three_encounter_witnesses_required")
        current = tuple(self.require_witness(item) for item in self._witnesses)
        roots = tuple(item.encounter_root.predecessor for item in current)
        expected = self._foreground._require_roots()
        if len({id(root) for root in roots}) != 3 or not all(
            any(root is candidate for candidate in roots) for root in expected
        ):
            raise EncounterWitnessRefusal("encounter_witness_set_mismatch")
        return current
