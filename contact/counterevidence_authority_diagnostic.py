"""Separate observation-grounded from action-attributed counterevidence."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from contact import distributional_developmental_comparison as base


PROTOCOL_VERSION = "counterevidence-authority-diagnostic-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "COUNTEREVIDENCE_AUTHORITY_DIAGNOSTIC.md"
SOURCE_DIR = (
    Path(__file__).parents[1]
    / "evidence"
    / "selective-longer-lineage-revision-20260820T192314Z"
)
SOURCE_PACKET_SHA256 = "1ce32ea264ff0631c6c45a4a73d6b5fee423b68540acb6367d53b6a5158933c2"
SOURCE_SPECIMEN_SHA256 = "b795ab2468b5c4cb5fb9f1429fa0eb14841b1bb3b1267ffc08c1cf5eb46fb10d"


class AuthorityDiagnosticRefusal(ValueError):
    pass


def source_material() -> tuple[dict[str, Any], dict[str, Any]]:
    packet_bytes = (SOURCE_DIR / "packet.json").read_bytes()
    specimen_bytes = (SOURCE_DIR / "specimen.json").read_bytes()
    if base.sha256(packet_bytes) != SOURCE_PACKET_SHA256:
        raise AuthorityDiagnosticRefusal("source_packet_hash_mismatch")
    if base.sha256(specimen_bytes) != SOURCE_SPECIMEN_SHA256:
        raise AuthorityDiagnosticRefusal("source_specimen_hash_mismatch")
    return json.loads(packet_bytes), json.loads(specimen_bytes)


def movement_claim(record: dict[str, str], slot: str) -> str | None:
    effect = record.get(f"{slot}_control_effect")
    return {
        "increases_position": "increased",
        "decreases_position": "decreased",
    }.get(effect)


def recommended_action(device: dict[str, Any], record: dict[str, str]) -> str | None:
    if len(device.get("allowed_actions", [])) < 2:
        return None
    wants = "increased" if device["target"] > device["position"] else "decreased"
    for index, slot in enumerate(("first", "second")):
        if movement_claim(record, slot) == wants:
            return device["allowed_actions"][index]
    return None


def build_packet() -> dict[str, Any]:
    source_packet, source_specimen = source_material()
    source_rows = {
        row["lineage"]: row
        for row in source_packet["calls"]
        if row["responsibility"] == "third_occurrence_action"
    }
    rows = []
    for lineage in sorted(source_rows):
        source = source_rows[lineage]
        device = source_specimen["lineages"][lineage]["third_source"]
        current_record = source_specimen["lineages"][lineage]["parent_v2"]["a"]["record"]
        actions = device["allowed_actions"][:2]
        selected_slot = (
            "first" if source["action"] == actions[0]
            else "second" if source["action"] == actions[1]
            else None
        )
        observed_movement = source["external_result"]["movement_direction"]
        claimed_movement = (
            movement_claim(current_record, selected_slot)
            if selected_slot is not None else None
        )
        source_complete = (
            selected_slot is not None
            and observed_movement in {"increased", "decreased"}
        )
        claim_contradicted = (
            source_complete
            and claimed_movement is not None
            and claimed_movement != observed_movement
        )
        expected_action = recommended_action(device, current_record)
        action_attributed = source["action"] == expected_action
        composed_admitted = (
            source_packet["proposals"][lineage]["revised"]["admission_status"]
            == "admitted"
        )
        observation_grounded = (
            composed_admitted and source_complete and claim_contradicted
        )
        attributed = observation_grounded and action_attributed
        rows.append({
            "action_attributed": action_attributed,
            "action_attributed_policy": "admitted" if attributed else "quarantined",
            "claim_contradicted": claim_contradicted,
            "committed_action": source["action"],
            "composed_proposal_admitted": composed_admitted,
            "current_record": current_record,
            "environment_movement": observed_movement,
            "lineage": lineage,
            "observation_grounded_policy": (
                "admitted" if observation_grounded else "quarantined"
            ),
            "recommended_action": expected_action,
            "retained_action_attribution_label": source["version_2_policy_consistent"],
            "selected_effect_claim": claimed_movement,
            "selected_slot": selected_slot,
            "source_complete": source_complete,
        })
    scores = {
        "action_attributed_admissions": sum(
            row["action_attributed_policy"] == "admitted" for row in rows
        ),
        "action_attribution_labels_exact": sum(
            row["action_attributed"] == row["retained_action_attribution_label"]
            for row in rows
        ),
        "complete_sources": sum(row["source_complete"] for row in rows),
        "contradicted_selected_effect_claims": sum(
            row["claim_contradicted"] for row in rows
        ),
        "observation_grounded_admissions": sum(
            row["observation_grounded_policy"] == "admitted" for row in rows
        ),
        "total": len(rows),
    }
    conforms = scores == {
        "action_attributed_admissions": 3,
        "action_attribution_labels_exact": 4,
        "complete_sources": 4,
        "contradicted_selected_effect_claims": 4,
        "observation_grounded_admissions": 4,
        "total": 4,
    }
    return {
        "diagnostic_verdict": {
            "class": "conforms" if conforms else "does_not_conform",
            "scope": "counterevidence_authority_diagnostic",
        },
        "formation_verdict": None,
        "logical_model_calls": 0,
        "protocol_version": PROTOCOL_VERSION,
        "rows": rows,
        "scores": scores,
        "source_packet_sha256": SOURCE_PACKET_SHA256,
        "source_specimen_sha256": SOURCE_SPECIMEN_SHA256,
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
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
        raise AuthorityDiagnosticRefusal("evidence_replay_mismatch")
    return replayed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args(argv)
    evidence_dir = args.evidence_dir or Path("evidence") / (
        "counterevidence-authority-diagnostic-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    packet = write_evidence(evidence_dir)
    replay_evidence(evidence_dir)
    print(json.dumps({
        "diagnostic_verdict": packet["diagnostic_verdict"],
        "evidence_dir": str(evidence_dir),
        "logical_model_calls": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
