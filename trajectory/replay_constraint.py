"""Harness-owned assignment, witness, and append checks for D-A-010."""

from __future__ import annotations

from dataclasses import dataclass

from formation.replay_constraint import (
    CONSTRAINT_EVENT,
    CONSTRAINT_ORDER,
    POLICY,
    RECORDER,
    TARGET_ROLE,
    ConstraintHandoffRefusal,
    ReplayConstraintBound,
    ReplayConstraintHandoff,
    RuntimeReplayConstraintMaterializer,
)
from trajectory.admitted_root import (
    AdmittedBranchRoot,
    AdmittedTreatmentBatch,
    AdmittedTreatmentBatchRefusal,
    FormationAppendController,
)


class ReplayConstraintAssignmentRefusal(ValueError):
    """The harness cannot issue or use this ablation assignment."""


class ReplayConstraintValidationRefusal(ValueError):
    """The runtime event is not the exact fixture constraint meaning."""


class ReplayConstraintAppendRefusal(ValueError):
    """The witnessed constraint cannot become the post-constraint root."""


_DELIVERY_USE_ISSUER = object()
_CONTROLLER_FACTORY_ISSUER = object()


class _PublicDeliveryUse:
    def __init__(self, issuer: object) -> None:
        if issuer is not _DELIVERY_USE_ISSUER:
            raise ReplayConstraintAssignmentRefusal("delivery_factory_required")
        self._issuer = issuer
        self._delivery: PublicReplayConstraintDelivery | None = None
        self._snapshot: tuple[object, ...] | None = None
        self.used = False

    def bind(self, delivery: PublicReplayConstraintDelivery) -> None:
        if self._delivery is not None:
            raise ReplayConstraintAssignmentRefusal("constraint_delivery_already_bound")
        self._delivery = delivery

        self._snapshot = (
            delivery.run_id,
            delivery.recipient,
            delivery.target_role,
            delivery.policy,
            delivery._use,
            delivery._registry,
            delivery._issuer,
            self._issuer,
        )

    def require(
        self,
        delivery: object,
        root: object,
        *,
        consumed: bool | None = None,
    ) -> PublicReplayConstraintDelivery:
        if (
            type(delivery) is not PublicReplayConstraintDelivery
            or delivery is not self._delivery
            or self._snapshot is None
            or delivery.run_id != self._snapshot[0]
            or delivery.recipient is not self._snapshot[1]
            or delivery.target_role != self._snapshot[2]
            or delivery.policy != self._snapshot[3]
            or delivery._use is not self._snapshot[4]
            or delivery._registry is not self._snapshot[5]
            or delivery._issuer is not self._snapshot[6]
            or self._issuer is not self._snapshot[7]
            or delivery.recipient is not root
            or (consumed is not None and self.used is not consumed)
        ):
            raise ReplayConstraintAssignmentRefusal("exact_root_bound_delivery_required")
        return delivery

    def consume(
        self, delivery: object, root: object
    ) -> PublicReplayConstraintDelivery:
        if self.used:
            raise ReplayConstraintAssignmentRefusal("constraint_delivery_already_consumed")
        current = self.require(delivery, root)
        self.used = True
        return current


class _IssuedDeliveryRegistry:
    """Narrow exact-delivery verifier with no trajectory assignment state."""

    def __init__(self, issuer: object) -> None:
        if issuer is not _DELIVERY_USE_ISSUER:
            raise ReplayConstraintAssignmentRefusal("delivery_registry_factory_required")
        self._delivery: PublicReplayConstraintDelivery | None = None
        self._snapshot: tuple[object, ...] | None = None

    def bind(self, delivery: PublicReplayConstraintDelivery) -> None:
        if self._delivery is not None:
            raise ReplayConstraintAssignmentRefusal("delivery_registry_already_bound")
        self._delivery = delivery
        self._snapshot = (
            delivery,
            delivery.run_id,
            delivery.recipient,
            delivery.target_role,
            delivery.policy,
            delivery._use,
            delivery._registry,
            delivery._issuer,
        )

    def require(self, delivery: object) -> PublicReplayConstraintDelivery:
        if (
            delivery is not self._delivery
            or self._snapshot is None
            or delivery is not self._snapshot[0]
            or delivery.run_id != self._snapshot[1]
            or delivery.recipient is not self._snapshot[2]
            or delivery.target_role != self._snapshot[3]
            or delivery.policy != self._snapshot[4]
            or delivery._use is not self._snapshot[5]
            or delivery._registry is not self._snapshot[6]
            or delivery._issuer is not self._snapshot[7]
        ):
            raise ReplayConstraintAssignmentRefusal("exact_issued_delivery_required")
        return delivery


@dataclass(frozen=True, slots=True)
class AblationAssignment:
    run_id: str
    recipient: AdmittedBranchRoot
    target_role: str
    policy: str
    reason: str
    expected_effect_reference: object
    _issuer: object


@dataclass(frozen=True, slots=True)
class PublicReplayConstraintDelivery:
    run_id: str
    recipient: AdmittedBranchRoot
    target_role: str
    policy: str
    _use: _PublicDeliveryUse
    _registry: _IssuedDeliveryRegistry
    _issuer: object


@dataclass(frozen=True, slots=True)
class ReplayConstraintWitness:
    run_id: str
    assignment: AblationAssignment
    delivery: PublicReplayConstraintDelivery
    handoff: ReplayConstraintHandoff
    _issuer: object


@dataclass(frozen=True, slots=True)
class ReplayConstraintBranchRoot:
    run_id: str
    admitted_root: AdmittedBranchRoot
    constraint: ReplayConstraintBound
    head: object
    _issuer: object


def validate_fixture_replay_constraint(event: object) -> str:
    if type(event) is not ReplayConstraintBound:
        raise ReplayConstraintValidationRefusal("invalid_fixture_replay_constraint")
    source = getattr(event, "_source", None)
    if (
        event.run_id != event.consumed_root.run_id
        or event.order != CONSTRAINT_ORDER
        or event.event != CONSTRAINT_EVENT
        or event.authority != RECORDER
        or event.policy != POLICY
        or source is None
        or source.consumed_root is not event.consumed_root
        or source.target_role != TARGET_ROLE
        or source.target is not event.target
        or event.target is not event.consumed_root.proposal._authorship.source.source_consequence
        or event.parents
        is not getattr(event, "_parents_identity", None)
        or len(event.parents) != 2
        or not any(parent is event.target for parent in event.parents)
        or not any(parent is event.consumed_root.head for parent in event.parents)
    ):
        raise ReplayConstraintValidationRefusal("invalid_fixture_replay_constraint")
    return "valid_fixture_replay_constraint"


class ReplayConstraintAppendController:
    """Trajectory boundary that selects ablation but never authors its event."""

    def __init__(
        self,
        formations: FormationAppendController,
        admitted_batch: object,
        _factory_issuer: object = None,
    ) -> None:
        if _factory_issuer is not _CONTROLLER_FACTORY_ISSUER:
            raise AdmittedTreatmentBatchRefusal("formation_constraint_factory_required")
        if type(formations) is not FormationAppendController:
            raise AdmittedTreatmentBatchRefusal("exact_formation_controller_required")
        self._issuer = object()
        self._root_issuer = object()
        self._formations = formations
        self._batch = formations.require_admitted_treatment_batch(admitted_batch)
        self._assignment: AblationAssignment | None = None
        self._assignment_snapshot: tuple[object, ...] | None = None
        self._delivery: PublicReplayConstraintDelivery | None = None
        self._delivery_snapshot: tuple[object, ...] | None = None
        self._witness: ReplayConstraintWitness | None = None
        self._witness_snapshot: tuple[object, ...] | None = None
        self._root: ReplayConstraintBranchRoot | None = None
        self._root_snapshot: tuple[object, ...] | None = None
        self._runtime: RuntimeReplayConstraintMaterializer | None = None
        self._reservation: object | None = None
        self._delivery_registry = _IssuedDeliveryRegistry(_DELIVERY_USE_ISSUER)

    @classmethod
    def _from_formation(
        cls,
        formations: FormationAppendController,
        admitted_batch: AdmittedTreatmentBatch,
    ) -> ReplayConstraintAppendController:
        return cls(formations, admitted_batch, _CONTROLLER_FACTORY_ISSUER)

    def assign(
        self, reservation: object
    ) -> tuple[AblationAssignment, PublicReplayConstraintDelivery]:
        if self._assignment is not None:
            raise ReplayConstraintAssignmentRefusal("ablation_already_assigned")
        from formation.replay_constraint import ReplayConstraintReservation

        if type(reservation) is not ReplayConstraintReservation:
            raise ReplayConstraintAssignmentRefusal("exact_runtime_reservation_required")
        from formation.replay_constraint import _ReservationUse

        if type(reservation._use) is not _ReservationUse:
            raise ReplayConstraintAssignmentRefusal("exact_runtime_reservation_required")
        reservation._use.require(reservation, self._batch)
        reservation._use.register_delivery_registry(
            reservation, self._batch, self._delivery_registry
        )
        self._reservation = reservation
        recipient = self._formations.resolve_ablation_root(self._batch, self)
        if not any(recipient is root for root in reservation.roots):
            raise ReplayConstraintAssignmentRefusal("reservation_root_set_mismatch")
        effect_reference = object()
        assignment = AblationAssignment(
            run_id=self._batch.run_id,
            recipient=recipient,
            target_role=TARGET_ROLE,
            policy=POLICY,
            reason="causal_probe",
            expected_effect_reference=effect_reference,
            _issuer=self._issuer,
        )
        use = _PublicDeliveryUse(_DELIVERY_USE_ISSUER)
        delivery = PublicReplayConstraintDelivery(
            run_id=self._batch.run_id,
            recipient=recipient,
            target_role=TARGET_ROLE,
            policy=POLICY,
            _use=use,
            _registry=self._delivery_registry,
            _issuer=self._issuer,
        )
        use.bind(delivery)
        self._delivery_registry.bind(delivery)
        self._assignment = assignment
        self._assignment_snapshot = (
            assignment.run_id,
            assignment.recipient,
            assignment.target_role,
            assignment.policy,
            assignment.reason,
            assignment.expected_effect_reference,
            assignment._issuer,
        )
        self._delivery = delivery
        self._delivery_snapshot = (
            delivery.run_id,
            delivery.recipient,
            delivery.target_role,
            delivery.policy,
            delivery._use,
            delivery._registry,
            delivery._issuer,
        )
        return assignment, delivery

    def require_assignment(self, assignment: object) -> AblationAssignment:
        if (
            type(assignment) is not AblationAssignment
            or assignment is not self._assignment
            or self._assignment_snapshot is None
        ):
            raise ReplayConstraintAssignmentRefusal("exact_ablation_assignment_required")
        values = (
            assignment.run_id,
            assignment.recipient,
            assignment.target_role,
            assignment.policy,
            assignment.reason,
            assignment.expected_effect_reference,
            assignment._issuer,
        )
        identity_indexes = (1, 5, 6)
        if any(
            value is not expected
            for index, (value, expected) in enumerate(
                zip(values, self._assignment_snapshot, strict=True)
            )
            if index in identity_indexes
        ) or any(
            value != expected
            for index, (value, expected) in enumerate(
                zip(values, self._assignment_snapshot, strict=True)
            )
            if index not in identity_indexes
        ):
            raise ReplayConstraintAssignmentRefusal("ablation_assignment_changed")
        expected = self._formations.resolve_ablation_root(self._batch, self)
        if assignment.recipient is not expected:
            raise ReplayConstraintAssignmentRefusal("ablation_assignment_root_changed")
        return assignment

    def require_delivery(self, delivery: object) -> PublicReplayConstraintDelivery:
        if (
            type(delivery) is not PublicReplayConstraintDelivery
            or delivery is not self._delivery
            or self._delivery_snapshot is None
        ):
            raise ReplayConstraintAssignmentRefusal("exact_public_constraint_delivery_required")
        values = (
            delivery.run_id,
            delivery.recipient,
            delivery.target_role,
            delivery.policy,
            delivery._use,
            delivery._registry,
            delivery._issuer,
        )
        identity_indexes = (1, 4, 5, 6)
        if any(
            value is not expected
            for index, (value, expected) in enumerate(
                zip(values, self._delivery_snapshot, strict=True)
            )
            if index in identity_indexes
        ) or any(
            value != expected
            for index, (value, expected) in enumerate(
                zip(values, self._delivery_snapshot, strict=True)
            )
            if index not in identity_indexes
        ):
            raise ReplayConstraintAssignmentRefusal("public_constraint_delivery_changed")
        assignment = self.require_assignment(self._assignment)
        if delivery.recipient is not assignment.recipient:
            raise ReplayConstraintAssignmentRefusal("assignment_delivery_root_mismatch")
        return delivery

    def witness(
        self,
        runtime: RuntimeReplayConstraintMaterializer,
        handoff: object,
        assignment: object,
        delivery: object,
    ) -> ReplayConstraintWitness:
        if type(runtime) is not RuntimeReplayConstraintMaterializer:
            raise ReplayConstraintAppendRefusal("exact_constraint_runtime_required")
        if self._witness is not None:
            raise ReplayConstraintAppendRefusal("constraint_already_witnessed")
        assignment = self.require_assignment(assignment)
        delivery = self.require_delivery(delivery)
        try:
            current = runtime.require_current(handoff)
        except ConstraintHandoffRefusal as error:
            raise ReplayConstraintAppendRefusal(str(error)) from error
        if (
            current.source.delivery is not delivery
            or current.event.consumed_root is not assignment.recipient
        ):
            raise ReplayConstraintAppendRefusal("constraint_handoff_assignment_mismatch")
        self._formations.require_returned_root(assignment.recipient)
        validate_fixture_replay_constraint(current.event)
        witness = ReplayConstraintWitness(
            run_id=current.run_id,
            assignment=assignment,
            delivery=delivery,
            handoff=current,
            _issuer=self._issuer,
        )
        self._witness = witness
        self._witness_snapshot = (
            witness.run_id,
            witness.assignment,
            witness.delivery,
            witness.handoff,
            witness._issuer,
        )
        self._runtime = runtime
        return witness

    def _require_witness(self, witness: object) -> ReplayConstraintWitness:
        if (
            type(witness) is not ReplayConstraintWitness
            or witness is not self._witness
            or self._witness_snapshot is None
        ):
            raise ReplayConstraintAppendRefusal("exact_constraint_witness_required")
        values = (
            witness.run_id,
            witness.assignment,
            witness.delivery,
            witness.handoff,
            witness._issuer,
        )
        if any(
            value is not expected
            for value, expected in zip(values, self._witness_snapshot, strict=True)
        ):
            raise ReplayConstraintAppendRefusal("constraint_witness_changed")
        return witness

    def append(
        self,
        runtime: RuntimeReplayConstraintMaterializer,
        handoff: object,
        witness: object,
    ) -> ReplayConstraintBranchRoot:
        if type(runtime) is not RuntimeReplayConstraintMaterializer:
            raise ReplayConstraintAppendRefusal("exact_constraint_runtime_required")
        if self._root is not None:
            raise ReplayConstraintAppendRefusal("constraint_root_already_returned")
        current_witness = self._require_witness(witness)
        try:
            current = runtime.require_current(handoff)
        except ConstraintHandoffRefusal as error:
            raise ReplayConstraintAppendRefusal(str(error)) from error
        if current is not current_witness.handoff or runtime is not self._runtime:
            raise ReplayConstraintAppendRefusal("constraint_witness_handoff_mismatch")
        validate_fixture_replay_constraint(current.event)
        admitted_root = self._formations.require_returned_root(
            current.event.consumed_root
        )
        root = ReplayConstraintBranchRoot(
            run_id=current.run_id,
            admitted_root=admitted_root,
            constraint=current.event,
            head=current.event.coordinate,
            _issuer=self._root_issuer,
        )
        self._root = root
        self._root_snapshot = (
            root.run_id,
            root.admitted_root,
            root.constraint,
            root.head,
            root._issuer,
            runtime,
            current,
            current_witness,
        )
        return root

    def require_returned_root(self, root: object) -> ReplayConstraintBranchRoot:
        if (
            type(root) is not ReplayConstraintBranchRoot
            or root is not self._root
            or self._root_snapshot is None
        ):
            raise ReplayConstraintAppendRefusal("exact_replay_constraint_root_required")
        snapshot = self._root_snapshot
        runtime = snapshot[5]
        handoff = snapshot[6]
        witness = snapshot[7]
        try:
            current = runtime.require_current(handoff)
        except ValueError as error:
            raise ReplayConstraintAppendRefusal("replay_constraint_root_changed") from error
        if (
            root.run_id != snapshot[0]
            or root.admitted_root is not snapshot[1]
            or root.constraint is not snapshot[2]
            or root.head is not snapshot[3]
            or root._issuer is not snapshot[4]
            or current is not handoff
            or self.require_assignment(self._assignment) is not self._assignment
            or self.require_delivery(self._delivery) is not self._delivery
            or self._delivery._use.require(
                self._delivery, root.admitted_root, consumed=True
            )
            is not self._delivery
            or self._reservation is None
            or self._reservation._use.require(
                self._reservation, self._batch
            )
            is not self._reservation
            or self._require_witness(witness) is not witness
            or current.event is not root.constraint
        ):
            raise ReplayConstraintAppendRefusal("replay_constraint_root_changed")
        self._formations.require_returned_root(root.admitted_root)
        validate_fixture_replay_constraint(root.constraint)
        return root
