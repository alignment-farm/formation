"""Test a restricted second model as a sensory clerk and applicability classifier.

Prospective exploratory note
----------------------------
Question: can a 4B clerical model encode restricted consequence reports and
classify later structural matches well enough to improve a separate 14B
participant's action?
Observation of interest: exact records, correct matching and nonmatching
classifications, improved matching action, and preserved unrelated action.
Models/interface: Qwen3 4B Q4_K_M as clerk and Qwen3 14B Q6_K as participant,
both through the local Docker Model Runner chat-completions endpoint.
Budget: 368 logical calls and at most 376 physical attempts, with no more than
eight transport retries. Valid outputs are never resampled.
Stopping condition: stop after the fixed schedule or either ceiling. Preserve
malformed, unavailable, and harmful outcomes.
Evidence destination: evidence/learned-clerical-instrument-<run-id>/.

This is an instrument exploration. It cannot establish Formation.
"""

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

from contact import distributional_developmental_comparison as base
from contact import staged_chain_validation as prior
from contact import unselected_lineage_behavior_contact as provider
from micro_environment.unselected_lineage_behavior import (
    FIRST_INCREASES,
    SECOND_INCREASES,
    LineageProfile,
    LineageState,
    ProposalReceipt,
    apply_committed_action,
)
from unselected_lineage_specimen import ACTION_RESPONSIBILITY, oracle_action


PROTOCOL_VERSION = "learned-clerical-instrument-exploration-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "LEARNED_CLERICAL_INSTRUMENT_EXPLORATION.md"

INSTRUMENT_MODEL = "huggingface.co/qwen/qwen3-4b-gguf:Q4_K_M"
INSTRUMENT_MODEL_DIGEST = "sha256:618c80458ca4012b132ef1847bcd49ec5f923c3d9df35fdc534715085108e9f3"

LINEAGES = ("lineage_01", "lineage_02")
DESIGN_POSITIONS = ("a", "b")
CASES = ("a_up", "a_down", "b_up", "b_down", "novel_up", "recombined_down")

COLD = "cold"
RAW = "raw_sensor_reports"
ALL_CLERK = "all_clerk_records"
CLERK_PIPELINE = "clerk_selected_clerk_records"
STATIC_CLERK_SELECTED = "clerk_selected_supplied_records"
CLERK_ORACLE_SELECTED = "oracle_selected_clerk_records"
STATIC_ORACLE_SELECTED = "oracle_selected_supplied_records"
BRANCHES = (
    COLD,
    RAW,
    ALL_CLERK,
    CLERK_PIPELINE,
    STATIC_CLERK_SELECTED,
    CLERK_ORACLE_SELECTED,
    STATIC_ORACLE_SELECTED,
)

CLERK_CATALOG = "clerk_records"
STATIC_CATALOG = "supplied_records"
CATALOGS = (CLERK_CATALOG, STATIC_CATALOG)

REPEATS = 4
SOURCE_ACTION_CALLS = len(LINEAGES) * len(DESIGN_POSITIONS)
ENCODING_CALLS = SOURCE_ACTION_CALLS
CLASSIFICATION_CALLS = len(LINEAGES) * len(CASES) * len(CATALOGS)
LATER_CALLS = len(LINEAGES) * len(CASES) * len(BRANCHES) * REPEATS
PLANNED_LOGICAL_CALLS = SOURCE_ACTION_CALLS + ENCODING_CALLS + CLASSIFICATION_CALLS + LATER_CALLS
PHYSICAL_CALL_CEILING = 376
MAX_RETRIES = 8

INCREASES = "increases_position"
DECREASES = "decreases_position"

INSTRUMENT_SETTINGS = {
    "max_tokens": 160,
    "response_format": {"type": "json_object"},
    "stream": False,
    "temperature": 0.2,
    "top_p": 0.9,
}

FEATURE_HELP = """Normalize the visible description with this vocabulary.
housing_class:
- faceted: several flat angled faces
- arched: a smooth curved arch
- ribbed: parallel raised ridges
- tapered: narrows toward the top
- smooth: plain and even
- dimpled: covered in small shallow hollows
beacon_class:
- violet: purple-violet light
- amber: orange-gold light
- cyan: blue-green light
- white: colorless white light
- green: green light
- red: red light"""

ENCODER_SYSTEM = f"""You are a clerical measurement component. You have no memory outside this request.

You receive a restricted sensory report about one device action. You do not receive an action request or a future task.

{FEATURE_HELP}

Exactly one displayed actuator increases position and the other decreases it. Use the observed actuator and gauge movement to record both effects.

Return exactly one JSON object with these keys and no others:
{{"scope":{{"beacon_class":"<value>","housing_class":"<value>"}},"first_displayed_actuator_effect":"<increases_position or decreases_position>","second_displayed_actuator_effect":"<increases_position or decreases_position>"}}
Do not add commentary."""

CLASSIFIER_SYSTEM = f"""You are a clerical applicability classifier. You have no memory outside this request.

You receive a description of one current device and a catalog containing record IDs and scope features only. You never receive controls, position, target, record effects, an action request, or a correct action.

{FEATURE_HELP}

Select a record only when both of its scope features match the current device. A recombination of features from two different records matches neither record.

Return exactly one JSON object with the single key applicable_record_ids. Its value must be a list of zero or more exact IDs from the catalog. Do not add commentary."""

PARTICIPANT_SYSTEM = """You are the action-authoring component of a cold practitioner. You have no memory outside this request.

DOMAIN RULES
Each device has two displayed controls. Exactly one moves position up by one and the other moves position down by one. The action hold leaves position unchanged. Each device uses fresh control strings and a fresh controller-family ID.

Retained instrument records may describe control effects for devices with a matching visible scope. A scope matches only when both housing_class and beacon_class match the current surface description. Do not apply a record with only one matching feature. Raw sensor reports may also be present.

Choose the allowed action that moves the current position toward the target. If position already equals target, choose hold.

OUTPUT INTERFACE
Return exactly one JSON object with the single key action. Its value must be one exact string from allowed_actions. Do not add keys or commentary."""


class InstrumentRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


@dataclass(frozen=True)
class Design:
    housing: str
    beacon: str
    increasing_slot: str
    source_description: str
    later_description: str


@dataclass(frozen=True)
class LaterCase:
    state: LineageState
    profile: LineageProfile
    description: str
    design_position: str | None


@dataclass(frozen=True)
class Lineage:
    name: str
    designs: dict[str, Design]
    acquisitions: dict[str, LineageState]
    acquisition_profiles: dict[str, LineageProfile]
    cases: dict[str, LaterCase]
    record_ids: dict[str, str]


DESIGN_SETS = (
    {
        "a": Design(
            "faceted", "violet", FIRST_INCREASES,
            "The enclosure has several flat, angled faces. Its status lamp shines purple-violet.",
            "A violet indicator sits on a faceted, many-sided case.",
        ),
        "b": Design(
            "arched", "amber", SECOND_INCREASES,
            "The enclosure forms a smooth curved arch. Its status lamp shines orange-gold amber.",
            "An amber indicator sits on a smoothly arched case.",
        ),
    },
    {
        "a": Design(
            "ribbed", "cyan", SECOND_INCREASES,
            "The enclosure has parallel raised ridges. Its status lamp shines blue-green cyan.",
            "A cyan indicator sits on a case with a ribbed surface.",
        ),
        "b": Design(
            "tapered", "white", FIRST_INCREASES,
            "The enclosure narrows toward the top. Its status lamp shines colorless white.",
            "A white indicator sits on a tapered case that narrows upward.",
        ),
    },
)


def make_state(label: str, position: int, target: int, profile: LineageProfile) -> LineageState:
    return LineageState(
        profile.controller_family,
        opaque(f"{label}:device"),
        position,
        target,
        (opaque(f"{label}:first"), opaque(f"{label}:second")),
    )


def make_lineage(name: str, index: int) -> Lineage:
    designs = DESIGN_SETS[index - 1]
    acquisitions: dict[str, LineageState] = {}
    acquisition_profiles: dict[str, LineageProfile] = {}
    record_ids = {position: opaque(f"{name}:{position}:record") for position in DESIGN_POSITIONS}
    for design_index, position_name in enumerate(DESIGN_POSITIONS, 1):
        design = designs[position_name]
        profile = LineageProfile(
            opaque(f"{name}:{position_name}:source-family"), design.increasing_slot
        )
        start = 900 + index * 311 + design_index * 71
        target = start + (1 if (index + design_index) % 2 else -1)
        acquisitions[position_name] = make_state(
            f"{name}:{position_name}:source", start, target, profile
        )
        acquisition_profiles[position_name] = profile

    cases: dict[str, LaterCase] = {}
    for case_index, case in enumerate(CASES, 1):
        if case.startswith("a_"):
            design_position = "a"
            design = designs["a"]
            description = design.later_description
            increasing_slot = design.increasing_slot
        elif case.startswith("b_"):
            design_position = "b"
            design = designs["b"]
            description = design.later_description
            increasing_slot = design.increasing_slot
        elif case == "novel_up":
            design_position = None
            description = (
                "A green indicator sits on a plain, smooth case."
                if index == 1 else
                "A red indicator sits on a dimpled case with shallow hollows."
            )
            increasing_slot = FIRST_INCREASES if index == 1 else SECOND_INCREASES
        else:
            design_position = None
            description = (
                f"An {designs['b'].beacon} indicator sits on a {designs['a'].housing} case."
            )
            increasing_slot = SECOND_INCREASES if index == 1 else FIRST_INCREASES
        profile = LineageProfile(opaque(f"{name}:{case}:fresh-family"), increasing_slot)
        start = 2200 + index * 503 + case_index * 83
        target = start + (1 if case.endswith("up") else -1)
        state = make_state(f"{name}:{case}:later", start, target, profile)
        cases[case] = LaterCase(state, profile, description, design_position)
    return Lineage(
        name, designs, acquisitions, acquisition_profiles, cases, record_ids
    )


LINEAGE_DATA = {
    name: make_lineage(name, index) for index, name in enumerate(LINEAGES, 1)
}


def canonical_envelope(model: str, system: str, user: str, settings: dict[str, Any]) -> bytes:
    return base.canonical_json_bytes({
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "model": model,
        **settings,
    })


def public_device(state: LineageState, description: str) -> dict[str, Any]:
    return {**base.public_device(state), "surface_description": description}


def participant_body(state: LineageState, description: str, retained_material: str) -> bytes:
    record = {
        "device": public_device(state, description),
        "responsibility": ACTION_RESPONSIBILITY,
        "retained_material": retained_material,
    }
    return canonical_envelope(
        base.MODEL,
        PARTICIPANT_SYSTEM,
        f"ACTION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",
        base.ACTION_SETTINGS,
    )


def static_record(design: Design) -> str:
    first = INCREASES if design.increasing_slot == FIRST_INCREASES else DECREASES
    second = DECREASES if first == INCREASES else INCREASES
    return base.canonical_json_bytes({
        "first_displayed_actuator_effect": first,
        "scope": {
            "beacon_class": design.beacon,
            "housing_class": design.housing,
        },
        "second_displayed_actuator_effect": second,
    }).decode()


def sensor_report(design: Design, result: Any) -> dict[str, str]:
    selected = getattr(result, "selected_slot", None)
    movement = getattr(result, "movement_direction", None)
    if selected in {"first", "second"}:
        actuator = f"The {selected} displayed actuator was engaged."
    else:
        actuator = "No displayed actuator engagement was available."
    if movement == "increased":
        gauge = "The position gauge rose by one mark."
    elif movement == "decreased":
        gauge = "The position gauge fell by one mark."
    else:
        gauge = "No gauge movement was available."
    return {
        "actuator_report": actuator,
        "device_report": design.source_description,
        "gauge_report": gauge,
    }


def encoder_body(report: dict[str, str]) -> bytes:
    return canonical_envelope(
        INSTRUMENT_MODEL,
        ENCODER_SYSTEM,
        f"SENSORY REPORT\n{base.canonical_json_bytes(report).decode()}\n/no_think",
        INSTRUMENT_SETTINGS,
    )


def parse_record(content: str) -> dict[str, Any] | None:
    try:
        value = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return None
    if type(value) is not dict or set(value) != {
        "scope", "first_displayed_actuator_effect", "second_displayed_actuator_effect"
    }:
        return None
    scope = value["scope"]
    if type(scope) is not dict or set(scope) != {"beacon_class", "housing_class"}:
        return None
    allowed_housing = {"faceted", "arched", "ribbed", "tapered", "smooth", "dimpled"}
    allowed_beacon = {"violet", "amber", "cyan", "white", "green", "red"}
    if scope["housing_class"] not in allowed_housing or scope["beacon_class"] not in allowed_beacon:
        return None
    effects = {
        value["first_displayed_actuator_effect"],
        value["second_displayed_actuator_effect"],
    }
    if effects != {INCREASES, DECREASES}:
        return None
    return value


def catalog(record_ids: dict[str, str], records: dict[str, str]) -> list[dict[str, Any]]:
    rows = []
    for position in DESIGN_POSITIONS:
        parsed = parse_record(records[position])
        rows.append({
            "record_id": record_ids[position],
            "scope": parsed["scope"] if parsed is not None else None,
        })
    return rows


def classifier_body(description: str, catalog_rows: list[dict[str, Any]]) -> bytes:
    record = {
        "current_device_description": description,
        "record_scope_catalog": catalog_rows,
    }
    return canonical_envelope(
        INSTRUMENT_MODEL,
        CLASSIFIER_SYSTEM,
        f"CLASSIFICATION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",
        INSTRUMENT_SETTINGS,
    )


def parse_selection(content: str, allowed_ids: set[str]) -> tuple[str, list[str]]:
    try:
        value = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return "invalid", []
    if type(value) is not dict or set(value) != {"applicable_record_ids"}:
        return "invalid", []
    selected = value["applicable_record_ids"]
    if (
        type(selected) is not list
        or any(type(item) is not str or item not in allowed_ids for item in selected)
        or len(selected) != len(set(selected))
    ):
        return "invalid", []
    return "available", selected


def record_material(record_ids: dict[str, str], records: dict[str, str], selected: list[str]) -> str:
    by_id = {record_ids[position]: records[position] for position in DESIGN_POSITIONS}
    return base.canonical_json_bytes({
        "instrument_records": [by_id[record_id] for record_id in selected]
    }).decode() if selected else ""


def raw_material(reports: dict[str, dict[str, str]]) -> str:
    return base.canonical_json_bytes({
        "raw_sensor_reports": [reports[position] for position in DESIGN_POSITIONS]
    }).decode()


def expected_selection(lineage: Lineage, case: str) -> list[str]:
    position = lineage.cases[case].design_position
    return [lineage.record_ids[position]] if position is not None else []


def specimen() -> dict[str, Any]:
    return {
        "branches": list(BRANCHES),
        "cases": list(CASES),
        "classification_calls": CLASSIFICATION_CALLS,
        "encoding_calls": ENCODING_CALLS,
        "instrument_model": INSTRUMENT_MODEL,
        "instrument_model_digest": INSTRUMENT_MODEL_DIGEST,
        "later_calls": LATER_CALLS,
        "participant_model": base.MODEL,
        "participant_model_digest": base.MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "source_action_calls": SOURCE_ACTION_CALLS,
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "lineages": {
            name: {
                "sources": {
                    position: {
                        "device": public_device(
                            lineage.acquisitions[position],
                            lineage.designs[position].source_description,
                        ),
                        "expected_record_sha256": base.sha256(
                            static_record(lineage.designs[position]).encode()
                        ),
                        "record_id": lineage.record_ids[position],
                    }
                    for position in DESIGN_POSITIONS
                },
                "later_cases": {
                    case: {
                        "device": public_device(later.state, later.description),
                        "expected_action": oracle_action(later.state, later.profile),
                        "expected_record_ids": expected_selection(lineage, case),
                    }
                    for case, later in lineage.cases.items()
                },
            }
            for name, lineage in LINEAGE_DATA.items()
        },
    }


def classification_schedule() -> tuple[tuple[str, str, str], ...]:
    rows = []
    for case_index, case in enumerate(CASES):
        for catalog_index in range(len(CATALOGS)):
            catalog_name = CATALOGS[(case_index + catalog_index) % len(CATALOGS)]
            shift = (case_index + catalog_index) % len(LINEAGES)
            order = LINEAGES[shift:] + LINEAGES[:shift]
            rows.extend((name, case, catalog_name) for name in order)
    return tuple(rows)


def later_schedule() -> tuple[tuple[int, str, str, str], ...]:
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_index, case in enumerate(CASES):
            for branch_index in range(len(BRANCHES)):
                branch = BRANCHES[(repeat - 1 + branch_index) % len(BRANCHES)]
                shift = (repeat + case_index + branch_index) % len(LINEAGES)
                order = LINEAGES[shift:] + LINEAGES[:shift]
                rows.extend((repeat, name, case, branch) for name in order)
    return tuple(rows)


@contextmanager
def configured_recorder():
    old_ceiling = prior.PHYSICAL_CALL_CEILING
    old_retries = prior.MAX_RETRIES
    try:
        prior.PHYSICAL_CALL_CEILING = PHYSICAL_CALL_CEILING
        prior.MAX_RETRIES = MAX_RETRIES
        yield
    finally:
        prior.PHYSICAL_CALL_CEILING = old_ceiling
        prior.MAX_RETRIES = old_retries


Transport = Callable[[bytes], tuple[int, bytes]]


def available_content(call_result: tuple[Any, ...]) -> tuple[str, bool, Any]:
    status, error, content, content_available, usage = call_result
    available = status == 200 and error is None and content_available
    return (content if available else ""), available, usage


def participant_call(
    recorder: prior.Recorder,
    logical_index: int,
    later: LaterCase,
    material: str,
) -> tuple[bytes, str, str | None, Any, Any]:
    body = participant_body(later.state, later.description, material)
    status, error, content, content_available, usage = recorder.call(logical_index, body)
    availability, action = base.parse_action(content, later.state)
    if status != 200 or error is not None:
        availability, action = "unavailable", None
    provider_available = status == 200 and error is None and content_available
    proposal = ProposalReceipt(
        provider_available, (action or content) if provider_available else ""
    )
    result = apply_committed_action(later.state, later.profile, proposal)
    return body, availability, action, result, usage


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    with configured_recorder():
        recorder = prior.Recorder(transport, evidence_dir)
        if evidence_dir is not None:
            (evidence_dir / "specimen.json").write_bytes(
                base.canonical_json_bytes(specimen())
            )
        calls: list[dict[str, Any]] = []
        artifacts: dict[str, dict[str, Any]] = {}
        logical_index = 0

        for name in LINEAGES:
            lineage = LINEAGE_DATA[name]
            artifacts[name] = {"reports": {}, "clerk_records": {}, "static_records": {}}
            for position in DESIGN_POSITIONS:
                state = lineage.acquisitions[position]
                profile = lineage.acquisition_profiles[position]
                description = lineage.designs[position].source_description
                logical_index += 1
                body = participant_body(state, description, "")
                status, error, content, content_available, usage = recorder.call(
                    logical_index, body
                )
                availability, action = base.parse_action(content, state)
                if status != 200 or error is not None:
                    availability, action = "unavailable", None
                provider_available = status == 200 and error is None and content_available
                proposal = ProposalReceipt(
                    provider_available, (action or content) if provider_available else ""
                )
                result = apply_committed_action(state, profile, proposal)
                report = sensor_report(lineage.designs[position], result)
                artifacts[name]["reports"][position] = report
                artifacts[name]["static_records"][position] = static_record(
                    lineage.designs[position]
                )
                calls.append({
                    "responsibility": "source_action",
                    "lineage": name,
                    "design_position": position,
                    "action": action,
                    "availability": availability,
                    "external_result": base.exposed_result(result),
                    "provider_usage": usage,
                    "request_sha256": base.sha256(body),
                })

        for name in LINEAGES:
            lineage = LINEAGE_DATA[name]
            for position in DESIGN_POSITIONS:
                report = artifacts[name]["reports"][position]
                logical_index += 1
                body = encoder_body(report)
                content, available, usage = available_content(
                    recorder.call(logical_index, body)
                )
                parsed = parse_record(content) if available else None
                exact = content == artifacts[name]["static_records"][position]
                artifacts[name]["clerk_records"][position] = content
                calls.append({
                    "responsibility": "clerical_encoding",
                    "lineage": name,
                    "design_position": position,
                    "available": available,
                    "valid": parsed is not None,
                    "exact": exact,
                    "content": content,
                    "provider_usage": usage,
                    "request_sha256": base.sha256(body),
                    "sensory_report_sha256": base.sha256(
                        base.canonical_json_bytes(report)
                    ),
                })

        selections: dict[str, dict[str, dict[str, list[str]]]] = {
            name: {catalog_name: {} for catalog_name in CATALOGS}
            for name in LINEAGES
        }
        for name, case, catalog_name in classification_schedule():
            lineage = LINEAGE_DATA[name]
            records = (
                artifacts[name]["clerk_records"]
                if catalog_name == CLERK_CATALOG
                else artifacts[name]["static_records"]
            )
            rows = catalog(lineage.record_ids, records)
            logical_index += 1
            body = classifier_body(lineage.cases[case].description, rows)
            content, available, usage = available_content(
                recorder.call(logical_index, body)
            )
            availability, selected = parse_selection(
                content, set(lineage.record_ids.values())
            )
            if not available:
                availability, selected = "unavailable", []
            expected = expected_selection(lineage, case)
            selections[name][catalog_name][case] = selected
            calls.append({
                "responsibility": "clerical_classification",
                "lineage": name,
                "case": case,
                "catalog": catalog_name,
                "availability": availability,
                "selected_record_ids": selected,
                "expected_record_ids": expected,
                "exact": availability == "available" and selected == expected,
                "false_selection": not expected and bool(selected),
                "content": content,
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
            })

        later_rows: list[dict[str, Any]] = []
        for repeat, name, case, branch in later_schedule():
            lineage = LINEAGE_DATA[name]
            later = lineage.cases[case]
            clerk_records = artifacts[name]["clerk_records"]
            static_records = artifacts[name]["static_records"]
            if branch == COLD:
                material = ""
            elif branch == RAW:
                material = raw_material(artifacts[name]["reports"])
            elif branch == ALL_CLERK:
                material = record_material(
                    lineage.record_ids,
                    clerk_records,
                    [lineage.record_ids[position] for position in DESIGN_POSITIONS],
                )
            elif branch == CLERK_PIPELINE:
                material = record_material(
                    lineage.record_ids,
                    clerk_records,
                    selections[name][CLERK_CATALOG][case],
                )
            elif branch == STATIC_CLERK_SELECTED:
                material = record_material(
                    lineage.record_ids,
                    static_records,
                    selections[name][STATIC_CATALOG][case],
                )
            elif branch == CLERK_ORACLE_SELECTED:
                material = record_material(
                    lineage.record_ids,
                    clerk_records,
                    expected_selection(lineage, case),
                )
            elif branch == STATIC_ORACLE_SELECTED:
                material = record_material(
                    lineage.record_ids,
                    static_records,
                    expected_selection(lineage, case),
                )
            else:  # pragma: no cover
                raise AssertionError(branch)
            logical_index += 1
            body, availability, action, result, usage = participant_call(
                recorder, logical_index, later, material
            )
            row = {
                "responsibility": "later_action",
                "lineage": name,
                "case": case,
                "branch": branch,
                "repeat": repeat,
                "action": action,
                "availability": availability,
                "correct_action": (
                    availability == "available"
                    and action == oracle_action(later.state, later.profile)
                ),
                "external_result": base.exposed_result(result),
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
                "retained_material_sha256": base.sha256(material.encode()),
            }
            later_rows.append(row)
            calls.append(row)

    if logical_index != PLANNED_LOGICAL_CALLS:
        raise InstrumentRefusal("logical_call_count_mismatch")

    distributions = {
        branch: {
            case: {
                "assigned": len(cell := [
                    row for row in later_rows
                    if row["branch"] == branch and row["case"] == case
                ]),
                "correct_actions": sum(row["correct_action"] for row in cell),
                "invalid_or_unavailable": sum(
                    row["availability"] != "available" for row in cell
                ),
                "distinct_outcomes": len(Counter(
                    row["action"] or f"<{row['availability']}>" for row in cell
                )),
            }
            for case in CASES
        }
        for branch in BRANCHES
    }

    matching_cases = ("a_up", "a_down", "b_up", "b_down")
    unrelated_cases = ("novel_up", "recombined_down")

    def total(branch: str, cases: tuple[str, ...]) -> int:
        return sum(distributions[branch][case]["correct_actions"] for case in cases)

    matching_scores = {branch: total(branch, matching_cases) for branch in BRANCHES}
    unrelated_scores = {branch: total(branch, unrelated_cases) for branch in BRANCHES}
    design_scores = {
        branch: {
            "a": total(branch, ("a_up", "a_down")),
            "b": total(branch, ("b_up", "b_down")),
        }
        for branch in BRANCHES
    }
    direction_scores = {
        branch: {
            "up": total(branch, ("a_up", "b_up")),
            "down": total(branch, ("a_down", "b_down")),
        }
        for branch in BRANCHES
    }
    classification_rows = [
        row for row in calls if row["responsibility"] == "clerical_classification"
    ]
    classification_scores = {
        catalog_name: {
            "exact": sum(
                row["exact"] for row in classification_rows
                if row["catalog"] == catalog_name
            ),
            "false_selections": sum(
                row["false_selection"] for row in classification_rows
                if row["catalog"] == catalog_name
            ),
            "total": len([
                row for row in classification_rows if row["catalog"] == catalog_name
            ]),
        }
        for catalog_name in CATALOGS
    }
    exact_records = sum(
        row["exact"] for row in calls if row["responsibility"] == "clerical_encoding"
    )
    valid_records = sum(
        row["valid"] for row in calls if row["responsibility"] == "clerical_encoding"
    )
    every_cell_valid = all(
        distributions[branch][case]["invalid_or_unavailable"] <= 1
        for branch in BRANCHES for case in CASES
    )
    engaged = (
        matching_scores[STATIC_ORACLE_SELECTED] >= 29
        and all(score >= 14 for score in design_scores[STATIC_ORACLE_SELECTED].values())
        and all(score >= 14 for score in direction_scores[STATIC_ORACLE_SELECTED].values())
        and every_cell_valid
    )
    encoding_found = (
        exact_records >= 3
        and matching_scores[CLERK_ORACLE_SELECTED] >= 27
    )
    classification_found = (
        classification_scores[STATIC_CATALOG]["exact"] >= 10
        and classification_scores[STATIC_CATALOG]["false_selections"] <= 1
        and matching_scores[STATIC_CLERK_SELECTED] >= 27
    )
    unrelated_loss = unrelated_scores[COLD] - unrelated_scores[CLERK_PIPELINE]
    pipeline_candidate = (
        encoding_found
        and classification_found
        and classification_scores[CLERK_CATALOG]["exact"] >= 10
        and classification_scores[CLERK_CATALOG]["false_selections"] <= 1
        and matching_scores[CLERK_PIPELINE] >= 27
        and matching_scores[CLERK_PIPELINE] - matching_scores[COLD] >= 8
        and matching_scores[CLERK_PIPELINE] - matching_scores[RAW] >= 4
        and matching_scores[CLERK_PIPELINE] - matching_scores[ALL_CLERK] >= 4
        and matching_scores[STATIC_ORACLE_SELECTED] - matching_scores[CLERK_PIPELINE] <= 4
        and unrelated_loss <= 2
    )
    harmful = engaged and unrelated_loss >= 4
    if not engaged:
        verdict_class = "not_engaged"
    elif harmful:
        verdict_class = "harmful"
    elif pipeline_candidate:
        verdict_class = "pipeline_candidate"
    elif encoding_found and not classification_found:
        verdict_class = "encoding_only"
    elif classification_found and not encoding_found:
        verdict_class = "classification_only"
    else:
        verdict_class = "null"

    packet = {
        "attempts": recorder.attempts,
        "calls": calls,
        "classification_scores": classification_scores,
        "design_scores": design_scores,
        "direction_scores": direction_scores,
        "encoding": {
            "exact_records": exact_records,
            "total_records": ENCODING_CALLS,
            "valid_records": valid_records,
        },
        "every_participant_cell_valid": every_cell_valid,
        "formation_verdict": None,
        "instrument_verdict": {
            "class": verdict_class,
            "scope": "learned_clerical_instrument_exploration",
        },
        "logical_calls": len(calls),
        "matching_scores": matching_scores,
        "models": {
            "clerical": {
                "model": INSTRUMENT_MODEL,
                "digest": INSTRUMENT_MODEL_DIGEST,
            },
            "participant": {"model": base.MODEL, "digest": base.MODEL_DIGEST},
        },
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "request_distributions": distributions,
        "retries": recorder.retries,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "unrelated_loss": unrelated_loss,
        "unrelated_scores": unrelated_scores,
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise InstrumentRefusal("retained_specimen_mismatch")
    retained = json.loads((evidence_dir / "packet.json").read_bytes())
    entries = []
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        meta = json.loads(meta_path.read_text())
        request = (evidence_dir / "attempts" / f"{stem}.request.json").read_bytes()
        response = (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes()
        if (
            base.sha256(request) != meta["request_sha256"]
            or base.sha256(response) != meta["response_sha256"]
        ):
            raise InstrumentRefusal("retained_attempt_hash_mismatch")
        entries.append((request, response, meta))
    position = 0

    def transport(body: bytes) -> tuple[int, bytes]:
        nonlocal position
        if position >= len(entries):
            raise InstrumentRefusal("missing_retained_attempt")
        request, response, meta = entries[position]
        position += 1
        if request != body:
            raise InstrumentRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise InstrumentRefusal("evidence_replay_mismatch")
    return replayed


def collect_provider_receipt(
    command_runner: provider.CommandRunner = provider.shell_command,
    endpoint_reader: provider.EndpointReader = provider.endpoint_receipt,
) -> dict[str, Any]:
    receipt = base.collect_provider_receipt(
        command_runner=command_runner, endpoint_reader=endpoint_reader
    )
    inspection_receipt = command_runner(
        ("docker", "model", "inspect", INSTRUMENT_MODEL)
    )
    reasons = list(receipt.get("refusals", []))
    inspection = None
    if inspection_receipt.get("returncode") != 0:
        reasons.append("instrument_model_inspect_failed")
    else:
        try:
            inspection = json.loads(inspection_receipt["stdout"])
            if (
                inspection.get("id") != INSTRUMENT_MODEL_DIGEST
                or INSTRUMENT_MODEL not in inspection.get("tags", [])
                or inspection.get("config", {}).get("architecture") != "qwen3"
            ):
                reasons.append("instrument_model_identity_mismatch")
        except (json.JSONDecodeError, KeyError, TypeError):
            reasons.append("instrument_model_inspect_invalid")
    try:
        endpoint_models = {
            row["id"] for row in json.loads(receipt["endpoint"]["body"])["data"]
        }
        if INSTRUMENT_MODEL not in endpoint_models:
            reasons.append("instrument_model_endpoint_missing")
    except (json.JSONDecodeError, KeyError, TypeError):
        reasons.append("instrument_endpoint_invalid")
    return {
        **receipt,
        "valid": not reasons,
        "refusals": reasons,
        "instrument_model_inspect_command": inspection_receipt,
        "instrument_model_inspection": inspection,
    }


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
        args.evidence_dir = Path("evidence") / f"learned-clerical-instrument-{run_id}"
    started = time.monotonic()
    receipt = collect_provider_receipt()
    if not receipt["valid"]:
        raise InstrumentRefusal("provider_identity_mismatch")
    packet = execute(base.live_transport, args.evidence_dir)
    (args.evidence_dir / "provider.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    replay_evidence(args.evidence_dir)
    print(json.dumps({
        "elapsed_seconds": time.monotonic() - started,
        "evidence_dir": str(args.evidence_dir),
        "instrument_verdict": packet["instrument_verdict"],
        "logical_calls": packet["logical_calls"],
        "physical_attempts": packet["physical_attempts"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
