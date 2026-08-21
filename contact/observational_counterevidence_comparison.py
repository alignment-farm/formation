"""Compare observation-grounded and action-attributed revision governors."""

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
from contact import learned_clerical_instrument_validation as learned_validation
from contact import learned_clerical_revision_exploration as revision
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


PROTOCOL_VERSION = "observational-counterevidence-comparison-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "OBSERVATIONAL_COUNTEREVIDENCE_COMPARISON.md"
PARENT_PACKET_SHA256 = longer.PARENT_PACKET_SHA256
PARENT_LINEAGES = longer.PARENT_LINEAGES
LINEAGES = longer.LINEAGES
DESIGN_POSITIONS = longer.DESIGN_POSITIONS
CASES = longer.CASES
ORIGINS = ("target_directed", "explicit_exploration")

COLD = "cold"
RAW = "raw_exploratory_occurrence"
OBS_GUIDED = "observation_governor_target_directed"
ATTR_GUIDED = "attribution_governor_target_directed"
OBS_EXPLORE = "observation_governor_exploration"
ATTR_EXPLORE = "attribution_governor_exploration"
REMOVED = "exploratory_revision_removed"
SUPPLIED = "normalized_selected_supplied_catalog"
BRANCHES = (
    COLD, RAW, OBS_GUIDED, ATTR_GUIDED, OBS_EXPLORE, ATTR_EXPLORE,
    REMOVED, SUPPLIED,
)
ENGAGEMENT_BRANCHES = (SUPPLIED, OBS_EXPLORE)

REPEATS = 3
PLANNED_LOGICAL_CALLS = 636
PHYSICAL_CALL_CEILING = 648
MAX_RETRIES = 12


class ObservationalRefusal(ValueError):
    pass


@dataclass(frozen=True)
class ComparisonLineage:
    source_state: LineageState
    source_profile: LineageProfile
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


def surface_description(scope: dict[str, str]) -> str:
    return (
        f"The enclosure shows {longer.HOUSING_WORDS[scope['housing_class']]}; "
        f"its signal light appears {longer.BEACON_WORDS[scope['beacon_class']]} ."
    ).replace(" .", ".")


def make_lineage(name: str, index: int) -> ComparisonLineage:
    parent = PARENT_LINEAGES[name]
    source_profile = LineageProfile(
        opaque(f"{name}:a:comparison-source-family"),
        parent.old_profiles["a"].increasing_slot,
    )
    position = 51100 + index * 521
    source_state = state(
        f"{name}:a:comparison-source",
        position,
        position + (1 if index % 2 else -1),
        source_profile,
    )
    post_cases = {}
    for case_index, case_name in enumerate(CASES, 1):
        if case_name.startswith(("a_", "b_")):
            design_position = case_name[0]
            design = parent.designs[design_position]
            scope = {"beacon_class": design.beacon, "housing_class": design.housing}
            increasing_slot = (
                parent.old_profiles["a"].increasing_slot
                if design_position == "a"
                else parent.counter_profiles["b"].increasing_slot
            )
        elif case_name == "novel_up":
            design_position = None
            scope = (
                {"beacon_class": "green", "housing_class": "smooth"}
                if index in {1, 4} else
                {"beacon_class": "red", "housing_class": "dimpled"}
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
            opaque(f"{name}:{case_name}:comparison-post-family"), increasing_slot
        )
        current = 53100 + index * 523 + case_index * 113
        post_cases[case_name] = revision.Case(
            state(
                f"{name}:{case_name}:comparison-post",
                current,
                current + (1 if case_name.endswith("up") else -1),
                profile,
            ),
            profile,
            surface_description(scope),
            scope,
            design_position,
        )
    return ComparisonLineage(source_state, source_profile, post_cases)


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


def recommended_action(state_value: LineageState, record: dict[str, str]) -> str | None:
    wants = "increases_position" if state_value.target > state_value.position else "decreases_position"
    for index, slot in enumerate(("first", "second")):
        if record.get(f"{slot}_control_effect") == wants:
            return state_value.controls[index]
    return None


def selected_claim(record: dict[str, str], state_value: LineageState, action: str | None) -> str | None:
    if action == state_value.controls[0]:
        return record.get("first_control_effect")
    if action == state_value.controls[1]:
        return record.get("second_control_effect")
    return None


def claim_contradicted(claim: str | None, movement: str | None) -> bool:
    return {
        "increases_position": "increased",
        "decreases_position": "decreased",
    }.get(claim) not in {None, movement}


def specimen() -> dict[str, Any]:
    _, parent = longer.load_parent()
    return {
        "branches": list(BRANCHES),
        "cases": list(CASES),
        "engagement_branches": list(ENGAGEMENT_BRANCHES),
        "instrument_model": learned.INSTRUMENT_MODEL,
        "instrument_model_digest": learned.INSTRUMENT_MODEL_DIGEST,
        "lineages": {
            name: {
                "parent_v2": {
                    position: {
                        key: parent[name][position][key]
                        for key in (
                            "record", "source_report_sha256",
                            "source_transcription_sha256", "version",
                        )
                    }
                    for position in DESIGN_POSITIONS
                },
                "source": learned.public_device(
                    LINEAGE_DATA[name].source_state,
                    PARENT_LINEAGES[name].designs["a"].source_description,
                ),
                "exploration_action": LINEAGE_DATA[name].source_state.controls[0],
                "post_cases": {
                    case_name: {
                        "device": learned.public_device(case.state, case.description),
                        "expected_action": oracle_action(case.state, case.profile),
                        "scope_role": case.design_position,
                    }
                    for case_name, case in LINEAGE_DATA[name].post_cases.items()
                },
            }
            for name in LINEAGES
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
            (evidence_dir / "specimen.json").write_bytes(base.canonical_json_bytes(specimen()))
        logical_index = 0
        calls = []
        occurrences = []
        artifacts = {
            name: {
                origin: {
                    "report": None,
                    "trans": "",
                    "prose": "",
                    "record": None,
                    "sentence": "",
                    "projection": None,
                    "composed": None,
                    "observation_governor": None,
                    "attribution_governor": None,
                    "action_attributed": False,
                    "claim_contradicted": False,
                }
                for origin in ORIGINS
            }
            for name in LINEAGES
        }

        for name in LINEAGES:
            lineage = PARENT_LINEAGES[name]
            comparison = LINEAGE_DATA[name]
            state_value = comparison.source_state
            current_record = parent[name]["a"]["record"]
            material = parent[name]["a"]["sentence"]
            logical_index += 1
            body = revision.participant_body(
                state_value, lineage.designs["a"].source_description, material
            )
            status, error, content, ca, usage = recorder.call(logical_index, body)
            availability, action = base.parse_action(content, state_value)
            if status != 200 or error is not None:
                availability, action = "unavailable", None
            source_actions = {
                "target_directed": {
                    "action": action,
                    "availability": availability,
                    "provider_usage": usage,
                    "request_sha256": base.sha256(body),
                },
                "explicit_exploration": {
                    "action": state_value.controls[0],
                    "availability": "available",
                    "provider_usage": None,
                    "request_sha256": None,
                },
            }
            for origin, source_action in source_actions.items():
                committed = source_action["action"]
                proposal = ProposalReceipt(
                    source_action["availability"] == "available",
                    committed or "",
                )
                result = apply_committed_action(
                    state_value, comparison.source_profile, proposal
                )
                claim = selected_claim(current_record, state_value, committed)
                contradicted = claim_contradicted(
                    claim, getattr(result, "movement_direction", None)
                )
                attributed = (
                    origin == "target_directed"
                    and committed == recommended_action(state_value, current_record)
                )
                report = learned.sensor_report(lineage.designs["a"], result)
                artifacts[name][origin]["report"] = report
                artifacts[name][origin]["action_attributed"] = attributed
                artifacts[name][origin]["claim_contradicted"] = contradicted
                row = {
                    "responsibility": "source_occurrence",
                    "lineage": name,
                    "origin": origin,
                    "availability": source_action["availability"],
                    "action": committed,
                    "action_attributed": attributed,
                    "claim_contradicted": contradicted,
                    "current_selected_effect_claim": claim,
                    "external_result": base.exposed_result(result),
                    "provider_usage": source_action["provider_usage"],
                    "request_sha256": source_action["request_sha256"],
                }
                occurrences.append(row)
                if origin == "target_directed":
                    calls.append(row)

        for phase in ("trans", "prose", "parse"):
            for origin in ORIGINS:
                for name in LINEAGES:
                    lineage = PARENT_LINEAGES[name]
                    artifact = artifacts[name][origin]
                    logical_index += 1
                    if phase == "trans":
                        body = staged.transcription_body(artifact["report"])
                    elif phase == "prose":
                        body = staged.sentence_body(artifact["trans"])
                    else:
                        body = prose_parser.parser_body(artifact["prose"])
                    content, ok, usage = available(recorder.call(logical_index, body))
                    expected_record = canonical.expected_record(lineage.designs["a"])
                    if phase == "trans":
                        parsed = staged.parse_transcription(content) if ok else None
                        expected = staged.expected_transcription(
                            lineage.designs["a"],
                            learned_validation.report_view(artifact["report"]),
                        )
                        artifact["trans"] = content
                        exact = parsed == expected
                        responsibility = "source_transcription"
                        rendered_exact = None
                    elif phase == "prose":
                        artifact["prose"] = content
                        exact = prose_parser.parse_explicit_sentence(content) == expected_record
                        responsibility = "source_explicit_prose"
                        rendered_exact = None
                    else:
                        record = canonical.parse_record(content) if ok else None
                        sentence = canonical.render_sentence(record)
                        artifact["record"] = record
                        artifact["sentence"] = sentence
                        exact = record == expected_record
                        rendered_exact = sentence == staged.expected_sentence(lineage.designs["a"])
                        responsibility = "source_prose_parse"
                    calls.append({
                        "responsibility": responsibility,
                        "lineage": name,
                        "origin": origin,
                        "available": ok,
                        "exact": exact,
                        "rendered_exact": rendered_exact,
                        "content": content,
                        "provider_usage": usage,
                        "request_sha256": base.sha256(body),
                    })

        for origin in ORIGINS:
            for name in LINEAGES:
                artifact = artifacts[name][origin]
                parsed_transcript = staged.parse_transcription(artifact["trans"])
                observed_actuator = (
                    parsed_transcript["observed_actuator"]
                    if parsed_transcript is not None else "unavailable"
                )
                logical_index += 1
                body = validation.projector_body(observed_actuator, artifact["record"])
                content, ok, usage = available(recorder.call(logical_index, body))
                availability, projected = validation.projection.parse_effect(content)
                if not ok:
                    availability, projected = "unavailable", None
                composed = validation.admission_decision(
                    artifact["report"], artifact["trans"], artifact["record"], projected
                )
                observation_admitted = (
                    composed["status"] == admission.ADMITTED
                    and artifact["claim_contradicted"]
                )
                attribution_admitted = (
                    observation_admitted and artifact["action_attributed"]
                )
                artifact["projection"] = projected
                artifact["composed"] = composed
                artifact["observation_governor"] = (
                    admission.ADMITTED if observation_admitted else admission.QUARANTINED
                )
                artifact["attribution_governor"] = (
                    admission.ADMITTED if attribution_admitted else admission.QUARANTINED
                )
                expected_projection = (
                    artifact["record"].get(f"{observed_actuator}_control_effect")
                    if type(artifact["record"]) is dict
                    and observed_actuator in {"first", "second"}
                    else None
                )
                calls.append({
                    "responsibility": "source_selected_effect_projection",
                    "lineage": name,
                    "origin": origin,
                    "availability": availability,
                    "content": content,
                    "projected_effect": projected,
                    "projection_exact": projected == expected_projection,
                    "composed_status": composed["status"],
                    "composed_reasons": composed["reasons"],
                    "observation_governor": artifact["observation_governor"],
                    "attribution_governor": artifact["attribution_governor"],
                    "provider_usage": usage,
                    "request_sha256": base.sha256(body),
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
                    "responsibility": "comparison_scope_normalization",
                    "lineage": name,
                    "case": case_name,
                    "available": ok,
                    "content": content,
                    "normalized_scope": scope,
                    "expected_scope": case.scope,
                    "exact": scope == case.scope,
                    "provider_usage": usage,
                    "request_sha256": base.sha256(body),
                })

        selections = {name: {} for name in LINEAGES}
        for name in LINEAGES:
            scopes = {
                "a": revision.source_scope(artifacts[name]["explicit_exploration"]["trans"]),
                "b": revision.source_scope(parent[name]["b"]["transcription"]),
            }
            lineage = PARENT_LINEAGES[name]
            for case_name in CASES:
                current_scope = normalizations[name][case_name]
                selections[name][case_name] = [
                    lineage.record_ids[position]
                    for position in DESIGN_POSITIONS
                    if scopes[position] is not None and scopes[position] == current_scope
                ] if current_scope is not None else []

        def selected_material(
            name: str,
            case_name: str,
            a_sentence: str,
            a_version: int,
        ) -> tuple[str, dict[str, int]]:
            selected = selections[name][case_name]
            lineage = PARENT_LINEAGES[name]
            sentences = {"a": a_sentence, "b": parent[name]["b"]["sentence"]}
            versions = {"a": a_version, "b": 2}
            positions = [
                position for position in DESIGN_POSITIONS
                if lineage.record_ids[position] in selected
            ]
            return (
                "\n".join(sentences[position] for position in positions if sentences[position]),
                {position: versions[position] for position in positions if sentences[position]},
            )

        def governed_material(
            name: str,
            case_name: str,
            origin: str,
            governor: str,
        ) -> tuple[str, dict[str, int]]:
            artifact = artifacts[name][origin]
            status = artifact[governor]
            if status == admission.ADMITTED:
                return selected_material(name, case_name, artifact["sentence"], 3)
            return selected_material(name, case_name, parent[name]["a"]["sentence"], 2)

        def material_for(name: str, case_name: str, branch: str) -> tuple[str, dict[str, int]]:
            if branch == COLD:
                return "", {}
            if branch == RAW:
                return base.canonical_json_bytes({
                    "raw_exploratory_occurrence": [
                        artifacts[name]["explicit_exploration"]["report"]
                    ]
                }).decode(), {}
            if branch == OBS_GUIDED:
                return governed_material(
                    name, case_name, "target_directed", "observation_governor"
                )
            if branch == ATTR_GUIDED:
                return governed_material(
                    name, case_name, "target_directed", "attribution_governor"
                )
            if branch == OBS_EXPLORE:
                return governed_material(
                    name, case_name, "explicit_exploration", "observation_governor"
                )
            if branch == ATTR_EXPLORE:
                return governed_material(
                    name, case_name, "explicit_exploration", "attribution_governor"
                )
            if branch == REMOVED:
                return selected_material(
                    name, case_name, parent[name]["a"]["sentence"], 2
                )
            if branch == SUPPLIED:
                lineage = PARENT_LINEAGES[name]
                return selected_material(
                    name, case_name, staged.expected_sentence(lineage.designs["a"]), 3
                )
            raise AssertionError(branch)

        post_rows = []
        for repeat, name, case_name, branch in post_schedule():
            case = LINEAGE_DATA[name].post_cases[case_name]
            material, versions = material_for(name, case_name, branch)
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
                "responsibility": "comparison_action",
                "lineage": name,
                "case": case_name,
                "branch": branch,
                "repeat": repeat,
                "availability": availability,
                "action": action,
                "correct_action": availability == "available"
                and action == oracle_action(case.state, case.profile),
                "external_result": base.exposed_result(result),
                "retained_material_sha256": base.sha256(material.encode()),
                "selected_versions": versions,
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
            }
            post_rows.append(row)
            calls.append(row)

    if logical_index != PLANNED_LOGICAL_CALLS or len(calls) != PLANNED_LOGICAL_CALLS:
        raise ObservationalRefusal("logical_call_count_mismatch")

    distributions = {
        branch: {
            case_name: {
                "assigned": len(cell := [
                    row for row in post_rows
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
    matching = ("a_up", "a_down", "b_up", "b_down")
    unrelated = ("novel_up", "recombined_down")

    def total(branch: str, cases: tuple[str, ...]) -> int:
        return sum(distributions[branch][case]["correct_actions"] for case in cases)

    matching_scores = {branch: total(branch, matching) for branch in BRANCHES}
    unrelated_scores = {branch: total(branch, unrelated) for branch in BRANCHES}
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
    invalid_cells = []
    for branch in BRANCHES:
        for case_name in CASES:
            for name in LINEAGES:
                invalid = sum(
                    row["availability"] != "available" for row in post_rows
                    if row["branch"] == branch
                    and row["case"] == case_name
                    and row["lineage"] == name
                )
                if invalid > 1:
                    invalid_cells.append({
                        "branch": branch,
                        "case": case_name,
                        "lineage": name,
                        "invalid": invalid,
                    })
    engagement_invalid = [
        row for row in invalid_cells if row["branch"] in ENGAGEMENT_BRANCHES
    ]
    projection_rows = [
        row for row in calls
        if row["responsibility"] == "source_selected_effect_projection"
    ]
    exact_records = {
        origin: sum(
            row["exact"] and row.get("rendered_exact")
            for row in calls
            if row["responsibility"] == "source_prose_parse"
            and row["origin"] == origin
        )
        for origin in ORIGINS
    }
    exact_projections = {
        origin: sum(
            row["projection_exact"] for row in projection_rows
            if row["origin"] == origin
        )
        for origin in ORIGINS
    }
    composed_admissions = {
        origin: sum(
            row["composed_status"] == admission.ADMITTED
            for row in projection_rows if row["origin"] == origin
        )
        for origin in ORIGINS
    }
    governor_counts = {
        origin: {
            "observation_admitted": sum(
                artifacts[name][origin]["observation_governor"] == admission.ADMITTED
                for name in LINEAGES
            ),
            "attribution_admitted": sum(
                artifacts[name][origin]["attribution_governor"] == admission.ADMITTED
                for name in LINEAGES
            ),
        }
        for origin in ORIGINS
    }
    equal_records = sum(
        artifacts[name]["target_directed"]["record"]
        == artifacts[name]["explicit_exploration"]["record"]
        for name in LINEAGES
    )
    exploration_occurrences = [
        row for row in occurrences if row["origin"] == "explicit_exploration"
    ]
    exploration_actions_exact = sum(
        row["action"] == LINEAGE_DATA[row["lineage"]].source_state.controls[0]
        for row in exploration_occurrences
    )
    exploration_contradictions = sum(
        row["claim_contradicted"] for row in exploration_occurrences
    )
    normal_exact = sum(
        row["exact"] for row in calls
        if row["responsibility"] == "comparison_scope_normalization"
    )
    selection_pairs = [
        (
            selections[name][case_name],
            [PARENT_LINEAGES[name].record_ids[position]] if position else [],
        )
        for name in LINEAGES
        for case_name in CASES
        for position in [LINEAGE_DATA[name].post_cases[case_name].design_position]
    ]
    selection_score = {
        "exact": sum(actual == expected for actual, expected in selection_pairs),
        "false_selections": sum(not expected and bool(actual) for actual, expected in selection_pairs),
        "total": len(selection_pairs),
    }
    assignment_exact = 0
    for row in post_rows:
        position = LINEAGE_DATA[row["lineage"]].post_cases[row["case"]].design_position
        if row["branch"] in {COLD, RAW} or position is None:
            expected = {}
        elif position == "b":
            expected = {"b": 2}
        elif row["branch"] in {OBS_EXPLORE, SUPPLIED}:
            expected = {"a": 3}
        elif row["branch"] in {ATTR_EXPLORE, REMOVED}:
            expected = {"a": 2}
        elif row["branch"] == OBS_GUIDED:
            admitted = artifacts[row["lineage"]]["target_directed"]["observation_governor"] == admission.ADMITTED
            expected = {"a": 3 if admitted else 2}
        else:
            admitted = artifacts[row["lineage"]]["target_directed"]["attribution_governor"] == admission.ADMITTED
            expected = {"a": 3 if admitted else 2}
        assignment_exact += row["selected_versions"] == expected

    engaged = (
        matching_scores[SUPPLIED] >= 43
        and all(score >= 21 for score in design_scores[SUPPLIED].values())
        and all(score >= 21 for score in direction_scores[SUPPLIED].values())
        and not engagement_invalid
    )
    unrelated_loss = unrelated_scores[COLD] - unrelated_scores[OBS_EXPLORE]
    supported = (
        engaged
        and exploration_actions_exact == 4
        and exploration_contradictions == 4
        and exact_records["explicit_exploration"] >= 3
        and exact_projections["explicit_exploration"] >= 3
        and composed_admissions["explicit_exploration"] == 4
        and governor_counts["explicit_exploration"]["observation_admitted"] == 4
        and governor_counts["explicit_exploration"]["attribution_admitted"] == 0
        and equal_records >= 3
        and normal_exact >= 20
        and selection_score["exact"] >= 20
        and selection_score["false_selections"] <= 2
        and matching_scores[OBS_EXPLORE] >= 43
        and all(score >= 21 for score in design_scores[OBS_EXPLORE].values())
        and all(score >= 21 for score in direction_scores[OBS_EXPLORE].values())
        and all(
            matching_scores[OBS_EXPLORE] - matching_scores[branch] >= 16
            for branch in (COLD, RAW, ATTR_EXPLORE, REMOVED)
        )
        and matching_scores[SUPPLIED] - matching_scores[OBS_EXPLORE] <= 4
        and assignment_exact == len(post_rows)
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
            "equal_target_and_exploration_records": equal_records,
            "exact_later_normalizations": normal_exact,
            "exact_records": exact_records,
            "exact_selected_effect_projections": exact_projections,
            "exploration_actions_exact": exploration_actions_exact,
            "exploration_claim_contradictions": exploration_contradictions,
            "later_version_assignments_exact": assignment_exact,
            "parent_admitted_version_2_records": 8,
        },
        "composed_admissions": composed_admissions,
        "design_scores": design_scores,
        "direction_scores": direction_scores,
        "engagement_invalid_participant_cells": engagement_invalid,
        "engagement_participant_branches": list(ENGAGEMENT_BRANCHES),
        "formation_verdict": None,
        "governor_counts": governor_counts,
        "invalid_participant_cells": invalid_cells,
        "logical_calls": len(calls),
        "matching_scores": matching_scores,
        "normalized_selection": selection_score,
        "occurrences": occurrences,
        "parent_packet_sha256": PARENT_PACKET_SHA256,
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "request_distributions": distributions,
        "retries": recorder.retries,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "unrelated_loss": unrelated_loss,
        "unrelated_scores": unrelated_scores,
        "validation_verdict": {
            "class": verdict_class,
            "scope": "observational_counterevidence_comparison",
        },
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise ObservationalRefusal("retained_specimen_mismatch")
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
            raise ObservationalRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise ObservationalRefusal("evidence_replay_mismatch")
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
        "observational-counterevidence-comparison-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    receipt = learned.collect_provider_receipt()
    if not receipt["valid"]:
        raise ObservationalRefusal("provider_identity_mismatch")
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
