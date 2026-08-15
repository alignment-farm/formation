"""Runtime-owned semantic practice requests for positive decisions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from formation.activation import (
    ActivatedDecisionRoot,
    ActivationDecisionRefusal,
    ActivationHandoff,
    RuntimePositiveActivationAuthority,
    WithheldDecisionRoot,
)
from formation.condition_append import baseline_condition, treatment_condition
from formation.foreground import PositiveForeground, foreground_values


PRACTICE_ACTOR = "blind-commit-v0"

_WITHHELD_REQUEST_ISSUER = object()
_ACTIVATED_REQUEST_ISSUER = object()
_REQUEST_ROOT_ISSUER = object()


class PracticeRequestRefusal(ValueError):
    """The fixture practice request cannot be prepared from this decision."""


class DecisionRootVerifier(Protocol):
    root: WithheldDecisionRoot | ActivatedDecisionRoot

    def require(
        self, root: object
    ) -> WithheldDecisionRoot | ActivatedDecisionRoot: ...


@dataclass(frozen=True, slots=True)
class WithheldPracticeRequest:
    run_id: str
    actor: str
    situation: PositiveForeground
    decision: object
    _issuer: object


@dataclass(frozen=True, slots=True)
class ActivatedPracticeRequest:
    run_id: str
    actor: str
    situation: PositiveForeground
    decision: object
    intervention: ActivationHandoff
    _issuer: object


@dataclass(frozen=True, slots=True)
class WithheldRequestRoot:
    run_id: str
    predecessor: WithheldDecisionRoot
    request: WithheldPracticeRequest
    _issuer: object


@dataclass(frozen=True, slots=True)
class ActivatedRequestRoot:
    run_id: str
    predecessor: ActivatedDecisionRoot
    request: ActivatedPracticeRequest
    intervention: ActivationHandoff
    _issuer: object


class _RequestPreparationUse:
    def __init__(self, verifier: DecisionRootVerifier) -> None:
        root = verifier.require(verifier.root)
        self.verifier = verifier
        self._verifier_snapshot = verifier
        self.root = root
        self.used = False
        self.request_root: WithheldRequestRoot | ActivatedRequestRoot | None = None
        self._preparations: list[WithheldRequestRoot | ActivatedRequestRoot] = []

    def require(
        self, root: object, *, used: bool | None = None
    ) -> WithheldDecisionRoot | ActivatedDecisionRoot:
        if (
            root is not self.root
            or self.verifier is not self._verifier_snapshot
            or self.verifier.require(root) is not root
            or (used is not None and self.used is not used)
        ):
            raise PracticeRequestRefusal("exact_practice_decision_root_required")
        return self.root


class RuntimePositivePracticeRequestAuthority:
    """One label-blind, two-decision positive request authority."""

    def __init__(
        self,
        verifiers: tuple[DecisionRootVerifier, DecisionRootVerifier],
        activation: RuntimePositiveActivationAuthority,
        owner: object,
        permit: object,
    ) -> None:
        if (
            len(verifiers) != 2
            or verifiers[0].root is verifiers[1].root
            or {type(item.root) for item in verifiers}
            != {WithheldDecisionRoot, ActivatedDecisionRoot}
        ):
            raise PracticeRequestRefusal("exact_positive_request_pair_required")
        roots = tuple(verifier.require(verifier.root) for verifier in verifiers)
        withheld = next(item for item in roots if type(item) is WithheldDecisionRoot)
        activated = next(item for item in roots if type(item) is ActivatedDecisionRoot)
        if (
            withheld.considered.formation_condition != baseline_condition()
            or withheld.considered.eligible_versions != ()
            or hasattr(withheld, "handoff_binding")
            or activated.considered.formation_condition != treatment_condition()
            or activated.considered.eligible_versions
            != (activated.selected_admission,)
            or activation.require_handoff_binding(
                activated.handoff_binding, activated
            )
            is not activated.handoff_binding
        ):
            raise PracticeRequestRefusal("exact_positive_request_pair_required")
        owner._preflight_practice_runtime(permit, verifiers)
        activation._claim_practice_authority(self, owner, permit)
        owner._claim_practice_runtime(self, permit, verifiers)
        self._activation = activation
        self._uses = tuple(_RequestPreparationUse(item) for item in verifiers)
        self._roots: list[WithheldRequestRoot | ActivatedRequestRoot] = []
        self._snapshots: list[tuple[object, ...]] = []
        self._active_handoff_consumption: tuple[object, ActivatedDecisionRoot] | None = None

    def _use_for(self, root: object) -> _RequestPreparationUse:
        use = next((item for item in self._uses if item.root is root), None)
        if use is None:
            raise PracticeRequestRefusal("exact_practice_decision_root_required")
        return use

    def prepare(
        self, root: object
    ) -> WithheldRequestRoot | ActivatedRequestRoot:
        use = self._use_for(root)
        if use.used or use.request_root is not None or use._preparations:
            raise PracticeRequestRefusal("practice_request_already_prepared")
        current = use.require(root, used=False)
        self._activation.require_root(current)
        situation = current.considered.situation
        if (
            situation is not current.predecessor.situation
            or foreground_values(situation)
            != foreground_values(current.predecessor.situation)
        ):
            raise PracticeRequestRefusal("practice_request_situation_changed")

        if type(current) is WithheldDecisionRoot:
            if (
                current.considered.formation_condition != baseline_condition()
                or current.considered.eligible_versions != ()
                or hasattr(current, "handoff_binding")
            ):
                raise PracticeRequestRefusal("exact_withheld_decision_required")
            request = WithheldPracticeRequest(
                current.run_id,
                PRACTICE_ACTOR,
                situation,
                current.result,
                _WITHHELD_REQUEST_ISSUER,
            )
            request_root: WithheldRequestRoot | ActivatedRequestRoot = (
                WithheldRequestRoot(
                    current.run_id, current, request, _REQUEST_ROOT_ISSUER
                )
            )
        else:
            if (
                type(current) is not ActivatedDecisionRoot
                or current.considered.formation_condition != treatment_condition()
                or current.considered.eligible_versions
                != (current.selected_admission,)
                or self._activation.require_handoff_binding(
                    current.handoff_binding, current
                )
                is not current.handoff_binding
            ):
                raise PracticeRequestRefusal("exact_activated_decision_required")
            preparation_token = object()
            self._active_handoff_consumption = (preparation_token, current)
            try:
                intervention = self._activation._consume_request_handoff(
                    self,
                    current.handoff_binding,
                    current,
                    preparation_token,
                )
            finally:
                self._active_handoff_consumption = None
            request = ActivatedPracticeRequest(
                current.run_id,
                PRACTICE_ACTOR,
                situation,
                current.result,
                intervention,
                _ACTIVATED_REQUEST_ISSUER,
            )
            request_root = ActivatedRequestRoot(
                current.run_id,
                current,
                request,
                intervention,
                _REQUEST_ROOT_ISSUER,
            )
        use.used = True
        use.request_root = request_root
        use._preparations.append(request_root)
        self._roots.append(request_root)
        self._snapshots.append(self._snapshot(request_root))
        return request_root

    def _require_active_handoff_consumption(
        self, token: object, root: object
    ) -> None:
        context = self._active_handoff_consumption
        if context is None or token is not context[0] or root is not context[1]:
            raise PracticeRequestRefusal("active_request_preparation_required")

    @staticmethod
    def _snapshot(root: WithheldRequestRoot | ActivatedRequestRoot) -> tuple[object, ...]:
        request = root.request
        common = (
            id(root),
            root.run_id,
            id(root.predecessor),
            id(root.request),
            id(root._issuer),
            request.run_id,
            request.actor,
            id(request.situation),
            id(request.decision),
            id(request._issuer),
            foreground_values(request.situation),
        )
        if type(root) is WithheldRequestRoot:
            return common
        return common + (id(root.intervention), id(request.intervention))

    def require_root(
        self, root: object
    ) -> WithheldRequestRoot | ActivatedRequestRoot:
        snapshot = next(
            (item for item in self._snapshots if item[0] == id(root)), None
        )
        if snapshot is None or type(root) not in (
            WithheldRequestRoot,
            ActivatedRequestRoot,
        ):
            raise PracticeRequestRefusal("exact_practice_request_root_required")
        if self._snapshot(root) != snapshot:
            raise PracticeRequestRefusal("practice_request_root_changed")
        use = self._use_for(root.predecessor)
        if (
            not use.used
            or use.request_root is not root
            or len(use._preparations) != 1
            or use._preparations[0] is not root
        ):
            raise PracticeRequestRefusal("practice_request_root_changed")
        use.verifier.require(root.predecessor)
        if type(root) is ActivatedRequestRoot:
            if root.request.intervention is not root.intervention:
                raise PracticeRequestRefusal("practice_request_intervention_changed")
            self._activation.require_handoff_binding(
                root.predecessor.handoff_binding, root.predecessor
            )
        return root

    def require_predecessor_current(
        self, root: object
    ) -> WithheldDecisionRoot | ActivatedDecisionRoot:
        use = self._use_for(root)
        if use.used or use.request_root is not None or use._preparations:
            raise PracticeRequestRefusal("practice_decision_predecessor_not_current")
        return use.require(root, used=False)
