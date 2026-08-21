"""Measure response costs after one contradiction suspends a record."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from contact import distributional_developmental_comparison as base
from contact import mirrored_recovery_influence_successor as mirrored
from micro_environment.unselected_lineage_behavior import (
    FIRST_INCREASES,
    SECOND_INCREASES,
    HOLD,
)


PROTOCOL_VERSION = "suspension-consequence-specimen-v1"
SPEC_PATH = (
    Path(__file__).parents[1] / "docs" / "SUSPENSION_CONSEQUENCE_SPECIMEN.md"
)
SOURCE_DIR = (
    Path(__file__).parents[1]
    / "evidence"
    / "mirrored-recovery-influence-successor-20260820T221149Z"
)
SOURCE_PACKET_SHA256 = (
    "5f829cf7c82cda235badf7bca35c30063caac4e2d011f04fbb4e523175a8b8c4"
)
SOURCE_PROTOCOL_VERSION = mirrored.PROTOCOL_VERSION

CASES = ("match_up_01", "match_down_01")
WORLDS = mirrored.WORLDS
WORLD_SLOTS = mirrored.WORLD_SLOTS

CURRENT = "current_record_then_resolve"
NEWEST = "newest_proposal_then_resolve"
COLD = "retained_cold_then_resolve"
EXPLORE = "first_control_explore_then_resolve"
HOLD_ONLY = "hold_only"
HOLD_EXPLORE = "hold_then_first_control_explore_then_resolve"
STRATEGIES = (CURRENT, NEWEST, COLD, EXPLORE, HOLD_ONLY, HOLD_EXPLORE)


class SuspensionSpecimenRefusal(ValueError):
    pass


def load_source() -> tuple[dict[str, Any], dict[str, Any]]:
    packet_bytes = (SOURCE_DIR / "packet.json").read_bytes()
    if base.sha256(packet_bytes) != SOURCE_PACKET_SHA256:
        raise SuspensionSpecimenRefusal("source_packet_hash_mismatch")
    packet = json.loads(packet_bytes)
    specimen = json.loads((SOURCE_DIR / "specimen.json").read_bytes())
    if (
        packet.get("protocol_version") != SOURCE_PROTOCOL_VERSION
        or packet.get("validation_verdict", {}).get("class") != "supported"
        or packet.get("formation_verdict") is not None
    ):
        raise SuspensionSpecimenRefusal("source_status_mismatch")
    return packet, specimen


def selected_slot(action: str, controls: tuple[str, str]) -> str | None:
    if action == controls[0]:
        return "first"
    if action == controls[1]:
        return "second"
    if action == HOLD:
        return "hold"
    raise SuspensionSpecimenRefusal("action_outside_public_controls")


def record_action(
    increasing_slot: str, position: int, target: int, controls: tuple[str, str]
) -> str:
    wants_increase = target > position
    increasing_index = 0 if increasing_slot == FIRST_INCREASES else 1
    selected_index = increasing_index if wants_increase else 1 - increasing_index
    return controls[selected_index]


def apply_action(
    action: str, position: int, target: int, controls: tuple[str, str], increasing_slot: str
) -> dict[str, Any]:
    slot = selected_slot(action, controls)
    if slot == "hold":
        after = position
        movement = "unchanged"
    else:
        increasing_index = 0 if increasing_slot == FIRST_INCREASES else 1
        action_index = controls.index(action)
        increases = action_index == increasing_index
        after = position + (1 if increases else -1)
        movement = "increased" if increases else "decreased"
    before_distance = abs(target - position)
    after_distance = abs(target - after)
    return {
        "action": action,
        "distance_after": after_distance,
        "distance_before": before_distance,
        "movement_direction": movement,
        "moved_away_from_target": after_distance > before_distance,
        "position_after": after,
        "position_before": position,
        "selected_slot": slot,
        "target_reached": after == target,
    }


def finish_after_informative_action(
    first_action: str,
    position: int,
    target: int,
    controls: tuple[str, str],
    increasing_slot: str,
    *,
    leading_hold: bool,
) -> dict[str, Any]:
    trajectory = []
    if leading_hold:
        held = apply_action(HOLD, position, target, controls, increasing_slot)
        trajectory.append({**held, "purpose": "hold"})
        position = held["position_after"]
    first = apply_action(first_action, position, target, controls, increasing_slot)
    trajectory.append({**first, "purpose": "informative_action"})
    position = first["position_after"]
    while position != target:
        action = record_action(increasing_slot, position, target, controls)
        result = apply_action(action, position, target, controls, increasing_slot)
        trajectory.append({**result, "purpose": "resolved_record_action"})
        position = result["position_after"]
        if len(trajectory) > 4:
            raise SuspensionSpecimenRefusal("trajectory_failed_to_reach_target")
    return {
        "actions_to_target": len(trajectory),
        "holds": sum(row["selected_slot"] == "hold" for row in trajectory),
        "informative_action_moved_away": first["moved_away_from_target"],
        "informative_action_target_hit": first["target_reached"],
        "relation_resolved": True,
        "target_reached": True,
        "trajectory": trajectory,
    }


def simulate_trial(
    strategy: str,
    cold_action: str,
    device: dict[str, Any],
    increasing_slot: str,
) -> dict[str, Any]:
    controls = tuple(device["allowed_actions"][:2])
    position = device["position"]
    target = device["target"]
    if strategy == HOLD_ONLY:
        held = apply_action(HOLD, position, target, controls, increasing_slot)
        return {
            "actions_to_target": None,
            "holds": 1,
            "informative_action_moved_away": False,
            "informative_action_target_hit": False,
            "relation_resolved": False,
            "target_reached": False,
            "trajectory": [{**held, "purpose": "hold"}],
        }
    if strategy == CURRENT:
        first_action = record_action(FIRST_INCREASES, position, target, controls)
        leading_hold = False
    elif strategy == NEWEST:
        first_action = record_action(SECOND_INCREASES, position, target, controls)
        leading_hold = False
    elif strategy == COLD:
        first_action = cold_action
        leading_hold = False
    elif strategy == EXPLORE:
        first_action = controls[0]
        leading_hold = False
    elif strategy == HOLD_EXPLORE:
        first_action = controls[0]
        leading_hold = True
    else:
        raise SuspensionSpecimenRefusal("unknown_strategy")
    return finish_after_informative_action(
        first_action,
        position,
        target,
        controls,
        increasing_slot,
        leading_hold=leading_hold,
    )


EXPECTED_OUTCOMES = {
    CURRENT: (6, 6, 12, 0, 24),
    NEWEST: (6, 6, 12, 0, 24),
    COLD: (6, 6, 12, 0, 24),
    EXPLORE: (6, 6, 12, 0, 24),
    HOLD_ONLY: (0, 0, 0, 12, None),
    HOLD_EXPLORE: (6, 6, 12, 0, 36),
}


def build_packet() -> dict[str, Any]:
    source_packet, source_specimen = load_source()
    cold_rows = [
        row for row in source_packet["calls"]
        if row["responsibility"] == "comparison_action"
        and row["branch"] == mirrored.COLD
        and row["case"] in CASES
    ]
    cold_by_key = {
        (row["world"], row["case"], row["repeat"]): row
        for row in cold_rows
    }
    if len(cold_by_key) != 12:
        raise SuspensionSpecimenRefusal("cold_source_receipts_incomplete")

    trials = []
    public_identity = 0
    cold_second_actions = 0
    for case_name in CASES:
        device = source_specimen["cases"][case_name]["public_device"]
        device_hashes = set()
        for world in WORLDS:
            device_hashes.add(base.sha256(base.canonical_json_bytes(device)))
            for repeat in range(1, 4):
                cold_row = cold_by_key[(world, case_name, repeat)]
                controls = tuple(device["allowed_actions"][:2])
                cold_second_actions += cold_row["action"] == controls[1]
                for strategy in STRATEGIES:
                    result = simulate_trial(
                        strategy,
                        cold_row["action"],
                        device,
                        WORLD_SLOTS[world],
                    )
                    trials.append({
                        "case": case_name,
                        "cold_source_request_sha256": cold_row["request_sha256"],
                        "hidden_relation_for_scoring": WORLD_SLOTS[world],
                        "public_device_sha256": base.sha256(
                            base.canonical_json_bytes(device)
                        ),
                        "repeat": repeat,
                        "result": result,
                        "strategy": strategy,
                        "world": world,
                    })
        public_identity += len(device_hashes) == 1

    outcomes = {}
    hit_cells = {}
    for strategy in STRATEGIES:
        rows = [row for row in trials if row["strategy"] == strategy]
        totals = [
            row["result"]["actions_to_target"] for row in rows
            if row["result"]["actions_to_target"] is not None
        ]
        outcomes[strategy] = {
            "holds": sum(row["result"]["holds"] for row in rows),
            "informative_action_moves_away": sum(
                row["result"]["informative_action_moved_away"] for row in rows
            ),
            "informative_action_target_hits": sum(
                row["result"]["informative_action_target_hit"] for row in rows
            ),
            "relations_resolved": sum(
                row["result"]["relation_resolved"] for row in rows
            ),
            "total_actions_to_target": sum(totals) if len(totals) == len(rows) else None,
            "trials": len(rows),
            "unfinished_trials": sum(not row["result"]["target_reached"] for row in rows),
        }
        hit_cells[strategy] = sorted({
            (row["world"], row["case"])
            for row in rows if row["result"]["informative_action_target_hit"]
        })

    exact_outcomes = sum(
        (
            outcomes[strategy]["informative_action_target_hits"],
            outcomes[strategy]["informative_action_moves_away"],
            outcomes[strategy]["relations_resolved"],
            outcomes[strategy]["unfinished_trials"],
            outcomes[strategy]["total_actions_to_target"],
        ) == expected
        for strategy, expected in EXPECTED_OUTCOMES.items()
    )
    non_hold_cells_distinct = len({
        tuple(hit_cells[strategy]) for strategy in (CURRENT, NEWEST, COLD, EXPLORE)
    }) == 4
    conforms = (
        public_identity == len(CASES)
        and cold_second_actions == 12
        and exact_outcomes == len(STRATEGIES)
        and non_hold_cells_distinct
    )
    return {
        "cold_source_receipts": cold_rows,
        "expected_outcomes": EXPECTED_OUTCOMES,
        "formation_verdict": None,
        "logical_model_calls": 0,
        "outcomes": outcomes,
        "protocol_version": PROTOCOL_VERSION,
        "scores": {
            "cold_second_control_actions": cold_second_actions,
            "exact_strategy_outcomes": exact_outcomes,
            "non_hold_hit_distributions_distinct": non_hold_cells_distinct,
            "public_mirror_identities": public_identity,
        },
        "source_packet_sha256": SOURCE_PACKET_SHA256,
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "specimen_verdict": {
            "class": "conforms" if conforms else "does_not_conform",
            "finding": "symmetric_action_information_equivalence" if conforms else None,
            "scope": "suspension_consequence_specimen",
        },
        "strategy_hit_cells": hit_cells,
        "trials": trials,
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
        raise SuspensionSpecimenRefusal("evidence_replay_mismatch")
    return replayed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args(argv)
    evidence_dir = args.evidence_dir or Path("evidence") / (
        "suspension-consequence-specimen-"
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
