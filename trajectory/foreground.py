"""Harness-owned fixture boundary for one shared positive foreground."""

from __future__ import annotations

from dataclasses import dataclass

from formation.foreground import (
    FixturePositiveForegroundSource,
    PositiveForegroundDelivery,
    ReceivedForegroundHandoff,
    RuntimeForegroundConsumer,
    _CONSUMER_FACTORY_ISSUER,
    _issue_positive_foreground_delivery,
    adapt_positive_foreground_source,
    fixture_positive_foreground_protocol,
    foreground_values,
)
from trajectory.admitted_root import AdmittedBranchRoot, FormationAppendController
from trajectory.fixture_condition import BranchLocalRoot, ConditionAppendController
from trajectory.replay_constraint import (
    ReplayConstraintAppendController,
    ReplayConstraintBranchRoot,
)


class ForegroundRecipientRefusal(ValueError):
    """The exact comparison recipient set is unavailable."""


class ForegroundValidationRefusal(ValueError):
    """The fixture foreground is not the exact seven-role value."""


class ForegroundDeliveryRefusal(ValueError):
    """The foreground freeze, delivery, or handoff is not current."""


@dataclass(frozen=True, slots=True)
class ForegroundComparisonGroup:
    run_id: str
    baseline: BranchLocalRoot
    governed: AdmittedBranchRoot
    ablation: ReplayConstraintBranchRoot
    _issuer: object


@dataclass(frozen=True, slots=True)
class FrozenPositiveForeground:
    run_id: str
    comparison_group: ForegroundComparisonGroup
    source: FixturePositiveForegroundSource
    foreground: object
    authorized_roots: tuple[object, object, object]
    _issuer: object


@dataclass(frozen=True, slots=True)
class ForegroundBound:
    freeze: FrozenPositiveForeground
    _issuer: object


@dataclass(frozen=True, slots=True)
class PositiveCaseAssignment:
    freeze: FrozenPositiveForeground
    recipient: object
    _issuer: object


@dataclass(frozen=True, slots=True)
class ReceivedForegroundWitness:
    freeze: FrozenPositiveForeground
    case_assignment: PositiveCaseAssignment
    handoff: ReceivedForegroundHandoff
    _issuer: object


def validate_fixture_positive_foreground(value: object) -> str:
    try:
        values = foreground_values(value)
    except (TypeError, ValueError, AttributeError) as error:
        raise ForegroundValidationRefusal("invalid_fixture_positive_foreground") from error
    if values != (
        "bundle-9",
        "registry-manifest",
        7,
        8,
        True,
        "release",
        "rebuild_then_release",
    ) or tuple(type(item) for item in values) != (
        str, str, int, int, bool, str, str
    ):
        raise ForegroundValidationRefusal("invalid_fixture_positive_foreground")
    return "valid_fixture_positive_foreground"


class ForegroundDeliveryController:
    """Freeze and deliver one public value to three exact current roots."""

    def __init__(
        self,
        constraints: ReplayConstraintAppendController,
        baseline: object,
        governed: object,
        ablation: object,
        _factory_permit: object = None,
    ) -> None:
        if (
            type(constraints) is not ReplayConstraintAppendController
            or _factory_permit is None
            or _factory_permit is not constraints._foreground_open_permit
        ):
            raise ForegroundRecipientRefusal(
                "constraint_foreground_factory_required"
            )
        formations = constraints._formations
        conditions = formations._conditions
        if (
            type(conditions) is not ConditionAppendController
            or type(formations) is not FormationAppendController
            or type(constraints) is not ReplayConstraintAppendController
        ):
            raise ForegroundRecipientRefusal("exact_root_controllers_required")
        baseline = conditions.require_returned_root(baseline)
        governed = formations.require_returned_root(governed)
        ablation = constraints.require_returned_root(ablation)
        run_ids = (
            baseline.prefix_root.run_id,
            governed.run_id,
            ablation.run_id,
        )
        if len(set(run_ids)) != 1:
            raise ForegroundRecipientRefusal("foreground_recipient_run_mismatch")
        if (
            baseline is governed
            or baseline is ablation
            or governed is ablation
            or ablation.admitted_root is not formations.resolve_ablation_root(
                formations._admitted_batch, constraints
            )
        ):
            raise ForegroundRecipientRefusal("exact_three_foreground_recipients_required")
        baseline_label = conditions.assignment_label_for_formation(
            baseline, formations._issuer
        )
        governed_label = conditions.assignment_label_for_formation(
            governed.condition_root, formations._issuer
        )
        if baseline_label != "baseline" or governed_label != "governed":
            raise ForegroundRecipientRefusal("foreground_recipient_meaning_mismatch")
        self._conditions = conditions
        self._formations = formations
        self._constraints = constraints
        self._issuer = object()
        self._protocol = fixture_positive_foreground_protocol()
        self._group = ForegroundComparisonGroup(
            run_ids[0], baseline, governed, ablation, self._issuer
        )
        self._group_snapshot = (
            self._group.run_id,
            self._group.baseline,
            self._group.governed,
            self._group.ablation,
            self._group._issuer,
        )
        self._verifiers = (
            conditions.foreground_root_verifier(baseline, formations._issuer),
            formations.foreground_root_verifier(governed, constraints),
            constraints.foreground_root_verifier(ablation),
        )
        if any(
            verifier.root is not root
            for verifier, root in zip(
                self._verifiers,
                (baseline, governed, ablation),
                strict=True,
            )
        ):
            raise ForegroundRecipientRefusal("foreground_recipient_verifier_mismatch")
        self._freeze: FrozenPositiveForeground | None = None
        self._freeze_snapshot: tuple[object, ...] | None = None
        self._bound: ForegroundBound | None = None
        self._assignments: list[PositiveCaseAssignment] = []
        self._assignment_snapshots: list[tuple[object, ...]] = []
        self._deliveries: list[PositiveForegroundDelivery] = []
        self._consumers: list[RuntimeForegroundConsumer] = []
        self._witnesses: list[ReceivedForegroundWitness] = []
        self._witness_snapshots: list[tuple[object, ...]] = []
        constraints._claim_foreground_controller(self, _factory_permit)

    @classmethod
    def _from_constraint_controller(
        cls,
        constraints: ReplayConstraintAppendController,
        baseline: object,
        governed: object,
        ablation: object,
        permit: object,
    ) -> ForegroundDeliveryController:
        return cls(
            constraints,
            baseline,
            governed,
            ablation,
            permit,
        )

    def _require_roots(self) -> tuple[object, object, object]:
        group = self._group
        if (
            group.run_id != self._group_snapshot[0]
            or group.baseline is not self._group_snapshot[1]
            or group.governed is not self._group_snapshot[2]
            or group.ablation is not self._group_snapshot[3]
            or group._issuer is not self._group_snapshot[4]
        ):
            raise ForegroundRecipientRefusal("foreground_group_changed")
        self._conditions.require_returned_root(group.baseline)
        self._formations.require_returned_root(group.governed)
        self._constraints.require_returned_root(group.ablation)
        for verifier, root in zip(
            self._verifiers,
            (group.baseline, group.governed, group.ablation),
            strict=True,
        ):
            if verifier.require(root) is not root:
                raise ForegroundRecipientRefusal("foreground_recipient_not_current")
        return group.baseline, group.governed, group.ablation

    def freeze(self) -> FrozenPositiveForeground:
        if self._freeze is not None:
            raise ForegroundDeliveryRefusal("positive_foreground_already_frozen")
        roots = self._require_roots()
        source = adapt_positive_foreground_source(
            self._group.run_id, self._protocol
        )
        validate_fixture_positive_foreground(source.foreground)
        freeze = FrozenPositiveForeground(
            run_id=self._group.run_id,
            comparison_group=self._group,
            source=source,
            foreground=source.foreground,
            authorized_roots=roots,
            _issuer=self._issuer,
        )
        self._freeze = freeze
        self._freeze_snapshot = (
            freeze.run_id,
            freeze.comparison_group,
            freeze.source,
            freeze.foreground,
            freeze.authorized_roots,
            freeze._issuer,
            foreground_values(freeze.foreground),
            source.run_id,
            source.foreground,
            source._issuer,
        )
        return freeze

    def _require_freeze(self, freeze: object) -> FrozenPositiveForeground:
        if (
            type(freeze) is not FrozenPositiveForeground
            or freeze is not self._freeze
            or self._freeze_snapshot is None
        ):
            raise ForegroundDeliveryRefusal("exact_frozen_positive_foreground_required")
        snapshot = self._freeze_snapshot
        if (
            freeze.run_id != snapshot[0]
            or freeze.comparison_group is not snapshot[1]
            or freeze.source is not snapshot[2]
            or freeze.foreground is not snapshot[3]
            or freeze.authorized_roots is not snapshot[4]
            or freeze._issuer is not snapshot[5]
            or foreground_values(freeze.foreground) != snapshot[6]
            or freeze.source.run_id != snapshot[7]
            or freeze.source.foreground is not snapshot[8]
            or freeze.source._issuer is not snapshot[9]
            or freeze.source.foreground is not freeze.foreground
            or freeze.authorized_roots != self._require_roots()
        ):
            raise ForegroundDeliveryRefusal("frozen_positive_foreground_changed")
        validate_fixture_positive_foreground(freeze.foreground)
        return freeze

    def bind(self, freeze: object) -> ForegroundBound:
        freeze = self._require_freeze(freeze)
        if self._bound is not None:
            raise ForegroundDeliveryRefusal("foreground_already_bound")
        self._bound = ForegroundBound(freeze, self._issuer)
        return self._bound

    def _require_bound(self, bound: object) -> ForegroundBound:
        if (
            type(bound) is not ForegroundBound
            or bound is not self._bound
            or bound.freeze is not self._freeze
            or bound._issuer is not self._issuer
        ):
            raise ForegroundDeliveryRefusal("exact_foreground_binding_required")
        self._require_freeze(bound.freeze)
        return bound

    def assign_case(
        self, bound: object, root: object
    ) -> PositiveCaseAssignment:
        bound = self._require_bound(bound)
        freeze = self._require_freeze(bound.freeze)
        if not any(root is candidate for candidate in freeze.authorized_roots):
            raise ForegroundRecipientRefusal("unauthorized_foreground_recipient")
        if any(item.recipient is root for item in self._assignments):
            raise ForegroundDeliveryRefusal("positive_case_already_assigned")
        assignment = PositiveCaseAssignment(freeze, root, self._issuer)
        self._assignments.append(assignment)
        self._assignment_snapshots.append(
            (assignment, assignment.freeze, assignment.recipient, assignment._issuer)
        )
        return assignment

    def _require_assignment(self, assignment: object) -> PositiveCaseAssignment:
        snapshot = next(
            (
                item
                for item in self._assignment_snapshots
                if item[0] is assignment
            ),
            None,
        )
        if (
            type(assignment) is not PositiveCaseAssignment
            or snapshot is None
            or assignment.freeze is not snapshot[1]
            or assignment.recipient is not snapshot[2]
            or assignment._issuer is not snapshot[3]
        ):
            raise ForegroundDeliveryRefusal(
                "exact_positive_case_assignment_required"
            )
        self._require_freeze(assignment.freeze)
        if not any(
            assignment.recipient is root for root in assignment.freeze.authorized_roots
        ):
            raise ForegroundRecipientRefusal("unauthorized_foreground_recipient")
        return assignment

    def issue_delivery(
        self, assignment: object
    ) -> tuple[PositiveForegroundDelivery, RuntimeForegroundConsumer]:
        assignment = self._require_assignment(assignment)
        if any(item.recipient is assignment.recipient for item in self._deliveries):
            raise ForegroundDeliveryRefusal("foreground_delivery_already_issued")
        freeze = self._require_freeze(assignment.freeze)
        verifier = next(
            item for item in self._verifiers if item.root is assignment.recipient
        )
        delivery, consumer = _issue_positive_foreground_delivery(
            freeze.run_id,
            assignment.recipient,
            freeze.foreground,
            freeze,
            freeze.comparison_group,
            verifier,
            _CONSUMER_FACTORY_ISSUER,
        )
        self._deliveries.append(delivery)
        self._consumers.append(consumer)
        return delivery, consumer

    def witness(
        self,
        assignment: object,
        consumer: RuntimeForegroundConsumer,
        handoff: object,
    ) -> ReceivedForegroundWitness:
        if (
            type(consumer) is not RuntimeForegroundConsumer
            or not any(consumer is item for item in self._consumers)
        ):
            raise ForegroundDeliveryRefusal("exact_foreground_runtime_boundary_required")
        assignment = self._require_assignment(assignment)
        current = consumer.require_current(handoff)
        delivery = next(
            (
                item
                for item in self._deliveries
                if item is current.consumed_delivery
            ),
            None,
        )
        if (
            delivery is None
            or delivery._freeze is not assignment.freeze
            or delivery._comparison_group is not assignment.freeze.comparison_group
            or current.consumed_root is not assignment.recipient
            or current.foreground is not assignment.freeze.foreground
            or foreground_values(current.foreground)
            != foreground_values(assignment.freeze.foreground)
            or any(item.handoff is current for item in self._witnesses)
        ):
            raise ForegroundDeliveryRefusal("received_foreground_mismatch")
        validate_fixture_positive_foreground(current.foreground)
        witness = ReceivedForegroundWitness(
            assignment.freeze, assignment, current, self._issuer
        )
        self._witnesses.append(witness)
        self._witness_snapshots.append(
            (
                witness,
                witness.freeze,
                witness.case_assignment,
                witness.handoff,
                witness._issuer,
                consumer,
            )
        )
        return witness

    def require_witness(self, witness: object) -> ReceivedForegroundWitness:
        snapshot = next(
            (item for item in self._witness_snapshots if item[0] is witness), None
        )
        if (
            type(witness) is not ReceivedForegroundWitness
            or snapshot is None
            or witness.freeze is not snapshot[1]
            or witness.case_assignment is not snapshot[2]
            or witness.handoff is not snapshot[3]
            or witness._issuer is not snapshot[4]
        ):
            raise ForegroundDeliveryRefusal("exact_received_foreground_witness_required")
        assignment = self._require_assignment(witness.case_assignment)
        current = snapshot[5].require_current(witness.handoff)
        if (
            current.consumed_root is not assignment.recipient
            or current.consumed_delivery._freeze is not witness.freeze
            or current.consumed_delivery._comparison_group
            is not witness.freeze.comparison_group
            or current.foreground is not witness.freeze.foreground
        ):
            raise ForegroundDeliveryRefusal("received_foreground_mismatch")
        validate_fixture_positive_foreground(current.foreground)
        return witness

    def require_complete_witnesses(self) -> tuple[ReceivedForegroundWitness, ...]:
        if len(self._witnesses) != 3:
            raise ForegroundDeliveryRefusal("three_foreground_witnesses_required")
        current = tuple(self.require_witness(item) for item in self._witnesses)
        roots = tuple(item.case_assignment.recipient for item in current)
        if len({id(root) for root in roots}) != 3 or not all(
            any(root is expected for root in roots)
            for expected in self._require_roots()
        ):
            raise ForegroundDeliveryRefusal("foreground_witness_set_mismatch")
        return current
