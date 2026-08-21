"""Run the prospective four-world validation of staged lesson authorship."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Callable

from contact import distributional_developmental_comparison as base
from contact import representation_class_exploration as forms
from contact import staged_observation_authorship as staged
from micro_environment.unselected_lineage_behavior import (
    FIRST_INCREASES,
    SECOND_INCREASES,
    LineageProfile,
    LineageState,
    ProposalReceipt,
    apply_committed_action,
)
from unselected_lineage_specimen import ACTION_RESPONSIBILITY, oracle_action


PROTOCOL_VERSION = "staged-chain-validation-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "STAGED_CHAIN_VALIDATION.md"
WORLDS = tuple(f"world_{index:02d}" for index in range(1, 5))
CASES = ("same_up", "same_down", "other_up", "other_down")

COLD = "cold"
RAW = "raw_experience"
DIRECT = "direct_table_scoped"
EXPOSED = "exposed_staged_scoped"
WITHHELD = "withheld_staged_scoped"
REMOVED = "exposed_staged_removed"
UNGATED = "exposed_staged_ungated"
STATIC = "static_table_scoped"
BRANCHES = (COLD, RAW, DIRECT, EXPOSED, WITHHELD, REMOVED, UNGATED, STATIC)

REPEATS = 4
AUTHORSHIP_CALLS = len(WORLDS) * 6
LATER_CALLS = len(WORLDS) * len(CASES) * len(BRANCHES) * REPEATS
PLANNED_LOGICAL_CALLS = AUTHORSHIP_CALLS + LATER_CALLS
PHYSICAL_CALL_CEILING = 544
MAX_RETRIES = 8


class ValidationRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


@dataclass(frozen=True)
class World:
    name: str
    profile: LineageProfile
    acquisition: LineageState
    cases: dict[str, LineageState]
    case_profiles: dict[str, LineageProfile]


def make_world(name: str, index: int) -> World:
    profile = LineageProfile(opaque(f"{name}:family"), SECOND_INCREASES)
    position = 700 + index * 191
    acquisition = LineageState(
        profile.controller_family,
        opaque(f"{name}:acquisition-device"),
        position,
        position - 1,
        (opaque(f"{name}:acquisition-first"), opaque(f"{name}:acquisition-second")),
    )
    cases: dict[str, LineageState] = {}
    profiles: dict[str, LineageProfile] = {}
    for case_index, case in enumerate(CASES, 1):
        matching = case.startswith("same")
        case_profile = profile if matching else LineageProfile(
            opaque(f"{name}:{case}:family"), FIRST_INCREASES
        )
        case_position = 1200 + index * 433 + case_index * 61
        cases[case] = LineageState(
            case_profile.controller_family,
            opaque(f"{name}:{case}:device"),
            case_position,
            case_position + (1 if case.endswith("up") else -1),
            (opaque(f"{name}:{case}:first"), opaque(f"{name}:{case}:second")),
        )
        profiles[case] = case_profile
    return World(name, profile, acquisition, cases, profiles)


WORLD_DATA = {name: make_world(name, index) for index, name in enumerate(WORLDS, 1)}


def expected_table(world: World, opposite: bool = False) -> str:
    return forms.expected_representation(world, "effect_table", opposite=opposite)


def action_body(state: LineageState, retained_material: str) -> bytes:
    record = {
        "device": base.public_device(state),
        "responsibility": ACTION_RESPONSIBILITY,
        "retained_material": retained_material,
    }
    return base.envelope(
        base.ACTION_SYSTEM,
        f"ACTION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",
        base.ACTION_SETTINGS,
    )


def observation_body(
    world: World,
    proposal: ProposalReceipt,
    result: Any,
    expose_consequence: bool,
) -> bytes:
    record = {
        "external_result": (
            base.exposed_result(result) if expose_consequence else forms.WITHHELD_SENTINEL
        ),
        "occurrence": base.occurrence(world.acquisition, proposal),
    }
    return base.envelope(
        staged.OBSERVATION_SYSTEM,
        f"OBSERVATION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",
        {**base.AUTHORSHIP_SETTINGS, "max_tokens": 128},
    )


def staged_table_body(world: World, observation: str) -> bytes:
    record = {
        "authored_observation": observation,
        "public_device": base.public_device(world.acquisition),
        "responsibility": "Author the complete effect table.",
    }
    return base.envelope(
        staged.STAGED_TABLE_SYSTEM,
        f"TABLE REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",
        {**base.AUTHORSHIP_SETTINGS, "max_tokens": 160},
    )


def direct_table_body(world: World, proposal: ProposalReceipt, result: Any) -> bytes:
    record = {
        "external_result": base.exposed_result(result),
        "occurrence": base.occurrence(world.acquisition, proposal),
        "responsibility": "Author the complete effect table.",
    }
    return base.envelope(
        forms.AUTHORSHIP_SYSTEMS["effect_table"],
        f"TABLE REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",
        {**base.AUTHORSHIP_SETTINGS, "max_tokens": 160},
    )


def specimen() -> dict[str, Any]:
    return {
        "authorship_calls": AUTHORSHIP_CALLS,
        "branches": list(BRANCHES),
        "cases": list(CASES),
        "later_calls": LATER_CALLS,
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "observation_system_sha256": base.sha256(staged.OBSERVATION_SYSTEM.encode()),
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "staged_table_system_sha256": base.sha256(staged.STAGED_TABLE_SYSTEM.encode()),
        "worlds": {
            name: {
                "acquisition": base.public_device(world.acquisition),
                "cases": {
                    case: {
                        "device": base.public_device(state),
                        "expected_action": oracle_action(state, world.case_profiles[case]),
                    }
                    for case, state in world.cases.items()
                },
                "expected_table_sha256": base.sha256(expected_table(world).encode()),
            }
            for name, world in WORLD_DATA.items()
        },
    }


def later_schedule() -> tuple[tuple[int, str, str, str], ...]:
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_index, case in enumerate(CASES):
            for branch_index in range(len(BRANCHES)):
                branch = BRANCHES[(repeat - 1 + branch_index) % len(BRANCHES)]
                shift = (repeat + case_index + branch_index) % len(WORLDS)
                order = WORLDS[shift:] + WORLDS[:shift]
                rows.extend((repeat, name, case, branch) for name in order)
    return tuple(rows)


Transport = Callable[[bytes], tuple[int, bytes]]


class Recorder:
    def __init__(self, transport: Transport, evidence_dir: Path | None):
        self.transport = transport
        self.attempts_dir = None
        self.physical = 0
        self.retries = 0
        self.attempts: list[dict[str, Any]] = []
        if evidence_dir is not None:
            evidence_dir.mkdir(parents=True, exist_ok=False)
            self.attempts_dir = evidence_dir / "attempts"
            self.attempts_dir.mkdir()
            (evidence_dir / "specimen.json").write_bytes(base.canonical_json_bytes(specimen()))

    def call(self, logical_index: int, body: bytes):
        final = None
        for attempt in (1, 2):
            if self.physical >= PHYSICAL_CALL_CEILING:
                raise ValidationRefusal("physical_call_ceiling")
            self.physical += 1
            status, raw, error = None, b"", None
            try:
                status, raw = self.transport(body)
            except ConnectionError as exc:
                error = str(exc)
            retryable = error is not None or status in {408, 429, 500, 502, 503, 504}
            meta = {
                "attempt": attempt,
                "error": error,
                "http_status": status,
                "logical_index": logical_index,
                "request_sha256": base.sha256(body),
                "response_sha256": base.sha256(raw),
                "retryable": retryable,
            }
            self.attempts.append(meta)
            if self.attempts_dir is not None:
                stem = f"{self.physical:03d}-sv{logical_index:03d}-a{attempt}"
                (self.attempts_dir / f"{stem}.request.json").write_bytes(body)
                (self.attempts_dir / f"{stem}.response.bin").write_bytes(raw)
                (self.attempts_dir / f"{stem}.meta.json").write_text(
                    json.dumps(meta, indent=2, sort_keys=True) + "\n"
                )
            if retryable and attempt == 1 and self.retries < MAX_RETRIES:
                self.retries += 1
                continue
            final = status, error, raw
            break
        if final is None:
            raise ValidationRefusal("logical_call_not_completed")
        status, error, raw = final
        content, available, provider = base.parse_content(raw, status)
        return status, error, content, available, provider.get("usage")


def _available_content(call_result: tuple[Any, ...]) -> tuple[str, Any]:
    status, error, content, content_available, usage = call_result
    available = status == 200 and error is None and content_available
    return (content if available else ""), usage


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    recorder = Recorder(transport, evidence_dir)
    calls: list[dict[str, Any]] = []
    artifacts: dict[str, dict[str, Any]] = {}
    logical_index = 0

    for name in WORLDS:
        world = WORLD_DATA[name]
        logical_index += 1
        body = action_body(world.acquisition, "")
        status, error, content, content_available, usage = recorder.call(logical_index, body)
        availability, action = base.parse_action(content, world.acquisition)
        if status != 200 or error is not None:
            availability, action = "unavailable", None
        provider_available = status == 200 and error is None and content_available
        proposal = ProposalReceipt(
            provider_available,
            (action or content) if provider_available else "",
        )
        result = apply_committed_action(world.acquisition, world.profile, proposal)
        calls.append({
            "responsibility": "acquisition",
            "world": name,
            "action": action,
            "availability": availability,
            "external_result": base.exposed_result(result),
            "provider_usage": usage,
            "request_sha256": base.sha256(body),
        })

        observations = {}
        for exposure_name, expose_consequence in (("exposed", True), ("withheld", False)):
            logical_index += 1
            body = observation_body(world, proposal, result, expose_consequence)
            observation, usage = _available_content(recorder.call(logical_index, body))
            fields = base.exposed_result(result)
            expected = staged.expected_observation(
                world,
                fields.get("selected_slot", ""),
                fields.get("movement_direction", ""),
            )
            calls.append({
                "responsibility": "observation_authorship",
                "world": name,
                "exposure": exposure_name,
                "content": observation,
                "exact": observation == expected,
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
            })
            observations[exposure_name] = observation

        tables = {}
        for exposure_name in ("exposed", "withheld"):
            logical_index += 1
            body = staged_table_body(world, observations[exposure_name])
            authored, usage = _available_content(recorder.call(logical_index, body))
            calls.append({
                "responsibility": "staged_table_authorship",
                "world": name,
                "exposure": exposure_name,
                "content": authored,
                "exact": authored == expected_table(world),
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
            })
            tables[exposure_name] = authored

        logical_index += 1
        body = direct_table_body(world, proposal, result)
        direct, usage = _available_content(recorder.call(logical_index, body))
        calls.append({
            "responsibility": "direct_table_authorship",
            "world": name,
            "content": direct,
            "exact": direct == expected_table(world),
            "provider_usage": usage,
            "request_sha256": base.sha256(body),
        })
        artifacts[name] = {
            "proposal": proposal,
            "result": result,
            "direct": direct,
            "exposed": tables["exposed"],
            "withheld": tables["withheld"],
        }

    later = []
    for repeat, name, case, branch in later_schedule():
        logical_index += 1
        world = WORLD_DATA[name]
        state = world.cases[case]
        matching = case.startswith("same")
        artifact = artifacts[name]
        if branch in (COLD, REMOVED):
            material = ""
        elif branch == RAW:
            material = base.canonical_json_bytes(base.experience_record(
                world.acquisition, artifact["proposal"], artifact["result"]
            )).decode()
        elif branch == DIRECT:
            material = artifact["direct"] if matching else ""
        elif branch == EXPOSED:
            material = artifact["exposed"] if matching else ""
        elif branch == WITHHELD:
            material = artifact["withheld"] if matching else ""
        elif branch == UNGATED:
            material = artifact["exposed"]
        elif branch == STATIC:
            material = expected_table(world) if matching else ""
        else:  # pragma: no cover - BRANCHES is frozen above
            raise AssertionError(branch)

        body = action_body(state, material)
        status, error, content, content_available, usage = recorder.call(logical_index, body)
        availability, action = base.parse_action(content, state)
        if status != 200 or error is not None:
            availability, action = "unavailable", None
        provider_available = status == 200 and error is None and content_available
        receipt = ProposalReceipt(
            provider_available,
            (action or content) if provider_available else "",
        )
        external_result = apply_committed_action(state, world.case_profiles[case], receipt)
        row = {
            "responsibility": "later_action",
            "world": name,
            "case": case,
            "branch": branch,
            "repeat": repeat,
            "action": action,
            "availability": availability,
            "correct_action": (
                availability == "available"
                and action == oracle_action(state, world.case_profiles[case])
            ),
            "external_result": base.exposed_result(external_result),
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
                    "assigned": len(rows := [
                        row for row in later
                        if row["world"] == name
                        and row["branch"] == branch
                        and row["case"] == case
                    ]),
                    "correct_actions": sum(row["correct_action"] for row in rows),
                    "invalid_or_unavailable": sum(
                        row["availability"] != "available" for row in rows
                    ),
                    "distinct_outcomes": len(Counter(
                        row["action"] or f"<{row['availability']}>" for row in rows
                    )),
                }
                for case in CASES
            }
            for branch in BRANCHES
        }
        for name in WORLDS
    }

    def total(branch: str, cases: tuple[str, ...]) -> int:
        return sum(
            distributions[name][branch][case]["correct_actions"]
            for name in WORLDS
            for case in cases
        )

    matching_cases = ("same_up", "same_down")
    unrelated_cases = ("other_up", "other_down")
    matching_scores = {branch: total(branch, matching_cases) for branch in BRANCHES}
    unrelated_scores = {branch: total(branch, unrelated_cases) for branch in BRANCHES}
    direction_scores = {
        "up": total(EXPOSED, ("same_up",)),
        "down": total(EXPOSED, ("same_down",)),
        "static_up": total(STATIC, ("same_up",)),
        "static_down": total(STATIC, ("same_down",)),
    }
    exposed_observations_exact = sum(
        row["exact"]
        for row in calls
        if row["responsibility"] == "observation_authorship"
        and row["exposure"] == "exposed"
    )
    exposed_tables_exact = sum(
        row["exact"]
        for row in calls
        if row["responsibility"] == "staged_table_authorship"
        and row["exposure"] == "exposed"
    )
    every_cell_valid = all(
        distributions[name][branch][case]["invalid_or_unavailable"] <= 1
        for name in WORLDS
        for branch in BRANCHES
        for case in CASES
    )
    scope_errors_prevented = unrelated_scores[EXPOSED] - unrelated_scores[UNGATED]
    unrelated_loss = unrelated_scores[COLD] - unrelated_scores[EXPOSED]
    engaged = (
        exposed_observations_exact == len(WORLDS)
        and exposed_tables_exact == len(WORLDS)
        and direction_scores["static_up"] >= 14
        and direction_scores["static_down"] >= 14
    )
    harmful = engaged and unrelated_loss >= 4
    supported = (
        engaged
        and matching_scores[EXPOSED] >= 28
        and direction_scores["up"] >= 14
        and direction_scores["down"] >= 14
        and all(
            matching_scores[EXPOSED] - matching_scores[branch] >= 24
            for branch in (COLD, DIRECT, WITHHELD, REMOVED)
        )
        and matching_scores[EXPOSED] - matching_scores[RAW] >= 16
        and unrelated_loss <= 2
        and scope_errors_prevented >= 8
        and every_cell_valid
    )
    verdict_class = (
        "not_engaged" if not engaged
        else "harmful" if harmful
        else "supported" if supported
        else "null"
    )
    verdict = {"class": verdict_class, "scope": "staged_chain_validation"}
    packet = {
        "attempts": recorder.attempts,
        "calls": calls,
        "direction_scores": direction_scores,
        "every_branch_case_valid": every_cell_valid,
        "exposed_observations_exact": exposed_observations_exact,
        "exposed_tables_exact": exposed_tables_exact,
        "formation_verdict": None,
        "logical_calls": len(calls),
        "matching_scores": matching_scores,
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "request_distributions": distributions,
        "retries": recorder.retries,
        "scope_errors_prevented": scope_errors_prevented,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "unrelated_loss": unrelated_loss,
        "unrelated_scores": unrelated_scores,
        "validation_verdict": verdict,
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise ValidationRefusal("retained_specimen_mismatch")
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
            raise ValidationRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise ValidationRefusal("evidence_replay_mismatch")
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
        args.evidence_dir = Path("evidence") / f"staged-chain-validation-{run_id}"
    started = time.monotonic()
    receipt = base.collect_provider_receipt()
    if not receipt["valid"]:
        raise ValidationRefusal("provider_identity_mismatch")
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
