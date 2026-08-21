"""Test whether retained signal records cause self-directed probing."""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Callable

from contact import asymmetric_probe_clerical_contact as predecessor
from contact import composed_clerical_revision_validation as validation
from contact import distributional_developmental_comparison as base
from micro_environment import asymmetric_suspension as domain


PROTOCOL_VERSION = "self-directed-probe-contact-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "SELF_DIRECTED_PROBE_CONTACT.md"
PREDECESSOR_PACKET_PATH = (
    Path(__file__).parents[1]
    / "evidence"
    / "asymmetric-probe-clerical-contact-20260820T224335Z"
    / "packet.json"
)
PREDECESSOR_PACKET_SHA256 = (
    "4c7bf10b7ea53abe4f1a9b4ddd477674b07101fc92139c37ed9abc2c2a06f005"
)

PROFILE_0 = predecessor.PROFILE_0
PROFILE_1 = predecessor.PROFILE_1
UNMAPPED_0 = "unmapped_profile_0"
UNMAPPED_1 = "unmapped_profile_1"
KNOWN_WORLDS = (PROFILE_0, PROFILE_1)
UNMAPPED_WORLDS = (UNMAPPED_0, UNMAPPED_1)
WORLDS = KNOWN_WORLDS + UNMAPPED_WORLDS
WORLD_SLOTS = {
    PROFILE_0: domain.FIRST_SLOT,
    PROFILE_1: domain.SECOND_SLOT,
    UNMAPPED_0: domain.FIRST_SLOT,
    UNMAPPED_1: domain.SECOND_SLOT,
}
WORLD_SIGNALS = {
    PROFILE_0: domain.STEADY,
    PROFILE_1: domain.PULSED,
    UNMAPPED_0: domain.UNMAPPED,
    UNMAPPED_1: domain.UNMAPPED,
}

MATCHING_CASES = tuple(f"matching_{index:02d}" for index in range(1, 4))
UNMAPPED_CASES = ("unmapped_01",)
CASES = MATCHING_CASES + UNMAPPED_CASES

COLD = "cold"
RAW = "raw_source_occurrences"
LEARNED = "learned_signal_catalog"
REMOVED = "learned_catalog_removed"
SUPPLIED = "supplied_signal_catalog"
REVERSED = "supplied_reversed_catalog"
BRANCHES = (COLD, RAW, LEARNED, REMOVED, SUPPLIED, REVERSED)
ENGAGEMENT_BRANCHES = (LEARNED, SUPPLIED)

REPEATS = 3
EPISODES = (
    len(MATCHING_CASES) * len(KNOWN_WORLDS)
    + len(UNMAPPED_CASES) * len(UNMAPPED_WORLDS)
) * len(BRANCHES) * REPEATS
LOGICAL_CALL_CEILING = EPISODES * 2
PHYSICAL_CALL_CEILING = LOGICAL_CALL_CEILING + 12
MAX_RETRIES = 12

PARTICIPANT_SYSTEM = """You are the action-authoring component of a cold practitioner. You have no memory outside this request.

The device has two displayed task controls, one diagnostic control, and hold. Exactly one task control completes the task. The other irreversibly fails it. Diagnostic action leaves the device intact and emits a signal. Hold leaves it intact without information. Every action costs one step.

Retained signal records may state which displayed task slot completes after an exact diagnostic signal. They do not reveal the current hidden profile. Apply a record only when its signal exactly matches an environment-issued diagnostic result.

Choose one exact allowed action. Prefer completing the task without irreversible failure and with fewer actions.

Return exactly one JSON object with the single key action. Do not add keys or commentary."""


class SelfDirectedProbeRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


def load_predecessor_packet() -> dict[str, Any]:
    packet_bytes = PREDECESSOR_PACKET_PATH.read_bytes()
    if base.sha256(packet_bytes) != PREDECESSOR_PACKET_SHA256:
        raise SelfDirectedProbeRefusal("predecessor_packet_hash_mismatch")
    packet = json.loads(packet_bytes)
    if (
        packet.get("protocol_version") != predecessor.PROTOCOL_VERSION
        or packet.get("validation_verdict", {}).get("class") != "supported"
        or packet.get("formation_verdict") is not None
    ):
        raise SelfDirectedProbeRefusal("predecessor_packet_status_mismatch")
    return packet


def checked_learned_records(packet: dict[str, Any]) -> list[dict[str, str]]:
    components = packet.get("components", {})
    if (
        components.get("admitted_signal_records") != 2
        or components.get("exact_signal_records") != 2
        or not components.get("opposite_signal_records")
    ):
        raise SelfDirectedProbeRefusal("predecessor_record_components_mismatch")
    records = []
    for world in KNOWN_WORLDS:
        artifact = packet.get("source_artifacts", {}).get(world, {})
        record = artifact.get("record")
        if (
            artifact.get("admission", {}).get("status") != "admitted"
            or record != predecessor.expected_record(world)
        ):
            raise SelfDirectedProbeRefusal("predecessor_record_mismatch")
        records.append(record)
    return records


def make_state(case_name: str) -> domain.SuspensionState:
    return domain.SuspensionState(
        opaque(f"{case_name}:device"),
        (opaque(f"{case_name}:first"), opaque(f"{case_name}:second")),
        opaque(f"{case_name}:diagnostic"),
    )


STATES = {case_name: make_state(case_name) for case_name in CASES}


def worlds_for(case_name: str) -> tuple[str, str]:
    return KNOWN_WORLDS if case_name in MATCHING_CASES else UNMAPPED_WORLDS


def profile_for(state: domain.SuspensionState, world: str) -> domain.SuspensionProfile:
    return domain.SuspensionProfile(
        state.device,
        world,
        WORLD_SLOTS[world],
        WORLD_SIGNALS[world],
    )


def public_state(state: domain.SuspensionState) -> dict[str, Any]:
    return {
        "allowed_actions": [
            *state.task_controls,
            state.diagnostic_control,
            domain.HOLD,
        ],
        "device": state.device,
        "diagnostic_control": state.diagnostic_control,
        "status": state.status,
        "task_controls": list(state.task_controls),
    }


def exposed_result(result: domain.SuspensionResult) -> dict[str, Any]:
    return {
        "action": result.action,
        "diagnostic_signal": result.diagnostic_signal,
        "disposition": result.disposition,
        "observation": result.observation,
        "reason": result.reason,
        "status_after": result.status_after,
        "status_before": result.status_before,
        "step_cost": result.step_cost,
    }


def state_after(
    state: domain.SuspensionState, result: domain.SuspensionResult
) -> domain.SuspensionState:
    return domain.SuspensionState(
        state.device,
        state.task_controls,
        state.diagnostic_control,
        result.status_after,
    )


def render_catalog(records: list[dict[str, str]]) -> str:
    ordered = sorted(records, key=lambda row: row["diagnostic_signal"])
    return "SIGNAL RECORD CATALOG\n" + "\n".join(
        f"- {predecessor.render_record(record)}" for record in ordered
    )


def supplied_records() -> list[dict[str, str]]:
    return [predecessor.expected_record(world) for world in KNOWN_WORLDS]


def reversed_records() -> list[dict[str, str]]:
    return [
        {
            "diagnostic_signal": record["diagnostic_signal"],
            "valid_task_slot": (
                domain.SECOND_SLOT
                if record["valid_task_slot"] == domain.FIRST_SLOT
                else domain.FIRST_SLOT
            ),
        }
        for record in supplied_records()
    ]


def material_for(
    branch: str, packet: dict[str, Any], learned_records: list[dict[str, str]]
) -> str:
    if branch in {COLD, REMOVED}:
        return ""
    if branch == RAW:
        return base.canonical_json_bytes({
            "raw_source_occurrences": packet["source_occurrences"],
        }).decode()
    if branch == LEARNED:
        return render_catalog(learned_records)
    if branch == SUPPLIED:
        return render_catalog(supplied_records())
    if branch == REVERSED:
        return render_catalog(reversed_records())
    raise AssertionError(branch)


def participant_body(
    state: domain.SuspensionState,
    action_number: int,
    prior_results: list[dict[str, Any]],
    material: str,
) -> bytes:
    value = {
        "action_number": action_number,
        "device": public_state(state),
        "prior_external_results": prior_results,
        "responsibility": "Choose one allowed action for this device.",
        "retained_material": material,
    }
    return predecessor.learned.canonical_envelope(
        base.MODEL,
        PARTICIPANT_SYSTEM,
        f"DEVICE ACTION REQUEST\n{base.canonical_json_bytes(value).decode()}\n/no_think",
        base.ACTION_SETTINGS,
    )


def parse_action(
    content: str, state: domain.SuspensionState
) -> tuple[str, str | None]:
    try:
        value = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return "invalid", None
    allowed = (*state.task_controls, state.diagnostic_control, domain.HOLD)
    if (
        type(value) is not dict
        or set(value) != {"action"}
        or type(value["action"]) is not str
        or value["action"] not in allowed
    ):
        return "invalid", None
    return "available", value["action"]


def action_role(action: str | None, state: domain.SuspensionState) -> str:
    if action is None:
        return "not_applied"
    if action == state.task_controls[0]:
        return "first_task_control"
    if action == state.task_controls[1]:
        return "second_task_control"
    if action == state.diagnostic_control:
        return "diagnostic"
    if action == domain.HOLD:
        return "hold"
    raise AssertionError(action)


def episode_schedule() -> tuple[tuple[int, str, str, str], ...]:
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_index, case_name in enumerate(CASES):
            for branch_index in range(len(BRANCHES)):
                branch = BRANCHES[
                    (repeat - 1 + case_index + branch_index) % len(BRANCHES)
                ]
                world_order = worlds_for(case_name)
                if (repeat + case_index + branch_index) % 2 == 0:
                    world_order = world_order[::-1]
                rows.extend(
                    (repeat, world, case_name, branch) for world in world_order
                )
    return tuple(rows)


def specimen() -> dict[str, Any]:
    packet = load_predecessor_packet()
    records = checked_learned_records(packet)
    return {
        "branches": list(BRANCHES),
        "cases": {
            case_name: {
                "mapped": case_name in MATCHING_CASES,
                "public_state": public_state(state),
                "worlds": {
                    world: {
                        "diagnostic_signal": WORLD_SIGNALS[world],
                        "expected_task_action": state.task_controls[
                            0 if WORLD_SLOTS[world] == domain.FIRST_SLOT else 1
                        ],
                    }
                    for world in worlds_for(case_name)
                },
            }
            for case_name, state in STATES.items()
        },
        "episode_count": EPISODES,
        "learned_catalog_sha256": base.sha256(render_catalog(records).encode()),
        "logical_call_ceiling": LOGICAL_CALL_CEILING,
        "participant_model": base.MODEL,
        "participant_model_digest": base.MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "predecessor_packet_sha256": PREDECESSOR_PACKET_SHA256,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
    }


@contextmanager
def configured_recorder():
    verifier = validation.verifier
    old_ceiling = verifier.PHYSICAL_CALL_CEILING
    old_retries = verifier.MAX_RETRIES
    try:
        verifier.PHYSICAL_CALL_CEILING = PHYSICAL_CALL_CEILING
        verifier.MAX_RETRIES = MAX_RETRIES
        yield
    finally:
        verifier.PHYSICAL_CALL_CEILING = old_ceiling
        verifier.MAX_RETRIES = old_retries


Transport = Callable[[bytes], tuple[int, bytes]]


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    parent = load_predecessor_packet()
    learned_records = checked_learned_records(parent)
    materials = {
        branch: material_for(branch, parent, learned_records) for branch in BRANCHES
    }
    if materials[LEARNED] != materials[SUPPLIED]:
        raise SelfDirectedProbeRefusal("learned_supplied_catalog_mismatch")

    with configured_recorder():
        recorder = validation.verifier.Recorder(transport, evidence_dir)
        if evidence_dir is not None:
            (evidence_dir / "specimen.json").write_bytes(
                base.canonical_json_bytes(specimen())
            )
        logical_index = 0
        calls: list[dict[str, Any]] = []
        episodes: list[dict[str, Any]] = []

        for repeat, world, case_name, branch in episode_schedule():
            state = STATES[case_name]
            profile = profile_for(state, world)
            material = materials[branch]
            results: list[dict[str, Any]] = []
            episode_calls: list[dict[str, Any]] = []
            current_state = state

            for number in (1, 2):
                logical_index += 1
                body = participant_body(current_state, number, results, material)
                status, error, content, content_available, usage = recorder.call(
                    logical_index, body
                )
                availability, action = parse_action(content, current_state)
                if status != 200 or error is not None or not content_available:
                    availability, action = "unavailable", None

                role = action_role(action, current_state)
                if availability == "available" and action is not None:
                    result = domain.apply_action(current_state, profile, action)
                    external = exposed_result(result)
                    results.append(external)
                    current_state = state_after(current_state, result)
                else:
                    external = {
                        "disposition": "not_applied",
                        "reason": availability,
                    }

                row = {
                    "action": action,
                    "action_number": number,
                    "action_role": role,
                    "availability": availability,
                    "branch": branch,
                    "case": case_name,
                    "external_result": external,
                    "mapped": case_name in MATCHING_CASES,
                    "provider_usage": usage,
                    "repeat": repeat,
                    "request_sha256": base.sha256(body),
                    "responsibility": "participant_device_action",
                    "retained_material_sha256": base.sha256(material.encode()),
                    "world": world,
                }
                calls.append(row)
                episode_calls.append(row)

                terminal = current_state.status in {domain.COMPLETED, domain.FAILED}
                if number == 2 or terminal or availability != "available":
                    break

            first = episode_calls[0]
            second = episode_calls[1] if len(episode_calls) == 2 else None
            completed = current_state.status == domain.COMPLETED
            failed = current_state.status == domain.FAILED
            diagnostic_first = first["action_role"] == "diagnostic"
            second_task = (
                second is not None
                and second["action_role"]
                in {"first_task_control", "second_task_control"}
            )
            episodes.append({
                "action_cost": sum(
                    row["external_result"].get("step_cost", 0)
                    for row in episode_calls
                ),
                "branch": branch,
                "call_count": len(episode_calls),
                "case": case_name,
                "completed": completed,
                "diagnostic_first": diagnostic_first,
                "failed": failed,
                "first_action_role": first["action_role"],
                "mapped": case_name in MATCHING_CASES,
                "post_unmapped_task_attempt": (
                    case_name in UNMAPPED_CASES and diagnostic_first and second_task
                ),
                "repeat": repeat,
                "second_action_role": (
                    second["action_role"] if second is not None else None
                ),
                "unfinished": not completed and not failed,
                "world": world,
            })

    if len(episodes) != EPISODES or logical_index > LOGICAL_CALL_CEILING:
        raise SelfDirectedProbeRefusal("schedule_ceiling_mismatch")

    def count(branch: str, mapped: bool, field: str) -> int:
        return sum(
            row[field]
            for row in episodes
            if row["branch"] == branch and row["mapped"] is mapped
        )

    matching = {
        branch: {
            "action_cost": sum(
                row["action_cost"] for row in episodes
                if row["branch"] == branch and row["mapped"]
            ),
            "completed": count(branch, True, "completed"),
            "diagnostic_first": count(branch, True, "diagnostic_first"),
            "failed": count(branch, True, "failed"),
            "unfinished": count(branch, True, "unfinished"),
        }
        for branch in BRANCHES
    }
    unmapped = {
        branch: {
            "completed": count(branch, False, "completed"),
            "diagnostic_first": count(branch, False, "diagnostic_first"),
            "failed": count(branch, False, "failed"),
            "post_signal_task_attempts": count(
                branch, False, "post_unmapped_task_attempt"
            ),
            "unfinished": count(branch, False, "unfinished"),
        }
        for branch in BRANCHES
    }
    world_completions = {
        branch: {
            world: sum(
                row["completed"] for row in episodes
                if row["branch"] == branch
                and row["world"] == world
                and row["mapped"]
            )
            for world in KNOWN_WORLDS
        }
        for branch in BRANCHES
    }

    invalid_cells = []
    for branch in BRANCHES:
        for case_name in CASES:
            for world in worlds_for(case_name):
                invalid = sum(
                    row["availability"] != "available" for row in calls
                    if row["branch"] == branch
                    and row["case"] == case_name
                    and row["world"] == world
                )
                if invalid > 1:
                    invalid_cells.append({
                        "branch": branch,
                        "case": case_name,
                        "invalid": invalid,
                        "world": world,
                    })
    engagement_invalid = [
        row for row in invalid_cells if row["branch"] in ENGAGEMENT_BRANCHES
    ]

    def initial_identity(branches: set[str]) -> int:
        exact = 0
        for repeat in range(1, REPEATS + 1):
            for case_name in CASES:
                for world in worlds_for(case_name):
                    hashes = {
                        row["request_sha256"] for row in calls
                        if row["repeat"] == repeat
                        and row["case"] == case_name
                        and row["world"] == world
                        and row["action_number"] == 1
                        and row["branch"] in branches
                    }
                    exact += len(hashes) == 1
        return exact

    learned_supplied_identity = initial_identity({LEARNED, SUPPLIED})
    cold_removal_identity = initial_identity({COLD, REMOVED})
    public_pair_identities = sum(
        public_state(STATES[case_name]) == public_state(STATES[case_name])
        for case_name in CASES
    )
    environment_results_exact = sum(
        row["external_result"].get("status_after")
        in {domain.INTACT, domain.COMPLETED, domain.FAILED}
        and (
            row["action_role"] != "diagnostic"
            or row["external_result"].get("diagnostic_signal")
            == WORLD_SIGNALS[row["world"]]
        )
        for row in calls
        if row["availability"] == "available"
    )
    applied_results = sum(
        row["availability"] == "available" for row in calls
    )

    engaged = (
        matching[SUPPLIED]["diagnostic_first"] >= 16
        and matching[SUPPLIED]["completed"] >= 16
        and all(value >= 8 for value in world_completions[SUPPLIED].values())
        and not engagement_invalid
    )
    supported = (
        engaged
        and learned_supplied_identity == 24
        and cold_removal_identity == 24
        and public_pair_identities == 4
        and environment_results_exact == applied_results
        and matching[LEARNED]["diagnostic_first"] >= 16
        and matching[LEARNED]["completed"] >= 16
        and all(value >= 8 for value in world_completions[LEARNED].values())
        and matching[LEARNED]["failed"] <= 1
        and matching[LEARNED]["completed"] - matching[COLD]["completed"] >= 6
        and matching[LEARNED]["completed"] - matching[REMOVED]["completed"] >= 6
        and matching[SUPPLIED]["completed"] - matching[LEARNED]["completed"] <= 2
        and matching[REVERSED]["diagnostic_first"] >= 16
        and matching[REVERSED]["failed"] >= 14
        and unmapped[LEARNED]["diagnostic_first"] >= 5
        and unmapped[LEARNED]["post_signal_task_attempts"] <= 1
        and unmapped[LEARNED]["failed"] <= 1
    )
    harmful = engaged and (
        unmapped[LEARNED]["post_signal_task_attempts"] >= 3
        or unmapped[LEARNED]["failed"] >= 3
    )
    verdict_class = (
        "not_engaged" if not engaged
        else "harmful" if harmful
        else "supported" if supported
        else "null"
    )

    packet = {
        "attempts": recorder.attempts,
        "calls": calls,
        "components": {
            "applied_environment_results": applied_results,
            "exact_environment_results": environment_results_exact,
            "exact_predecessor_records": len(learned_records),
            "public_profile_pair_identities": public_pair_identities,
        },
        "engagement_invalid_participant_cells": engagement_invalid,
        "episode_count": len(episodes),
        "episodes": episodes,
        "formation_verdict": None,
        "initial_request_identity": {
            "cold_removal_pairs": cold_removal_identity,
            "learned_supplied_pairs": learned_supplied_identity,
        },
        "invalid_participant_cells": invalid_cells,
        "logical_calls": len(calls),
        "logical_call_ceiling": LOGICAL_CALL_CEILING,
        "matching_outcomes": matching,
        "physical_attempts": recorder.physical,
        "predecessor_packet_sha256": PREDECESSOR_PACKET_SHA256,
        "protocol_version": PROTOCOL_VERSION,
        "request_action_distributions": {
            branch: dict(Counter(
                row["action"] or f"<{row['availability']}>" for row in calls
                if row["branch"] == branch
            ))
            for branch in BRANCHES
        },
        "retries": recorder.retries,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "unmapped_outcomes": unmapped,
        "validation_verdict": {
            "class": verdict_class,
            "scope": "self_directed_probe_contact",
        },
        "world_completions": world_completions,
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(
        specimen()
    ):
        raise SelfDirectedProbeRefusal("retained_specimen_mismatch")
    retained = json.loads((evidence_dir / "packet.json").read_bytes())
    entries = []
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        entries.append((
            (evidence_dir / "attempts" / f"{stem}.request.json").read_bytes(),
            (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes(),
            json.loads(meta_path.read_text()),
        ))
    position = 0

    def transport(body: bytes) -> tuple[int, bytes]:
        nonlocal position
        request, response, meta = entries[position]
        position += 1
        if request != body:
            raise SelfDirectedProbeRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise SelfDirectedProbeRefusal("evidence_replay_mismatch")
    return replayed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args(argv)
    if not args.live:
        print(json.dumps({
            "episode_count": EPISODES,
            "logical_call_ceiling": LOGICAL_CALL_CEILING,
            "mode": "smoke_no_contact",
            "side_effects_entered": False,
        }, sort_keys=True))
        return 0
    evidence_dir = args.evidence_dir or Path("evidence") / (
        "self-directed-probe-contact-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    receipt = predecessor.learned.collect_provider_receipt()
    if not receipt["valid"]:
        raise SelfDirectedProbeRefusal("provider_identity_mismatch")
    started = time.monotonic()
    packet = execute(base.live_transport, evidence_dir)
    (evidence_dir / "provider.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    replay_evidence(evidence_dir)
    print(json.dumps({
        "elapsed_seconds": time.monotonic() - started,
        "episode_count": packet["episode_count"],
        "evidence_dir": str(evidence_dir),
        "logical_calls": packet["logical_calls"],
        "physical_attempts": packet["physical_attempts"],
        "validation_verdict": packet["validation_verdict"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
