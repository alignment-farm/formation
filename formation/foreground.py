"""Runtime-facing typed capabilities for the fixture positive foreground."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


_SOURCE_ISSUER = object()
_DELIVERY_ISSUER = object()
_CONSUMER_FACTORY_ISSUER = object()
_PROTOCOL_ISSUER = object()


class ForegroundSourceRefusal(ValueError):
    """The protocol foreground source is unavailable or changed."""


class ForegroundConsumptionRefusal(ValueError):
    """The root-bound foreground delivery cannot be consumed."""


@dataclass(frozen=True, slots=True)
class PositiveForeground:
    candidate_object: str
    derived_from: str
    artifact_revision: int
    authority_revision: int
    depends_on_current_authority: bool
    commit_action: str
    refresh_action: str


def foreground_values(value: PositiveForeground) -> tuple[object, ...]:
    if type(value) is not PositiveForeground:
        raise ForegroundSourceRefusal("exact_positive_foreground_required")
    return (
        value.candidate_object,
        value.derived_from,
        value.artifact_revision,
        value.authority_revision,
        value.depends_on_current_authority,
        value.commit_action,
        value.refresh_action,
    )


@dataclass(frozen=True, slots=True)
class FixturePositiveForegroundSource:
    run_id: str
    foreground: PositiveForeground
    _issuer: object


@dataclass(frozen=True, slots=True)
class FixturePositiveForegroundProtocol:
    foreground: PositiveForeground
    _issuer: object


_PROTOCOL_FOREGROUND = PositiveForeground(
    candidate_object="bundle-9",
    derived_from="registry-manifest",
    artifact_revision=7,
    authority_revision=8,
    depends_on_current_authority=True,
    commit_action="release",
    refresh_action="rebuild_then_release",
)
_FIXTURE_PROTOCOL = FixturePositiveForegroundProtocol(
    _PROTOCOL_FOREGROUND,
    _PROTOCOL_ISSUER,
)


def fixture_positive_foreground_protocol() -> FixturePositiveForegroundProtocol:
    return _FIXTURE_PROTOCOL


def adapt_positive_foreground_source(
    run_id: str, protocol: object
) -> FixturePositiveForegroundSource:
    if not isinstance(run_id, str) or not run_id:
        raise ForegroundSourceRefusal("invalid_foreground_run")
    if (
        type(protocol) is not FixturePositiveForegroundProtocol
        or protocol is not _FIXTURE_PROTOCOL
        or protocol._issuer is not _PROTOCOL_ISSUER
        or protocol.foreground is not _PROTOCOL_FOREGROUND
    ):
        raise ForegroundSourceRefusal("exact_fixture_foreground_protocol_required")
    value = protocol.foreground
    foreground_values(value)
    return FixturePositiveForegroundSource(run_id, value, _SOURCE_ISSUER)


@dataclass(frozen=True, slots=True)
class PositiveForegroundDelivery:
    run_id: str
    recipient: object
    foreground: PositiveForeground
    _freeze: object
    _comparison_group: object
    _use: _PositiveForegroundDeliveryUse
    _issuer: object


@dataclass(frozen=True, slots=True)
class ReceivedForegroundHandoff:
    run_id: str
    consumed_root: object
    consumed_delivery: PositiveForegroundDelivery
    foreground: PositiveForeground
    _issuer: object


class RecipientCurrentnessVerifier(Protocol):
    """A detached verifier for one exact developmental recipient root."""

    root: object

    def require(self, root: object) -> object: ...


class _PositiveForegroundDeliveryUse:
    """One issued delivery's detached provenance and linear-use registry."""

    def __init__(
        self,
        run_id: str,
        recipient: object,
        foreground: PositiveForeground,
        freeze: object,
        comparison_group: object,
        verifier: RecipientCurrentnessVerifier,
        issuer: object,
    ) -> None:
        if issuer is not _CONSUMER_FACTORY_ISSUER:
            raise ForegroundConsumptionRefusal("foreground_delivery_factory_required")
        if verifier.root is not recipient or verifier.require(recipient) is not recipient:
            raise ForegroundConsumptionRefusal("foreground_recipient_not_current")
        self._run_id = run_id
        self._recipient = recipient
        self._foreground = foreground
        self._foreground_values = foreground_values(foreground)
        self._freeze = freeze
        self._comparison_group = comparison_group
        self._freeze_snapshot = (
            freeze.run_id,
            freeze.comparison_group,
            freeze.source,
            freeze.foreground,
            freeze.authorized_roots,
            freeze._issuer,
        )
        self._group_snapshot = (
            comparison_group.run_id,
            comparison_group.baseline,
            comparison_group.governed,
            comparison_group.ablation,
            comparison_group._issuer,
        )
        self._verifier = verifier
        self._delivery: PositiveForegroundDelivery | None = None
        self._delivery_snapshot: tuple[object, ...] | None = None
        self._consumed = False

    def bind(self, delivery: PositiveForegroundDelivery) -> None:
        if self._delivery is not None:
            raise ForegroundConsumptionRefusal("foreground_delivery_already_bound")
        self._delivery = delivery
        self._delivery_snapshot = (
            delivery.run_id,
            delivery.recipient,
            delivery.foreground,
            delivery._freeze,
            delivery._comparison_group,
            delivery._use,
            delivery._issuer,
        )

    def require(
        self, delivery: object, recipient: object, *, consumed: bool | None = None
    ) -> PositiveForegroundDelivery:
        if (
            type(delivery) is not PositiveForegroundDelivery
            or delivery is not self._delivery
            or self._delivery_snapshot is None
            or delivery.run_id != self._run_id
            or delivery.run_id != self._delivery_snapshot[0]
            or delivery.recipient is not self._recipient
            or delivery.recipient is not self._delivery_snapshot[1]
            or delivery.recipient is not recipient
            or delivery.foreground is not self._foreground
            or delivery.foreground is not self._delivery_snapshot[2]
            or delivery._freeze is not self._freeze
            or delivery._freeze is not self._delivery_snapshot[3]
            or delivery._comparison_group is not self._comparison_group
            or delivery._comparison_group is not self._delivery_snapshot[4]
            or delivery._use is not self
            or delivery._use is not self._delivery_snapshot[5]
            or delivery._issuer is not _DELIVERY_ISSUER
            or delivery._issuer is not self._delivery_snapshot[6]
            or foreground_values(delivery.foreground) != self._foreground_values
            or (consumed is not None and self._consumed is not consumed)
        ):
            raise ForegroundConsumptionRefusal("positive_delivery_changed")
        freeze_snapshot = self._freeze_snapshot
        group_snapshot = self._group_snapshot
        if (
            self._freeze.run_id != freeze_snapshot[0]
            or self._freeze.comparison_group is not freeze_snapshot[1]
            or self._freeze.source is not freeze_snapshot[2]
            or self._freeze.foreground is not freeze_snapshot[3]
            or self._freeze.authorized_roots is not freeze_snapshot[4]
            or self._freeze._issuer is not freeze_snapshot[5]
            or self._freeze.comparison_group is not self._comparison_group
            or self._freeze.run_id != self._run_id
            or self._freeze.foreground is not self._foreground
            or not any(
                recipient is candidate
                for candidate in self._freeze.authorized_roots
            )
            or self._comparison_group.run_id != group_snapshot[0]
            or self._comparison_group.baseline is not group_snapshot[1]
            or self._comparison_group.governed is not group_snapshot[2]
            or self._comparison_group.ablation is not group_snapshot[3]
            or self._comparison_group._issuer is not group_snapshot[4]
        ):
            raise ForegroundConsumptionRefusal("positive_delivery_provenance_changed")
        if self._verifier.require(recipient) is not recipient:
            raise ForegroundConsumptionRefusal("foreground_recipient_not_current")
        return delivery

    def consume(self, delivery: object, recipient: object) -> PositiveForegroundDelivery:
        if self._consumed:
            raise ForegroundConsumptionRefusal("positive_delivery_already_consumed")
        current = self.require(delivery, recipient, consumed=False)
        self._consumed = True
        return current


class RuntimeForegroundConsumer:
    """One detached, root-bound linear consumption boundary."""

    def __init__(self, delivery: PositiveForegroundDelivery, issuer: object) -> None:
        if issuer is not _CONSUMER_FACTORY_ISSUER:
            raise ForegroundConsumptionRefusal("foreground_consumer_factory_required")
        if type(delivery) is not PositiveForegroundDelivery:
            raise ForegroundConsumptionRefusal("exact_positive_delivery_required")
        self._delivery = delivery
        self._snapshot = (
            delivery.run_id,
            delivery.recipient,
            delivery.foreground,
            delivery._freeze,
            delivery._comparison_group,
            delivery._use,
            foreground_values(delivery.foreground),
            delivery._issuer,
        )
        self._issuer = object()
        self._handoff: ReceivedForegroundHandoff | None = None
        self._handoff_snapshot: tuple[object, ...] | None = None
        self._encounter_authority: object | None = None
        self._encounter_permit = object()
        self._encounter_binding: object | None = None
        self._encounter_opened = False

    def _require_delivery(self, delivery: object) -> PositiveForegroundDelivery:
        if (
            type(delivery) is not PositiveForegroundDelivery
            or delivery is not self._delivery
        ):
            raise ForegroundConsumptionRefusal("exact_positive_delivery_required")
        snapshot = self._snapshot
        if (
            delivery.run_id != snapshot[0]
            or delivery.recipient is not snapshot[1]
            or delivery.foreground is not snapshot[2]
            or delivery._freeze is not snapshot[3]
            or delivery._comparison_group is not snapshot[4]
            or delivery._use is not snapshot[5]
            or foreground_values(delivery.foreground) != snapshot[6]
            or delivery._issuer is not snapshot[7]
        ):
            raise ForegroundConsumptionRefusal("positive_delivery_changed")
        delivery._use.require(delivery, delivery.recipient)
        return delivery

    def consume(self, delivery: object) -> ReceivedForegroundHandoff:
        if self._handoff is not None:
            raise ForegroundConsumptionRefusal("positive_delivery_already_consumed")
        current = self._require_delivery(delivery)
        current._use.consume(current, current.recipient)
        handoff = ReceivedForegroundHandoff(
            run_id=current.run_id,
            consumed_root=current.recipient,
            consumed_delivery=current,
            foreground=current.foreground,
            _issuer=self._issuer,
        )
        self._handoff = handoff
        self._handoff_snapshot = (
            handoff.run_id,
            handoff.consumed_root,
            handoff.consumed_delivery,
            handoff.foreground,
            foreground_values(handoff.foreground),
            handoff._issuer,
        )
        return handoff

    def require_current(self, handoff: object) -> ReceivedForegroundHandoff:
        self._require_delivery(self._delivery)
        if (
            type(handoff) is not ReceivedForegroundHandoff
            or handoff is not self._handoff
            or self._handoff_snapshot is None
        ):
            raise ForegroundConsumptionRefusal("exact_received_foreground_handoff_required")
        snapshot = self._handoff_snapshot
        if (
            handoff.run_id != snapshot[0]
            or handoff.consumed_root is not snapshot[1]
            or handoff.consumed_delivery is not snapshot[2]
            or handoff.foreground is not snapshot[3]
            or foreground_values(handoff.foreground) != snapshot[4]
            or handoff._issuer is not snapshot[5]
            or handoff.consumed_delivery is not self._delivery
            or self._delivery._use.require(
                self._delivery, handoff.consumed_root, consumed=True
            ) is not self._delivery
        ):
            raise ForegroundConsumptionRefusal("received_foreground_handoff_changed")
        return handoff

    def _claim_encounter_authority(self, authority: object, permit: object) -> None:
        self._require_encounter_unclaimed(permit)
        self._encounter_authority = authority

    def _require_encounter_unclaimed(self, permit: object) -> None:
        if permit is not self._encounter_permit:
            raise ForegroundConsumptionRefusal("encounter_authority_factory_required")
        if self._encounter_authority is not None:
            raise ForegroundConsumptionRefusal("encounter_authority_already_registered")

    def _register_encounter_binding(
        self,
        authority: object,
        handoff: object,
        binding: object,
        permit: object,
    ) -> None:
        if (
            permit is not self._encounter_permit
            or authority is not self._encounter_authority
        ):
            raise ForegroundConsumptionRefusal("exact_encounter_authority_required")
        self.require_current(handoff)
        if self._encounter_binding is not None:
            raise ForegroundConsumptionRefusal("encounter_opening_already_bound")
        self._encounter_binding = binding

    def _consume_encounter_binding(
        self,
        authority: object,
        handoff: object,
        binding: object,
        permit: object,
    ) -> None:
        if (
            permit is not self._encounter_permit
            or authority is not self._encounter_authority
            or binding is not self._encounter_binding
        ):
            raise ForegroundConsumptionRefusal("exact_encounter_opening_binding_required")
        self.require_current(handoff)
        if self._encounter_opened:
            raise ForegroundConsumptionRefusal("encounter_opening_already_consumed")
        self._encounter_opened = True


def _issue_positive_foreground_delivery(
    run_id: str,
    recipient: object,
    foreground: PositiveForeground,
    freeze: object,
    comparison_group: object,
    verifier: RecipientCurrentnessVerifier,
    issuer: object,
) -> tuple[PositiveForegroundDelivery, RuntimeForegroundConsumer]:
    """Factory used only by the registered trajectory foreground controller."""

    if issuer is not _CONSUMER_FACTORY_ISSUER:
        raise ForegroundConsumptionRefusal("foreground_delivery_factory_required")
    use = _PositiveForegroundDeliveryUse(
        run_id,
        recipient,
        foreground,
        freeze,
        comparison_group,
        verifier,
        _CONSUMER_FACTORY_ISSUER,
    )
    delivery = PositiveForegroundDelivery(
        run_id,
        recipient,
        foreground,
        freeze,
        comparison_group,
        use,
        _DELIVERY_ISSUER,
    )
    use.bind(delivery)
    return delivery, RuntimeForegroundConsumer(delivery, _CONSUMER_FACTORY_ISSUER)
