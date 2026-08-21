"""Test learned signal records in the asymmetric suspension domain."""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Callable

from contact import asymmetric_suspension_domain_specimen as domain_specimen
from contact import composed_clerical_revision_validation as validation
from contact import distributional_developmental_comparison as base
from contact import learned_clerical_instrument_exploration as learned
from micro_environment import asymmetric_suspension as domain


PROTOCOL_VERSION = "asymmetric-probe-clerical-contact-v1"
SPEC_PATH = (
    Path(__file__).parents[1] / "docs" / "ASYMMETRIC_PROBE_CLERICAL_CONTACT.md"
)
DOMAIN_PACKET_PATH = (
    Path(__file__).parents[1]
    / "evidence"
    / "asymmetric-suspension-domain-20260820T223216Z"
    / "packet.json"
)
DOMAIN_PACKET_SHA256 = (
    "ae76cdc2f41a608b50bc78a6bb701206f0640655a8dc5450f931925855238a31"
)
DOMAIN_PROTOCOL_VERSION = domain_specimen.PROTOCOL_VERSION

PROFILE_0 = "profile_0"
PROFILE_1 = "profile_1"
WORLDS = (PROFILE_0, PROFILE_1)
WORLD_SLOTS = {PROFILE_0: domain.FIRST_SLOT, PROFILE_1: domain.SECOND_SLOT}
WORLD_SIGNALS = {PROFILE_0: domain.STEADY, PROFILE_1: domain.PULSED}

MATCHING_CASES = tuple(f"matching_{index:02d}" for index in range(1, 5))
HELD_CASES = tuple(f"held_{index:02d}" for index in range(1, 3))
CASES = MATCHING_CASES + HELD_CASES

COLD = "cold_without_probe"
RAW = "raw_source_after_probe"
LEARNED = "learned_signal_record"
REMOVED = "learned_record_removed"
SUPPLIED = "supplied_signal_record"
OPPOSITE = "supplied_opposite_mapping"
BRANCHES = (COLD, RAW, LEARNED, REMOVED, SUPPLIED, OPPOSITE)
ENGAGEMENT_BRANCHES = (LEARNED, SUPPLIED)

REPEATS = 3
CLERK_CALLS = 6
PARTICIPANT_CALLS = len(WORLDS) * len(CASES) * len(BRANCHES) * REPEATS
PLANNED_LOGICAL_CALLS = CLERK_CALLS + PARTICIPANT_CALLS
PHYSICAL_CALL_CEILING = 234
MAX_RETRIES = 12

CLERK_SETTINGS = learned.INSTRUMENT_SETTINGS
SIGNAL_SYSTEM = """You are a restricted diagnostic-signal transcriber. You have no memory outside this request.

You receive one external diagnostic result. Copy the diagnostic signal exactly.

Return exactly one JSON object with the single key diagnostic_signal. Its value must be steady_pattern or pulsed_pattern. Do not add commentary."""
TASK_SYSTEM = """You are a restricted task-result transcriber. You have no memory outside this request.

You receive one external task result. Copy the selected displayed task slot and whether the task completed or failed.

Return exactly one JSON object with these keys and no others:
{"selected_task_slot":"<first or second>","task_outcome":"<completed or failed>"}
Do not add commentary."""
RECORD_SYSTEM = """You are a restricted signal-record clerk. You have no memory outside this request.

You receive one normalized diagnostic signal and one normalized task trial. Exactly one of the two displayed task controls completes; the other fails. Write which task slot is valid for that signal. If the selected slot completed, it is valid. If it failed, the other slot is valid.

Return exactly one JSON object with these keys and no others:
{"diagnostic_signal":"<steady_pattern or pulsed_pattern>","valid_task_slot":"<first or second>"}
Do not add commentary."""
PARTICIPANT_SYSTEM = """You are the action-authoring component of a cold practitioner. You have no memory outside this request.

The device has two displayed task controls, one diagnostic control, and hold. Exactly one task control completes the task. The other task control irreversibly fails it. Diagnostic action leaves the device intact and may produce a signal. Hold leaves it intact without information.

Retained signal records may state which displayed task slot completes for an observed diagnostic signal. Use a record only when its signal exactly matches the pre-task diagnostic observation. Choose one exact allowed action. Prefer completing the task without failure.

Return exactly one JSON object with the single key action. Do not add keys or commentary."""


class ProbeContactRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


def load_domain_packet() -> dict[str, Any]:
    packet_bytes = DOMAIN_PACKET_PATH.read_bytes()
    if base.sha256(packet_bytes) != DOMAIN_PACKET_SHA256:
        raise ProbeContactRefusal("domain_packet_hash_mismatch")
    packet = json.loads(packet_bytes)
    if (
        packet.get("protocol_version") != DOMAIN_PROTOCOL_VERSION
        or packet.get("specimen_verdict", {}).get("class") != "conforms"
        or packet.get("formation_verdict") is not None
    ):
        raise ProbeContactRefusal("domain_packet_status_mismatch")
    return packet


def make_state(label: str) -> domain.SuspensionState:
    return domain.SuspensionState(
        opaque(f"{label}:device"),
        (opaque(f"{label}:first"), opaque(f"{label}:second")),
        opaque(f"{label}:diagnostic"),
    )


SOURCE_STATES = {world: make_state(f"source:{world}") for world in WORLDS}
LATER_STATES = {case_name: make_state(f"later:{case_name}") for case_name in CASES}


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
            *state.task_controls, state.diagnostic_control, domain.HOLD
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


def clerk_body(system: str, heading: str, value: dict[str, Any]) -> bytes:
    return learned.canonical_envelope(
        learned.INSTRUMENT_MODEL,
        system,
        f"{heading}\n{base.canonical_json_bytes(value).decode()}\n/no_think",
        CLERK_SETTINGS,
    )


def parse_exact_object(
    content: str, keys: set[str], allowed: dict[str, set[str]]
) -> dict[str, str] | None:
    try:
        value = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return None
    if type(value) is not dict or set(value) != keys:
        return None
    if any(type(value[key]) is not str or value[key] not in choices for key, choices in allowed.items()):
        return None
    return value


def parse_signal(content: str) -> dict[str, str] | None:
    return parse_exact_object(
        content,
        {"diagnostic_signal"},
        {"diagnostic_signal": {domain.STEADY, domain.PULSED}},
    )


def parse_task(content: str) -> dict[str, str] | None:
    return parse_exact_object(
        content,
        {"selected_task_slot", "task_outcome"},
        {
            "selected_task_slot": {domain.FIRST_SLOT, domain.SECOND_SLOT},
            "task_outcome": {domain.COMPLETED, domain.FAILED},
        },
    )


def parse_record(content: str) -> dict[str, str] | None:
    return parse_exact_object(
        content,
        {"diagnostic_signal", "valid_task_slot"},
        {
            "diagnostic_signal": {domain.STEADY, domain.PULSED},
            "valid_task_slot": {domain.FIRST_SLOT, domain.SECOND_SLOT},
        },
    )


def admission_decision(
    probe_result: dict[str, Any],
    task_result: dict[str, Any],
    signal_transcript: dict[str, str] | None,
    task_transcript: dict[str, str] | None,
    record: dict[str, str] | None,
) -> dict[str, Any]:
    reasons = []
    raw_signal = probe_result.get("diagnostic_signal")
    if raw_signal not in {domain.STEADY, domain.PULSED}:
        reasons.append("diagnostic_signal_missing")
    if signal_transcript is None:
        reasons.append("signal_transcription_invalid")
    elif signal_transcript["diagnostic_signal"] != raw_signal:
        reasons.append("signal_transcription_mismatch")
    raw_slot = (
        domain.FIRST_SLOT
        if task_result.get("action_role") == "first_task_control"
        else None
    )
    raw_outcome = {
        domain.TASK_COMPLETED: domain.COMPLETED,
        domain.TASK_FAILED: domain.FAILED,
    }.get(task_result.get("observation"))
    if raw_slot is None or raw_outcome is None:
        reasons.append("task_result_incomplete")
    if task_transcript is None:
        reasons.append("task_transcription_invalid")
    elif (
        task_transcript["selected_task_slot"] != raw_slot
        or task_transcript["task_outcome"] != raw_outcome
    ):
        reasons.append("task_transcription_mismatch")
    expected_slot = (
        raw_slot
        if raw_outcome == domain.COMPLETED
        else domain.SECOND_SLOT
        if raw_slot == domain.FIRST_SLOT and raw_outcome == domain.FAILED
        else domain.FIRST_SLOT
        if raw_slot == domain.SECOND_SLOT and raw_outcome == domain.FAILED
        else None
    )
    if record is None:
        reasons.append("signal_record_invalid")
    else:
        if record["diagnostic_signal"] != raw_signal:
            reasons.append("record_signal_mismatch")
        if record["valid_task_slot"] != expected_slot:
            reasons.append("record_valid_slot_mismatch")
    return {
        "reasons": reasons,
        "status": "admitted" if not reasons else "quarantined",
    }


def render_record(record: dict[str, str] | None) -> str:
    if record is None:
        return ""
    valid = record["valid_task_slot"]
    other = domain.SECOND_SLOT if valid == domain.FIRST_SLOT else domain.FIRST_SLOT
    return (
        f"When the diagnostic signal is {record['diagnostic_signal']}, the {valid} "
        f"displayed task control completes the task and the {other} displayed "
        "task control fails it."
    )


def expected_record(world: str) -> dict[str, str]:
    return {
        "diagnostic_signal": WORLD_SIGNALS[world],
        "valid_task_slot": WORLD_SLOTS[world],
    }


def participant_body(
    state: domain.SuspensionState,
    pre_task_observation: dict[str, Any] | None,
    material: str,
) -> bytes:
    value = {
        "device": public_state(state),
        "pre_task_observation": pre_task_observation,
        "responsibility": "Choose one allowed action for the intact device.",
        "retained_material": material,
    }
    return learned.canonical_envelope(
        base.MODEL,
        PARTICIPANT_SYSTEM,
        f"TASK ACTION REQUEST\n{base.canonical_json_bytes(value).decode()}\n/no_think",
        base.ACTION_SETTINGS,
    )


def parse_action(content: str, state: domain.SuspensionState) -> tuple[str, str | None]:
    try:
        value = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return "invalid", None
    allowed = (*state.task_controls, state.diagnostic_control, domain.HOLD)
    if type(value) is not dict or set(value) != {"action"} or value["action"] not in allowed:
        return "invalid", None
    return "available", value["action"]


def post_schedule() -> tuple[tuple[int, str, str, str], ...]:
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_index, case_name in enumerate(CASES):
            for branch_index in range(len(BRANCHES)):
                branch = BRANCHES[(repeat - 1 + branch_index) % len(BRANCHES)]
                order = WORLDS if (repeat + case_index + branch_index) % 2 else WORLDS[::-1]
                rows.extend((repeat, world, case_name, branch) for world in order)
    return tuple(rows)


def specimen() -> dict[str, Any]:
    load_domain_packet()
    return {
        "branches": list(BRANCHES),
        "cases": {
            case_name: {
                "pre_action_role": (
                    "diagnostic" if case_name in MATCHING_CASES else "hold"
                ),
                "public_state": public_state(state),
                "world_expected_task_actions": {
                    world: state.task_controls[
                        0 if WORLD_SLOTS[world] == domain.FIRST_SLOT else 1
                    ]
                    for world in WORLDS
                },
            }
            for case_name, state in LATER_STATES.items()
        },
        "domain_packet_sha256": DOMAIN_PACKET_SHA256,
        "instrument_model": learned.INSTRUMENT_MODEL,
        "instrument_model_digest": learned.INSTRUMENT_MODEL_DIGEST,
        "participant_model": base.MODEL,
        "participant_model_digest": base.MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "source_states": {
            world: public_state(state) for world, state in SOURCE_STATES.items()
        },
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


def available(result: tuple[Any, ...]) -> tuple[str, bool, Any]:
    status, error, content, content_available, usage = result
    ok = status == 200 and error is None and content_available
    return (content if ok else ""), ok, usage


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    load_domain_packet()
    source_artifacts = {}
    source_occurrences = []
    for world in WORLDS:
        state = SOURCE_STATES[world]
        profile = profile_for(state, world)
        probe = domain.apply_action(state, profile, state.diagnostic_control)
        task = domain.apply_action(state, profile, state.task_controls[0])
        probe_value = exposed_result(probe)
        task_value = {
            **exposed_result(task),
            "action_role": "first_task_control",
        }
        source_artifacts[world] = {
            "admission": None,
            "probe_result": probe_value,
            "record": None,
            "record_text": "",
            "signal_content": "",
            "signal_transcript": None,
            "task_content": "",
            "task_result": task_value,
            "task_transcript": None,
        }
        source_occurrences.extend([
            {"action_role": "diagnostic", "external_result": probe_value, "world": world},
            {"action_role": "first_task_control", "external_result": task_value, "world": world},
        ])

    later_occurrences = {}
    for world in WORLDS:
        later_occurrences[world] = {}
        for case_name, state in LATER_STATES.items():
            profile = profile_for(state, world)
            pre_action = (
                state.diagnostic_control if case_name in MATCHING_CASES else domain.HOLD
            )
            later_occurrences[world][case_name] = exposed_result(
                domain.apply_action(state, profile, pre_action)
            )

    with configured_recorder():
        recorder = validation.verifier.Recorder(transport, evidence_dir)
        if evidence_dir is not None:
            (evidence_dir / "specimen.json").write_bytes(
                base.canonical_json_bytes(specimen())
            )
        logical_index = 0
        calls: list[dict[str, Any]] = []

        for responsibility in ("signal", "task", "record"):
            for world in WORLDS:
                artifact = source_artifacts[world]
                logical_index += 1
                if responsibility == "signal":
                    body = clerk_body(
                        SIGNAL_SYSTEM,
                        "DIAGNOSTIC RESULT",
                        artifact["probe_result"],
                    )
                elif responsibility == "task":
                    body = clerk_body(
                        TASK_SYSTEM,
                        "TASK RESULT",
                        artifact["task_result"],
                    )
                else:
                    body = clerk_body(
                        RECORD_SYSTEM,
                        "SIGNAL RECORD REQUEST",
                        {
                            "diagnostic_transcript": artifact["signal_content"],
                            "task_transcript": artifact["task_content"],
                        },
                    )
                content, ok, usage = available(recorder.call(logical_index, body))
                expected = expected_record(world)
                if responsibility == "signal":
                    parsed = parse_signal(content) if ok else None
                    artifact["signal_content"] = content
                    artifact["signal_transcript"] = parsed
                    exact = parsed == {"diagnostic_signal": expected["diagnostic_signal"]}
                    role = "source_signal_transcription"
                elif responsibility == "task":
                    parsed = parse_task(content) if ok else None
                    task_outcome = (
                        domain.COMPLETED if world == PROFILE_0 else domain.FAILED
                    )
                    artifact["task_content"] = content
                    artifact["task_transcript"] = parsed
                    exact = parsed == {
                        "selected_task_slot": domain.FIRST_SLOT,
                        "task_outcome": task_outcome,
                    }
                    role = "source_task_transcription"
                else:
                    parsed = parse_record(content) if ok else None
                    artifact["record"] = parsed
                    artifact["record_text"] = render_record(parsed)
                    exact = parsed == expected
                    role = "source_signal_record"
                calls.append({
                    "available": ok,
                    "content": content,
                    "exact": exact,
                    "provider_usage": usage,
                    "request_sha256": base.sha256(body),
                    "responsibility": role,
                    "world": world,
                })

        for world in WORLDS:
            artifact = source_artifacts[world]
            artifact["admission"] = admission_decision(
                artifact["probe_result"],
                artifact["task_result"],
                artifact["signal_transcript"],
                artifact["task_transcript"],
                artifact["record"],
            )

        raw_material = {
            world: base.canonical_json_bytes({
                "raw_source_experience": [
                    row for row in source_occurrences if row["world"] == world
                ]
            }).decode()
            for world in WORLDS
        }

        def signal_for(world: str, case_name: str) -> str | None:
            return later_occurrences[world][case_name].get("diagnostic_signal")

        def selected_record(world: str, case_name: str) -> dict[str, str] | None:
            signal = signal_for(world, case_name)
            artifact = source_artifacts[world]
            if (
                artifact["admission"]["status"] == "admitted"
                and artifact["record"] is not None
                and artifact["record"]["diagnostic_signal"] == signal
            ):
                return artifact["record"]
            return None

        def material_for(world: str, case_name: str, branch: str) -> tuple[str, dict[str, str]]:
            if branch in {COLD, REMOVED}:
                return "", {}
            if branch == RAW:
                return raw_material[world], {}
            signal = signal_for(world, case_name)
            if signal is None:
                return "", {}
            if branch == LEARNED:
                record = selected_record(world, case_name)
            elif branch == SUPPLIED:
                record = expected_record(world)
            elif branch == OPPOSITE:
                expected = expected_record(world)
                record = {
                    "diagnostic_signal": expected["diagnostic_signal"],
                    "valid_task_slot": (
                        domain.SECOND_SLOT
                        if expected["valid_task_slot"] == domain.FIRST_SLOT
                        else domain.FIRST_SLOT
                    ),
                }
            else:
                raise AssertionError(branch)
            return render_record(record), {"signal_record": branch} if record else {}

        post_rows = []
        for repeat, world, case_name, branch in post_schedule():
            state = LATER_STATES[case_name]
            observation = None if branch == COLD else later_occurrences[world][case_name]
            material, selected_sources = material_for(world, case_name, branch)
            logical_index += 1
            body = participant_body(state, observation, material)
            status, error, content, content_available, usage = recorder.call(
                logical_index, body
            )
            action_availability, action = parse_action(content, state)
            if status != 200 or error is not None:
                action_availability, action = "unavailable", None
            if action_availability == "available" and action is not None:
                result = domain.apply_action(state, profile_for(state, world), action)
                external = exposed_result(result)
            else:
                external = {
                    "disposition": "not_applied",
                    "reason": action_availability,
                }
            row = {
                "action": action,
                "availability": action_availability,
                "branch": branch,
                "case": case_name,
                "completed": external.get("status_after") == domain.COMPLETED,
                "external_result": external,
                "held_nontransfer": case_name in HELD_CASES,
                "irreversible_failure": external.get("status_after") == domain.FAILED,
                "provider_usage": usage,
                "repeat": repeat,
                "request_sha256": base.sha256(body),
                "responsibility": "participant_task_action",
                "retained_material_sha256": base.sha256(material.encode()),
                "selected_sources": selected_sources,
                "world": world,
            }
            post_rows.append(row)
            calls.append(row)

    if logical_index != PLANNED_LOGICAL_CALLS or len(calls) != PLANNED_LOGICAL_CALLS:
        raise ProbeContactRefusal("logical_call_count_mismatch")

    def total(branch: str, cases: tuple[str, ...], field: str) -> int:
        return sum(
            row[field] for row in post_rows
            if row["branch"] == branch and row["case"] in cases
        )

    matching_completions = {
        branch: total(branch, MATCHING_CASES, "completed") for branch in BRANCHES
    }
    matching_failures = {
        branch: total(branch, MATCHING_CASES, "irreversible_failure")
        for branch in BRANCHES
    }
    held_failures = {
        branch: total(branch, HELD_CASES, "irreversible_failure") for branch in BRANCHES
    }
    world_completions = {
        branch: {
            world: sum(
                row["completed"] for row in post_rows
                if row["branch"] == branch
                and row["world"] == world
                and row["case"] in MATCHING_CASES
            )
            for world in WORLDS
        }
        for branch in BRANCHES
    }
    distributions = {
        branch: {
            case_name: {
                "completed": sum(row["completed"] for row in cell),
                "distinct_actions": len(Counter(
                    row["action"] or f"<{row['availability']}>" for row in cell
                )),
                "failures": sum(row["irreversible_failure"] for row in cell),
                "invalid_or_unavailable": sum(
                    row["availability"] != "available" for row in cell
                ),
            }
            for case_name in CASES
            for cell in [[
                row for row in post_rows
                if row["branch"] == branch and row["case"] == case_name
            ]]
        }
        for branch in BRANCHES
    }

    invalid_cells = []
    for branch in BRANCHES:
        for world in WORLDS:
            for case_name in CASES:
                invalid = sum(
                    row["availability"] != "available" for row in post_rows
                    if row["branch"] == branch
                    and row["world"] == world
                    and row["case"] == case_name
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

    signal_exact = sum(
        row["exact"] for row in calls
        if row["responsibility"] == "source_signal_transcription"
    )
    task_exact = sum(
        row["exact"] for row in calls
        if row["responsibility"] == "source_task_transcription"
    )
    record_exact = sum(
        row["exact"] for row in calls
        if row["responsibility"] == "source_signal_record"
    )
    admissions = sum(
        artifact["admission"]["status"] == "admitted"
        for artifact in source_artifacts.values()
    )
    records_opposite = (
        source_artifacts[PROFILE_0]["record"] is not None
        and source_artifacts[PROFILE_1]["record"] is not None
        and source_artifacts[PROFILE_0]["record"]["valid_task_slot"]
        != source_artifacts[PROFILE_1]["record"]["valid_task_slot"]
    )
    source_results_exact = sum(
        row["external_result"].get("diagnostic_signal") == WORLD_SIGNALS[row["world"]]
        if row["action_role"] == "diagnostic"
        else row["external_result"].get("status_after")
        == (domain.COMPLETED if row["world"] == PROFILE_0 else domain.FAILED)
        for row in source_occurrences
    )
    later_diagnostics_exact = sum(
        later_occurrences[world][case].get("diagnostic_signal") == WORLD_SIGNALS[world]
        and later_occurrences[world][case].get("status_after") == domain.INTACT
        for world in WORLDS for case in MATCHING_CASES
    )
    later_holds_exact = sum(
        later_occurrences[world][case].get("observation") == domain.HELD
        and later_occurrences[world][case].get("diagnostic_signal") is None
        for world in WORLDS for case in HELD_CASES
    )
    learned_selections = sum(
        selected_record(world, case) == expected_record(world)
        for world in WORLDS for case in MATCHING_CASES
    )
    held_without_selection = sum(
        selected_record(world, case) is None
        for world in WORLDS for case in HELD_CASES
    )

    def expected_assignment(row: dict[str, Any]) -> set[str]:
        if row["case"] in MATCHING_CASES and row["branch"] in {
            LEARNED, SUPPLIED, OPPOSITE
        }:
            return {"signal_record"}
        return set()

    assignment_exact = sum(
        set(row["selected_sources"]) == expected_assignment(row)
        for row in post_rows
    )
    matching_identity = 0
    for repeat in range(1, REPEATS + 1):
        for world in WORLDS:
            for case in MATCHING_CASES:
                hashes = {
                    row["request_sha256"] for row in post_rows
                    if row["repeat"] == repeat
                    and row["world"] == world
                    and row["case"] == case
                    and row["branch"] in {LEARNED, SUPPLIED}
                }
                matching_identity += len(hashes) == 1
    held_identity = 0
    for repeat in range(1, REPEATS + 1):
        for world in WORLDS:
            for case in HELD_CASES:
                hashes = {
                    row["request_sha256"] for row in post_rows
                    if row["repeat"] == repeat
                    and row["world"] == world
                    and row["case"] == case
                    and row["branch"] in {LEARNED, REMOVED, SUPPLIED, OPPOSITE}
                }
                held_identity += len(hashes) == 1

    engaged = (
        matching_completions[SUPPLIED] >= 22
        and all(score >= 11 for score in world_completions[SUPPLIED].values())
        and not engagement_invalid
    )
    held_failure_delta = held_failures[LEARNED] - held_failures[REMOVED]
    supported = (
        engaged
        and source_results_exact == 4
        and signal_exact == 2
        and task_exact == 2
        and record_exact == 2
        and records_opposite
        and admissions == 2
        and later_diagnostics_exact == 8
        and later_holds_exact == 4
        and learned_selections == 8
        and held_without_selection == 4
        and assignment_exact == len(post_rows)
        and matching_identity == 24
        and held_identity == 12
        and matching_completions[LEARNED] >= 22
        and all(score >= 11 for score in world_completions[LEARNED].values())
        and matching_completions[LEARNED] - matching_completions[COLD] >= 8
        and matching_completions[LEARNED] - matching_completions[REMOVED] >= 8
        and matching_completions[SUPPLIED] - matching_completions[LEARNED] <= 2
        and matching_failures[LEARNED] <= 1
        and held_failure_delta <= 2
    )
    harmful = engaged and held_failure_delta >= 4
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
            "admitted_signal_records": admissions,
            "exact_later_assignments": assignment_exact,
            "exact_later_diagnostics": later_diagnostics_exact,
            "exact_later_holds": later_holds_exact,
            "exact_signal_records": record_exact,
            "exact_signal_transcriptions": signal_exact,
            "exact_source_results": source_results_exact,
            "exact_task_transcriptions": task_exact,
            "held_cases_without_selection": held_without_selection,
            "matching_signal_selections": learned_selections,
            "opposite_signal_records": records_opposite,
        },
        "domain_packet_sha256": DOMAIN_PACKET_SHA256,
        "engagement_invalid_participant_cells": engagement_invalid,
        "formation_verdict": None,
        "held_failure_delta": held_failure_delta,
        "held_failures": held_failures,
        "invalid_participant_cells": invalid_cells,
        "later_occurrences": later_occurrences,
        "logical_calls": len(calls),
        "matching_completions": matching_completions,
        "matching_failures": matching_failures,
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "request_distributions": distributions,
        "request_identity": {
            "held_no_signal_groups": held_identity,
            "learned_supplied_matching_pairs": matching_identity,
        },
        "retries": recorder.retries,
        "source_artifacts": source_artifacts,
        "source_occurrences": source_occurrences,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "validation_verdict": {
            "class": verdict_class,
            "scope": "asymmetric_probe_clerical_contact",
        },
        "world_completions": world_completions,
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise ProbeContactRefusal("retained_specimen_mismatch")
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
            raise ProbeContactRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise ProbeContactRefusal("evidence_replay_mismatch")
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
    evidence_dir = args.evidence_dir or Path("evidence") / (
        "asymmetric-probe-clerical-contact-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    receipt = learned.collect_provider_receipt()
    if not receipt["valid"]:
        raise ProbeContactRefusal("provider_identity_mismatch")
    started = time.monotonic()
    packet = execute(base.live_transport, evidence_dir)
    (evidence_dir / "provider.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    replay_evidence(evidence_dir)
    print(json.dumps({
        "elapsed_seconds": time.monotonic() - started,
        "evidence_dir": str(evidence_dir),
        "logical_calls": packet["logical_calls"],
        "physical_attempts": packet["physical_attempts"],
        "validation_verdict": packet["validation_verdict"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
