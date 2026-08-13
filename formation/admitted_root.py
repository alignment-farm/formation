"""Runtime-owned fixture capabilities for proposal and direct admission.

This module selects no receipt bytes or general lifecycle schema. It produces
only the semantic, current-run capabilities required by ``ADMITTED_ROOT.md``.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import re

from formation.condition_append import (
    GOVERNOR,
    INTERPRETER,
    RuntimeConditionMaterializer,
    treatment_condition,
)
from formation.fixture_prefix import expected_fixture_artifact


PROPOSAL_ORDER = 8
ADMISSION_ORDER = 9
PROPOSAL_EVENT = "candidate_proposed"
ADMISSION_EVENT = "candidate_admitted"
RECORDER = "formation_runtime"
SOURCE_CONSEQUENCE = "D-C-005"
SOURCE_EXPERIENCE = "D-C-006"
STATUS_ELIGIBLE = "eligible"

CANDIDATE_REPRESENTATION = (
    "When committing a derived object whose acceptability depends on the current\n"
    "authoritative source, compare its source revision with the authority revision.\n"
    "Refresh before commitment on mismatch. Do not apply this check when current\n"
    "authority is not part of the object's validity rule. Treat an externally sourced\n"
    "correction showing that revision mismatch was not causal as counterevidence."
)

CLAIMED_APPLICABILITY = (
    "A commitment of a derived object whose acceptability depends on its current "
    "authoritative source"
)
EXPLICIT_NON_APPLICABILITY = (
    "An object whose validity is independent of current authority"
)
EXPECTED_EFFECT = (
    "Compare artifact and authority revisions; refresh before commitment when they differ"
)
COUNTEREVIDENCE = (
    "An externally sourced correction to D-C-005 showing revision mismatch was not causal"
)
ADMITTED_SCOPE = (
    "Commitments of derived objects whose acceptability depends on the current "
    "authoritative source; authority-independent validity is excluded"
)
WARRANT_CHECKS = (
    "source_experience_contains_external_consequence",
    "proposal_cites_consequence_and_declares_practice_change",
    "applicability_excludes_authority_independent_validity",
    "source_consequence_correction_named_as_counterevidence",
)

_SOURCE_ISSUER = object()
_COORDINATE_ISSUER = object()
_RUNTIME_RUN_ISSUER = object()
_AUTHORITY_FACTORY_ISSUER = object()


def _contains_hidden_branch_label(value: str) -> bool:
    lowered = value.lower()
    return any(
        word in lowered for word in ("baseline", "governed", "ablation")
    ) or re.search(r"(^|[^a-z0-9])[bga]([^a-z0-9]|$)", lowered) is not None


class FormationSourceRefusal(ValueError):
    """The runtime cannot derive the fixture formation source."""


class ProposalRefusal(ValueError):
    """The runtime cannot issue or reuse this proposal."""


class AdmissionRefusal(ValueError):
    """The governor cannot issue or reuse this admission."""


class FormationCoordinateRefusal(ValueError):
    """The runtime coordinate capability is unavailable or changed."""


class OpaqueFormationCoordinate:
    """Identity-only coordinate capability with no selected wire encoding."""

    __slots__ = ("_run_id", "_sequence", "_issuer")

    def __init__(self, run_id: str, sequence: int) -> None:
        self._run_id = run_id
        self._sequence = sequence
        self._issuer = _COORDINATE_ISSUER


@dataclass(frozen=True)
class RetainedReceipt:
    root: object
    coordinate: str
    artifact: bytes
    _issuer: object


@dataclass(frozen=True)
class RetainedConditionHead:
    root: object
    coordinate: str
    _issuer: object


@dataclass(frozen=True)
class CandidateProjection:
    source_experience: str
    source_consequence: str
    author: str
    claimed_applicability: str
    explicit_non_applicability: str
    expected_practice_effect: str
    counterevidence: str
    expiry: None


@dataclass(frozen=True)
class AdmissionWarrant:
    source_consequence: str
    satisfied_checks: tuple[str, ...]


def _projection_values(projection: CandidateProjection) -> tuple[object, ...]:
    return (
        projection.source_experience,
        projection.source_consequence,
        projection.author,
        projection.claimed_applicability,
        projection.explicit_non_applicability,
        projection.expected_practice_effect,
        projection.counterevidence,
        projection.expiry,
    )


def _warrant_values(warrant: AdmissionWarrant) -> tuple[object, ...]:
    return (warrant.source_consequence, tuple(warrant.satisfied_checks))


class _FormationSourceUse:
    def __init__(self, source_root: object) -> None:
        self.source_root = source_root
        self.source: FixtureFormationSource | None = None
        self.used = False

    def bind(self, source: FixtureFormationSource) -> None:
        if self.source is not None:
            raise FormationSourceRefusal("formation_source_already_bound")
        self.source = source

    def consume(self, source: object) -> FixtureFormationSource:
        if self.used:
            raise FormationSourceRefusal("formation_source_already_consumed")
        if type(source) is not FixtureFormationSource or source is not self.source:
            raise FormationSourceRefusal("exact_formation_source_required")
        if source._issuer is not _SOURCE_ISSUER or source.consumed_root is not self.source_root:
            raise FormationSourceRefusal("forged_or_wrong_root_formation_source")
        self.used = True
        return source


@dataclass(frozen=True)
class FixtureFormationSource:
    run_id: str
    consumed_root: object
    source_consequence: RetainedReceipt
    source_experience: RetainedReceipt
    condition_head: RetainedConditionHead
    public_condition: object
    _use: _FormationSourceUse
    _issuer: object


@dataclass(frozen=True)
class InterpreterAuthorship:
    source: FixtureFormationSource
    representation: str
    projection: CandidateProjection
    _issuer: object


@dataclass(frozen=True)
class GovernorDecision:
    proposal: ProposedCandidate
    warrant: AdmissionWarrant
    scope: str
    status: str
    trial: None
    _issuer: object


@dataclass(frozen=True)
class ProposedCandidate:
    run_id: str
    consumed_root: object
    coordinate: OpaqueFormationCoordinate
    order: int
    event: str
    author: str
    recorder: str
    parents: frozenset[object]
    representation: str
    projection: CandidateProjection
    _authorship: InterpreterAuthorship
    _issuer: object


@dataclass(frozen=True)
class ProposalHandoff:
    run_id: str
    source: FixtureFormationSource
    proposal: ProposedCandidate
    _issuer: object


@dataclass(frozen=True)
class AdmittedCandidate:
    run_id: str
    consumed_root: object
    proposal: ProposedCandidate
    coordinate: OpaqueFormationCoordinate
    order: int
    event: str
    decision_authority: str
    recorder: str
    parents: frozenset[object]
    warrant: AdmissionWarrant
    scope: str
    status: str
    trial: None
    _decision: GovernorDecision
    _issuer: object


@dataclass(frozen=True)
class AdmissionHandoff:
    run_id: str
    proposal_handoff: ProposalHandoff
    admission: AdmittedCandidate
    _issuer: object


def proposal_public_semantics(proposal: ProposedCandidate) -> tuple[object, ...]:
    return (
        proposal.order,
        proposal.event,
        proposal.author,
        proposal.recorder,
        proposal.representation,
        _projection_values(proposal.projection),
    )


def admission_public_semantics(admission: AdmittedCandidate) -> tuple[object, ...]:
    return (
        admission.order,
        admission.event,
        admission.decision_authority,
        admission.recorder,
        proposal_public_semantics(admission.proposal),
        _warrant_values(admission.warrant),
        admission.scope,
        admission.status,
        admission.trial,
    )


def _read_retained_receipts(
    source: FixtureFormationSource,
) -> tuple[dict[str, object], dict[str, object]]:
    try:
        consequence = json.loads(source.source_consequence.artifact)
        experience = json.loads(source.source_experience.artifact)
    except (TypeError, ValueError, UnicodeError) as error:
        raise FormationSourceRefusal("invalid_retained_formation_receipts") from error
    if (
        not isinstance(consequence, dict)
        or consequence.get("coordinate") != SOURCE_CONSEQUENCE
        or consequence.get("event") != "consequence_observed"
        or consequence.get("authority") != "environment"
        or not isinstance(consequence.get("payload"), dict)
        or consequence["payload"].get("outcome") != "rejected"
        or consequence["payload"].get("reason") != "stale_dependency"
        or consequence["payload"].get("observed_rule")
        != "artifact_revision_must_equal_authority_revision"
        or not isinstance(experience, dict)
        or experience.get("coordinate") != SOURCE_EXPERIENCE
        or experience.get("event") != "experience_closed"
        or not isinstance(experience.get("payload"), dict)
        or experience["payload"].get("consequence") != "K-C-001"
        or experience["payload"].get("applicability_claim") is not None
    ):
        raise FormationSourceRefusal("invalid_retained_formation_receipts")
    return consequence, experience


class _FixtureInterpreter:
    """Exact runtime interpreter that originates one proposal meaning."""

    def __init__(self, root: object, issuer: object) -> None:
        if issuer is not _AUTHORITY_FACTORY_ISSUER:
            raise ProposalRefusal("runtime_interpreter_factory_required")
        self._root = root
        self._issuer = object()
        self._current: InterpreterAuthorship | None = None
        self._snapshot: tuple[object, ...] | None = None

    def interpret(self, source: object) -> InterpreterAuthorship:
        if self._current is not None:
            raise ProposalRefusal("interpreter_already_invoked")
        if (
            type(source) is not FixtureFormationSource
            or source.consumed_root is not self._root
        ):
            raise ProposalRefusal("exact_interpreter_source_required")
        source._use.consume(source)
        _read_retained_receipts(source)
        projection = CandidateProjection(
            source.source_experience.coordinate,
            source.source_consequence.coordinate,
            INTERPRETER,
            CLAIMED_APPLICABILITY,
            EXPLICIT_NON_APPLICABILITY,
            EXPECTED_EFFECT,
            COUNTEREVIDENCE,
            None,
        )
        authorship = InterpreterAuthorship(
            source=source,
            representation=CANDIDATE_REPRESENTATION,
            projection=projection,
            _issuer=self._issuer,
        )
        self._current = authorship
        self._snapshot = (
            authorship.source,
            authorship.representation,
            _projection_values(authorship.projection),
            authorship._issuer,
        )
        return authorship

    def require_current(self, authorship: object) -> InterpreterAuthorship:
        if (
            type(authorship) is not InterpreterAuthorship
            or authorship is not self._current
            or self._snapshot is None
            or authorship.source is not self._snapshot[0]
            or authorship.representation != self._snapshot[1]
            or _projection_values(authorship.projection) != self._snapshot[2]
            or authorship._issuer is not self._snapshot[3]
        ):
            raise ProposalRefusal("interpreter_authorship_changed_or_forged")
        _read_retained_receipts(authorship.source)
        return authorship


class _ConsequenceWarrantGovernor:
    """Exact runtime governor that originates one direct-admission decision."""

    def __init__(self, root: object, issuer: object) -> None:
        if issuer is not _AUTHORITY_FACTORY_ISSUER:
            raise AdmissionRefusal("runtime_governor_factory_required")
        self._root = root
        self._issuer = object()
        self._current: GovernorDecision | None = None
        self._snapshot: tuple[object, ...] | None = None

    def decide(
        self,
        source: FixtureFormationSource,
        proposal: ProposedCandidate,
    ) -> GovernorDecision:
        if self._current is not None:
            raise AdmissionRefusal("governor_already_invoked")
        if (
            source.consumed_root is not self._root
            or proposal.consumed_root is not self._root
        ):
            raise AdmissionRefusal("governor_root_mismatch")
        consequence, experience = _read_retained_receipts(source)
        projection = proposal.projection
        checks = (
            consequence.get("authority") == "environment"
            and experience["payload"].get("consequence")
            == consequence["payload"].get("consequence"),
            projection.source_consequence == source.source_consequence.coordinate
            and projection.expected_practice_effect == EXPECTED_EFFECT,
            projection.explicit_non_applicability == EXPLICIT_NON_APPLICABILITY,
            projection.counterevidence == COUNTEREVIDENCE,
        )
        if checks != (True, True, True, True):
            raise AdmissionRefusal("governor_warrant_not_satisfied")
        decision = GovernorDecision(
            proposal=proposal,
            warrant=AdmissionWarrant(SOURCE_CONSEQUENCE, WARRANT_CHECKS),
            scope=ADMITTED_SCOPE,
            status=STATUS_ELIGIBLE,
            trial=None,
            _issuer=self._issuer,
        )
        self._current = decision
        self._snapshot = (
            decision.proposal,
            _warrant_values(decision.warrant),
            decision.scope,
            decision.status,
            decision.trial,
            decision._issuer,
        )
        return decision

    def require_current(self, decision: object) -> GovernorDecision:
        if (
            type(decision) is not GovernorDecision
            or decision is not self._current
            or self._snapshot is None
            or decision.proposal is not self._snapshot[0]
            or _warrant_values(decision.warrant) != self._snapshot[1]
            or decision.scope != self._snapshot[2]
            or decision.status != self._snapshot[3]
            or decision.trial is not self._snapshot[4]
            or decision._issuer is not self._snapshot[5]
        ):
            raise AdmissionRefusal("governor_decision_changed_or_forged")
        return decision


class RuntimeFormationRun:
    """Runtime-owned label-blind formation over the two treatment roots."""

    def __init__(self, run_id: str, treatment_batch: object) -> None:
        if not isinstance(run_id, str) or not run_id:
            raise FormationSourceRefusal("invalid_run_id")
        if _contains_hidden_branch_label(run_id):
            raise FormationSourceRefusal("label_bearing_run_id")
        from trajectory.fixture_condition import TreatmentRootBatch

        if type(treatment_batch) is not TreatmentRootBatch:
            raise FormationSourceRefusal("exact_treatment_root_batch_required")
        if treatment_batch.run_id != run_id:
            raise FormationSourceRefusal("treatment_root_batch_run_mismatch")
        roots = treatment_batch._use.consume(treatment_batch)
        if len(roots) != 2 or roots[0] is roots[1]:
            raise FormationSourceRefusal("exact_two_treatment_roots_required")
        self.run_id = run_id
        self._issuer = _RUNTIME_RUN_ISSUER
        self._slots = tuple(
            (
                root,
                OpaqueFormationCoordinate(run_id, index * 2 + 1),
                OpaqueFormationCoordinate(run_id, index * 2 + 2),
            )
            for index, root in enumerate(roots)
        )
        self._opened_roots: list[object] = []

    def materializer(self, root: object) -> RuntimeFormationMaterializer:
        slot = next((item for item in self._slots if item[0] is root), None)
        if slot is None:
            raise FormationSourceRefusal("exact_treatment_root_required")
        if any(root is opened for opened in self._opened_roots):
            raise FormationSourceRefusal("formation_materializer_already_opened")
        self._opened_roots.append(root)
        return RuntimeFormationMaterializer(self, *slot, self._issuer)


class RuntimeFormationMaterializer:
    """One-shot interpreter and governor owner for one treatment root."""

    def __init__(
        self,
        run: RuntimeFormationRun,
        root: object,
        proposal_coordinate: OpaqueFormationCoordinate,
        admission_coordinate: OpaqueFormationCoordinate,
        issuer: object,
    ) -> None:
        if type(run) is not RuntimeFormationRun or issuer is not _RUNTIME_RUN_ISSUER:
            raise FormationSourceRefusal("runtime_formation_factory_required")
        self.run_id = run.run_id
        self._root = root
        self._proposal_coordinate = proposal_coordinate
        self._admission_coordinate = admission_coordinate
        prefix_root = getattr(root, "prefix_root", None)
        prefix_binding = getattr(prefix_root, "binding", None)
        condition_binding = getattr(root, "condition_binding", None)
        self._reserved = (
            root,
            prefix_root,
            getattr(prefix_root, "artifact", None),
            (
                getattr(prefix_binding, "materializer", None),
                getattr(prefix_binding, "identity_contract", None),
                getattr(prefix_binding, "algorithm", None),
                getattr(prefix_binding, "digest", None),
                getattr(prefix_binding, "byte_length", None),
            ),
            getattr(root, "condition_segment", None),
            getattr(root, "head", None),
            (
                getattr(condition_binding, "materializer", None),
                getattr(condition_binding, "identity_contract", None),
                getattr(condition_binding, "algorithm", None),
                getattr(condition_binding, "digest", None),
                getattr(condition_binding, "byte_length", None),
            ),
            proposal_coordinate,
            proposal_coordinate._run_id,
            proposal_coordinate._sequence,
            admission_coordinate,
            admission_coordinate._run_id,
            admission_coordinate._sequence,
        )
        self._interpreter = _FixtureInterpreter(root, _AUTHORITY_FACTORY_ISSUER)
        self._governor = _ConsequenceWarrantGovernor(
            root, _AUTHORITY_FACTORY_ISSUER
        )
        self._issuer = object()
        self._source: FixtureFormationSource | None = None
        self._source_snapshot: tuple[object, ...] | None = None
        self._proposal_handoff: ProposalHandoff | None = None
        self._proposal_snapshot: tuple[object, ...] | None = None
        self._admission_handoff: AdmissionHandoff | None = None
        self._admission_snapshot: tuple[object, ...] | None = None
        self._proposal_consumed = False

    def _require_reservation(self) -> None:
        from trajectory.fixture_condition import compute_condition_binding
        from trajectory.fixture_fork import compute_binding

        prefix_binding = getattr(self._reserved[1], "binding", None)
        condition_binding = getattr(self._root, "condition_binding", None)
        prefix_binding_values = (
            getattr(prefix_binding, "materializer", None),
            getattr(prefix_binding, "identity_contract", None),
            getattr(prefix_binding, "algorithm", None),
            getattr(prefix_binding, "digest", None),
            getattr(prefix_binding, "byte_length", None),
        )
        condition_binding_values = (
            getattr(condition_binding, "materializer", None),
            getattr(condition_binding, "identity_contract", None),
            getattr(condition_binding, "algorithm", None),
            getattr(condition_binding, "digest", None),
            getattr(condition_binding, "byte_length", None),
        )
        if (
            self._root is not self._reserved[0]
            or getattr(self._root, "prefix_root", None) is not self._reserved[1]
            or getattr(self._reserved[1], "artifact", None) is not self._reserved[2]
            or prefix_binding_values != self._reserved[3]
            or getattr(self._root, "condition_segment", None) is not self._reserved[4]
            or getattr(self._root, "head", None) != self._reserved[5]
            or condition_binding_values != self._reserved[6]
            or compute_binding(self._reserved[2]) != prefix_binding
            or compute_condition_binding(self._reserved[4]) != condition_binding
            or self._proposal_coordinate is not self._reserved[7]
            or self._admission_coordinate is not self._reserved[10]
            or self._proposal_coordinate._issuer is not _COORDINATE_ISSUER
            or self._admission_coordinate._issuer is not _COORDINATE_ISSUER
            or self._proposal_coordinate._run_id != self._reserved[8]
            or self._proposal_coordinate._sequence != self._reserved[9]
            or self._admission_coordinate._run_id != self._reserved[11]
            or self._admission_coordinate._sequence != self._reserved[12]
        ):
            raise FormationCoordinateRefusal("formation_reservation_changed")

    def adapt_source(self) -> FixtureFormationSource:
        if self._source is not None:
            raise FormationSourceRefusal("formation_source_already_issued")
        self._require_reservation()
        root = self._root
        prefix_root = getattr(root, "prefix_root", None)
        prefix_artifact = getattr(prefix_root, "artifact", None)
        if type(prefix_artifact) is not bytes or prefix_artifact != expected_fixture_artifact():
            raise FormationSourceRefusal("invalid_retained_prefix")
        expected_condition = RuntimeConditionMaterializer._encode(
            getattr(root, "head", ""), treatment_condition()
        )
        if getattr(root, "condition_segment", None) != expected_condition:
            raise FormationSourceRefusal("invalid_treatment_condition_root")
        if getattr(prefix_root, "run_id", None) != self.run_id:
            raise FormationSourceRefusal("formation_root_run_mismatch")
        lines = prefix_artifact.splitlines(keepends=True)
        if len(lines) != 6:
            raise FormationSourceRefusal("invalid_retained_prefix")
        receipt_issuer = object()
        consequence = RetainedReceipt(root, SOURCE_CONSEQUENCE, lines[4], receipt_issuer)
        experience = RetainedReceipt(root, SOURCE_EXPERIENCE, lines[5], receipt_issuer)
        condition_head = RetainedConditionHead(root, root.head, receipt_issuer)
        use = _FormationSourceUse(root)
        source = FixtureFormationSource(
            run_id=self.run_id,
            consumed_root=root,
            source_consequence=consequence,
            source_experience=experience,
            condition_head=condition_head,
            public_condition=treatment_condition(),
            _use=use,
            _issuer=_SOURCE_ISSUER,
        )
        use.bind(source)
        self._source = source
        self._source_snapshot = (
            source.run_id,
            source.consumed_root,
            source.source_consequence,
            source.source_experience,
            source.condition_head,
            source.public_condition,
            source._use,
            source._issuer,
            (
                consequence.root,
                consequence.coordinate,
                consequence.artifact,
                consequence._issuer,
            ),
            (
                experience.root,
                experience.coordinate,
                experience.artifact,
                experience._issuer,
            ),
            (
                condition_head.root,
                condition_head.coordinate,
                condition_head._issuer,
            ),
        )
        return source

    def _require_source(self, source: object) -> FixtureFormationSource:
        if source is not self._source or self._source_snapshot is None:
            raise FormationSourceRefusal("exact_formation_source_required")
        snapshot = self._source_snapshot
        if (
            source.run_id != snapshot[0]
            or source.consumed_root is not snapshot[1]
            or source.source_consequence is not snapshot[2]
            or source.source_experience is not snapshot[3]
            or source.condition_head is not snapshot[4]
            or source.public_condition is not snapshot[5]
            or source._use is not snapshot[6]
            or source._issuer is not snapshot[7]
            or source.source_consequence.root is not snapshot[8][0]
            or source.source_consequence.coordinate != snapshot[8][1]
            or source.source_consequence.artifact is not snapshot[8][2]
            or source.source_consequence._issuer is not snapshot[8][3]
            or source.source_experience.root is not snapshot[9][0]
            or source.source_experience.coordinate != snapshot[9][1]
            or source.source_experience.artifact is not snapshot[9][2]
            or source.source_experience._issuer is not snapshot[9][3]
            or source.condition_head.root is not snapshot[10][0]
            or source.condition_head.coordinate != snapshot[10][1]
            or source.condition_head._issuer is not snapshot[10][2]
        ):
            raise FormationSourceRefusal("formation_source_changed")
        return source

    def propose(self, source: object) -> ProposalHandoff:
        if self._proposal_handoff is not None:
            raise ProposalRefusal("proposal_already_issued")
        self._require_reservation()
        current = self._require_source(source)
        if (
            current.source_consequence.coordinate != SOURCE_CONSEQUENCE
            or current.source_experience.coordinate != SOURCE_EXPERIENCE
            or current.source_consequence.root is not self._root
            or current.source_experience.root is not self._root
        ):
            raise FormationSourceRefusal("formation_source_receipts_changed")
        authorship = self._interpreter.interpret(current)
        proposal = ProposedCandidate(
            run_id=self.run_id,
            consumed_root=self._root,
            coordinate=self._proposal_coordinate,
            order=PROPOSAL_ORDER,
            event=PROPOSAL_EVENT,
            author=INTERPRETER,
            recorder=RECORDER,
            parents=frozenset(
                (
                    current.source_consequence,
                    current.source_experience,
                    current.condition_head,
                )
            ),
            representation=authorship.representation,
            projection=authorship.projection,
            _authorship=authorship,
            _issuer=self._issuer,
        )
        handoff = ProposalHandoff(self.run_id, current, proposal, self._issuer)
        self._proposal_handoff = handoff
        self._proposal_snapshot = (
            handoff.run_id,
            handoff.source,
            handoff.proposal,
            proposal.run_id,
            proposal.consumed_root,
            proposal.coordinate,
            proposal.order,
            proposal.event,
            proposal.author,
            proposal.recorder,
            proposal.parents,
            proposal.representation,
            proposal.projection,
            _projection_values(proposal.projection),
            proposal._authorship,
            proposal._issuer,
            handoff._issuer,
        )
        return handoff

    def require_current_proposal(self, handoff: object) -> ProposalHandoff:
        self._require_reservation()
        if type(handoff) is not ProposalHandoff or handoff is not self._proposal_handoff:
            raise ProposalRefusal("exact_current_proposal_handoff_required")
        if self._proposal_snapshot is None:
            raise ProposalRefusal("missing_proposal_snapshot")
        proposal = handoff.proposal
        self._require_source(handoff.source)
        self._interpreter.require_current(proposal._authorship)
        if proposal._authorship.source is not handoff.source:
            raise ProposalRefusal("proposal_authorship_source_mismatch")
        snapshot = self._proposal_snapshot
        values = (
            handoff.run_id,
            handoff.source,
            handoff.proposal,
            proposal.run_id,
            proposal.consumed_root,
            proposal.coordinate,
            proposal.order,
            proposal.event,
            proposal.author,
            proposal.recorder,
            proposal.parents,
            proposal.representation,
            proposal.projection,
            _projection_values(proposal.projection),
            proposal._authorship,
            proposal._issuer,
            handoff._issuer,
        )
        if any(
            value is not expected
            for index, (value, expected) in enumerate(zip(values, snapshot, strict=True))
            if index in (1, 2, 4, 5, 10, 12, 14, 15, 16)
        ) or any(
            value != expected
            for index, (value, expected) in enumerate(zip(values, snapshot, strict=True))
            if index not in (1, 2, 4, 5, 10, 12, 14, 15, 16)
        ):
            raise ProposalRefusal("proposal_handoff_changed")
        return handoff

    def admit(self, proposal_handoff: object) -> AdmissionHandoff:
        if self._admission_handoff is not None or self._proposal_consumed:
            raise AdmissionRefusal("proposal_already_admitted_or_admission_issued")
        self._require_reservation()
        current = self.require_current_proposal(proposal_handoff)
        proposal = current.proposal
        if proposal.consumed_root is not self._root:
            raise AdmissionRefusal("proposal_root_mismatch")
        decision = self._governor.decide(current.source, proposal)
        self._proposal_consumed = True
        admission = AdmittedCandidate(
            run_id=self.run_id,
            consumed_root=self._root,
            proposal=proposal,
            coordinate=self._admission_coordinate,
            order=ADMISSION_ORDER,
            event=ADMISSION_EVENT,
            decision_authority=GOVERNOR,
            recorder=RECORDER,
            parents=frozenset(
                (
                    current.source.source_consequence,
                    current.source.condition_head,
                    proposal.coordinate,
                )
            ),
            warrant=decision.warrant,
            scope=decision.scope,
            status=decision.status,
            trial=decision.trial,
            _decision=decision,
            _issuer=self._issuer,
        )
        handoff = AdmissionHandoff(self.run_id, current, admission, self._issuer)
        self._admission_handoff = handoff
        self._admission_snapshot = (
            handoff.run_id,
            handoff.proposal_handoff,
            handoff.admission,
            admission.run_id,
            admission.consumed_root,
            admission.proposal,
            admission.coordinate,
            admission.order,
            admission.event,
            admission.decision_authority,
            admission.recorder,
            admission.parents,
            admission.warrant,
            _warrant_values(admission.warrant),
            admission.scope,
            admission.status,
            admission.trial,
            admission._decision,
            admission._issuer,
            handoff._issuer,
        )
        return handoff

    def require_current_admission(self, handoff: object) -> AdmissionHandoff:
        self._require_reservation()
        if type(handoff) is not AdmissionHandoff or handoff is not self._admission_handoff:
            raise AdmissionRefusal("exact_current_admission_handoff_required")
        if self._admission_snapshot is None:
            raise AdmissionRefusal("missing_admission_snapshot")
        admission = handoff.admission
        proposal_handoff = self.require_current_proposal(handoff.proposal_handoff)
        if admission.proposal is not proposal_handoff.proposal:
            raise AdmissionRefusal("admission_proposal_mismatch")
        self._governor.require_current(admission._decision)
        if admission._decision.proposal is not admission.proposal:
            raise AdmissionRefusal("admission_decision_proposal_mismatch")
        values = (
            handoff.run_id,
            handoff.proposal_handoff,
            handoff.admission,
            admission.run_id,
            admission.consumed_root,
            admission.proposal,
            admission.coordinate,
            admission.order,
            admission.event,
            admission.decision_authority,
            admission.recorder,
            admission.parents,
            admission.warrant,
            _warrant_values(admission.warrant),
            admission.scope,
            admission.status,
            admission.trial,
            admission._decision,
            admission._issuer,
            handoff._issuer,
        )
        snapshot = self._admission_snapshot
        identity_indexes = (1, 2, 4, 5, 6, 11, 12, 16, 17, 18, 19)
        if any(
            value is not expected
            for index, (value, expected) in enumerate(zip(values, snapshot, strict=True))
            if index in identity_indexes
        ) or any(
            value != expected
            for index, (value, expected) in enumerate(zip(values, snapshot, strict=True))
            if index not in identity_indexes
        ):
            raise AdmissionRefusal("admission_handoff_changed")
        return handoff
