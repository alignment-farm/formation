"""Test recovered-record influence in public-identical mirrored worlds."""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Callable

from contact import canonical_clerical_record_diagnostic as canonical
from contact import clerical_prose_parser_diagnostic as prose_parser
from contact import composed_clerical_revision_validation as validation
from contact import distributional_developmental_comparison as base
from contact import learned_clerical_instrument_exploration as learned
from contact import learned_clerical_revision_exploration as revision
from contact import learned_contested_counterevidence_continuation as predecessor
from contact import observational_counterevidence_comparison as observational
from contact import source_grounded_revision_admission as admission
from contact import staged_clerical_instrument_successor as staged
from micro_environment.unselected_lineage_behavior import (
    FIRST_INCREASES,
    SECOND_INCREASES,
    LineageProfile,
    LineageState,
    ProposalReceipt,
    apply_committed_action,
)
from unselected_lineage_specimen import oracle_action


PROTOCOL_VERSION = "mirrored-recovery-influence-successor-v1"
SPEC_PATH = (
    Path(__file__).parents[1]
    / "docs"
    / "MIRRORED_RECOVERY_INFLUENCE_SUCCESSOR.md"
)
PREDECESSOR_DIR = (
    Path(__file__).parents[1]
    / "evidence"
    / "learned-contested-counterevidence-continuation-20260820T214847Z"
)
PREDECESSOR_PACKET_SHA256 = (
    "9a6ee167842bd48516f401da439def019475c1a3183361893b163b5d724e5953"
)
PREDECESSOR_PROTOCOL_VERSION = predecessor.PROTOCOL_VERSION

FIRST_WORLD = "mirror_first_increases"
SECOND_WORLD = "mirror_second_increases"
WORLDS = (FIRST_WORLD, SECOND_WORLD)
WORLD_SLOTS = {
    FIRST_WORLD: FIRST_INCREASES,
    SECOND_WORLD: SECOND_INCREASES,
}
EVENT_RELATIONS = ("current_acquisition", "transient_opposite", "current_recovery")

MATCHING_CASES = tuple(
    [f"match_up_{index:02d}" for index in range(1, 5)]
    + [f"match_down_{index:02d}" for index in range(1, 5)]
)
UNRELATED_CASES = ("novel_up", "novel_down", "recombined_up", "recombined_down")
CASES = MATCHING_CASES + UNRELATED_CASES

COLD = "cold"
RECOVERED = "recovered_current_record"
REMOVED = "recovered_record_removed"
SUPPLIED = "supplied_correct_record"
BRANCHES = (COLD, RECOVERED, REMOVED, SUPPLIED)
ENGAGEMENT_BRANCHES = (RECOVERED, SUPPLIED)

REPEATS = 3
SOURCE_OCCURRENCES = len(WORLDS) * len(EVENT_RELATIONS)
CLERK_CALLS = SOURCE_OCCURRENCES * 4
NORMALIZATION_CALLS = len(CASES)
LATER_CALLS = len(WORLDS) * len(CASES) * len(BRANCHES) * REPEATS
PLANNED_LOGICAL_CALLS = CLERK_CALLS + NORMALIZATION_CALLS + LATER_CALLS
PHYSICAL_CALL_CEILING = 336
MAX_RETRIES = 12

VISIBLE_DESIGN = learned.DESIGN_SETS[0]["a"]
VISIBLE_SCOPE = {
    "beacon_class": VISIBLE_DESIGN.beacon,
    "housing_class": VISIBLE_DESIGN.housing,
}


class MirroredRecoveryRefusal(ValueError):
    pass


@dataclass(frozen=True)
class SourceEvent:
    event_id: str
    order: int
    relation_role: str
    state: LineageState
    profile: LineageProfile


@dataclass(frozen=True)
class LaterCase:
    state: LineageState
    description: str
    scope: dict[str, str]
    profiles: dict[str, LineageProfile]
    matching: bool


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


def state(label: str, position: int, target: int, family: str) -> LineageState:
    return LineageState(
        family,
        opaque(f"{label}:device"),
        position,
        target,
        (opaque(f"{label}:first"), opaque(f"{label}:second")),
    )


def record_for_slot(increasing_slot: str) -> dict[str, str]:
    first = (
        learned.INCREASES
        if increasing_slot == FIRST_INCREASES
        else learned.DECREASES
    )
    return {
        "first_control_effect": first,
        "second_control_effect": (
            learned.DECREASES if first == learned.INCREASES else learned.INCREASES
        ),
    }


def opposite_slot(increasing_slot: str) -> str:
    return (
        SECOND_INCREASES if increasing_slot == FIRST_INCREASES else FIRST_INCREASES
    )


def make_source_events(world: str, world_index: int) -> tuple[SourceEvent, ...]:
    current_slot = WORLD_SLOTS[world]
    events = []
    for order, role in enumerate(EVENT_RELATIONS, 1):
        slot = opposite_slot(current_slot) if role == "transient_opposite" else current_slot
        family = opaque(f"{world}:source:{order}:family")
        profile = LineageProfile(family, slot)
        position = 71100 + world_index * 617 + order * 139
        events.append(SourceEvent(
            f"{world}:{order}:{role}",
            order,
            role,
            state(
                f"{world}:source:{order}",
                position,
                position + (1 if (world_index + order) % 2 else -1),
                family,
            ),
            profile,
        ))
    return tuple(events)


SOURCE_EVENTS = {
    world: make_source_events(world, index)
    for index, world in enumerate(WORLDS, 1)
}


def make_later_case(case_name: str, case_index: int) -> LaterCase:
    matching = case_name in MATCHING_CASES
    if matching:
        scope = VISIBLE_SCOPE
        description = observational.surface_description(scope)
    elif case_name.startswith("novel"):
        scope = {"beacon_class": "green", "housing_class": "smooth"}
        description = observational.surface_description(scope)
    else:
        scope = {
            "beacon_class": learned.DESIGN_SETS[0]["b"].beacon,
            "housing_class": VISIBLE_DESIGN.housing,
        }
        description = observational.surface_description(scope)
    family = opaque(f"later:{case_name}:family")
    position = 75100 + case_index * 149
    target = position + (1 if "_up" in case_name else -1)
    state_value = state(f"later:{case_name}", position, target, family)
    if matching:
        profiles = {
            world: LineageProfile(family, WORLD_SLOTS[world]) for world in WORLDS
        }
    else:
        slot = FIRST_INCREASES if case_index % 2 else SECOND_INCREASES
        profiles = {world: LineageProfile(family, slot) for world in WORLDS}
    return LaterCase(state_value, description, scope, profiles, matching)


LATER_CASES = {
    case_name: make_later_case(case_name, index)
    for index, case_name in enumerate(CASES, 1)
}


def post_schedule() -> tuple[tuple[int, str, str, str], ...]:
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_index, case_name in enumerate(CASES):
            for branch_index in range(len(BRANCHES)):
                branch = BRANCHES[(repeat - 1 + branch_index) % len(BRANCHES)]
                order = WORLDS if (repeat + case_index + branch_index) % 2 else WORLDS[::-1]
                rows.extend((repeat, world, case_name, branch) for world in order)
    return tuple(rows)


def load_predecessor() -> dict[str, Any]:
    packet_bytes = (PREDECESSOR_DIR / "packet.json").read_bytes()
    if base.sha256(packet_bytes) != PREDECESSOR_PACKET_SHA256:
        raise MirroredRecoveryRefusal("predecessor_packet_hash_mismatch")
    packet = json.loads(packet_bytes)
    if (
        packet.get("protocol_version") != PREDECESSOR_PROTOCOL_VERSION
        or packet.get("validation_verdict", {}).get("class") != "null"
        or packet.get("formation_verdict") is not None
    ):
        raise MirroredRecoveryRefusal("predecessor_status_mismatch")
    return packet


def expected_movement(event: SourceEvent) -> str:
    return {
        learned.INCREASES: "increased",
        learned.DECREASES: "decreased",
    }[record_for_slot(event.profile.increasing_slot)["first_control_effect"]]


def specimen() -> dict[str, Any]:
    load_predecessor()
    return {
        "branches": list(BRANCHES),
        "cases": {
            case_name: {
                "description": case.description,
                "matching": case.matching,
                "public_device": learned.public_device(case.state, case.description),
                "scope": case.scope,
                "world_expected_actions": {
                    world: oracle_action(case.state, case.profiles[world])
                    for world in WORLDS
                },
            }
            for case_name, case in LATER_CASES.items()
        },
        "instrument_model": learned.INSTRUMENT_MODEL,
        "instrument_model_digest": learned.INSTRUMENT_MODEL_DIGEST,
        "participant_model": base.MODEL,
        "participant_model_digest": base.MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "predecessor_packet_sha256": PREDECESSOR_PACKET_SHA256,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "source_events": {
            world: [{
                "event_id": event.event_id,
                "expected_movement": expected_movement(event),
                "exploration_action": event.state.controls[0],
                "public_device": learned.public_device(
                    event.state, VISIBLE_DESIGN.source_description
                ),
                "relation_role": event.relation_role,
            } for event in SOURCE_EVENTS[world]]
            for world in WORLDS
        },
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "world_relations": WORLD_SLOTS,
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
    load_predecessor()
    with configured_recorder():
        recorder = validation.verifier.Recorder(transport, evidence_dir)
        if evidence_dir is not None:
            (evidence_dir / "specimen.json").write_bytes(
                base.canonical_json_bytes(specimen())
            )
        logical_index = 0
        calls: list[dict[str, Any]] = []
        artifacts: dict[str, list[dict[str, Any]]] = {world: [] for world in WORLDS}

        for world in WORLDS:
            for event in SOURCE_EVENTS[world]:
                action = event.state.controls[0]
                result = apply_committed_action(
                    event.state, event.profile, ProposalReceipt(True, action)
                )
                artifacts[world].append({
                    "action": action,
                    "composed": None,
                    "event": event,
                    "expected_record": record_for_slot(event.profile.increasing_slot),
                    "external_result": base.exposed_result(result),
                    "movement": result.movement_direction,
                    "prose": "",
                    "projection": None,
                    "record": None,
                    "report": learned.sensor_report(VISIBLE_DESIGN, result),
                    "sentence": "",
                    "trans": "",
                })

        flat_artifacts = [
            artifact for world in WORLDS for artifact in artifacts[world]
        ]
        for phase in ("trans", "prose", "parse"):
            for world in WORLDS:
                for artifact in artifacts[world]:
                    event = artifact["event"]
                    logical_index += 1
                    if phase == "trans":
                        body = staged.transcription_body(artifact["report"])
                    elif phase == "prose":
                        body = staged.sentence_body(artifact["trans"])
                    else:
                        body = prose_parser.parser_body(artifact["prose"])
                    content, ok, usage = available(recorder.call(logical_index, body))
                    expected_record = artifact["expected_record"]
                    if phase == "trans":
                        parsed = staged.parse_transcription(content) if ok else None
                        artifact["trans"] = content
                        expected = {
                            "observed_actuator": "first",
                            "observed_effect": expected_record["first_control_effect"],
                            "scope": VISIBLE_SCOPE,
                        }
                        exact = parsed == expected
                        responsibility = "source_transcription"
                    elif phase == "prose":
                        artifact["prose"] = content
                        exact = prose_parser.parse_explicit_sentence(content) == expected_record
                        responsibility = "source_explicit_prose"
                    else:
                        record = canonical.parse_record(content) if ok else None
                        artifact["record"] = record
                        artifact["sentence"] = canonical.render_sentence(record)
                        exact = record == expected_record
                        responsibility = "source_prose_parse"
                    calls.append({
                        "available": ok,
                        "content": content,
                        "event_id": event.event_id,
                        "exact": exact,
                        "provider_usage": usage,
                        "relation_role": event.relation_role,
                        "request_sha256": base.sha256(body),
                        "responsibility": responsibility,
                        "world": world,
                    })

        for world in WORLDS:
            for artifact in artifacts[world]:
                event = artifact["event"]
                transcript = staged.parse_transcription(artifact["trans"])
                observed = (
                    transcript["observed_actuator"]
                    if transcript is not None else "unavailable"
                )
                logical_index += 1
                body = validation.projector_body(observed, artifact["record"])
                content, ok, usage = available(recorder.call(logical_index, body))
                projection_availability, projected = validation.projection.parse_effect(content)
                if not ok:
                    projection_availability, projected = "unavailable", None
                composed = validation.admission_decision(
                    artifact["report"], artifact["trans"], artifact["record"], projected
                )
                artifact["projection"] = projected
                artifact["composed"] = composed
                calls.append({
                    "availability": projection_availability,
                    "composed_reasons": composed["reasons"],
                    "composed_status": composed["status"],
                    "content": content,
                    "event_id": event.event_id,
                    "projected_effect": projected,
                    "projection_exact": (
                        projected == artifact["expected_record"]["first_control_effect"]
                    ),
                    "provider_usage": usage,
                    "relation_role": event.relation_role,
                    "request_sha256": base.sha256(body),
                    "responsibility": "source_selected_effect_projection",
                    "world": world,
                })

        occurrences: dict[str, list[dict[str, Any]]] = {}
        transitions: dict[str, list[dict[str, Any]]] = {}
        decisions: dict[str, dict[str, Any]] = {}
        for world in WORLDS:
            rows = []
            for artifact in artifacts[world]:
                event = artifact["event"]
                rows.append({
                    "action": artifact["action"],
                    "composed_reasons": artifact["composed"]["reasons"],
                    "composed_status": artifact["composed"]["status"],
                    "event_id": event.event_id,
                    "external_result": artifact["external_result"],
                    "movement": artifact["movement"],
                    "movement_status": "complete",
                    "order": event.order,
                    "proposed_record": artifact["record"],
                    "relation_role": event.relation_role,
                    "report": artifact["report"],
                    "selected_slot": "first",
                    "source_id": f"source:{event.event_id}",
                })
            occurrences[world] = rows
            current = rows[0]["proposed_record"]
            counter_rows = [
                {**row, "order": index}
                for index, row in enumerate(rows[1:], 1)
            ]
            if type(current) is dict:
                transitions[world] = [
                    predecessor.decide_history(current, counter_rows[:index])
                    for index in range(1, len(counter_rows) + 1)
                ]
            else:
                transitions[world] = [{
                    "active_record": None,
                    "closed_uncorroborated_occurrence_ids": [],
                    "considered_occurrence_ids": [
                        row["event_id"] for row in counter_rows[:index]
                    ],
                    "contradicting_occurrence_ids": [],
                    "governance_state": "current_unavailable",
                    "supporting_current_occurrence_ids": [],
                    "unresolved_occurrence_ids": [],
                } for index in range(1, len(counter_rows) + 1)]
            decisions[world] = transitions[world][-1]

        normalizations = {}
        for case_name in CASES:
            case = LATER_CASES[case_name]
            logical_index += 1
            body = staged.normalizer_body(case.description)
            content, ok, usage = available(recorder.call(logical_index, body))
            scope = staged.parse_scope(content) if ok else None
            normalizations[case_name] = scope
            calls.append({
                "available": ok,
                "case": case_name,
                "content": content,
                "exact": scope == case.scope,
                "expected_scope": case.scope,
                "normalized_scope": scope,
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
                "responsibility": "comparison_scope_normalization",
            })

        def recovered_entry(world: str) -> dict[str, Any] | None:
            acquisition = artifacts[world][0]
            transcript = staged.parse_transcription(acquisition["trans"])
            if (
                acquisition["composed"]["status"] != admission.ADMITTED
                or decisions[world]["governance_state"] != "current_retained"
                or decisions[world]["active_record"] != acquisition["record"]
                or transcript is None
            ):
                return None
            return {
                "scope": transcript["scope"],
                "sentence": acquisition["sentence"],
            }

        def supplied_entry(world: str) -> dict[str, Any]:
            return {
                "scope": VISIBLE_SCOPE,
                "sentence": canonical.render_sentence(record_for_slot(WORLD_SLOTS[world])),
            }

        def material_for(
            world: str, case_name: str, branch: str
        ) -> tuple[str, dict[str, str]]:
            if branch in {COLD, REMOVED}:
                return "", {}
            entry = recovered_entry(world) if branch == RECOVERED else supplied_entry(world)
            selected = (
                entry is not None
                and normalizations[case_name] is not None
                and entry["scope"] == normalizations[case_name]
            )
            return (
                entry["sentence"] if selected else "",
                {"a": branch} if selected else {},
            )

        post_rows = []
        for repeat_index, world, case_name, branch in post_schedule():
            case = LATER_CASES[case_name]
            material, selected_sources = material_for(world, case_name, branch)
            logical_index += 1
            body = revision.participant_body(case.state, case.description, material)
            status, error, content, content_available, usage = recorder.call(
                logical_index, body
            )
            action_availability, action = base.parse_action(content, case.state)
            if status != 200 or error is not None:
                action_availability, action = "unavailable", None
            proposal = ProposalReceipt(
                status == 200 and error is None and content_available,
                (action or content)
                if status == 200 and error is None and content_available else "",
            )
            result = apply_committed_action(
                case.state, case.profiles[world], proposal
            )
            row = {
                "action": action,
                "availability": action_availability,
                "branch": branch,
                "case": case_name,
                "correct_action": (
                    action_availability == "available"
                    and action == oracle_action(case.state, case.profiles[world])
                ),
                "external_result": base.exposed_result(result),
                "provider_usage": usage,
                "repeat": repeat_index,
                "request_sha256": base.sha256(body),
                "responsibility": "comparison_action",
                "retained_material_sha256": base.sha256(material.encode()),
                "selected_sources": selected_sources,
                "world": world,
            }
            post_rows.append(row)
            calls.append(row)

    if logical_index != PLANNED_LOGICAL_CALLS or len(calls) != PLANNED_LOGICAL_CALLS:
        raise MirroredRecoveryRefusal("logical_call_count_mismatch")

    distributions = {
        branch: {
            case_name: {
                "assigned": len(cell := [
                    row for row in post_rows
                    if row["branch"] == branch and row["case"] == case_name
                ]),
                "correct_actions": sum(row["correct_action"] for row in cell),
                "distinct_outcomes": len(Counter(
                    row["action"] or f"<{row['availability']}>" for row in cell
                )),
                "invalid_or_unavailable": sum(
                    row["availability"] != "available" for row in cell
                ),
            }
            for case_name in CASES
        }
        for branch in BRANCHES
    }

    def score(branch: str, worlds: tuple[str, ...], cases: tuple[str, ...]) -> int:
        return sum(
            row["correct_action"] for row in post_rows
            if row["branch"] == branch
            and row["world"] in worlds
            and row["case"] in cases
        )

    matching_scores = {
        branch: score(branch, WORLDS, MATCHING_CASES) for branch in BRANCHES
    }
    unrelated_scores = {
        branch: score(branch, WORLDS, UNRELATED_CASES) for branch in BRANCHES
    }
    world_scores = {
        branch: {
            world: {
                "matching": score(branch, (world,), MATCHING_CASES),
                "up": score(
                    branch, (world,), tuple(c for c in MATCHING_CASES if "_up_" in c)
                ),
                "down": score(
                    branch, (world,), tuple(c for c in MATCHING_CASES if "_down_" in c)
                ),
            }
            for world in WORLDS
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

    exact_records = sum(
        artifact["record"] == artifact["expected_record"]
        for artifact in flat_artifacts
    )
    exact_projections = sum(
        artifact["projection"] == artifact["expected_record"]["first_control_effect"]
        for artifact in flat_artifacts
    )
    composed_admissions = sum(
        artifact["composed"]["status"] == admission.ADMITTED
        for artifact in flat_artifacts
    )
    movements_exact = sum(
        artifact["movement"] == expected_movement(artifact["event"])
        for artifact in flat_artifacts
    )
    exploration_actions_exact = sum(
        artifact["action"] == artifact["event"].state.controls[0]
        for artifact in flat_artifacts
    )
    opposite_current_records = (
        artifacts[FIRST_WORLD][0]["record"]
        == predecessor.opposite_record(artifacts[SECOND_WORLD][0]["record"])
        if type(artifacts[SECOND_WORLD][0]["record"]) is dict else False
    )
    transition_exact = sum(
        tuple(row["governance_state"] for row in transitions[world])
        == ("suspended_pending_corroboration", "current_retained")
        for world in WORLDS
    )
    ordered_sources_exact = sum(
        all(
            decision["considered_occurrence_ids"]
            == [row["event_id"] for row in occurrences[world][1:]][:index]
            for index, decision in enumerate(transitions[world], 1)
        )
        for world in WORLDS
    )
    normal_exact = sum(
        row["exact"] for row in calls
        if row["responsibility"] == "comparison_scope_normalization"
    )
    false_unrelated = sum(
        normalizations[case_name] == VISIBLE_SCOPE for case_name in UNRELATED_CASES
    )
    assignment_exact = sum(
        set(row["selected_sources"])
        == ({"a"} if row["case"] in MATCHING_CASES and row["branch"] in {RECOVERED, SUPPLIED} else set())
        for row in post_rows
    )

    empty_request_identity = 0
    for repeat_index in range(1, REPEATS + 1):
        for case_name in CASES:
            hashes = {
                row["request_sha256"] for row in post_rows
                if row["repeat"] == repeat_index
                and row["case"] == case_name
                and row["branch"] in {COLD, REMOVED}
            }
            empty_request_identity += len(hashes) == 1

    guided_request_identity = 0
    for repeat_index in range(1, REPEATS + 1):
        for world in WORLDS:
            for case_name in CASES:
                hashes = {
                    row["request_sha256"] for row in post_rows
                    if row["repeat"] == repeat_index
                    and row["world"] == world
                    and row["case"] == case_name
                    and row["branch"] in {RECOVERED, SUPPLIED}
                }
                guided_request_identity += len(hashes) == 1

    unrelated_request_identity = 0
    for repeat_index in range(1, REPEATS + 1):
        for case_name in UNRELATED_CASES:
            hashes = {
                row["request_sha256"] for row in post_rows
                if row["repeat"] == repeat_index and row["case"] == case_name
            }
            unrelated_request_identity += len(hashes) == 1

    unrelated_loss = unrelated_scores[COLD] - unrelated_scores[RECOVERED]
    supplied_worlds = world_scores[SUPPLIED]
    engaged = (
        matching_scores[SUPPLIED] >= 43
        and all(
            value["matching"] >= 21
            and value["up"] >= 10
            and value["down"] >= 10
            for value in supplied_worlds.values()
        )
        and not engagement_invalid
    )
    recovered_worlds = world_scores[RECOVERED]
    supported = (
        engaged
        and exploration_actions_exact == SOURCE_OCCURRENCES
        and movements_exact == SOURCE_OCCURRENCES
        and exact_records == SOURCE_OCCURRENCES
        and exact_projections == SOURCE_OCCURRENCES
        and composed_admissions == SOURCE_OCCURRENCES
        and opposite_current_records
        and transition_exact == len(WORLDS)
        and ordered_sources_exact == len(WORLDS)
        and normal_exact >= 10
        and false_unrelated == 0
        and assignment_exact == len(post_rows)
        and empty_request_identity == 36
        and guided_request_identity == 72
        and unrelated_request_identity == 12
        and matching_scores[RECOVERED] >= 43
        and all(
            value["matching"] >= 21
            and value["up"] >= 10
            and value["down"] >= 10
            for value in recovered_worlds.values()
        )
        and matching_scores[RECOVERED] - matching_scores[COLD] >= 16
        and matching_scores[RECOVERED] - matching_scores[REMOVED] >= 16
        and matching_scores[SUPPLIED] - matching_scores[RECOVERED] <= 4
        and unrelated_loss <= 3
    )
    harmful = engaged and unrelated_loss >= 6
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
            "composed_source_admissions": composed_admissions,
            "exact_clerk_records": exact_records,
            "exact_governance_histories": transition_exact,
            "exact_later_assignments": assignment_exact,
            "exact_later_normalizations": normal_exact,
            "exact_ordered_sources": ordered_sources_exact,
            "exact_selected_effect_projections": exact_projections,
            "exploration_actions_exact": exploration_actions_exact,
            "opposite_current_records": opposite_current_records,
            "source_movements_exact": movements_exact,
        },
        "decisions": decisions,
        "engagement_invalid_participant_cells": engagement_invalid,
        "engagement_participant_branches": list(ENGAGEMENT_BRANCHES),
        "formation_verdict": None,
        "invalid_participant_cells": invalid_cells,
        "logical_calls": len(calls),
        "matching_scores": matching_scores,
        "normalized_selection": {
            "exact": normal_exact,
            "false_unrelated": false_unrelated,
            "total": NORMALIZATION_CALLS,
        },
        "occurrences": occurrences,
        "physical_attempts": recorder.physical,
        "predecessor_packet_sha256": PREDECESSOR_PACKET_SHA256,
        "protocol_version": PROTOCOL_VERSION,
        "request_distributions": distributions,
        "request_identity": {
            "cold_removal_mirror_groups": empty_request_identity,
            "recovered_supplied_within_world_pairs": guided_request_identity,
            "unrelated_all_condition_groups": unrelated_request_identity,
        },
        "retries": recorder.retries,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "transitions": transitions,
        "unrelated_loss": unrelated_loss,
        "unrelated_scores": unrelated_scores,
        "validation_verdict": {
            "class": verdict_class,
            "scope": "mirrored_recovery_influence_successor",
        },
        "world_scores": world_scores,
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise MirroredRecoveryRefusal("retained_specimen_mismatch")
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
            raise MirroredRecoveryRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise MirroredRecoveryRefusal("evidence_replay_mismatch")
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
        "mirrored-recovery-influence-successor-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    receipt = learned.collect_provider_receipt()
    if not receipt["valid"]:
        raise MirroredRecoveryRefusal("provider_identity_mismatch")
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
