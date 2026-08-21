"""Runtime-governed authorization for a costly diagnostic encounter."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json

from micro_environment import knowledge_cost_interaction as domain


POLICY_VERSION = "exact-public-alphabet-coverage-v1"
RUNTIME_GOVERNOR = "formation_runtime_governor"
AUTHORIZE = "authorize_diagnostic"
WITHHOLD = "withhold_diagnostic"
COMPLETE_COVERAGE = "complete_exact_coverage"
INCOMPLETE_COVERAGE = "incomplete_exact_coverage"


class DiagnosticPolicyRefusal(ValueError):
    """The declared diagnostic policy cannot decide from these inputs."""


def _text(value: object, refusal: str) -> str:
    if type(value) is not str or not value:
        raise DiagnosticPolicyRefusal(refusal)
    return value


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode()


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


@dataclass(frozen=True, slots=True)
class AdmittedSignalRecord:
    record_id: str
    diagnostic_signal: str
    observed_task_slot: str
    admission_id: str

    def __post_init__(self) -> None:
        _text(self.record_id, "record_id_must_be_text")
        _text(self.diagnostic_signal, "diagnostic_signal_must_be_text")
        if self.observed_task_slot not in domain.SLOTS:
            raise DiagnosticPolicyRefusal("unknown_observed_task_slot")
        _text(self.admission_id, "admission_id_must_be_text")


@dataclass(frozen=True, slots=True)
class DiagnosticAuthorization:
    authority: str
    policy_version: str
    disposition: str
    reason: str
    device: str
    diagnostic_control: str
    diagnostic_cost: str
    diagnostic_alphabet: tuple[str, str]
    public_state_sha256: str
    considered_records_sha256: str
    considered_record_ids: tuple[str, ...]
    exact_matches: tuple[tuple[str, str], ...]
    missing_signals: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SelectedSignalRecord:
    authority: str
    policy_version: str
    authorization_sha256: str
    observed_signal: str
    record: AdmittedSignalRecord


def _require_initial_state(state: object) -> domain.KnowledgeCostState:
    if type(state) is not domain.KnowledgeCostState:
        raise DiagnosticPolicyRefusal("exact_knowledge_cost_state_required")
    if (
        state.phase != domain.FIRST_ACTION
        or state.task_status != domain.INTACT
        or state.observed_signal is not None
        or state.service_window != domain.AVAILABLE
    ):
        raise DiagnosticPolicyRefusal("initial_public_state_required")
    return state


def _canonical_records(
    records: object,
) -> tuple[AdmittedSignalRecord, ...]:
    if type(records) is not tuple or any(
        type(record) is not AdmittedSignalRecord for record in records
    ):
        raise DiagnosticPolicyRefusal("exact_admitted_record_tuple_required")
    ordered = tuple(sorted(records, key=lambda record: record.record_id))
    if len({record.record_id for record in ordered}) != len(ordered):
        raise DiagnosticPolicyRefusal("record_ids_must_be_unique")
    if len({record.admission_id for record in ordered}) != len(ordered):
        raise DiagnosticPolicyRefusal("admission_ids_must_be_unique")
    return ordered


def public_state_value(state: object) -> dict[str, object]:
    exact = _require_initial_state(state)
    return {
        "device": exact.device,
        "diagnostic_alphabet": list(exact.diagnostic_alphabet),
        "diagnostic_control": exact.diagnostic_control,
        "diagnostic_cost": exact.diagnostic_cost,
        "episode_phase": exact.phase,
        "service_window": exact.service_window,
        "task_controls": list(exact.task_controls),
        "task_status": exact.task_status,
    }


def record_set_value(records: object) -> list[dict[str, str]]:
    return [asdict(record) for record in _canonical_records(records)]


def decide_diagnostic(
    state: object, records: object
) -> DiagnosticAuthorization:
    exact_state = _require_initial_state(state)
    exact_records = _canonical_records(records)
    matches: list[tuple[str, str]] = []
    missing: list[str] = []
    for signal in exact_state.diagnostic_alphabet:
        matching = tuple(
            record for record in exact_records if record.diagnostic_signal == signal
        )
        if len(matching) > 1:
            raise DiagnosticPolicyRefusal("ambiguous_signal_coverage")
        if matching:
            matches.append((signal, matching[0].record_id))
        else:
            missing.append(signal)

    complete = not missing
    return DiagnosticAuthorization(
        authority=RUNTIME_GOVERNOR,
        policy_version=POLICY_VERSION,
        disposition=AUTHORIZE if complete else WITHHOLD,
        reason=COMPLETE_COVERAGE if complete else INCOMPLETE_COVERAGE,
        device=exact_state.device,
        diagnostic_control=exact_state.diagnostic_control,
        diagnostic_cost=exact_state.diagnostic_cost,
        diagnostic_alphabet=exact_state.diagnostic_alphabet,
        public_state_sha256=_sha256(public_state_value(exact_state)),
        considered_records_sha256=_sha256(record_set_value(exact_records)),
        considered_record_ids=tuple(record.record_id for record in exact_records),
        exact_matches=tuple(matches),
        missing_signals=tuple(missing),
    )


def _require_current_authorization(
    authorization: object,
    state: object,
    records: object,
) -> DiagnosticAuthorization:
    if type(authorization) is not DiagnosticAuthorization:
        raise DiagnosticPolicyRefusal("exact_diagnostic_authorization_required")
    current = decide_diagnostic(state, records)
    if authorization != current:
        raise DiagnosticPolicyRefusal("stale_or_mismatched_authorization")
    return authorization


def authorized_diagnostic_control(
    authorization: object,
    state: object,
    records: object,
) -> str | None:
    exact = _require_current_authorization(authorization, state, records)
    if exact.disposition == WITHHOLD:
        return None
    if exact.disposition != AUTHORIZE:
        raise DiagnosticPolicyRefusal("unknown_authorization_disposition")
    return exact.diagnostic_control


def select_observed_record(
    authorization: object,
    state: object,
    records: object,
    diagnostic_result: object,
) -> SelectedSignalRecord:
    exact = _require_current_authorization(authorization, state, records)
    exact_records = _canonical_records(records)
    if exact.disposition != AUTHORIZE:
        raise DiagnosticPolicyRefusal("diagnostic_was_not_authorized")
    if (
        type(diagnostic_result) is not domain.KnowledgeCostResult
        or diagnostic_result.action != exact.diagnostic_control
        or diagnostic_result.disposition != domain.APPLIED
        or not diagnostic_result.information_acquired
        or diagnostic_result.diagnostic_signal not in exact.diagnostic_alphabet
        or diagnostic_result.phase_after != domain.POST_DIAGNOSTIC
    ):
        raise DiagnosticPolicyRefusal("exact_diagnostic_result_required")
    matches = tuple(
        record
        for record in exact_records
        if record.diagnostic_signal == diagnostic_result.diagnostic_signal
    )
    if len(matches) != 1:
        raise DiagnosticPolicyRefusal("authorized_signal_record_missing")
    return SelectedSignalRecord(
        authority=RUNTIME_GOVERNOR,
        policy_version=POLICY_VERSION,
        authorization_sha256=_sha256(asdict(exact)),
        observed_signal=diagnostic_result.diagnostic_signal,
        record=matches[0],
    )
