"""Test an explicit exact-match applicability receipt after diagnostic action."""

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

from contact import asymmetric_probe_clerical_contact as clerk_contact
from contact import composed_clerical_revision_validation as validation
from contact import distributional_developmental_comparison as base
from contact import self_directed_probe_contact as prior
from micro_environment import asymmetric_suspension as domain


PROTOCOL_VERSION = "explicit-applicability-receipt-contact-v1"
SPEC_PATH = (
    Path(__file__).parents[1]
    / "docs"
    / "EXPLICIT_APPLICABILITY_RECEIPT_CONTACT.md"
)
PREDECESSOR_PACKET_PATH = (
    Path(__file__).parents[1]
    / "evidence"
    / "self-directed-probe-contact-20260820T225832Z"
    / "packet.json"
)
PREDECESSOR_PACKET_SHA256 = (
    "92fe84ff6a8579aa6e9c4d70ff443de04732815712e2d0c8fca1b228a9e39ebb"
)

MATCHING_CASES = tuple(f"matching_{index:02d}" for index in range(1, 4))
UNMAPPED_CASES = ("unmapped_01",)
CASES = MATCHING_CASES + UNMAPPED_CASES

FULL = "full_learned_catalog"
SELECTED_SILENT = "selected_record_silent_absence"
RECEIPT = "selected_record_explicit_receipt"
REMOVED = "no_record_no_receipt"
SUPPLIED_RECEIPT = "supplied_record_explicit_receipt"
REVERSED_RECEIPT = "reversed_record_explicit_receipt"
BRANCHES = (
    FULL,
    SELECTED_SILENT,
    RECEIPT,
    REMOVED,
    SUPPLIED_RECEIPT,
    REVERSED_RECEIPT,
)
ENGAGEMENT_BRANCHES = (RECEIPT, SUPPLIED_RECEIPT)

REPEATS = 3
PLANNED_LOGICAL_CALLS = (
    len(MATCHING_CASES) * len(prior.KNOWN_WORLDS)
    + len(UNMAPPED_CASES) * len(prior.UNMAPPED_WORLDS)
) * len(BRANCHES) * REPEATS
PHYSICAL_CALL_CEILING = PLANNED_LOGICAL_CALLS + 12
MAX_RETRIES = 12

PARTICIPANT_SYSTEM = """You are the action-authoring component of a cold practitioner. You have no memory outside this request.

The device has two displayed task controls, one diagnostic control, and hold. Exactly one task control completes the task. The other irreversibly fails it. The device is still intact after the retained diagnostic result.

Retained signal records may state which displayed task slot completes after an exact diagnostic signal. Apply a record only when its signal exactly matches the environment-issued result.

An applicability receipt reports the runtime's exact comparison between the observed signal and retained model-written signal fields. An empty applicable_record_ids list means that comparison found no matching retained record. The receipt does not choose an action.

Choose one exact allowed action. Prefer completing the task without irreversible failure.

Return exactly one JSON object with the single key action. Do not add keys or commentary."""


class ApplicabilityReceiptRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


def load_predecessor_packet() -> dict[str, Any]:
    packet_bytes = PREDECESSOR_PACKET_PATH.read_bytes()
    if base.sha256(packet_bytes) != PREDECESSOR_PACKET_SHA256:
        raise ApplicabilityReceiptRefusal("predecessor_packet_hash_mismatch")
    packet = json.loads(packet_bytes)
    if (
        packet.get("protocol_version") != prior.PROTOCOL_VERSION
        or packet.get("validation_verdict", {}).get("class") != "harmful"
        or packet.get("formation_verdict") is not None
        or packet.get("predecessor_packet_sha256")
        != prior.PREDECESSOR_PACKET_SHA256
    ):
        raise ApplicabilityReceiptRefusal("predecessor_packet_status_mismatch")
    return packet


def clerk_packet_and_records() -> tuple[dict[str, Any], list[dict[str, str]]]:
    packet = prior.load_predecessor_packet()
    return packet, prior.checked_learned_records(packet)


def record_id(record: dict[str, str]) -> str:
    return f"record_{record['diagnostic_signal']}"


def catalog(records: list[dict[str, str]]) -> list[dict[str, Any]]:
    return [
        {"record": record, "record_id": record_id(record)}
        for record in sorted(records, key=lambda row: row["diagnostic_signal"])
    ]


def render_records(records: list[dict[str, str]]) -> str:
    if not records:
        return ""
    return "SIGNAL RECORDS\n" + "\n".join(
        f"- {record_id(record)}: {clerk_contact.render_record(record)}"
        for record in sorted(records, key=lambda row: row["diagnostic_signal"])
    )


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
        for record in prior.supplied_records()
    ]


def exact_matches(
    signal: str, records: list[dict[str, str]]
) -> list[dict[str, str]]:
    return [record for record in records if record["diagnostic_signal"] == signal]


def make_state(case_name: str) -> domain.SuspensionState:
    return domain.SuspensionState(
        opaque(f"{case_name}:device"),
        (opaque(f"{case_name}:first"), opaque(f"{case_name}:second")),
        opaque(f"{case_name}:diagnostic"),
    )


STATES = {case_name: make_state(case_name) for case_name in CASES}


def worlds_for(case_name: str) -> tuple[str, str]:
    return (
        prior.KNOWN_WORLDS
        if case_name in MATCHING_CASES
        else prior.UNMAPPED_WORLDS
    )


def profile_for(state: domain.SuspensionState, world: str) -> domain.SuspensionProfile:
    return domain.SuspensionProfile(
        state.device,
        world,
        prior.WORLD_SLOTS[world],
        prior.WORLD_SIGNALS[world],
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


def branch_input(
    branch: str,
    signal: str,
    learned_records: list[dict[str, str]],
) -> tuple[str, dict[str, Any] | None, list[str]]:
    learned_matches = exact_matches(signal, learned_records)
    supplied_matches = exact_matches(signal, prior.supplied_records())
    reversed_matches = exact_matches(signal, reversed_records())

    if branch == FULL:
        selected = learned_records
        return render_records(selected), None, [record_id(row) for row in selected]
    if branch == SELECTED_SILENT:
        selected = learned_matches
        return render_records(selected), None, [record_id(row) for row in selected]
    if branch == REMOVED:
        return "", None, []
    if branch == RECEIPT:
        selected = learned_matches
    elif branch == SUPPLIED_RECEIPT:
        selected = supplied_matches
    elif branch == REVERSED_RECEIPT:
        selected = reversed_matches
    else:
        raise AssertionError(branch)
    ids = [record_id(row) for row in selected]
    return (
        render_records(selected),
        {"applicable_record_ids": ids, "observed_signal": signal},
        ids,
    )


def participant_body(
    state: domain.SuspensionState,
    diagnostic_result: dict[str, Any],
    material: str,
    receipt: dict[str, Any] | None,
) -> bytes:
    value = {
        "applicability_receipt": receipt,
        "device": public_state(state),
        "diagnostic_result": diagnostic_result,
        "responsibility": "Choose one allowed action for the intact device.",
        "retained_material": material,
    }
    return clerk_contact.learned.canonical_envelope(
        base.MODEL,
        PARTICIPANT_SYSTEM,
        f"POST-DIAGNOSTIC ACTION REQUEST\n{base.canonical_json_bytes(value).decode()}\n/no_think",
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


def schedule() -> tuple[tuple[int, str, str, str], ...]:
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_index, case_name in enumerate(CASES):
            for branch_index in range(len(BRANCHES)):
                branch = BRANCHES[
                    (repeat - 1 + case_index + branch_index) % len(BRANCHES)
                ]
                order = worlds_for(case_name)
                if (repeat + case_index + branch_index) % 2 == 0:
                    order = order[::-1]
                rows.extend(
                    (repeat, world, case_name, branch) for world in order
                )
    return tuple(rows)


def specimen() -> dict[str, Any]:
    load_predecessor_packet()
    _, records = clerk_packet_and_records()
    return {
        "branches": list(BRANCHES),
        "cases": {
            case_name: {
                "mapped": case_name in MATCHING_CASES,
                "public_state": public_state(state),
                "worlds": {
                    world: {
                        "diagnostic_signal": prior.WORLD_SIGNALS[world],
                        "expected_task_action": state.task_controls[
                            0
                            if prior.WORLD_SLOTS[world] == domain.FIRST_SLOT
                            else 1
                        ],
                    }
                    for world in worlds_for(case_name)
                },
            }
            for case_name, state in STATES.items()
        },
        "learned_catalog": catalog(records),
        "participant_model": base.MODEL,
        "participant_model_digest": base.MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
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
    load_predecessor_packet()
    _, learned_records = clerk_packet_and_records()

    diagnostic_results = {}
    for world in prior.WORLDS:
        diagnostic_results[world] = {}
        relevant_cases = (
            MATCHING_CASES if world in prior.KNOWN_WORLDS else UNMAPPED_CASES
        )
        for case_name in relevant_cases:
            state = STATES[case_name]
            diagnostic_results[world][case_name] = exposed_result(
                domain.apply_action(
                    state, profile_for(state, world), state.diagnostic_control
                )
            )

    with configured_recorder():
        recorder = validation.verifier.Recorder(transport, evidence_dir)
        if evidence_dir is not None:
            (evidence_dir / "specimen.json").write_bytes(
                base.canonical_json_bytes(specimen())
            )
        calls = []
        for logical_index, (repeat, world, case_name, branch) in enumerate(
            schedule(), start=1
        ):
            state = STATES[case_name]
            diagnostic_result = diagnostic_results[world][case_name]
            signal = diagnostic_result["diagnostic_signal"]
            material, receipt, selected_ids = branch_input(
                branch, signal, learned_records
            )
            body = participant_body(
                state, diagnostic_result, material, receipt
            )
            status, error, content, content_available, usage = recorder.call(
                logical_index, body
            )
            availability, action = parse_action(content, state)
            if status != 200 or error is not None or not content_available:
                availability, action = "unavailable", None
            role = action_role(action, state)
            if availability == "available" and action is not None:
                result = domain.apply_action(
                    state, profile_for(state, world), action
                )
                external = exposed_result(result)
            else:
                external = {
                    "disposition": "not_applied",
                    "reason": availability,
                }
            calls.append({
                "action": action,
                "action_role": role,
                "availability": availability,
                "branch": branch,
                "case": case_name,
                "completed": external.get("status_after") == domain.COMPLETED,
                "diagnostic_result": diagnostic_result,
                "failed": external.get("status_after") == domain.FAILED,
                "mapped": case_name in MATCHING_CASES,
                "provider_usage": usage,
                "receipt": receipt,
                "repeat": repeat,
                "request_sha256": base.sha256(body),
                "responsibility": "post_diagnostic_task_action",
                "retained_material_sha256": base.sha256(material.encode()),
                "selected_record_ids": selected_ids,
                "world": world,
            })

    if len(calls) != PLANNED_LOGICAL_CALLS:
        raise ApplicabilityReceiptRefusal("logical_call_count_mismatch")

    def count(branch: str, mapped: bool, predicate: Callable[[dict[str, Any]], bool]) -> int:
        return sum(
            predicate(row) for row in calls
            if row["branch"] == branch and row["mapped"] is mapped
        )

    matching = {
        branch: {
            "completed": count(branch, True, lambda row: row["completed"]),
            "diagnostic": count(
                branch, True, lambda row: row["action_role"] == "diagnostic"
            ),
            "failed": count(branch, True, lambda row: row["failed"]),
            "hold": count(branch, True, lambda row: row["action_role"] == "hold"),
            "task_attempts": count(
                branch,
                True,
                lambda row: row["action_role"]
                in {"first_task_control", "second_task_control"},
            ),
        }
        for branch in BRANCHES
    }
    unmapped = {
        branch: {
            "completed": count(branch, False, lambda row: row["completed"]),
            "diagnostic": count(
                branch, False, lambda row: row["action_role"] == "diagnostic"
            ),
            "failed": count(branch, False, lambda row: row["failed"]),
            "hold": count(branch, False, lambda row: row["action_role"] == "hold"),
            "task_attempts": count(
                branch,
                False,
                lambda row: row["action_role"]
                in {"first_task_control", "second_task_control"},
            ),
        }
        for branch in BRANCHES
    }
    world_completions = {
        branch: {
            world: sum(
                row["completed"] for row in calls
                if row["branch"] == branch
                and row["world"] == world
                and row["mapped"]
            )
            for world in prior.KNOWN_WORLDS
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

    assignments_exact = 0
    for row in calls:
        signal = row["diagnostic_result"]["diagnostic_signal"]
        if row["branch"] == FULL:
            expected_ids = [record_id(record) for record in learned_records]
        elif row["branch"] == REMOVED:
            expected_ids = []
        else:
            expected_ids = [
                record_id(record)
                for record in exact_matches(signal, learned_records)
            ]
        assignments_exact += row["selected_record_ids"] == expected_ids

    diagnostics_exact = sum(
        result["status_after"] == domain.INTACT
        and result["diagnostic_signal"] == prior.WORLD_SIGNALS[world]
        for world, cases in diagnostic_results.items()
        for result in cases.values()
    )

    def identity(branches: set[str], only_unmapped: bool = False) -> int:
        exact = 0
        selected_cases = UNMAPPED_CASES if only_unmapped else CASES
        for repeat in range(1, REPEATS + 1):
            for case_name in selected_cases:
                for world in worlds_for(case_name):
                    hashes = {
                        row["request_sha256"] for row in calls
                        if row["repeat"] == repeat
                        and row["case"] == case_name
                        and row["world"] == world
                        and row["branch"] in branches
                    }
                    exact += len(hashes) == 1
        return exact

    learned_supplied_identity = identity({RECEIPT, SUPPLIED_RECEIPT})
    unknown_receipt_identity = identity(
        {RECEIPT, SUPPLIED_RECEIPT, REVERSED_RECEIPT}, only_unmapped=True
    )
    unknown_silent_identity = identity(
        {SELECTED_SILENT, REMOVED}, only_unmapped=True
    )

    engaged = (
        matching[SUPPLIED_RECEIPT]["completed"] >= 16
        and all(
            value >= 8 for value in world_completions[SUPPLIED_RECEIPT].values()
        )
        and unmapped[FULL]["task_attempts"] >= 4
        and unmapped[SELECTED_SILENT]["task_attempts"] >= 4
        and not engagement_invalid
    )
    supported = (
        engaged
        and assignments_exact == len(calls)
        and diagnostics_exact == 8
        and learned_supplied_identity == 24
        and unknown_receipt_identity == 6
        and unknown_silent_identity == 6
        and matching[RECEIPT]["completed"] >= 16
        and all(value >= 8 for value in world_completions[RECEIPT].values())
        and matching[RECEIPT]["failed"] <= 1
        and matching[RECEIPT]["completed"] - matching[REMOVED]["completed"] >= 6
        and matching[SUPPLIED_RECEIPT]["completed"]
        - matching[RECEIPT]["completed"] <= 2
        and matching[REVERSED_RECEIPT]["failed"] >= 14
        and unmapped[RECEIPT]["task_attempts"] <= 1
        and unmapped[RECEIPT]["failed"] <= 1
        and unmapped[FULL]["task_attempts"]
        - unmapped[RECEIPT]["task_attempts"] >= 4
        and unmapped[SELECTED_SILENT]["task_attempts"]
        - unmapped[RECEIPT]["task_attempts"] >= 4
    )
    harmful = engaged and (
        unmapped[RECEIPT]["task_attempts"] >= 3
        or unmapped[RECEIPT]["failed"] >= 3
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
            "exact_record_assignments": assignments_exact,
            "exact_retained_records": len(learned_records),
            "exact_shared_diagnostics": diagnostics_exact,
        },
        "engagement_invalid_participant_cells": engagement_invalid,
        "formation_verdict": None,
        "invalid_participant_cells": invalid_cells,
        "logical_calls": len(calls),
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
        "request_identity": {
            "learned_supplied_receipt_pairs": learned_supplied_identity,
            "unmapped_receipt_groups": unknown_receipt_identity,
            "unmapped_silent_pairs": unknown_silent_identity,
        },
        "retries": recorder.retries,
        "shared_diagnostic_results": diagnostic_results,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "unmapped_outcomes": unmapped,
        "validation_verdict": {
            "class": verdict_class,
            "scope": "explicit_applicability_receipt_contact",
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
        raise ApplicabilityReceiptRefusal("retained_specimen_mismatch")
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
            raise ApplicabilityReceiptRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise ApplicabilityReceiptRefusal("evidence_replay_mismatch")
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
        "explicit-applicability-receipt-contact-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    receipt = clerk_contact.learned.collect_provider_receipt()
    if not receipt["valid"]:
        raise ApplicabilityReceiptRefusal("provider_identity_mismatch")
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
