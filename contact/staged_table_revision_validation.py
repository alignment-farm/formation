"""Run the eight-world aggregate validation of staged-table revision."""

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
from contact import staged_table_revision_exploration as revision
from micro_environment.unselected_lineage_behavior import (
    FIRST_INCREASES,
    SECOND_INCREASES,
    LineageProfile,
    LineageState,
)


PROTOCOL_VERSION = "staged-table-revision-validation-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "STAGED_TABLE_REVISION_VALIDATION.md"
WORLDS = tuple(f"world_{index:02d}" for index in range(1, 9))
REPEATS = 3
LINEAGE_CALLS = len(WORLDS) * 8
PRE_ACTION_CALLS = (
    len(WORLDS) * len(revision.PRE_CASES) * len(revision.PRE_BRANCHES) * REPEATS
)
POST_ACTION_CALLS = (
    len(WORLDS) * len(revision.POST_CASES) * len(revision.POST_BRANCHES) * REPEATS
)
PLANNED_LOGICAL_CALLS = LINEAGE_CALLS + PRE_ACTION_CALLS + POST_ACTION_CALLS
PHYSICAL_CALL_CEILING = 936
MAX_RETRIES = 8


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


def make_world(name: str, index: int) -> revision.World:
    initial_slot = FIRST_INCREASES if index % 2 else SECOND_INCREASES
    new_slot = SECOND_INCREASES if initial_slot == FIRST_INCREASES else FIRST_INCREASES
    family = opaque(f"{name}:family")
    profile = LineageProfile(family, initial_slot)
    new_profile = LineageProfile(family, new_slot)
    position = 1300 + index * 263
    acquisition = LineageState(
        family,
        opaque(f"{name}:acquisition-device"),
        position,
        position - 1,
        (opaque(f"{name}:acquisition-first"), opaque(f"{name}:acquisition-second")),
    )
    pre_cases = {}
    for case_index, case in enumerate(revision.PRE_CASES, 1):
        case_position = 2800 + index * 419 + case_index * 89
        pre_cases[case] = LineageState(
            family,
            opaque(f"{name}:{case}:device"),
            case_position,
            case_position + (1 if case.endswith("up") else -1),
            (opaque(f"{name}:{case}:first"), opaque(f"{name}:{case}:second")),
        )
    counter_position = 4300 + index * 307
    counter_state = LineageState(
        family,
        opaque(f"{name}:counter-device"),
        counter_position,
        counter_position - 1,
        (opaque(f"{name}:counter-first"), opaque(f"{name}:counter-second")),
    )
    post_cases = {}
    post_profiles = {}
    for case_index, case in enumerate(revision.POST_CASES, 1):
        matching = case.startswith("same")
        case_profile = new_profile if matching else LineageProfile(
            opaque(f"{name}:{case}:family"), initial_slot
        )
        case_position = 5400 + index * 547 + case_index * 97
        post_cases[case] = LineageState(
            case_profile.controller_family,
            opaque(f"{name}:{case}:device"),
            case_position,
            case_position + (1 if case.endswith("up") else -1),
            (opaque(f"{name}:{case}:first"), opaque(f"{name}:{case}:second")),
        )
        post_profiles[case] = case_profile
    return revision.World(
        name, profile, new_profile, acquisition, pre_cases, counter_state,
        post_cases, post_profiles
    )


WORLD_DATA = {name: make_world(name, index) for index, name in enumerate(WORLDS, 1)}


_CONFIGURATION = {
    "PROTOCOL_VERSION": PROTOCOL_VERSION,
    "SPEC_PATH": SPEC_PATH,
    "WORLDS": WORLDS,
    "REPEATS": REPEATS,
    "LINEAGE_CALLS": LINEAGE_CALLS,
    "PRE_ACTION_CALLS": PRE_ACTION_CALLS,
    "POST_ACTION_CALLS": POST_ACTION_CALLS,
    "PLANNED_LOGICAL_CALLS": PLANNED_LOGICAL_CALLS,
    "PHYSICAL_CALL_CEILING": PHYSICAL_CALL_CEILING,
    "MAX_RETRIES": MAX_RETRIES,
    "WORLD_DATA": WORLD_DATA,
}


@contextmanager
def configured_revision():
    original = {name: getattr(revision, name) for name in _CONFIGURATION}
    try:
        for name, value in _CONFIGURATION.items():
            setattr(revision, name, value)
        yield
    finally:
        for name, value in original.items():
            setattr(revision, name, value)


def specimen() -> dict[str, Any]:
    with configured_revision():
        result = revision.specimen()
    result["initial_relation_groups"] = {
        relation: [
            name for name, world in WORLD_DATA.items()
            if world.profile.increasing_slot == relation
        ]
        for relation in (FIRST_INCREASES, SECOND_INCREASES)
    }
    result["changed_relation_groups"] = {
        relation: [
            name for name, world in WORLD_DATA.items()
            if world.new_profile.increasing_slot == relation
        ]
        for relation in (FIRST_INCREASES, SECOND_INCREASES)
    }
    return result


def score(packet: dict[str, Any]) -> dict[str, Any]:
    pre_dist = packet["pre_change_distributions"]
    post_dist = packet["post_change_distributions"]

    def total(dist, branch, cases, worlds=WORLDS):
        return sum(
            dist[name][branch][case]["correct_actions"]
            for name in worlds for case in cases
        )

    pre_scores = {
        branch: total(pre_dist, branch, revision.PRE_CASES)
        for branch in revision.PRE_BRANCHES
    }
    matching_cases = ("same_up", "same_down")
    unrelated_cases = ("other_up", "other_down")
    post_matching = {
        branch: total(post_dist, branch, matching_cases)
        for branch in revision.POST_BRANCHES
    }
    post_unrelated = {
        branch: total(post_dist, branch, unrelated_cases)
        for branch in revision.POST_BRANCHES
    }
    pre_direction = {
        "up": total(pre_dist, revision.PRE_OLD, ("pre_up",)),
        "down": total(pre_dist, revision.PRE_OLD, ("pre_down",)),
    }
    post_direction = {
        branch: {
            "up": total(post_dist, branch, ("same_up",)),
            "down": total(post_dist, branch, ("same_down",)),
        }
        for branch in (revision.REVISED, revision.STATIC_NEW)
    }
    relation_scores = {}
    quadrant_scores = {}
    for relation in (FIRST_INCREASES, SECOND_INCREASES):
        names = tuple(
            name for name, world in WORLD_DATA.items()
            if world.new_profile.increasing_slot == relation
        )
        relation_scores[relation] = {
            branch: total(post_dist, branch, matching_cases, names)
            for branch in (revision.REVISED, revision.STATIC_NEW)
        }
        quadrant_scores[relation] = {
            "up": total(post_dist, revision.REVISED, ("same_up",), names),
            "down": total(post_dist, revision.REVISED, ("same_down",), names),
        }
    every_cell_valid = all(
        post_dist[name][branch][case]["invalid_or_unavailable"] <= 1
        for name in WORLDS
        for branch in revision.POST_BRANCHES
        for case in revision.POST_CASES
    )
    unrelated_loss = post_unrelated[revision.POST_COLD] - post_unrelated[revision.REVISED]
    gate_errors_prevented = (
        post_unrelated[revision.REVISED] - post_unrelated[revision.UNGATED]
    )
    exact = packet["exact_authorship_counts"]
    engaged = (
        all(count >= 7 for count in exact.values())
        and pre_scores[revision.PRE_OLD] >= 43
        and all(score >= 21 for score in pre_direction.values())
        and packet["counter_actions_old_policy_consistent"] >= 7
        and post_matching[revision.STATIC_NEW] >= 43
        and all(score >= 21 for score in post_direction[revision.STATIC_NEW].values())
        and all(
            scores[revision.STATIC_NEW] >= 21 for scores in relation_scores.values()
        )
    )
    harmful = engaged and unrelated_loss >= 6
    supported = (
        engaged
        and post_matching[revision.REVISED] >= 43
        and all(score >= 21 for score in post_direction[revision.REVISED].values())
        and all(
            scores[revision.REVISED] >= 21 for scores in relation_scores.values()
        )
        and all(
            score >= 9
            for directions in quadrant_scores.values()
            for score in directions.values()
        )
        and all(
            post_matching[revision.REVISED] - post_matching[branch] >= 16
            for branch in (revision.POST_COLD, revision.STALE, revision.REMOVED)
        )
        and all(
            post_matching[revision.REVISED] - post_matching[branch] >= 12
            for branch in (revision.RAW_COUNTER, revision.HIDDEN)
        )
        and post_matching[revision.STATIC_NEW] - post_matching[revision.REVISED] <= 3
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
        "every_post_branch_case_valid": every_cell_valid,
        "gate_errors_prevented": gate_errors_prevented,
        "post_direction_scores": post_direction,
        "post_matching_scores": post_matching,
        "post_relation_direction_scores": quadrant_scores,
        "post_relation_scores": relation_scores,
        "post_unrelated_scores": post_unrelated,
        "pre_change_direction_scores": pre_direction,
        "pre_change_scores": pre_scores,
        "revision_verdict": {
            "class": verdict_class,
            "scope": "staged_table_revision_validation",
        },
        "unrelated_loss": unrelated_loss,
    })
    return packet


Transport = Callable[[bytes], tuple[int, bytes]]


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    with configured_revision():
        packet = revision.execute(transport, evidence_dir)
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
        raise revision.prior.ValidationRefusal("retained_specimen_mismatch")
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
            raise revision.prior.ValidationRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise revision.prior.ValidationRefusal("evidence_replay_mismatch")
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
        args.evidence_dir = (
            Path("evidence") / f"staged-table-revision-validation-{run_id}"
        )
    started = time.monotonic()
    receipt = base.collect_provider_receipt()
    if not receipt["valid"]:
        raise revision.prior.ValidationRefusal("provider_identity_mismatch")
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
        "revision_verdict": packet["revision_verdict"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
