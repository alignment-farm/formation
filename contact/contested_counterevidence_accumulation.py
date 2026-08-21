"""Distinguish repeated, corrected, isolated, and contested counterevidence."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from contact import distributional_developmental_comparison as base


PROTOCOL_VERSION = "contested-counterevidence-accumulation-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "CONTESTED_COUNTEREVIDENCE_ACCUMULATION.md"
CURRENT = {
    "first_control_effect": "increases_position",
    "second_control_effect": "decreases_position",
}
OPPOSITE = {
    "first_control_effect": "decreases_position",
    "second_control_effect": "increases_position",
}


class AccumulationRefusal(ValueError):
    pass


def occurrence(
    event_id: str,
    order: int,
    *,
    movement_status: str,
    movement: str | None,
    proposed_record: dict[str, str] | None,
    composed_status: str,
) -> dict[str, Any]:
    return {
        "composed_status": composed_status,
        "event_id": event_id,
        "movement": movement,
        "movement_status": movement_status,
        "order": order,
        "proposed_record": proposed_record,
        "selected_slot": "first",
        "source_id": f"source:{event_id}",
    }


HISTORIES = {
    "repeated_contradiction": [
        occurrence(
            "repeat:1", 1, movement_status="complete", movement="decreased",
            proposed_record=OPPOSITE, composed_status="admitted",
        ),
        occurrence(
            "repeat:2", 2, movement_status="complete", movement="decreased",
            proposed_record=OPPOSITE, composed_status="admitted",
        ),
    ],
    "self_correcting": [
        occurrence(
            "corrected:1", 1, movement_status="complete", movement="decreased",
            proposed_record=OPPOSITE, composed_status="admitted",
        ),
        occurrence(
            "corrected:2", 2, movement_status="complete", movement="increased",
            proposed_record=CURRENT, composed_status="admitted",
        ),
    ],
    "isolated_contradiction": [
        occurrence(
            "isolated:1", 1, movement_status="complete", movement="decreased",
            proposed_record=OPPOSITE, composed_status="admitted",
        ),
    ],
    "contested_movement": [
        occurrence(
            "contested:1", 1, movement_status="contested", movement=None,
            proposed_record=None, composed_status="quarantined",
        ),
    ],
}


def claimed_movement(record: dict[str, str], slot: str) -> str | None:
    return {
        "increases_position": "increased",
        "decreases_position": "decreased",
    }.get(record.get(f"{slot}_control_effect"))


def decide(history: list[dict[str, Any]]) -> dict[str, Any]:
    if [row["order"] for row in history] != list(range(1, len(history) + 1)):
        raise AccumulationRefusal("noncontiguous_occurrence_order")
    considered = [row["event_id"] for row in history]
    unresolved = [
        row["event_id"] for row in history
        if row["movement_status"] != "complete"
    ]
    eligible = [
        row for row in history
        if row["movement_status"] == "complete"
        and row["movement"] in {"increased", "decreased"}
        and row["composed_status"] == "admitted"
        and type(row["proposed_record"]) is dict
    ]
    supports_current = [
        row["event_id"] for row in eligible
        if row["proposed_record"] == CURRENT
        and row["movement"] == claimed_movement(CURRENT, row["selected_slot"])
    ]
    supports_opposite = [
        row["event_id"] for row in eligible
        if row["proposed_record"] == OPPOSITE
        and row["movement"] == claimed_movement(OPPOSITE, row["selected_slot"])
        and row["movement"] != claimed_movement(CURRENT, row["selected_slot"])
    ]
    closed = []
    if unresolved:
        state = "suspended_unresolved"
        active_record = None
    elif (
        len(eligible) >= 2
        and eligible[-1]["event_id"] in supports_opposite
        and eligible[-2]["event_id"] in supports_opposite
        and eligible[-1]["proposed_record"] == eligible[-2]["proposed_record"]
    ):
        state = "superseded"
        active_record = OPPOSITE
    elif supports_current and supports_opposite and history[-1]["event_id"] in supports_current:
        state = "current_retained"
        active_record = CURRENT
        closed = supports_opposite.copy()
    elif supports_opposite:
        state = "suspended_pending_corroboration"
        active_record = None
    else:
        state = "current_retained"
        active_record = CURRENT
    return {
        "active_record": active_record,
        "closed_uncorroborated_occurrence_ids": closed,
        "considered_occurrence_ids": considered,
        "contradicting_occurrence_ids": supports_opposite,
        "governance_state": state,
        "supporting_current_occurrence_ids": supports_current,
        "unresolved_occurrence_ids": unresolved,
    }


EXPECTED = {
    "repeated_contradiction": "superseded",
    "self_correcting": "current_retained",
    "isolated_contradiction": "suspended_pending_corroboration",
    "contested_movement": "suspended_unresolved",
}


def build_packet() -> dict[str, Any]:
    decisions = {name: decide(history) for name, history in HISTORIES.items()}
    exact = sum(
        decisions[name]["governance_state"] == expected
        for name, expected in EXPECTED.items()
    )
    lineage_exact = sum(
        decisions[name]["considered_occurrence_ids"]
        == [row["event_id"] for row in HISTORIES[name]]
        for name in HISTORIES
    )
    conforms = exact == len(EXPECTED) and lineage_exact == len(HISTORIES)
    return {
        "current_record": CURRENT,
        "decisions": decisions,
        "formation_verdict": None,
        "histories": HISTORIES,
        "logical_model_calls": 0,
        "protocol_version": PROTOCOL_VERSION,
        "scores": {
            "exact_governance_states": exact,
            "exact_ordered_lineages": lineage_exact,
            "total_histories": len(HISTORIES),
        },
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "specimen_verdict": {
            "class": "conforms" if conforms else "does_not_conform",
            "scope": "contested_counterevidence_accumulation",
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
        raise AccumulationRefusal("evidence_replay_mismatch")
    return replayed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args(argv)
    evidence_dir = args.evidence_dir or Path("evidence") / (
        "contested-counterevidence-accumulation-"
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
