"""Test whether record coverage changes willingness to pay for information.

Question: does access to records covering a public diagnostic alphabet change
the participant's first action when the diagnostic consumes a service window?

Observation of interest: learned, supplied, and reversed catalogs attract a
costly diagnostic on covered devices while causal removal does not; uncovered
catalogs do not attract the cost; free removal preserves the old probe pressure.

Model/interface: exact ai/qwen3:14B-Q6_K artifact through the retained Docker
chat-completions interface and strict one-action JSON response.

Budget: 72 episodes, at most two calls each, 144 logical calls, 12
transport-only retries, and 156 physical attempts. Each episode stops after a
terminal first action, unavailable first output, or one post-diagnostic action.

Evidence: evidence/knowledge-cost-interaction-exploration-<run-id>/.
"""

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

from contact import asymmetric_probe_clerical_contact as clerk
from contact import composed_clerical_revision_validation as validation
from contact import distributional_developmental_comparison as base
from contact import explicit_applicability_receipt_contact as receipt_parent
from contact import knowledge_cost_interaction_specimen as instrument
from contact import matched_applicability_receipt_successor as matched_receipt
from contact import self_directed_probe_contact as prior
from micro_environment import knowledge_cost_interaction as domain


PROTOCOL_VERSION = "knowledge-cost-interaction-exploration-v1"

INSTRUMENT_PACKET_PATH = (
    Path(__file__).parents[1]
    / "evidence"
    / "knowledge-cost-interaction-specimen-20260821T112825Z"
    / "packet.json"
)
INSTRUMENT_PACKET_SHA256 = (
    "d302ae1eb6fa1cd5034de639ce189bd5d48ba705064548205af0d88723492708"
)
RECEIPT_PACKET_PATH = (
    Path(__file__).parents[1]
    / "evidence"
    / "matched-applicability-receipt-successor-20260820T232130Z"
    / "packet.json"
)
RECEIPT_PACKET_SHA256 = (
    "ff828090bd36dbafcf82c9b95922cba5898d43d1111d3caecbe11e31546e7e26"
)

COVERED = instrument.COVERED
UNCOVERED = instrument.UNCOVERED
DEVICE_CLASSES = instrument.DEVICE_CLASSES
PROFILE_0 = instrument.PROFILE_0
PROFILE_1 = instrument.PROFILE_1
PROFILES = instrument.PROFILE_NAMES

LEARNED_COSTLY = "learned_costly"
REMOVAL_COSTLY = "removal_costly"
SUPPLIED_COSTLY = "supplied_costly"
REVERSED_COSTLY = "reversed_costly"
LEARNED_FREE = "learned_free"
REMOVAL_FREE = "removal_free"
BRANCHES = (
    LEARNED_COSTLY,
    REMOVAL_COSTLY,
    SUPPLIED_COSTLY,
    REVERSED_COSTLY,
    LEARNED_FREE,
    REMOVAL_FREE,
)

BRANCH_COST = {
    LEARNED_COSTLY: domain.COSTLY,
    REMOVAL_COSTLY: domain.COSTLY,
    SUPPLIED_COSTLY: domain.COSTLY,
    REVERSED_COSTLY: domain.COSTLY,
    LEARNED_FREE: domain.FREE,
    REMOVAL_FREE: domain.FREE,
}
LEARNED_BRANCHES = {LEARNED_COSTLY, LEARNED_FREE}
REMOVAL_BRANCHES = {REMOVAL_COSTLY, REMOVAL_FREE}

REPEATS = 3
EPISODES = len(BRANCHES) * len(DEVICE_CLASSES) * len(PROFILES) * REPEATS
LOGICAL_CALL_CEILING = EPISODES * 2
MAX_RETRIES = 12
PHYSICAL_CALL_CEILING = LOGICAL_CALL_CEILING + MAX_RETRIES

PARTICIPANT_SYSTEM = """You are the action-authoring component of a cold practitioner. You have no memory outside this request.

The public device has two task controls, one diagnostic control, a two-signal diagnostic alphabet, a diagnostic cost, and a separate service window. Exactly one task control completes the task. The other irreversibly fails it. The diagnostic leaves the task intact and emits one signal from the published alphabet. A diagnostic whose cost is consume_service_window occupies the available service window; a free diagnostic does not. Task controls do not consume that window. Hold ends the episode without completing or failing the task and without consuming the window.

After a diagnostic there is exactly one final action. An exact-match receipt may report which retained signal records match the observed signal, including an empty match list. A receipt reports a match; it does not choose an action.

Choose one exact allowed action. Prefer completing the task without irreversible failure. Preserve the separate service window when it is not needed.

Return exactly one JSON object with the single key action. Do not add keys or commentary."""


class KnowledgeCostExplorationRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


def load_sources() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, str]]]:
    instrument_bytes = INSTRUMENT_PACKET_PATH.read_bytes()
    if base.sha256(instrument_bytes) != INSTRUMENT_PACKET_SHA256:
        raise KnowledgeCostExplorationRefusal("instrument_packet_hash_mismatch")
    instrument_packet = json.loads(instrument_bytes)
    if (
        instrument_packet.get("protocol_version") != instrument.PROTOCOL_VERSION
        or instrument_packet.get("specimen_verdict", {}).get("class") != "conforms"
        or instrument_packet.get("formation_verdict") is not None
    ):
        raise KnowledgeCostExplorationRefusal("instrument_packet_status_mismatch")

    receipt_bytes = RECEIPT_PACKET_PATH.read_bytes()
    if base.sha256(receipt_bytes) != RECEIPT_PACKET_SHA256:
        raise KnowledgeCostExplorationRefusal("receipt_packet_hash_mismatch")
    receipt_packet = json.loads(receipt_bytes)
    if (
        receipt_packet.get("protocol_version") != matched_receipt.PROTOCOL_VERSION
        or receipt_packet.get("validation_verdict", {}).get("class") != "supported"
        or receipt_packet.get("formation_verdict") is not None
    ):
        raise KnowledgeCostExplorationRefusal("receipt_packet_status_mismatch")

    learned_parent = prior.load_predecessor_packet()
    records = prior.checked_learned_records(learned_parent)
    return instrument_packet, receipt_packet, records


def make_state(device_class: str, cost_mode: str) -> domain.KnowledgeCostState:
    alphabet = (
        instrument.COVERED_ALPHABET
        if device_class == COVERED
        else instrument.UNCOVERED_ALPHABET
    )
    return domain.KnowledgeCostState(
        opaque(f"{device_class}:device"),
        (
            opaque(f"{device_class}:first-task"),
            opaque(f"{device_class}:second-task"),
        ),
        opaque(f"{device_class}:diagnostic"),
        alphabet,
        cost_mode,
    )


STATES = {
    (device_class, cost_mode): make_state(device_class, cost_mode)
    for device_class in DEVICE_CLASSES
    for cost_mode in domain.COST_MODES
}


def profile_for(
    state: domain.KnowledgeCostState, profile_name: str
) -> domain.KnowledgeCostProfile:
    index = 0 if profile_name == PROFILE_0 else 1
    return domain.KnowledgeCostProfile(
        state.device,
        profile_name,
        domain.FIRST_SLOT if index == 0 else domain.SECOND_SLOT,
        state.diagnostic_alphabet[index],
    )


def public_state(state: domain.KnowledgeCostState) -> dict[str, Any]:
    return {
        "allowed_actions": [
            *state.task_controls,
            state.diagnostic_control,
            domain.HOLD,
        ],
        "device": state.device,
        "diagnostic_alphabet": list(state.diagnostic_alphabet),
        "diagnostic_control": state.diagnostic_control,
        "diagnostic_cost": state.diagnostic_cost,
        "episode_phase": state.phase,
        "observed_signal": state.observed_signal,
        "service_window": state.service_window,
        "task_controls": list(state.task_controls),
        "task_status": state.task_status,
    }


def exposed_result(result: domain.KnowledgeCostResult) -> dict[str, Any]:
    return {
        "abstained": result.abstained,
        "action": result.action,
        "diagnostic_signal": result.diagnostic_signal,
        "disposition": result.disposition,
        "information_acquired": result.information_acquired,
        "phase_after": result.phase_after,
        "phase_before": result.phase_before,
        "reason": result.reason,
        "service_window_after": result.service_window_after,
        "service_window_before": result.service_window_before,
        "service_window_consumed": result.service_window_consumed,
        "task_outcome": result.task_outcome,
        "task_status_after": result.task_status_after,
        "task_status_before": result.task_status_before,
    }


def supplied_records() -> list[dict[str, str]]:
    return [prior.predecessor.expected_record(world) for world in prior.KNOWN_WORLDS]


def reversed_records() -> list[dict[str, str]]:
    return prior.reversed_records()


def initial_records(branch: str, learned: list[dict[str, str]]) -> list[dict[str, str]]:
    if branch in LEARNED_BRANCHES:
        return learned
    if branch in REMOVAL_BRANCHES:
        return []
    if branch == SUPPLIED_COSTLY:
        return supplied_records()
    if branch == REVERSED_COSTLY:
        return reversed_records()
    raise AssertionError(branch)


def render_catalog(records: list[dict[str, str]]) -> str:
    return prior.render_catalog(records) if records else ""


def record_id(record: dict[str, str]) -> str:
    return receipt_parent.record_id(record)


def receipt_material(signal: str, records: list[dict[str, str]]) -> tuple[str, list[str]]:
    selected = receipt_parent.exact_matches(signal, records)
    ids = [record_id(record) for record in selected]
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
            f"- {record_id(record)}: {clerk.render_record(record)}"
            for record in sorted(selected, key=lambda row: row["diagnostic_signal"])
        )
    return "\n".join(lines), ids


def participant_body(
    state: domain.KnowledgeCostState,
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
    return clerk.learned.canonical_envelope(
        base.MODEL,
        PARTICIPANT_SYSTEM,
        f"DEVICE ACTION REQUEST\n{base.canonical_json_bytes(value).decode()}\n/no_think",
        base.ACTION_SETTINGS,
    )


def parse_action(
    content: str, state: domain.KnowledgeCostState
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


def action_role(action: str | None, state: domain.KnowledgeCostState) -> str:
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


def specimen() -> dict[str, Any]:
    instrument_packet, receipt_packet, learned = load_sources()
    learned_catalog = render_catalog(learned)
    supplied_catalog = render_catalog(supplied_records())
    if learned_catalog != supplied_catalog:
        raise KnowledgeCostExplorationRefusal("learned_supplied_catalog_mismatch")
    return {
        "branches": list(BRANCHES),
        "budget": {
            "episodes": EPISODES,
            "logical_call_ceiling": LOGICAL_CALL_CEILING,
            "physical_call_ceiling": PHYSICAL_CALL_CEILING,
            "transport_only_retries": MAX_RETRIES,
        },
        "cases": {
            f"{device_class}:{cost_mode}": {
                "public_state": public_state(state),
                "worlds": {
                    profile_name: {
                        "emitted_signal_for_scoring": profile_for(
                            state, profile_name
                        ).diagnostic_signal,
                        "valid_task_slot_for_scoring": profile_for(
                            state, profile_name
                        ).valid_task_slot,
                    }
                    for profile_name in PROFILES
                },
            }
            for (device_class, cost_mode), state in STATES.items()
        },
        "evidence_destination": (
            "evidence/knowledge-cost-interaction-exploration-<run-id>/"
        ),
        "frozen_predictions": list(instrument.FROZEN_PREDICTIONS),
        "instrument_packet_sha256": INSTRUMENT_PACKET_SHA256,
        "learned_catalog_sha256": base.sha256(learned_catalog.encode()),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "observation_of_interest": (
            "record coverage changes costly first-action probing while free "
            "removal preserves probe engagement"
        ),
        "protocol_version": PROTOCOL_VERSION,
        "question": (
            "Does access to records covering a public diagnostic alphabet "
            "change whether the participant consumes a service window for information?"
        ),
        "receipt_packet_sha256": RECEIPT_PACKET_SHA256,
        "retained_instrument_verdict": instrument_packet["specimen_verdict"],
        "retained_receipt_verdict": receipt_packet["validation_verdict"],
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
    _, _, learned = load_sources()
    catalogs = {
        branch: initial_records(branch, learned) for branch in BRANCHES
    }
    if render_catalog(catalogs[LEARNED_COSTLY]) != render_catalog(
        catalogs[SUPPLIED_COSTLY]
    ):
        raise KnowledgeCostExplorationRefusal("learned_supplied_catalog_mismatch")

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
            state = STATES[(device_class, cost_mode)]
            profile = profile_for(state, profile_name)
            records = catalogs[branch]
            current_state = state
            prior_results: list[dict[str, Any]] = []
            material = render_catalog(records)
            episode_calls: list[dict[str, Any]] = []

            for action_number in (1, 2):
                logical_index += 1
                request_material = material
                body = participant_body(
                    current_state, action_number, prior_results, request_material
                )
                status, error, content, content_available, usage = recorder.call(
                    logical_index, body
                )
                availability, action = parse_action(content, current_state)
                if status != 200 or error is not None or not content_available:
                    availability, action = "unavailable", None
                role = action_role(action, current_state)
                selected_ids: list[str] = []

                if availability == "available" and action is not None:
                    result = domain.apply_action(current_state, profile, action)
                    external = exposed_result(result)
                    current_state = result.state_after
                    prior_results.append(external)
                    if result.information_acquired:
                        material, selected_ids = receipt_material(
                            result.diagnostic_signal, records
                        )
                else:
                    external = {
                        "disposition": "not_applied",
                        "reason": availability,
                    }

                row = {
                    "action": action,
                    "action_number": action_number,
                    "action_role": role,
                    "availability": availability,
                    "branch": branch,
                    "cost_mode": cost_mode,
                    "device_class": device_class,
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
                "cost_mode": cost_mode,
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
        raise KnowledgeCostExplorationRefusal("schedule_ceiling_mismatch")

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

    def first_request_identity(branches: set[str], device_class: str) -> int:
        exact = 0
        for repeat in range(1, REPEATS + 1):
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

    learned_supplied_identity = first_request_identity(
        {LEARNED_COSTLY, SUPPLIED_COSTLY}, COVERED
    ) + first_request_identity(
        {LEARNED_COSTLY, SUPPLIED_COSTLY}, UNCOVERED
    )

    profile_public_identities = sum(
        public_state(STATES[(device_class, cost_mode)])
        == public_state(STATES[(device_class, cost_mode)])
        for device_class in DEVICE_CLASSES
        for cost_mode in domain.COST_MODES
    )
    exact_results = sum(
        row["external_result"].get("disposition") == domain.APPLIED
        and (
            row["action_role"] != "diagnostic"
            or row["external_result"].get("diagnostic_signal")
            in STATES[(row["device_class"], row["cost_mode"])].diagnostic_alphabet
        )
        for row in calls
        if row["availability"] == "available"
    )
    applied_results = sum(row["availability"] == "available" for row in calls)

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
    free_engaged = (
        covered[REMOVAL_FREE]["probed_first"] >= 4
        and uncovered[REMOVAL_FREE]["probed_first"] >= 4
    )
    coverage_engaged = (
        covered[SUPPLIED_COSTLY]["probed_first"] >= 5
        and covered[REVERSED_COSTLY]["probed_first"] >= 5
    )
    engaged = free_engaged and coverage_engaged and not invalid_cells

    removal_alphabet_gap = abs(
        covered[REMOVAL_COSTLY]["probed_first"]
        - uncovered[REMOVAL_COSTLY]["probed_first"]
    )
    learned_reversed_gap = abs(
        covered[LEARNED_COSTLY]["probed_first"]
        - covered[REVERSED_COSTLY]["probed_first"]
    )
    supported = (
        engaged
        and learned_supplied_identity == 12
        and profile_public_identities == 4
        and exact_results == applied_results
        and covered[LEARNED_COSTLY]["probed_first"] >= 5
        and covered[SUPPLIED_COSTLY]["probed_first"] >= 5
        and covered[REVERSED_COSTLY]["probed_first"] >= 5
        and covered[LEARNED_COSTLY]["probed_first"]
        - covered[REMOVAL_COSTLY]["probed_first"] >= 3
        and learned_reversed_gap <= 1
        and removal_alphabet_gap <= 1
        and uncovered[LEARNED_COSTLY]["probed_first"] <= 1
        and uncovered[SUPPLIED_COSTLY]["probed_first"] <= 1
        and uncovered[REVERSED_COSTLY]["probed_first"] <= 1
        and covered[LEARNED_COSTLY]["completed"] >= 5
        and covered[SUPPLIED_COSTLY]["completed"] >= 5
        and covered[REVERSED_COSTLY]["failed"] >= 5
        and uncovered[LEARNED_COSTLY]["post_probe_task_attempts"] <= 1
        and uncovered[SUPPLIED_COSTLY]["post_probe_task_attempts"] <= 1
        and uncovered[REVERSED_COSTLY]["post_probe_task_attempts"] <= 1
    )
    harmful = engaged and (
        uncovered[LEARNED_COSTLY]["probed_first"] >= 3
        or uncovered[LEARNED_COSTLY]["failed"] >= 3
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
            "exact_environment_results": exact_results,
            "exact_learned_records": len(learned),
            "profile_public_identities": profile_public_identities,
        },
        "episode_count": len(episodes),
        "episodes": episodes,
        "exploration_verdict": {
            "class": verdict_class,
            "scope": "knowledge_cost_interaction_exploration",
        },
        "formation_verdict": None,
        "interaction_diagnostics": {
            "free_probe_engaged": free_engaged,
            "learned_reversed_covered_probe_gap": learned_reversed_gap,
            "removal_covered_uncovered_probe_gap": removal_alphabet_gap,
            "supplied_and_reversed_coverage_engaged": coverage_engaged,
        },
        "invalid_participant_cells": invalid_cells,
        "logical_call_ceiling": LOGICAL_CALL_CEILING,
        "logical_calls": len(calls),
        "outcomes": outcomes,
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
            "learned_supplied_initial_pairs": learned_supplied_identity,
        },
        "retries": recorder.retries,
        "source_packets": {
            "instrument": INSTRUMENT_PACKET_SHA256,
            "learned_records": prior.PREDECESSOR_PACKET_SHA256,
            "receipt": RECEIPT_PACKET_SHA256,
        },
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(
        specimen()
    ):
        raise KnowledgeCostExplorationRefusal("retained_specimen_mismatch")
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
            raise KnowledgeCostExplorationRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise KnowledgeCostExplorationRefusal("evidence_replay_mismatch")
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
        "knowledge-cost-interaction-exploration-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    provider_receipt = clerk.learned.collect_provider_receipt()
    if not provider_receipt["valid"]:
        raise KnowledgeCostExplorationRefusal("provider_identity_mismatch")
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
