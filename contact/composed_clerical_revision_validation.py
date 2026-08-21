"""Run the fresh composed clerical revision validation."""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any, Callable

from contact import canonical_clerical_record_diagnostic as canonical
from contact import clerical_prose_parser_diagnostic as prose_parser
from contact import clerical_selected_effect_projection as projection
from contact import clerical_source_support_verifier as verifier
from contact import distributional_developmental_comparison as base
from contact import learned_clerical_instrument_exploration as learned
from contact import learned_clerical_instrument_validation as validated
from contact import learned_clerical_revision_exploration as revision
from contact import source_grounded_revision_admission as admission
from contact import staged_clerical_instrument_successor as staged
from micro_environment.unselected_lineage_behavior import (
    FIRST_INCREASES,
    SECOND_INCREASES,
    LineageProfile,
    ProposalReceipt,
    apply_committed_action,
)
from unselected_lineage_specimen import oracle_action


PROTOCOL_VERSION = "composed-clerical-revision-validation-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "COMPOSED_CLERICAL_REVISION_VALIDATION.md"
LINEAGES = ("fresh_01", "fresh_02", "fresh_03", "fresh_04")
DESIGN_POSITIONS = revision.DESIGN_POSITIONS
PRE_CASES = revision.PRE_CASES
CASES = learned.CASES

COLD = "cold"
RAW = "raw_counterexperience"
ADMITTED = "composed_admitted_revision"
STALE = "stale_proposal_checked"
HIDDEN = "hidden_proposal_checked"
REMOVED = "admitted_revision_removed"
SUPPLIED = "normalized_selected_supplied_revision"
ORACLE = "environment_selected_clerk_revision"
BRANCHES = (COLD, RAW, ADMITTED, STALE, HIDDEN, REMOVED, SUPPLIED, ORACLE)

REPEATS = 3
PLANNED_LOGICAL_CALLS = 768
PHYSICAL_CALL_CEILING = 780
MAX_RETRIES = 12


class ValidationRefusal(ValueError):
    pass


LINEAGE_DATA = {
    name: revision.make_lineage(name, index)
    for index, name in enumerate(LINEAGES, 1)
}


def projector_body(observed_actuator: str, record: dict[str, str] | None) -> bytes:
    value = {
        "observed_actuator": observed_actuator,
        "proposed_effect_record": record if record is not None else {},
    }
    return learned.canonical_envelope(
        learned.INSTRUMENT_MODEL,
        projection.PROJECTION_SYSTEM,
        f"FIELD PROJECTION REQUEST\n{base.canonical_json_bytes(value).decode()}\n/no_think",
        projection.PROJECTION_SETTINGS,
    )


def admission_decision(
    report: dict[str, str], transcript_text: str,
    record: dict[str, str] | None, projected_effect: str | None,
) -> dict[str, Any]:
    raw_actuator, raw_movement = admission.measurement_values(report)
    transcript = staged.parse_transcription(transcript_text)
    reasons = []
    if raw_actuator is None:
        reasons.append("selected_actuator_missing")
    if raw_movement is None:
        reasons.append("movement_direction_missing")
    if transcript is None:
        reasons.append("sensory_transcription_invalid")
        transcribed_actuator = None
        transcribed_effect = None
    else:
        transcribed_actuator = transcript["observed_actuator"]
        transcribed_effect = transcript["observed_effect"]
        if raw_actuator is not None and transcribed_actuator != raw_actuator:
            reasons.append("transcribed_actuator_mismatch")
        expected_effect = {
            "increased": learned.INCREASES,
            "decreased": learned.DECREASES,
        }.get(raw_movement)
        if expected_effect is not None and transcribed_effect != expected_effect:
            reasons.append("transcribed_effect_mismatch")
    if not admission.structurally_complete(record):
        reasons.append("record_structure_incomplete")
    expected_projection = (
        record.get(f"{transcribed_actuator}_control_effect")
        if type(record) is dict and transcribed_actuator in {"first", "second"}
        else None
    )
    if projected_effect not in {learned.INCREASES, learned.DECREASES}:
        reasons.append("projected_effect_invalid")
    elif projected_effect != expected_projection:
        reasons.append("projected_field_mismatch")
    if (
        projected_effect in {learned.INCREASES, learned.DECREASES}
        and transcribed_effect in {learned.INCREASES, learned.DECREASES}
        and projected_effect != transcribed_effect
    ):
        reasons.append("claimed_effect_mismatch")
    return {
        "reasons": reasons,
        "status": admission.ADMITTED if not reasons else admission.QUARANTINED,
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


def specimen() -> dict[str, Any]:
    return {
        "branches": list(BRANCHES),
        "cases": list(CASES),
        "instrument_model": learned.INSTRUMENT_MODEL,
        "instrument_model_digest": learned.INSTRUMENT_MODEL_DIGEST,
        "lineages": {
            name: {
                "old_sources": {
                    position: learned.public_device(
                        lineage.old_sources[position],
                        lineage.designs[position].source_description,
                    )
                    for position in DESIGN_POSITIONS
                },
                "post_cases": {
                    case_name: {
                        "device": learned.public_device(case.state, case.description),
                        "expected_action": oracle_action(case.state, case.profile),
                        "expected_record_ids": revision.expected_selection(lineage, case_name),
                    }
                    for case_name, case in lineage.post_cases.items()
                },
            }
            for name, lineage in LINEAGE_DATA.items()
        },
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


def execute(
    transport: Transport,
    evidence_dir: Path | None = None,
    *,
    engagement_branches: tuple[str, ...] | None = None,
    verdict_scope: str = "composed_clerical_revision_validation",
) -> dict[str, Any]:
    with configured_recorder():
        recorder = verifier.Recorder(transport, evidence_dir)
        if evidence_dir is not None:
            (evidence_dir / "specimen.json").write_bytes(
                base.canonical_json_bytes(specimen())
            )
        logical_index = 0
        calls = []
        artifacts = {
            name: {
                "old_report": {}, "old_trans": {}, "old_prose": {},
                "old_record": {}, "old_sentence": {},
                "counter_report": {}, "hidden_report": {},
                "revised": {"trans": {}, "prose": {}, "record": {}, "sentence": {}},
                "hidden": {"trans": {}, "prose": {}, "record": {}, "sentence": {}},
                "projection": {"old": {}, "revised": {}, "stale": {}, "hidden": {}},
                "admission": {"old": {}, "revised": {}, "stale": {}, "hidden": {}},
                "static": {},
            }
            for name in LINEAGES
        }

        for name in LINEAGES:
            lineage = LINEAGE_DATA[name]
            for position in DESIGN_POSITIONS:
                state = lineage.old_sources[position]
                logical_index += 1
                body = revision.participant_body(
                    state, lineage.designs[position].source_description, ""
                )
                status, error, content, ca, usage = recorder.call(logical_index, body)
                availability, action = base.parse_action(content, state)
                if status != 200 or error is not None:
                    availability, action = "unavailable", None
                proposal = ProposalReceipt(
                    status == 200 and error is None and ca,
                    (action or content) if status == 200 and error is None and ca else "",
                )
                result = apply_committed_action(
                    state, lineage.old_profiles[position], proposal
                )
                artifacts[name]["old_report"][position] = learned.sensor_report(
                    lineage.designs[position], result
                )
                calls.append({
                    "responsibility": "old_source_action", "lineage": name,
                    "design_position": position, "availability": availability,
                    "action": action, "external_result": base.exposed_result(result),
                    "provider_usage": usage, "request_sha256": base.sha256(body),
                })

        for phase in ("trans", "prose", "parse"):
            for name in LINEAGES:
                lineage = LINEAGE_DATA[name]
                for position in DESIGN_POSITIONS:
                    logical_index += 1
                    if phase == "trans":
                        body = staged.transcription_body(artifacts[name]["old_report"][position])
                    elif phase == "prose":
                        body = staged.sentence_body(artifacts[name]["old_trans"][position])
                    else:
                        body = prose_parser.parser_body(artifacts[name]["old_prose"][position])
                    content, ok, usage = available(recorder.call(logical_index, body))
                    expected = canonical.expected_record(lineage.designs[position])
                    if phase == "trans":
                        parsed = staged.parse_transcription(content) if ok else None
                        expected_value = staged.expected_transcription(
                            lineage.designs[position],
                            validated.report_view(artifacts[name]["old_report"][position]),
                        )
                        artifacts[name]["old_trans"][position] = content
                        exact = parsed == expected_value
                        responsibility = "old_transcription"
                        rendered_exact = None
                    elif phase == "prose":
                        artifacts[name]["old_prose"][position] = content
                        exact = prose_parser.parse_explicit_sentence(content) == expected
                        responsibility = "old_explicit_prose"
                        rendered_exact = None
                    else:
                        record = canonical.parse_record(content) if ok else None
                        sentence = canonical.render_sentence(record)
                        artifacts[name]["old_record"][position] = record
                        artifacts[name]["old_sentence"][position] = sentence
                        exact = record == expected
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
            material = artifacts[name]["old_sentence"][case.design_position]
            logical_index += 1
            body = revision.participant_body(case.state, case.description, material)
            status, error, content, ca, usage = recorder.call(logical_index, body)
            availability, action = base.parse_action(content, case.state)
            if status != 200 or error is not None:
                availability, action = "unavailable", None
            row = {
                "responsibility": "prechange_action", "lineage": name,
                "case": case_name, "repeat": repeat, "availability": availability,
                "action": action,
                "correct_action": availability == "available"
                and action == oracle_action(case.state, case.profile),
                "provider_usage": usage, "request_sha256": base.sha256(body),
            }
            pre_rows.append(row); calls.append(row)

        counter_old_policy = 0
        counter_contradictions = 0
        for name in LINEAGES:
            lineage = LINEAGE_DATA[name]
            for position in DESIGN_POSITIONS:
                state = lineage.counter_sources[position]
                material = artifacts[name]["old_sentence"][position]
                logical_index += 1
                body = revision.participant_body(
                    state, lineage.designs[position].source_description, material
                )
                status, error, content, ca, usage = recorder.call(logical_index, body)
                availability, action = base.parse_action(content, state)
                if status != 200 or error is not None:
                    availability, action = "unavailable", None
                proposal = ProposalReceipt(
                    status == 200 and error is None and ca,
                    (action or content) if status == 200 and error is None and ca else "",
                )
                result = apply_committed_action(
                    state, lineage.counter_profiles[position], proposal
                )
                old_profile = LineageProfile(
                    state.controller_family, lineage.designs[position].increasing_slot
                )
                old_consistent = availability == "available" and action == oracle_action(state, old_profile)
                counter_old_policy += old_consistent
                selected = getattr(result, "selected_slot", None)
                old_movement = (
                    "increased"
                    if (selected == "first")
                    == (lineage.designs[position].increasing_slot == FIRST_INCREASES)
                    else "decreased"
                ) if selected in {"first", "second"} else None
                contradicts = old_movement is not None and getattr(result, "movement_direction", None) not in {None, old_movement}
                counter_contradictions += contradicts
                report = learned.sensor_report(lineage.designs[position], result)
                artifacts[name]["counter_report"][position] = report
                artifacts[name]["hidden_report"][position] = validated.hidden_report(report)
                new_design = revision.design_with_slot(
                    lineage.designs[position], lineage.counter_profiles[position].increasing_slot
                )
                artifacts[name]["static"][position] = staged.expected_sentence(new_design)
                calls.append({
                    "responsibility": "counter_action", "lineage": name,
                    "design_position": position, "availability": availability,
                    "action": action, "old_policy_consistent": old_consistent,
                    "contradicts_old_record": contradicts,
                    "external_result": base.exposed_result(result),
                    "provider_usage": usage, "request_sha256": base.sha256(body),
                })

        for condition in ("revised", "hidden"):
            report_key = "counter_report" if condition == "revised" else "hidden_report"
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
                        new_design = revision.design_with_slot(
                            lineage.designs[position], lineage.counter_profiles[position].increasing_slot
                        )
                        expected = canonical.expected_record(new_design)
                        if phase == "trans":
                            parsed = staged.parse_transcription(content) if ok else None
                            expected_value = staged.expected_transcription(
                                new_design, validated.report_view(artifacts[name][report_key][position])
                            )
                            artifacts[name][condition]["trans"][position] = content
                            exact = parsed == expected_value
                            responsibility = "revision_transcription"
                            rendered_exact = None
                        elif phase == "prose":
                            artifacts[name][condition]["prose"][position] = content
                            exact = prose_parser.parse_explicit_sentence(content) == expected
                            responsibility = "revision_explicit_prose"
                            rendered_exact = None
                        else:
                            record = canonical.parse_record(content) if ok else None
                            sentence = canonical.render_sentence(record)
                            artifacts[name][condition]["record"][position] = record
                            artifacts[name][condition]["sentence"][position] = sentence
                            exact = record == expected
                            rendered_exact = sentence == staged.expected_sentence(new_design)
                            responsibility = "revision_prose_parse"
                        calls.append({
                            "responsibility": responsibility, "lineage": name,
                            "design_position": position, "condition": condition,
                            "available": ok, "exact": exact,
                            "rendered_exact": rendered_exact, "content": content,
                            "provider_usage": usage, "request_sha256": base.sha256(body),
                        })

        proposal_sources = {
            "old": ("old_report", "old_trans", "old_record"),
            "revised": ("counter_report", "revised", "revised"),
            "stale": ("counter_report", "revised", "old_record"),
            "hidden": ("hidden_report", "hidden", "hidden"),
        }
        for proposal_kind, (report_key, transcript_key, record_key) in proposal_sources.items():
            for name in LINEAGES:
                for position in DESIGN_POSITIONS:
                    transcript = (
                        artifacts[name][transcript_key][position]
                        if transcript_key == "old_trans"
                        else artifacts[name][transcript_key]["trans"][position]
                    )
                    record = (
                        artifacts[name][record_key][position]
                        if record_key == "old_record"
                        else artifacts[name][record_key]["record"][position]
                    )
                    parsed_transcript = staged.parse_transcription(transcript)
                    observed_actuator = (
                        parsed_transcript["observed_actuator"]
                        if parsed_transcript is not None else "unavailable"
                    )
                    logical_index += 1
                    body = projector_body(observed_actuator, record)
                    content, ok, usage = available(recorder.call(logical_index, body))
                    availability, projected = projection.parse_effect(content)
                    if not ok:
                        availability, projected = "unavailable", None
                    decision = admission_decision(
                        artifacts[name][report_key][position], transcript, record, projected
                    )
                    artifacts[name]["projection"][proposal_kind][position] = projected
                    artifacts[name]["admission"][proposal_kind][position] = decision
                    expected_projection = (
                        record.get(f"{observed_actuator}_control_effect")
                        if type(record) is dict and observed_actuator in {"first", "second"}
                        else None
                    )
                    calls.append({
                        "responsibility": "selected_effect_projection", "lineage": name,
                        "design_position": position, "proposal_kind": proposal_kind,
                        "availability": availability, "content": content,
                        "projected_effect": projected,
                        "projection_exact": projected == expected_projection,
                        "admission_status": decision["status"],
                        "admission_reasons": decision["reasons"],
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
                    "case": case_name, "available": ok, "content": content,
                    "normalized_scope": scope, "expected_scope": case.scope,
                    "exact": scope == case.scope,
                    "provider_usage": usage, "request_sha256": base.sha256(body),
                })

        selections = {name: {} for name in LINEAGES}
        for name in LINEAGES:
            lineage = LINEAGE_DATA[name]
            scopes = {
                position: revision.source_scope(artifacts[name]["revised"]["trans"][position])
                for position in DESIGN_POSITIONS
            }
            for case_name in CASES:
                selections[name][case_name] = revision.exact_match(
                    lineage, normalizations[name][case_name], scopes
                )

        def material_for(name: str, case_name: str, branch: str) -> str:
            lineage = LINEAGE_DATA[name]
            selected = selections[name][case_name]
            if branch == COLD:
                return ""
            if branch == RAW:
                return revision.raw_material(artifacts[name]["counter_report"])
            if branch == SUPPLIED:
                return revision.selected_sentence(lineage, artifacts[name]["static"], selected)
            if branch == ORACLE:
                return revision.selected_sentence(
                    lineage, artifacts[name]["revised"]["sentence"],
                    revision.expected_selection(lineage, case_name),
                )
            sentences = {}
            for position in DESIGN_POSITIONS:
                old = artifacts[name]["old_sentence"][position]
                if branch == ADMITTED:
                    decision = artifacts[name]["admission"]["revised"][position]
                    candidate = artifacts[name]["revised"]["sentence"][position]
                elif branch == HIDDEN:
                    decision = artifacts[name]["admission"]["hidden"][position]
                    candidate = artifacts[name]["hidden"]["sentence"][position]
                elif branch == STALE:
                    decision = artifacts[name]["admission"]["stale"][position]
                    candidate = artifacts[name]["old_sentence"][position]
                elif branch == REMOVED:
                    decision = {"status": admission.QUARANTINED}
                    candidate = ""
                else:
                    raise AssertionError(branch)
                sentences[position] = candidate if decision["status"] == admission.ADMITTED else old
            return revision.selected_sentence(lineage, sentences, selected)

        post_rows = []
        for repeat, name, case_name, branch in post_schedule():
            lineage = LINEAGE_DATA[name]
            case = lineage.post_cases[case_name]
            material = material_for(name, case_name, branch)
            logical_index += 1
            body = revision.participant_body(case.state, case.description, material)
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
                "availability": availability, "action": action,
                "correct_action": availability == "available"
                and action == oracle_action(case.state, case.profile),
                "external_result": base.exposed_result(result),
                "retained_material_sha256": base.sha256(material.encode()),
                "provider_usage": usage, "request_sha256": base.sha256(body),
            }
            post_rows.append(row); calls.append(row)

    if logical_index != PLANNED_LOGICAL_CALLS or len(calls) != PLANNED_LOGICAL_CALLS:
        raise ValidationRefusal("logical_call_count_mismatch")

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
    matching_scores = {branch: total(branch, matching) for branch in BRANCHES}
    unrelated_scores = {branch: total(branch, unrelated) for branch in BRANCHES}
    design_scores = {branch: {"a": total(branch, ("a_up", "a_down")), "b": total(branch, ("b_up", "b_down"))} for branch in BRANCHES}
    direction_scores = {branch: {"up": total(branch, ("a_up", "b_up")), "down": total(branch, ("a_down", "b_down"))} for branch in BRANCHES}
    invalid_cells = []
    for branch in BRANCHES:
        for case_name in CASES:
            for name in LINEAGES:
                invalid = sum(
                    row["availability"] != "available" for row in post_rows
                    if row["branch"] == branch and row["case"] == case_name and row["lineage"] == name
                )
                if invalid > 1:
                    invalid_cells.append({"branch": branch, "case": case_name, "lineage": name, "invalid": invalid})
    every_cell_valid = not invalid_cells
    engagement_invalid_cells = (
        invalid_cells
        if engagement_branches is None
        else [row for row in invalid_cells if row["branch"] in engagement_branches]
    )
    every_engagement_cell_valid = not engagement_invalid_cells
    old_exact = sum(r["exact"] and r.get("rendered_exact") for r in calls if r["responsibility"] == "old_prose_parse")
    revised_exact = sum(r["exact"] and r.get("rendered_exact") for r in calls if r["responsibility"] == "revision_prose_parse" and r["condition"] == "revised")
    projection_rows = [r for r in calls if r["responsibility"] == "selected_effect_projection"]
    projection_exact = sum(r["projection_exact"] for r in projection_rows if r["proposal_kind"] == "revised")
    admission_counts = {
        kind: {
            "admitted": sum(r["admission_status"] == admission.ADMITTED for r in projection_rows if r["proposal_kind"] == kind),
            "quarantined": sum(r["admission_status"] == admission.QUARANTINED for r in projection_rows if r["proposal_kind"] == kind),
        }
        for kind in ("old", "revised", "stale", "hidden")
    }
    normal_exact = sum(r["exact"] for r in calls if r["responsibility"] == "later_scope_normalization")
    selection_rows = [
        (selections[name][case], revision.expected_selection(LINEAGE_DATA[name], case))
        for name in LINEAGES for case in CASES
    ]
    selection_score = {
        "exact": sum(actual == expected for actual, expected in selection_rows),
        "false_selections": sum(not expected and bool(actual) for actual, expected in selection_rows),
        "total": len(selection_rows),
    }
    pre_correct = sum(r["correct_action"] for r in pre_rows)
    engaged = (
        matching_scores[SUPPLIED] >= 43
        and all(score >= 21 for score in design_scores[SUPPLIED].values())
        and all(score >= 21 for score in direction_scores[SUPPLIED].values())
        and every_engagement_cell_valid
    )
    unrelated_loss = unrelated_scores[COLD] - unrelated_scores[ADMITTED]
    supported = (
        engaged and old_exact >= 7 and pre_correct >= 43
        and counter_old_policy == 8 and counter_contradictions == 8
        and revised_exact >= 7 and projection_exact >= 7
        and admission_counts["old"]["admitted"] == 8
        and admission_counts["revised"]["admitted"] == 8
        and admission_counts["stale"]["quarantined"] == 8
        and admission_counts["hidden"]["quarantined"] == 8
        and normal_exact >= 20 and selection_score["exact"] >= 20
        and selection_score["false_selections"] <= 2
        and matching_scores[ADMITTED] >= 43
        and all(score >= 21 for score in design_scores[ADMITTED].values())
        and all(score >= 21 for score in direction_scores[ADMITTED].values())
        and all(matching_scores[ADMITTED] - matching_scores[branch] >= 16 for branch in (COLD, RAW, STALE, HIDDEN, REMOVED))
        and matching_scores[SUPPLIED] - matching_scores[ADMITTED] <= 4
        and matching_scores[ORACLE] >= 43 and unrelated_loss <= 3
    )
    harmful = engaged and unrelated_loss >= 6
    verdict_class = "not_engaged" if not engaged else "harmful" if harmful else "supported" if supported else "null"
    proposals = {
        name: {
            position: {
                kind: {
                    "admission_reasons": artifacts[name]["admission"][kind][position]["reasons"],
                    "admission_status": artifacts[name]["admission"][kind][position]["status"],
                    "projected_effect": artifacts[name]["projection"][kind][position],
                    "proposed_record": (
                        artifacts[name]["old_record"][position]
                        if kind in {"old", "stale"}
                        else artifacts[name][kind]["record"][position]
                    ),
                    "source_report_sha256": base.sha256(base.canonical_json_bytes(
                        artifacts[name][
                            "old_report" if kind == "old"
                            else "hidden_report" if kind == "hidden"
                            else "counter_report"
                        ][position]
                    )),
                    "source_transcription_sha256": base.sha256((
                        artifacts[name]["old_trans"][position]
                        if kind == "old"
                        else artifacts[name]["hidden" if kind == "hidden" else "revised"]["trans"][position]
                    ).encode()),
                    "version": 1 if kind == "old" else 2,
                }
                for kind in ("old", "revised", "stale", "hidden")
            }
            for position in DESIGN_POSITIONS
        }
        for name in LINEAGES
    }
    packet = {
        "admission_counts": admission_counts,
        "attempts": recorder.attempts,
        "calls": calls,
        "components": {
            "counter_actions_contradicting_old_records": counter_contradictions,
            "counter_actions_old_policy_consistent": counter_old_policy,
            "exact_later_normalizations": normal_exact,
            "exact_old_records": old_exact,
            "exact_revised_projections": projection_exact,
            "exact_revised_records": revised_exact,
            "prechange_correct_actions": pre_correct,
        },
        "design_scores": design_scores,
        "direction_scores": direction_scores,
        "formation_verdict": None,
        "invalid_participant_cells": invalid_cells,
        "logical_calls": len(calls),
        "matching_scores": matching_scores,
        "normalized_selection": selection_score,
        "physical_attempts": recorder.physical,
        "proposals": proposals,
        "protocol_version": PROTOCOL_VERSION,
        "request_distributions": distributions,
        "retries": recorder.retries,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "unrelated_loss": unrelated_loss,
        "unrelated_scores": unrelated_scores,
        "validation_verdict": {"class": verdict_class, "scope": verdict_scope},
    }
    if engagement_branches is not None:
        packet["engagement_participant_branches"] = list(engagement_branches)
        packet["engagement_invalid_participant_cells"] = engagement_invalid_cells
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
        entries.append(((evidence_dir / "attempts" / f"{stem}.request.json").read_bytes(), (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes(), json.loads(meta_path.read_text())))
    position = 0
    def transport(body: bytes) -> tuple[int, bytes]:
        nonlocal position
        request, response, meta = entries[position]; position += 1
        if request != body: raise ValidationRefusal("retained_request_mismatch")
        if meta["error"] is not None: raise ConnectionError(meta["error"])
        return meta["http_status"], response
    replayed = execute(transport)
    if position != len(entries) or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained):
        raise ValidationRefusal("evidence_replay_mismatch")
    return replayed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args(argv)
    if not args.live:
        print(json.dumps({"mode": "smoke_no_contact", "planned_logical_calls": PLANNED_LOGICAL_CALLS, "side_effects_entered": False}, sort_keys=True)); return 0
    evidence_dir = args.evidence_dir or Path("evidence") / ("composed-clerical-revision-validation-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    receipt = learned.collect_provider_receipt()
    if not receipt["valid"]: raise ValidationRefusal("provider_identity_mismatch")
    started = time.monotonic()
    packet = execute(base.live_transport, evidence_dir)
    (evidence_dir / "provider.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    replay_evidence(evidence_dir)
    print(json.dumps({"elapsed_seconds": time.monotonic() - started, "evidence_dir": str(evidence_dir), "logical_calls": packet["logical_calls"], "physical_attempts": packet["physical_attempts"], "validation_verdict": packet["validation_verdict"]}, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
