"""Validate the fresh end-to-end learned clerical instrument."""

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
from contact import distributional_developmental_comparison as base
from contact import learned_clerical_instrument_exploration as learned
from contact import staged_chain_validation as prior
from contact import staged_clerical_instrument_successor as staged
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


PROTOCOL_VERSION = "learned-clerical-instrument-validation-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "LEARNED_CLERICAL_INSTRUMENT_VALIDATION.md"
LINEAGES = tuple(f"lineage_{index:02d}" for index in range(1, 5))
DESIGN_POSITIONS = ("a", "b")
CASES = learned.CASES

COLD = "cold"
RAW = "raw_exposed_sensor_reports"
FULL = "exposed_clerical_pipeline"
HIDDEN = "consequence_hidden_clerical_pipeline"
REMOVED = "exposed_guidance_removed"
ALL_RENDERED = "all_exposed_rendered_sentences"
NORMALIZED_STATIC = "normalized_selected_supplied_sentence"
ORACLE_EXPOSED = "oracle_selected_exposed_sentence"
ORACLE_STATIC = "oracle_selected_supplied_sentence"
BRANCHES = (
    COLD,
    RAW,
    FULL,
    HIDDEN,
    REMOVED,
    ALL_RENDERED,
    NORMALIZED_STATIC,
    ORACLE_EXPOSED,
    ORACLE_STATIC,
)

REPEATS = 3
SOURCE_ACTION_CALLS = len(LINEAGES) * len(DESIGN_POSITIONS)
EXPOSED_CLERK_CALLS = SOURCE_ACTION_CALLS * 3
HIDDEN_CLERK_CALLS = SOURCE_ACTION_CALLS * 3
NORMALIZATION_CALLS = len(LINEAGES) * len(CASES)
LATER_CALLS = len(LINEAGES) * len(CASES) * len(BRANCHES) * REPEATS
PLANNED_LOGICAL_CALLS = (
    SOURCE_ACTION_CALLS
    + EXPOSED_CLERK_CALLS
    + HIDDEN_CLERK_CALLS
    + NORMALIZATION_CALLS
    + LATER_CALLS
)
PHYSICAL_CALL_CEILING = 740
MAX_RETRIES = 12


class ValidationRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


def validation_designs(index: int) -> dict[str, learned.Design]:
    if index in {1, 3}:
        a_slot, b_slot = (
            (FIRST_INCREASES, SECOND_INCREASES)
            if index == 1 else
            (SECOND_INCREASES, FIRST_INCREASES)
        )
        return {
            "a": learned.Design(
                "faceted", "violet", a_slot,
                "The enclosure has several flat, angled faces. Its status lamp shines purple-violet.",
                "A violet indicator sits on a faceted case.",
            ),
            "b": learned.Design(
                "arched", "amber", b_slot,
                "The enclosure forms a curved arch. Its status lamp shines amber.",
                "An amber indicator sits on an arched case.",
            ),
        }
    a_slot, b_slot = (
        (SECOND_INCREASES, FIRST_INCREASES)
        if index == 2 else
        (FIRST_INCREASES, SECOND_INCREASES)
    )
    return {
        "a": learned.Design(
            "ribbed", "cyan", a_slot,
            "The enclosure has parallel raised ridges. Its status lamp shines cyan.",
            "A cyan indicator sits on a ribbed case.",
        ),
        "b": learned.Design(
            "tapered", "white", b_slot,
            "The enclosure narrows toward the top. Its status lamp shines white.",
            "A white indicator sits on a tapered case.",
        ),
    }


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
    designs = validation_designs(index)
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
        position = 23100 + index * 401 + design_index * 83
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
            if index % 2:
                description = "A green indicator sits on a plain, smooth case."
                scope = {"beacon_class": "green", "housing_class": "smooth"}
            else:
                description = "A red indicator sits on a dimpled case."
                scope = {"beacon_class": "red", "housing_class": "dimpled"}
            increasing_slot = FIRST_INCREASES if index in {1, 4} else SECOND_INCREASES
        else:
            design_position = None
            description = (
                f"An {designs['b'].beacon} indicator sits on a {designs['a'].housing} case."
            )
            scope = {
                "beacon_class": designs["b"].beacon,
                "housing_class": designs["a"].housing,
            }
            increasing_slot = SECOND_INCREASES if index in {1, 4} else FIRST_INCREASES
        profile = LineageProfile(
            opaque(f"{name}:{case_name}:fresh-family"), increasing_slot
        )
        position = 27100 + index * 557 + case_index * 109
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


def hidden_report(report: dict[str, str]) -> dict[str, str]:
    return {**report, "gauge_report": "Gauge movement was unavailable to this clerk."}


def report_view(report: dict[str, str]) -> Any:
    return type("ReportView", (), {
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
    })()


def expected_selection(lineage: Lineage, case_name: str) -> list[str]:
    position = lineage.cases[case_name].design_position
    return [lineage.record_ids[position]] if position is not None else []


def source_scope(transcription: str) -> dict[str, str] | None:
    parsed = staged.parse_transcription(transcription)
    return parsed["scope"] if parsed is not None else None


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


def selected_sentence(
    lineage: Lineage,
    sentences: dict[str, str],
    selected: list[str],
) -> str:
    by_id = {
        lineage.record_ids[position]: sentences[position]
        for position in DESIGN_POSITIONS
    }
    if len(selected) == 1:
        return by_id[selected[0]]
    if not selected:
        return ""
    return "\n".join(by_id[record_id] for record_id in selected)


def all_material(sentences: dict[str, str]) -> str:
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
        "exposed_clerk_calls": EXPOSED_CLERK_CALLS,
        "hidden_clerk_calls": HIDDEN_CLERK_CALLS,
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
        "source_action_calls": SOURCE_ACTION_CALLS,
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "lineages": {
            name: {
                "sources": {
                    position: learned.public_device(
                        lineage.acquisitions[position],
                        lineage.designs[position].source_description,
                    )
                    for position in DESIGN_POSITIONS
                },
                "cases": {
                    case_name: {
                        "device": learned.public_device(case.state, case.description),
                        "expected_action": oracle_action(case.state, case.profile),
                        "expected_record_ids": expected_selection(lineage, case_name),
                        "expected_scope": case.scope,
                    }
                    for case_name, case in lineage.cases.items()
                },
            }
            for name, lineage in LINEAGE_DATA.items()
        },
    }


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
                "hidden_reports": {},
                "exposed": {"transcriptions": {}, "prose": {}, "sentences": {}},
                "hidden": {"transcriptions": {}, "prose": {}, "sentences": {}},
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
                artifacts[name]["hidden_reports"][position] = hidden_report(report)
                artifacts[name]["static_sentences"][position] = staged.expected_sentence(
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

        for condition in ("exposed", "hidden"):
            report_key = "reports" if condition == "exposed" else "hidden_reports"
            for phase in ("transcription", "prose", "parse"):
                for name in LINEAGES:
                    lineage = LINEAGE_DATA[name]
                    for position in DESIGN_POSITIONS:
                        logical_index += 1
                        if phase == "transcription":
                            report = artifacts[name][report_key][position]
                            body = staged.transcription_body(report)
                        elif phase == "prose":
                            body = staged.sentence_body(
                                artifacts[name][condition]["transcriptions"][position]
                            )
                        else:
                            body = prose_parser.parser_body(
                                artifacts[name][condition]["prose"][position]
                            )
                        content, available, usage = available_content(
                            recorder.call(logical_index, body)
                        )
                        expected_record = canonical.expected_record(
                            lineage.designs[position]
                        )
                        if phase == "transcription":
                            parsed = staged.parse_transcription(content) if available else None
                            expected = staged.expected_transcription(
                                lineage.designs[position],
                                report_view(artifacts[name][report_key][position]),
                            )
                            artifacts[name][condition]["transcriptions"][position] = content
                            row = {
                                "responsibility": "clerical_transcription",
                                "valid": parsed is not None,
                                "exact": parsed == expected,
                                "expected": expected,
                            }
                        elif phase == "prose":
                            semantic = prose_parser.parse_explicit_sentence(content)
                            artifacts[name][condition]["prose"][position] = content
                            row = {
                                "responsibility": "clerical_explicit_prose",
                                "valid": semantic is not None,
                                "exact": semantic == expected_record,
                                "expected": expected_record,
                            }
                        else:
                            parsed = canonical.parse_record(content) if available else None
                            sentence = canonical.render_sentence(parsed)
                            artifacts[name][condition]["sentences"][position] = sentence
                            row = {
                                "responsibility": "clerical_prose_parse",
                                "valid": parsed is not None,
                                "exact": parsed == expected_record,
                                "rendered_sentence": sentence,
                                "rendered_exact": sentence == staged.expected_sentence(
                                    lineage.designs[position]
                                ),
                                "expected": expected_record,
                            }
                        calls.append({
                            **row,
                            "lineage": name,
                            "design_position": position,
                            "consequence_condition": condition,
                            "available": available,
                            "content": content,
                            "provider_usage": usage,
                            "request_sha256": base.sha256(body),
                        })

        normalized_scopes = {name: {} for name in LINEAGES}
        for name in LINEAGES:
            lineage = LINEAGE_DATA[name]
            for case_name in CASES:
                later = lineage.cases[case_name]
                logical_index += 1
                body = staged.normalizer_body(later.description)
                content, available, usage = available_content(
                    recorder.call(logical_index, body)
                )
                scope = staged.parse_scope(content) if available else None
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

        selections = {name: {"exposed": {}, "hidden": {}, "static": {}} for name in LINEAGES}
        for name in LINEAGES:
            lineage = LINEAGE_DATA[name]
            scopes = {
                condition: {
                    position: source_scope(
                        artifacts[name][condition]["transcriptions"][position]
                    )
                    for position in DESIGN_POSITIONS
                }
                for condition in ("exposed", "hidden")
            }
            scopes["static"] = {
                position: {
                    "beacon_class": lineage.designs[position].beacon,
                    "housing_class": lineage.designs[position].housing,
                }
                for position in DESIGN_POSITIONS
            }
            for case_name in CASES:
                for condition in ("exposed", "hidden", "static"):
                    selections[name][condition][case_name] = exact_match_ids(
                        lineage,
                        normalized_scopes[name][case_name],
                        scopes[condition],
                    )

        later_rows = []
        for repeat, name, case_name, branch in later_schedule():
            lineage = LINEAGE_DATA[name]
            later = lineage.cases[case_name]
            expected = expected_selection(lineage, case_name)
            if branch in {COLD, REMOVED}:
                material = ""
            elif branch == RAW:
                material = raw_material(artifacts[name]["reports"])
            elif branch == FULL:
                material = selected_sentence(
                    lineage,
                    artifacts[name]["exposed"]["sentences"],
                    selections[name]["exposed"][case_name],
                )
            elif branch == HIDDEN:
                material = selected_sentence(
                    lineage,
                    artifacts[name]["hidden"]["sentences"],
                    selections[name]["hidden"][case_name],
                )
            elif branch == ALL_RENDERED:
                material = all_material(artifacts[name]["exposed"]["sentences"])
            elif branch == NORMALIZED_STATIC:
                material = selected_sentence(
                    lineage,
                    artifacts[name]["static_sentences"],
                    selections[name]["static"][case_name],
                )
            elif branch == ORACLE_EXPOSED:
                material = selected_sentence(
                    lineage, artifacts[name]["exposed"]["sentences"], expected
                )
            elif branch == ORACLE_STATIC:
                material = selected_sentence(
                    lineage, artifacts[name]["static_sentences"], expected
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
        raise ValidationRefusal("logical_call_count_mismatch")

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

    def component_count(responsibility: str, condition: str, field: str = "exact") -> int:
        return sum(
            row[field] for row in calls
            if row["responsibility"] == responsibility
            and row.get("consequence_condition") == condition
        )

    exact_transcriptions = component_count("clerical_transcription", "exposed")
    exact_prose = component_count("clerical_explicit_prose", "exposed")
    exact_records = component_count("clerical_prose_parse", "exposed")
    exact_rendered = component_count("clerical_prose_parse", "exposed", "rendered_exact")
    hidden_exact_records = component_count("clerical_prose_parse", "hidden")
    exact_normalizations = sum(
        row["exact"] for row in calls
        if row["responsibility"] == "later_scope_normalization"
    )
    selection_rows = []
    for name in LINEAGES:
        lineage = LINEAGE_DATA[name]
        for case_name in CASES:
            selected = selections[name]["exposed"][case_name]
            expected = expected_selection(lineage, case_name)
            selection_rows.append((selected, expected))
    selection_score = {
        "exact": sum(selected == expected for selected, expected in selection_rows),
        "false_selections": sum(not expected and bool(selected) for selected, expected in selection_rows),
        "total": len(selection_rows),
    }
    engaged = (
        matching_scores[ORACLE_STATIC] >= 43
        and all(score >= 21 for score in design_scores[ORACLE_STATIC].values())
        and all(score >= 21 for score in direction_scores[ORACLE_STATIC].values())
        and every_cell_valid
    )
    unrelated_loss = unrelated_scores[COLD] - unrelated_scores[FULL]
    supported = (
        engaged
        and exact_transcriptions >= 7
        and exact_prose >= 7
        and exact_records >= 7
        and exact_rendered >= 7
        and exact_normalizations >= 20
        and selection_score["exact"] >= 20
        and selection_score["false_selections"] <= 2
        and matching_scores[FULL] >= 43
        and all(score >= 21 for score in design_scores[FULL].values())
        and all(score >= 21 for score in direction_scores[FULL].values())
        and all(
            matching_scores[FULL] - matching_scores[branch] >= 16
            for branch in (COLD, RAW, HIDDEN, REMOVED)
        )
        and matching_scores[ORACLE_STATIC] - matching_scores[FULL] <= 4
        and matching_scores[ORACLE_EXPOSED] >= 43
        and matching_scores[NORMALIZED_STATIC] >= 43
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
            "exposed_exact_prose": exact_prose,
            "exposed_exact_records": exact_records,
            "exposed_exact_rendered": exact_rendered,
            "exposed_exact_transcriptions": exact_transcriptions,
            "hidden_exact_records": hidden_exact_records,
            "later_exact_normalizations": exact_normalizations,
        },
        "design_scores": design_scores,
        "direction_scores": direction_scores,
        "every_participant_cell_valid": every_cell_valid,
        "formation_verdict": None,
        "instrument_verdict": {
            "class": verdict_class,
            "scope": "learned_clerical_instrument_validation",
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
        "normalized_selection": selection_score,
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "request_distributions": distributions,
        "retries": recorder.retries,
        "scope_errors_prevented": max(0, unrelated_scores[FULL] - unrelated_scores[ALL_RENDERED]),
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "unrelated_loss": unrelated_loss,
        "unrelated_scores": unrelated_scores,
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise ValidationRefusal("retained_specimen_mismatch")
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
            raise ValidationRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise ValidationRefusal("evidence_replay_mismatch")
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
        args.evidence_dir = Path("evidence") / f"learned-clerical-instrument-validation-{run_id}"
    started = time.monotonic()
    receipt = learned.collect_provider_receipt()
    if not receipt["valid"]:
        raise ValidationRefusal("provider_identity_mismatch")
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
