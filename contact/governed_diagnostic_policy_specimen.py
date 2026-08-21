"""Conform record-governed opening of a costly diagnostic encounter."""

from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable

from contact import distributional_developmental_comparison as base
from contact import knowledge_cost_interaction_specimen as parent
from contact import self_directed_probe_contact as prior
from formation import diagnostic_policy as policy
from micro_environment import knowledge_cost_interaction as domain


PROTOCOL_VERSION = "governed-diagnostic-policy-specimen-v1"
SPEC_PATH = (
    Path(__file__).parents[1]
    / "docs"
    / "GOVERNED_DIAGNOSTIC_ENCOUNTER_POLICY.md"
)

LEARNED = "learned_covered"
SUPPLIED = "supplied_covered"
REVERSED = "reversed_covered"
REMOVAL = "removal_covered"
UNCOVERED = "learned_uncovered"
CONDITIONS = (LEARNED, SUPPLIED, REVERSED, REMOVAL, UNCOVERED)


class GovernedDiagnosticSpecimenRefusal(ValueError):
    pass


def records(
    prefix: str,
    source_records: tuple[dict[str, str], ...],
    *,
    reversed_slots: bool = False,
) -> tuple[policy.AdmittedSignalRecord, ...]:
    slots = tuple(record["valid_task_slot"] for record in source_records)
    if reversed_slots:
        slots = tuple(reversed(slots))
    return tuple(
        policy.AdmittedSignalRecord(
            record_id=f"record-{record['diagnostic_signal']}",
            diagnostic_signal=record["diagnostic_signal"],
            observed_task_slot=slot,
            admission_id=f"{prefix}-{index}",
        )
        for index, (record, slot) in enumerate(zip(source_records, slots, strict=True))
    )


RETAINED_SOURCE_RECORDS = tuple(
    prior.checked_learned_records(prior.load_predecessor_packet())
)
LEARNED_RECORDS = records("learned-admission", RETAINED_SOURCE_RECORDS)
SUPPLIED_RECORDS = records("supplied-admission", RETAINED_SOURCE_RECORDS)
REVERSED_RECORDS = records(
    "reversed-admission", RETAINED_SOURCE_RECORDS, reversed_slots=True
)
REMOVAL_RECORDS: tuple[policy.AdmittedSignalRecord, ...] = ()

CONDITION_INPUTS = {
    LEARNED: (parent.STATES[(parent.COVERED, domain.COSTLY)], LEARNED_RECORDS),
    SUPPLIED: (parent.STATES[(parent.COVERED, domain.COSTLY)], SUPPLIED_RECORDS),
    REVERSED: (parent.STATES[(parent.COVERED, domain.COSTLY)], REVERSED_RECORDS),
    REMOVAL: (parent.STATES[(parent.COVERED, domain.COSTLY)], REMOVAL_RECORDS),
    UNCOVERED: (parent.STATES[(parent.UNCOVERED, domain.COSTLY)], LEARNED_RECORDS),
}


def _capture(call: Callable[[], Any]) -> str | None:
    try:
        call()
    except (policy.DiagnosticPolicyRefusal, domain.KnowledgeCostRefusal) as exc:
        return str(exc)
    return None


def _task_control(
    state: domain.KnowledgeCostState,
    selected: policy.SelectedSignalRecord,
) -> str:
    return state.task_controls[
        0 if selected.record.observed_task_slot == domain.FIRST_SLOT else 1
    ]


def _decision_value(decision: policy.DiagnosticAuthorization) -> dict[str, Any]:
    return asdict(decision)


def _handoff_value(handoff: policy.SelectedSignalRecord) -> dict[str, Any]:
    return asdict(handoff)


def refusal_witnesses() -> dict[str, str | None]:
    state, exact_records = CONDITION_INPUTS[LEARNED]
    authorization = policy.decide_diagnostic(state, exact_records)
    profile = parent.PROFILES[(parent.COVERED, parent.PROFILE_0)]
    diagnostic = domain.apply_action(
        state, profile, state.diagnostic_control
    )
    duplicate_signal = (
        *exact_records,
        policy.AdmittedSignalRecord(
            "record-steady-duplicate",
            parent.COVERED_ALPHABET[0],
            domain.SECOND_SLOT,
            "duplicate-admission",
        ),
    )
    post_state = diagnostic.state_after
    task_result = domain.apply_action(post_state, profile, state.task_controls[0])
    return {
        "state_type": _capture(lambda: policy.decide_diagnostic(asdict(state), exact_records)),
        "record_container": _capture(lambda: policy.decide_diagnostic(state, list(exact_records))),
        "duplicate_record_id": _capture(
            lambda: policy.decide_diagnostic(state, (exact_records[0], exact_records[0]))
        ),
        "ambiguous_signal": _capture(lambda: policy.decide_diagnostic(state, duplicate_signal)),
        "noninitial_state": _capture(lambda: policy.decide_diagnostic(post_state, exact_records)),
        "stale_authorization": _capture(
            lambda: policy.authorized_diagnostic_control(
                authorization, state, REVERSED_RECORDS
            )
        ),
        "withheld_selection": _capture(
            lambda: policy.select_observed_record(
                policy.decide_diagnostic(state, REMOVAL_RECORDS),
                state,
                REMOVAL_RECORDS,
                diagnostic,
            )
        ),
        "nondiagnostic_result": _capture(
            lambda: policy.select_observed_record(
                authorization, state, exact_records, task_result
            )
        ),
        "malformed_record": _capture(
            lambda: policy.AdmittedSignalRecord(
                "record", parent.COVERED_ALPHABET[0], "unknown", "admission"
            )
        ),
    }


def build_packet() -> dict[str, Any]:
    decisions: dict[str, Any] = {}
    trajectories: dict[str, Any] = {}
    input_before = {
        condition: {
            "records": policy.record_set_value(records_value),
            "state": policy.public_state_value(state),
        }
        for condition, (state, records_value) in CONDITION_INPUTS.items()
    }

    for condition in CONDITIONS:
        state, records_value = CONDITION_INPUTS[condition]
        decision = policy.decide_diagnostic(state, records_value)
        repeated = policy.decide_diagnostic(state, tuple(reversed(records_value)))
        decisions[condition] = {
            "decision": _decision_value(decision),
            "order_reversed_decision": _decision_value(repeated),
        }
        control = policy.authorized_diagnostic_control(
            decision, state, records_value
        )
        if control is None:
            trajectories[condition] = {
                "environment_action": None,
                "model_invoked": False,
                "service_window_after": state.service_window,
                "state_unchanged": asdict(state),
            }
            continue

        for profile_name in parent.PROFILE_NAMES:
            profile = parent.PROFILES[(parent.COVERED, profile_name)]
            diagnostic = domain.apply_action(state, profile, control)
            selected = policy.select_observed_record(
                decision, state, records_value, diagnostic
            )
            task = domain.apply_action(
                diagnostic.state_after, profile, _task_control(state, selected)
            )
            trajectories[f"{condition}:{profile_name}"] = {
                "diagnostic_result": asdict(diagnostic),
                "model_invoked": False,
                "selected_record": _handoff_value(selected),
                "task_result_from_deterministic_interpreter": asdict(task),
            }

    dispositions = {
        condition: row["decision"]["disposition"]
        for condition, row in decisions.items()
    }
    authorization_collapse = (
        dispositions[LEARNED]
        == dispositions[SUPPLIED]
        == dispositions[REVERSED]
        == policy.AUTHORIZE
    )
    withholding_exact = (
        dispositions[REMOVAL] == dispositions[UNCOVERED] == policy.WITHHOLD
        and all(
            trajectories[condition]["environment_action"] is None
            and trajectories[condition]["service_window_after"] == domain.AVAILABLE
            for condition in (REMOVAL, UNCOVERED)
        )
    )
    order_independent = all(
        row["decision"] == row["order_reversed_decision"]
        for row in decisions.values()
    )
    correct_outcomes = all(
        trajectories[f"{condition}:{profile}"][
            "task_result_from_deterministic_interpreter"
        ]["task_status_after"]
        == domain.COMPLETED
        for condition in (LEARNED, SUPPLIED)
        for profile in parent.PROFILE_NAMES
    )
    reversed_outcomes = all(
        trajectories[f"{REVERSED}:{profile}"][
            "task_result_from_deterministic_interpreter"
        ]["task_status_after"]
        == domain.FAILED
        for profile in parent.PROFILE_NAMES
    )
    costly_transitions = all(
        trajectories[f"{condition}:{profile}"]["diagnostic_result"][
            "service_window_consumed"
        ]
        for condition in (LEARNED, SUPPLIED, REVERSED)
        for profile in parent.PROFILE_NAMES
    )
    no_hidden_fields = all(
        not {
            "profile_id",
            "valid_task_slot",
            "diagnostic_signal",
            "expected_action",
            "score",
            "branch",
        }.intersection(row["decision"])
        for row in decisions.values()
    )
    input_after = {
        condition: {
            "records": policy.record_set_value(records_value),
            "state": policy.public_state_value(state),
        }
        for condition, (state, records_value) in CONDITION_INPUTS.items()
    }
    input_immutable = input_before == input_after
    refusals = refusal_witnesses()
    conforms = all(
        (
            authorization_collapse,
            withholding_exact,
            order_independent,
            correct_outcomes,
            reversed_outcomes,
            costly_transitions,
            no_hidden_fields,
            input_immutable,
            all(refusals.values()),
        )
    )

    return {
        "claim_boundary": (
            "deterministic_runtime_governance_mechanism_only; "
            "no_model_behavior_or_formation_claim"
        ),
        "decisions": decisions,
        "formation_verdict": None,
        "logical_model_calls": 0,
        "policy_version": policy.POLICY_VERSION,
        "retained_source_packet_sha256": prior.PREDECESSOR_PACKET_SHA256,
        "retained_source_records": list(RETAINED_SOURCE_RECORDS),
        "protocol_version": PROTOCOL_VERSION,
        "refusal_witnesses": refusals,
        "scores": {
            "authorization_collapse": int(authorization_collapse),
            "correct_later_outcomes": int(correct_outcomes),
            "costly_transitions": int(costly_transitions),
            "input_immutable": int(input_immutable),
            "no_hidden_fields": int(no_hidden_fields),
            "order_independent": int(order_independent),
            "refusals_exact": sum(bool(value) for value in refusals.values()),
            "reversed_later_outcomes": int(reversed_outcomes),
            "withholding_exact": int(withholding_exact),
        },
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "specimen_verdict": {
            "class": "conforms" if conforms else "does_not_conform",
            "finding": (
                "governed_diagnostic_encounter_mechanism_available"
                if conforms
                else None
            ),
            "scope": "governed_diagnostic_policy_specimen",
        },
        "trajectories": trajectories,
    }


def write_evidence(evidence_dir: Path) -> dict[str, Any]:
    evidence_dir.mkdir(parents=True, exist_ok=False)
    packet = build_packet()
    (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    retained = (evidence_dir / "packet.json").read_bytes()
    replayed = build_packet()
    if retained != base.canonical_json_bytes(replayed):
        raise GovernedDiagnosticSpecimenRefusal("evidence_replay_mismatch")
    return replayed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args(argv)
    evidence_dir = args.evidence_dir or Path("evidence") / (
        "governed-diagnostic-policy-specimen-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    packet = write_evidence(evidence_dir)
    replay_evidence(evidence_dir)
    print(
        json.dumps(
            {
                "evidence_dir": str(evidence_dir),
                "logical_model_calls": 0,
                "specimen_verdict": packet["specimen_verdict"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
