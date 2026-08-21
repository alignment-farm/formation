"""Run the eight-world aggregate validation of the staged lesson chain."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Callable

from contact import distributional_developmental_comparison as base
from contact import staged_chain_validation as prior
from micro_environment.unselected_lineage_behavior import (
    FIRST_INCREASES,
    SECOND_INCREASES,
    LineageProfile,
    LineageState,
)


PROTOCOL_VERSION = "staged-chain-aggregate-validation-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "STAGED_CHAIN_AGGREGATE_VALIDATION.md"
WORLDS = tuple(f"world_{index:02d}" for index in range(1, 9))
CASES = prior.CASES
BRANCHES = prior.BRANCHES
REPEATS = 3
AUTHORSHIP_CALLS = len(WORLDS) * 6
LATER_CALLS = len(WORLDS) * len(CASES) * len(BRANCHES) * REPEATS
PLANNED_LOGICAL_CALLS = AUTHORSHIP_CALLS + LATER_CALLS
PHYSICAL_CALL_CEILING = 824
MAX_RETRIES = 8


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


def make_world(name: str, index: int) -> prior.World:
    increasing_slot = FIRST_INCREASES if index % 2 else SECOND_INCREASES
    profile = LineageProfile(opaque(f"{name}:family"), increasing_slot)
    position = 1000 + index * 239
    acquisition = LineageState(
        profile.controller_family,
        opaque(f"{name}:acquisition-device"),
        position,
        position - 1,
        (opaque(f"{name}:acquisition-first"), opaque(f"{name}:acquisition-second")),
    )
    opposite = SECOND_INCREASES if increasing_slot == FIRST_INCREASES else FIRST_INCREASES
    cases = {}
    profiles = {}
    for case_index, case in enumerate(CASES, 1):
        matching = case.startswith("same")
        case_profile = profile if matching else LineageProfile(
            opaque(f"{name}:{case}:family"), opposite
        )
        case_position = 2200 + index * 503 + case_index * 73
        cases[case] = LineageState(
            case_profile.controller_family,
            opaque(f"{name}:{case}:device"),
            case_position,
            case_position + (1 if case.endswith("up") else -1),
            (opaque(f"{name}:{case}:first"), opaque(f"{name}:{case}:second")),
        )
        profiles[case] = case_profile
    return prior.World(name, profile, acquisition, cases, profiles)


WORLD_DATA = {name: make_world(name, index) for index, name in enumerate(WORLDS, 1)}


_CONFIGURATION = {
    "PROTOCOL_VERSION": PROTOCOL_VERSION,
    "SPEC_PATH": SPEC_PATH,
    "WORLDS": WORLDS,
    "CASES": CASES,
    "BRANCHES": BRANCHES,
    "REPEATS": REPEATS,
    "AUTHORSHIP_CALLS": AUTHORSHIP_CALLS,
    "LATER_CALLS": LATER_CALLS,
    "PLANNED_LOGICAL_CALLS": PLANNED_LOGICAL_CALLS,
    "PHYSICAL_CALL_CEILING": PHYSICAL_CALL_CEILING,
    "MAX_RETRIES": MAX_RETRIES,
    "WORLD_DATA": WORLD_DATA,
}


@contextmanager
def configured_prior():
    original = {name: getattr(prior, name) for name in _CONFIGURATION}
    try:
        for name, value in _CONFIGURATION.items():
            setattr(prior, name, value)
        yield
    finally:
        for name, value in original.items():
            setattr(prior, name, value)


def specimen() -> dict[str, Any]:
    with configured_prior():
        result = prior.specimen()
    result["relation_groups"] = {
        relation: [
            name for name, world in WORLD_DATA.items()
            if world.profile.increasing_slot == relation
        ]
        for relation in (FIRST_INCREASES, SECOND_INCREASES)
    }
    return result


def score(packet: dict[str, Any]) -> dict[str, Any]:
    distributions = packet["request_distributions"]

    def total(branch: str, cases: tuple[str, ...], worlds=WORLDS) -> int:
        return sum(
            distributions[name][branch][case]["correct_actions"]
            for name in worlds
            for case in cases
        )

    matching_cases = ("same_up", "same_down")
    unrelated_cases = ("other_up", "other_down")
    matching_scores = {branch: total(branch, matching_cases) for branch in BRANCHES}
    unrelated_scores = {branch: total(branch, unrelated_cases) for branch in BRANCHES}
    direction_scores = {
        branch: {
            "up": total(branch, ("same_up",)),
            "down": total(branch, ("same_down",)),
        }
        for branch in (prior.EXPOSED, prior.STATIC)
    }
    relation_scores = {}
    quadrant_scores = {}
    for relation in (FIRST_INCREASES, SECOND_INCREASES):
        names = tuple(
            name for name, world in WORLD_DATA.items()
            if world.profile.increasing_slot == relation
        )
        relation_scores[relation] = {
            branch: total(branch, matching_cases, names)
            for branch in (prior.EXPOSED, prior.STATIC)
        }
        quadrant_scores[relation] = {
            "up": total(prior.EXPOSED, ("same_up",), names),
            "down": total(prior.EXPOSED, ("same_down",), names),
        }
    every_cell_valid = all(
        distributions[name][branch][case]["invalid_or_unavailable"] <= 1
        for name in WORLDS
        for branch in BRANCHES
        for case in CASES
    )
    unrelated_loss = unrelated_scores[prior.COLD] - unrelated_scores[prior.EXPOSED]
    scope_errors_prevented = (
        unrelated_scores[prior.EXPOSED] - unrelated_scores[prior.UNGATED]
    )
    engaged = (
        packet["exposed_observations_exact"] >= 7
        and packet["exposed_tables_exact"] >= 7
        and matching_scores[prior.STATIC] >= 43
        and all(score >= 21 for score in direction_scores[prior.STATIC].values())
        and all(
            scores[prior.STATIC] >= 21 for scores in relation_scores.values()
        )
    )
    harmful = engaged and unrelated_loss >= 6
    supported = (
        engaged
        and matching_scores[prior.EXPOSED] >= 43
        and all(score >= 21 for score in direction_scores[prior.EXPOSED].values())
        and all(
            scores[prior.EXPOSED] >= 21 for scores in relation_scores.values()
        )
        and all(
            score >= 9
            for directions in quadrant_scores.values()
            for score in directions.values()
        )
        and all(
            matching_scores[prior.EXPOSED] - matching_scores[branch] >= 16
            for branch in (prior.COLD, prior.RAW, prior.REMOVED)
        )
        and all(
            matching_scores[prior.EXPOSED] - matching_scores[branch] >= 12
            for branch in (prior.DIRECT, prior.WITHHELD)
        )
        and matching_scores[prior.STATIC] - matching_scores[prior.EXPOSED] <= 3
        and unrelated_loss <= 3
        and every_cell_valid
    )
    verdict_class = (
        "not_engaged" if not engaged
        else "harmful" if harmful
        else "supported" if supported
        else "null"
    )
    packet.update({
        "direction_scores": direction_scores,
        "every_branch_case_valid": every_cell_valid,
        "matching_scores": matching_scores,
        "relation_matching_scores": relation_scores,
        "relation_direction_scores": quadrant_scores,
        "scope_errors_prevented": scope_errors_prevented,
        "unrelated_loss": unrelated_loss,
        "unrelated_scores": unrelated_scores,
        "validation_verdict": {
            "class": verdict_class,
            "scope": "staged_chain_aggregate_validation",
        },
    })
    return packet


Transport = Callable[[bytes], tuple[int, bytes]]


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    with configured_prior():
        packet = prior.execute(transport, evidence_dir)
    packet = score(packet)
    retained_specimen = specimen()
    packet["specimen_sha256"] = base.sha256(base.canonical_json_bytes(retained_specimen))
    if evidence_dir is not None:
        (evidence_dir / "specimen.json").write_bytes(
            base.canonical_json_bytes(retained_specimen)
        )
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise prior.ValidationRefusal("retained_specimen_mismatch")
    retained = json.loads((evidence_dir / "packet.json").read_bytes())
    entries = []
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        meta = json.loads(meta_path.read_text())
        request = (evidence_dir / "attempts" / f"{stem}.request.json").read_bytes()
        response = (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes()
        entries.append((request, response, meta))
    position = 0

    def transport(body: bytes) -> tuple[int, bytes]:
        nonlocal position
        request, response, meta = entries[position]
        position += 1
        if request != body:
            raise prior.ValidationRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise prior.ValidationRefusal("evidence_replay_mismatch")
    return replayed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args(argv)
    if not args.live:
        print(json.dumps({
            "mode": "smoke_no_contact",
            "planned_logical_calls": PLANNED_LOGICAL_CALLS,
            "side_effects_entered": False,
        }, sort_keys=True))
        return 0
    if args.evidence_dir is None:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        args.evidence_dir = Path("evidence") / f"staged-chain-aggregate-validation-{run_id}"
    started = time.monotonic()
    receipt = base.collect_provider_receipt()
    if not receipt["valid"]:
        raise prior.ValidationRefusal("provider_identity_mismatch")
    packet = execute(base.live_transport, args.evidence_dir)
    (args.evidence_dir / "provider.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    replay_evidence(args.evidence_dir)
    print(json.dumps({
        "elapsed_seconds": time.monotonic() - started,
        "evidence_dir": str(args.evidence_dir),
        "logical_calls": packet["logical_calls"],
        "physical_attempts": packet["physical_attempts"],
        "validation_verdict": packet["validation_verdict"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
