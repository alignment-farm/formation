"""Compare model-authored representation classes after one consequence."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Callable

from contact import distributional_developmental_comparison as base
from micro_environment.unselected_lineage_behavior import (
    FIRST_INCREASES,
    SECOND_INCREASES,
    LineageProfile,
    LineageState,
    ProposalReceipt,
    apply_committed_action,
)
from unselected_lineage_specimen import ACTION_RESPONSIBILITY, oracle_action


PROTOCOL_VERSION = "representation-class-exploration-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "REPRESENTATION_CLASS_EXPLORATION.md"
WITHHELD_SENTINEL = "EXTERNAL_RESULT_WITHHELD_REPRESENTATION_CLASS_V1"
EXPOSED = "result_exposed"
WITHHELD = "result_withheld"
FORMATS = ("relation_sentence", "effect_table", "target_policy")
WORLDS = ("world_a", "world_b")
MATCHING_CASES = ("same_up", "same_down")
NONMATCHING_CASES = ("other_up", "other_down")
MATCHING_CONDITIONS = (
    "empty",
    "exposed_relation_sentence",
    "withheld_relation_sentence",
    "exposed_effect_table",
    "withheld_effect_table",
    "exposed_target_policy",
    "withheld_target_policy",
)
NONMATCHING_CONDITIONS = (
    "empty",
    "ungated_relation_sentence",
    "ungated_effect_table",
    "ungated_target_policy",
)
REPEATS = 4
PLANNED_LOGICAL_CALLS = (
    len(WORLDS)
    + len(WORLDS) * len(FORMATS) * 2
    + len(WORLDS) * len(MATCHING_CASES) * len(MATCHING_CONDITIONS) * REPEATS
    + len(WORLDS) * len(NONMATCHING_CASES) * len(NONMATCHING_CONDITIONS) * REPEATS
)
PHYSICAL_CALL_CEILING = 198
MAX_RETRIES = 8


class RepresentationExplorationRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


@dataclass(frozen=True)
class World:
    name: str
    profile: LineageProfile
    other_profile: LineageProfile
    acquisition: LineageState
    matching_cases: dict[str, LineageState]
    nonmatching_cases: dict[str, LineageState]


def make_world(name: str, acquisition_up: bool) -> World:
    profile = LineageProfile(opaque(f"{name}:source-family"), SECOND_INCREASES)
    other_profile = LineageProfile(opaque(f"{name}:other-family"), FIRST_INCREASES)
    origin = 430 if acquisition_up else 680
    acquisition = LineageState(
        profile.controller_family,
        opaque(f"{name}:acquisition-device"),
        origin,
        origin + (1 if acquisition_up else -1),
        (opaque(f"{name}:acquisition-first"), opaque(f"{name}:acquisition-second")),
    )
    offset = 0 if name == "world_a" else 29
    matching = {
        "same_up": LineageState(
            profile.controller_family,
            opaque(f"{name}:same-up-device"),
            220 + offset,
            221 + offset,
            (opaque(f"{name}:same-up-first"), opaque(f"{name}:same-up-second")),
        ),
        "same_down": LineageState(
            profile.controller_family,
            opaque(f"{name}:same-down-device"),
            820 + offset,
            819 + offset,
            (opaque(f"{name}:same-down-first"), opaque(f"{name}:same-down-second")),
        ),
    }
    nonmatching = {
        "other_up": LineageState(
            other_profile.controller_family,
            opaque(f"{name}:other-up-device"),
            370 + offset,
            371 + offset,
            (opaque(f"{name}:other-up-first"), opaque(f"{name}:other-up-second")),
        ),
        "other_down": LineageState(
            other_profile.controller_family,
            opaque(f"{name}:other-down-device"),
            970 + offset,
            969 + offset,
            (opaque(f"{name}:other-down-first"), opaque(f"{name}:other-down-second")),
        ),
    }
    return World(name, profile, other_profile, acquisition, matching, nonmatching)


WORLD_DATA = {
    "world_a": make_world("world_a", True),
    "world_b": make_world("world_b", False),
}


AUTHORSHIP_SYSTEMS = {
    "relation_sentence": """You author retained guidance in a controlled cold-model experiment. You have no memory outside this request.

REPRESENTATION_FORMAT: relation_sentence
Use the occurrence and environment-issued result to infer what the first and second displayed controls do within this controller family.
Return exactly one sentence in this form:
For controller family <controller_family>, the first displayed control <increases or decreases> position and the second displayed control <decreases or increases> position.
Fill every item from the record. State the first control before the second. Return no commentary, action strings, brackets, or labels.""",
    "effect_table": """You author retained guidance in a controlled cold-model experiment. You have no memory outside this request.

REPRESENTATION_FORMAT: effect_table
Use the occurrence and environment-issued result to infer what the first and second displayed controls do within this controller family.
Return exactly one JSON object with these keys in this order:
{"controller_family":"<controller_family>","first_displayed_control_effect":"<increases_position or decreases_position>","second_displayed_control_effect":"<decreases_position or increases_position>"}
Fill every value from the record. Return no markdown, commentary, action strings, or extra keys.""",
    "target_policy": """You author retained guidance in a controlled cold-model experiment. You have no memory outside this request.

REPRESENTATION_FORMAT: target_policy
Use the occurrence and environment-issued result to infer which displayed slot should be chosen for targets above and below the current position within this controller family.
Return exactly one JSON object with these keys in this order:
{"controller_family":"<controller_family>","target_above_position":"<first_displayed_control or second_displayed_control>","target_below_position":"<second_displayed_control or first_displayed_control>"}
Fill every value from the record. Return no markdown, commentary, action strings, or extra keys.""",
}


def expected_representation(world: World, representation_format: str, opposite: bool = False) -> str:
    second_increases = world.profile.increasing_slot == SECOND_INCREASES
    if opposite:
        second_increases = not second_increases
    first_effect = "decreases" if second_increases else "increases"
    second_effect = "increases" if second_increases else "decreases"
    if representation_format == "relation_sentence":
        return (
            f"For controller family {world.profile.controller_family}, the first displayed control "
            f"{first_effect} position and the second displayed control {second_effect} position."
        )
    if representation_format == "effect_table":
        return base.canonical_json_bytes({
            "controller_family": world.profile.controller_family,
            "first_displayed_control_effect": f"{first_effect}_position",
            "second_displayed_control_effect": f"{second_effect}_position",
        }).decode()
    if representation_format == "target_policy":
        return base.canonical_json_bytes({
            "controller_family": world.profile.controller_family,
            "target_above_position": "second_displayed_control" if second_increases else "first_displayed_control",
            "target_below_position": "first_displayed_control" if second_increases else "second_displayed_control",
        }).decode()
    raise RepresentationExplorationRefusal("unknown_representation_format")


def action_body(state: LineageState, retained_material: str) -> bytes:
    record = {
        "device": base.public_device(state),
        "responsibility": ACTION_RESPONSIBILITY,
        "retained_material": retained_material,
    }
    user = f"ACTION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think"
    return base.envelope(base.ACTION_SYSTEM, user, base.ACTION_SETTINGS)


def authorship_body(
    world: World,
    proposal: ProposalReceipt,
    result: Any,
    exposure: str,
    representation_format: str,
) -> bytes:
    record = {
        "external_result": base.exposed_result(result) if exposure == EXPOSED else WITHHELD_SENTINEL,
        "occurrence": base.occurrence(world.acquisition, proposal),
        "responsibility": "Author the requested retained representation from this record.",
    }
    user = f"AUTHORSHIP REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think"
    return base.envelope(
        AUTHORSHIP_SYSTEMS[representation_format],
        user,
        {**base.AUTHORSHIP_SETTINGS, "max_tokens": 160},
    )


def all_cases(world: World) -> dict[str, LineageState]:
    return {**world.matching_cases, **world.nonmatching_cases}


def profile_for(world: World, case: str) -> LineageProfile:
    return world.profile if case in MATCHING_CASES else world.other_profile


def specimen() -> dict[str, Any]:
    return {
        "authorship_system_sha256": {
            key: base.sha256(value.encode()) for key, value in AUTHORSHIP_SYSTEMS.items()
        },
        "formats": list(FORMATS),
        "matching_conditions": list(MATCHING_CONDITIONS),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "nonmatching_conditions": list(NONMATCHING_CONDITIONS),
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "worlds": {
            name: {
                "acquisition": base.public_device(world.acquisition),
                "cases": {
                    case: {
                        "device": base.public_device(state),
                        "expected_action": oracle_action(state, profile_for(world, case)),
                    }
                    for case, state in all_cases(world).items()
                },
                "expected_representations": {
                    key: base.sha256(expected_representation(world, key).encode()) for key in FORMATS
                },
            }
            for name, world in WORLD_DATA.items()
        },
    }


def later_schedule() -> tuple[tuple[int, str, str, str], ...]:
    rows = []
    groups = (
        (MATCHING_CASES, MATCHING_CONDITIONS),
        (NONMATCHING_CASES, NONMATCHING_CONDITIONS),
    )
    for repeat in range(1, REPEATS + 1):
        for cases, conditions in groups:
            for case_offset, case in enumerate(cases):
                for condition_offset in range(len(conditions)):
                    condition = conditions[(repeat - 1 + condition_offset) % len(conditions)]
                    order = WORLDS if (repeat + case_offset + condition_offset) % 2 else tuple(reversed(WORLDS))
                    for name in order:
                        rows.append((repeat, name, case, condition))
    expected = PLANNED_LOGICAL_CALLS - len(WORLDS) - len(WORLDS) * len(FORMATS) * 2
    if len(rows) != expected:
        raise RepresentationExplorationRefusal("schedule_size_mismatch")
    return tuple(rows)


Transport = Callable[[bytes], tuple[int, bytes]]


class Recorder:
    def __init__(self, transport: Transport, evidence_dir: Path | None) -> None:
        self.transport = transport
        self.attempts_dir = None
        if evidence_dir is not None:
            evidence_dir.mkdir(parents=True, exist_ok=False)
            self.attempts_dir = evidence_dir / "attempts"
            self.attempts_dir.mkdir()
            (evidence_dir / "specimen.json").write_bytes(base.canonical_json_bytes(specimen()))
        self.physical = 0
        self.retries = 0
        self.attempts: list[dict[str, Any]] = []

    def call(self, logical_index: int, body: bytes) -> tuple[int | None, str | None, str, bool, object]:
        final = None
        for attempt in (1, 2):
            if self.physical >= PHYSICAL_CALL_CEILING:
                raise RepresentationExplorationRefusal("physical_call_ceiling")
            self.physical += 1
            status = None
            raw = b""
            error = None
            try:
                status, raw = self.transport(body)
            except ConnectionError as exc:
                error = str(exc)
            retryable = error is not None or status in {408, 429, 500, 502, 503, 504}
            invocation = f"rx{logical_index:03d}"
            meta = {
                "attempt": attempt,
                "error": error,
                "http_status": status,
                "invocation": invocation,
                "logical_index": logical_index,
                "request_sha256": base.sha256(body),
                "response_sha256": base.sha256(raw),
                "retryable": retryable,
            }
            self.attempts.append(meta)
            if self.attempts_dir is not None:
                stem = f"{self.physical:03d}-{invocation}-a{attempt}"
                (self.attempts_dir / f"{stem}.request.json").write_bytes(body)
                (self.attempts_dir / f"{stem}.response.bin").write_bytes(raw)
                (self.attempts_dir / f"{stem}.meta.json").write_text(
                    json.dumps(meta, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
            if retryable and attempt == 1 and self.retries < MAX_RETRIES:
                self.retries += 1
                continue
            final = status, error, raw
            break
        if final is None:
            raise RepresentationExplorationRefusal("logical_call_not_completed")
        status, error, raw = final
        content, available, provider = base.parse_content(raw, status)
        return status, error, content, available, provider.get("usage")


def matching_material(condition: str, candidates: dict[tuple[str, str, str], str], name: str) -> str:
    if condition == "empty":
        return ""
    short_exposure, representation_format = condition.split("_", 1)
    exposure = EXPOSED if short_exposure == "exposed" else WITHHELD
    return candidates[(name, exposure, representation_format)]


def nonmatching_material(condition: str, candidates: dict[tuple[str, str, str], str], name: str) -> str:
    if condition == "empty":
        return ""
    prefix = "ungated_"
    if not condition.startswith(prefix):
        raise RepresentationExplorationRefusal("unknown_nonmatching_condition")
    return candidates[(name, EXPOSED, condition.removeprefix(prefix))]


def _distribution(rows: list[dict[str, Any]]) -> dict[str, Any]:
    outcomes = [row["action"] if row["action"] is not None else f"<{row['availability']}>" for row in rows]
    return {
        "action_counts": dict(sorted(Counter(outcomes).items())),
        "assigned": len(rows),
        "correct_actions": sum(bool(row["correct_action"]) for row in rows),
        "invalid_or_unavailable": sum(row["availability"] != "available" for row in rows),
    }


def representation_findings(
    candidates: dict[tuple[str, str, str], str],
    distributions: dict[str, dict[str, dict[str, dict[str, Any]]]],
) -> dict[str, dict[str, Any]]:
    findings = {}
    for representation_format in FORMATS:
        authored_exact = all(
            candidates[(name, EXPOSED, representation_format)] == expected_representation(WORLD_DATA[name], representation_format)
            for name in WORLDS
        )
        direction_pass = {}
        for case in MATCHING_CASES:
            passed = True
            for name in WORLDS:
                exposed = distributions[name][f"exposed_{representation_format}"][case]
                withheld = distributions[name][f"withheld_{representation_format}"][case]
                empty = distributions[name]["empty"][case]
                passed &= exposed["correct_actions"] >= 3
                passed &= exposed["correct_actions"] - empty["correct_actions"] >= 2
                passed &= exposed["correct_actions"] - withheld["correct_actions"] >= 2
                passed &= exposed["invalid_or_unavailable"] <= 1
            direction_pass[case] = bool(passed)
        harmful_cells = []
        for name in WORLDS:
            for case in NONMATCHING_CASES:
                empty = distributions[name]["empty"][case]["correct_actions"]
                exposed = distributions[name][f"ungated_{representation_format}"][case]["correct_actions"]
                if empty - exposed >= 2:
                    harmful_cells.append(f"{name}:{case}")
        if not authored_exact:
            status = "not_authored"
        elif all(direction_pass.values()):
            status = "bidirectional_candidate"
        elif any(direction_pass.values()):
            status = "one_direction_only"
        else:
            status = "not_engaged"
        findings[representation_format] = {
            "authored_exact": authored_exact,
            "direction_pass": direction_pass,
            "status": status,
            "ungated_harmful_cells": harmful_cells,
        }
    return findings


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    recorder = Recorder(transport, evidence_dir)
    calls = []
    acquisitions: dict[str, tuple[ProposalReceipt, Any]] = {}
    for logical_index, name in enumerate(WORLDS, 1):
        world = WORLD_DATA[name]
        body = action_body(world.acquisition, "")
        status, error, content, content_available, usage = recorder.call(logical_index, body)
        availability, action = base.parse_action(content, world.acquisition)
        if status != 200 or error is not None:
            availability, action = "unavailable", None
        provider_available = status == 200 and error is None and content_available
        proposal = ProposalReceipt(provider_available, (action or content) if provider_available else "")
        result = apply_committed_action(world.acquisition, world.profile, proposal)
        acquisitions[name] = proposal, result
        calls.append({
            "action": action,
            "availability": availability,
            "correct_action": availability == "available" and action == oracle_action(world.acquisition, world.profile),
            "external_result": base.exposed_result(result),
            "invocation": f"rx{logical_index:03d}",
            "logical_index": logical_index,
            "provider_usage": usage,
            "request_sha256": base.sha256(body),
            "responsibility": "acquisition_action",
            "world": name,
        })

    candidates: dict[tuple[str, str, str], str] = {}
    authorship_order = [
        (name, exposure, representation_format)
        for representation_format in FORMATS
        for exposure in (EXPOSED, WITHHELD)
        for name in (WORLDS if exposure == EXPOSED else tuple(reversed(WORLDS)))
    ]
    for logical_index, (name, exposure, representation_format) in enumerate(authorship_order, len(WORLDS) + 1):
        world = WORLD_DATA[name]
        proposal, result = acquisitions[name]
        body = authorship_body(world, proposal, result, exposure, representation_format)
        status, error, content, content_available, usage = recorder.call(logical_index, body)
        available = status == 200 and error is None and content_available
        candidate = content if available else ""
        candidates[(name, exposure, representation_format)] = candidate
        calls.append({
            "available": available,
            "content": candidate,
            "content_sha256": base.sha256(candidate.encode()),
            "exact_expected_match": candidate == expected_representation(world, representation_format),
            "exact_opposite_match": candidate == expected_representation(world, representation_format, opposite=True),
            "exposure": exposure,
            "format": representation_format,
            "invocation": f"rx{logical_index:03d}",
            "logical_index": logical_index,
            "provider_usage": usage,
            "request_sha256": base.sha256(body),
            "responsibility": "intermediate_authorship",
            "world": name,
        })

    later = []
    start = len(WORLDS) + len(authorship_order) + 1
    for logical_index, (repeat, name, case, condition) in enumerate(later_schedule(), start):
        world = WORLD_DATA[name]
        state = all_cases(world)[case]
        if case in MATCHING_CASES:
            material = matching_material(condition, candidates, name)
        else:
            material = nonmatching_material(condition, candidates, name)
        body = action_body(state, material)
        status, error, content, content_available, usage = recorder.call(logical_index, body)
        availability, action = base.parse_action(content, state)
        if status != 200 or error is not None:
            availability, action = "unavailable", None
        provider_available = status == 200 and error is None and content_available
        proposal = ProposalReceipt(provider_available, (action or content) if provider_available else "")
        result = apply_committed_action(state, profile_for(world, case), proposal)
        row = {
            "action": action,
            "availability": availability,
            "case": case,
            "condition": condition,
            "correct_action": availability == "available" and action == oracle_action(state, profile_for(world, case)),
            "external_result": base.exposed_result(result),
            "invocation": f"rx{logical_index:03d}",
            "logical_index": logical_index,
            "proposal": asdict(proposal),
            "provider_usage": usage,
            "repeat": repeat,
            "request_sha256": base.sha256(body),
            "responsibility": "later_action",
            "retained_material_sha256": base.sha256(material.encode()),
            "world": name,
        }
        later.append(row)
        calls.append(row)

    distributions = {
        name: {
            condition: {
                case: _distribution([
                    row for row in later
                    if row["world"] == name and row["condition"] == condition and row["case"] == case
                ])
                for case in (
                    (*MATCHING_CASES, *NONMATCHING_CASES)
                    if condition == "empty"
                    else MATCHING_CASES if condition in MATCHING_CONDITIONS
                    else NONMATCHING_CASES
                )
            }
            for condition in (*MATCHING_CONDITIONS, *NONMATCHING_CONDITIONS[1:])
        }
        for name in WORLDS
    }
    findings = representation_findings(candidates, distributions)
    verdict = {
        "class": "candidate_found" if any(row["status"] == "bidirectional_candidate" for row in findings.values()) else "null",
        "scope": "representation_class_exploration",
    }
    packet = {
        "attempts": recorder.attempts,
        "calls": calls,
        "candidates": [
            {
                "content": candidates[(name, exposure, representation_format)],
                "exact_expected_match": candidates[(name, exposure, representation_format)] == expected_representation(WORLD_DATA[name], representation_format),
                "exact_opposite_match": candidates[(name, exposure, representation_format)] == expected_representation(WORLD_DATA[name], representation_format, opposite=True),
                "exposure": exposure,
                "format": representation_format,
                "world": name,
            }
            for name in WORLDS for representation_format in FORMATS for exposure in (EXPOSED, WITHHELD)
        ],
        "formation_verdict": None,
        "logical_calls": len(calls),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "representation_findings": findings,
        "representation_trial_verdict": verdict,
        "request_distributions": distributions,
        "retries": recorder.retries,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise RepresentationExplorationRefusal("retained_specimen_mismatch")
    retained = json.loads((evidence_dir / "packet.json").read_bytes())
    entries = []
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        request = (evidence_dir / "attempts" / f"{stem}.request.json").read_bytes()
        response = (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes()
        if base.sha256(request) != meta["request_sha256"] or base.sha256(response) != meta["response_sha256"]:
            raise RepresentationExplorationRefusal("retained_attempt_hash_mismatch")
        entries.append((request, response, meta))
    position = 0

    def replay_transport(body: bytes) -> tuple[int, bytes]:
        nonlocal position
        if position >= len(entries):
            raise RepresentationExplorationRefusal("missing_retained_attempt")
        request, response, meta = entries[position]
        position += 1
        if request != body:
            raise RepresentationExplorationRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(replay_transport)
    if position != len(entries) or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained):
        raise RepresentationExplorationRefusal("evidence_replay_mismatch")
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
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        args.evidence_dir = Path("evidence") / f"representation-class-exploration-{stamp}"
    started = time.monotonic()
    receipt = base.collect_provider_receipt()
    if not receipt["valid"]:
        raise RepresentationExplorationRefusal("provider_identity_mismatch")
    packet = execute(base.live_transport, args.evidence_dir)
    (args.evidence_dir / "provider.json").write_text(
        json.dumps(receipt, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    replay_evidence(args.evidence_dir)
    print(json.dumps({
        "elapsed_seconds": time.monotonic() - started,
        "evidence_dir": str(args.evidence_dir),
        "logical_calls": packet["logical_calls"],
        "physical_attempts": packet["physical_attempts"],
        "representation_trial_verdict": packet["representation_trial_verdict"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
