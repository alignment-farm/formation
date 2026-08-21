"""Explore revision in the validated learned clerical substrate."""

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
from contact import learned_clerical_instrument_validation as validated
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


PROTOCOL_VERSION = "learned-clerical-revision-exploration-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "LEARNED_CLERICAL_REVISION_EXPLORATION.md"
LINEAGES = ("lineage_01", "lineage_02")
DESIGN_POSITIONS = ("a", "b")
PRE_CASES = ("a_up", "a_down", "b_up", "b_down")
CASES = learned.CASES

COLD = "cold"
RAW = "raw_counterexperience"
REVISED = "newest_exposed_revision"
STALE = "stale_old_record"
HIDDEN = "consequence_hidden_revision"
REMOVED = "exposed_revision_removed"
ALL_VERSIONS = "old_and_new_versions"
SUPPLIED = "normalized_selected_supplied_revision"
ORACLE_REVISED = "oracle_selected_exposed_revision"
BRANCHES = (
    COLD, RAW, REVISED, STALE, HIDDEN, REMOVED, ALL_VERSIONS, SUPPLIED,
    ORACLE_REVISED,
)

REPEATS = 3
OLD_RECORD_CALLS = len(LINEAGES) * len(DESIGN_POSITIONS) * 4
PRE_ACTION_CALLS = len(LINEAGES) * len(PRE_CASES) * REPEATS
COUNTER_ACTION_CALLS = len(LINEAGES) * len(DESIGN_POSITIONS)
REVISION_CLERK_CALLS = len(LINEAGES) * len(DESIGN_POSITIONS) * 3 * 2
NORMALIZATION_CALLS = len(LINEAGES) * len(CASES)
POST_ACTION_CALLS = len(LINEAGES) * len(CASES) * len(BRANCHES) * REPEATS
PLANNED_LOGICAL_CALLS = (
    OLD_RECORD_CALLS + PRE_ACTION_CALLS + COUNTER_ACTION_CALLS
    + REVISION_CLERK_CALLS + NORMALIZATION_CALLS + POST_ACTION_CALLS
)
PHYSICAL_CALL_CEILING = 412
MAX_RETRIES = 8


class RevisionRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


def flip(slot: str) -> str:
    return SECOND_INCREASES if slot == FIRST_INCREASES else FIRST_INCREASES


@dataclass(frozen=True)
class Case:
    state: LineageState
    profile: LineageProfile
    description: str
    scope: dict[str, str]
    design_position: str | None


@dataclass(frozen=True)
class Lineage:
    name: str
    designs: dict[str, learned.Design]
    old_sources: dict[str, LineageState]
    old_profiles: dict[str, LineageProfile]
    pre_cases: dict[str, Case]
    counter_sources: dict[str, LineageState]
    counter_profiles: dict[str, LineageProfile]
    post_cases: dict[str, Case]
    record_ids: dict[str, str]


def state(label: str, position: int, target: int, profile: LineageProfile) -> LineageState:
    return LineageState(
        profile.controller_family,
        opaque(f"{label}:device"),
        position,
        target,
        (opaque(f"{label}:first"), opaque(f"{label}:second")),
    )


def make_lineage(name: str, index: int) -> Lineage:
    designs = validated.validation_designs(index)
    old_sources = {}
    old_profiles = {}
    counter_sources = {}
    counter_profiles = {}
    for design_index, position_name in enumerate(DESIGN_POSITIONS, 1):
        design = designs[position_name]
        old_profile = LineageProfile(
            opaque(f"{name}:{position_name}:old-family"), design.increasing_slot
        )
        old_position = 31100 + index * 421 + design_index * 89
        old_sources[position_name] = state(
            f"{name}:{position_name}:old-source",
            old_position,
            old_position + (1 if (index + design_index) % 2 else -1),
            old_profile,
        )
        old_profiles[position_name] = old_profile
        counter_profile = LineageProfile(
            opaque(f"{name}:{position_name}:counter-family"),
            flip(design.increasing_slot),
        )
        counter_position = 33100 + index * 433 + design_index * 97
        counter_sources[position_name] = state(
            f"{name}:{position_name}:counter-source",
            counter_position,
            counter_position + (1 if design_index == 1 else -1),
            counter_profile,
        )
        counter_profiles[position_name] = counter_profile

    pre_cases = {}
    for case_index, case_name in enumerate(PRE_CASES, 1):
        position_name = case_name[0]
        design = designs[position_name]
        profile = LineageProfile(
            opaque(f"{name}:{case_name}:pre-family"), design.increasing_slot
        )
        current = 35100 + index * 449 + case_index * 101
        pre_cases[case_name] = Case(
            state(
                f"{name}:{case_name}:pre", current,
                current + (1 if case_name.endswith("up") else -1), profile,
            ),
            profile,
            design.later_description,
            {"beacon_class": design.beacon, "housing_class": design.housing},
            position_name,
        )

    post_cases = {}
    for case_index, case_name in enumerate(CASES, 1):
        if case_name.startswith("a_") or case_name.startswith("b_"):
            position_name = case_name[0]
            design = designs[position_name]
            description = design.later_description
            scope = {"beacon_class": design.beacon, "housing_class": design.housing}
            increasing_slot = flip(design.increasing_slot)
        elif case_name == "novel_up":
            position_name = None
            if index == 1:
                description = "A green indicator sits on a plain, smooth case."
                scope = {"beacon_class": "green", "housing_class": "smooth"}
                increasing_slot = FIRST_INCREASES
            else:
                description = "A red indicator sits on a dimpled case."
                scope = {"beacon_class": "red", "housing_class": "dimpled"}
                increasing_slot = SECOND_INCREASES
        else:
            position_name = None
            description = (
                f"An {designs['b'].beacon} indicator sits on a {designs['a'].housing} case."
            )
            scope = {
                "beacon_class": designs["b"].beacon,
                "housing_class": designs["a"].housing,
            }
            increasing_slot = SECOND_INCREASES if index == 1 else FIRST_INCREASES
        profile = LineageProfile(
            opaque(f"{name}:{case_name}:post-family"), increasing_slot
        )
        current = 37100 + index * 461 + case_index * 103
        post_cases[case_name] = Case(
            state(
                f"{name}:{case_name}:post", current,
                current + (1 if case_name.endswith("up") else -1), profile,
            ),
            profile, description, scope, position_name,
        )
    return Lineage(
        name, designs, old_sources, old_profiles, pre_cases, counter_sources,
        counter_profiles, post_cases,
        {position: opaque(f"{name}:{position}:record") for position in DESIGN_POSITIONS},
    )


LINEAGE_DATA = {
    name: make_lineage(name, index) for index, name in enumerate(LINEAGES, 1)
}


def participant_body(state_value: LineageState, description: str, material: str) -> bytes:
    record = {
        "device": learned.public_device(state_value, description),
        "responsibility": ACTION_RESPONSIBILITY,
        "retained_material": material,
    }
    return learned.canonical_envelope(
        base.MODEL, calibration.PARTICIPANT_SYSTEM,
        f"ACTION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",
        base.ACTION_SETTINGS,
    )


def design_with_slot(design: learned.Design, increasing_slot: str) -> learned.Design:
    return learned.Design(
        design.housing, design.beacon, increasing_slot,
        design.source_description, design.later_description,
    )


def expected_selection(lineage: Lineage, case_name: str) -> list[str]:
    position = lineage.post_cases[case_name].design_position
    return [lineage.record_ids[position]] if position is not None else []


def source_scope(transcription: str) -> dict[str, str] | None:
    parsed = staged.parse_transcription(transcription)
    return parsed["scope"] if parsed is not None else None


def exact_match(
    lineage: Lineage,
    current_scope: dict[str, str] | None,
    scopes: dict[str, dict[str, str] | None],
) -> list[str]:
    if current_scope is None:
        return []
    return [
        lineage.record_ids[position]
        for position in DESIGN_POSITIONS
        if scopes[position] is not None and scopes[position] == current_scope
    ]


def selected_sentence(
    lineage: Lineage, sentences: dict[str, str], selected: list[str]
) -> str:
    by_id = {
        lineage.record_ids[position]: sentences[position]
        for position in DESIGN_POSITIONS
    }
    if len(selected) == 1:
        return by_id[selected[0]]
    if not selected:
        return ""
    return "\n".join(by_id[item] for item in selected)


def newest_eligible_sentence(
    lineage: Lineage,
    selected: list[str],
    versions: tuple[tuple[int, dict[str, str]], ...],
) -> str:
    """Render only the newest complete version of each selected record lineage."""
    if not selected:
        return ""
    selected_sentences = []
    for record_id in selected:
        position = next(
            (item for item in DESIGN_POSITIONS if lineage.record_ids[item] == record_id),
            None,
        )
        if position is None:
            continue
        eligible = [
            (version, sentences[position])
            for version, sentences in versions
            if sentences.get(position)
        ]
        if eligible:
            selected_sentences.append(max(eligible, key=lambda item: item[0])[1])
    return "\n".join(selected_sentences)


def raw_material(reports: dict[str, dict[str, str]]) -> str:
    return base.canonical_json_bytes({
        "raw_counterexperiences": [reports[position] for position in DESIGN_POSITIONS]
    }).decode()


def all_versions(
    lineage: Lineage,
    old: dict[str, str],
    new: dict[str, str],
    selected: list[str],
) -> str:
    positions = [
        position
        for position in DESIGN_POSITIONS
        if lineage.record_ids[position] in selected
    ]
    return "\n".join(
        f"VERSION 1: {old[position]}\nVERSION 2: {new[position]}"
        for position in positions
    )


def specimen() -> dict[str, Any]:
    return {
        "branches": list(BRANCHES),
        "cases": list(CASES),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "instrument_model": learned.INSTRUMENT_MODEL,
        "instrument_model_digest": learned.INSTRUMENT_MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "lineages": {
            name: {
                "old_sources": {
                    position: learned.public_device(
                        lineage.old_sources[position],
                        lineage.designs[position].source_description,
                    )
                    for position in DESIGN_POSITIONS
                },
                "counter_sources": {
                    position: learned.public_device(
                        lineage.counter_sources[position],
                        lineage.designs[position].source_description,
                    )
                    for position in DESIGN_POSITIONS
                },
                "post_cases": {
                    case_name: {
                        "device": learned.public_device(case.state, case.description),
                        "expected_action": oracle_action(case.state, case.profile),
                        "expected_record_ids": expected_selection(lineage, case_name),
                    }
                    for case_name, case in lineage.post_cases.items()
                },
            }
            for name, lineage in LINEAGE_DATA.items()
        },
    }


def pre_schedule() -> tuple[tuple[int, str, str], ...]:
    return tuple(
        (repeat, name, case_name)
        for repeat in range(1, REPEATS + 1)
        for case_name in PRE_CASES
        for name in LINEAGES
    )


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


def available(call_result: tuple[Any, ...]) -> tuple[str, bool, Any]:
    status, error, content, content_available, usage = call_result
    ok = status == 200 and error is None and content_available
    return (content if ok else ""), ok, usage


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    with configured_recorder():
        recorder = prior.Recorder(transport, evidence_dir)
        if evidence_dir is not None:
            (evidence_dir / "specimen.json").write_bytes(
                base.canonical_json_bytes(specimen())
            )
        calls = []
        artifacts = {
            name: {
                "old_reports": {}, "old_trans": {}, "old_prose": {},
                "old_records": {}, "old_sentences": {}, "old_source_refs": {},
                "counter_reports": {}, "hidden_reports": {},
                "counter_source_refs": {},
                "revised": {"trans": {}, "prose": {}, "records": {}, "sentences": {}},
                "hidden": {"trans": {}, "prose": {}, "records": {}, "sentences": {}},
                "static": {},
            }
            for name in LINEAGES
        }
        logical_index = 0

        for name in LINEAGES:
            lineage = LINEAGE_DATA[name]
            for position in DESIGN_POSITIONS:
                state_value = lineage.old_sources[position]
                logical_index += 1
                body = participant_body(
                    state_value, lineage.designs[position].source_description, ""
                )
                status, error, content, ca, usage = recorder.call(logical_index, body)
                availability, action = base.parse_action(content, state_value)
                if status != 200 or error is not None:
                    availability, action = "unavailable", None
                proposal = ProposalReceipt(
                    status == 200 and error is None and ca,
                    (action or content) if status == 200 and error is None and ca else "",
                )
                result = apply_committed_action(
                    state_value, lineage.old_profiles[position], proposal
                )
                artifacts[name]["old_reports"][position] = learned.sensor_report(
                    lineage.designs[position], result
                )
                source_row = {
                    "responsibility": "old_source_action", "lineage": name,
                    "design_position": position, "action": action,
                    "availability": availability, "external_result": base.exposed_result(result),
                    "provider_usage": usage, "request_sha256": base.sha256(body),
                }
                calls.append(source_row)
                artifacts[name]["old_source_refs"][position] = {
                    "responsibility": source_row["responsibility"],
                    "request_sha256": source_row["request_sha256"],
                    "external_result_sha256": base.sha256(
                        base.canonical_json_bytes(source_row["external_result"])
                    ),
                }

        for phase in ("trans", "prose", "parse"):
            for name in LINEAGES:
                lineage = LINEAGE_DATA[name]
                for position in DESIGN_POSITIONS:
                    logical_index += 1
                    if phase == "trans":
                        body = staged.transcription_body(artifacts[name]["old_reports"][position])
                    elif phase == "prose":
                        body = staged.sentence_body(artifacts[name]["old_trans"][position])
                    else:
                        body = prose_parser.parser_body(artifacts[name]["old_prose"][position])
                    content, ok, usage = available(recorder.call(logical_index, body))
                    expected = canonical.expected_record(lineage.designs[position])
                    if phase == "trans":
                        parsed = staged.parse_transcription(content) if ok else None
                        report = artifacts[name]["old_reports"][position]
                        expected_trans = staged.expected_transcription(
                            lineage.designs[position], validated.report_view(report)
                        )
                        artifacts[name]["old_trans"][position] = content
                        exact = parsed == expected_trans
                        responsibility = "old_transcription"
                        rendered_exact = None
                    elif phase == "prose":
                        artifacts[name]["old_prose"][position] = content
                        exact = prose_parser.parse_explicit_sentence(content) == expected
                        responsibility = "old_explicit_prose"
                        rendered_exact = None
                    else:
                        parsed = canonical.parse_record(content) if ok else None
                        sentence = canonical.render_sentence(parsed)
                        artifacts[name]["old_records"][position] = parsed
                        artifacts[name]["old_sentences"][position] = sentence
                        exact = parsed == expected
                        rendered_exact = sentence == staged.expected_sentence(lineage.designs[position])
                        responsibility = "old_prose_parse"
                    calls.append({
                        "responsibility": responsibility, "lineage": name,
                        "design_position": position, "available": ok, "exact": exact,
                        "rendered_exact": rendered_exact, "content": content,
                        "provider_usage": usage, "request_sha256": base.sha256(body),
                    })

        pre_rows = []
        for repeat, name, case_name in pre_schedule():
            lineage = LINEAGE_DATA[name]
            case = lineage.pre_cases[case_name]
            material = artifacts[name]["old_sentences"][case.design_position]
            logical_index += 1
            body = participant_body(case.state, case.description, material)
            status, error, content, ca, usage = recorder.call(logical_index, body)
            availability, action = base.parse_action(content, case.state)
            if status != 200 or error is not None:
                availability, action = "unavailable", None
            correct = availability == "available" and action == oracle_action(case.state, case.profile)
            row = {
                "responsibility": "prechange_action", "lineage": name,
                "case": case_name, "repeat": repeat, "action": action,
                "availability": availability, "correct_action": correct,
                "provider_usage": usage, "request_sha256": base.sha256(body),
            }
            pre_rows.append(row); calls.append(row)

        counter_old_policy = 0
        counter_contradictions = 0
        for name in LINEAGES:
            lineage = LINEAGE_DATA[name]
            for position in DESIGN_POSITIONS:
                state_value = lineage.counter_sources[position]
                material = artifacts[name]["old_sentences"][position]
                logical_index += 1
                body = participant_body(
                    state_value, lineage.designs[position].source_description, material
                )
                status, error, content, ca, usage = recorder.call(logical_index, body)
                availability, action = base.parse_action(content, state_value)
                if status != 200 or error is not None:
                    availability, action = "unavailable", None
                proposal = ProposalReceipt(
                    status == 200 and error is None and ca,
                    (action or content) if status == 200 and error is None and ca else "",
                )
                result = apply_committed_action(
                    state_value, lineage.counter_profiles[position], proposal
                )
                old_view = LineageProfile(
                    state_value.controller_family,
                    lineage.designs[position].increasing_slot,
                )
                old_consistent = (
                    availability == "available"
                    and action == oracle_action(state_value, old_view)
                )
                counter_old_policy += old_consistent
                selected_slot = getattr(result, "selected_slot", None)
                old_expected_movement = (
                    "increased"
                    if (
                        selected_slot == "first"
                        and lineage.designs[position].increasing_slot == FIRST_INCREASES
                    ) or (
                        selected_slot == "second"
                        and lineage.designs[position].increasing_slot == SECOND_INCREASES
                    )
                    else "decreased"
                    if selected_slot in {"first", "second"}
                    else None
                )
                contradicts_old_record = (
                    old_expected_movement is not None
                    and getattr(result, "movement_direction", None)
                    not in {None, old_expected_movement}
                )
                counter_contradictions += contradicts_old_record
                report = learned.sensor_report(lineage.designs[position], result)
                artifacts[name]["counter_reports"][position] = report
                artifacts[name]["hidden_reports"][position] = validated.hidden_report(report)
                new_design = design_with_slot(
                    lineage.designs[position], lineage.counter_profiles[position].increasing_slot
                )
                artifacts[name]["static"][position] = staged.expected_sentence(new_design)
                counter_row = {
                    "responsibility": "counter_action", "lineage": name,
                    "design_position": position, "action": action,
                    "availability": availability, "old_policy_consistent": old_consistent,
                    "contradicts_old_record": contradicts_old_record,
                    "external_result": base.exposed_result(result),
                    "provider_usage": usage, "request_sha256": base.sha256(body),
                }
                calls.append(counter_row)
                artifacts[name]["counter_source_refs"][position] = {
                    "responsibility": counter_row["responsibility"],
                    "request_sha256": counter_row["request_sha256"],
                    "external_result_sha256": base.sha256(
                        base.canonical_json_bytes(counter_row["external_result"])
                    ),
                }

        for condition in ("revised", "hidden"):
            report_key = "counter_reports" if condition == "revised" else "hidden_reports"
            for phase in ("trans", "prose", "parse"):
                for name in LINEAGES:
                    lineage = LINEAGE_DATA[name]
                    for position in DESIGN_POSITIONS:
                        logical_index += 1
                        if phase == "trans":
                            body = staged.transcription_body(artifacts[name][report_key][position])
                        elif phase == "prose":
                            body = staged.sentence_body(artifacts[name][condition]["trans"][position])
                        else:
                            body = prose_parser.parser_body(artifacts[name][condition]["prose"][position])
                        content, ok, usage = available(recorder.call(logical_index, body))
                        new_design = design_with_slot(
                            lineage.designs[position], lineage.counter_profiles[position].increasing_slot
                        )
                        expected = canonical.expected_record(new_design)
                        if phase == "trans":
                            parsed = staged.parse_transcription(content) if ok else None
                            expected_trans = staged.expected_transcription(
                                new_design, validated.report_view(artifacts[name][report_key][position])
                            )
                            artifacts[name][condition]["trans"][position] = content
                            exact = parsed == expected_trans
                            responsibility = "revision_transcription"
                            rendered_exact = None
                        elif phase == "prose":
                            artifacts[name][condition]["prose"][position] = content
                            exact = prose_parser.parse_explicit_sentence(content) == expected
                            responsibility = "revision_explicit_prose"
                            rendered_exact = None
                        else:
                            parsed = canonical.parse_record(content) if ok else None
                            sentence = canonical.render_sentence(parsed)
                            artifacts[name][condition]["records"][position] = parsed
                            artifacts[name][condition]["sentences"][position] = sentence
                            exact = parsed == expected
                            rendered_exact = sentence == staged.expected_sentence(new_design)
                            responsibility = "revision_prose_parse"
                        calls.append({
                            "responsibility": responsibility, "lineage": name,
                            "design_position": position,
                            "consequence_condition": condition,
                            "available": ok, "exact": exact,
                            "rendered_exact": rendered_exact, "content": content,
                            "provider_usage": usage, "request_sha256": base.sha256(body),
                        })

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
                    "responsibility": "later_scope_normalization", "lineage": name,
                    "case": case_name, "available": ok, "valid": scope is not None,
                    "exact": scope == case.scope, "content": content,
                    "normalized_scope": scope, "expected_scope": case.scope,
                    "provider_usage": usage, "request_sha256": base.sha256(body),
                })

        selections = {name: {"old": {}, "revised": {}, "hidden": {}, "static": {}} for name in LINEAGES}
        for name in LINEAGES:
            lineage = LINEAGE_DATA[name]
            scopes = {
                "old": {p: source_scope(artifacts[name]["old_trans"][p]) for p in DESIGN_POSITIONS},
                "revised": {p: source_scope(artifacts[name]["revised"]["trans"][p]) for p in DESIGN_POSITIONS},
                "hidden": {p: source_scope(artifacts[name]["hidden"]["trans"][p]) for p in DESIGN_POSITIONS},
                "static": {p: {"beacon_class": lineage.designs[p].beacon, "housing_class": lineage.designs[p].housing} for p in DESIGN_POSITIONS},
            }
            for case_name in CASES:
                for version in scopes:
                    selections[name][version][case_name] = exact_match(
                        lineage, normalizations[name][case_name], scopes[version]
                    )

        record_versions = {}
        hidden_comparator_versions = {}
        for name in LINEAGES:
            lineage = LINEAGE_DATA[name]
            record_versions[name] = {}
            hidden_comparator_versions[name] = {}
            for position in DESIGN_POSITIONS:
                old_version_id = opaque(f"{name}:{position}:version:1")
                revised_version_id = opaque(f"{name}:{position}:version:2")
                hidden_version_id = opaque(f"{name}:{position}:hidden-version:2")
                old_entry = {
                    "record_lineage_id": lineage.record_ids[position],
                    "record_version_id": old_version_id,
                    "version": 1,
                    "supersedes_record_version_id": None,
                    "source_occurrence": artifacts[name]["old_source_refs"][position],
                    "record": artifacts[name]["old_records"][position],
                    "rendered_sentence": artifacts[name]["old_sentences"][position],
                }
                revised_entry = {
                    "record_lineage_id": lineage.record_ids[position],
                    "record_version_id": revised_version_id,
                    "version": 2,
                    "supersedes_record_version_id": old_version_id,
                    "source_occurrence": artifacts[name]["counter_source_refs"][position],
                    "record": artifacts[name]["revised"]["records"][position],
                    "rendered_sentence": artifacts[name]["revised"]["sentences"][position],
                }
                hidden_entry = {
                    "record_lineage_id": lineage.record_ids[position],
                    "record_version_id": hidden_version_id,
                    "version": 2,
                    "supersedes_record_version_id": old_version_id,
                    "source_occurrence": artifacts[name]["counter_source_refs"][position],
                    "record": artifacts[name]["hidden"]["records"][position],
                    "rendered_sentence": artifacts[name]["hidden"]["sentences"][position],
                }
                record_versions[name][position] = [old_entry, revised_entry]
                hidden_comparator_versions[name][position] = [old_entry, hidden_entry]

        post_rows = []
        for repeat, name, case_name, branch in post_schedule():
            lineage = LINEAGE_DATA[name]
            case = lineage.post_cases[case_name]
            expected = expected_selection(lineage, case_name)
            if branch == COLD:
                material = ""
            elif branch == RAW:
                material = raw_material(artifacts[name]["counter_reports"])
            elif branch == REVISED:
                material = newest_eligible_sentence(
                    lineage,
                    selections[name]["revised"][case_name],
                    (
                        (1, artifacts[name]["old_sentences"]),
                        (2, artifacts[name]["revised"]["sentences"]),
                    ),
                )
            elif branch == STALE:
                material = selected_sentence(lineage, artifacts[name]["old_sentences"], selections[name]["old"][case_name])
            elif branch == HIDDEN:
                material = newest_eligible_sentence(
                    lineage,
                    selections[name]["old"][case_name],
                    (
                        (1, artifacts[name]["old_sentences"]),
                        (2, artifacts[name]["hidden"]["sentences"]),
                    ),
                )
            elif branch == REMOVED:
                material = newest_eligible_sentence(
                    lineage,
                    selections[name]["old"][case_name],
                    ((1, artifacts[name]["old_sentences"]),),
                )
            elif branch == ALL_VERSIONS:
                material = all_versions(
                    lineage,
                    artifacts[name]["old_sentences"],
                    artifacts[name]["revised"]["sentences"],
                    selections[name]["revised"][case_name],
                )
            elif branch == SUPPLIED:
                material = selected_sentence(lineage, artifacts[name]["static"], selections[name]["static"][case_name])
            elif branch == ORACLE_REVISED:
                material = selected_sentence(lineage, artifacts[name]["revised"]["sentences"], expected)
            else:  # pragma: no cover
                raise AssertionError(branch)
            logical_index += 1
            body = participant_body(case.state, case.description, material)
            status, error, content, ca, usage = recorder.call(logical_index, body)
            availability, action = base.parse_action(content, case.state)
            if status != 200 or error is not None:
                availability, action = "unavailable", None
            proposal = ProposalReceipt(
                status == 200 and error is None and ca,
                (action or content) if status == 200 and error is None and ca else "",
            )
            result = apply_committed_action(case.state, case.profile, proposal)
            row = {
                "responsibility": "postchange_action", "lineage": name,
                "case": case_name, "branch": branch, "repeat": repeat,
                "action": action, "availability": availability,
                "correct_action": availability == "available" and action == oracle_action(case.state, case.profile),
                "external_result": base.exposed_result(result),
                "provider_usage": usage, "request_sha256": base.sha256(body),
                "retained_material_sha256": base.sha256(material.encode()),
            }
            post_rows.append(row); calls.append(row)

    if logical_index != PLANNED_LOGICAL_CALLS:
        raise RevisionRefusal("logical_call_count_mismatch")

    distributions = {
        branch: {
            case_name: {
                "assigned": len(cell := [r for r in post_rows if r["branch"] == branch and r["case"] == case_name]),
                "correct_actions": sum(r["correct_action"] for r in cell),
                "invalid_or_unavailable": sum(r["availability"] != "available" for r in cell),
                "distinct_outcomes": len(Counter(r["action"] or f"<{r['availability']}>" for r in cell)),
            }
            for case_name in CASES
        }
        for branch in BRANCHES
    }
    matching = ("a_up", "a_down", "b_up", "b_down")
    unrelated = ("novel_up", "recombined_down")
    def total(branch: str, cases: tuple[str, ...]) -> int:
        return sum(distributions[branch][case]["correct_actions"] for case in cases)
    matching_scores = {b: total(b, matching) for b in BRANCHES}
    unrelated_scores = {b: total(b, unrelated) for b in BRANCHES}
    design_scores = {b: {"a": total(b, ("a_up", "a_down")), "b": total(b, ("b_up", "b_down"))} for b in BRANCHES}
    direction_scores = {b: {"up": total(b, ("a_up", "b_up")), "down": total(b, ("a_down", "b_down"))} for b in BRANCHES}
    invalid_participant_cells = []
    for branch in BRANCHES:
        for case_name in CASES:
            for name in LINEAGES:
                invalid_count = sum(
                    row["availability"] != "available"
                    for row in post_rows
                    if row["branch"] == branch
                    and row["case"] == case_name
                    and row["lineage"] == name
                )
                if invalid_count > 1:
                    invalid_participant_cells.append({
                        "branch": branch,
                        "case": case_name,
                        "invalid_or_unavailable": invalid_count,
                        "lineage": name,
                    })
    every_cell_valid = not invalid_participant_cells
    old_exact = sum(r["exact"] and r.get("rendered_exact") for r in calls if r["responsibility"] == "old_prose_parse")
    revision_exact = sum(r["exact"] and r.get("rendered_exact") for r in calls if r["responsibility"] == "revision_prose_parse" and r["consequence_condition"] == "revised")
    hidden_exact = sum(r["exact"] for r in calls if r["responsibility"] == "revision_prose_parse" and r["consequence_condition"] == "hidden")
    pre_correct = sum(r["correct_action"] for r in pre_rows)
    exact_normalizations = sum(r["exact"] for r in calls if r["responsibility"] == "later_scope_normalization")
    selection_rows = []
    for name in LINEAGES:
        for case_name in CASES:
            selection_rows.append((selections[name]["revised"][case_name], expected_selection(LINEAGE_DATA[name], case_name)))
    selection_score = {
        "exact": sum(a == b for a, b in selection_rows),
        "false_selections": sum(not b and bool(a) for a, b in selection_rows),
        "total": len(selection_rows),
    }
    engaged = (
        matching_scores[SUPPLIED] >= 21
        and all(score >= 10 for score in design_scores[SUPPLIED].values())
        and all(score >= 10 for score in direction_scores[SUPPLIED].values())
        and every_cell_valid
    )
    unrelated_loss = unrelated_scores[COLD] - unrelated_scores[REVISED]
    candidate = (
        engaged and old_exact >= 3 and pre_correct >= 21
        and counter_old_policy == 4 and counter_contradictions == 4
        and revision_exact >= 3
        and exact_normalizations >= 10 and selection_score["exact"] >= 10
        and selection_score["false_selections"] <= 1
        and matching_scores[REVISED] >= 21
        and all(matching_scores[REVISED] - matching_scores[b] >= 8 for b in (COLD, RAW, HIDDEN, REMOVED))
        and matching_scores[REVISED] - matching_scores[STALE] >= 16
        and matching_scores[SUPPLIED] - matching_scores[REVISED] <= 3
        and matching_scores[ORACLE_REVISED] >= 21
        and unrelated_loss <= 2
    )
    harmful = engaged and unrelated_loss >= 4
    verdict_class = "not_engaged" if not engaged else "harmful" if harmful else "revision_candidate" if candidate else "null"
    packet = {
        "attempts": recorder.attempts,
        "calls": calls,
        "components": {
            "counter_actions_contradicting_old_records": counter_contradictions,
            "counter_actions_old_policy_consistent": counter_old_policy,
            "exact_hidden_revision_records": hidden_exact,
            "exact_later_normalizations": exact_normalizations,
            "exact_old_records": old_exact,
            "exact_revised_records": revision_exact,
            "prechange_correct_actions": pre_correct,
        },
        "design_scores": design_scores,
        "direction_scores": direction_scores,
        "every_participant_cell_valid": every_cell_valid,
        "invalid_participant_cells": invalid_participant_cells,
        "formation_verdict": None,
        "logical_calls": len(calls),
        "matching_scores": matching_scores,
        "normalized_selection": selection_score,
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "record_versions": record_versions,
        "hidden_comparator_versions": hidden_comparator_versions,
        "request_distributions": distributions,
        "retries": recorder.retries,
        "revision_verdict": {"class": verdict_class, "scope": "learned_clerical_revision_exploration"},
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "unrelated_loss": unrelated_loss,
        "unrelated_scores": unrelated_scores,
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise RevisionRefusal("retained_specimen_mismatch")
    retained = json.loads((evidence_dir / "packet.json").read_bytes())
    entries = []
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        meta = json.loads(meta_path.read_text())
        entries.append(((evidence_dir / "attempts" / f"{stem}.request.json").read_bytes(), (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes(), meta))
    position = 0
    def transport(body: bytes) -> tuple[int, bytes]:
        nonlocal position
        request, response, meta = entries[position]; position += 1
        if request != body: raise RevisionRefusal("retained_request_mismatch")
        if meta["error"] is not None: raise ConnectionError(meta["error"])
        return meta["http_status"], response
    replayed = execute(transport)
    if position != len(entries) or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained):
        raise RevisionRefusal("evidence_replay_mismatch")
    return replayed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args(argv)
    if not args.live:
        print(json.dumps({"mode": "smoke_no_contact", "planned_logical_calls": PLANNED_LOGICAL_CALLS, "side_effects_entered": False}, sort_keys=True)); return 0
    if args.evidence_dir is None:
        args.evidence_dir = Path("evidence") / f"learned-clerical-revision-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    started = time.monotonic(); receipt = learned.collect_provider_receipt()
    if not receipt["valid"]: raise RevisionRefusal("provider_identity_mismatch")
    packet = execute(base.live_transport, args.evidence_dir)
    (args.evidence_dir / "provider.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    replay_evidence(args.evidence_dir)
    print(json.dumps({"elapsed_seconds": time.monotonic() - started, "evidence_dir": str(args.evidence_dir), "logical_calls": packet["logical_calls"], "physical_attempts": packet["physical_attempts"], "revision_verdict": packet["revision_verdict"]}, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
