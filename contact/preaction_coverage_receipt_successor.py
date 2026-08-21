"""Test an explicit alphabet-to-record coverage receipt before costly probing.

Question: does a factual pre-action coverage receipt make a costly diagnostic
attractive only when every public signal has a retained interpretation?

Observation of interest: learned, supplied, and reversed complete receipts
cause covered probes; learned and supplied uncovered receipts plus removal
receipts cause first-action hold; reversed records fail only after probing.

Model/interface: exact ai/qwen3:14B-Q6_K artifact through the retained Docker
chat-completions interface and strict one-action JSON response.

Budget: 96 episodes, at most two calls each, 192 logical calls, 12
transport-only retries, and 204 physical attempts. Each episode stops after a
terminal first action, unavailable first output, or one post-diagnostic action.

Evidence: evidence/preaction-coverage-receipt-successor-<run-id>/.
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
from contact import knowledge_cost_interaction_exploration as parent
from micro_environment import knowledge_cost_interaction as domain


PROTOCOL_VERSION = "preaction-coverage-receipt-successor-v1"
PARENT_PACKET_PATH = (
    Path(__file__).parents[1]
    / "evidence"
    / "knowledge-cost-interaction-exploration-20260821T132804Z"
    / "packet.json"
)
PARENT_PACKET_SHA256 = (
    "7c56a0b7d08ad6e6c5a51ae4a5f4c4cc9b2ea4c1517faa2f62c08e2e25862374"
)

LEARNED_RECEIPT = "learned_coverage_receipt"
REMOVAL_RECEIPT = "removal_coverage_receipt"
SUPPLIED_RECEIPT = "supplied_coverage_receipt"
REVERSED_RECEIPT = "reversed_coverage_receipt"
PARENT_LEARNED_COSTLY = "exact_parent_learned_costly"
PARENT_REMOVAL_COSTLY = "exact_parent_removal_costly"
PARENT_LEARNED_FREE = "exact_parent_learned_free"
PARENT_REMOVAL_FREE = "exact_parent_removal_free"
BRANCHES = (
    LEARNED_RECEIPT,
    REMOVAL_RECEIPT,
    SUPPLIED_RECEIPT,
    REVERSED_RECEIPT,
    PARENT_LEARNED_COSTLY,
    PARENT_REMOVAL_COSTLY,
    PARENT_LEARNED_FREE,
    PARENT_REMOVAL_FREE,
)
RECEIPT_BRANCHES = {
    LEARNED_RECEIPT,
    REMOVAL_RECEIPT,
    SUPPLIED_RECEIPT,
    REVERSED_RECEIPT,
}
PARENT_BRANCH = {
    PARENT_LEARNED_COSTLY: parent.LEARNED_COSTLY,
    PARENT_REMOVAL_COSTLY: parent.REMOVAL_COSTLY,
    PARENT_LEARNED_FREE: parent.LEARNED_FREE,
    PARENT_REMOVAL_FREE: parent.REMOVAL_FREE,
}
BRANCH_COST = {
    LEARNED_RECEIPT: domain.COSTLY,
    REMOVAL_RECEIPT: domain.COSTLY,
    SUPPLIED_RECEIPT: domain.COSTLY,
    REVERSED_RECEIPT: domain.COSTLY,
    **{
        branch: parent.BRANCH_COST[parent_branch]
        for branch, parent_branch in PARENT_BRANCH.items()
    },
}

COVERED = parent.COVERED
UNCOVERED = parent.UNCOVERED
DEVICE_CLASSES = parent.DEVICE_CLASSES
PROFILES = parent.PROFILES
REPEATS = 3
EPISODES = len(BRANCHES) * len(DEVICE_CLASSES) * len(PROFILES) * REPEATS
LOGICAL_CALL_CEILING = EPISODES * 2
MAX_RETRIES = 12
PHYSICAL_CALL_CEILING = LOGICAL_CALL_CEILING + MAX_RETRIES


class PreactionCoverageRefusal(ValueError):
    pass


def load_parent() -> tuple[dict[str, Any], list[dict[str, str]]]:
    packet_bytes = PARENT_PACKET_PATH.read_bytes()
    if base.sha256(packet_bytes) != PARENT_PACKET_SHA256:
        raise PreactionCoverageRefusal("parent_packet_hash_mismatch")
    packet = json.loads(packet_bytes)
    if (
        packet.get("protocol_version") != parent.PROTOCOL_VERSION
        or packet.get("exploration_verdict", {}).get("class") != "harmful"
        or packet.get("formation_verdict") is not None
    ):
        raise PreactionCoverageRefusal("parent_packet_status_mismatch")
    _, _, records = parent.load_sources()
    return packet, records


def records_for(branch: str, learned: list[dict[str, str]]) -> list[dict[str, str]]:
    if branch in {LEARNED_RECEIPT, PARENT_LEARNED_COSTLY, PARENT_LEARNED_FREE}:
        return learned
    if branch in {REMOVAL_RECEIPT, PARENT_REMOVAL_COSTLY, PARENT_REMOVAL_FREE}:
        return []
    if branch == SUPPLIED_RECEIPT:
        return parent.supplied_records()
    if branch == REVERSED_RECEIPT:
        return parent.reversed_records()
    raise AssertionError(branch)


def coverage_value(
    alphabet: tuple[str, str], records: list[dict[str, str]]
) -> dict[str, Any]:
    matches = {
        signal: [
            parent.record_id(record)
            for record in records
            if record["diagnostic_signal"] == signal
        ]
        for signal in alphabet
    }
    return {
        "diagnostic_alphabet": list(alphabet),
        "matching_record_ids_by_signal": matches,
        "uncovered_signals": [
            signal for signal, record_ids in matches.items() if not record_ids
        ],
    }


def coverage_material(
    state: domain.KnowledgeCostState, records: list[dict[str, str]]
) -> str:
    lines = []
    catalog = parent.render_catalog(records)
    if catalog:
        lines.append(catalog)
    lines.extend((
        "PRE-ACTION COVERAGE RECEIPT",
        base.canonical_json_bytes(
            coverage_value(state.diagnostic_alphabet, records)
        ).decode(),
    ))
    return "\n\n".join(lines)


def initial_material(
    branch: str,
    state: domain.KnowledgeCostState,
    records: list[dict[str, str]],
) -> str:
    if branch in RECEIPT_BRANCHES:
        return coverage_material(state, records)
    return parent.render_catalog(records)


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


def parent_first_hashes(packet: dict[str, Any]) -> dict[tuple[int, str, str, str], str]:
    return {
        (row["repeat"], row["profile"], row["device_class"], row["branch"]): row[
            "request_sha256"
        ]
        for row in packet["calls"]
        if row["action_number"] == 1
    }


def specimen() -> dict[str, Any]:
    packet, learned = load_parent()
    if parent.render_catalog(learned) != parent.render_catalog(
        parent.supplied_records()
    ):
        raise PreactionCoverageRefusal("learned_supplied_catalog_mismatch")
    cases = {}
    for device_class in DEVICE_CLASSES:
        for cost_mode in domain.COST_MODES:
            state = parent.STATES[(device_class, cost_mode)]
            cases[f"{device_class}:{cost_mode}"] = {
                "public_state": parent.public_state(state),
                "coverage": {
                    "learned": coverage_value(state.diagnostic_alphabet, learned),
                    "removal": coverage_value(state.diagnostic_alphabet, []),
                    "reversed": coverage_value(
                        state.diagnostic_alphabet, parent.reversed_records()
                    ),
                    "supplied": coverage_value(
                        state.diagnostic_alphabet, parent.supplied_records()
                    ),
                },
            }
    return {
        "branches": list(BRANCHES),
        "budget": {
            "episodes": EPISODES,
            "logical_call_ceiling": LOGICAL_CALL_CEILING,
            "physical_call_ceiling": PHYSICAL_CALL_CEILING,
            "transport_only_retries": MAX_RETRIES,
        },
        "cases": cases,
        "evidence_destination": (
            "evidence/preaction-coverage-receipt-successor-<run-id>/"
        ),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "observation_of_interest": (
            "an exact pre-action coverage receipt separates useful from useless "
            "costly probes without using record correctness"
        ),
        "parent_packet_sha256": PARENT_PACKET_SHA256,
        "parent_verdict": packet["exploration_verdict"],
        "protocol_version": PROTOCOL_VERSION,
        "question": (
            "Does an explicit alphabet-to-record coverage receipt make costly "
            "probing selective before the signal is observed?"
        ),
        "schedule": [list(row) for row in schedule()],
        "stopping_rule": (
            "stop each episode after a terminal first action, unavailable first "
            "output, or one post-diagnostic action; never resample valid output"
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
    parent_packet, learned = load_parent()
    expected_parent_hashes = parent_first_hashes(parent_packet)

    with configured_recorder():
        recorder = validation.verifier.Recorder(transport, evidence_dir)
        if evidence_dir is not None:
            (evidence_dir / "specimen.json").write_bytes(
                base.canonical_json_bytes(specimen())
            )
        logical_index = 0
        calls: list[dict[str, Any]] = []
        episodes: list[dict[str, Any]] = []

        for repeat, profile_name, device_class, branch in schedule():
            cost_mode = BRANCH_COST[branch]
            state = parent.STATES[(device_class, cost_mode)]
            profile = parent.profile_for(state, profile_name)
            records = records_for(branch, learned)
            material = initial_material(branch, state, records)
            current_state = state
            prior_results: list[dict[str, Any]] = []
            episode_calls: list[dict[str, Any]] = []

            for action_number in (1, 2):
                logical_index += 1
                request_material = material
                body = parent.participant_body(
                    current_state, action_number, prior_results, request_material
                )
                status, error, content, content_available, usage = recorder.call(
                    logical_index, body
                )
                availability, action = parent.parse_action(content, current_state)
                if status != 200 or error is not None or not content_available:
                    availability, action = "unavailable", None
                role = parent.action_role(action, current_state)
                selected_ids: list[str] = []

                if availability == "available" and action is not None:
                    result = domain.apply_action(current_state, profile, action)
                    external = parent.exposed_result(result)
                    current_state = result.state_after
                    prior_results.append(external)
                    if result.information_acquired:
                        material, selected_ids = parent.receipt_material(
                            result.diagnostic_signal, records
                        )
                else:
                    external = {
                        "disposition": "not_applied",
                        "reason": availability,
                    }

                expected_parent_hash = None
                if action_number == 1 and branch in PARENT_BRANCH:
                    expected_parent_hash = expected_parent_hashes[
                        (repeat, profile_name, device_class, PARENT_BRANCH[branch])
                    ]
                row = {
                    "action": action,
                    "action_number": action_number,
                    "action_role": role,
                    "availability": availability,
                    "branch": branch,
                    "cost_mode": cost_mode,
                    "device_class": device_class,
                    "expected_parent_request_sha256": expected_parent_hash,
                    "external_result": external,
                    "profile": profile_name,
                    "provider_usage": usage,
                    "repeat": repeat,
                    "request_sha256": base.sha256(body),
                    "responsibility": "participant_device_action",
                    "retained_material_sha256": base.sha256(
                        request_material.encode()
                    ),
                    "selected_record_ids": selected_ids,
                }
                calls.append(row)
                episode_calls.append(row)

                if (
                    current_state.phase == domain.TERMINAL
                    or availability != "available"
                    or action_number == 2
                ):
                    break

            first = episode_calls[0]
            second = episode_calls[1] if len(episode_calls) == 2 else None
            episodes.append({
                "branch": branch,
                "call_count": len(episode_calls),
                "completed": current_state.task_status == domain.COMPLETED,
                "device_class": device_class,
                "direct_task_first": first["action_role"] in {
                    "first_task_control", "second_task_control"
                },
                "failed": current_state.task_status == domain.FAILED,
                "first_action_role": first["action_role"],
                "held_first": first["action_role"] == "hold",
                "post_probe_task_attempt": (
                    second is not None
                    and second["action_role"] in {
                        "first_task_control", "second_task_control"
                    }
                ),
                "probe_first": first["action_role"] == "diagnostic",
                "profile": profile_name,
                "repeat": repeat,
                "second_action_role": (
                    second["action_role"] if second is not None else None
                ),
                "service_window_consumed": any(
                    row["external_result"].get("service_window_consumed", False)
                    for row in episode_calls
                ),
                "unfinished": current_state.task_status == domain.INTACT,
            })

    if len(episodes) != EPISODES or logical_index > LOGICAL_CALL_CEILING:
        raise PreactionCoverageRefusal("schedule_ceiling_mismatch")

    def outcome(branch: str, device_class: str) -> dict[str, int]:
        rows = [
            row for row in episodes
            if row["branch"] == branch and row["device_class"] == device_class
        ]
        return {
            "completed": sum(row["completed"] for row in rows),
            "direct_task_first": sum(row["direct_task_first"] for row in rows),
            "failed": sum(row["failed"] for row in rows),
            "held_first": sum(row["held_first"] for row in rows),
            "post_probe_task_attempts": sum(
                row["post_probe_task_attempt"] for row in rows
            ),
            "probed_first": sum(row["probe_first"] for row in rows),
            "service_windows_consumed": sum(
                row["service_window_consumed"] for row in rows
            ),
            "trials": len(rows),
            "unfinished": sum(row["unfinished"] for row in rows),
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

    def initial_identity(branches: set[str]) -> int:
        exact = 0
        for repeat in range(1, REPEATS + 1):
            for device_class in DEVICE_CLASSES:
                for profile_name in PROFILES:
                    hashes = {
                        row["request_sha256"] for row in calls
                        if row["action_number"] == 1
                        and row["branch"] in branches
                        and row["device_class"] == device_class
                        and row["profile"] == profile_name
                        and row["repeat"] == repeat
                    }
                    exact += len(hashes) == 1
        return exact

    learned_supplied_identity = initial_identity(
        {LEARNED_RECEIPT, SUPPLIED_RECEIPT}
    )
    coverage_assignments_exact = sum(
        coverage_value(
            parent.STATES[(row["device_class"], domain.COSTLY)].diagnostic_alphabet,
            records_for(row["branch"], learned),
        )["uncovered_signals"]
        == (
            []
            if row["device_class"] == COVERED
            and row["branch"] in {
                LEARNED_RECEIPT, SUPPLIED_RECEIPT, REVERSED_RECEIPT
            }
            else list(parent.STATES[
                (row["device_class"], domain.COSTLY)
            ].diagnostic_alphabet)
        )
        for row in calls
        if row["action_number"] == 1 and row["branch"] in RECEIPT_BRANCHES
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
        covered[PARENT_LEARNED_COSTLY]["probed_first"] >= 5
        and uncovered[PARENT_LEARNED_COSTLY]["probed_first"] >= 5
        and covered[PARENT_REMOVAL_FREE]["probed_first"] >= 4
        and uncovered[PARENT_REMOVAL_FREE]["probed_first"] >= 4
        and covered[SUPPLIED_RECEIPT]["probed_first"] >= 5
        and covered[REVERSED_RECEIPT]["probed_first"] >= 5
        and not invalid_cells
    )
    reversed_probe_gap = abs(
        covered[LEARNED_RECEIPT]["probed_first"]
        - covered[REVERSED_RECEIPT]["probed_first"]
    )
    removal_alphabet_gap = abs(
        uncovered[REMOVAL_RECEIPT]["probed_first"]
        - covered[REMOVAL_RECEIPT]["probed_first"]
    )
    supported = (
        engaged
        and parent_hash_matches == 48
        and learned_supplied_identity == 12
        and coverage_assignments_exact == 48
        and covered[LEARNED_RECEIPT]["probed_first"] >= 5
        and covered[SUPPLIED_RECEIPT]["probed_first"] >= 5
        and covered[REVERSED_RECEIPT]["probed_first"] >= 5
        and reversed_probe_gap <= 1
        and uncovered[LEARNED_RECEIPT]["probed_first"] <= 1
        and uncovered[SUPPLIED_RECEIPT]["probed_first"] <= 1
        and uncovered[REVERSED_RECEIPT]["probed_first"] <= 1
        and covered[REMOVAL_RECEIPT]["probed_first"] <= 1
        and uncovered[REMOVAL_RECEIPT]["probed_first"] <= 1
        and removal_alphabet_gap <= 1
        and uncovered[LEARNED_RECEIPT]["held_first"] >= 5
        and uncovered[SUPPLIED_RECEIPT]["held_first"] >= 5
        and uncovered[REVERSED_RECEIPT]["held_first"] >= 5
        and covered[REMOVAL_RECEIPT]["held_first"] >= 5
        and uncovered[REMOVAL_RECEIPT]["held_first"] >= 5
        and covered[LEARNED_RECEIPT]["completed"] >= 5
        and covered[SUPPLIED_RECEIPT]["completed"] >= 5
        and covered[REVERSED_RECEIPT]["failed"] >= 5
    )
    harmful = engaged and (
        uncovered[LEARNED_RECEIPT]["probed_first"] >= 3
        or uncovered[LEARNED_RECEIPT]["direct_task_first"] >= 3
        or uncovered[LEARNED_RECEIPT]["failed"] >= 3
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
            "exact_coverage_assignments": coverage_assignments_exact,
            "exact_learned_records": len(learned),
            "exact_parent_first_request_hashes": parent_hash_matches,
        },
        "episode_count": len(episodes),
        "episodes": episodes,
        "exploration_verdict": {
            "class": verdict_class,
            "scope": "preaction_coverage_receipt_successor",
        },
        "formation_verdict": None,
        "interaction_diagnostics": {
            "removal_covered_uncovered_probe_gap": removal_alphabet_gap,
            "reversed_covered_probe_gap": reversed_probe_gap,
        },
        "invalid_participant_cells": invalid_cells,
        "logical_call_ceiling": LOGICAL_CALL_CEILING,
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
            "learned_supplied_receipt_pairs": learned_supplied_identity,
        },
        "retries": recorder.retries,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(
        specimen()
    ):
        raise PreactionCoverageRefusal("retained_specimen_mismatch")
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
            raise PreactionCoverageRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise PreactionCoverageRefusal("evidence_replay_mismatch")
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
        "preaction-coverage-receipt-successor-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    provider_receipt = parent.clerk.learned.collect_provider_receipt()
    if not provider_receipt["valid"]:
        raise PreactionCoverageRefusal("provider_identity_mismatch")
    started = time.monotonic()
    packet = execute(base.live_transport, evidence_dir)
    (evidence_dir / "provider.json").write_text(
        json.dumps(provider_receipt, indent=2, sort_keys=True) + "\n"
    )
    replay_evidence(evidence_dir)
    print(json.dumps({
        "elapsed_seconds": time.monotonic() - started,
        "episode_count": packet["episode_count"],
        "evidence_dir": str(evidence_dir),
        "exploration_verdict": packet["exploration_verdict"],
        "logical_calls": packet["logical_calls"],
        "physical_attempts": packet["physical_attempts"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
