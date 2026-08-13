"""Harness-owned assignment, validation, witness, and append checks."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re

from formation.condition_append import (
    BASELINE_CONDITION,
    IDENTITY_CONTRACT,
    MATERIALIZER,
    SOURCE_HEAD,
    TREATMENT_CONDITION,
    ConditionHandoffRefusal,
    FrozenConditionAppendHandoff,
    PublicConditionDelivery,
    PublicFormationCondition,
    RuntimeConditionMaterializer,
    _adapt_condition_source,
    _issue_public_condition_delivery,
    baseline_condition,
    treatment_condition,
)
from trajectory.fixture_fork import ForkController, ForkRefusal, FrozenBranchRoot


ALGORITHM = "sha-256"
_COORDINATE_PATTERN = re.compile(r"D-X-[0-9]{6}\Z")
_LABELS = ("baseline", "governed", "ablation")
_ASSIGNMENT_COORDINATES = {
    "baseline": "T-B-001",
    "governed": "T-G-001",
    "ablation": "T-A-001",
}


def _contains_branch_word(value: str) -> bool:
    lowered = value.lower()
    return any(word in lowered for word in _LABELS) or re.search(
        r"(^|[^a-z0-9])[bga]([^a-z0-9]|$)", lowered
    ) is not None


class AssignmentRefusal(ValueError):
    """The hidden assignment cannot yield this public delivery."""


class ConditionValidationRefusal(ValueError):
    """The runtime bytes are not the exact fixture condition receipt."""


class ConditionAppendRefusal(ValueError):
    """The condition segment cannot become the branch-local root."""


class TreatmentRootBatchRefusal(ValueError):
    """The exact label-blind treatment root batch is unavailable."""


@dataclass(frozen=True)
class BranchAssignment:
    coordinate: str
    label: str
    root: FrozenBranchRoot
    _issuer: object


@dataclass(frozen=True)
class ConditionBinding:
    materializer: str
    identity_contract: str
    algorithm: str
    digest: str
    byte_length: int

    def require_valid(self) -> None:
        if type(self) is not ConditionBinding:
            raise ConditionAppendRefusal("complete_condition_binding_required")
        if self.materializer != MATERIALIZER:
            raise ConditionAppendRefusal("unknown_condition_materializer")
        if self.identity_contract != IDENTITY_CONTRACT:
            raise ConditionAppendRefusal("unknown_condition_identity_contract")
        if self.algorithm != ALGORITHM:
            raise ConditionAppendRefusal("unknown_condition_digest_algorithm")
        if (
            not isinstance(self.digest, str)
            or len(self.digest) != 64
            or self.digest != self.digest.lower()
            or any(character not in "0123456789abcdef" for character in self.digest)
        ):
            raise ConditionAppendRefusal("invalid_condition_digest")
        if not isinstance(self.byte_length, int) or isinstance(self.byte_length, bool):
            raise ConditionAppendRefusal("invalid_condition_byte_length")
        if self.byte_length < 0:
            raise ConditionAppendRefusal("invalid_condition_byte_length")


@dataclass(frozen=True)
class ConditionWitness:
    assignment_coordinate: str
    prefix_witness_coordinate: str
    handoff_id: str
    run_id: str
    head_after: str
    binding: ConditionBinding
    _issuer: object


@dataclass(frozen=True)
class BranchLocalRoot:
    prefix_root: FrozenBranchRoot
    condition_segment: bytes
    head: str
    condition_binding: ConditionBinding
    _issuer: object


class _TreatmentRootBatchUse:
    def __init__(self, controller: ConditionAppendController) -> None:
        self._controller = controller
        self._batch: TreatmentRootBatch | None = None
        self.used = False

    def bind(self, batch: TreatmentRootBatch) -> None:
        if self._batch is not None:
            raise TreatmentRootBatchRefusal("treatment_root_batch_already_bound")
        self._batch = batch

    def consume(self, batch: object) -> tuple[BranchLocalRoot, BranchLocalRoot]:
        if self.used:
            raise TreatmentRootBatchRefusal("treatment_root_batch_already_consumed")
        current = self._controller.require_treatment_root_batch(batch)
        if current is not self._batch:
            raise TreatmentRootBatchRefusal("exact_treatment_root_batch_required")
        self.used = True
        return current.roots


@dataclass(frozen=True)
class TreatmentRootBatch:
    """Exact two-root public-treatment set in label-blind issuance order."""

    run_id: str
    roots: tuple[BranchLocalRoot, BranchLocalRoot]
    _use: _TreatmentRootBatchUse
    _issuer: object


def _condition_for_label(label: str) -> PublicFormationCondition:
    if label == "baseline":
        return baseline_condition()
    if label in ("governed", "ablation"):
        return treatment_condition()
    raise AssignmentRefusal("unknown_fixture_branch_label")


def _expected_condition_artifact(
    coordinate: str, condition: PublicFormationCondition
) -> bytes:
    if not isinstance(coordinate, str) or not _COORDINATE_PATTERN.fullmatch(coordinate):
        raise ConditionValidationRefusal("invalid_fixture_condition_bytes")
    if condition.condition == BASELINE_CONDITION and condition == baseline_condition():
        payload = (
            b'{"condition":"audit_lineage_only-v0","interpreter":null,'
            b'"governor":null,"influence_policy":"declared-role-match-v0"}'
        )
    elif condition.condition == TREATMENT_CONDITION and condition == treatment_condition():
        payload = (
            b'{"condition":"consequence_governance_activation-v0",'
            b'"interpreter":"revision-check-candidate-v0",'
            b'"governor":"consequence-warrant-v0",'
            b'"influence_policy":"declared-role-match-v0"}'
        )
    else:
        raise ConditionValidationRefusal("invalid_fixture_condition_bytes")
    return (
        b'{"contract":"fixture-v0","coordinate":"'
        + coordinate.encode("ascii")
        + b'","record":"developmental","order":7,'
        + b'"event":"formation_condition_bound","authority":"formation_runtime",'
        + b'"parents":["D-C-006"],"retention":"inline","payload":'
        + payload
        + b"}\n"
    )


def validate_fixture_condition(
    artifact: object, coordinate: str, condition: PublicFormationCondition
) -> str:
    if type(artifact) is not bytes:
        raise ConditionValidationRefusal("invalid_fixture_condition_bytes")
    try:
        expected = _expected_condition_artifact(coordinate, condition)
    except (UnicodeError, ConditionValidationRefusal) as error:
        raise ConditionValidationRefusal("invalid_fixture_condition_bytes") from error
    if artifact != expected:
        raise ConditionValidationRefusal("invalid_fixture_condition_bytes")
    return "valid_fixture_condition_bytes"


def compute_condition_binding(artifact: bytes) -> ConditionBinding:
    return ConditionBinding(
        materializer=MATERIALIZER,
        identity_contract=IDENTITY_CONTRACT,
        algorithm=ALGORITHM,
        digest=hashlib.sha256(artifact).hexdigest(),
        byte_length=len(artifact),
    )


class ConditionAppendController:
    """Harness controller that never authors developmental bytes."""

    def __init__(self, forks: ForkController) -> None:
        self._forks = forks
        self._issuer = object()
        self._root_issuer = object()
        self._assignments: list[BranchAssignment] = []
        self._deliveries: list[PublicConditionDelivery] = []
        self._assignment_snapshots: list[tuple[object, ...]] = []
        self._delivered_assignments: list[BranchAssignment] = []
        self._witnesses: list[ConditionWitness] = []
        self._witness_snapshots: list[tuple[object, ...]] = []
        self._witnessed_handoffs: list[FrozenConditionAppendHandoff] = []
        self._witnessed_assignments: list[BranchAssignment] = []
        self._roots: list[BranchLocalRoot] = []
        self._witnessed_coordinates: list[str] = []
        self._root_snapshots: list[tuple[object, ...]] = []
        self._root_conditions: list[tuple[BranchLocalRoot, str]] = []
        self._treatment_batch_issuer = object()
        self._treatment_batch: TreatmentRootBatch | None = None
        self._treatment_batch_snapshot: tuple[object, ...] | None = None
        self._formation_controller: object | None = None
        self._forks.register_assignment_controller(self._issuer)

    def assign(
        self, root: object, label: str
    ) -> tuple[BranchAssignment, PublicConditionDelivery]:
        current = self._forks.require_issued_root(root)
        if label not in _LABELS:
            raise AssignmentRefusal("unknown_fixture_branch_label")
        if _contains_branch_word(current.run_id):
            raise AssignmentRefusal("label_bearing_run_id")
        try:
            self._forks.reserve_assignment(current, label, self._issuer)
        except ForkRefusal as error:
            raise AssignmentRefusal(str(error)) from error
        assignment = BranchAssignment(
            coordinate=_ASSIGNMENT_COORDINATES[label],
            label=label,
            root=current,
            _issuer=self._issuer,
        )
        delivery = _issue_public_condition_delivery(current, _condition_for_label(label))
        self._assignments.append(assignment)
        self._deliveries.append(delivery)
        self._assignment_snapshots.append(
            (
                assignment,
                assignment.coordinate,
                assignment.label,
                assignment.root,
                assignment._issuer,
                delivery,
                delivery.root,
                PublicFormationCondition(
                    delivery.condition.condition,
                    delivery.condition.interpreter,
                    delivery.condition.governor,
                    delivery.condition.influence_policy,
                ),
                delivery._issuer,
            )
        )
        return assignment, delivery

    def _require_assignment_delivery(
        self,
        assignment: object,
        delivery: object,
    ) -> tuple[BranchAssignment, PublicConditionDelivery]:
        if type(assignment) is not BranchAssignment or not any(
            assignment is item for item in self._assignments
        ):
            raise AssignmentRefusal("exact_assignment_required")
        if type(delivery) is not PublicConditionDelivery or not any(
            delivery is item for item in self._deliveries
        ):
            raise AssignmentRefusal("exact_public_delivery_required")
        snapshot = next(
            (
                item
                for item in self._assignment_snapshots
                if item[0] is assignment and item[5] is delivery
            ),
            None,
        )
        if snapshot is None:
            raise AssignmentRefusal("assignment_delivery_pair_mismatch")
        if (
            assignment.coordinate != snapshot[1]
            or assignment.label != snapshot[2]
            or assignment.root is not snapshot[3]
            or assignment._issuer is not snapshot[4]
            or delivery.root is not snapshot[6]
            or delivery.condition != snapshot[7]
            or delivery._issuer is not snapshot[8]
        ):
            raise AssignmentRefusal("assignment_or_delivery_changed")
        if assignment.coordinate != _ASSIGNMENT_COORDINATES[assignment.label]:
            raise AssignmentRefusal("assignment_coordinate_mismatch")
        return assignment, delivery

    def deliver(
        self,
        root: object,
        assignment: object,
        delivery: object,
    ):
        current = self._forks.require_issued_root(root)
        assignment, delivery = self._require_assignment_delivery(assignment, delivery)
        if any(assignment is item for item in self._delivered_assignments):
            raise AssignmentRefusal("assignment_already_delivered")
        if assignment.root is not current or delivery.root is not current:
            raise AssignmentRefusal("assignment_or_delivery_root_mismatch")
        if delivery.condition != _condition_for_label(assignment.label):
            raise AssignmentRefusal("assignment_condition_mismatch")
        self._forks.consume_root(current)
        self._delivered_assignments.append(assignment)
        return _adapt_condition_source(current.run_id, current, delivery)

    def witness(
        self,
        runtime: RuntimeConditionMaterializer,
        handoff: object,
        assignment: object,
        delivery: object,
    ) -> ConditionWitness:
        current = runtime.require_current(handoff)
        assignment, delivery = self._require_assignment_delivery(assignment, delivery)
        if not any(assignment is item for item in self._delivered_assignments):
            raise AssignmentRefusal("public_condition_not_delivered")
        if any(current is item for item in self._witnessed_handoffs):
            raise ConditionAppendRefusal("condition_handoff_already_witnessed")
        if any(assignment is item for item in self._witnessed_assignments):
            raise ConditionAppendRefusal("assignment_already_witnessed")
        if current.consumed_root is not assignment.root or delivery.root is not assignment.root:
            raise ConditionAppendRefusal("condition_handoff_root_mismatch")
        if current.condition != delivery.condition.condition:
            raise ConditionAppendRefusal("condition_handoff_delivery_mismatch")
        if current.head_after in self._witnessed_coordinates:
            raise ConditionAppendRefusal("condition_coordinate_collision")
        validate_fixture_condition(
            current.artifact, current.head_after, delivery.condition
        )
        binding = compute_condition_binding(current.artifact)
        binding.require_valid()
        witness = ConditionWitness(
            assignment_coordinate=assignment.coordinate,
            prefix_witness_coordinate=assignment.root.witness_coordinate,
            handoff_id=current.handoff_id,
            run_id=current.run_id,
            head_after=current.head_after,
            binding=binding,
            _issuer=self._issuer,
        )
        self._witnesses.append(witness)
        self._witness_snapshots.append(
            (
                witness,
                witness.assignment_coordinate,
                witness.prefix_witness_coordinate,
                witness.handoff_id,
                witness.run_id,
                witness.head_after,
                ConditionBinding(
                    witness.binding.materializer,
                    witness.binding.identity_contract,
                    witness.binding.algorithm,
                    witness.binding.digest,
                    witness.binding.byte_length,
                ),
                witness._issuer,
            )
        )
        self._witnessed_handoffs.append(current)
        self._witnessed_assignments.append(assignment)
        self._witnessed_coordinates.append(current.head_after)
        return witness

    def append(
        self,
        runtime: RuntimeConditionMaterializer,
        handoff: object,
        witness: object,
        root: object,
    ) -> BranchLocalRoot:
        try:
            current = runtime.require_current(handoff)
        except ConditionHandoffRefusal as error:
            if str(error) == "condition_handoff_changed":
                raise ConditionAppendRefusal("condition_binding_mismatch") from error
            raise
        prefix_root = self._forks.require_issued_root(root)
        if type(witness) is not ConditionWitness or not any(
            witness is item for item in self._witnesses
        ):
            raise ConditionAppendRefusal("exact_condition_witness_required")
        snapshot = next(
            (item for item in self._witness_snapshots if item[0] is witness), None
        )
        if snapshot is None:
            raise ConditionAppendRefusal("exact_condition_witness_required")
        if (
            witness.assignment_coordinate != snapshot[1]
            or witness.prefix_witness_coordinate != snapshot[2]
            or witness.handoff_id != snapshot[3]
            or witness.run_id != snapshot[4]
            or witness.head_after != snapshot[5]
            or witness.binding != snapshot[6]
            or witness._issuer is not snapshot[7]
        ):
            raise ConditionAppendRefusal("condition_witness_changed")
        witness.binding.require_valid()
        if (
            current.consumed_root is not prefix_root
            or witness.handoff_id != current.handoff_id
            or witness.run_id != current.run_id
            or witness.head_after != current.head_after
        ):
            raise ConditionAppendRefusal("condition_witness_handoff_mismatch")
        if compute_condition_binding(current.artifact) != witness.binding:
            raise ConditionAppendRefusal("condition_binding_mismatch")
        if any(local.prefix_root is prefix_root for local in self._roots):
            raise ConditionAppendRefusal("condition_root_already_returned")
        local_root = BranchLocalRoot(
            prefix_root=prefix_root,
            condition_segment=current.artifact,
            head=current.head_after,
            condition_binding=witness.binding,
            _issuer=self._root_issuer,
        )
        self._roots.append(local_root)
        self._root_conditions.append((local_root, current.condition))
        self._root_snapshots.append(
            (
                local_root,
                local_root.prefix_root,
                local_root.condition_segment,
                local_root.head,
                ConditionBinding(
                    local_root.condition_binding.materializer,
                    local_root.condition_binding.identity_contract,
                    local_root.condition_binding.algorithm,
                    local_root.condition_binding.digest,
                    local_root.condition_binding.byte_length,
                ),
                local_root._issuer,
            )
        )
        return local_root

    def require_returned_root(self, root: object) -> BranchLocalRoot:
        if type(root) is not BranchLocalRoot:
            raise ConditionAppendRefusal("exact_branch_local_root_required")
        snapshot = next(
            (item for item in self._root_snapshots if item[0] is root), None
        )
        if snapshot is None or root._issuer is not self._root_issuer:
            raise ConditionAppendRefusal("exact_branch_local_root_required")
        if (
            root.prefix_root is not snapshot[1]
            or root.condition_segment is not snapshot[2]
            or root.head != snapshot[3]
            or root.condition_binding != snapshot[4]
            or root._issuer is not snapshot[5]
        ):
            raise ConditionAppendRefusal("branch_local_root_changed")
        self._forks.require_issued_root(root.prefix_root)
        return root

    def issue_treatment_root_batch(self) -> TreatmentRootBatch:
        if self._treatment_batch is not None:
            raise TreatmentRootBatchRefusal("treatment_root_batch_already_issued")
        if len(self._roots) != 3 or len(self._root_conditions) != 3:
            raise TreatmentRootBatchRefusal("all_condition_roots_required")
        try:
            prefix_roots = self._forks.require_roots_in_issuance_order(self._issuer)
        except ForkRefusal as error:
            raise TreatmentRootBatchRefusal(str(error)) from error
        local_by_prefix = {id(root.prefix_root): root for root in self._roots}
        if len(local_by_prefix) != 3:
            raise TreatmentRootBatchRefusal("three_distinct_condition_roots_required")
        ordered = tuple(local_by_prefix.get(id(prefix)) for prefix in prefix_roots)
        if any(root is None for root in ordered):
            raise TreatmentRootBatchRefusal("condition_root_set_mismatch")
        condition_by_root = {id(root): condition for root, condition in self._root_conditions}
        treatment = tuple(
            root
            for root in ordered
            if root is not None and condition_by_root.get(id(root)) == TREATMENT_CONDITION
        )
        if len(treatment) != 2 or treatment[0] is treatment[1]:
            raise TreatmentRootBatchRefusal("exact_two_treatment_roots_required")
        first = self.require_returned_root(treatment[0])
        second = self.require_returned_root(treatment[1])
        if first.prefix_root.run_id != second.prefix_root.run_id:
            raise TreatmentRootBatchRefusal("treatment_root_run_mismatch")
        use = _TreatmentRootBatchUse(self)
        batch = TreatmentRootBatch(
            run_id=first.prefix_root.run_id,
            roots=(first, second),
            _use=use,
            _issuer=self._treatment_batch_issuer,
        )
        use.bind(batch)
        self._treatment_batch = batch
        self._treatment_batch_snapshot = (
            batch.run_id,
            batch.roots,
            batch._use,
            batch._issuer,
        )
        return batch

    def require_treatment_root_batch(self, batch: object) -> TreatmentRootBatch:
        if (
            type(batch) is not TreatmentRootBatch
            or batch is not self._treatment_batch
            or batch._issuer is not self._treatment_batch_issuer
            or self._treatment_batch_snapshot is None
        ):
            raise TreatmentRootBatchRefusal("exact_treatment_root_batch_required")
        snapshot = self._treatment_batch_snapshot
        if (
            batch.run_id != snapshot[0]
            or batch.roots is not snapshot[1]
            or batch._use is not snapshot[2]
            or batch._issuer is not snapshot[3]
        ):
            raise TreatmentRootBatchRefusal("treatment_root_batch_changed")
        if len(batch.roots) != 2 or batch.roots[0] is batch.roots[1]:
            raise TreatmentRootBatchRefusal("exact_two_treatment_roots_required")
        for root in batch.roots:
            self.require_returned_root(root)
            condition = next(
                (value for item, value in self._root_conditions if item is root), None
            )
            if condition != TREATMENT_CONDITION:
                raise TreatmentRootBatchRefusal("non_treatment_root_in_batch")
        return batch

    def register_formation_controller(
        self, batch: object, controller: object
    ) -> TreatmentRootBatch:
        current = self.require_treatment_root_batch(batch)
        if self._formation_controller is not None:
            raise TreatmentRootBatchRefusal("formation_controller_already_registered")
        self._formation_controller = controller
        return current

    def assignment_label_for_formation(
        self, root: object, formation_controller: object
    ) -> str:
        """Resolve a retained harness assignment without exposing it to runtime."""

        if formation_controller is not self._formation_controller:
            raise AssignmentRefusal("exact_formation_controller_required")
        current = self.require_returned_root(root)
        matching = tuple(
            assignment
            for assignment in self._assignments
            if assignment.root is current.prefix_root
        )
        if len(matching) != 1:
            raise AssignmentRefusal("exact_retained_assignment_required")
        assignment = matching[0]
        snapshot = next(
            (
                item
                for item in self._assignment_snapshots
                if item[0] is assignment
            ),
            None,
        )
        if snapshot is None:
            raise AssignmentRefusal("exact_retained_assignment_required")
        self._require_assignment_delivery(assignment, snapshot[5])
        return assignment.label
