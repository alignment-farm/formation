"""Test structured clerk effects with deterministic calibrated rendering."""

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
from contact import staged_clerical_instrument_successor as source
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


PROTOCOL_VERSION = "canonical-clerical-record-diagnostic-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "CANONICAL_CLERICAL_RECORD_DIAGNOSTIC.md"
SOURCE_DIR = Path(__file__).parents[1] / "evidence" / "staged-clerical-instrument-20260820T164000Z"
SOURCE_PACKET_SHA256 = "fbd47acdc4d6f493a46bcb0103d04449829b137b2ccdb4a3ec4a285cf5da7bc5"
SOURCE_SPECIMEN_SHA256 = "7530dd0752b9018fd82920c8ef9e9b3e90d4261ffe53d10e1881cdb35a0b072c"

LINEAGES = source.LINEAGES
DESIGN_POSITIONS = source.DESIGN_POSITIONS
CASES = source.CASES

COLD = "cold"
RAW = "retained_raw_sensor_reports"
ALL_RENDERED = "all_rendered_records"
NORMALIZED_RENDERED = "normalized_selected_rendered_record"
NORMALIZED_STATIC = "normalized_selected_supplied_sentence"
ORACLE_RENDERED = "oracle_selected_rendered_record"
ORACLE_STATIC = "oracle_selected_supplied_sentence"
BRANCHES = (
    COLD,
    RAW,
    ALL_RENDERED,
    NORMALIZED_RENDERED,
    NORMALIZED_STATIC,
    ORACLE_RENDERED,
    ORACLE_STATIC,
)

REPEATS = 4
RECORD_CALLS = len(LINEAGES) * len(DESIGN_POSITIONS)
LATER_CALLS = len(LINEAGES) * len(CASES) * len(BRANCHES) * REPEATS
PLANNED_LOGICAL_CALLS = RECORD_CALLS + LATER_CALLS
PHYSICAL_CALL_CEILING = 348
MAX_RETRIES = 8

RECORD_SYSTEM = """You are a clerical effect-record writer. You have no memory outside this request.

You receive one exact normalized sensory transcript. Exactly one displayed control increases position and the other decreases it. Put the complete relation into named fields.

Return exactly one JSON object with these keys and no others:
{"first_control_effect":"<increases_position or decreases_position>","second_control_effect":"<decreases_position or increases_position>"}
Do not add commentary."""


class DiagnosticRefusal(ValueError):
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
    cases: dict[str, LaterCase]
    record_ids: dict[str, str]


def make_lineage(name: str, index: int) -> Lineage:
    designs = learned.DESIGN_SETS[index - 1]
    cases = {}
    for case_index, case_name in enumerate(CASES, 1):
        source_case = source.LINEAGE_DATA[name].cases[case_name]
        if source_case.design_position is not None:
            design = designs[source_case.design_position]
            increasing_slot = design.increasing_slot
        else:
            increasing_slot = (
                FIRST_INCREASES
                if source_case.profile.increasing_slot == FIRST_INCREASES
                else SECOND_INCREASES
            )
        profile = LineageProfile(
            opaque(f"{name}:{case_name}:fresh-family"), increasing_slot
        )
        position = 15100 + index * 521 + case_index * 103
        target = position + (1 if case_name.endswith("up") else -1)
        state = LineageState(
            profile.controller_family,
            opaque(f"{name}:{case_name}:device"),
            position,
            target,
            (
                opaque(f"{name}:{case_name}:first"),
                opaque(f"{name}:{case_name}:second"),
            ),
        )
        cases[case_name] = LaterCase(
            state,
            profile,
            source_case.description,
            source_case.scope,
            source_case.design_position,
        )
    return Lineage(
        name,
        designs,
        cases,
        {position: opaque(f"{name}:{position}:record") for position in DESIGN_POSITIONS},
    )


LINEAGE_DATA = {
    name: make_lineage(name, index) for index, name in enumerate(LINEAGES, 1)
}


def load_source_artifacts() -> dict[str, Any]:
    packet_bytes = (SOURCE_DIR / "packet.json").read_bytes()
    specimen_bytes = (SOURCE_DIR / "specimen.json").read_bytes()
    if base.sha256(packet_bytes) != SOURCE_PACKET_SHA256:
        raise DiagnosticRefusal("source_packet_mismatch")
    if base.sha256(specimen_bytes) != SOURCE_SPECIMEN_SHA256:
        raise DiagnosticRefusal("source_specimen_mismatch")
    packet = json.loads(packet_bytes)
    if (
        packet["encoding"]["exact_transcriptions"] != 4
        or packet["normalization"]["exact"] < 10
        or packet["selection_scores"]["normalized_model_scopes"]["false_selections"] != 0
    ):
        raise DiagnosticRefusal("source_result_not_eligible")
    artifacts = {
        name: {
            "reports": {},
            "transcriptions": {},
            "normalizations": {},
        }
        for name in LINEAGES
    }
    for row in packet["calls"]:
        name = row.get("lineage")
        if row["responsibility"] == "source_action":
            position = row["design_position"]
            result = row["external_result"]
            design = source.LINEAGE_DATA[name].designs[position]
            selected = result.get("selected_slot")
            movement = result.get("movement_direction")
            artifacts[name]["reports"][position] = {
                "actuator_report": (
                    f"The {selected} displayed actuator was engaged."
                    if selected in {"first", "second"}
                    else "No displayed actuator engagement was available."
                ),
                "device_report": design.source_description,
                "gauge_report": (
                    "The position gauge rose by one mark."
                    if movement == "increased"
                    else "The position gauge fell by one mark."
                    if movement == "decreased"
                    else "No gauge movement was available."
                ),
            }
        elif row["responsibility"] == "clerical_transcription":
            if not row["exact"]:
                raise DiagnosticRefusal("source_transcription_not_exact")
            artifacts[name]["transcriptions"][row["design_position"]] = row["content"]
        elif row["responsibility"] == "later_scope_normalization":
            if not row["valid"]:
                raise DiagnosticRefusal("source_normalization_invalid")
            artifacts[name]["normalizations"][row["case"]] = row["normalized_scope"]
    if any(
        set(artifact["reports"]) != set(DESIGN_POSITIONS)
        or set(artifact["transcriptions"]) != set(DESIGN_POSITIONS)
        or set(artifact["normalizations"]) != set(CASES)
        for artifact in artifacts.values()
    ):
        raise DiagnosticRefusal("source_artifacts_incomplete")
    return artifacts


def record_body(transcription: str) -> bytes:
    record = {"normalized_sensory_transcript": transcription}
    return learned.canonical_envelope(
        learned.INSTRUMENT_MODEL,
        RECORD_SYSTEM,
        f"EFFECT RECORD REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",
        learned.INSTRUMENT_SETTINGS,
    )


def parse_record(content: str) -> dict[str, str] | None:
    try:
        value = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return None
    if type(value) is not dict or set(value) != {
        "first_control_effect", "second_control_effect"
    }:
        return None
    if {
        value["first_control_effect"], value["second_control_effect"]
    } != {learned.INCREASES, learned.DECREASES}:
        return None
    return value


def expected_record(design: learned.Design) -> dict[str, str]:
    first = (
        learned.INCREASES
        if design.increasing_slot == FIRST_INCREASES
        else learned.DECREASES
    )
    return {
        "first_control_effect": first,
        "second_control_effect": (
            learned.DECREASES if first == learned.INCREASES else learned.INCREASES
        ),
    }


def render_sentence(record: dict[str, str] | None) -> str:
    if record is None:
        return ""
    first = "increases" if record["first_control_effect"] == learned.INCREASES else "decreases"
    second = "increases" if record["second_control_effect"] == learned.INCREASES else "decreases"
    return (
        f"The first displayed control {first} position. "
        f"The second displayed control {second} position."
    )


def expected_selection(lineage: Lineage, case_name: str) -> list[str]:
    position = lineage.cases[case_name].design_position
    return [lineage.record_ids[position]] if position is not None else []


def source_scopes(artifacts: dict[str, Any], name: str) -> dict[str, dict[str, str]]:
    return {
        position: source.parse_transcription(
            artifacts[name]["transcriptions"][position]
        )["scope"]
        for position in DESIGN_POSITIONS
    }


def static_scopes(lineage: Lineage) -> dict[str, dict[str, str]]:
    return {
        position: {
            "beacon_class": lineage.designs[position].beacon,
            "housing_class": lineage.designs[position].housing,
        }
        for position in DESIGN_POSITIONS
    }


def exact_match_ids(
    lineage: Lineage,
    current_scope: dict[str, str],
    scopes: dict[str, dict[str, str]],
) -> list[str]:
    return [
        lineage.record_ids[position]
        for position in DESIGN_POSITIONS
        if scopes[position] == current_scope
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


def participant_body(case: LaterCase, material: str) -> bytes:
    record = {
        "device": learned.public_device(case.state, case.description),
        "responsibility": ACTION_RESPONSIBILITY,
        "retained_material": material,
    }
    return learned.canonical_envelope(
        base.MODEL,
        calibration.PARTICIPANT_SYSTEM,
        f"ACTION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",
        base.ACTION_SETTINGS,
    )


def specimen() -> dict[str, Any]:
    artifacts = load_source_artifacts()
    return {
        "branches": list(BRANCHES),
        "cases": list(CASES),
        "instrument_model": learned.INSTRUMENT_MODEL,
        "instrument_model_digest": learned.INSTRUMENT_MODEL_DIGEST,
        "later_calls": LATER_CALLS,
        "participant_model": base.MODEL,
        "participant_model_digest": base.MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "record_calls": RECORD_CALLS,
        "repeats": REPEATS,
        "source_packet_sha256": SOURCE_PACKET_SHA256,
        "source_specimen_sha256": SOURCE_SPECIMEN_SHA256,
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "lineages": {
            name: {
                "record_ids": lineage.record_ids,
                "retained_transcription_sha256": {
                    position: base.sha256(
                        artifacts[name]["transcriptions"][position].encode()
                    )
                    for position in DESIGN_POSITIONS
                },
                "cases": {
                    case_name: {
                        "device": learned.public_device(case.state, case.description),
                        "expected_action": oracle_action(case.state, case.profile),
                        "expected_record_ids": expected_selection(lineage, case_name),
                        "retained_normalized_scope": artifacts[name]["normalizations"][case_name],
                    }
                    for case_name, case in lineage.cases.items()
                },
            }
            for name, lineage in LINEAGE_DATA.items()
        },
    }


def schedule() -> tuple[tuple[int, str, str, str], ...]:
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


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    artifacts = load_source_artifacts()
    with configured_recorder():
        recorder = prior.Recorder(transport, evidence_dir)
        if evidence_dir is not None:
            (evidence_dir / "specimen.json").write_bytes(
                base.canonical_json_bytes(specimen())
            )
        calls = []
        rendered = {name: {} for name in LINEAGES}
        logical_index = 0
        for name in LINEAGES:
            lineage = LINEAGE_DATA[name]
            for position in DESIGN_POSITIONS:
                transcription = artifacts[name]["transcriptions"][position]
                logical_index += 1
                body = record_body(transcription)
                status, error, content, content_available, usage = recorder.call(
                    logical_index, body
                )
                available = status == 200 and error is None and content_available
                parsed = parse_record(content) if available else None
                expected = expected_record(lineage.designs[position])
                sentence = render_sentence(parsed)
                rendered[name][position] = sentence
                calls.append({
                    "responsibility": "canonical_effect_record",
                    "lineage": name,
                    "design_position": position,
                    "available": available,
                    "valid": parsed is not None,
                    "exact": parsed == expected,
                    "content": content if available else "",
                    "parsed": parsed,
                    "rendered_sentence": sentence,
                    "rendered_exact": sentence == source.expected_sentence(lineage.designs[position]),
                    "provider_usage": usage,
                    "request_sha256": base.sha256(body),
                })

        normalized_selections = {name: {} for name in LINEAGES}
        static_selections = {name: {} for name in LINEAGES}
        static_sentences = {
            name: {
                position: source.expected_sentence(
                    LINEAGE_DATA[name].designs[position]
                )
                for position in DESIGN_POSITIONS
            }
            for name in LINEAGES
        }
        for name in LINEAGES:
            lineage = LINEAGE_DATA[name]
            model_scopes = source_scopes(artifacts, name)
            supplied_scopes = static_scopes(lineage)
            for case_name in CASES:
                current_scope = artifacts[name]["normalizations"][case_name]
                normalized_selections[name][case_name] = exact_match_ids(
                    lineage, current_scope, model_scopes
                )
                static_selections[name][case_name] = exact_match_ids(
                    lineage, current_scope, supplied_scopes
                )

        later_rows = []
        for repeat, name, case_name, branch in schedule():
            lineage = LINEAGE_DATA[name]
            case = lineage.cases[case_name]
            expected = expected_selection(lineage, case_name)
            if branch == COLD:
                material = ""
            elif branch == RAW:
                material = raw_material(artifacts[name]["reports"])
            elif branch == ALL_RENDERED:
                material = all_material(rendered[name])
            elif branch == NORMALIZED_RENDERED:
                material = selected_sentence(
                    lineage, rendered[name], normalized_selections[name][case_name]
                )
            elif branch == NORMALIZED_STATIC:
                material = selected_sentence(
                    lineage, static_sentences[name], static_selections[name][case_name]
                )
            elif branch == ORACLE_RENDERED:
                material = selected_sentence(lineage, rendered[name], expected)
            elif branch == ORACLE_STATIC:
                material = selected_sentence(lineage, static_sentences[name], expected)
            else:  # pragma: no cover
                raise AssertionError(branch)
            logical_index += 1
            body = participant_body(case, material)
            status, error, content, content_available, usage = recorder.call(
                logical_index, body
            )
            availability, action = base.parse_action(content, case.state)
            if status != 200 or error is not None:
                availability, action = "unavailable", None
            provider_available = status == 200 and error is None and content_available
            proposal = ProposalReceipt(
                provider_available, (action or content) if provider_available else ""
            )
            result = apply_committed_action(case.state, case.profile, proposal)
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
                    and action == oracle_action(case.state, case.profile)
                ),
                "external_result": base.exposed_result(result),
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
                "retained_material_sha256": base.sha256(material.encode()),
            }
            later_rows.append(row)
            calls.append(row)

    if logical_index != PLANNED_LOGICAL_CALLS:
        raise DiagnosticRefusal("logical_call_count_mismatch")

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
    exact_records = sum(
        row["exact"] for row in calls
        if row["responsibility"] == "canonical_effect_record"
    )
    rendered_exact = sum(
        row["rendered_exact"] for row in calls
        if row["responsibility"] == "canonical_effect_record"
    )
    selection_rows = []
    for name in LINEAGES:
        lineage = LINEAGE_DATA[name]
        for case_name in CASES:
            selected = normalized_selections[name][case_name]
            expected = expected_selection(lineage, case_name)
            selection_rows.append((selected, expected))
    selection_score = {
        "exact": sum(selected == expected for selected, expected in selection_rows),
        "false_selections": sum(not expected and bool(selected) for selected, expected in selection_rows),
        "total": len(selection_rows),
    }
    engaged = (
        matching_scores[ORACLE_STATIC] >= 29
        and all(score >= 14 for score in design_scores[ORACLE_STATIC].values())
        and all(score >= 14 for score in direction_scores[ORACLE_STATIC].values())
        and every_cell_valid
    )
    record_found = (
        exact_records >= 3
        and matching_scores[ORACLE_RENDERED] >= 27
    )
    unrelated_loss = unrelated_scores[COLD] - unrelated_scores[NORMALIZED_RENDERED]
    pipeline_candidate = (
        record_found
        and selection_score["exact"] >= 10
        and selection_score["false_selections"] <= 1
        and matching_scores[NORMALIZED_RENDERED] >= 27
        and matching_scores[NORMALIZED_RENDERED] - matching_scores[COLD] >= 8
        and matching_scores[NORMALIZED_RENDERED] - matching_scores[RAW] >= 4
        and matching_scores[NORMALIZED_RENDERED] - matching_scores[ALL_RENDERED] >= 4
        and matching_scores[ORACLE_STATIC] - matching_scores[NORMALIZED_RENDERED] <= 4
        and unrelated_loss <= 2
    )
    harmful = engaged and unrelated_loss >= 4
    if not engaged:
        verdict_class = "not_engaged"
    elif harmful:
        verdict_class = "harmful"
    elif pipeline_candidate:
        verdict_class = "pipeline_candidate"
    elif record_found:
        verdict_class = "canonical_record_only"
    else:
        verdict_class = "null"

    packet = {
        "attempts": recorder.attempts,
        "calls": calls,
        "canonical_records": {
            "exact": exact_records,
            "rendered_exact": rendered_exact,
            "total": RECORD_CALLS,
        },
        "design_scores": design_scores,
        "direction_scores": direction_scores,
        "every_participant_cell_valid": every_cell_valid,
        "formation_verdict": None,
        "instrument_verdict": {
            "class": verdict_class,
            "scope": "canonical_clerical_record_diagnostic",
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
        "source_packet_sha256": SOURCE_PACKET_SHA256,
        "source_specimen_sha256": SOURCE_SPECIMEN_SHA256,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "unrelated_loss": unrelated_loss,
        "unrelated_scores": unrelated_scores,
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise DiagnosticRefusal("retained_specimen_mismatch")
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
            raise DiagnosticRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise DiagnosticRefusal("evidence_replay_mismatch")
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
        args.evidence_dir = Path("evidence") / f"canonical-clerical-record-{run_id}"
    started = time.monotonic()
    receipt = learned.collect_provider_receipt()
    if not receipt["valid"]:
        raise DiagnosticRefusal("provider_identity_mismatch")
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
