"""Continue the supported clerk lineages through one selective third version."""

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


PROTOCOL_VERSION = "selective-longer-lineage-revision-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "SELECTIVE_LONGER_LINEAGE_REVISION.md"
PARENT_DIR = (
    Path(__file__).parents[1]
    / "evidence"
    / "composed-clerical-revision-engagement-successor-20260820T185545Z"
)
PARENT_PACKET_SHA256 = "f277f29851432bc40602427922d1a7ebfdb9da3f3bb7d551eb555c2b7d1413a5"
PARENT_PROTOCOL_VERSION = "composed-clerical-revision-engagement-successor-v1"
LINEAGES = ("engagement_01", "engagement_02", "engagement_03", "engagement_04")
PARENT_LINEAGES = {
    name: revision.make_lineage(name, index)
    for index, name in enumerate(LINEAGES, 1)
}
DESIGN_POSITIONS = revision.DESIGN_POSITIONS
PRE_CASES = revision.PRE_CASES
CASES = learned.CASES

COLD = "cold"
RAW = "raw_third_occurrence"
CURRENT = "composed_current_catalog"
STALE = "stale_v2_checked"
HIDDEN = "hidden_v3_checked"
REMOVED = "v3_removed_restores_v2"
SUPPLIED = "normalized_selected_supplied_catalog"
ORACLE = "environment_selected_clerk_catalog"
BRANCHES = (COLD, RAW, CURRENT, STALE, HIDDEN, REMOVED, SUPPLIED, ORACLE)
ENGAGEMENT_BRANCHES = (SUPPLIED, CURRENT)

REPEATS = 3
PLANNED_LOGICAL_CALLS = 688
PHYSICAL_CALL_CEILING = 700
MAX_RETRIES = 12


class ContinuationRefusal(ValueError):
    pass


@dataclass(frozen=True)
class ContinuationLineage:
    pre_cases: dict[str, revision.Case]
    third_source: LineageState
    third_profile: LineageProfile
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


HOUSING_WORDS = {
    "faceted": "several flat angled faces",
    "arched": "a smooth curved arch",
    "ribbed": "parallel raised ridges",
    "tapered": "a shape that narrows toward the top",
    "smooth": "a plain and even surface",
    "dimpled": "small shallow hollows",
}
BEACON_WORDS = {
    "violet": "purple-violet",
    "amber": "orange-gold",
    "cyan": "blue-green",
    "white": "colorless white",
    "green": "green",
    "red": "red",
}


def new_description(scope: dict[str, str]) -> str:
    return (
        f"A {BEACON_WORDS[scope['beacon_class']]} signal light is mounted above "
        f"an enclosure with {HOUSING_WORDS[scope['housing_class']]} ."
    ).replace(" .", ".")


def make_continuation(name: str, index: int) -> ContinuationLineage:
    parent = PARENT_LINEAGES[name]
    pre_cases = {}
    for case_index, case_name in enumerate(PRE_CASES, 1):
        design_position = case_name[0]
        design = parent.designs[design_position]
        scope = {"beacon_class": design.beacon, "housing_class": design.housing}
        profile = LineageProfile(
            opaque(f"{name}:{case_name}:continuation-pre-family"),
            parent.counter_profiles[design_position].increasing_slot,
        )
        current = 41100 + index * 487 + case_index * 107
        pre_cases[case_name] = revision.Case(
            state(
                f"{name}:{case_name}:continuation-pre",
                current,
                current + (1 if case_name.endswith("up") else -1),
                profile,
            ),
            profile,
            new_description(scope),
            scope,
            design_position,
        )

    third_profile = LineageProfile(
        opaque(f"{name}:a:third-family"),
        parent.old_profiles["a"].increasing_slot,
    )
    third_position = 43100 + index * 499
    third_source = state(
        f"{name}:a:third-source",
        third_position,
        third_position + (1 if index % 2 else -1),
        third_profile,
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
                if index % 2 else
                {"beacon_class": "red", "housing_class": "dimpled"}
            )
            increasing_slot = FIRST_INCREASES if index in {1, 4} else SECOND_INCREASES
        else:
            design_position = None
            scope = {
                "beacon_class": parent.designs["b"].beacon,
                "housing_class": parent.designs["a"].housing,
            }
            increasing_slot = SECOND_INCREASES if index in {1, 4} else FIRST_INCREASES
        profile = LineageProfile(
            opaque(f"{name}:{case_name}:continuation-post-family"),
            increasing_slot,
        )
        current = 45100 + index * 503 + case_index * 109
        post_cases[case_name] = revision.Case(
            state(
                f"{name}:{case_name}:continuation-post",
                current,
                current + (1 if case_name.endswith("up") else -1),
                profile,
            ),
            profile,
            new_description(scope),
            scope,
            design_position,
        )
    return ContinuationLineage(pre_cases, third_source, third_profile, post_cases)


LINEAGE_DATA = {
    name: make_continuation(name, index)
    for index, name in enumerate(LINEAGES, 1)
}


def load_parent() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    packet_bytes = (PARENT_DIR / "packet.json").read_bytes()
    if base.sha256(packet_bytes) != PARENT_PACKET_SHA256:
        raise ContinuationRefusal("parent_packet_hash_mismatch")
    packet = json.loads(packet_bytes)
    if (
        packet.get("protocol_version") != PARENT_PROTOCOL_VERSION
        or packet.get("validation_verdict", {}).get("class") != "supported"
        or packet.get("formation_verdict") is not None
    ):
        raise ContinuationRefusal("parent_packet_status_mismatch")
    retained = {}
    for name in LINEAGES:
        retained[name] = {}
        for position in DESIGN_POSITIONS:
            proposal = packet["proposals"][name][position]["revised"]
            if proposal["admission_status"] != admission.ADMITTED or proposal["version"] != 2:
                raise ContinuationRefusal("parent_version_not_admitted")
            transcripts = [
                row["content"] for row in packet["calls"]
                if row["responsibility"] == "revision_transcription"
                and row["condition"] == "revised"
                and row["lineage"] == name
                and row["design_position"] == position
            ]
            if len(transcripts) != 1 or revision.source_scope(transcripts[0]) is None:
                raise ContinuationRefusal("parent_transcription_missing")
            record = proposal["proposed_record"]
            sentence = canonical.render_sentence(record)
            if not sentence:
                raise ContinuationRefusal("parent_record_unrenderable")
            retained[name][position] = {
                "record": record,
                "sentence": sentence,
                "source_report_sha256": proposal["source_report_sha256"],
                "source_transcription_sha256": proposal["source_transcription_sha256"],
                "transcription": transcripts[0],
                "version": 2,
            }
    return packet, retained


def pre_schedule() -> tuple[tuple[int, str, str], ...]:
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_index, case_name in enumerate(PRE_CASES):
            shift = (repeat + case_index) % len(LINEAGES)
            order = LINEAGES[shift:] + LINEAGES[:shift]
            rows.extend((repeat, name, case_name) for name in order)
    return tuple(rows)


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
    _, parent = load_parent()
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
                "third_source": learned.public_device(
                    LINEAGE_DATA[name].third_source,
                    PARENT_LINEAGES[name].designs["a"].source_description,
                ),
                "post_cases": {
                    case_name: {
                        "device": learned.public_device(case.state, case.description),
                        "expected_action": oracle_action(case.state, case.profile),
                        "expected_version": (
                            3 if case.design_position == "a"
                            else 2 if case.design_position == "b"
                            else None
                        ),
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
    _, parent = load_parent()
    with configured_recorder():
        recorder = validation.verifier.Recorder(transport, evidence_dir)
        if evidence_dir is not None:
            (evidence_dir / "specimen.json").write_bytes(base.canonical_json_bytes(specimen()))
        logical_index = 0
        calls = []
        artifacts = {
            name: {
                "report": None,
                "hidden_report": None,
                "revised": {"trans": "", "prose": "", "record": None, "sentence": ""},
                "hidden": {"trans": "", "prose": "", "record": None, "sentence": ""},
                "projection": {},
                "admission": {},
            }
            for name in LINEAGES
        }

        pre_rows = []
        for repeat, name, case_name in pre_schedule():
            case = LINEAGE_DATA[name].pre_cases[case_name]
            position = case.design_position
            material = parent[name][position]["sentence"]
            logical_index += 1
            body = revision.participant_body(case.state, case.description, material)
            status, error, content, ca, usage = recorder.call(logical_index, body)
            availability, action = base.parse_action(content, case.state)
            if status != 200 or error is not None:
                availability, action = "unavailable", None
            row = {
                "responsibility": "precontinuation_action",
                "lineage": name,
                "case": case_name,
                "repeat": repeat,
                "availability": availability,
                "action": action,
                "correct_action": availability == "available"
                and action == oracle_action(case.state, case.profile),
                "retained_version": 2,
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
            }
            pre_rows.append(row)
            calls.append(row)

        counter_current_policy = 0
        counter_contradictions = 0
        for name in LINEAGES:
            lineage = PARENT_LINEAGES[name]
            continuation = LINEAGE_DATA[name]
            state_value = continuation.third_source
            material = parent[name]["a"]["sentence"]
            logical_index += 1
            body = revision.participant_body(
                state_value, lineage.designs["a"].source_description, material
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
                state_value, continuation.third_profile, proposal
            )
            current_profile = LineageProfile(
                state_value.controller_family,
                lineage.counter_profiles["a"].increasing_slot,
            )
            current_consistent = (
                availability == "available"
                and action == oracle_action(state_value, current_profile)
            )
            counter_current_policy += current_consistent
            selected = getattr(result, "selected_slot", None)
            current_movement = (
                "increased"
                if (selected == "first")
                == (current_profile.increasing_slot == FIRST_INCREASES)
                else "decreased"
            ) if selected in {"first", "second"} else None
            contradicts = (
                current_movement is not None
                and getattr(result, "movement_direction", None) not in {None, current_movement}
            )
            counter_contradictions += contradicts
            report = learned.sensor_report(lineage.designs["a"], result)
            artifacts[name]["report"] = report
            artifacts[name]["hidden_report"] = learned_validation.hidden_report(report)
            calls.append({
                "responsibility": "third_occurrence_action",
                "lineage": name,
                "availability": availability,
                "action": action,
                "version_2_policy_consistent": current_consistent,
                "contradicts_version_2": contradicts,
                "external_result": base.exposed_result(result),
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
            })

        for condition in ("revised", "hidden"):
            report_key = "report" if condition == "revised" else "hidden_report"
            for phase in ("trans", "prose", "parse"):
                for name in LINEAGES:
                    lineage = PARENT_LINEAGES[name]
                    logical_index += 1
                    if phase == "trans":
                        body = staged.transcription_body(artifacts[name][report_key])
                    elif phase == "prose":
                        body = staged.sentence_body(artifacts[name][condition]["trans"])
                    else:
                        body = prose_parser.parser_body(artifacts[name][condition]["prose"])
                    content, ok, usage = available(recorder.call(logical_index, body))
                    expected_record = canonical.expected_record(lineage.designs["a"])
                    if phase == "trans":
                        parsed = staged.parse_transcription(content) if ok else None
                        expected = staged.expected_transcription(
                            lineage.designs["a"],
                            learned_validation.report_view(artifacts[name][report_key]),
                        )
                        artifacts[name][condition]["trans"] = content
                        exact = parsed == expected
                        responsibility = "third_transcription"
                        rendered_exact = None
                    elif phase == "prose":
                        artifacts[name][condition]["prose"] = content
                        exact = prose_parser.parse_explicit_sentence(content) == expected_record
                        responsibility = "third_explicit_prose"
                        rendered_exact = None
                    else:
                        record = canonical.parse_record(content) if ok else None
                        sentence = canonical.render_sentence(record)
                        artifacts[name][condition]["record"] = record
                        artifacts[name][condition]["sentence"] = sentence
                        exact = record == expected_record
                        rendered_exact = sentence == staged.expected_sentence(lineage.designs["a"])
                        responsibility = "third_prose_parse"
                    calls.append({
                        "responsibility": responsibility,
                        "lineage": name,
                        "condition": condition,
                        "available": ok,
                        "exact": exact,
                        "rendered_exact": rendered_exact,
                        "content": content,
                        "provider_usage": usage,
                        "request_sha256": base.sha256(body),
                    })

        for kind in ("revised", "stale", "hidden"):
            for name in LINEAGES:
                if kind == "hidden":
                    report = artifacts[name]["hidden_report"]
                    transcript = artifacts[name]["hidden"]["trans"]
                    record = artifacts[name]["hidden"]["record"]
                else:
                    report = artifacts[name]["report"]
                    transcript = artifacts[name]["revised"]["trans"]
                    record = (
                        artifacts[name]["revised"]["record"]
                        if kind == "revised" else parent[name]["a"]["record"]
                    )
                parsed_transcript = staged.parse_transcription(transcript)
                observed_actuator = (
                    parsed_transcript["observed_actuator"]
                    if parsed_transcript is not None else "unavailable"
                )
                logical_index += 1
                body = validation.projector_body(observed_actuator, record)
                content, ok, usage = available(recorder.call(logical_index, body))
                availability, projected = validation.projection.parse_effect(content)
                if not ok:
                    availability, projected = "unavailable", None
                decision = validation.admission_decision(
                    report, transcript, record, projected
                )
                artifacts[name]["projection"][kind] = projected
                artifacts[name]["admission"][kind] = decision
                expected_projection = (
                    record.get(f"{observed_actuator}_control_effect")
                    if type(record) is dict and observed_actuator in {"first", "second"}
                    else None
                )
                calls.append({
                    "responsibility": "third_selected_effect_projection",
                    "lineage": name,
                    "proposal_kind": kind,
                    "availability": availability,
                    "content": content,
                    "projected_effect": projected,
                    "projection_exact": projected == expected_projection,
                    "admission_status": decision["status"],
                    "admission_reasons": decision["reasons"],
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
                    "responsibility": "continuation_scope_normalization",
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
                "a": revision.source_scope(artifacts[name]["revised"]["trans"]),
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

        def select_material(
            name: str,
            selected: list[str],
            sentences: dict[str, str],
            versions: dict[str, int],
        ) -> tuple[str, dict[str, int]]:
            lineage = PARENT_LINEAGES[name]
            chosen = [
                position for position in DESIGN_POSITIONS
                if lineage.record_ids[position] in selected
            ]
            return (
                "\n".join(sentences[position] for position in chosen if sentences[position]),
                {position: versions[position] for position in chosen if sentences[position]},
            )

        def material_for(name: str, case_name: str, branch: str) -> tuple[str, dict[str, int]]:
            lineage = PARENT_LINEAGES[name]
            learned_selected = selections[name][case_name]
            expected_position = LINEAGE_DATA[name].post_cases[case_name].design_position
            oracle_selected = (
                [lineage.record_ids[expected_position]] if expected_position is not None else []
            )
            parent_sentences = {
                position: parent[name][position]["sentence"]
                for position in DESIGN_POSITIONS
            }
            if branch == COLD:
                return "", {}
            if branch == RAW:
                return base.canonical_json_bytes({
                    "raw_third_occurrence": [artifacts[name]["report"]]
                }).decode(), {}
            if branch == REMOVED:
                return select_material(
                    name, learned_selected, parent_sentences, {"a": 2, "b": 2}
                )
            if branch == SUPPLIED:
                supplied = {
                    "a": staged.expected_sentence(lineage.designs["a"]),
                    "b": staged.expected_sentence(revision.design_with_slot(
                        lineage.designs["b"], lineage.counter_profiles["b"].increasing_slot
                    )),
                }
                return select_material(
                    name, learned_selected, supplied, {"a": 3, "b": 2}
                )
            if branch == ORACLE:
                current = {
                    "a": artifacts[name]["revised"]["sentence"],
                    "b": parent_sentences["b"],
                }
                return select_material(
                    name, oracle_selected, current, {"a": 3, "b": 2}
                )
            if branch == CURRENT:
                a_sentence = (
                    artifacts[name]["revised"]["sentence"]
                    if artifacts[name]["admission"]["revised"]["status"] == admission.ADMITTED
                    else parent_sentences["a"]
                )
                a_version = 3 if a_sentence != parent_sentences["a"] else 2
            elif branch == STALE:
                a_sentence = parent_sentences["a"]
                a_version = 2
            elif branch == HIDDEN:
                if artifacts[name]["admission"]["hidden"]["status"] == admission.ADMITTED:
                    a_sentence = artifacts[name]["hidden"]["sentence"]
                    a_version = 3
                else:
                    a_sentence = parent_sentences["a"]
                    a_version = 2
            else:
                raise AssertionError(branch)
            return select_material(
                name,
                learned_selected,
                {"a": a_sentence, "b": parent_sentences["b"]},
                {"a": a_version, "b": 2},
            )

        post_rows = []
        for repeat, name, case_name, branch in post_schedule():
            case = LINEAGE_DATA[name].post_cases[case_name]
            material, selected_versions = material_for(name, case_name, branch)
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
                "responsibility": "continuation_action",
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
                "selected_versions": selected_versions,
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
            }
            post_rows.append(row)
            calls.append(row)

    if logical_index != PLANNED_LOGICAL_CALLS or len(calls) != PLANNED_LOGICAL_CALLS:
        raise ContinuationRefusal("logical_call_count_mismatch")

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
    engagement_invalid_cells = [
        row for row in invalid_cells if row["branch"] in ENGAGEMENT_BRANCHES
    ]
    projection_rows = [
        row for row in calls
        if row["responsibility"] == "third_selected_effect_projection"
    ]
    admission_counts = {
        kind: {
            "admitted": sum(
                row["admission_status"] == admission.ADMITTED
                for row in projection_rows if row["proposal_kind"] == kind
            ),
            "quarantined": sum(
                row["admission_status"] == admission.QUARANTINED
                for row in projection_rows if row["proposal_kind"] == kind
            ),
        }
        for kind in ("revised", "stale", "hidden")
    }
    third_exact = sum(
        row["exact"] and row.get("rendered_exact")
        for row in calls
        if row["responsibility"] == "third_prose_parse"
        and row["condition"] == "revised"
    )
    projection_exact = sum(
        row["projection_exact"] for row in projection_rows
        if row["proposal_kind"] == "revised"
    )
    normal_exact = sum(
        row["exact"] for row in calls
        if row["responsibility"] == "continuation_scope_normalization"
    )
    selection_pairs = [
        (
            selections[name][case_name],
            [PARENT_LINEAGES[name].record_ids[position]] if position is not None else [],
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
    current_assignment_exact = 0
    current_rows = [row for row in post_rows if row["branch"] == CURRENT]
    for row in current_rows:
        position = LINEAGE_DATA[row["lineage"]].post_cases[row["case"]].design_position
        expected = {position: 3 if position == "a" else 2} if position else {}
        current_assignment_exact += row["selected_versions"] == expected

    pre_correct = sum(row["correct_action"] for row in pre_rows)
    engaged = (
        matching_scores[SUPPLIED] >= 43
        and all(score >= 21 for score in design_scores[SUPPLIED].values())
        and all(score >= 21 for score in direction_scores[SUPPLIED].values())
        and not engagement_invalid_cells
    )
    unrelated_loss = unrelated_scores[COLD] - unrelated_scores[CURRENT]
    supported = (
        engaged
        and pre_correct >= 43
        and counter_current_policy == 4
        and counter_contradictions == 4
        and third_exact >= 3
        and projection_exact >= 3
        and admission_counts["revised"]["admitted"] == 4
        and admission_counts["stale"]["quarantined"] == 4
        and admission_counts["hidden"]["quarantined"] == 4
        and normal_exact >= 20
        and selection_score["exact"] >= 20
        and selection_score["false_selections"] <= 2
        and matching_scores[CURRENT] >= 43
        and all(score >= 21 for score in design_scores[CURRENT].values())
        and all(score >= 21 for score in direction_scores[CURRENT].values())
        and design_scores[CURRENT]["a"] >= 21
        and design_scores[CURRENT]["b"] >= 21
        and all(
            matching_scores[CURRENT] - matching_scores[branch] >= 16
            for branch in (COLD, RAW, STALE, HIDDEN, REMOVED)
        )
        and matching_scores[SUPPLIED] - matching_scores[CURRENT] <= 4
        and matching_scores[ORACLE] >= 43
        and current_assignment_exact == len(current_rows)
        and unrelated_loss <= 3
    )
    harmful = engaged and unrelated_loss >= 6
    verdict_class = (
        "not_engaged" if not engaged
        else "harmful" if harmful
        else "supported" if supported
        else "null"
    )
    proposals = {
        name: {
            kind: {
                "admission_reasons": artifacts[name]["admission"][kind]["reasons"],
                "admission_status": artifacts[name]["admission"][kind]["status"],
                "projected_effect": artifacts[name]["projection"][kind],
                "proposed_record": (
                    parent[name]["a"]["record"]
                    if kind == "stale" else artifacts[name][kind]["record"]
                ),
                "source_report_sha256": base.sha256(base.canonical_json_bytes(
                    artifacts[name]["hidden_report" if kind == "hidden" else "report"]
                )),
                "source_transcription_sha256": base.sha256(
                    artifacts[name]["hidden" if kind == "hidden" else "revised"]["trans"].encode()
                ),
                "version": 2 if kind == "stale" else 3,
            }
            for kind in ("revised", "stale", "hidden")
        }
        for name in LINEAGES
    }
    packet = {
        "admission_counts": admission_counts,
        "attempts": recorder.attempts,
        "calls": calls,
        "components": {
            "counteractions_contradicting_version_2": counter_contradictions,
            "counteractions_version_2_policy_consistent": counter_current_policy,
            "current_version_assignments_exact": current_assignment_exact,
            "exact_later_normalizations": normal_exact,
            "exact_third_version_projections": projection_exact,
            "exact_third_version_records": third_exact,
            "parent_admitted_version_2_records": 8,
            "precontinuation_correct_actions": pre_correct,
        },
        "design_scores": design_scores,
        "direction_scores": direction_scores,
        "engagement_invalid_participant_cells": engagement_invalid_cells,
        "engagement_participant_branches": list(ENGAGEMENT_BRANCHES),
        "formation_verdict": None,
        "invalid_participant_cells": invalid_cells,
        "logical_calls": len(calls),
        "matching_scores": matching_scores,
        "normalized_selection": selection_score,
        "parent_lineage": {
            "packet_sha256": PARENT_PACKET_SHA256,
            "protocol_version": PARENT_PROTOCOL_VERSION,
            "retained_versions": {
                name: {
                    position: {
                        key: parent[name][position][key]
                        for key in (
                            "record", "source_report_sha256",
                            "source_transcription_sha256", "version",
                        )
                    }
                    for position in DESIGN_POSITIONS
                }
                for name in LINEAGES
            },
        },
        "physical_attempts": recorder.physical,
        "proposals": proposals,
        "protocol_version": PROTOCOL_VERSION,
        "request_distributions": distributions,
        "retries": recorder.retries,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "unrelated_loss": unrelated_loss,
        "unrelated_scores": unrelated_scores,
        "validation_verdict": {
            "class": verdict_class,
            "scope": "selective_longer_lineage_revision",
        },
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise ContinuationRefusal("retained_specimen_mismatch")
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
            raise ContinuationRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise ContinuationRefusal("evidence_replay_mismatch")
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
        "selective-longer-lineage-revision-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    receipt = learned.collect_provider_receipt()
    if not receipt["valid"]:
        raise ContinuationRefusal("provider_identity_mismatch")
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
