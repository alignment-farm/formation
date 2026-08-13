"""Runtime-owned producer for the fixture's formation-condition receipt.

This module emits only the first branch-local receipt after ``D-C-006``. It is
not a general developmental recorder or event schema.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import re


MATERIALIZER = "fixture-v0-condition-jsonl-v0"
IDENTITY_CONTRACT = "fixture-v0-condition-identity-v0"
SOURCE_HEAD = "D-C-006"

BASELINE_CONDITION = "audit_lineage_only-v0"
TREATMENT_CONDITION = "consequence_governance_activation-v0"
INTERPRETER = "revision-check-candidate-v0"
GOVERNOR = "consequence-warrant-v0"
INFLUENCE_POLICY = "declared-role-match-v0"

_COORDINATE_PATTERN = re.compile(r"D-X-[0-9]{6}\Z")
_DELIVERY_ISSUER = object()
_SOURCE_ISSUER = object()
_ISSUED_DELIVERIES: list[object] = []
_ADAPTED_DELIVERIES: list[object] = []
_ISSUED_SOURCES: list[tuple[object, object]] = []


def _contains_hidden_branch_label(value: str) -> bool:
    lowered = value.lower()
    return any(
        word in lowered for word in ("baseline", "governed", "ablation")
    ) or re.search(r"(^|[^a-z0-9])[bga]([^a-z0-9]|$)", lowered) is not None


class ConditionSourceRefusal(ValueError):
    """The delivered condition cannot become a runtime receipt source."""


class ConditionHandoffRefusal(ValueError):
    """The runtime condition handoff is not exact and current."""


class CoordinateRefusal(ValueError):
    """The runtime cannot issue a unique fixture event coordinate."""


@dataclass(frozen=True)
class PublicFormationCondition:
    condition: str
    interpreter: str | None
    governor: str | None
    influence_policy: str

    def require_valid(self) -> None:
        if type(self) is not PublicFormationCondition:
            raise ConditionSourceRefusal("exact_public_condition_required")
        if self == baseline_condition():
            return
        if self == treatment_condition():
            return
        raise ConditionSourceRefusal("unknown_public_condition")


def baseline_condition() -> PublicFormationCondition:
    return PublicFormationCondition(
        condition=BASELINE_CONDITION,
        interpreter=None,
        governor=None,
        influence_policy=INFLUENCE_POLICY,
    )


def treatment_condition() -> PublicFormationCondition:
    return PublicFormationCondition(
        condition=TREATMENT_CONDITION,
        interpreter=INTERPRETER,
        governor=GOVERNOR,
        influence_policy=INFLUENCE_POLICY,
    )


@dataclass(frozen=True)
class PublicConditionDelivery:
    """Label-free public configuration bound to one exact fork root."""

    root: object
    condition: PublicFormationCondition
    _issuer: object


def _issue_public_condition_delivery(
    root: object, condition: PublicFormationCondition
) -> PublicConditionDelivery:
    condition.require_valid()
    delivery = PublicConditionDelivery(root, condition, _DELIVERY_ISSUER)
    _ISSUED_DELIVERIES.append(delivery)
    return delivery


class _ConditionSourceUse:
    def __init__(
        self,
        run_id: str,
        root: object,
        condition: PublicFormationCondition,
        delivery: PublicConditionDelivery,
    ) -> None:
        self.used = False
        self.run_id = run_id
        self.root = root
        self.root_run_id = getattr(root, "run_id", None)
        self.root_source_head = getattr(root, "source_head", None)
        self.root_artifact = getattr(root, "artifact", None)
        self.condition = PublicFormationCondition(
            condition.condition,
            condition.interpreter,
            condition.governor,
            condition.influence_policy,
        )
        self.delivery = delivery

    def consume(self, source: ConditionReceiptSource) -> None:
        if self.used:
            raise ConditionSourceRefusal("condition_source_already_consumed")
        if (
            source.run_id != self.run_id
            or source.source_head != SOURCE_HEAD
            or source.root is not self.root
            or getattr(source.root, "run_id", None) != self.root_run_id
            or getattr(source.root, "source_head", None) != self.root_source_head
            or getattr(source.root, "artifact", None) is not self.root_artifact
            or source.condition != self.condition
            or source.delivery is not self.delivery
        ):
            raise ConditionSourceRefusal("condition_source_changed")
        self.used = True


@dataclass(frozen=True)
class ConditionReceiptSource:
    run_id: str
    source_head: str
    root: object
    condition: PublicFormationCondition
    delivery: PublicConditionDelivery
    _use: _ConditionSourceUse
    _issuer: object


def _adapt_condition_source(
    run_id: str,
    root: object,
    delivery: PublicConditionDelivery,
) -> ConditionReceiptSource:
    if not isinstance(run_id, str) or not run_id:
        raise ConditionSourceRefusal("invalid_run_id")
    if type(delivery) is not PublicConditionDelivery:
        raise ConditionSourceRefusal("exact_public_delivery_required")
    if delivery._issuer is not _DELIVERY_ISSUER:
        raise ConditionSourceRefusal("forged_public_delivery")
    if not any(delivery is item for item in _ISSUED_DELIVERIES):
        raise ConditionSourceRefusal("exact_issued_delivery_required")
    if any(delivery is item for item in _ADAPTED_DELIVERIES):
        raise ConditionSourceRefusal("public_delivery_already_consumed")
    if delivery.root is not root:
        raise ConditionSourceRefusal("delivery_root_mismatch")
    delivery.condition.require_valid()
    condition = PublicFormationCondition(
        delivery.condition.condition,
        delivery.condition.interpreter,
        delivery.condition.governor,
        delivery.condition.influence_policy,
    )
    source = ConditionReceiptSource(
        run_id=run_id,
        source_head=SOURCE_HEAD,
        root=root,
        condition=condition,
        delivery=delivery,
        _use=_ConditionSourceUse(run_id, root, condition, delivery),
        _issuer=_SOURCE_ISSUER,
    )
    _ADAPTED_DELIVERIES.append(delivery)
    _ISSUED_SOURCES.append((source, source._use))
    return source


class _RuntimeConditionCoordinateAllocator:
    """Private label-blind allocator used only while a runtime run is created."""

    def __init__(self) -> None:
        self._next = 1
        self._issued: list[str] = []

    def issue(self) -> str:
        if self._next > 999999:
            raise CoordinateRefusal("coordinate_space_exhausted")
        coordinate = f"D-X-{self._next:06d}"
        self._next += 1
        if coordinate in self._issued or not _COORDINATE_PATTERN.fullmatch(coordinate):
            raise CoordinateRefusal("coordinate_collision_or_invalid")
        self._issued.append(coordinate)
        return coordinate


_RUNTIME_RUN_ISSUER = object()


class RuntimeConditionRun:
    """Runtime-owned coordinate reservation for the three unlabeled roots."""

    def __init__(self, run_id: str, fork_boundary: object) -> None:
        if not isinstance(run_id, str) or not run_id:
            raise ConditionSourceRefusal("invalid_run_id")
        if _contains_hidden_branch_label(run_id):
            raise ConditionSourceRefusal("label_bearing_run_id")
        from trajectory.fixture_fork import ForkController

        if type(fork_boundary) is not ForkController:
            raise CoordinateRefusal("exact_fork_boundary_required")
        claim_roots = getattr(fork_boundary, "claim_runtime_roots", None)
        if not callable(claim_roots):
            raise CoordinateRefusal("exact_fork_boundary_required")
        roots = claim_roots()
        if len(roots) != 3 or len({id(root) for root in roots}) != 3:
            raise CoordinateRefusal("three_distinct_roots_required")
        if any(
            getattr(root, "run_id", None) != run_id
            or getattr(root, "source_head", None) != SOURCE_HEAD
            for root in roots
        ):
            raise CoordinateRefusal("runtime_root_run_or_head_mismatch")
        allocator = _RuntimeConditionCoordinateAllocator()
        self.run_id = run_id
        self._issuer = _RUNTIME_RUN_ISSUER
        self._coordinates = [(root, allocator.issue()) for root in roots]
        self._opened_roots: list[object] = []

    def materializer(self, root: object) -> RuntimeConditionMaterializer:
        entry = next((item for item in self._coordinates if item[0] is root), None)
        if entry is None:
            raise CoordinateRefusal("exact_runtime_root_required")
        if any(root is opened for opened in self._opened_roots):
            raise CoordinateRefusal("runtime_root_materializer_already_opened")
        self._opened_roots.append(root)
        return RuntimeConditionMaterializer(self, root, entry[1], self._issuer)


@dataclass(frozen=True)
class FrozenConditionAppendHandoff:
    handoff_id: str
    run_id: str
    consumed_root: object
    source_head: str
    head_after: str
    materializer: str
    condition: str
    artifact: bytes
    _issuer: object


class RuntimeConditionMaterializer:
    """One-shot runtime owner of one fixture condition append."""

    def __init__(
        self,
        run: RuntimeConditionRun,
        root: object,
        coordinate: str,
        issuer: object,
    ) -> None:
        if type(run) is not RuntimeConditionRun or issuer is not _RUNTIME_RUN_ISSUER:
            raise CoordinateRefusal("runtime_run_factory_required")
        if not _COORDINATE_PATTERN.fullmatch(coordinate):
            raise CoordinateRefusal("invalid_reserved_coordinate")
        self.run_id = run.run_id
        self._root = root
        self._coordinate = coordinate
        self._reserved_root = root
        self._reserved_coordinate = coordinate
        self._issuer = object()
        self._current: FrozenConditionAppendHandoff | None = None
        self._snapshot: tuple[object, ...] | None = None
        self._closed = False

    def materialize(self, source: object) -> FrozenConditionAppendHandoff:
        if self._closed or self._current is not None:
            raise ConditionHandoffRefusal("condition_handoff_already_issued_or_closed")
        if type(source) is not ConditionReceiptSource:
            raise ConditionSourceRefusal("exact_condition_source_required")
        source_entry = next(
            (item for item in _ISSUED_SOURCES if item[0] is source), None
        )
        if source_entry is None or source._use is not source_entry[1]:
            raise ConditionSourceRefusal("exact_condition_source_required")
        if source._issuer is not _SOURCE_ISSUER:
            raise ConditionSourceRefusal("forged_condition_source")
        if source.run_id != self.run_id or source.source_head != SOURCE_HEAD:
            raise ConditionSourceRefusal("condition_source_run_or_head_mismatch")
        if source.delivery.root is not source.root:
            raise ConditionSourceRefusal("condition_source_root_mismatch")
        if source.delivery.condition != source.condition:
            raise ConditionSourceRefusal("condition_source_delivery_changed")
        if (
            self._root is not self._reserved_root
            or self._coordinate != self._reserved_coordinate
        ):
            raise CoordinateRefusal("runtime_coordinate_reservation_changed")
        if source.root is not self._root:
            raise ConditionSourceRefusal("condition_source_runtime_root_mismatch")
        source.condition.require_valid()
        source._use.consume(source)

        coordinate = self._coordinate
        artifact = self._encode(coordinate, source.condition)
        handoff = FrozenConditionAppendHandoff(
            handoff_id=f"{self.run_id}:fixture-condition:{coordinate}",
            run_id=self.run_id,
            consumed_root=source.root,
            source_head=SOURCE_HEAD,
            head_after=coordinate,
            materializer=MATERIALIZER,
            condition=source.condition.condition,
            artifact=artifact,
            _issuer=self._issuer,
        )
        self._current = handoff
        self._snapshot = (
            handoff.handoff_id,
            handoff.run_id,
            handoff.consumed_root,
            handoff.source_head,
            handoff.head_after,
            handoff.materializer,
            handoff.condition,
            handoff.artifact,
            handoff._issuer,
        )
        return handoff

    @staticmethod
    def _encode(coordinate: str, condition: PublicFormationCondition) -> bytes:
        receipt = {
            "contract": "fixture-v0",
            "coordinate": coordinate,
            "record": "developmental",
            "order": 7,
            "event": "formation_condition_bound",
            "authority": "formation_runtime",
            "parents": [SOURCE_HEAD],
            "retention": "inline",
            "payload": {
                "condition": condition.condition,
                "interpreter": condition.interpreter,
                "governor": condition.governor,
                "influence_policy": condition.influence_policy,
            },
        }
        return json.dumps(receipt, ensure_ascii=True, separators=(",", ":")).encode(
            "ascii"
        ) + b"\n"

    def require_current(self, handoff: object) -> FrozenConditionAppendHandoff:
        if type(handoff) is not FrozenConditionAppendHandoff:
            raise ConditionHandoffRefusal("exact_condition_handoff_required")
        if self._closed or self._current is not handoff:
            raise ConditionHandoffRefusal("stale_or_forged_condition_handoff")
        if handoff._issuer is not self._issuer:
            raise ConditionHandoffRefusal("forged_condition_handoff")
        if self._snapshot is None:
            raise ConditionHandoffRefusal("missing_condition_handoff_snapshot")
        if (
            handoff.run_id != self.run_id
            or handoff.source_head != SOURCE_HEAD
            or handoff.materializer != MATERIALIZER
        ):
            raise ConditionHandoffRefusal("condition_handoff_metadata_mismatch")
        if (
            handoff.handoff_id != self._snapshot[0]
            or handoff.run_id != self._snapshot[1]
            or handoff.consumed_root is not self._snapshot[2]
            or handoff.source_head != self._snapshot[3]
            or handoff.head_after != self._snapshot[4]
            or handoff.materializer != self._snapshot[5]
            or handoff.condition != self._snapshot[6]
            or handoff.artifact is not self._snapshot[7]
            or handoff._issuer is not self._snapshot[8]
        ):
            raise ConditionHandoffRefusal("condition_handoff_changed")
        return handoff

    def close(self) -> None:
        self._closed = True
