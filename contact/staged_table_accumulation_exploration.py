"""Explore coexistence and joint use of two staged effect tables."""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Callable

from contact import distributional_developmental_comparison as base
from contact import staged_chain_validation as prior
from contact import staged_table_revision_exploration as revision
from micro_environment.unselected_lineage_behavior import (
    FIRST_INCREASES,
    SECOND_INCREASES,
    LineageProfile,
    LineageState,
    ProposalReceipt,
    apply_committed_action,
)
from unselected_lineage_specimen import oracle_action


PROTOCOL_VERSION = "staged-table-accumulation-exploration-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "STAGED_TABLE_ACCUMULATION_EXPLORATION.md"
LINEAGES = tuple(f"lineage_{index:02d}" for index in range(1, 5))
CASES = ("a_up", "a_down", "b_up", "b_down", "other_up", "other_down")
COLD = "cold"
RAW = "both_raw_experiences"
GATED = "both_authored_gated"
JOINT = "both_authored_joint"
FIRST_ONLY = "first_table_only"
SECOND_ONLY = "second_table_only"
JOINT_STATIC = "both_supplied_joint"
GATED_STATIC = "both_supplied_gated"
BRANCHES = (
    COLD, RAW, GATED, JOINT, FIRST_ONLY, SECOND_ONLY, JOINT_STATIC, GATED_STATIC
)
REPEATS = 3
AUTHORSHIP_CALLS = len(LINEAGES) * 2 * 3
LATER_CALLS = len(LINEAGES) * len(CASES) * len(BRANCHES) * REPEATS
PLANNED_LOGICAL_CALLS = AUTHORSHIP_CALLS + LATER_CALLS
PHYSICAL_CALL_CEILING = 608
MAX_RETRIES = 8


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


@dataclass(frozen=True)
class Lineage:
    name: str
    profiles: dict[str, LineageProfile]
    acquisitions: dict[str, LineageState]
    cases: dict[str, LineageState]
    case_profiles: dict[str, LineageProfile]


def make_lineage(name: str, index: int) -> Lineage:
    a_slot = FIRST_INCREASES if index % 2 else SECOND_INCREASES
    b_slot = SECOND_INCREASES if a_slot == FIRST_INCREASES else FIRST_INCREASES
    profiles = {
        "a": LineageProfile(opaque(f"{name}:a-family"), a_slot),
        "b": LineageProfile(opaque(f"{name}:b-family"), b_slot),
    }
    acquisitions = {}
    for family_index, family in enumerate(("a", "b"), 1):
        position = 1400 + index * 277 + family_index * 101
        acquisitions[family] = LineageState(
            profiles[family].controller_family,
            opaque(f"{name}:{family}:acquisition-device"),
            position,
            position - 1,
            (
                opaque(f"{name}:{family}:acquisition-first"),
                opaque(f"{name}:{family}:acquisition-second"),
            ),
        )
    other_profile = LineageProfile(opaque(f"{name}:other-family"), FIRST_INCREASES)
    cases = {}
    case_profiles = {}
    for case_index, case in enumerate(CASES, 1):
        family = case.split("_", 1)[0]
        profile = profiles[family] if family in profiles else other_profile
        position = 3100 + index * 431 + case_index * 103
        cases[case] = LineageState(
            profile.controller_family,
            opaque(f"{name}:{case}:device"),
            position,
            position + (1 if case.endswith("up") else -1),
            (opaque(f"{name}:{case}:first"), opaque(f"{name}:{case}:second")),
        )
        case_profiles[case] = profile
    return Lineage(name, profiles, acquisitions, cases, case_profiles)


LINEAGE_DATA = {
    name: make_lineage(name, index) for index, name in enumerate(LINEAGES, 1)
}


def table_for(profile: LineageProfile) -> str:
    return revision.table_for_profile(profile)


def joint_material(table_a: str, table_b: str) -> str:
    return base.canonical_json_bytes({
        "retained_effect_tables": [table_a, table_b],
    }).decode()


def raw_material(artifacts: dict[str, Any]) -> str:
    return base.canonical_json_bytes({
        "raw_experiences": [
            base.experience_record(
                artifacts[family]["state"],
                artifacts[family]["proposal"],
                artifacts[family]["result"],
            )
            for family in ("a", "b")
        ],
    }).decode()


def specimen() -> dict[str, Any]:
    return {
        "authorship_calls": AUTHORSHIP_CALLS,
        "branches": list(BRANCHES),
        "cases": list(CASES),
        "later_calls": LATER_CALLS,
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "lineages": {
            name: {
                "acquisitions": {
                    family: base.public_device(state)
                    for family, state in lineage.acquisitions.items()
                },
                "cases": {
                    case: {
                        "device": base.public_device(state),
                        "expected_action": oracle_action(
                            state, lineage.case_profiles[case]
                        ),
                    }
                    for case, state in lineage.cases.items()
                },
                "expected_table_sha256": {
                    family: base.sha256(table_for(profile).encode())
                    for family, profile in lineage.profiles.items()
                },
            }
            for name, lineage in LINEAGE_DATA.items()
        },
    }


def schedule():
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_index, case in enumerate(CASES):
            for branch_index in range(len(BRANCHES)):
                branch = BRANCHES[(repeat - 1 + branch_index) % len(BRANCHES)]
                shift = (repeat + case_index + branch_index) % len(LINEAGES)
                order = LINEAGES[shift:] + LINEAGES[:shift]
                rows.extend((repeat, name, case, branch) for name in order)
    return tuple(rows)


@contextmanager
def configured_recorder():
    old_ceiling = prior.PHYSICAL_CALL_CEILING
    old_retries = prior.MAX_RETRIES
    try:
        prior.PHYSICAL_CALL_CEILING = PHYSICAL_CALL_CEILING
        prior.MAX_RETRIES = MAX_RETRIES
        yield
    finally:
        prior.PHYSICAL_CALL_CEILING = old_ceiling
        prior.MAX_RETRIES = old_retries


Transport = Callable[[bytes], tuple[int, bytes]]


def available_content(call_result):
    status, error, content, content_available, usage = call_result
    available = status == 200 and error is None and content_available
    return (content if available else ""), usage


def action_call(recorder, logical_index, state, profile, material):
    body = prior.action_body(state, material)
    status, error, content, content_available, usage = recorder.call(logical_index, body)
    availability, action = base.parse_action(content, state)
    if status != 200 or error is not None:
        availability, action = "unavailable", None
    provider_available = status == 200 and error is None and content_available
    proposal = ProposalReceipt(
        provider_available,
        (action or content) if provider_available else "",
    )
    result = apply_committed_action(state, profile, proposal)
    return body, availability, action, proposal, result, usage


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    with configured_recorder():
        recorder = prior.Recorder(transport, evidence_dir)
        if evidence_dir is not None:
            (evidence_dir / "specimen.json").write_bytes(base.canonical_json_bytes(specimen()))
        calls = []
        artifacts = {}
        logical_index = 0
        for name in LINEAGES:
            lineage = LINEAGE_DATA[name]
            artifacts[name] = {}
            for family in ("a", "b"):
                state = lineage.acquisitions[family]
                profile = lineage.profiles[family]
                logical_index += 1
                body, availability, action, proposal, result, usage = action_call(
                    recorder, logical_index, state, profile, ""
                )
                calls.append({
                    "responsibility": "acquisition",
                    "lineage": name,
                    "family_position": family,
                    "action": action,
                    "availability": availability,
                    "external_result": base.exposed_result(result),
                    "provider_usage": usage,
                    "request_sha256": base.sha256(body),
                })
                logical_index += 1
                body = revision.observation_body(state, proposal, result, True)
                observation, usage = available_content(recorder.call(logical_index, body))
                fields = base.exposed_result(result)
                view = type("WorldView", (), {"profile": profile})()
                expected_observation = prior.staged.expected_observation(
                    view,
                    fields.get("selected_slot", ""),
                    fields.get("movement_direction", ""),
                )
                calls.append({
                    "responsibility": "observation_authorship",
                    "lineage": name,
                    "family_position": family,
                    "content": observation,
                    "exact": observation == expected_observation,
                    "provider_usage": usage,
                    "request_sha256": base.sha256(body),
                })
                logical_index += 1
                body = revision.staged_table_body(state, observation)
                table, usage = available_content(recorder.call(logical_index, body))
                calls.append({
                    "responsibility": "table_authorship",
                    "lineage": name,
                    "family_position": family,
                    "content": table,
                    "exact": table == table_for(profile),
                    "provider_usage": usage,
                    "request_sha256": base.sha256(body),
                })
                artifacts[name][family] = {
                    "state": state,
                    "proposal": proposal,
                    "result": result,
                    "table": table,
                }

        later = []
        for repeat, name, case, branch in schedule():
            logical_index += 1
            lineage = LINEAGE_DATA[name]
            state = lineage.cases[case]
            profile = lineage.case_profiles[case]
            family = case.split("_", 1)[0]
            artifact = artifacts[name]
            if branch == COLD:
                material = ""
            elif branch == RAW:
                material = raw_material(artifact)
            elif branch == GATED:
                material = artifact[family]["table"] if family in ("a", "b") else ""
            elif branch == JOINT:
                material = joint_material(artifact["a"]["table"], artifact["b"]["table"])
            elif branch == FIRST_ONLY:
                material = artifact["a"]["table"] if family == "a" else ""
            elif branch == SECOND_ONLY:
                material = artifact["b"]["table"] if family == "b" else ""
            elif branch == JOINT_STATIC:
                material = joint_material(
                    table_for(lineage.profiles["a"]), table_for(lineage.profiles["b"])
                )
            elif branch == GATED_STATIC:
                material = table_for(lineage.profiles[family]) if family in ("a", "b") else ""
            else:  # pragma: no cover
                raise AssertionError(branch)
            body, availability, action, proposal, result, usage = action_call(
                recorder, logical_index, state, profile, material
            )
            row = {
                "responsibility": "later_action",
                "lineage": name,
                "case": case,
                "branch": branch,
                "repeat": repeat,
                "action": action,
                "availability": availability,
                "correct_action": (
                    availability == "available" and action == oracle_action(state, profile)
                ),
                "external_result": base.exposed_result(result),
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
                "retained_material_sha256": base.sha256(material.encode()),
            }
            later.append(row)
            calls.append(row)

    distributions = {
        name: {
            branch: {
                case: {
                    "assigned": len(cell := [
                        row for row in later
                        if row["lineage"] == name
                        and row["branch"] == branch
                        and row["case"] == case
                    ]),
                    "correct_actions": sum(row["correct_action"] for row in cell),
                    "invalid_or_unavailable": sum(
                        row["availability"] != "available" for row in cell
                    ),
                    "distinct_outcomes": len(Counter(
                        row["action"] or f"<{row['availability']}" for row in cell
                    )),
                }
                for case in CASES
            }
            for branch in BRANCHES
        }
        for name in LINEAGES
    }

    def total(branch, cases):
        return sum(
            distributions[name][branch][case]["correct_actions"]
            for name in LINEAGES for case in cases
        )

    matching_cases = ("a_up", "a_down", "b_up", "b_down")
    unrelated_cases = ("other_up", "other_down")
    matching_scores = {branch: total(branch, matching_cases) for branch in BRANCHES}
    unrelated_scores = {branch: total(branch, unrelated_cases) for branch in BRANCHES}
    family_scores = {
        branch: {
            "a": total(branch, ("a_up", "a_down")),
            "b": total(branch, ("b_up", "b_down")),
        }
        for branch in BRANCHES
    }
    direction_scores = {
        branch: {
            "up": total(branch, ("a_up", "b_up")),
            "down": total(branch, ("a_down", "b_down")),
        }
        for branch in BRANCHES
    }
    exact_observations = sum(
        row["exact"] for row in calls if row["responsibility"] == "observation_authorship"
    )
    exact_tables = sum(
        row["exact"] for row in calls if row["responsibility"] == "table_authorship"
    )
    every_cell_valid = all(
        distributions[name][branch][case]["invalid_or_unavailable"] <= 1
        for name in LINEAGES for branch in BRANCHES for case in CASES
    )
    unrelated_loss = unrelated_scores[COLD] - unrelated_scores[GATED]
    engaged = (
        exact_observations == 8
        and exact_tables == 8
        and matching_scores[GATED_STATIC] >= 43
        and all(score >= 21 for score in family_scores[GATED_STATIC].values())
        and all(score >= 21 for score in direction_scores[GATED_STATIC].values())
    )
    harmful = engaged and unrelated_loss >= 6
    candidate = (
        engaged
        and matching_scores[GATED] >= 43
        and all(score >= 21 for score in family_scores[GATED].values())
        and all(score >= 21 for score in direction_scores[GATED].values())
        and matching_scores[JOINT] >= 40
        and all(score >= 19 for score in family_scores[JOINT].values())
        and all(score >= 19 for score in direction_scores[JOINT].values())
        and matching_scores[GATED] - matching_scores[COLD] >= 16
        and matching_scores[GATED] - matching_scores[RAW] >= 16
        and family_scores[FIRST_ONLY]["a"] - family_scores[GATED]["a"] <= 3
        and family_scores[SECOND_ONLY]["b"] - family_scores[GATED]["b"] <= 3
        and matching_scores[JOINT_STATIC] - matching_scores[JOINT] <= 4
        and matching_scores[GATED_STATIC] - matching_scores[GATED] <= 3
        and unrelated_loss <= 3
        and every_cell_valid
    )
    verdict_class = (
        "not_engaged" if not engaged
        else "harmful" if harmful
        else "candidate_found" if candidate
        else "null"
    )
    packet = {
        "accumulation_verdict": {
            "class": verdict_class,
            "scope": "staged_table_accumulation_exploration",
        },
        "attempts": recorder.attempts,
        "calls": calls,
        "direction_scores": direction_scores,
        "every_branch_case_valid": every_cell_valid,
        "exact_observations": exact_observations,
        "exact_tables": exact_tables,
        "family_scores": family_scores,
        "formation_verdict": None,
        "logical_calls": len(calls),
        "matching_scores": matching_scores,
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "request_distributions": distributions,
        "retries": recorder.retries,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "unrelated_loss": unrelated_loss,
        "unrelated_scores": unrelated_scores,
    }
    if evidence_dir is not None:
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
        args.evidence_dir = Path("evidence") / f"staged-table-accumulation-{run_id}"
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
        "accumulation_verdict": packet["accumulation_verdict"],
        "elapsed_seconds": time.monotonic() - started,
        "evidence_dir": str(args.evidence_dir),
        "logical_calls": packet["logical_calls"],
        "physical_attempts": packet["physical_attempts"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
