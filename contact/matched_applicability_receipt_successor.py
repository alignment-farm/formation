"""Repeat no-match pressure under the exact harmful participant interface."""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any, Callable

from contact import asymmetric_probe_clerical_contact as clerk_contact
from contact import composed_clerical_revision_validation as validation
from contact import distributional_developmental_comparison as base
from contact import explicit_applicability_receipt_contact as first_receipt
from contact import self_directed_probe_contact as prior
from micro_environment import asymmetric_suspension as domain


PROTOCOL_VERSION = "matched-applicability-receipt-successor-v1"
SPEC_PATH = (
    Path(__file__).parents[1]
    / "docs"
    / "MATCHED_APPLICABILITY_RECEIPT_SUCCESSOR.md"
)
RECEIPT_PACKET_PATH = (
    Path(__file__).parents[1]
    / "evidence"
    / "explicit-applicability-receipt-contact-20260820T231222Z"
    / "packet.json"
)
RECEIPT_PACKET_SHA256 = (
    "a68e4934da537e5af3f58ba33c14fe7450666d22a34702dacb7da180e7e575f9"
)

FULL = "exact_parent_full_catalog"
SILENT = "exact_parent_silent_absence"
RECEIPT = "learned_match_receipt"
NO_RECORD = "exact_parent_no_record"
SUPPLIED_RECEIPT = "supplied_match_receipt"
REVERSED_RECEIPT = "reversed_match_receipt"
BRANCHES = (
    FULL,
    SILENT,
    RECEIPT,
    NO_RECORD,
    SUPPLIED_RECEIPT,
    REVERSED_RECEIPT,
)
ENGAGEMENT_BRANCHES = (RECEIPT, SUPPLIED_RECEIPT)

REPEATS = 3
PLANNED_LOGICAL_CALLS = first_receipt.PLANNED_LOGICAL_CALLS
PHYSICAL_CALL_CEILING = PLANNED_LOGICAL_CALLS + 12
MAX_RETRIES = 12


class MatchedReceiptRefusal(ValueError):
    pass


def load_receipt_packet() -> dict[str, Any]:
    packet_bytes = RECEIPT_PACKET_PATH.read_bytes()
    if base.sha256(packet_bytes) != RECEIPT_PACKET_SHA256:
        raise MatchedReceiptRefusal("receipt_packet_hash_mismatch")
    packet = json.loads(packet_bytes)
    if (
        packet.get("protocol_version") != first_receipt.PROTOCOL_VERSION
        or packet.get("validation_verdict", {}).get("class") != "not_engaged"
        or packet.get("formation_verdict") is not None
        or packet.get("predecessor_packet_sha256")
        != first_receipt.PREDECESSOR_PACKET_SHA256
    ):
        raise MatchedReceiptRefusal("receipt_packet_status_mismatch")
    return packet


def parent_and_records() -> tuple[dict[str, Any], list[dict[str, str]]]:
    parent = first_receipt.load_predecessor_packet()
    if parent.get("validation_verdict", {}).get("class") != "harmful":
        raise MatchedReceiptRefusal("harmful_parent_status_mismatch")
    supported_packet = prior.load_predecessor_packet()
    records = prior.checked_learned_records(supported_packet)
    return parent, records


def receipt_material(signal: str, records: list[dict[str, str]]) -> str:
    selected = first_receipt.exact_matches(signal, records)
    ids = [first_receipt.record_id(record) for record in selected]
    lines = [
        "APPLICABILITY MATCH RECEIPT",
        base.canonical_json_bytes({
            "applicable_record_ids": ids,
            "observed_signal": signal,
        }).decode(),
    ]
    if selected:
        lines.append("MATCHING RETAINED SIGNAL RECORDS")
        lines.extend(
            f"- {first_receipt.record_id(record)}: "
            f"{clerk_contact.render_record(record)}"
            for record in sorted(
                selected, key=lambda row: row["diagnostic_signal"]
            )
        )
    return "\n".join(lines)


def material_for(
    branch: str,
    signal: str,
    parent: dict[str, Any],
    records: list[dict[str, str]],
) -> tuple[str, list[str]]:
    if branch == FULL:
        material = prior.material_for(prior.LEARNED, parent, records)
        return material, [first_receipt.record_id(row) for row in records]
    if branch in {SILENT, NO_RECORD}:
        return "", []
    if branch == RECEIPT:
        selected = first_receipt.exact_matches(signal, records)
    elif branch == SUPPLIED_RECEIPT:
        selected = first_receipt.exact_matches(signal, prior.supplied_records())
    elif branch == REVERSED_RECEIPT:
        selected = first_receipt.exact_matches(
            signal, first_receipt.reversed_records()
        )
    else:
        raise AssertionError(branch)
    return receipt_material(signal, selected), [
        first_receipt.record_id(row) for row in selected
    ]


def diagnostics() -> dict[str, dict[str, dict[str, Any]]]:
    values = {}
    for world in prior.WORLDS:
        values[world] = {}
        cases = (
            prior.MATCHING_CASES
            if world in prior.KNOWN_WORLDS
            else prior.UNMAPPED_CASES
        )
        for case_name in cases:
            state = prior.STATES[case_name]
            values[world][case_name] = prior.exposed_result(domain.apply_action(
                state, prior.profile_for(state, world), state.diagnostic_control
            ))
    return values


def schedule() -> tuple[tuple[int, str, str, str], ...]:
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_index, case_name in enumerate(prior.CASES):
            for branch_index in range(len(BRANCHES)):
                branch = BRANCHES[
                    (repeat - 1 + case_index + branch_index) % len(BRANCHES)
                ]
                order = prior.worlds_for(case_name)
                if (repeat + case_index + branch_index) % 2 == 0:
                    order = order[::-1]
                rows.extend(
                    (repeat, world, case_name, branch) for world in order
                )
    return tuple(rows)


def parent_second_hashes(parent: dict[str, Any]) -> dict[tuple[int, str, str, str], str]:
    return {
        (row["repeat"], row["world"], row["case"], row["branch"]): row[
            "request_sha256"
        ]
        for row in parent["calls"]
        if row["action_number"] == 2
    }


def specimen() -> dict[str, Any]:
    load_receipt_packet()
    parent, records = parent_and_records()
    parent_hashes = parent_second_hashes(parent)
    required_parent_hashes = sum(
        (repeat, world, case_name, parent_branch) in parent_hashes
        for repeat in range(1, REPEATS + 1)
        for case_name in prior.CASES
        for world in prior.worlds_for(case_name)
        for parent_branch in (prior.LEARNED, prior.REMOVED)
    )
    if required_parent_hashes != 48:
        raise MatchedReceiptRefusal("parent_second_request_set_incomplete")
    return {
        "branches": list(BRANCHES),
        "harmful_parent_packet_sha256": first_receipt.PREDECESSOR_PACKET_SHA256,
        "learned_records": records,
        "not_engaged_parent_packet_sha256": RECEIPT_PACKET_SHA256,
        "participant_model": base.MODEL,
        "participant_model_digest": base.MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
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
    load_receipt_packet()
    parent, records = parent_and_records()
    parent_hashes = parent_second_hashes(parent)
    diagnostic_results = diagnostics()

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
            state = prior.STATES[case_name]
            diagnostic_result = diagnostic_results[world][case_name]
            signal = diagnostic_result["diagnostic_signal"]
            material, selected_ids = material_for(
                branch, signal, parent, records
            )
            body = prior.participant_body(
                state, 2, [diagnostic_result], material
            )
            status, error, content, content_available, usage = recorder.call(
                logical_index, body
            )
            availability, action = prior.parse_action(content, state)
            if status != 200 or error is not None or not content_available:
                availability, action = "unavailable", None
            role = first_receipt.action_role(action, state)
            if availability == "available" and action is not None:
                external = first_receipt.exposed_result(domain.apply_action(
                    state, prior.profile_for(state, world), action
                ))
            else:
                external = {
                    "disposition": "not_applied",
                    "reason": availability,
                }
            expected_parent_hash = None
            if branch == FULL:
                expected_parent_hash = parent_hashes[
                    (repeat, world, case_name, prior.LEARNED)
                ]
            elif branch in {SILENT, NO_RECORD}:
                expected_parent_hash = parent_hashes[
                    (repeat, world, case_name, prior.REMOVED)
                ]
            request_hash = base.sha256(body)
            calls.append({
                "action": action,
                "action_role": role,
                "availability": availability,
                "branch": branch,
                "case": case_name,
                "completed": external.get("status_after") == domain.COMPLETED,
                "diagnostic_result": diagnostic_result,
                "expected_parent_request_sha256": expected_parent_hash,
                "failed": external.get("status_after") == domain.FAILED,
                "mapped": case_name in prior.MATCHING_CASES,
                "provider_usage": usage,
                "repeat": repeat,
                "request_sha256": request_hash,
                "responsibility": "matched_post_diagnostic_action",
                "selected_record_ids": selected_ids,
                "world": world,
            })

    if len(calls) != PLANNED_LOGICAL_CALLS:
        raise MatchedReceiptRefusal("logical_call_count_mismatch")

    def count(branch: str, mapped: bool, predicate: Callable[[dict[str, Any]], bool]) -> int:
        return sum(
            predicate(row) for row in calls
            if row["branch"] == branch and row["mapped"] is mapped
        )

    def outcomes(mapped: bool) -> dict[str, dict[str, int]]:
        return {
            branch: {
                "completed": count(branch, mapped, lambda row: row["completed"]),
                "diagnostic": count(
                    branch, mapped, lambda row: row["action_role"] == "diagnostic"
                ),
                "failed": count(branch, mapped, lambda row: row["failed"]),
                "hold": count(
                    branch, mapped, lambda row: row["action_role"] == "hold"
                ),
                "task_attempts": count(
                    branch,
                    mapped,
                    lambda row: row["action_role"]
                    in {"first_task_control", "second_task_control"},
                ),
            }
            for branch in BRANCHES
        }

    matching = outcomes(True)
    unmapped = outcomes(False)
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
        for case_name in prior.CASES:
            for world in prior.worlds_for(case_name):
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

    parent_hash_matches = sum(
        row["expected_parent_request_sha256"] == row["request_sha256"]
        for row in calls
        if row["expected_parent_request_sha256"] is not None
    )
    assignments_exact = sum(
        row["selected_record_ids"]
        == (
            [first_receipt.record_id(record) for record in records]
            if row["branch"] == FULL
            else []
            if row["branch"] in {SILENT, NO_RECORD}
            else [
                first_receipt.record_id(record)
                for record in first_receipt.exact_matches(
                    row["diagnostic_result"]["diagnostic_signal"], records
                )
            ]
        )
        for row in calls
    )
    diagnostics_exact = sum(
        result["status_after"] == domain.INTACT
        and result["diagnostic_signal"] == prior.WORLD_SIGNALS[world]
        for world, cases in diagnostic_results.items()
        for result in cases.values()
    )

    def identity(branches: set[str], only_unmapped: bool = False) -> int:
        exact = 0
        cases = prior.UNMAPPED_CASES if only_unmapped else prior.CASES
        for repeat in range(1, REPEATS + 1):
            for case_name in cases:
                for world in prior.worlds_for(case_name):
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
    silent_no_record_identity = identity({SILENT, NO_RECORD})

    engaged = (
        matching[SUPPLIED_RECEIPT]["completed"] >= 16
        and all(
            value >= 8 for value in world_completions[SUPPLIED_RECEIPT].values()
        )
        and unmapped[FULL]["task_attempts"] >= 4
        and unmapped[SILENT]["task_attempts"] >= 4
        and not engagement_invalid
    )
    supported = (
        engaged
        and parent_hash_matches == 72
        and assignments_exact == len(calls)
        and diagnostics_exact == 8
        and learned_supplied_identity == 24
        and unknown_receipt_identity == 6
        and silent_no_record_identity == 24
        and matching[RECEIPT]["completed"] >= 16
        and all(value >= 8 for value in world_completions[RECEIPT].values())
        and matching[RECEIPT]["failed"] <= 1
        and matching[RECEIPT]["completed"] - matching[NO_RECORD]["completed"] >= 6
        and matching[SUPPLIED_RECEIPT]["completed"]
        - matching[RECEIPT]["completed"] <= 2
        and matching[REVERSED_RECEIPT]["failed"] >= 14
        and unmapped[RECEIPT]["task_attempts"] <= 1
        and unmapped[RECEIPT]["failed"] <= 1
        and unmapped[FULL]["task_attempts"]
        - unmapped[RECEIPT]["task_attempts"] >= 4
        and unmapped[SILENT]["task_attempts"]
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
            "exact_parent_control_request_hashes": parent_hash_matches,
            "exact_record_assignments": assignments_exact,
            "exact_retained_records": len(records),
            "exact_shared_diagnostics": diagnostics_exact,
        },
        "engagement_invalid_participant_cells": engagement_invalid,
        "formation_verdict": None,
        "invalid_participant_cells": invalid_cells,
        "logical_calls": len(calls),
        "matching_outcomes": matching,
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "receipt_parent_packet_sha256": RECEIPT_PACKET_SHA256,
        "request_action_distributions": {
            branch: dict(Counter(
                row["action"] or f"<{row['availability']}>" for row in calls
                if row["branch"] == branch
            ))
            for branch in BRANCHES
        },
        "request_identity": {
            "learned_supplied_receipt_pairs": learned_supplied_identity,
            "silent_no_record_pairs": silent_no_record_identity,
            "unmapped_receipt_groups": unknown_receipt_identity,
        },
        "retries": recorder.retries,
        "self_directed_parent_packet_sha256": first_receipt.PREDECESSOR_PACKET_SHA256,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "unmapped_outcomes": unmapped,
        "validation_verdict": {
            "class": verdict_class,
            "scope": "matched_applicability_receipt_successor",
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
        raise MatchedReceiptRefusal("retained_specimen_mismatch")
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
            raise MatchedReceiptRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise MatchedReceiptRefusal("evidence_replay_mismatch")
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
        "matched-applicability-receipt-successor-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    receipt = clerk_contact.learned.collect_provider_receipt()
    if not receipt["valid"]:
        raise MatchedReceiptRefusal("provider_identity_mismatch")
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
