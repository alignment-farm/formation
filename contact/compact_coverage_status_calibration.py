"""Calibrate one compact pre-action coverage fact without a catalog.

Question: can the participant use an isolated exact `complete` or `none`
coverage status when choosing whether to pay for a diagnostic?

Observation of interest: byte-identical complete statuses attract probing
regardless of record correctness, while byte-identical none statuses produce
hold rather than probe or direct task guesses.

Model/interface: exact ai/qwen3:14B-Q6_K artifact through the retained Docker
chat-completions interface and strict one-action JSON response.

Budget: 72 first-action calls, 12 transport-only retries, and 84 physical
attempts. Every case stops after the first available or unavailable output.

Evidence: evidence/compact-coverage-status-calibration-<run-id>/.
"""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any, Callable

from contact import composed_clerical_revision_validation as validation
from contact import distributional_developmental_comparison as base
from contact import knowledge_cost_interaction_exploration as original
from contact import preaction_coverage_receipt_successor as parent
from micro_environment import knowledge_cost_interaction as domain


PROTOCOL_VERSION = "compact-coverage-status-calibration-v1"
PARENT_PACKET_PATH = (
    Path(__file__).parents[1]
    / "evidence"
    / "preaction-coverage-receipt-successor-20260821T144006Z"
    / "packet.json"
)
PARENT_PACKET_SHA256 = (
    "c9e3dc22c2ba65d4164d322054e9a61028901b83503d04972c547577a82c6456"
)

LEARNED_STATUS = "learned_compact_status"
SUPPLIED_STATUS = "supplied_compact_status"
REVERSED_STATUS = "reversed_compact_status"
REMOVAL_STATUS = "removal_compact_status"
PARENT_CATALOG = "exact_parent_learned_costly"
PARENT_FREE_REMOVAL = "exact_parent_removal_free"
BRANCHES = (
    LEARNED_STATUS,
    SUPPLIED_STATUS,
    REVERSED_STATUS,
    REMOVAL_STATUS,
    PARENT_CATALOG,
    PARENT_FREE_REMOVAL,
)
STATUS_BRANCHES = {
    LEARNED_STATUS,
    SUPPLIED_STATUS,
    REVERSED_STATUS,
    REMOVAL_STATUS,
}

COVERED = original.COVERED
UNCOVERED = original.UNCOVERED
DEVICE_CLASSES = original.DEVICE_CLASSES
PROFILES = original.PROFILES
REPEATS = 3
PLANNED_LOGICAL_CALLS = (
    len(BRANCHES) * len(DEVICE_CLASSES) * len(PROFILES) * REPEATS
)
MAX_RETRIES = 12
PHYSICAL_CALL_CEILING = PLANNED_LOGICAL_CALLS + MAX_RETRIES


class CompactCoverageRefusal(ValueError):
    pass


def load_parent() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, str]]]:
    packet_bytes = PARENT_PACKET_PATH.read_bytes()
    if base.sha256(packet_bytes) != PARENT_PACKET_SHA256:
        raise CompactCoverageRefusal("parent_packet_hash_mismatch")
    packet = json.loads(packet_bytes)
    if (
        packet.get("protocol_version") != parent.PROTOCOL_VERSION
        or packet.get("exploration_verdict", {}).get("class") != "harmful"
        or packet.get("formation_verdict") is not None
    ):
        raise CompactCoverageRefusal("parent_packet_status_mismatch")
    original_packet, learned = parent.load_parent()
    return packet, original_packet, learned


def records_for(branch: str, learned: list[dict[str, str]]) -> list[dict[str, str]]:
    if branch in {LEARNED_STATUS, PARENT_CATALOG}:
        return learned
    if branch in {REMOVAL_STATUS, PARENT_FREE_REMOVAL}:
        return []
    if branch == SUPPLIED_STATUS:
        return original.supplied_records()
    if branch == REVERSED_STATUS:
        return original.reversed_records()
    raise AssertionError(branch)


def exact_status(
    alphabet: tuple[str, str], records: list[dict[str, str]]
) -> str:
    covered = {
        record["diagnostic_signal"] for record in records
    }.intersection(alphabet)
    if len(covered) == len(alphabet):
        return "complete"
    if not covered:
        return "none"
    raise CompactCoverageRefusal("partial_coverage_outside_calibration")


def status_material(status: str) -> str:
    if status not in {"complete", "none"}:
        raise CompactCoverageRefusal("unknown_coverage_status")
    return "PRE-ACTION COVERAGE STATUS\n" + base.canonical_json_bytes({
        "coverage_status": status,
    }).decode()


def cost_for(branch: str) -> str:
    return domain.FREE if branch == PARENT_FREE_REMOVAL else domain.COSTLY


def material_for(
    branch: str,
    state: domain.KnowledgeCostState,
    learned: list[dict[str, str]],
) -> tuple[str, str | None]:
    records = records_for(branch, learned)
    if branch in STATUS_BRANCHES:
        status = exact_status(state.diagnostic_alphabet, records)
        return status_material(status), status
    return original.render_catalog(records), None


def schedule() -> tuple[tuple[int, str, str, str], ...]:
    rows = []
    for repeat in range(1, REPEATS + 1):
        for device_index, device_class in enumerate(DEVICE_CLASSES):
            for branch_index in range(len(BRANCHES)):
                branch = BRANCHES[
                    (repeat - 1 + device_index + branch_index) % len(BRANCHES)
                ]
                profiles = PROFILES
                if (repeat + device_index + branch_index) % 2 == 0:
                    profiles = profiles[::-1]
                rows.extend(
                    (repeat, profile_name, device_class, branch)
                    for profile_name in profiles
                )
    return tuple(rows)


def original_first_hashes(
    packet: dict[str, Any]
) -> dict[tuple[int, str, str, str], str]:
    return {
        (row["repeat"], row["profile"], row["device_class"], row["branch"]): row[
            "request_sha256"
        ]
        for row in packet["calls"]
        if row["action_number"] == 1
    }


def specimen() -> dict[str, Any]:
    parent_packet, _, learned = load_parent()
    cases = {}
    for device_class in DEVICE_CLASSES:
        state = original.STATES[(device_class, domain.COSTLY)]
        cases[device_class] = {
            "public_state": original.public_state(state),
            "statuses": {
                branch: exact_status(
                    state.diagnostic_alphabet, records_for(branch, learned)
                )
                for branch in STATUS_BRANCHES
            },
        }
    return {
        "branches": list(BRANCHES),
        "budget": {
            "logical_calls": PLANNED_LOGICAL_CALLS,
            "physical_call_ceiling": PHYSICAL_CALL_CEILING,
            "transport_only_retries": MAX_RETRIES,
        },
        "cases": cases,
        "evidence_destination": (
            "evidence/compact-coverage-status-calibration-<run-id>/"
        ),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "observation_of_interest": (
            "an isolated complete status causes probe and an isolated none "
            "status causes hold without direct task action"
        ),
        "parent_packet_sha256": PARENT_PACKET_SHA256,
        "parent_verdict": parent_packet["exploration_verdict"],
        "protocol_version": PROTOCOL_VERSION,
        "question": (
            "Can the participant use one compact exact coverage status before action?"
        ),
        "route_stop": (
            "stop the coverage-representation route if none does not reliably "
            "produce hold in this isolated interface"
        ),
        "schedule": [list(row) for row in schedule()],
        "stopping_rule": (
            "stop every case after the first available or unavailable output; "
            "never resample valid output"
        ),
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
    _, original_packet, learned = load_parent()
    expected_hashes = original_first_hashes(original_packet)

    with configured_recorder():
        recorder = validation.verifier.Recorder(transport, evidence_dir)
        if evidence_dir is not None:
            (evidence_dir / "specimen.json").write_bytes(
                base.canonical_json_bytes(specimen())
            )
        calls = []
        for logical_index, (repeat, profile_name, device_class, branch) in enumerate(
            schedule(), start=1
        ):
            cost_mode = cost_for(branch)
            state = original.STATES[(device_class, cost_mode)]
            profile = original.profile_for(state, profile_name)
            material, coverage_status = material_for(branch, state, learned)
            body = original.participant_body(state, 1, [], material)
            status, error, content, content_available, usage = recorder.call(
                logical_index, body
            )
            availability, action = original.parse_action(content, state)
            if status != 200 or error is not None or not content_available:
                availability, action = "unavailable", None
            role = original.action_role(action, state)
            if availability == "available" and action is not None:
                result = domain.apply_action(state, profile, action)
                external = original.exposed_result(result)
            else:
                external = {
                    "disposition": "not_applied",
                    "reason": availability,
                }
            expected_parent_hash = None
            if branch == PARENT_CATALOG:
                expected_parent_hash = expected_hashes[
                    (repeat, profile_name, device_class, original.LEARNED_COSTLY)
                ]
            elif branch == PARENT_FREE_REMOVAL:
                expected_parent_hash = expected_hashes[
                    (repeat, profile_name, device_class, original.REMOVAL_FREE)
                ]
            calls.append({
                "action": action,
                "action_role": role,
                "availability": availability,
                "branch": branch,
                "coverage_status": coverage_status,
                "device_class": device_class,
                "expected_parent_request_sha256": expected_parent_hash,
                "external_result": external,
                "profile": profile_name,
                "provider_usage": usage,
                "repeat": repeat,
                "request_sha256": base.sha256(body),
                "responsibility": "participant_first_action_calibration",
            })

    if len(calls) != PLANNED_LOGICAL_CALLS:
        raise CompactCoverageRefusal("logical_call_count_mismatch")

    def outcome(branch: str, device_class: str) -> dict[str, int]:
        rows = [
            row for row in calls
            if row["branch"] == branch and row["device_class"] == device_class
        ]
        return {
            "direct_task_attempts": sum(
                row["action_role"] in {"first_task_control", "second_task_control"}
                for row in rows
            ),
            "failures": sum(
                row["external_result"].get("task_status_after") == domain.FAILED
                for row in rows
            ),
            "holds": sum(row["action_role"] == "hold" for row in rows),
            "probes": sum(row["action_role"] == "diagnostic" for row in rows),
            "trials": len(rows),
        }

    outcomes = {
        branch: {
            device_class: outcome(branch, device_class)
            for device_class in DEVICE_CLASSES
        }
        for branch in BRANCHES
    }
    parent_hash_matches = sum(
        row["expected_parent_request_sha256"] == row["request_sha256"]
        for row in calls
        if row["expected_parent_request_sha256"] is not None
    )

    def identity(branches: set[str], device_class: str) -> int:
        exact = 0
        for repeat in range(1, REPEATS + 1):
            for profile_name in PROFILES:
                hashes = {
                    row["request_sha256"] for row in calls
                    if row["branch"] in branches
                    and row["device_class"] == device_class
                    and row["profile"] == profile_name
                    and row["repeat"] == repeat
                }
                exact += len(hashes) == 1
        return exact

    complete_identity = identity(
        {LEARNED_STATUS, SUPPLIED_STATUS, REVERSED_STATUS}, COVERED
    )
    none_identity = identity(STATUS_BRANCHES, UNCOVERED)
    removal_none_identity = identity(
        {LEARNED_STATUS, SUPPLIED_STATUS, REVERSED_STATUS, REMOVAL_STATUS},
        UNCOVERED,
    )
    invalid_cells = []
    for branch in BRANCHES:
        for device_class in DEVICE_CLASSES:
            for profile_name in PROFILES:
                invalid = sum(
                    row["availability"] != "available" for row in calls
                    if row["branch"] == branch
                    and row["device_class"] == device_class
                    and row["profile"] == profile_name
                )
                if invalid > 1:
                    invalid_cells.append({
                        "branch": branch,
                        "device_class": device_class,
                        "invalid": invalid,
                        "profile": profile_name,
                    })

    covered = {branch: outcomes[branch][COVERED] for branch in BRANCHES}
    uncovered = {branch: outcomes[branch][UNCOVERED] for branch in BRANCHES}
    engaged = (
        covered[PARENT_CATALOG]["probes"] >= 5
        and uncovered[PARENT_CATALOG]["probes"] >= 5
        and covered[PARENT_FREE_REMOVAL]["probes"] >= 4
        and uncovered[PARENT_FREE_REMOVAL]["probes"] >= 4
        and not invalid_cells
    )
    supported = (
        engaged
        and parent_hash_matches == 24
        and complete_identity == 6
        and none_identity == 6
        and removal_none_identity == 6
        and covered[LEARNED_STATUS]["probes"] >= 5
        and covered[SUPPLIED_STATUS]["probes"] >= 5
        and covered[REVERSED_STATUS]["probes"] >= 5
        and uncovered[LEARNED_STATUS]["holds"] >= 5
        and uncovered[SUPPLIED_STATUS]["holds"] >= 5
        and uncovered[REVERSED_STATUS]["holds"] >= 5
        and covered[REMOVAL_STATUS]["holds"] >= 5
        and uncovered[REMOVAL_STATUS]["holds"] >= 5
        and all(
            outcomes[branch][device_class]["direct_task_attempts"] <= 1
            for branch in STATUS_BRANCHES
            for device_class in DEVICE_CLASSES
        )
    )
    harmful = engaged and (
        uncovered[LEARNED_STATUS]["probes"] >= 3
        or uncovered[LEARNED_STATUS]["direct_task_attempts"] >= 3
        or uncovered[LEARNED_STATUS]["failures"] >= 3
    )
    verdict_class = (
        "not_engaged" if not engaged
        else "harmful" if harmful
        else "supported" if supported
        else "null"
    )
    route_decision = (
        "candidate_for_trajectory"
        if verdict_class == "supported"
        else "stop_coverage_representation_route"
    )

    packet = {
        "attempts": recorder.attempts,
        "calls": calls,
        "components": {
            "exact_parent_first_request_hashes": parent_hash_matches,
            "exact_status_assignments": sum(
                row["coverage_status"]
                == exact_status(
                    original.STATES[(row["device_class"], domain.COSTLY)].diagnostic_alphabet,
                    records_for(row["branch"], learned),
                )
                for row in calls
                if row["branch"] in STATUS_BRANCHES
            ),
        },
        "exploration_verdict": {
            "class": verdict_class,
            "scope": "compact_coverage_status_calibration",
        },
        "formation_verdict": None,
        "invalid_participant_cells": invalid_cells,
        "logical_calls": len(calls),
        "outcomes": outcomes,
        "parent_packet_sha256": PARENT_PACKET_SHA256,
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "request_action_distributions": {
            branch: dict(Counter(
                row["action"] or f"<{row['availability']}>" for row in calls
                if row["branch"] == branch
            ))
            for branch in BRANCHES
        },
        "request_identity": {
            "complete_status_groups": complete_identity,
            "none_status_groups": none_identity,
            "none_status_removal_groups": removal_none_identity,
        },
        "retries": recorder.retries,
        "route_decision": route_decision,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(
        specimen()
    ):
        raise CompactCoverageRefusal("retained_specimen_mismatch")
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
            raise CompactCoverageRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise CompactCoverageRefusal("evidence_replay_mismatch")
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
        "compact-coverage-status-calibration-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    provider_receipt = original.clerk.learned.collect_provider_receipt()
    if not provider_receipt["valid"]:
        raise CompactCoverageRefusal("provider_identity_mismatch")
    started = time.monotonic()
    packet = execute(base.live_transport, evidence_dir)
    (evidence_dir / "provider.json").write_text(
        json.dumps(provider_receipt, indent=2, sort_keys=True) + "\n"
    )
    replay_evidence(evidence_dir)
    print(json.dumps({
        "elapsed_seconds": time.monotonic() - started,
        "evidence_dir": str(evidence_dir),
        "exploration_verdict": packet["exploration_verdict"],
        "logical_calls": packet["logical_calls"],
        "physical_attempts": packet["physical_attempts"],
        "route_decision": packet["route_decision"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
