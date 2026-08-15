"""Harness-owned validators and witnesses for fixture direct admission."""

from __future__ import annotations

from dataclasses import dataclass

from formation.admitted_root import (
    ADMISSION_EVENT,
    ADMISSION_ORDER,
    ADMITTED_SCOPE,
    CANDIDATE_REPRESENTATION,
    CLAIMED_APPLICABILITY,
    COUNTEREVIDENCE,
    EXPECTED_EFFECT,
    EXPLICIT_NON_APPLICABILITY,
    PROPOSAL_EVENT,
    PROPOSAL_ORDER,
    RECORDER,
    SOURCE_CONSEQUENCE,
    SOURCE_EXPERIENCE,
    STATUS_ELIGIBLE,
    WARRANT_CHECKS,
    AdmissionHandoff,
    AdmissionRefusal,
    AdmissionWarrant,
    AdmittedCandidate,
    CandidateProjection,
    ProposalHandoff,
    ProposalRefusal,
    ProposedCandidate,
    RuntimeFormationMaterializer,
    admission_public_semantics,
    proposal_public_semantics,
)
from formation.condition_append import GOVERNOR, INTERPRETER
from trajectory.fixture_condition import (
    BranchLocalRoot,
    ConditionAppendController,
    TreatmentRootBatch,
    TreatmentRootBatchRefusal,
)


class FormationValidationRefusal(ValueError):
    """A proposal or admission is not the exact fixture semantic object."""


class FormationAppendRefusal(ValueError):
    """The witnessed formation path cannot become an admitted root."""


class AdmittedTreatmentBatchRefusal(ValueError):
    """The exact pair of returned treatment admission roots is unavailable."""


@dataclass(frozen=True)
class ProposalWitness:
    run_id: str
    root: BranchLocalRoot
    proposal_handoff: ProposalHandoff
    _issuer: object


@dataclass(frozen=True)
class AdmissionWitness:
    run_id: str
    root: BranchLocalRoot
    admission_handoff: AdmissionHandoff
    proposal_witness: ProposalWitness
    _issuer: object


@dataclass(frozen=True)
class AdmittedBranchRoot:
    run_id: str
    condition_root: BranchLocalRoot
    proposal: ProposedCandidate
    admission: AdmittedCandidate
    head: object
    _issuer: object


class _AdmittedTreatmentBatchUse:
    def __init__(self, verifiers: tuple[_AdmittedRootVerifier, _AdmittedRootVerifier]) -> None:
        self._verifiers = verifiers
        self._batch: AdmittedTreatmentBatch | None = None
        self._snapshot: tuple[object, ...] | None = None
        self.used = False

    def bind(self, batch: AdmittedTreatmentBatch) -> None:
        if self._batch is not None:
            raise AdmittedTreatmentBatchRefusal("admitted_treatment_batch_already_bound")
        self._batch = batch
        self._snapshot = (
            batch.run_id,
            batch.roots,
            batch._use,
            batch._issuer,
        )

    def require_root(self, root: object) -> AdmittedBranchRoot:
        verifier = next(
            (item for item in self._verifiers if item.root is root), None
        )
        if verifier is None:
            raise AdmittedTreatmentBatchRefusal("exact_admitted_treatment_root_required")
        return verifier.require(root)

    def require(
        self, batch: object, *, consumed: bool | None = None
    ) -> AdmittedTreatmentBatch:
        if (
            type(batch) is not AdmittedTreatmentBatch
            or batch is not self._batch
            or self._snapshot is None
            or batch.run_id != self._snapshot[0]
            or batch.roots is not self._snapshot[1]
            or batch._use is not self._snapshot[2]
            or batch._issuer is not self._snapshot[3]
            or (consumed is not None and self.used is not consumed)
        ):
            raise AdmittedTreatmentBatchRefusal("exact_admitted_treatment_batch_required")
        for root in batch.roots:
            self.require_root(root)
        return batch

    def consume(self, batch: object) -> tuple[AdmittedBranchRoot, AdmittedBranchRoot]:
        if self.used:
            raise AdmittedTreatmentBatchRefusal("admitted_treatment_batch_already_consumed")
        self.require(batch, consumed=False)
        self.used = True
        return batch.roots


@dataclass(frozen=True)
class AdmittedTreatmentBatch:
    """Exact two-root admitted set in the original label-blind order."""

    run_id: str
    roots: tuple[AdmittedBranchRoot, AdmittedBranchRoot]
    _use: _AdmittedTreatmentBatchUse
    _issuer: object


class _AdmittedRootVerifier:
    """Detached runtime-chain verifier with no trajectory assignment authority."""

    def __init__(self, root: AdmittedBranchRoot, runtime: object, handoff: object) -> None:
        self.root = root
        self._runtime = runtime
        self._handoff = handoff
        self._snapshot = (
            root.run_id,
            root.condition_root,
            root.proposal,
            root.admission,
            root.head,
            root._issuer,
        )

    def require(self, root: object) -> AdmittedBranchRoot:
        if type(root) is not AdmittedBranchRoot or root is not self.root:
            raise AdmittedTreatmentBatchRefusal("exact_admitted_treatment_root_required")
        try:
            current = self._runtime.require_current_admission(self._handoff)
        except ValueError as error:
            raise AdmittedTreatmentBatchRefusal("admitted_treatment_root_changed") from error
        if (
            root.run_id != self._snapshot[0]
            or root.condition_root is not self._snapshot[1]
            or root.proposal is not self._snapshot[2]
            or root.admission is not self._snapshot[3]
            or root.head is not self._snapshot[4]
            or root._issuer is not self._snapshot[5]
            or current is not self._handoff
            or current.admission is not root.admission
            or current.admission.proposal is not root.proposal
        ):
            raise AdmittedTreatmentBatchRefusal("admitted_treatment_root_changed")
        return root


def validate_fixture_proposal(proposal: object) -> str:
    if type(proposal) is not ProposedCandidate:
        raise FormationValidationRefusal("invalid_fixture_proposal")
    expected_projection = CandidateProjection(
        SOURCE_EXPERIENCE,
        SOURCE_CONSEQUENCE,
        INTERPRETER,
        CLAIMED_APPLICABILITY,
        EXPLICIT_NON_APPLICABILITY,
        EXPECTED_EFFECT,
        COUNTEREVIDENCE,
        None,
    )
    source = proposal_public_semantics(proposal)
    expected = (
        PROPOSAL_ORDER,
        PROPOSAL_EVENT,
        INTERPRETER,
        RECORDER,
        CANDIDATE_REPRESENTATION,
        (
            expected_projection.source_experience,
            expected_projection.source_consequence,
            expected_projection.author,
            expected_projection.claimed_applicability,
            expected_projection.explicit_non_applicability,
            expected_projection.expected_practice_effect,
            expected_projection.counterevidence,
            expected_projection.expiry,
        ),
    )
    if source != expected or len(proposal.parents) != 3:
        raise FormationValidationRefusal("invalid_fixture_proposal")
    coordinates = {getattr(parent, "coordinate", None) for parent in proposal.parents}
    if coordinates != {SOURCE_CONSEQUENCE, SOURCE_EXPERIENCE, proposal.consumed_root.head}:
        raise FormationValidationRefusal("invalid_fixture_proposal")
    if any(getattr(parent, "root", None) is not proposal.consumed_root for parent in proposal.parents):
        raise FormationValidationRefusal("invalid_fixture_proposal")
    if (
        proposal._authorship.source.consumed_root is not proposal.consumed_root
        or proposal._authorship.representation != proposal.representation
        or proposal._authorship.projection is not proposal.projection
    ):
        raise FormationValidationRefusal("invalid_fixture_proposal")
    return "valid_fixture_proposal"


def validate_fixture_admission(admission: object) -> str:
    if type(admission) is not AdmittedCandidate:
        raise FormationValidationRefusal("invalid_fixture_admission")
    expected = (
        ADMISSION_ORDER,
        ADMISSION_EVENT,
        GOVERNOR,
        RECORDER,
        proposal_public_semantics(admission.proposal),
        (SOURCE_CONSEQUENCE, WARRANT_CHECKS),
        ADMITTED_SCOPE,
        STATUS_ELIGIBLE,
        None,
    )
    if admission_public_semantics(admission) != expected or len(admission.parents) != 3:
        raise FormationValidationRefusal("invalid_fixture_admission")
    if admission.proposal.consumed_root is not admission.consumed_root:
        raise FormationValidationRefusal("invalid_fixture_admission")
    if admission.proposal.coordinate not in admission.parents:
        raise FormationValidationRefusal("invalid_fixture_admission")
    other_coordinates = {
        getattr(parent, "coordinate", None)
        for parent in admission.parents
        if parent is not admission.proposal.coordinate
    }
    if other_coordinates != {SOURCE_CONSEQUENCE, admission.consumed_root.head}:
        raise FormationValidationRefusal("invalid_fixture_admission")
    if any(
        getattr(parent, "root", admission.consumed_root) is not admission.consumed_root
        for parent in admission.parents
    ):
        raise FormationValidationRefusal("invalid_fixture_admission")
    if (
        admission._decision.proposal is not admission.proposal
        or admission._decision.warrant is not admission.warrant
        or admission._decision.scope != admission.scope
        or admission._decision.status != admission.status
        or admission._decision.trial is not admission.trial
    ):
        raise FormationValidationRefusal("invalid_fixture_admission")
    return "valid_fixture_admission"


class FormationAppendController:
    """Harness witness that never authors proposal or admission objects."""

    def __init__(
        self,
        conditions: ConditionAppendController,
        treatment_batch: object,
    ) -> None:
        if type(conditions) is not ConditionAppendController:
            raise TreatmentRootBatchRefusal("exact_condition_controller_required")
        self._issuer = object()
        batch = conditions.register_formation_controller(treatment_batch, self._issuer)
        self._conditions = conditions
        self._batch = batch
        self._root_issuer = object()
        self._proposal_witnesses: list[ProposalWitness] = []
        self._proposal_snapshots: list[tuple[object, ...]] = []
        self._admission_witnesses: list[AdmissionWitness] = []
        self._admission_snapshots: list[tuple[object, ...]] = []
        self._roots: list[AdmittedBranchRoot] = []
        self._root_snapshots: list[tuple[object, ...]] = []
        self._admitted_batch_issuer = object()
        self._admitted_batch: AdmittedTreatmentBatch | None = None
        self._admitted_batch_snapshot: tuple[object, ...] | None = None
        self._constraint_controller: object | None = None
        self._constraint_controller_snapshot: object | None = None

    def _require_batch_root(self, root: object) -> BranchLocalRoot:
        self._conditions.require_treatment_root_batch(self._batch)
        if type(root) is not BranchLocalRoot or not any(
            root is item for item in self._batch.roots
        ):
            raise FormationAppendRefusal("exact_treatment_root_required")
        return self._conditions.require_returned_root(root)

    def witness_proposal(
        self,
        runtime: RuntimeFormationMaterializer,
        handoff: object,
    ) -> ProposalWitness:
        try:
            current = runtime.require_current_proposal(handoff)
        except ProposalRefusal as error:
            raise FormationAppendRefusal(str(error)) from error
        root = self._require_batch_root(current.proposal.consumed_root)
        if current.source.consumed_root is not root:
            raise FormationAppendRefusal("proposal_source_root_mismatch")
        if any(witness.root is root for witness in self._proposal_witnesses):
            raise FormationAppendRefusal("proposal_already_witnessed")
        validate_fixture_proposal(current.proposal)
        witness = ProposalWitness(current.run_id, root, current, self._issuer)
        self._proposal_witnesses.append(witness)
        self._proposal_snapshots.append(
            (witness.run_id, witness.root, witness.proposal_handoff, witness._issuer)
        )
        return witness

    def _require_proposal_witness(self, witness: object) -> ProposalWitness:
        if type(witness) is not ProposalWitness or not any(
            witness is item for item in self._proposal_witnesses
        ):
            raise FormationAppendRefusal("exact_proposal_witness_required")
        snapshot = next(
            item
            for item in self._proposal_snapshots
            if item[2] is witness.proposal_handoff
        )
        if (
            witness.run_id != snapshot[0]
            or witness.root is not snapshot[1]
            or witness.proposal_handoff is not snapshot[2]
            or witness._issuer is not snapshot[3]
        ):
            raise FormationAppendRefusal("proposal_witness_changed")
        return witness

    def witness_admission(
        self,
        runtime: RuntimeFormationMaterializer,
        handoff: object,
        proposal_witness: object,
    ) -> AdmissionWitness:
        proposal_witness = self._require_proposal_witness(proposal_witness)
        try:
            current = runtime.require_current_admission(handoff)
        except AdmissionRefusal as error:
            raise FormationAppendRefusal(str(error)) from error
        root = self._require_batch_root(current.admission.consumed_root)
        if (
            proposal_witness.root is not root
            or current.proposal_handoff is not proposal_witness.proposal_handoff
            or current.admission.proposal is not proposal_witness.proposal_handoff.proposal
        ):
            raise FormationAppendRefusal("admission_proposal_witness_mismatch")
        if any(witness.root is root for witness in self._admission_witnesses):
            raise FormationAppendRefusal("admission_already_witnessed")
        validate_fixture_admission(current.admission)
        witness = AdmissionWitness(
            current.run_id,
            root,
            current,
            proposal_witness,
            self._issuer,
        )
        self._admission_witnesses.append(witness)
        self._admission_snapshots.append(
            (
                witness.run_id,
                witness.root,
                witness.admission_handoff,
                witness.proposal_witness,
                witness._issuer,
            )
        )
        return witness

    def _require_admission_witness(self, witness: object) -> AdmissionWitness:
        if type(witness) is not AdmissionWitness or not any(
            witness is item for item in self._admission_witnesses
        ):
            raise FormationAppendRefusal("exact_admission_witness_required")
        snapshot = next(
            item
            for item in self._admission_snapshots
            if item[2] is witness.admission_handoff
        )
        if (
            witness.run_id != snapshot[0]
            or witness.root is not snapshot[1]
            or witness.admission_handoff is not snapshot[2]
            or witness.proposal_witness is not snapshot[3]
            or witness._issuer is not snapshot[4]
        ):
            raise FormationAppendRefusal("admission_witness_changed")
        return witness

    def append(
        self,
        runtime: RuntimeFormationMaterializer,
        admission_handoff: object,
        proposal_witness: object,
        admission_witness: object,
    ) -> AdmittedBranchRoot:
        proposal_witness = self._require_proposal_witness(proposal_witness)
        admission_witness = self._require_admission_witness(admission_witness)
        try:
            current = runtime.require_current_admission(admission_handoff)
        except AdmissionRefusal as error:
            raise FormationAppendRefusal(str(error)) from error
        root = self._require_batch_root(current.admission.consumed_root)
        if (
            proposal_witness.root is not root
            or admission_witness.root is not root
            or admission_witness.proposal_witness is not proposal_witness
            or admission_witness.admission_handoff is not current
        ):
            raise FormationAppendRefusal("formation_witness_handoff_mismatch")
        validate_fixture_proposal(current.admission.proposal)
        validate_fixture_admission(current.admission)
        if any(item.condition_root is root for item in self._roots):
            raise FormationAppendRefusal("admitted_root_already_returned")
        admitted_root = AdmittedBranchRoot(
            run_id=current.run_id,
            condition_root=root,
            proposal=current.admission.proposal,
            admission=current.admission,
            head=current.admission.coordinate,
            _issuer=self._root_issuer,
        )
        if self._roots:
            reference = self._roots[0]
            if (
                proposal_public_semantics(admitted_root.proposal)
                != proposal_public_semantics(reference.proposal)
                or admission_public_semantics(admitted_root.admission)
                != admission_public_semantics(reference.admission)
                or admitted_root.proposal is reference.proposal
                or admitted_root.admission is reference.admission
                or admitted_root.head is reference.head
            ):
                raise FormationAppendRefusal("treatment_admission_pair_mismatch")
        self._roots.append(admitted_root)
        self._root_snapshots.append(
            (
                admitted_root.run_id,
                admitted_root.condition_root,
                admitted_root.proposal,
                admitted_root.admission,
                admitted_root.head,
                admitted_root._issuer,
                proposal_public_semantics(admitted_root.proposal),
                admission_public_semantics(admitted_root.admission),
                admitted_root.proposal._authorship,
                (
                    admitted_root.proposal._authorship.source,
                    admitted_root.proposal._authorship.representation,
                    admitted_root.proposal._authorship.projection,
                    proposal_public_semantics(admitted_root.proposal),
                    admitted_root.proposal._authorship._issuer,
                ),
                admitted_root.admission._decision,
                (
                    admitted_root.admission._decision.proposal,
                    admitted_root.admission._decision.warrant,
                    admission_public_semantics(admitted_root.admission),
                    admitted_root.admission._decision.scope,
                    admitted_root.admission._decision.status,
                    admitted_root.admission._decision.trial,
                    admitted_root.admission._decision._issuer,
                ),
                (
                    admitted_root.proposal._authorship.source,
                    admitted_root.proposal._authorship.source.run_id,
                    admitted_root.proposal._authorship.source.consumed_root,
                    admitted_root.proposal._authorship.source.source_consequence,
                    admitted_root.proposal._authorship.source.source_consequence.root,
                    admitted_root.proposal._authorship.source.source_consequence.coordinate,
                    admitted_root.proposal._authorship.source.source_consequence.artifact,
                    admitted_root.proposal._authorship.source.source_consequence._issuer,
                    admitted_root.proposal._authorship.source.source_experience,
                    admitted_root.proposal._authorship.source.source_experience.root,
                    admitted_root.proposal._authorship.source.source_experience.coordinate,
                    admitted_root.proposal._authorship.source.source_experience.artifact,
                    admitted_root.proposal._authorship.source.source_experience._issuer,
                    admitted_root.proposal._authorship.source.condition_head,
                    admitted_root.proposal._authorship.source.condition_head.root,
                    admitted_root.proposal._authorship.source.condition_head.coordinate,
                    admitted_root.proposal._authorship.source.condition_head._issuer,
                    admitted_root.proposal._authorship.source.public_condition,
                    admitted_root.proposal._authorship.source.public_condition.condition,
                    admitted_root.proposal._authorship.source.public_condition.interpreter,
                    admitted_root.proposal._authorship.source.public_condition.governor,
                    admitted_root.proposal._authorship.source.public_condition.influence_policy,
                    admitted_root.proposal._authorship.source._use,
                    admitted_root.proposal._authorship.source._use.source_root,
                    admitted_root.proposal._authorship.source._use.source,
                    admitted_root.proposal._authorship.source._use.used,
                    admitted_root.proposal._authorship.source._issuer,
                ),
                runtime,
                current,
            )
        )
        return admitted_root

    def require_returned_root(self, root: object) -> AdmittedBranchRoot:
        if type(root) is not AdmittedBranchRoot or not any(
            root is item for item in self._roots
        ):
            raise FormationAppendRefusal("exact_admitted_root_required")
        snapshot = next(item for item in self._root_snapshots if item[1] is root.condition_root)
        runtime = snapshot[13]
        admission_handoff = snapshot[14]
        try:
            verified_handoff = runtime.require_current_admission(admission_handoff)
        except ValueError as error:
            raise FormationAppendRefusal("admitted_root_changed") from error
        source = root.proposal._authorship.source
        source_snapshot = snapshot[12]
        if (
            root.run_id != snapshot[0]
            or root.condition_root is not snapshot[1]
            or root.proposal is not snapshot[2]
            or root.admission is not snapshot[3]
            or root.head is not snapshot[4]
            or root._issuer is not snapshot[5]
            or proposal_public_semantics(root.proposal) != snapshot[6]
            or admission_public_semantics(root.admission) != snapshot[7]
            or root.proposal._authorship is not snapshot[8]
            or root.proposal._authorship.source is not snapshot[9][0]
            or root.proposal._authorship.representation != snapshot[9][1]
            or root.proposal._authorship.projection is not snapshot[9][2]
            or proposal_public_semantics(root.proposal) != snapshot[9][3]
            or root.proposal._authorship._issuer is not snapshot[9][4]
            or root.admission._decision is not snapshot[10]
            or root.admission._decision.proposal is not snapshot[11][0]
            or root.admission._decision.warrant is not snapshot[11][1]
            or admission_public_semantics(root.admission) != snapshot[11][2]
            or root.admission._decision.scope != snapshot[11][3]
            or root.admission._decision.status != snapshot[11][4]
            or root.admission._decision.trial is not snapshot[11][5]
            or root.admission._decision._issuer is not snapshot[11][6]
            or source is not source_snapshot[0]
            or source.run_id != source_snapshot[1]
            or source.consumed_root is not source_snapshot[2]
            or source.source_consequence is not source_snapshot[3]
            or source.source_consequence.root is not source_snapshot[4]
            or source.source_consequence.coordinate != source_snapshot[5]
            or source.source_consequence.artifact is not source_snapshot[6]
            or source.source_consequence._issuer is not source_snapshot[7]
            or source.source_experience is not source_snapshot[8]
            or source.source_experience.root is not source_snapshot[9]
            or source.source_experience.coordinate != source_snapshot[10]
            or source.source_experience.artifact is not source_snapshot[11]
            or source.source_experience._issuer is not source_snapshot[12]
            or source.condition_head is not source_snapshot[13]
            or source.condition_head.root is not source_snapshot[14]
            or source.condition_head.coordinate != source_snapshot[15]
            or source.condition_head._issuer is not source_snapshot[16]
            or source.public_condition is not source_snapshot[17]
            or source.public_condition.condition != source_snapshot[18]
            or source.public_condition.interpreter != source_snapshot[19]
            or source.public_condition.governor != source_snapshot[20]
            or source.public_condition.influence_policy != source_snapshot[21]
            or source._use is not source_snapshot[22]
            or source._use.source_root is not source_snapshot[23]
            or source._use.source is not source_snapshot[24]
            or source._use.used is not source_snapshot[25]
            or source._issuer is not source_snapshot[26]
            or verified_handoff is not admission_handoff
            or admission_handoff.admission is not root.admission
            or admission_handoff.proposal_handoff.proposal is not root.proposal
        ):
            raise FormationAppendRefusal("admitted_root_changed")
        self._require_batch_root(root.condition_root)
        validate_fixture_proposal(root.proposal)
        validate_fixture_admission(root.admission)
        return root

    def issue_admitted_treatment_batch(self) -> AdmittedTreatmentBatch:
        if self._admitted_batch is not None:
            raise AdmittedTreatmentBatchRefusal("admitted_treatment_batch_already_issued")
        if len(self._roots) != 2:
            raise AdmittedTreatmentBatchRefusal("both_admitted_treatment_roots_required")
        admitted_by_condition = {id(root.condition_root): root for root in self._roots}
        ordered = tuple(admitted_by_condition.get(id(root)) for root in self._batch.roots)
        if (
            len(ordered) != 2
            or any(root is None for root in ordered)
            or ordered[0] is ordered[1]
        ):
            raise AdmittedTreatmentBatchRefusal("admitted_treatment_root_set_mismatch")
        first = self.require_returned_root(ordered[0])
        second = self.require_returned_root(ordered[1])
        verifiers = tuple(
            _AdmittedRootVerifier(
                root,
                next(
                    snapshot[13]
                    for snapshot in self._root_snapshots
                    if snapshot[1] is root.condition_root
                ),
                next(
                    snapshot[14]
                    for snapshot in self._root_snapshots
                    if snapshot[1] is root.condition_root
                ),
            )
            for root in (first, second)
        )
        use = _AdmittedTreatmentBatchUse(verifiers)
        batch = AdmittedTreatmentBatch(
            run_id=first.run_id,
            roots=(first, second),
            _use=use,
            _issuer=self._admitted_batch_issuer,
        )
        use.bind(batch)
        self._admitted_batch = batch
        self._admitted_batch_snapshot = (
            batch.run_id,
            batch.roots,
            batch._use,
            batch._issuer,
        )
        return batch

    def require_admitted_treatment_batch(
        self, batch: object
    ) -> AdmittedTreatmentBatch:
        if (
            type(batch) is not AdmittedTreatmentBatch
            or batch is not self._admitted_batch
            or batch._issuer is not self._admitted_batch_issuer
            or self._admitted_batch_snapshot is None
        ):
            raise AdmittedTreatmentBatchRefusal("exact_admitted_treatment_batch_required")
        snapshot = self._admitted_batch_snapshot
        if (
            batch.run_id != snapshot[0]
            or batch.roots is not snapshot[1]
            or batch._use is not snapshot[2]
            or batch._issuer is not snapshot[3]
            or len(batch.roots) != 2
            or batch.roots[0] is batch.roots[1]
        ):
            raise AdmittedTreatmentBatchRefusal("admitted_treatment_batch_changed")
        for root in batch.roots:
            self.require_returned_root(root)
        return batch

    def open_constraint_controller(self, batch: object):
        from trajectory.replay_constraint import ReplayConstraintAppendController

        current = self.require_admitted_treatment_batch(batch)
        if self._constraint_controller is not None:
            raise AdmittedTreatmentBatchRefusal("constraint_controller_already_registered")
        controller = ReplayConstraintAppendController._from_formation(self, current)
        self._constraint_controller = controller
        self._constraint_controller_snapshot = controller
        return controller

    def resolve_ablation_root(
        self, batch: object, controller: object
    ) -> AdmittedBranchRoot:
        current = self.require_admitted_treatment_batch(batch)
        from trajectory.replay_constraint import ReplayConstraintAppendController

        if (
            type(controller) is not ReplayConstraintAppendController
            or controller is not self._constraint_controller
            or controller is not self._constraint_controller_snapshot
        ):
            raise AdmittedTreatmentBatchRefusal("exact_constraint_controller_required")
        selected = tuple(
            root
            for root in current.roots
            if self._conditions.assignment_label_for_formation(
                root.condition_root, self._issuer
            )
            == "ablation"
        )
        if len(selected) != 1:
            raise AdmittedTreatmentBatchRefusal("exact_ablation_assignment_required")
        return self.require_returned_root(selected[0])

    def foreground_root_verifier(
        self, root: object, constraint_controller: object
    ) -> _AdmittedRootVerifier:
        """Return the retained label-free verifier to the registered next gate."""

        from trajectory.replay_constraint import ReplayConstraintAppendController

        if (
            type(constraint_controller) is not ReplayConstraintAppendController
            or constraint_controller is not self._constraint_controller
            or constraint_controller is not self._constraint_controller_snapshot
        ):
            raise AdmittedTreatmentBatchRefusal("exact_constraint_controller_required")
        current = self.require_returned_root(root)
        verifier = next(
            (
                item
                for item in self._admitted_batch._use._verifiers
                if item.root is current
            ),
            None,
        )
        if verifier is None or verifier.require(current) is not current:
            raise AdmittedTreatmentBatchRefusal("exact_admitted_treatment_root_required")
        return verifier
