"""Compare immediate and two-confirmation governance under uncertain evidence."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from contact import distributional_developmental_comparison as base


PROTOCOL_VERSION = "uncertain-consequence-policy-specimen-v1"
SPEC_PATH = (
    Path(__file__).parents[1]
    / "docs"
    / "UNCERTAIN_CONSEQUENCE_POLICY_SPECIMEN.md"
)
RELATION_0 = "relation_0"
RELATION_1 = "relation_1"
IMMEDIATE = "immediate"
TWO_CONFIRMATION = "two_confirmation"
POLICIES = (IMMEDIATE, TWO_CONFIRMATION)


class PolicySpecimenRefusal(ValueError):
    pass


def history(name: str, truths: tuple[str, ...], reports: tuple[str | None, ...]):
    if len(truths) != len(reports):
        raise PolicySpecimenRefusal("history_length_mismatch")
    return [{
        "event_id": f"{name}:{index}",
        "hidden_relation_for_scoring": truth,
        "movement_status": "unresolved" if report is None else "complete",
        "observed_relation": report,
        "order": index,
        "source_id": f"source:{name}:{index}",
    } for index, (truth, report) in enumerate(zip(truths, reports, strict=True), 1)]


HISTORIES = {
    "stable_isolated_anomalies": history(
        "stable_isolated_anomalies",
        (RELATION_0,) * 6,
        (RELATION_0, RELATION_1, RELATION_0, RELATION_0, RELATION_1, RELATION_0),
    ),
    "clean_lasting_change": history(
        "clean_lasting_change",
        (RELATION_0, RELATION_0, RELATION_1, RELATION_1, RELATION_1, RELATION_1),
        (RELATION_0, RELATION_0, RELATION_1, RELATION_1, RELATION_1, RELATION_1),
    ),
    "stable_alternating_reports": history(
        "stable_alternating_reports",
        (RELATION_0,) * 6,
        (RELATION_0, RELATION_1, RELATION_0, RELATION_1, RELATION_0, RELATION_1),
    ),
    "change_interrupted_unresolved": history(
        "change_interrupted_unresolved",
        (RELATION_0, RELATION_1, RELATION_1, RELATION_1, RELATION_1, RELATION_1),
        (RELATION_0, RELATION_1, None, RELATION_1, RELATION_1, RELATION_1),
    ),
    "changed_with_old_relation_anomaly": history(
        "changed_with_old_relation_anomaly",
        (RELATION_0, RELATION_1, RELATION_1, RELATION_1, RELATION_1, RELATION_1),
        (RELATION_0, RELATION_1, RELATION_1, RELATION_0, RELATION_1, RELATION_1),
    ),
}


def public_receipts(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "event_id": row["event_id"],
        "movement_status": row["movement_status"],
        "observed_relation": row["observed_relation"],
        "order": row["order"],
        "source_id": row["source_id"],
    } for row in rows]


def apply_policy(policy: str, receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if policy not in POLICIES:
        raise PolicySpecimenRefusal("unknown_policy")
    if [row["order"] for row in receipts] != list(range(1, len(receipts) + 1)):
        raise PolicySpecimenRefusal("noncontiguous_occurrence_order")
    current = RELATION_0
    candidate = None
    candidate_ids: list[str] = []
    closed_ids: list[str] = []
    transitions = []
    considered = []
    for receipt in receipts:
        considered.append(receipt["event_id"])
        report = receipt["observed_relation"]
        status = receipt["movement_status"]
        replaced = False
        if status != "complete" or report not in {RELATION_0, RELATION_1}:
            candidate = None
            candidate_ids = []
            governance_state = "suspended_unresolved"
            delivered = None
        elif report == current:
            closed_ids.extend(candidate_ids)
            candidate = None
            candidate_ids = []
            governance_state = "current_retained"
            delivered = current
        elif policy == IMMEDIATE:
            current = report
            candidate = None
            candidate_ids = []
            governance_state = "superseded"
            delivered = current
            replaced = True
        elif candidate == report:
            candidate_ids.append(receipt["event_id"])
            current = report
            candidate = None
            candidate_ids = []
            governance_state = "superseded"
            delivered = current
            replaced = True
        else:
            candidate = report
            candidate_ids = [receipt["event_id"]]
            governance_state = "suspended_pending_corroboration"
            delivered = None
        transitions.append({
            "candidate_occurrence_ids": candidate_ids.copy(),
            "candidate_relation": candidate,
            "closed_occurrence_ids": closed_ids.copy(),
            "considered_occurrence_ids": considered.copy(),
            "current_record": current,
            "delivered_record": delivered,
            "event_id": receipt["event_id"],
            "governance_state": governance_state,
            "replacement_committed": replaced,
        })
    return transitions


def score_history(
    rows: list[dict[str, Any]], transitions: list[dict[str, Any]]
) -> dict[str, Any]:
    correct = 0
    wrong = 0
    suspended = 0
    false_replacements = 0
    correct_replacements = 0
    for occurrence, transition in zip(rows, transitions, strict=True):
        truth = occurrence["hidden_relation_for_scoring"]
        delivered = transition["delivered_record"]
        if delivered is None:
            suspended += 1
        elif delivered == truth:
            correct += 1
        else:
            wrong += 1
        if transition["replacement_committed"]:
            if transition["current_record"] == truth:
                correct_replacements += 1
            else:
                false_replacements += 1

    change_index = next((
        index for index, row in enumerate(rows)
        if row["hidden_relation_for_scoring"] != RELATION_0
    ), None)
    delay = None
    if change_index is not None:
        changed_relation = rows[change_index]["hidden_relation_for_scoring"]
        first_correct = next((
            index for index in range(change_index, len(rows))
            if transitions[index]["delivered_record"] == changed_relation
        ), None)
        delay = None if first_correct is None else first_correct - change_index
    return {
        "adaptation_delay": delay,
        "correct_deliveries": correct,
        "correct_replacements": correct_replacements,
        "false_replacements": false_replacements,
        "suspended_deliveries": suspended,
        "wrong_deliveries": wrong,
    }


EXPECTED_AGGREGATE = {
    IMMEDIATE: {
        "correct_deliveries": 23,
        "false_replacements": 6,
        "suspended_deliveries": 1,
        "wrong_deliveries": 6,
    },
    TWO_CONFIRMATION: {
        "correct_deliveries": 19,
        "false_replacements": 0,
        "suspended_deliveries": 11,
        "wrong_deliveries": 0,
    },
}


def build_packet() -> dict[str, Any]:
    policy_results = {}
    source_preservation = {}
    for policy in POLICIES:
        histories = {}
        preserved = 0
        for name, rows in HISTORIES.items():
            transitions = apply_policy(policy, public_receipts(rows))
            histories[name] = {
                "scores": score_history(rows, transitions),
                "transitions": transitions,
            }
            preserved += transitions[-1]["considered_occurrence_ids"] == [
                row["event_id"] for row in rows
            ]
        aggregate = {
            key: sum(history["scores"][key] for history in histories.values())
            for key in (
                "correct_deliveries", "false_replacements",
                "suspended_deliveries", "wrong_deliveries",
            )
        }
        policy_results[policy] = {"aggregate": aggregate, "histories": histories}
        source_preservation[policy] = preserved

    immediate = policy_results[IMMEDIATE]
    corroborated = policy_results[TWO_CONFIRMATION]
    conforms = (
        all(
            policy_results[policy]["aggregate"] == EXPECTED_AGGREGATE[policy]
            for policy in POLICIES
        )
        and source_preservation == {IMMEDIATE: 5, TWO_CONFIRMATION: 5}
        and immediate["histories"]["clean_lasting_change"]["scores"]["adaptation_delay"] == 0
        and corroborated["histories"]["clean_lasting_change"]["scores"]["adaptation_delay"] == 1
        and corroborated["histories"]["change_interrupted_unresolved"]["scores"]["adaptation_delay"] == 3
    )
    return {
        "expected_aggregate": EXPECTED_AGGREGATE,
        "formation_verdict": None,
        "histories": HISTORIES,
        "logical_model_calls": 0,
        "policy_results": policy_results,
        "protocol_version": PROTOCOL_VERSION,
        "source_preservation": source_preservation,
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "specimen_verdict": {
            "class": "conforms" if conforms else "does_not_conform",
            "finding": "tradeoff_exposed" if conforms else None,
            "scope": "uncertain_consequence_policy_specimen",
        },
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
        raise PolicySpecimenRefusal("evidence_replay_mismatch")
    return replayed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args(argv)
    evidence_dir = args.evidence_dir or Path("evidence") / (
        "uncertain-consequence-policy-specimen-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    packet = write_evidence(evidence_dir)
    replay_evidence(evidence_dir)
    print(json.dumps({
        "evidence_dir": str(evidence_dir),
        "logical_model_calls": 0,
        "specimen_verdict": packet["specimen_verdict"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
