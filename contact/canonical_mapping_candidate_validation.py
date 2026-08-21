"""Execute the frozen canonical mapping candidate validation."""

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

from contact import canonical_mapping_authorship_contact as authorship
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


PROTOCOL_VERSION = "canonical-mapping-candidate-validation-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "CANONICAL_MAPPING_CANDIDATE_VALIDATION.md"
WITHHELD_SENTINEL = "EXTERNAL_RESULT_WITHHELD_CANONICAL_VALIDATION_V1"
EXPOSED = "result_exposed"
WITHHELD = "result_withheld"
COLD = "cold"
RAW = "raw"
AUTHORED_UNGATED = "authored_ungated"
GOVERNED = "governed"
DELIVERY_ABLATION = "delivery_ablation"
WITHHELD_GOVERNED = "consequence_withheld_governed"
ORACLE_STATIC = "oracle_static_scoped"
BRANCHES = (
    COLD,
    RAW,
    AUTHORED_UNGATED,
    GOVERNED,
    DELIVERY_ABLATION,
    WITHHELD_GOVERNED,
    ORACLE_STATIC,
)
CASES = ("same_family_up", "same_family_down", "other_family_up")
WORLDS = ("world_a", "world_b")
REPEATS = 6
PLANNED_LOGICAL_CALLS = 2 + 4 + len(WORLDS) * len(BRANCHES) * len(CASES) * REPEATS
PHYSICAL_CALL_CEILING = 266
MAX_RETRIES = 8


class CandidateValidationRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


@dataclass(frozen=True)
class World:
    name: str
    profile: LineageProfile
    other_profile: LineageProfile
    acquisition: LineageState
    cases: dict[str, LineageState]


def make_world(name: str, acquisition_up: bool) -> World:
    profile = LineageProfile(opaque(f"{name}:source-family"), SECOND_INCREASES)
    other = LineageProfile(opaque(f"{name}:other-family"), FIRST_INCREASES)
    acquisition_position = 430 if acquisition_up else 681
    acquisition = LineageState(
        profile.controller_family,
        opaque(f"{name}:acquisition-device"),
        acquisition_position,
        acquisition_position + (1 if acquisition_up else -1),
        (opaque(f"{name}:acquisition-first"), opaque(f"{name}:acquisition-second")),
    )
    cases = {
        "same_family_up": LineageState(
            profile.controller_family,
            opaque(f"{name}:same-up-device"),
            200 + (17 if name == "world_b" else 0),
            201 + (17 if name == "world_b" else 0),
            (opaque(f"{name}:same-up-first"), opaque(f"{name}:same-up-second")),
        ),
        "same_family_down": LineageState(
            profile.controller_family,
            opaque(f"{name}:same-down-device"),
            830 + (19 if name == "world_b" else 0),
            829 + (19 if name == "world_b" else 0),
            (opaque(f"{name}:same-down-first"), opaque(f"{name}:same-down-second")),
        ),
        "other_family_up": LineageState(
            other.controller_family,
            opaque(f"{name}:other-up-device"),
            510 + (23 if name == "world_b" else 0),
            511 + (23 if name == "world_b" else 0),
            (opaque(f"{name}:other-up-first"), opaque(f"{name}:other-up-second")),
        ),
    }
    return World(name, profile, other, acquisition, cases)


WORLD_DATA = {
    "world_a": make_world("world_a", True),
    "world_b": make_world("world_b", False),
}


def profile_for(world: World, case: str) -> LineageProfile:
    return world.other_profile if case == "other_family_up" else world.profile


def static_mapping(world: World) -> str:
    return (
        f"For controller family {world.profile.controller_family}, the first displayed control "
        "decreases position and the second displayed control increases position."
    )


def action_body(state: LineageState, retained_material: str) -> bytes:
    record = {
        "device": base.public_device(state),
        "responsibility": ACTION_RESPONSIBILITY,
        "retained_material": retained_material,
    }
    user = f"ACTION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think"
    return base.envelope(base.ACTION_SYSTEM, user, base.ACTION_SETTINGS)


def authorship_body(world: World, proposal: ProposalReceipt, result: Any, exposure: str) -> bytes:
    external_result: object = base.exposed_result(result) if exposure == EXPOSED else WITHHELD_SENTINEL
    record = {
        "external_result": external_result,
        "occurrence": base.occurrence(world.acquisition, proposal),
        "responsibility": authorship.AUTHORSHIP_RESPONSIBILITY,
    }
    user = f"AUTHORSHIP REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think"
    return base.envelope(authorship.AUTHORSHIP_SYSTEM, user, {**base.AUTHORSHIP_SETTINGS, "max_tokens": 128})


def specimen() -> dict[str, Any]:
    return {
        "branches": list(BRANCHES),
        "cases": list(CASES),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
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
                    for case, state in world.cases.items()
                },
                "static_mapping_sha256": base.sha256(static_mapping(world).encode()),
            }
            for name, world in WORLD_DATA.items()
        },
    }


def later_schedule() -> tuple[tuple[int, str, str, str], ...]:
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_offset in range(len(CASES)):
            case = CASES[(repeat - 1 + case_offset) % len(CASES)]
            for branch_offset in range(len(BRANCHES)):
                branch = BRANCHES[(repeat - 1 + branch_offset) % len(BRANCHES)]
                world_order = WORLDS if (repeat + case_offset + branch_offset) % 2 else tuple(reversed(WORLDS))
                for world_name in world_order:
                    rows.append((repeat, world_name, case, branch))
    if len(rows) != PLANNED_LOGICAL_CALLS - 6:
        raise CandidateValidationRefusal("schedule_size_mismatch")
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
                raise CandidateValidationRefusal("physical_call_ceiling")
            self.physical += 1
            status = None
            raw = b""
            error = None
            try:
                status, raw = self.transport(body)
            except ConnectionError as exc:
                error = str(exc)
            retryable = error is not None or status in {408, 429, 500, 502, 503, 504}
            invocation = f"vv{logical_index:03d}"
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
                    json.dumps(meta, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8"
                )
            if retryable and attempt == 1 and self.retries < MAX_RETRIES:
                self.retries += 1
                continue
            final = status, error, raw
            break
        if final is None:
            raise CandidateValidationRefusal("logical_call_not_completed")
        status, error, raw = final
        content, available, provider = base.parse_content(raw, status)
        return status, error, content, available, provider.get("usage")


def _distribution(rows: list[dict[str, Any]]) -> dict[str, Any]:
    outcomes = [row["action"] if row["action"] is not None else f"<{row['availability']}>" for row in rows]
    return {
        "action_counts": dict(sorted(Counter(outcomes).items())),
        "assigned": len(rows),
        "correct_actions": sum(bool(row["correct_action"]) for row in rows),
        "invalid_or_unavailable": sum(row["availability"] != "available" for row in rows),
    }


def branch_material(
    world: World,
    case: str,
    branch: str,
    proposal: ProposalReceipt,
    result: Any,
    candidates: dict[tuple[str, str], str],
) -> str:
    state = world.cases[case]
    matches = state.controller_family == world.profile.controller_family
    if branch in (COLD, DELIVERY_ABLATION):
        return ""
    if branch == RAW:
        return base.canonical_json_bytes(base.experience_record(world.acquisition, proposal, result)).decode()
    if branch == AUTHORED_UNGATED:
        return candidates[(world.name, EXPOSED)]
    if branch == GOVERNED:
        return candidates[(world.name, EXPOSED)] if matches else ""
    if branch == WITHHELD_GOVERNED:
        return candidates[(world.name, WITHHELD)] if matches else ""
    if branch == ORACLE_STATIC:
        return static_mapping(world) if matches else ""
    raise CandidateValidationRefusal("unknown_branch")


def _candidate_verdict(
    distributions: dict[str, dict[str, dict[str, dict[str, Any]]]],
    candidates: dict[tuple[str, str], str],
) -> dict[str, str]:
    if any(candidates[(name, EXPOSED)] != static_mapping(WORLD_DATA[name]) for name in WORLDS):
        return {"class": "not_engaged", "scope": "acquisition_transfer_selectivity"}
    for name in WORLDS:
        for case in ("same_family_up", "same_family_down"):
            if distributions[name][ORACLE_STATIC][case]["correct_actions"] < 5:
                return {"class": "not_engaged", "scope": "acquisition_transfer_selectivity"}
    for name in WORLDS:
        if (
            distributions[name][GOVERNED]["other_family_up"]["correct_actions"]
            <= distributions[name][COLD]["other_family_up"]["correct_actions"] - 3
        ):
            return {"class": "harmful", "scope": "acquisition_transfer_selectivity"}
    supported = True
    for name in WORLDS:
        for case in ("same_family_up", "same_family_down"):
            governed = distributions[name][GOVERNED][case]["correct_actions"]
            supported &= governed >= 5
            for baseline in (COLD, RAW, DELIVERY_ABLATION, WITHHELD_GOVERNED):
                supported &= governed - distributions[name][baseline][case]["correct_actions"] >= 4
        supported &= (
            distributions[name][GOVERNED]["other_family_up"]["correct_actions"]
            >= distributions[name][COLD]["other_family_up"]["correct_actions"] - 1
        )
        supported &= (
            distributions[name][GOVERNED]["other_family_up"]["correct_actions"]
            - distributions[name][AUTHORED_UNGATED]["other_family_up"]["correct_actions"] >= 4
        )
        for branch in BRANCHES:
            for case in CASES:
                supported &= distributions[name][branch][case]["invalid_or_unavailable"] <= 1
    return {"class": "supported" if supported else "null", "scope": "acquisition_transfer_selectivity"}


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
            "invocation": f"vv{logical_index:03d}",
            "logical_index": logical_index,
            "provider_usage": usage,
            "request_sha256": base.sha256(body),
            "responsibility": "acquisition_action",
            "world": name,
        })

    candidates: dict[tuple[str, str], str] = {}
    authorship_order = (("world_a", EXPOSED), ("world_b", WITHHELD), ("world_a", WITHHELD), ("world_b", EXPOSED))
    for logical_index, (name, exposure) in enumerate(authorship_order, 3):
        world = WORLD_DATA[name]
        proposal, result = acquisitions[name]
        body = authorship_body(world, proposal, result, exposure)
        status, error, content, content_available, usage = recorder.call(logical_index, body)
        available = status == 200 and error is None and content_available
        candidate = content if available else ""
        candidates[(name, exposure)] = candidate
        calls.append({
            "available": available,
            "content": candidate,
            "content_sha256": base.sha256(candidate.encode()),
            "exact_static_match": candidate == static_mapping(world),
            "exposure": exposure,
            "invocation": f"vv{logical_index:03d}",
            "logical_index": logical_index,
            "provider_usage": usage,
            "request_sha256": base.sha256(body),
            "responsibility": "intermediate_authorship",
            "world": name,
        })

    later = []
    for logical_index, (repeat, name, case, branch) in enumerate(later_schedule(), 7):
        world = WORLD_DATA[name]
        state = world.cases[case]
        proposal, result = acquisitions[name]
        material = branch_material(world, case, branch, proposal, result, candidates)
        body = action_body(state, material)
        status, error, content, content_available, usage = recorder.call(logical_index, body)
        availability, action = base.parse_action(content, state)
        if status != 200 or error is not None:
            availability, action = "unavailable", None
        provider_available = status == 200 and error is None and content_available
        later_proposal = ProposalReceipt(provider_available, (action or content) if provider_available else "")
        later_result = apply_committed_action(state, profile_for(world, case), later_proposal)
        row = {
            "action": action,
            "availability": availability,
            "branch": branch,
            "case": case,
            "correct_action": availability == "available" and action == oracle_action(state, profile_for(world, case)),
            "external_result": base.exposed_result(later_result),
            "invocation": f"vv{logical_index:03d}",
            "logical_index": logical_index,
            "proposal": asdict(later_proposal),
            "provider_usage": usage,
            "repeat": repeat,
            "request_sha256": base.sha256(body),
            "retained_material_sha256": base.sha256(material.encode()),
            "world": name,
        }
        later.append(row)
        calls.append({**row, "responsibility": "later_action"})

    distributions = {
        name: {
            branch: {
                case: _distribution([
                    row for row in later
                    if row["world"] == name and row["branch"] == branch and row["case"] == case
                ])
                for case in CASES
            }
            for branch in BRANCHES
        }
        for name in WORLDS
    }
    verdict = _candidate_verdict(distributions, candidates)
    packet = {
        "attempts": recorder.attempts,
        "calls": calls,
        "candidate_validation_verdict": verdict,
        "candidates": [
            {
                "content": candidates[(name, exposure)],
                "exact_static_match": candidates[(name, exposure)] == static_mapping(WORLD_DATA[name]),
                "exposure": exposure,
                "world": name,
            }
            for name in WORLDS for exposure in (EXPOSED, WITHHELD)
        ],
        "formation_verdict": None,
        "logical_calls": len(calls),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "request_distributions": distributions,
        "retries": recorder.retries,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "validation_verdict": verdict,
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise CandidateValidationRefusal("retained_specimen_mismatch")
    retained = json.loads((evidence_dir / "packet.json").read_bytes())
    entries = []
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        request = (evidence_dir / "attempts" / f"{stem}.request.json").read_bytes()
        response = (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes()
        if base.sha256(request) != meta["request_sha256"] or base.sha256(response) != meta["response_sha256"]:
            raise CandidateValidationRefusal("retained_attempt_hash_mismatch")
        entries.append((request, response, meta))
    position = 0

    def replay_transport(body: bytes) -> tuple[int, bytes]:
        nonlocal position
        if position >= len(entries):
            raise CandidateValidationRefusal("missing_retained_attempt")
        request, response, meta = entries[position]
        position += 1
        if request != body:
            raise CandidateValidationRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(replay_transport)
    if position != len(entries) or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained):
        raise CandidateValidationRefusal("evidence_replay_mismatch")
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
        args.evidence_dir = Path("evidence") / f"canonical-mapping-candidate-validation-{stamp}"
    started = time.monotonic()
    receipt = base.collect_provider_receipt()
    if not receipt["valid"]:
        raise CandidateValidationRefusal("provider_identity_mismatch")
    packet = execute(base.live_transport, args.evidence_dir)
    (args.evidence_dir / "provider.json").write_text(
        json.dumps(receipt, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    replay_evidence(args.evidence_dir)
    print(json.dumps({
        "candidate_validation_verdict": packet["candidate_validation_verdict"],
        "elapsed_seconds": time.monotonic() - started,
        "evidence_dir": str(args.evidence_dir),
        "logical_calls": packet["logical_calls"],
        "physical_attempts": packet["physical_attempts"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
