"""Test learned clerical proposals across accumulated and contested evidence."""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass, replace
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
from contact import learned_clerical_instrument_validation as learned_validation
from contact import learned_clerical_revision_exploration as revision
from contact import observational_counterevidence_comparison as observational
from contact import selective_longer_lineage_revision as longer
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


PROTOCOL_VERSION = "learned-contested-counterevidence-continuation-v1"
SPEC_PATH = (
    Path(__file__).parents[1]
    / "docs"
    / "LEARNED_CONTESTED_COUNTEREVIDENCE_CONTINUATION.md"
)
PARENT_PACKET_SHA256 = longer.PARENT_PACKET_SHA256
PARENT_LINEAGES = longer.PARENT_LINEAGES
LINEAGES = longer.LINEAGES
CASES = learned.CASES

REPEATED = "repeated_contradiction"
SELF_CORRECTING = "self_correcting"
ISOLATED = "isolated_contradiction"
CONTESTED = "contested_movement"
HISTORIES = (REPEATED, SELF_CORRECTING, ISOLATED, CONTESTED)
HISTORY_BY_LINEAGE = dict(zip(LINEAGES, HISTORIES, strict=True))
EVENT_RELATIONS = {
    REPEATED: ("opposite", "opposite"),
    SELF_CORRECTING: ("opposite", "current"),
    ISOLATED: ("opposite",),
    CONTESTED: ("contested",),
}
EXPECTED_TRANSITIONS = {
    REPEATED: ("suspended_pending_corroboration", "superseded"),
    SELF_CORRECTING: ("suspended_pending_corroboration", "current_retained"),
    ISOLATED: ("suspended_pending_corroboration",),
    CONTESTED: ("suspended_unresolved",),
}

COLD = "cold"
RAW = "raw_ordered_history"
GOVERNED = "governed_accumulated_catalog"
LATEST = "latest_complete_proposal_without_accumulation"
REMOVED = "governed_a_removed"
SUPPLIED = "supplied_correct_catalog"
BRANCHES = (COLD, RAW, GOVERNED, LATEST, REMOVED, SUPPLIED)
ENGAGEMENT_BRANCHES = (GOVERNED, SUPPLIED)

REPEATS = 3
SOURCE_OCCURRENCES = 6
CLERK_CALLS = SOURCE_OCCURRENCES * 4
NORMALIZATION_CALLS = len(LINEAGES) * len(CASES)
LATER_CALLS = len(LINEAGES) * len(CASES) * len(BRANCHES) * REPEATS
PLANNED_LOGICAL_CALLS = CLERK_CALLS + NORMALIZATION_CALLS + LATER_CALLS
PHYSICAL_CALL_CEILING = 492
MAX_RETRIES = 12


class LearnedAccumulationRefusal(ValueError):
    pass


@dataclass(frozen=True)
class SourceEvent:
    event_id: str
    order: int
    relation: str
    state: LineageState
    profile: LineageProfile
    movement_status: str


@dataclass(frozen=True)
class AccumulationLineage:
    history_name: str
    source_events: tuple[SourceEvent, ...]
    post_cases: dict[str, revision.Case]


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


def state(label: str, position: int, target: int, profile: LineageProfile) -> LineageState:
    return LineageState(
        profile.controller_family,
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


def claimed_movement(record: dict[str, str], slot: str) -> str | None:
    return {
        learned.INCREASES: "increased",
        learned.DECREASES: "decreased",
    }.get(record.get(f"{slot}_control_effect"))


def opposite_record(current: dict[str, str]) -> dict[str, str]:
    return {
        "first_control_effect": current["second_control_effect"],
        "second_control_effect": current["first_control_effect"],
    }


def decide_history(
    current_record: dict[str, str], history: list[dict[str, Any]]
) -> dict[str, Any]:
    if [row["order"] for row in history] != list(range(1, len(history) + 1)):
        raise LearnedAccumulationRefusal("noncontiguous_occurrence_order")
    opposite = opposite_record(current_record)
    considered = [row["event_id"] for row in history]
    unresolved = [
        row["event_id"] for row in history
        if row["movement_status"] != "complete"
    ]
    eligible = [
        row for row in history
        if row["movement_status"] == "complete"
        and row["movement"] in {"increased", "decreased"}
        and row["composed_status"] == admission.ADMITTED
        and type(row["proposed_record"]) is dict
    ]
    supports_current = [
        row["event_id"] for row in eligible
        if row["proposed_record"] == current_record
        and row["movement"] == claimed_movement(current_record, row["selected_slot"])
    ]
    supports_opposite = [
        row["event_id"] for row in eligible
        if row["proposed_record"] == opposite
        and row["movement"] == claimed_movement(opposite, row["selected_slot"])
        and row["movement"] != claimed_movement(current_record, row["selected_slot"])
    ]
    closed: list[str] = []
    if unresolved:
        governance_state = "suspended_unresolved"
        active_record = None
    elif (
        len(eligible) >= 2
        and eligible[-1]["event_id"] in supports_opposite
        and eligible[-2]["event_id"] in supports_opposite
        and eligible[-1]["proposed_record"] == eligible[-2]["proposed_record"]
    ):
        governance_state = "superseded"
        active_record = opposite
    elif (
        supports_current
        and supports_opposite
        and history[-1]["event_id"] in supports_current
    ):
        governance_state = "current_retained"
        active_record = current_record
        closed = supports_opposite.copy()
    elif supports_opposite:
        governance_state = "suspended_pending_corroboration"
        active_record = None
    else:
        governance_state = "current_retained"
        active_record = current_record
    return {
        "active_record": active_record,
        "closed_uncorroborated_occurrence_ids": closed,
        "considered_occurrence_ids": considered,
        "contradicting_occurrence_ids": supports_opposite,
        "governance_state": governance_state,
        "supporting_current_occurrence_ids": supports_current,
        "unresolved_occurrence_ids": unresolved,
    }


def relation_slot(parent: revision.RevisionLineage, relation: str) -> str:
    if relation == "opposite":
        return parent.old_profiles["a"].increasing_slot
    return parent.counter_profiles["a"].increasing_slot


def make_lineage(name: str, index: int) -> AccumulationLineage:
    parent = PARENT_LINEAGES[name]
    history_name = HISTORY_BY_LINEAGE[name]
    source_events = []
    for order, relation in enumerate(EVENT_RELATIONS[history_name], 1):
        increasing_slot = relation_slot(parent, relation)
        profile = LineageProfile(
            opaque(f"{name}:source:{order}:family"), increasing_slot
        )
        position = 61100 + index * 541 + order * 127
        source_events.append(SourceEvent(
            f"{history_name}:{order}",
            order,
            relation,
            state(
                f"{name}:source:{order}",
                position,
                position + (1 if (index + order) % 2 else -1),
                profile,
            ),
            profile,
            "contested" if relation == "contested" else "complete",
        ))

    post_cases = {}
    for case_index, case_name in enumerate(CASES, 1):
        if case_name.startswith(("a_", "b_")):
            design_position = case_name[0]
            design = parent.designs[design_position]
            scope = {"beacon_class": design.beacon, "housing_class": design.housing}
            if design_position == "a":
                increasing_slot = (
                    parent.old_profiles["a"].increasing_slot
                    if history_name == REPEATED
                    else parent.counter_profiles["a"].increasing_slot
                )
            else:
                increasing_slot = parent.counter_profiles["b"].increasing_slot
        elif case_name == "novel_up":
            design_position = None
            scope = (
                {"beacon_class": "green", "housing_class": "smooth"}
                if index in {1, 4}
                else {"beacon_class": "red", "housing_class": "dimpled"}
            )
            increasing_slot = FIRST_INCREASES if index % 2 else SECOND_INCREASES
        else:
            design_position = None
            scope = {
                "beacon_class": parent.designs["b"].beacon,
                "housing_class": parent.designs["a"].housing,
            }
            increasing_slot = SECOND_INCREASES if index % 2 else FIRST_INCREASES
        profile = LineageProfile(
            opaque(f"{name}:{case_name}:post-family"), increasing_slot
        )
        position = 64100 + index * 547 + case_index * 131
        post_cases[case_name] = revision.Case(
            state(
                f"{name}:{case_name}:post",
                position,
                position + (1 if case_name.endswith("up") else -1),
                profile,
            ),
            profile,
            observational.surface_description(scope),
            scope,
            design_position,
        )
    return AccumulationLineage(history_name, tuple(source_events), post_cases)


LINEAGE_DATA = {
    name: make_lineage(name, index)
    for index, name in enumerate(LINEAGES, 1)
}


def post_schedule() -> tuple[tuple[int, str, str, str], ...]:
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_index, case_name in enumerate(CASES):
            for branch_index in range(len(BRANCHES)):
                branch = BRANCHES[(repeat - 1 + branch_index) % len(BRANCHES)]
                shift = (repeat + case_index + branch_index) % len(LINEAGES)
                order = LINEAGES[shift:] + LINEAGES[:shift]
                rows.extend((repeat, name, case_name, branch) for name in order)
    return tuple(rows)


def expected_event_record(name: str, event: SourceEvent) -> dict[str, str] | None:
    if event.movement_status != "complete":
        return None
    return record_for_slot(event.profile.increasing_slot)


def expected_event_movement(event: SourceEvent) -> str | None:
    if event.movement_status != "complete":
        return None
    return claimed_movement(record_for_slot(event.profile.increasing_slot), "first")


def contested_report(name: str) -> dict[str, str]:
    design = PARENT_LINEAGES[name].designs["a"]
    return {
        "actuator_report": "The first displayed actuator was engaged.",
        "device_report": design.source_description,
        "gauge_report": (
            "Two public gauge readings disagreed. The movement direction is contested."
        ),
    }


def specimen() -> dict[str, Any]:
    _, parent = longer.load_parent()
    return {
        "branches": list(BRANCHES),
        "cases": list(CASES),
        "expected_transitions": {
            name: list(EXPECTED_TRANSITIONS[history])
            for name, history in HISTORY_BY_LINEAGE.items()
        },
        "instrument_model": learned.INSTRUMENT_MODEL,
        "instrument_model_digest": learned.INSTRUMENT_MODEL_DIGEST,
        "lineages": {
            name: {
                "history_name": data.history_name,
                "parent_v2": {
                    position: {
                        key: parent[name][position][key]
                        for key in (
                            "record", "source_report_sha256",
                            "source_transcription_sha256", "version",
                        )
                    }
                    for position in ("a", "b")
                },
                "source_events": [
                    {
                        "event_id": event.event_id,
                        "exploration_action": event.state.controls[0],
                        "movement_status": event.movement_status,
                        "expected_movement": expected_event_movement(event),
                        "public_device": learned.public_device(
                            event.state,
                            PARENT_LINEAGES[name].designs["a"].source_description,
                        ),
                        "relation_role": event.relation,
                    }
                    for event in data.source_events
                ],
                "post_cases": {
                    case_name: {
                        "device": learned.public_device(case.state, case.description),
                        "expected_action": oracle_action(case.state, case.profile),
                        "scope_role": case.design_position,
                    }
                    for case_name, case in data.post_cases.items()
                },
            }
            for name, data in LINEAGE_DATA.items()
        },
        "parent_packet_sha256": PARENT_PACKET_SHA256,
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


def available(result: tuple[Any, ...]) -> tuple[str, bool, Any]:
    status, error, content, content_available, usage = result
    ok = status == 200 and error is None and content_available
    return (content if ok else ""), ok, usage


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    _, parent = longer.load_parent()
    with configured_recorder():
        recorder = validation.verifier.Recorder(transport, evidence_dir)
        if evidence_dir is not None:
            (evidence_dir / "specimen.json").write_bytes(
                base.canonical_json_bytes(specimen())
            )
        logical_index = 0
        calls: list[dict[str, Any]] = []
        artifacts: dict[str, list[dict[str, Any]]] = {name: [] for name in LINEAGES}

        for name in LINEAGES:
            design = PARENT_LINEAGES[name].designs["a"]
            for event in LINEAGE_DATA[name].source_events:
                action = event.state.controls[0]
                if event.movement_status == "contested":
                    report = contested_report(name)
                    external_result = {
                        "application_status": "applied",
                        "movement_direction": None,
                        "movement_status": "contested",
                        "position_after": None,
                        "selected_slot": "first",
                        "target_reached": None,
                    }
                    movement = None
                else:
                    result = apply_committed_action(
                        event.state,
                        event.profile,
                        ProposalReceipt(True, action),
                    )
                    report = learned.sensor_report(design, result)
                    external_result = base.exposed_result(result)
                    movement = result.movement_direction
                artifacts[name].append({
                    "action": action,
                    "composed": None,
                    "event": event,
                    "expected_record": expected_event_record(name, event),
                    "external_result": external_result,
                    "movement": movement,
                    "prose": "",
                    "projection": None,
                    "record": None,
                    "report": report,
                    "sentence": "",
                    "trans": "",
                })

        flat_artifacts = [
            artifact for name in LINEAGES for artifact in artifacts[name]
        ]
        for phase in ("trans", "prose", "parse"):
            for name in LINEAGES:
                design = PARENT_LINEAGES[name].designs["a"]
                for artifact in artifacts[name]:
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
                        expected_transcript = None
                        if event.movement_status == "complete":
                            expected_transcript = {
                                "observed_actuator": "first",
                                "observed_effect": expected_record["first_control_effect"],
                                "scope": {
                                    "beacon_class": design.beacon,
                                    "housing_class": design.housing,
                                },
                            }
                        exact = (
                            parsed == expected_transcript
                            if expected_transcript is not None else None
                        )
                        responsibility = "source_transcription"
                    elif phase == "prose":
                        artifact["prose"] = content
                        exact = (
                            prose_parser.parse_explicit_sentence(content) == expected_record
                            if expected_record is not None else None
                        )
                        responsibility = "source_explicit_prose"
                    else:
                        record = canonical.parse_record(content) if ok else None
                        artifact["record"] = record
                        artifact["sentence"] = canonical.render_sentence(record)
                        exact = (
                            record == expected_record
                            if expected_record is not None else None
                        )
                        responsibility = "source_prose_parse"
                    calls.append({
                        "available": ok,
                        "content": content,
                        "event_id": event.event_id,
                        "exact": exact,
                        "history": HISTORY_BY_LINEAGE[name],
                        "lineage": name,
                        "movement_status": event.movement_status,
                        "provider_usage": usage,
                        "request_sha256": base.sha256(body),
                        "responsibility": responsibility,
                    })

        for name in LINEAGES:
            for artifact in artifacts[name]:
                event = artifact["event"]
                parsed_transcript = staged.parse_transcription(artifact["trans"])
                observed_actuator = (
                    parsed_transcript["observed_actuator"]
                    if parsed_transcript is not None else "unavailable"
                )
                logical_index += 1
                body = validation.projector_body(observed_actuator, artifact["record"])
                content, ok, usage = available(recorder.call(logical_index, body))
                projection_availability, projected = validation.projection.parse_effect(content)
                if not ok:
                    projection_availability, projected = "unavailable", None
                composed = validation.admission_decision(
                    artifact["report"], artifact["trans"], artifact["record"], projected
                )
                artifact["projection"] = projected
                artifact["composed"] = composed
                expected_projection = (
                    artifact["expected_record"]["first_control_effect"]
                    if artifact["expected_record"] is not None else None
                )
                calls.append({
                    "availability": projection_availability,
                    "composed_reasons": composed["reasons"],
                    "composed_status": composed["status"],
                    "content": content,
                    "event_id": event.event_id,
                    "history": HISTORY_BY_LINEAGE[name],
                    "lineage": name,
                    "movement_status": event.movement_status,
                    "projected_effect": projected,
                    "projection_exact": (
                        projected == expected_projection
                        if expected_projection is not None else None
                    ),
                    "provider_usage": usage,
                    "request_sha256": base.sha256(body),
                    "responsibility": "source_selected_effect_projection",
                })

        occurrences: dict[str, list[dict[str, Any]]] = {}
        transitions: dict[str, list[dict[str, Any]]] = {}
        decisions: dict[str, dict[str, Any]] = {}
        for name in LINEAGES:
            current_record = parent[name]["a"]["record"]
            rows = []
            prefixes = []
            for artifact in artifacts[name]:
                event = artifact["event"]
                row = {
                    "action": artifact["action"],
                    "composed_reasons": artifact["composed"]["reasons"],
                    "composed_status": artifact["composed"]["status"],
                    "event_id": event.event_id,
                    "external_result": artifact["external_result"],
                    "movement": artifact["movement"],
                    "movement_status": event.movement_status,
                    "order": event.order,
                    "proposed_record": artifact["record"],
                    "report": artifact["report"],
                    "selected_slot": "first",
                    "source_id": f"source:{event.event_id}",
                }
                rows.append(row)
                prefixes.append(decide_history(current_record, rows.copy()))
            occurrences[name] = rows
            transitions[name] = prefixes
            decisions[name] = prefixes[-1]

        normalizations = {name: {} for name in LINEAGES}
        for name in LINEAGES:
            for case_name in CASES:
                case = LINEAGE_DATA[name].post_cases[case_name]
                logical_index += 1
                body = staged.normalizer_body(case.description)
                content, ok, usage = available(recorder.call(logical_index, body))
                scope = staged.parse_scope(content) if ok else None
                normalizations[name][case_name] = scope
                calls.append({
                    "available": ok,
                    "case": case_name,
                    "content": content,
                    "exact": scope == case.scope,
                    "expected_scope": case.scope,
                    "history": HISTORY_BY_LINEAGE[name],
                    "lineage": name,
                    "normalized_scope": scope,
                    "provider_usage": usage,
                    "request_sha256": base.sha256(body),
                    "responsibility": "comparison_scope_normalization",
                })

        def parent_entry(name: str, position: str) -> dict[str, Any]:
            parsed = staged.parse_transcription(parent[name][position]["transcription"])
            return {
                "scope": parsed["scope"] if parsed is not None else None,
                "sentence": parent[name][position]["sentence"],
                "source": f"parent_{position}_v2",
            }

        def artifact_entry(name: str, artifact: dict[str, Any], label: str) -> dict[str, Any]:
            parsed = staged.parse_transcription(artifact["trans"])
            return {
                "scope": parsed["scope"] if parsed is not None else None,
                "sentence": artifact["sentence"],
                "source": label,
            }

        def latest_admitted(name: str) -> dict[str, Any] | None:
            rows = [
                artifact for artifact in artifacts[name]
                if artifact["composed"]["status"] == admission.ADMITTED
            ]
            return rows[-1] if rows else None

        def governed_a(name: str) -> dict[str, Any] | None:
            decision = decisions[name]
            if decision["governance_state"] == "current_retained":
                return parent_entry(name, "a")
            if decision["governance_state"] == "superseded":
                candidates = [
                    artifact for artifact in artifacts[name]
                    if artifact["composed"]["status"] == admission.ADMITTED
                    and artifact["record"] == decision["active_record"]
                ]
                return (
                    artifact_entry(name, candidates[-1], "governed_a_v3")
                    if candidates else None
                )
            return None

        def supplied_a(name: str) -> dict[str, Any]:
            lineage = LINEAGE_DATA[name]
            case = lineage.post_cases["a_up"]
            return {
                "scope": case.scope,
                "sentence": canonical.render_sentence(
                    record_for_slot(case.profile.increasing_slot)
                ),
                "source": "supplied_correct_a",
            }

        def entries_for(name: str, branch: str) -> list[dict[str, Any]]:
            if branch in {COLD, RAW}:
                return []
            b_entry = parent_entry(name, "b")
            if branch == GOVERNED:
                a_entry = governed_a(name)
            elif branch == LATEST:
                latest = latest_admitted(name)
                a_entry = (
                    artifact_entry(name, latest, f"latest_proposal:{latest['event'].event_id}")
                    if latest is not None else None
                )
            elif branch == REMOVED:
                a_entry = None
            elif branch == SUPPLIED:
                a_entry = supplied_a(name)
                b_entry = {
                    **parent_entry(name, "b"),
                    "source": "supplied_correct_b",
                }
            else:
                raise AssertionError(branch)
            return [entry for entry in (a_entry, b_entry) if entry is not None]

        raw_material = {
            name: base.canonical_json_bytes({
                "raw_ordered_history": [
                    {
                        "event_id": row["event_id"],
                        "external_result": row["external_result"],
                        "order": row["order"],
                        "sensory_report": row["report"],
                    }
                    for row in occurrences[name]
                ]
            }).decode()
            for name in LINEAGES
        }

        def material_for(
            name: str, case_name: str, branch: str
        ) -> tuple[str, dict[str, str]]:
            if branch == COLD:
                return "", {}
            if branch == RAW:
                return raw_material[name], {}
            current_scope = normalizations[name][case_name]
            selected = [
                entry for entry in entries_for(name, branch)
                if current_scope is not None and entry["scope"] == current_scope
            ]
            return (
                "\n".join(entry["sentence"] for entry in selected if entry["sentence"]),
                {entry["source"].split("_")[1] if entry["source"].startswith("parent_") else (
                    "b" if entry["source"].endswith("_b") else "a"
                ): entry["source"] for entry in selected},
            )

        post_rows = []
        for repeat_index, name, case_name, branch in post_schedule():
            case = LINEAGE_DATA[name].post_cases[case_name]
            material, selected_sources = material_for(name, case_name, branch)
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
            result = apply_committed_action(case.state, case.profile, proposal)
            row = {
                "action": action,
                "availability": action_availability,
                "branch": branch,
                "case": case_name,
                "correct_action": (
                    action_availability == "available"
                    and action == oracle_action(case.state, case.profile)
                ),
                "external_result": base.exposed_result(result),
                "history": HISTORY_BY_LINEAGE[name],
                "lineage": name,
                "provider_usage": usage,
                "repeat": repeat_index,
                "request_sha256": base.sha256(body),
                "responsibility": "comparison_action",
                "retained_material_sha256": base.sha256(material.encode()),
                "selected_sources": selected_sources,
            }
            post_rows.append(row)
            calls.append(row)

    if logical_index != PLANNED_LOGICAL_CALLS or len(calls) != PLANNED_LOGICAL_CALLS:
        raise LearnedAccumulationRefusal("logical_call_count_mismatch")

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

    def score(branch: str, names: tuple[str, ...], cases: tuple[str, ...]) -> int:
        return sum(
            row["correct_action"] for row in post_rows
            if row["branch"] == branch
            and row["lineage"] in names
            and row["case"] in cases
        )

    matching_cases = ("a_up", "a_down", "b_up", "b_down")
    a_cases = ("a_up", "a_down")
    b_cases = ("b_up", "b_down")
    unrelated_cases = ("novel_up", "recombined_down")
    matching_scores = {
        branch: score(branch, LINEAGES, matching_cases) for branch in BRANCHES
    }
    unrelated_scores = {
        branch: score(branch, LINEAGES, unrelated_cases) for branch in BRANCHES
    }
    history_scores = {
        branch: {
            HISTORY_BY_LINEAGE[name]: {
                "a": score(branch, (name,), a_cases),
                "b": score(branch, (name,), b_cases),
                "unrelated": score(branch, (name,), unrelated_cases),
            }
            for name in LINEAGES
        }
        for branch in BRANCHES
    }

    invalid_cells = []
    for branch in BRANCHES:
        for name in LINEAGES:
            for case_name in CASES:
                invalid = sum(
                    row["availability"] != "available" for row in post_rows
                    if row["branch"] == branch
                    and row["lineage"] == name
                    and row["case"] == case_name
                )
                if invalid > 1:
                    invalid_cells.append({
                        "branch": branch,
                        "case": case_name,
                        "invalid": invalid,
                        "lineage": name,
                    })
    engagement_invalid = [
        row for row in invalid_cells if row["branch"] in ENGAGEMENT_BRANCHES
    ]

    complete_artifacts = [
        artifact for artifact in flat_artifacts
        if artifact["event"].movement_status == "complete"
    ]
    contested_artifacts = [
        artifact for artifact in flat_artifacts
        if artifact["event"].movement_status == "contested"
    ]
    exact_records = sum(
        artifact["record"] == artifact["expected_record"]
        for artifact in complete_artifacts
    )
    exact_projections = sum(
        artifact["projection"] == artifact["expected_record"]["first_control_effect"]
        for artifact in complete_artifacts
    )
    complete_admissions = sum(
        artifact["composed"]["status"] == admission.ADMITTED
        for artifact in complete_artifacts
    )
    contested_quarantines = sum(
        artifact["composed"]["status"] == admission.QUARANTINED
        for artifact in contested_artifacts
    )
    exploration_actions_exact = sum(
        artifact["action"] == artifact["event"].state.controls[0]
        for artifact in flat_artifacts
    )
    complete_movements_exact = sum(
        artifact["movement"] == expected_event_movement(artifact["event"])
        for artifact in complete_artifacts
    )
    contested_movements_unsettled = sum(
        artifact["movement"] is None for artifact in contested_artifacts
    )
    transition_exact = sum(
        tuple(row["governance_state"] for row in transitions[name])
        == EXPECTED_TRANSITIONS[HISTORY_BY_LINEAGE[name]]
        for name in LINEAGES
    )
    ordered_sources_exact = sum(
        all(
            decision["considered_occurrence_ids"]
            == [row["event_id"] for row in occurrences[name]][:index]
            for index, decision in enumerate(transitions[name], 1)
        )
        for name in LINEAGES
    )
    final_state_exact = sum(
        decisions[name]["governance_state"]
        == EXPECTED_TRANSITIONS[HISTORY_BY_LINEAGE[name]][-1]
        for name in LINEAGES
    )
    normal_exact = sum(
        row["exact"] for row in calls
        if row["responsibility"] == "comparison_scope_normalization"
    )
    false_unrelated = sum(
        normalizations[name][case_name] in (
            LINEAGE_DATA[name].post_cases["a_up"].scope,
            LINEAGE_DATA[name].post_cases["b_up"].scope,
        )
        for name in LINEAGES
        for case_name in unrelated_cases
    )

    def expected_selected_positions(row: dict[str, Any]) -> set[str]:
        position = LINEAGE_DATA[row["lineage"]].post_cases[row["case"]].design_position
        if position is None or row["branch"] in {COLD, RAW}:
            return set()
        if position == "b":
            return {"b"}
        if row["branch"] == SUPPLIED:
            return {"a"}
        if row["branch"] == REMOVED:
            return set()
        if row["branch"] == LATEST:
            return (
                {"a"}
                if HISTORY_BY_LINEAGE[row["lineage"]] != CONTESTED else set()
            )
        return (
            {"a"}
            if decisions[row["lineage"]]["governance_state"]
            in {"superseded", "current_retained"}
            else set()
        )

    assignment_exact = sum(
        set(row["selected_sources"]) == expected_selected_positions(row)
        for row in post_rows
    )
    suspended_without_a = sum(
        "a" not in row["selected_sources"]
        for row in post_rows
        if row["branch"] == GOVERNED
        and row["history"] in {ISOLATED, CONTESTED}
        and row["case"] in a_cases
    )
    unrelated_loss = unrelated_scores[COLD] - unrelated_scores[GOVERNED]

    supplied_per_history = history_scores[SUPPLIED]
    engaged = (
        matching_scores[SUPPLIED] >= 43
        and all(
            row["a"] >= 5 and row["b"] >= 5
            for row in supplied_per_history.values()
        )
        and not engagement_invalid
    )
    repeated_governed = history_scores[GOVERNED][REPEATED]["a"]
    corrected_governed = history_scores[GOVERNED][SELF_CORRECTING]["a"]
    supported = (
        engaged
        and exploration_actions_exact == SOURCE_OCCURRENCES
        and complete_movements_exact == 5
        and contested_movements_unsettled == 1
        and exact_records == 5
        and exact_projections == 5
        and complete_admissions == 5
        and contested_quarantines == 1
        and transition_exact == 4
        and ordered_sources_exact == 4
        and final_state_exact == 4
        and normal_exact >= 20
        and false_unrelated <= 2
        and assignment_exact == len(post_rows)
        and repeated_governed >= 5
        and corrected_governed >= 5
        and repeated_governed - history_scores[REMOVED][REPEATED]["a"] >= 2
        and corrected_governed - history_scores[REMOVED][SELF_CORRECTING]["a"] >= 2
        and sum(
            history_scores[GOVERNED][history]["b"] for history in HISTORIES
        ) >= 21
        and (
            history_scores[GOVERNED][ISOLATED]["a"]
            - history_scores[LATEST][ISOLATED]["a"] >= 2
        )
        and suspended_without_a == 12
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
            "complete_composed_admissions": complete_admissions,
            "complete_movements_exact": complete_movements_exact,
            "contested_movement_unsettled": contested_movements_unsettled,
            "contested_proposal_quarantines": contested_quarantines,
            "exact_complete_records": exact_records,
            "exact_complete_selected_effect_projections": exact_projections,
            "exact_final_governance_states": final_state_exact,
            "exact_intermediate_governance_histories": transition_exact,
            "exact_later_catalog_assignments": assignment_exact,
            "exact_later_normalizations": normal_exact,
            "exact_ordered_source_histories": ordered_sources_exact,
            "exploration_actions_exact": exploration_actions_exact,
            "parent_admitted_version_2_records": 8,
            "suspended_a_deliveries_without_record": suspended_without_a,
        },
        "decisions": decisions,
        "engagement_invalid_participant_cells": engagement_invalid,
        "engagement_participant_branches": list(ENGAGEMENT_BRANCHES),
        "formation_verdict": None,
        "history_scores": history_scores,
        "invalid_participant_cells": invalid_cells,
        "logical_calls": len(calls),
        "matching_scores": matching_scores,
        "normalized_selection": {
            "exact": normal_exact,
            "false_unrelated": false_unrelated,
            "total": NORMALIZATION_CALLS,
        },
        "occurrences": occurrences,
        "parent_packet_sha256": PARENT_PACKET_SHA256,
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "request_distributions": distributions,
        "retries": recorder.retries,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "transitions": transitions,
        "unrelated_loss": unrelated_loss,
        "unrelated_scores": unrelated_scores,
        "validation_verdict": {
            "class": verdict_class,
            "scope": "learned_contested_counterevidence_continuation",
        },
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise LearnedAccumulationRefusal("retained_specimen_mismatch")
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
            raise LearnedAccumulationRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise LearnedAccumulationRefusal("evidence_replay_mismatch")
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
        "learned-contested-counterevidence-continuation-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    receipt = learned.collect_provider_receipt()
    if not receipt["valid"]:
        raise LearnedAccumulationRefusal("provider_identity_mismatch")
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
