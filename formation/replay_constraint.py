"""Runtime-owned fixture capability for the D-A-010 constraint append.

This module binds one public constraint at an admitted head. It deliberately
does not derive or represent a constrained replay view.
"""

from __future__ import annotations

from dataclasses import dataclass
import re


TARGET_ROLE = "retained_acquisition_consequence"
POLICY = "transitive_exclusion"
CONSTRAINT_ORDER = 10
CONSTRAINT_EVENT = "replay_constraint_bound"
RECORDER = "formation_runtime"

_RUN_ISSUER = object()
_COORDINATE_ISSUER = object()
_SOURCE_ISSUER = object()


def _contains_hidden_branch_label(value: str) -> bool:
    lowered = value.lower()
    return any(
        word in lowered for word in ("baseline", "governed", "ablation")
    ) or re.search(r"(^|[^a-z0-9])[bga]([^a-z0-9]|$)", lowered) is not None


class ReplayConstraintReservationRefusal(ValueError):
    """The runtime's label-blind constraint reservation is unavailable."""


class ReplayConstraintSourceRefusal(ValueError):
    """The runtime cannot resolve this public constraint source."""


class ConstraintHandoffRefusal(ValueError):
    """The runtime constraint event or handoff is not current."""


class OpaqueReplayConstraintCoordinate:
    """Identity-only runtime coordinate with no selected wire encoding."""

    __slots__ = ("_run_id", "_sequence", "_issuer")

    def __init__(self, run_id: str, sequence: int) -> None:
        self._run_id = run_id
        self._sequence = sequence
        self._issuer = _COORDINATE_ISSUER


class _ReservationUse:
    def __init__(self, run: RuntimeReplayConstraintRun, batch: object) -> None:
        self._run = run
        self._batch = batch
        self._reservation: ReplayConstraintReservation | None = None
        self._snapshot: tuple[object, ...] | None = None
        self._delivery_registry: object | None = None

    def bind(self, reservation: ReplayConstraintReservation) -> None:
        if self._reservation is not None:
            raise ReplayConstraintReservationRefusal("constraint_reservation_already_bound")
        self._reservation = reservation
        self._snapshot = (self._run, self._batch, reservation)

    def require(self, reservation: object, batch: object) -> ReplayConstraintReservation:
        if (
            type(reservation) is not ReplayConstraintReservation
            or reservation is not self._reservation
            or batch is not self._batch
            or self._snapshot is None
            or self._run is not self._snapshot[0]
            or self._batch is not self._snapshot[1]
            or self._reservation is not self._snapshot[2]
        ):
            raise ReplayConstraintReservationRefusal("exact_constraint_reservation_required")
        return self._run.require_reservation(reservation)

    def register_delivery_registry(
        self, reservation: object, batch: object, registry: object
    ) -> None:
        from trajectory.replay_constraint import _IssuedDeliveryRegistry

        self.require(reservation, batch)
        if type(registry) is not _IssuedDeliveryRegistry:
            raise ReplayConstraintReservationRefusal("exact_delivery_registry_required")
        if self._delivery_registry is not None:
            raise ReplayConstraintReservationRefusal("delivery_registry_already_registered")
        self._delivery_registry = registry
        self._run._register_delivery_registry(registry)


@dataclass(frozen=True, slots=True)
class ReplayConstraintReservation:
    run_id: str
    roots: tuple[object, object]
    _use: _ReservationUse
    _issuer: object


class _ConstraintSourceUse:
    def __init__(self) -> None:
        self._source: FixtureReplayConstraintSource | None = None
        self.used = False

    def bind(self, source: FixtureReplayConstraintSource) -> None:
        if self._source is not None:
            raise ReplayConstraintSourceRefusal("constraint_source_already_bound")
        self._source = source

    def consume(self, source: object) -> FixtureReplayConstraintSource:
        if self.used:
            raise ReplayConstraintSourceRefusal("constraint_source_already_consumed")
        if type(source) is not FixtureReplayConstraintSource or source is not self._source:
            raise ReplayConstraintSourceRefusal("exact_constraint_source_required")
        self.used = True
        return source

    def require(
        self, source: object, *, consumed: bool | None = None
    ) -> FixtureReplayConstraintSource:
        if (
            type(source) is not FixtureReplayConstraintSource
            or source is not self._source
            or (consumed is not None and self.used is not consumed)
        ):
            raise ReplayConstraintSourceRefusal("exact_constraint_source_required")
        return source


@dataclass(frozen=True, slots=True)
class FixtureReplayConstraintSource:
    run_id: str
    consumed_root: object
    source_head: object
    target_role: str
    target: object
    policy: str
    delivery: object
    _use: _ConstraintSourceUse
    _issuer: object


@dataclass(frozen=True, slots=True)
class ReplayConstraintBound:
    run_id: str
    consumed_root: object
    coordinate: OpaqueReplayConstraintCoordinate
    order: int
    event: str
    authority: str
    parents: frozenset[object]
    target: object
    policy: str
    _source: FixtureReplayConstraintSource
    _parents_identity: frozenset[object]
    _issuer: object


@dataclass(frozen=True, slots=True)
class ReplayConstraintHandoff:
    run_id: str
    source: FixtureReplayConstraintSource
    event: ReplayConstraintBound
    _issuer: object


class RuntimeReplayConstraintRun:
    """Reserve constraint coordinates before the later ablation assignment."""

    def __init__(self, run_id: str, admitted_batch: object) -> None:
        from trajectory.admitted_root import AdmittedTreatmentBatch

        if not isinstance(run_id, str) or not run_id:
            raise ReplayConstraintReservationRefusal("invalid_run_id")
        if _contains_hidden_branch_label(run_id):
            raise ReplayConstraintReservationRefusal("label_bearing_run_id")
        if type(admitted_batch) is not AdmittedTreatmentBatch:
            raise ReplayConstraintReservationRefusal("exact_admitted_treatment_batch_required")
        if admitted_batch.run_id != run_id:
            raise ReplayConstraintReservationRefusal("admitted_treatment_batch_run_mismatch")
        roots = admitted_batch._use.consume(admitted_batch)
        if len(roots) != 2 or roots[0] is roots[1]:
            raise ReplayConstraintReservationRefusal("exact_two_admitted_roots_required")
        self.run_id = run_id
        self._batch = admitted_batch
        self._admitted_verifier = admitted_batch._use
        self._slots = tuple(
            (
                root,
                OpaqueReplayConstraintCoordinate(run_id, index + 1),
            )
            for index, root in enumerate(roots)
        )
        self._slot_snapshot = tuple(
            (
                root,
                coordinate,
                coordinate._run_id,
                coordinate._sequence,
                coordinate._issuer,
            )
            for root, coordinate in self._slots
        )
        self._opened: list[object] = []
        self._materializers: tuple[RuntimeReplayConstraintMaterializer, ...] = ()
        self._materializer_snapshots: tuple[tuple[object, ...], ...] = ()
        self._delivery_registry: object | None = None
        use = _ReservationUse(self, admitted_batch)
        self._reservation = ReplayConstraintReservation(
            run_id=run_id,
            roots=(roots[0], roots[1]),
            _use=use,
            _issuer=_RUN_ISSUER,
        )
        use.bind(self._reservation)
        self._reservation_snapshot = (
            self._reservation.run_id,
            self._reservation.roots,
            self._reservation._use,
            self._reservation._issuer,
        )

    def reservation(self) -> ReplayConstraintReservation:
        return self.require_reservation(self._reservation)

    def require_reservation(self, reservation: object) -> ReplayConstraintReservation:
        self._batch._use.require(self._batch, consumed=True)
        if (
            type(reservation) is not ReplayConstraintReservation
            or reservation is not self._reservation
        ):
            raise ReplayConstraintReservationRefusal("exact_constraint_reservation_required")
        snapshot = self._reservation_snapshot
        if (
            reservation.run_id != snapshot[0]
            or reservation.roots is not snapshot[1]
            or reservation._use is not snapshot[2]
            or reservation._issuer is not snapshot[3]
        ):
            raise ReplayConstraintReservationRefusal("constraint_reservation_changed")
        for current, expected in zip(self._slots, self._slot_snapshot, strict=True):
            root, coordinate = current
            if (
                root is not expected[0]
                or coordinate is not expected[1]
                or coordinate._run_id != expected[2]
                or coordinate._sequence != expected[3]
                or coordinate._issuer is not expected[4]
            ):
                raise ReplayConstraintReservationRefusal("constraint_reservation_changed")
            self._admitted_verifier.require_root(root)
        return reservation

    def materializer(
        self, root: object, delivery: object
    ) -> RuntimeReplayConstraintMaterializer:
        from trajectory.replay_constraint import (
            PublicReplayConstraintDelivery,
            _DELIVERY_USE_ISSUER,
            _PublicDeliveryUse,
        )

        self.require_reservation(self._reservation)
        if (
            type(delivery) is not PublicReplayConstraintDelivery
            or delivery.recipient is not root
            or type(delivery._use) is not _PublicDeliveryUse
            or delivery._use._issuer is not _DELIVERY_USE_ISSUER
            or delivery._registry is not self._delivery_registry
        ):
            raise ReplayConstraintReservationRefusal(
                "root_bound_constraint_delivery_required"
            )
        try:
            delivery._registry.require(delivery)
            current_delivery = delivery._use.require(delivery, root)
        except ValueError as error:
            raise ReplayConstraintReservationRefusal(str(error)) from error
        if current_delivery is not delivery:
            raise ReplayConstraintReservationRefusal(
                "root_bound_constraint_delivery_required"
            )
        slot = next((item for item in self._slots if item[0] is root), None)
        if slot is None:
            raise ReplayConstraintReservationRefusal("exact_reserved_admitted_root_required")
        if any(opened is root for opened in self._opened):
            raise ReplayConstraintReservationRefusal("constraint_materializer_already_opened")
        self._opened.append(root)
        materializer = RuntimeReplayConstraintMaterializer(
            self, slot[0], slot[1], delivery, _RUN_ISSUER
        )
        self._materializers = (*self._materializers, materializer)
        self._materializer_snapshots = (
            *self._materializer_snapshots,
            (materializer, slot[0], slot[1], delivery),
        )
        return materializer

    def _register_delivery_registry(self, registry: object) -> None:
        if self._delivery_registry is not None:
            raise ReplayConstraintReservationRefusal("delivery_registry_already_registered")
        self._delivery_registry = registry

    def require_materializer(
        self,
        materializer: object,
        root: object,
        coordinate: object,
        delivery: object,
    ) -> None:
        matches = tuple(
            snapshot
            for snapshot in self._materializer_snapshots
            if snapshot[0] is materializer
        )
        if (
            len(matches) != 1
            or not any(materializer is item for item in self._materializers)
            or matches[0][1] is not root
            or matches[0][2] is not coordinate
            or matches[0][3] is not delivery
        ):
            raise ReplayConstraintReservationRefusal(
                "exact_registered_constraint_materializer_required"
            )


class RuntimeReplayConstraintMaterializer:
    """Resolve one public target role and author one constraint event."""

    def __init__(
        self,
        run: RuntimeReplayConstraintRun,
        root: object,
        coordinate: OpaqueReplayConstraintCoordinate,
        delivery: object,
        issuer: object,
    ) -> None:
        if type(run) is not RuntimeReplayConstraintRun or issuer is not _RUN_ISSUER:
            raise ReplayConstraintReservationRefusal("runtime_constraint_factory_required")
        self.run_id = run.run_id
        self._run = run
        self._root = root
        self._coordinate = coordinate
        self._delivery = delivery
        self._reserved = (
            root,
            coordinate,
            coordinate._run_id,
            coordinate._sequence,
            coordinate._issuer,
        )
        self._issuer = object()
        self._source: FixtureReplayConstraintSource | None = None
        self._source_snapshot: tuple[object, ...] | None = None
        self._handoff: ReplayConstraintHandoff | None = None
        self._handoff_snapshot: tuple[object, ...] | None = None

    def _require_reservation(self) -> None:
        self._run.require_reservation(self._run._reservation)
        self._run.require_materializer(
            self, self._root, self._coordinate, self._delivery
        )
        if (
            self._root is not self._reserved[0]
            or self._coordinate is not self._reserved[1]
            or self._coordinate._run_id != self._reserved[2]
            or self._coordinate._sequence != self._reserved[3]
            or self._coordinate._issuer is not self._reserved[4]
        ):
            raise ReplayConstraintReservationRefusal("constraint_reservation_changed")
        self._run._admitted_verifier.require_root(self._root)

    def adapt_source(self, delivery: object) -> FixtureReplayConstraintSource:
        from trajectory.replay_constraint import (
            PublicReplayConstraintDelivery,
            _DELIVERY_USE_ISSUER,
            _PublicDeliveryUse,
        )

        if self._source is not None:
            raise ReplayConstraintSourceRefusal("constraint_source_already_issued")
        self._require_reservation()
        if (
            type(delivery) is not PublicReplayConstraintDelivery
            or type(delivery._use) is not _PublicDeliveryUse
            or delivery._use._issuer is not _DELIVERY_USE_ISSUER
            or delivery._registry is not self._run._delivery_registry
        ):
            raise ReplayConstraintSourceRefusal("exact_public_constraint_delivery_required")
        delivery._registry.require(delivery)
        if delivery is not self._delivery:
            raise ReplayConstraintSourceRefusal("exact_public_constraint_delivery_required")
        try:
            current_delivery = delivery._use.consume(delivery, self._root)
        except ValueError as error:
            raise ReplayConstraintSourceRefusal(str(error)) from error
        if (
            current_delivery.run_id != self.run_id
            or current_delivery.recipient is not self._root
            or current_delivery.target_role != TARGET_ROLE
            or current_delivery.policy != POLICY
        ):
            raise ReplayConstraintSourceRefusal("invalid_public_constraint_delivery")
        formation_source = self._root.proposal._authorship.source
        target = formation_source.source_consequence
        if (
            target.coordinate != "D-C-005"
            or target.root is not self._root.condition_root
            or formation_source.consumed_root is not self._root.condition_root
            or self._root.admission.warrant.source_consequence != "D-C-005"
        ):
            raise ReplayConstraintSourceRefusal("retained_consequence_target_unavailable")
        use = _ConstraintSourceUse()
        source = FixtureReplayConstraintSource(
            run_id=self.run_id,
            consumed_root=self._root,
            source_head=self._root.head,
            target_role=TARGET_ROLE,
            target=target,
            policy=POLICY,
            delivery=current_delivery,
            _use=use,
            _issuer=_SOURCE_ISSUER,
        )
        use.bind(source)
        self._source = source
        self._source_snapshot = (
            source.run_id,
            source.consumed_root,
            source.source_head,
            source.target_role,
            source.target,
            source.policy,
            source.delivery,
            source._use,
            source._issuer,
            target.root,
            target.coordinate,
            target.artifact,
            target._issuer,
            current_delivery.run_id,
            current_delivery.recipient,
            current_delivery.target_role,
            current_delivery.policy,
            current_delivery._use,
            current_delivery._issuer,
        )
        return source

    def _require_source(self, source: object) -> FixtureReplayConstraintSource:
        if source is not self._source or self._source_snapshot is None:
            raise ReplayConstraintSourceRefusal("exact_constraint_source_required")
        snapshot = self._source_snapshot
        values = (
            source.run_id,
            source.consumed_root,
            source.source_head,
            source.target_role,
            source.target,
            source.policy,
            source.delivery,
            source._use,
            source._issuer,
            source.target.root,
            source.target.coordinate,
            source.target.artifact,
            source.target._issuer,
            source.delivery.run_id,
            source.delivery.recipient,
            source.delivery.target_role,
            source.delivery.policy,
            source.delivery._use,
            source.delivery._issuer,
        )
        identity_indexes = (1, 2, 4, 6, 7, 8, 9, 11, 12, 14, 17, 18)
        if any(
            value is not expected
            for index, (value, expected) in enumerate(zip(values, snapshot, strict=True))
            if index in identity_indexes
        ) or any(
            value != expected
            for index, (value, expected) in enumerate(zip(values, snapshot, strict=True))
            if index not in identity_indexes
        ):
            raise ReplayConstraintSourceRefusal("constraint_source_changed")
        return source

    def materialize(self, source: object) -> ReplayConstraintHandoff:
        if self._handoff is not None:
            raise ConstraintHandoffRefusal("constraint_already_materialized")
        self._require_reservation()
        current = self._require_source(source)
        current._use.consume(current)
        parents = frozenset((current.target, current.source_head))
        event = ReplayConstraintBound(
            run_id=self.run_id,
            consumed_root=self._root,
            coordinate=self._coordinate,
            order=CONSTRAINT_ORDER,
            event=CONSTRAINT_EVENT,
            authority=RECORDER,
            parents=parents,
            target=current.target,
            policy=POLICY,
            _source=current,
            _parents_identity=parents,
            _issuer=self._issuer,
        )
        handoff = ReplayConstraintHandoff(
            run_id=self.run_id,
            source=current,
            event=event,
            _issuer=self._issuer,
        )
        self._handoff = handoff
        self._handoff_snapshot = (
            handoff.run_id,
            handoff.source,
            handoff.event,
            handoff._issuer,
            event.run_id,
            event.consumed_root,
            event.coordinate,
            event.order,
            event.event,
            event.authority,
            event.parents,
            event.target,
            event.policy,
            event._source,
            event._parents_identity,
            event._issuer,
            self._coordinate._run_id,
            self._coordinate._sequence,
            self._coordinate._issuer,
        )
        return handoff

    def require_current(self, handoff: object) -> ReplayConstraintHandoff:
        self._require_reservation()
        if type(handoff) is not ReplayConstraintHandoff or handoff is not self._handoff:
            raise ConstraintHandoffRefusal("exact_current_constraint_handoff_required")
        if self._handoff_snapshot is None:
            raise ConstraintHandoffRefusal("missing_constraint_handoff_snapshot")
        self._require_source(handoff.source)
        handoff.source._use.require(handoff.source, consumed=True)
        handoff.source.delivery._use.require(
            handoff.source.delivery, self._root, consumed=True
        )
        handoff.source.delivery._registry.require(handoff.source.delivery)
        event = handoff.event
        values = (
            handoff.run_id,
            handoff.source,
            handoff.event,
            handoff._issuer,
            event.run_id,
            event.consumed_root,
            event.coordinate,
            event.order,
            event.event,
            event.authority,
            event.parents,
            event.target,
            event.policy,
            event._source,
            event._parents_identity,
            event._issuer,
            event.coordinate._run_id,
            event.coordinate._sequence,
            event.coordinate._issuer,
        )
        identity_indexes = (1, 2, 3, 5, 6, 10, 11, 13, 14, 15, 18)
        if any(
            value is not expected
            for index, (value, expected) in enumerate(
                zip(values, self._handoff_snapshot, strict=True)
            )
            if index in identity_indexes
        ) or any(
            value != expected
            for index, (value, expected) in enumerate(
                zip(values, self._handoff_snapshot, strict=True)
            )
            if index not in identity_indexes
        ):
            raise ConstraintHandoffRefusal("constraint_handoff_changed")
        if (
            event.target is not handoff.source.target
            or event._source is not handoff.source
            or event.parents is not event._parents_identity
            or not any(parent is event.target for parent in event.parents)
            or not any(parent is event.consumed_root.head for parent in event.parents)
        ):
            raise ConstraintHandoffRefusal("constraint_handoff_changed")
        return handoff
