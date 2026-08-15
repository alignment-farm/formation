"""Runtime-owned positive activation decisions for baseline and governed roots."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from formation.admitted_root import (
    ADMITTED_SCOPE,
    CANDIDATE_REPRESENTATION,
    AdmittedCandidate,
    ProposedCandidate,
    admission_public_semantics,
    proposal_public_semantics,
)
from formation.condition_append import (
    INFLUENCE_POLICY,
    PublicFormationCondition,
    baseline_condition,
    treatment_condition,
)
from formation.encounter import EncounterBranchRoot
from formation.foreground import PositiveForeground, foreground_values


INTERVENTION_PROCEDURE = "revision-check-intervention-v0"
SELECTION_REASON = (
    "derived_from is present and depends_on_current_authority is true"
)
WITHHOLDING_REFUSAL = "no_admitted_change"

_CONSIDERED_ISSUER = object()
_WITHHELD_ISSUER = object()
_ACTIVATED_ISSUER = object()
_HANDOFF_ISSUER = object()
_BINDING_ISSUER = object()
_ROOT_ISSUER = object()


class ActivationDecisionRefusal(ValueError):
    """The fixture activation decision cannot be made from this lineage."""


class ActivationInputVerifier(Protocol):
    root: EncounterBranchRoot
    condition: PublicFormationCondition
    admission: AdmittedCandidate | None
    proposal: ProposedCandidate | None
    replay_constrained: bool

    def require(self, root: object) -> EncounterBranchRoot: ...


@dataclass(frozen=True, slots=True)
class ActivationConsidered:
    run_id: str
    predecessor: EncounterBranchRoot
    encounter: object
    formation_condition: PublicFormationCondition
    activation_policy: str
    eligible_versions: tuple[AdmittedCandidate, ...]
    situation: PositiveForeground
    _issuer: object


@dataclass(frozen=True, slots=True)
class ActivationWithheld:
    run_id: str
    considered: ActivationConsidered
    refusal: str
    _issuer: object


@dataclass(frozen=True, slots=True)
class ChangeActivated:
    run_id: str
    considered: ActivationConsidered
    selected_admission: AdmittedCandidate
    _issuer: object


@dataclass(frozen=True, slots=True)
class ActivationHandoff:
    run_id: str
    encounter: object
    considered: ActivationConsidered
    selected_admission: AdmittedCandidate
    proposal: ProposedCandidate
    intervention_procedure: str
    intervention_content: str
    selection_reason: str
    _issuer: object


@dataclass(frozen=True, slots=True)
class ActivationHandoffBinding:
    run_id: str
    token: object
    _issuer: object


@dataclass(frozen=True, slots=True)
class WithheldDecisionRoot:
    run_id: str
    predecessor: EncounterBranchRoot
    considered: ActivationConsidered
    result: ActivationWithheld
    _issuer: object


@dataclass(frozen=True, slots=True)
class ActivatedDecisionRoot:
    run_id: str
    predecessor: EncounterBranchRoot
    considered: ActivationConsidered
    result: ChangeActivated
    selected_admission: AdmittedCandidate
    proposal: ProposedCandidate
    handoff_binding: ActivationHandoffBinding
    _issuer: object


class _DecisionUse:
    def __init__(self, verifier: ActivationInputVerifier) -> None:
        root = verifier.require(verifier.root)
        self.verifier = verifier
        self.root = root
        self.condition = verifier.condition
        self.admission = verifier.admission
        self.proposal = verifier.proposal
        self._input_snapshot = (
            self.condition,
            self.admission,
            self.proposal,
        )
        self.used = False
        self.decision_root: WithheldDecisionRoot | ActivatedDecisionRoot | None = None

    def require(self, root: object, *, used: bool | None = None) -> EncounterBranchRoot:
        if (
            root is not self.root
            or self.verifier.require(root) is not root
            or self.condition != self._input_snapshot[0]
            or self.admission is not self._input_snapshot[1]
            or self.proposal is not self._input_snapshot[2]
            or self.condition != self.verifier.condition
            or self.admission is not self.verifier.admission
            or self.proposal is not self.verifier.proposal
            or (used is not None and self.used is not used)
        ):
            raise ActivationDecisionRefusal("exact_activation_encounter_required")
        return self.root


class _ActivationHandoffUse:
    def __init__(
        self,
        binding: ActivationHandoffBinding,
        handoff: ActivationHandoff,
        decision_root: ActivatedDecisionRoot,
    ) -> None:
        self.binding = binding
        self.handoff = handoff
        self.decision_root = decision_root
        self._binding_snapshot = (binding.run_id, binding.token, binding._issuer)
        self._handoff_snapshot = (
            handoff.run_id,
            handoff.encounter,
            handoff.considered,
            handoff.selected_admission,
            handoff.proposal,
            handoff.intervention_procedure,
            handoff.intervention_content,
            handoff.selection_reason,
            handoff._issuer,
        )
        self.request_consumed = False

    def require(
        self, binding: object, decision_root: object
    ) -> ActivationHandoffBinding:
        if (
            type(binding) is not ActivationHandoffBinding
            or binding is not self.binding
            or decision_root is not self.decision_root
            or binding.run_id != self._binding_snapshot[0]
            or binding.token is not self._binding_snapshot[1]
            or binding._issuer is not self._binding_snapshot[2]
        ):
            raise ActivationDecisionRefusal("exact_activation_handoff_binding_required")
        handoff = self.handoff
        snapshot = self._handoff_snapshot
        if (
            handoff.run_id != snapshot[0]
            or handoff.encounter is not snapshot[1]
            or handoff.considered is not snapshot[2]
            or handoff.selected_admission is not snapshot[3]
            or handoff.proposal is not snapshot[4]
            or handoff.intervention_procedure != snapshot[5]
            or handoff.intervention_content != snapshot[6]
            or handoff.selection_reason != snapshot[7]
            or handoff._issuer is not snapshot[8]
        ):
            raise ActivationDecisionRefusal("activation_handoff_changed")
        return binding


class RuntimePositiveActivationAuthority:
    """One label-blind, two-root positive activation authority."""

    def __init__(
        self,
        verifiers: tuple[ActivationInputVerifier, ActivationInputVerifier],
        owner: object,
        permit: object,
    ) -> None:
        if (
            len(verifiers) != 2
            or verifiers[0].root is verifiers[1].root
            or any(verifier.replay_constrained for verifier in verifiers)
        ):
            raise ActivationDecisionRefusal("exact_positive_activation_pair_required")
        conditions = {verifier.condition.condition for verifier in verifiers}
        if conditions != {
            baseline_condition().condition,
            treatment_condition().condition,
        }:
            raise ActivationDecisionRefusal("exact_positive_activation_pair_required")
        for verifier in verifiers:
            verifier.require(verifier.root)
            if verifier.condition == baseline_condition():
                if verifier.admission is not None or verifier.proposal is not None:
                    raise ActivationDecisionRefusal("baseline_eligible_state_not_empty")
            elif (
                verifier.condition != treatment_condition()
                or type(verifier.admission) is not AdmittedCandidate
                or type(verifier.proposal) is not ProposedCandidate
                or verifier.admission.proposal is not verifier.proposal
            ):
                raise ActivationDecisionRefusal("governed_admission_required")
        owner._claim_activation_runtime(self, permit, verifiers)
        self._uses = tuple(_DecisionUse(verifier) for verifier in verifiers)
        self._decision_roots: list[WithheldDecisionRoot | ActivatedDecisionRoot] = []
        self._decision_snapshots: list[tuple[object, ...]] = []
        self._handoff_uses: list[_ActivationHandoffUse] = []
        self._issuer = object()

    def _use_for(self, root: object) -> _DecisionUse:
        use = next((item for item in self._uses if item.root is root), None)
        if use is None:
            raise ActivationDecisionRefusal("exact_activation_encounter_required")
        return use

    def decide(
        self, root: object
    ) -> WithheldDecisionRoot | ActivatedDecisionRoot:
        use = self._use_for(root)
        if use.used or use.decision_root is not None:
            raise ActivationDecisionRefusal("activation_decision_already_consumed")
        current = use.require(root, used=False)
        if current.situation is not current.append.situation:
            raise ActivationDecisionRefusal("activation_situation_changed")
        foreground_values(current.situation)
        if use.condition == baseline_condition():
            considered = ActivationConsidered(
                current.run_id,
                current,
                current.encounter,
                baseline_condition(),
                INFLUENCE_POLICY,
                (),
                current.situation,
                _CONSIDERED_ISSUER,
            )
            result = ActivationWithheld(
                current.run_id, considered, WITHHOLDING_REFUSAL, _WITHHELD_ISSUER
            )
            decision_root: WithheldDecisionRoot | ActivatedDecisionRoot = (
                WithheldDecisionRoot(
                    current.run_id, current, considered, result, _ROOT_ISSUER
                )
            )
        else:
            admission = use.admission
            proposal = use.proposal
            if (
                type(admission) is not AdmittedCandidate
                or type(proposal) is not ProposedCandidate
                or admission.proposal is not proposal
                or admission.scope != ADMITTED_SCOPE
                or admission.status != "eligible"
                or proposal.representation != CANDIDATE_REPRESENTATION
                or current.situation.derived_from == ""
                or type(current.situation.depends_on_current_authority) is not bool
                or current.situation.depends_on_current_authority is not True
            ):
                raise ActivationDecisionRefusal("positive_applicability_not_met")
            considered = ActivationConsidered(
                current.run_id,
                current,
                current.encounter,
                treatment_condition(),
                INFLUENCE_POLICY,
                (admission,),
                current.situation,
                _CONSIDERED_ISSUER,
            )
            result = ChangeActivated(
                current.run_id, considered, admission, _ACTIVATED_ISSUER
            )
            binding = ActivationHandoffBinding(
                current.run_id, object(), _BINDING_ISSUER
            )
            handoff = ActivationHandoff(
                current.run_id,
                current.encounter,
                considered,
                admission,
                proposal,
                INTERVENTION_PROCEDURE,
                proposal.representation,
                SELECTION_REASON,
                _HANDOFF_ISSUER,
            )
            decision_root = ActivatedDecisionRoot(
                current.run_id,
                current,
                considered,
                result,
                admission,
                proposal,
                binding,
                _ROOT_ISSUER,
            )
            self._handoff_uses.append(
                _ActivationHandoffUse(binding, handoff, decision_root)
            )
        use.used = True
        use.decision_root = decision_root
        self._decision_roots.append(decision_root)
        self._decision_snapshots.append(self._snapshot(decision_root))
        return decision_root

    @staticmethod
    def _snapshot(root: WithheldDecisionRoot | ActivatedDecisionRoot) -> tuple[object, ...]:
        considered = root.considered
        common = (
            id(root),
            root.run_id,
            id(root.predecessor),
            id(root.considered),
            id(root.result),
            id(root._issuer),
            considered.run_id,
            id(considered.predecessor),
            id(considered.encounter),
            considered.formation_condition,
            considered.activation_policy,
            tuple(id(item) for item in considered.eligible_versions),
            id(considered.situation),
            id(considered._issuer),
            foreground_values(considered.situation),
        )
        if type(root) is WithheldDecisionRoot:
            return common + (
                root.result.run_id,
                id(root.result.considered),
                root.result.refusal,
                id(root.result._issuer),
            )
        return common + (
            id(root.selected_admission),
            id(root.proposal),
            id(root.handoff_binding),
            root.result.run_id,
            id(root.result.considered),
            id(root.result.selected_admission),
            id(root.result._issuer),
            admission_public_semantics(root.selected_admission),
            proposal_public_semantics(root.proposal),
            root.handoff_binding.run_id,
            id(root.handoff_binding.token),
            id(root.handoff_binding._issuer),
        )

    def require_root(
        self, root: object
    ) -> WithheldDecisionRoot | ActivatedDecisionRoot:
        snapshot = next(
            (item for item in self._decision_snapshots if item[0] == id(root)), None
        )
        if snapshot is None or type(root) not in (
            WithheldDecisionRoot,
            ActivatedDecisionRoot,
        ):
            raise ActivationDecisionRefusal("exact_activation_decision_root_required")
        if self._snapshot(root) != snapshot:
            raise ActivationDecisionRefusal("activation_decision_root_changed")
        use = self._use_for(root.predecessor)
        if not use.used or use.decision_root is not root:
            raise ActivationDecisionRefusal("activation_decision_root_changed")
        use.verifier.require(root.predecessor)
        if type(root) is ActivatedDecisionRoot:
            self.require_handoff_binding(root.handoff_binding, root)
        return root

    def require_predecessor_current(self, root: object) -> EncounterBranchRoot:
        use = self._use_for(root)
        if use.used or use.decision_root is not None:
            raise ActivationDecisionRefusal("activation_predecessor_not_current")
        return use.require(root, used=False)

    def require_handoff_binding(
        self, binding: object, root: object
    ) -> ActivationHandoffBinding:
        use = next(
            (item for item in self._handoff_uses if item.binding is binding), None
        )
        if use is None:
            raise ActivationDecisionRefusal("exact_activation_handoff_binding_required")
        return use.require(binding, root)

    def root_verifier(self, root: object) -> _DecisionRootVerifier:
        return _DecisionRootVerifier(self.require_root(root))


class _DecisionRootVerifier:
    """Snapshot-only verifier with no activation registry backpointer."""

    def __init__(self, root: WithheldDecisionRoot | ActivatedDecisionRoot) -> None:
        self.root = root
        self._snapshot = RuntimePositiveActivationAuthority._snapshot(root)

    def require(
        self, root: object
    ) -> WithheldDecisionRoot | ActivatedDecisionRoot:
        if root is not self.root or type(root) not in (
            WithheldDecisionRoot,
            ActivatedDecisionRoot,
        ):
            raise ActivationDecisionRefusal("exact_activation_decision_root_required")
        if RuntimePositiveActivationAuthority._snapshot(root) != self._snapshot:
            raise ActivationDecisionRefusal("activation_decision_root_changed")
        return root
