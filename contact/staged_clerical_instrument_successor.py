"""Run the staged successor for restricted learned clerical instrumentation."""

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
from contact import learned_clerical_instrument_exploration as learned
from contact import staged_chain_validation as prior
from contact import structural_record_delivery_calibration as calibration
from micro_environment.unselected_lineage_behavior import (
    FIRST_INCREASES,
    SECOND_INCREASES,
    LineageProfile,
    LineageState,
    ProposalReceipt,
    apply_committed_action,
)
from unselected_lineage_specimen import ACTION_RESPONSIBILITY, oracle_action


PROTOCOL_VERSION = "staged-clerical-instrument-successor-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "STAGED_CLERICAL_INSTRUMENT_SUCCESSOR.md"

LINEAGES = learned.LINEAGES
DESIGN_POSITIONS = learned.DESIGN_POSITIONS
CASES = learned.CASES

COLD = "cold"
RAW = "raw_sensor_reports"
ALL_SENTENCES = "all_clerk_sentences"
DIRECT_SELECTOR = "direct_selector_clerk_sentence"
NORMALIZED_PIPELINE = "normalized_scope_clerk_sentence"
NORMALIZED_STATIC = "normalized_scope_supplied_sentence"
ORACLE_CLERK = "oracle_selected_clerk_sentence"
ORACLE_STATIC = "oracle_selected_supplied_sentence"
BRANCHES = (
    COLD,
    RAW,
    ALL_SENTENCES,
    DIRECT_SELECTOR,
    NORMALIZED_PIPELINE,
    NORMALIZED_STATIC,
    ORACLE_CLERK,
    ORACLE_STATIC,
)

REPEATS = 4
SOURCE_ACTION_CALLS = len(LINEAGES) * len(DESIGN_POSITIONS)
TRANSCRIPTION_CALLS = SOURCE_ACTION_CALLS
SENTENCE_CALLS = SOURCE_ACTION_CALLS
NORMALIZATION_CALLS = len(LINEAGES) * len(CASES)
DIRECT_SELECTOR_CALLS = NORMALIZATION_CALLS
LATER_CALLS = len(LINEAGES) * len(CASES) * len(BRANCHES) * REPEATS
PLANNED_LOGICAL_CALLS = (
    SOURCE_ACTION_CALLS
    + TRANSCRIPTION_CALLS
    + SENTENCE_CALLS
    + NORMALIZATION_CALLS
    + DIRECT_SELECTOR_CALLS
    + LATER_CALLS
)
PHYSICAL_CALL_CEILING = 428
MAX_RETRIES = 8

CLERK_JSON_SETTINGS = learned.INSTRUMENT_SETTINGS
CLERK_TEXT_SETTINGS = {
    "max_tokens": 96,
    "stream": False,
    "temperature": 0.2,
    "top_p": 0.9,
}

TRANSCRIPTION_SYSTEM = f"""You are a clerical sensory transcriber. You have no memory outside this request.

You receive a restricted sensory report about one device action. You do not receive an action request or a future task.

{learned.FEATURE_HELP}

Normalize the two visible features. Copy which displayed actuator was engaged. A gauge that rose has the observed effect increases_position. A gauge that fell has the observed effect decreases_position.

Return exactly one JSON object with these keys and no others:
{{"observed_actuator":"<first or second>","observed_effect":"<increases_position or decreases_position>","scope":{{"beacon_class":"<value>","housing_class":"<value>"}}}}
Do not infer the unobserved actuator. Do not add commentary."""

SENTENCE_SYSTEM = """You are a clerical record writer. You have no memory outside this request.

You receive one normalized sensory transcript. Exactly one displayed control increases position and the other decreases it. Write both effects from the observed actuator and observed effect.

Return exactly two sentences in this form and add nothing else:
The first displayed control <increases or decreases> position. The second displayed control <decreases or increases> position."""

NORMALIZER_SYSTEM = f"""You are a clerical device-description normalizer. You have no memory outside this request.

{learned.FEATURE_HELP}

Return exactly one JSON object with the single key scope. Its value must contain beacon_class and housing_class. Do not add commentary."""


class SuccessorRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


@dataclass(frozen=True)
class LaterCase:
    state: LineageState
    profile: LineageProfile
    description: str
    scope: dict[str, str]
    design_position: str | None


@dataclass(frozen=True)
class Lineage:
    name: str
    designs: dict[str, learned.Design]
    acquisitions: dict[str, LineageState]
    acquisition_profiles: dict[str, LineageProfile]
    cases: dict[str, LaterCase]
    record_ids: dict[str, str]


def make_state(label: str, position: int, target: int, profile: LineageProfile) -> LineageState:
    return LineageState(
        profile.controller_family,
        opaque(f"{label}:device"),
        position,
        target,
        (opaque(f"{label}:first"), opaque(f"{label}:second")),
    )


def make_lineage(name: str, index: int) -> Lineage:
    designs = learned.DESIGN_SETS[index - 1]
    acquisitions = {}
    acquisition_profiles = {}
    record_ids = {
        position: opaque(f"{name}:{position}:record") for position in DESIGN_POSITIONS
    }
    for design_index, position_name in enumerate(DESIGN_POSITIONS, 1):
        design = designs[position_name]
        profile = LineageProfile(
            opaque(f"{name}:{position_name}:source-family"), design.increasing_slot
        )
        position = 8100 + index * 313 + design_index * 79
        target = position + (1 if (index + design_index) % 2 else -1)
        acquisitions[position_name] = make_state(
            f"{name}:{position_name}:source", position, target, profile
        )
        acquisition_profiles[position_name] = profile

    cases = {}
    for case_index, case_name in enumerate(CASES, 1):
        if case_name.startswith("a_"):
            design_position = "a"
            design = designs["a"]
            description = design.later_description
            scope = {"beacon_class": design.beacon, "housing_class": design.housing}
            increasing_slot = design.increasing_slot
        elif case_name.startswith("b_"):
            design_position = "b"
            design = designs["b"]
            description = design.later_description
            scope = {"beacon_class": design.beacon, "housing_class": design.housing}
            increasing_slot = design.increasing_slot
        elif case_name == "novel_up":
            design_position = None
            if index == 1:
                description = "A green indicator sits on a plain, smooth case."
                scope = {"beacon_class": "green", "housing_class": "smooth"}
                increasing_slot = FIRST_INCREASES
            else:
                description = "A red indicator sits on a dimpled case with shallow hollows."
                scope = {"beacon_class": "red", "housing_class": "dimpled"}
                increasing_slot = SECOND_INCREASES
        else:
            design_position = None
            description = (
                f"An {designs['b'].beacon} indicator sits on a {designs['a'].housing} case."
            )
            scope = {
                "beacon_class": designs["b"].beacon,
                "housing_class": designs["a"].housing,
            }
            increasing_slot = SECOND_INCREASES if index == 1 else FIRST_INCREASES
        profile = LineageProfile(
            opaque(f"{name}:{case_name}:fresh-family"), increasing_slot
        )
        position = 10300 + index * 509 + case_index * 101
        target = position + (1 if case_name.endswith("up") else -1)
        state = make_state(f"{name}:{case_name}:later", position, target, profile)
        cases[case_name] = LaterCase(
            state, profile, description, scope, design_position
        )
    return Lineage(
        name, designs, acquisitions, acquisition_profiles, cases, record_ids
    )


LINEAGE_DATA = {
    name: make_lineage(name, index) for index, name in enumerate(LINEAGES, 1)
}


def participant_body(state: LineageState, description: str, material: str) -> bytes:
    record = {
        "device": learned.public_device(state, description),
        "responsibility": ACTION_RESPONSIBILITY,
        "retained_material": material,
    }
    return learned.canonical_envelope(
        base.MODEL,
        calibration.PARTICIPANT_SYSTEM,
        f"ACTION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",
        base.ACTION_SETTINGS,
    )


def transcription_body(report: dict[str, str]) -> bytes:
    return learned.canonical_envelope(
        learned.INSTRUMENT_MODEL,
        TRANSCRIPTION_SYSTEM,
        f"SENSORY REPORT\n{base.canonical_json_bytes(report).decode()}\n/no_think",
        CLERK_JSON_SETTINGS,
    )


def parse_transcription(content: str) -> dict[str, Any] | None:
    try:
        value = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return None
    if type(value) is not dict or set(value) != {
        "observed_actuator", "observed_effect", "scope"
    }:
        return None
    if value["observed_actuator"] not in {"first", "second"}:
        return None
    if value["observed_effect"] not in {learned.INCREASES, learned.DECREASES}:
        return None
    scope = learned.parse_record(base.canonical_json_bytes({
        "first_displayed_actuator_effect": learned.INCREASES,
        "scope": value["scope"],
        "second_displayed_actuator_effect": learned.DECREASES,
    }).decode())
    return value if scope is not None else None


def expected_transcription(design: learned.Design, result: Any) -> dict[str, Any] | None:
    selected = getattr(result, "selected_slot", None)
    movement = getattr(result, "movement_direction", None)
    if selected not in {"first", "second"} or movement not in {"increased", "decreased"}:
        return None
    return {
        "observed_actuator": selected,
        "observed_effect": (
            learned.INCREASES if movement == "increased" else learned.DECREASES
        ),
        "scope": {
            "beacon_class": design.beacon,
            "housing_class": design.housing,
        },
    }


def sentence_body(transcription: str) -> bytes:
    record = {"normalized_sensory_transcript": transcription}
    return learned.canonical_envelope(
        learned.INSTRUMENT_MODEL,
        SENTENCE_SYSTEM,
        f"RECORD REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",
        CLERK_TEXT_SETTINGS,
    )


def expected_sentence(design: learned.Design) -> str:
    first = "increases" if design.increasing_slot == FIRST_INCREASES else "decreases"
    second = "decreases" if first == "increases" else "increases"
    return (
        f"The first displayed control {first} position. "
        f"The second displayed control {second} position."
    )


def normalizer_body(description: str) -> bytes:
    record = {"current_device_description": description}
    return learned.canonical_envelope(
        learned.INSTRUMENT_MODEL,
        NORMALIZER_SYSTEM,
        f"NORMALIZATION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",
        CLERK_JSON_SETTINGS,
    )


def parse_scope(content: str) -> dict[str, str] | None:
    try:
        value = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return None
    if type(value) is not dict or set(value) != {"scope"}:
        return None
    synthetic = base.canonical_json_bytes({
        "first_displayed_actuator_effect": learned.INCREASES,
        "scope": value["scope"],
        "second_displayed_actuator_effect": learned.DECREASES,
    }).decode()
    return value["scope"] if learned.parse_record(synthetic) is not None else None


def source_scope(transcription: str) -> dict[str, str] | None:
    parsed = parse_transcription(transcription)
    return parsed["scope"] if parsed is not None else None


def catalog_rows(lineage: Lineage, transcriptions: dict[str, str]) -> list[dict[str, Any]]:
    return [
        {
            "record_id": lineage.record_ids[position],
            "scope": source_scope(transcriptions[position]),
        }
        for position in DESIGN_POSITIONS
    ]


def exact_match_ids(
    lineage: Lineage,
    current_scope: dict[str, str] | None,
    source_scopes: dict[str, dict[str, str] | None],
) -> list[str]:
    if current_scope is None:
        return []
    return [
        lineage.record_ids[position]
        for position in DESIGN_POSITIONS
        if source_scopes[position] is not None
        and source_scopes[position] == current_scope
    ]


def expected_selection(lineage: Lineage, case_name: str) -> list[str]:
    position = lineage.cases[case_name].design_position
    return [lineage.record_ids[position]] if position is not None else []


def selected_sentence(
    lineage: Lineage,
    sentences: dict[str, str],
    selected_ids: list[str],
) -> str:
    by_id = {
        lineage.record_ids[position]: sentences[position]
        for position in DESIGN_POSITIONS
    }
    if len(selected_ids) == 1:
        return by_id[selected_ids[0]]
    if not selected_ids:
        return ""
    return "\n".join(by_id[record_id] for record_id in selected_ids)


def all_sentence_material(sentences: dict[str, str]) -> str:
    return "\n".join(
        f"RETAINED GUIDANCE {index}: {sentences[position]}"
        for index, position in enumerate(DESIGN_POSITIONS, 1)
    )


def raw_material(reports: dict[str, dict[str, str]]) -> str:
    return base.canonical_json_bytes({
        "raw_sensor_reports": [reports[position] for position in DESIGN_POSITIONS]
    }).decode()


def specimen() -> dict[str, Any]:
    return {
        "branches": list(BRANCHES),
        "cases": list(CASES),
        "direct_selector_calls": DIRECT_SELECTOR_CALLS,
        "instrument_model": learned.INSTRUMENT_MODEL,
        "instrument_model_digest": learned.INSTRUMENT_MODEL_DIGEST,
        "later_calls": LATER_CALLS,
        "normalization_calls": NORMALIZATION_CALLS,
        "participant_model": base.MODEL,
        "participant_model_digest": base.MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "sentence_calls": SENTENCE_CALLS,
        "source_action_calls": SOURCE_ACTION_CALLS,
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "transcription_calls": TRANSCRIPTION_CALLS,
        "lineages": {
            name: {
                "sources": {
                    position: {
                        "device": learned.public_device(
                            lineage.acquisitions[position],
                            lineage.designs[position].source_description,
                        ),
                        "expected_sentence_sha256": base.sha256(
                            expected_sentence(lineage.designs[position]).encode()
                        ),
                        "record_id": lineage.record_ids[position],
                    }
                    for position in DESIGN_POSITIONS
                },
                "later_cases": {
                    case_name: {
                        "device": learned.public_device(later.state, later.description),
                        "expected_action": oracle_action(later.state, later.profile),
                        "expected_record_ids": expected_selection(lineage, case_name),
                        "expected_scope": later.scope,
                    }
                    for case_name, later in lineage.cases.items()
                },
            }
            for name, lineage in LINEAGE_DATA.items()
        },
    }


def classification_schedule() -> tuple[tuple[str, str, str], ...]:
    rows = []
    for case_index, case_name in enumerate(CASES):
        shift = case_index % len(LINEAGES)
        order = LINEAGES[shift:] + LINEAGES[:shift]
        rows.extend((name, case_name, "normalize") for name in order)
        rows.extend((name, case_name, "direct_select") for name in reversed(order))
    return tuple(rows)


def later_schedule() -> tuple[tuple[int, str, str, str], ...]:
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_index, case_name in enumerate(CASES):
            for branch_index in range(len(BRANCHES)):
                branch = BRANCHES[(repeat - 1 + branch_index) % len(BRANCHES)]
                shift = (repeat + case_index + branch_index) % len(LINEAGES)
                order = LINEAGES[shift:] + LINEAGES[:shift]
                rows.extend((repeat, name, case_name, branch) for name in order)
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


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    with configured_recorder():
        recorder = prior.Recorder(transport, evidence_dir)
        if evidence_dir is not None:
            (evidence_dir / "specimen.json").write_bytes(
                base.canonical_json_bytes(specimen())
            )
        calls = []
        artifacts = {}
        logical_index = 0

        for name in LINEAGES:
            lineage = LINEAGE_DATA[name]
            artifacts[name] = {
                "reports": {},
                "transcriptions": {},
                "sentences": {},
                "static_sentences": {},
            }
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
                report = learned.sensor_report(lineage.designs[position], result)
                artifacts[name]["reports"][position] = report
                artifacts[name]["static_sentences"][position] = expected_sentence(
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
                body = transcription_body(report)
                content, available, usage = available_content(
                    recorder.call(logical_index, body)
                )
                parsed = parse_transcription(content) if available else None
                expected = expected_transcription(
                    lineage.designs[position],
                    type("ResultView", (), {
                        "selected_slot": (
                            "first" if "first displayed" in report["actuator_report"]
                            else "second" if "second displayed" in report["actuator_report"]
                            else None
                        ),
                        "movement_direction": (
                            "increased" if "rose" in report["gauge_report"]
                            else "decreased" if "fell" in report["gauge_report"]
                            else None
                        ),
                    })(),
                )
                artifacts[name]["transcriptions"][position] = content
                calls.append({
                    "responsibility": "clerical_transcription",
                    "lineage": name,
                    "design_position": position,
                    "available": available,
                    "valid": parsed is not None,
                    "exact": parsed == expected,
                    "content": content,
                    "expected": expected,
                    "provider_usage": usage,
                    "request_sha256": base.sha256(body),
                })

        for name in LINEAGES:
            lineage = LINEAGE_DATA[name]
            for position in DESIGN_POSITIONS:
                transcription = artifacts[name]["transcriptions"][position]
                logical_index += 1
                body = sentence_body(transcription)
                content, available, usage = available_content(
                    recorder.call(logical_index, body)
                )
                expected = expected_sentence(lineage.designs[position])
                artifacts[name]["sentences"][position] = content
                calls.append({
                    "responsibility": "clerical_sentence",
                    "lineage": name,
                    "design_position": position,
                    "available": available,
                    "exact": available and content == expected,
                    "content": content,
                    "expected": expected,
                    "provider_usage": usage,
                    "request_sha256": base.sha256(body),
                })

        normalized_scopes = {name: {} for name in LINEAGES}
        direct_selections = {name: {} for name in LINEAGES}
        for name, case_name, task in classification_schedule():
            lineage = LINEAGE_DATA[name]
            later = lineage.cases[case_name]
            logical_index += 1
            if task == "normalize":
                body = normalizer_body(later.description)
                content, available, usage = available_content(
                    recorder.call(logical_index, body)
                )
                scope = parse_scope(content) if available else None
                normalized_scopes[name][case_name] = scope
                calls.append({
                    "responsibility": "later_scope_normalization",
                    "lineage": name,
                    "case": case_name,
                    "available": available,
                    "valid": scope is not None,
                    "exact": scope == later.scope,
                    "content": content,
                    "normalized_scope": scope,
                    "expected_scope": later.scope,
                    "provider_usage": usage,
                    "request_sha256": base.sha256(body),
                })
            else:
                body = learned.classifier_body(
                    later.description,
                    catalog_rows(lineage, artifacts[name]["transcriptions"]),
                )
                content, available, usage = available_content(
                    recorder.call(logical_index, body)
                )
                availability, selected = learned.parse_selection(
                    content, set(lineage.record_ids.values())
                )
                if not available:
                    availability, selected = "unavailable", []
                expected = expected_selection(lineage, case_name)
                direct_selections[name][case_name] = selected
                calls.append({
                    "responsibility": "direct_scope_selection",
                    "lineage": name,
                    "case": case_name,
                    "availability": availability,
                    "selected_record_ids": selected,
                    "expected_record_ids": expected,
                    "exact": availability == "available" and selected == expected,
                    "false_selection": not expected and bool(selected),
                    "content": content,
                    "provider_usage": usage,
                    "request_sha256": base.sha256(body),
                })

        selections = {}
        for name in LINEAGES:
            lineage = LINEAGE_DATA[name]
            model_source_scopes = {
                position: source_scope(artifacts[name]["transcriptions"][position])
                for position in DESIGN_POSITIONS
            }
            static_source_scopes = {
                position: {
                    "beacon_class": lineage.designs[position].beacon,
                    "housing_class": lineage.designs[position].housing,
                }
                for position in DESIGN_POSITIONS
            }
            selections[name] = {"model": {}, "static": {}}
            for case_name in CASES:
                current_scope = normalized_scopes[name].get(case_name)
                selections[name]["model"][case_name] = exact_match_ids(
                    lineage, current_scope, model_source_scopes
                )
                selections[name]["static"][case_name] = exact_match_ids(
                    lineage, current_scope, static_source_scopes
                )

        later_rows = []
        for repeat, name, case_name, branch in later_schedule():
            lineage = LINEAGE_DATA[name]
            later = lineage.cases[case_name]
            sentences = artifacts[name]["sentences"]
            static_sentences = artifacts[name]["static_sentences"]
            if branch == COLD:
                material = ""
            elif branch == RAW:
                material = raw_material(artifacts[name]["reports"])
            elif branch == ALL_SENTENCES:
                material = all_sentence_material(sentences)
            elif branch == DIRECT_SELECTOR:
                material = selected_sentence(
                    lineage, sentences, direct_selections[name][case_name]
                )
            elif branch == NORMALIZED_PIPELINE:
                material = selected_sentence(
                    lineage, sentences, selections[name]["model"][case_name]
                )
            elif branch == NORMALIZED_STATIC:
                material = selected_sentence(
                    lineage, static_sentences, selections[name]["static"][case_name]
                )
            elif branch == ORACLE_CLERK:
                material = selected_sentence(
                    lineage, sentences, expected_selection(lineage, case_name)
                )
            elif branch == ORACLE_STATIC:
                material = selected_sentence(
                    lineage, static_sentences, expected_selection(lineage, case_name)
                )
            else:  # pragma: no cover
                raise AssertionError(branch)
            logical_index += 1
            body = participant_body(later.state, later.description, material)
            status, error, content, content_available, usage = recorder.call(
                logical_index, body
            )
            availability, action = base.parse_action(content, later.state)
            if status != 200 or error is not None:
                availability, action = "unavailable", None
            provider_available = status == 200 and error is None and content_available
            proposal = ProposalReceipt(
                provider_available, (action or content) if provider_available else ""
            )
            result = apply_committed_action(later.state, later.profile, proposal)
            row = {
                "responsibility": "later_action",
                "lineage": name,
                "case": case_name,
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
        raise SuccessorRefusal("logical_call_count_mismatch")

    distributions = {
        branch: {
            case_name: {
                "assigned": len(cell := [
                    row for row in later_rows
                    if row["branch"] == branch and row["case"] == case_name
                ]),
                "correct_actions": sum(row["correct_action"] for row in cell),
                "invalid_or_unavailable": sum(
                    row["availability"] != "available" for row in cell
                ),
                "distinct_outcomes": len(Counter(
                    row["action"] or f"<{row['availability']}>" for row in cell
                )),
            }
            for case_name in CASES
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
    every_cell_valid = all(
        distributions[branch][case]["invalid_or_unavailable"] <= 1
        for branch in BRANCHES for case in CASES
    )
    exact_transcriptions = sum(
        row["exact"] for row in calls
        if row["responsibility"] == "clerical_transcription"
    )
    exact_sentences = sum(
        row["exact"] for row in calls
        if row["responsibility"] == "clerical_sentence"
    )
    exact_normalizations = sum(
        row["exact"] for row in calls
        if row["responsibility"] == "later_scope_normalization"
    )
    direct_rows = [
        row for row in calls if row["responsibility"] == "direct_scope_selection"
    ]

    def selection_score(kind: str) -> dict[str, int]:
        rows = []
        for name in LINEAGES:
            lineage = LINEAGE_DATA[name]
            for case_name in CASES:
                selected = selections[name][kind][case_name]
                expected = expected_selection(lineage, case_name)
                rows.append((selected, expected))
        return {
            "exact": sum(selected == expected for selected, expected in rows),
            "false_selections": sum(not expected and bool(selected) for selected, expected in rows),
            "total": len(rows),
        }

    selection_scores = {
        "direct_selector": {
            "exact": sum(row["exact"] for row in direct_rows),
            "false_selections": sum(row["false_selection"] for row in direct_rows),
            "total": len(direct_rows),
        },
        "normalized_model_scopes": selection_score("model"),
        "normalized_supplied_scopes": selection_score("static"),
    }
    engaged = (
        matching_scores[ORACLE_STATIC] >= 29
        and all(score >= 14 for score in design_scores[ORACLE_STATIC].values())
        and all(score >= 14 for score in direction_scores[ORACLE_STATIC].values())
        and every_cell_valid
    )
    encoding_found = (
        exact_transcriptions >= 3
        and exact_sentences >= 3
        and matching_scores[ORACLE_CLERK] >= 27
    )
    normalization_found = (
        exact_normalizations >= 10
        and selection_scores["normalized_supplied_scopes"]["exact"] >= 10
        and selection_scores["normalized_supplied_scopes"]["false_selections"] <= 1
        and matching_scores[NORMALIZED_STATIC] >= 27
    )
    unrelated_loss = unrelated_scores[COLD] - unrelated_scores[NORMALIZED_PIPELINE]
    pipeline_candidate = (
        encoding_found
        and normalization_found
        and selection_scores["normalized_model_scopes"]["exact"] >= 10
        and selection_scores["normalized_model_scopes"]["false_selections"] <= 1
        and matching_scores[NORMALIZED_PIPELINE] >= 27
        and matching_scores[NORMALIZED_PIPELINE] - matching_scores[COLD] >= 8
        and matching_scores[NORMALIZED_PIPELINE] - matching_scores[RAW] >= 4
        and matching_scores[NORMALIZED_PIPELINE] - matching_scores[ALL_SENTENCES] >= 4
        and matching_scores[ORACLE_STATIC] - matching_scores[NORMALIZED_PIPELINE] <= 4
        and unrelated_loss <= 2
    )
    harmful = engaged and unrelated_loss >= 4
    if not engaged:
        verdict_class = "not_engaged"
    elif harmful:
        verdict_class = "harmful"
    elif pipeline_candidate:
        verdict_class = "pipeline_candidate"
    elif encoding_found and not normalization_found:
        verdict_class = "encoding_only"
    elif normalization_found and not encoding_found:
        verdict_class = "normalization_only"
    else:
        verdict_class = "null"

    packet = {
        "attempts": recorder.attempts,
        "calls": calls,
        "design_scores": design_scores,
        "direction_scores": direction_scores,
        "encoding": {
            "exact_sentences": exact_sentences,
            "exact_transcriptions": exact_transcriptions,
            "total": SOURCE_ACTION_CALLS,
        },
        "every_participant_cell_valid": every_cell_valid,
        "formation_verdict": None,
        "instrument_verdict": {
            "class": verdict_class,
            "scope": "staged_clerical_instrument_successor",
        },
        "logical_calls": len(calls),
        "matching_scores": matching_scores,
        "models": {
            "clerical": {
                "model": learned.INSTRUMENT_MODEL,
                "digest": learned.INSTRUMENT_MODEL_DIGEST,
            },
            "participant": {"model": base.MODEL, "digest": base.MODEL_DIGEST},
        },
        "normalization": {
            "exact": exact_normalizations,
            "total": NORMALIZATION_CALLS,
        },
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "request_distributions": distributions,
        "retries": recorder.retries,
        "selection_scores": selection_scores,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "unrelated_loss": unrelated_loss,
        "unrelated_scores": unrelated_scores,
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise SuccessorRefusal("retained_specimen_mismatch")
    retained = json.loads((evidence_dir / "packet.json").read_bytes())
    entries = []
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        meta = json.loads(meta_path.read_text())
        request = (evidence_dir / "attempts" / f"{stem}.request.json").read_bytes()
        response = (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes()
        entries.append((request, response, meta))
    position = 0

    def transport(body: bytes) -> tuple[int, bytes]:
        nonlocal position
        request, response, meta = entries[position]
        position += 1
        if request != body:
            raise SuccessorRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise SuccessorRefusal("evidence_replay_mismatch")
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
    if args.evidence_dir is None:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        args.evidence_dir = Path("evidence") / f"staged-clerical-instrument-{run_id}"
    started = time.monotonic()
    receipt = learned.collect_provider_receipt()
    if not receipt["valid"]:
        raise SuccessorRefusal("provider_identity_mismatch")
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
