"""Runtime-owned typed append for the fixture positive encounter."""

from __future__ import annotations

from dataclasses import dataclass

from formation.foreground import (
    PositiveForeground,
    ReceivedForegroundHandoff,
    RecipientCurrentnessVerifier,
    RuntimeForegroundConsumer,
    foreground_values,
)


_BINDING_ISSUER = object()
_ENCOUNTER_ISSUER = object()
_APPEND_ISSUER = object()
_ROOT_ISSUER = object()


class EncounterOpeningRefusal(ValueError):
    """The positive encounter cannot be opened from this capability chain."""


@dataclass(frozen=True, slots=True)
class EncounterOpeningBinding:
    """Sealed lineage-safe identity for one privately retained handoff."""

    run_id: str
    token: object
    _issuer: object


@dataclass(frozen=True, slots=True)
class PositiveEncounter:
    run_id: str
    token: object
    _issuer: object


@dataclass(frozen=True, slots=True)
class EncounterOpenedAppend:
    run_id: str
    predecessor: object
    opening_binding: EncounterOpeningBinding
    encounter: PositiveEncounter
    situation: PositiveForeground
    _issuer: object


@dataclass(frozen=True, slots=True)
class EncounterBranchRoot:
    run_id: str
    predecessor: object
    opening_binding: EncounterOpeningBinding
    encounter: PositiveEncounter
    append: EncounterOpenedAppend
    situation: PositiveForeground
    _issuer: object


class _OpeningUse:
    """Private handoff registry entry; never retained by developmental lineage."""

    def __init__(
        self,
        consumer: RuntimeForegroundConsumer,
        handoff: ReceivedForegroundHandoff,
        verifier: RecipientCurrentnessVerifier,
        binding: EncounterOpeningBinding,
    ) -> None:
        current = consumer.require_current(handoff)
        predecessor = verifier.require(current.consumed_root)
        if predecessor is not current.consumed_root:
            raise EncounterOpeningRefusal("encounter_predecessor_not_current")
        self.consumer = consumer
        self.handoff = current
        self.verifier = verifier
        self.binding = binding
        self.predecessor = predecessor
        self.foreground = current.foreground
        self._binding_snapshot = (binding.run_id, binding.token, binding._issuer)
        self._handoff_snapshot = (
            current.run_id,
            current.consumed_root,
            current.consumed_delivery,
            current.foreground,
            foreground_values(current.foreground),
            current._issuer,
        )
        self.opened = False
        self.root: EncounterBranchRoot | None = None
        self.predecessor_current = True

    def require(
        self,
        binding: object,
        predecessor: object,
        *,
        opened: bool | None = None,
    ) -> ReceivedForegroundHandoff:
        if (
            type(binding) is not EncounterOpeningBinding
            or binding is not self.binding
            or binding.run_id != self._binding_snapshot[0]
            or binding.token is not self._binding_snapshot[1]
            or binding._issuer is not self._binding_snapshot[2]
            or predecessor is not self.predecessor
            or self.verifier.require(predecessor) is not predecessor
            or (opened is not None and self.opened is not opened)
        ):
            raise EncounterOpeningRefusal("exact_encounter_opening_binding_required")
        current = self.consumer.require_current(self.handoff)
        snapshot = self._handoff_snapshot
        if (
            current.run_id != snapshot[0]
            or current.consumed_root is not snapshot[1]
            or current.consumed_delivery is not snapshot[2]
            or current.foreground is not snapshot[3]
            or foreground_values(current.foreground) != snapshot[4]
            or current._issuer is not snapshot[5]
            or current.consumed_root is not predecessor
            or current.foreground is not self.foreground
        ):
            raise EncounterOpeningRefusal("received_foreground_handoff_changed")
        return current


class RuntimeEncounterOpener:
    """One registered runtime authority for the comparison group's openings."""

    def __init__(
        self,
        consumers: tuple[RuntimeForegroundConsumer, ...],
        verifiers: tuple[RecipientCurrentnessVerifier, ...],
        owner: object,
        permit: object,
    ) -> None:
        if (
            len(consumers) != 3
            or len(verifiers) != 3
            or len({id(item) for item in consumers}) != 3
            or len({id(item.root) for item in verifiers}) != 3
            or any(
                verifier.root is not consumer._delivery.recipient
                or verifier.require(verifier.root) is not verifier.root
                for consumer, verifier in zip(consumers, verifiers, strict=True)
            )
        ):
            raise EncounterOpeningRefusal("exact_three_encounter_recipients_required")
        consumer_permits = tuple(
            consumer._encounter_permit for consumer in consumers
        )
        for consumer, consumer_permit in zip(
            consumers, consumer_permits, strict=True
        ):
            consumer._require_encounter_unclaimed(consumer_permit)
        owner._claim_encounter_runtime(self, permit, consumers)
        self._consumers = consumers
        self._verifiers = verifiers
        self._uses: list[_OpeningUse] = []
        self._roots: list[EncounterBranchRoot] = []
        self._root_snapshots: list[tuple[object, ...]] = []
        self._issuer = object()
        self._consumer_permits = consumer_permits
        for consumer, consumer_permit in zip(
            consumers, self._consumer_permits, strict=True
        ):
            consumer._claim_encounter_authority(self, consumer_permit)

    def bind(
        self,
        consumer: object,
        handoff: object,
    ) -> EncounterOpeningBinding:
        match = next(
            (
                (allowed, verifier)
                for allowed, verifier in zip(
                    self._consumers, self._verifiers, strict=True
                )
                if consumer is allowed
            ),
            None,
        )
        if match is None or type(consumer) is not RuntimeForegroundConsumer:
            raise EncounterOpeningRefusal("exact_foreground_consumer_required")
        if any(use.consumer is consumer for use in self._uses):
            raise EncounterOpeningRefusal("encounter_opening_already_bound")
        allowed, verifier = match
        consumer_permit = self._consumer_permits[self._consumers.index(allowed)]
        current = allowed.require_current(handoff)
        binding = EncounterOpeningBinding(current.run_id, object(), _BINDING_ISSUER)
        use = _OpeningUse(allowed, current, verifier, binding)
        allowed._register_encounter_binding(
            self,
            current,
            binding,
            consumer_permit,
        )
        self._uses.append(use)
        return binding

    def _find_use(self, binding: object) -> _OpeningUse:
        use = next((item for item in self._uses if item.binding is binding), None)
        if use is None:
            raise EncounterOpeningRefusal("exact_encounter_opening_binding_required")
        return use

    def require_binding(
        self,
        binding: object,
        consumer: object,
        handoff: object,
        predecessor: object,
        *,
        opened: bool | None = None,
    ) -> EncounterOpeningBinding:
        use = self._find_use(binding)
        if use.consumer is not consumer or use.handoff is not handoff:
            raise EncounterOpeningRefusal("exact_encounter_opening_binding_required")
        use.require(binding, predecessor, opened=opened)
        return use.binding

    def open(self, predecessor: object, binding: object) -> EncounterBranchRoot:
        use = self._find_use(binding)
        if use.opened or use.root is not None:
            raise EncounterOpeningRefusal("encounter_opening_already_consumed")
        current = use.require(binding, predecessor, opened=False)
        encounter = PositiveEncounter(current.run_id, object(), _ENCOUNTER_ISSUER)
        append = EncounterOpenedAppend(
            current.run_id,
            predecessor,
            use.binding,
            encounter,
            current.foreground,
            _APPEND_ISSUER,
        )
        root = EncounterBranchRoot(
            current.run_id,
            predecessor,
            use.binding,
            encounter,
            append,
            current.foreground,
            _ROOT_ISSUER,
        )
        use.consumer._consume_encounter_binding(
            self,
            current,
            use.binding,
            self._consumer_permits[self._consumers.index(use.consumer)],
        )
        use.opened = True
        use.predecessor_current = False
        use.root = root
        self._roots.append(root)
        self._root_snapshots.append(
            (
                root,
                root.run_id,
                root.predecessor,
                root.opening_binding,
                root.encounter,
                root.append,
                root.situation,
                root._issuer,
                append.run_id,
                append.predecessor,
                append.opening_binding,
                append.encounter,
                append.situation,
                append._issuer,
                encounter.run_id,
                encounter.token,
                encounter._issuer,
                foreground_values(root.situation),
            )
        )
        return root

    def require_predecessor_current(self, predecessor: object) -> object:
        use = next(
            (item for item in self._uses if item.predecessor is predecessor), None
        )
        if use is None or not use.predecessor_current:
            raise EncounterOpeningRefusal("encounter_predecessor_not_current")
        use.verifier.require(predecessor)
        return predecessor

    def require_root(self, root: object) -> EncounterBranchRoot:
        snapshot = next(
            (item for item in self._root_snapshots if item[0] is root), None
        )
        if type(root) is not EncounterBranchRoot or snapshot is None:
            raise EncounterOpeningRefusal("exact_encounter_root_required")
        append = root.append
        encounter = root.encounter
        if (
            root.run_id != snapshot[1]
            or root.predecessor is not snapshot[2]
            or root.opening_binding is not snapshot[3]
            or root.encounter is not snapshot[4]
            or root.append is not snapshot[5]
            or root.situation is not snapshot[6]
            or root._issuer is not snapshot[7]
            or append.run_id != snapshot[8]
            or append.predecessor is not snapshot[9]
            or append.opening_binding is not snapshot[10]
            or append.encounter is not snapshot[11]
            or append.situation is not snapshot[12]
            or append._issuer is not snapshot[13]
            or encounter.run_id != snapshot[14]
            or encounter.token is not snapshot[15]
            or encounter._issuer is not snapshot[16]
            or foreground_values(root.situation) != snapshot[17]
            or append.situation is not root.situation
            or append.predecessor is not root.predecessor
            or append.opening_binding is not root.opening_binding
            or append.encounter is not root.encounter
        ):
            raise EncounterOpeningRefusal("encounter_root_changed")
        use = self._find_use(root.opening_binding)
        if not use.opened or use.root is not root:
            raise EncounterOpeningRefusal("encounter_root_changed")
        use.require(root.opening_binding, root.predecessor, opened=True)
        return root

    def root_verifier(self, root: object) -> _EncounterRootVerifier:
        current = self.require_root(root)
        return _EncounterRootVerifier(current)


class _EncounterRootVerifier:
    """Detached verifier for the exact current encounter-layer head."""

    def __init__(self, root: EncounterBranchRoot) -> None:
        self.root = root
        self._snapshot = (
            root.run_id,
            root.predecessor,
            root.opening_binding,
            root.encounter,
            root.append,
            root.situation,
            root._issuer,
            root.opening_binding.run_id,
            root.opening_binding.token,
            root.opening_binding._issuer,
            root.encounter.run_id,
            root.encounter.token,
            root.encounter._issuer,
            root.append.run_id,
            root.append.predecessor,
            root.append.opening_binding,
            root.append.encounter,
            root.append.situation,
            root.append._issuer,
            foreground_values(root.situation),
        )

    def require(self, root: object) -> EncounterBranchRoot:
        if type(root) is not EncounterBranchRoot or root is not self.root:
            raise EncounterOpeningRefusal("exact_encounter_root_required")
        snapshot = self._snapshot
        if (
            root.run_id != snapshot[0]
            or root.predecessor is not snapshot[1]
            or root.opening_binding is not snapshot[2]
            or root.encounter is not snapshot[3]
            or root.append is not snapshot[4]
            or root.situation is not snapshot[5]
            or root._issuer is not snapshot[6]
            or root.opening_binding.run_id != snapshot[7]
            or root.opening_binding.token is not snapshot[8]
            or root.opening_binding._issuer is not snapshot[9]
            or root.encounter.run_id != snapshot[10]
            or root.encounter.token is not snapshot[11]
            or root.encounter._issuer is not snapshot[12]
            or root.append.run_id != snapshot[13]
            or root.append.predecessor is not snapshot[14]
            or root.append.opening_binding is not snapshot[15]
            or root.append.encounter is not snapshot[16]
            or root.append.situation is not snapshot[17]
            or root.append._issuer is not snapshot[18]
            or foreground_values(root.situation) != snapshot[19]
        ):
            raise EncounterOpeningRefusal("encounter_root_changed")
        return root
