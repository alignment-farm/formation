"""Calibrate participant delivery forms for selected structural records."""

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
from micro_environment.unselected_lineage_behavior import (
    LineageProfile,
    LineageState,
    ProposalReceipt,
    apply_committed_action,
)
from unselected_lineage_specimen import ACTION_RESPONSIBILITY, oracle_action


PROTOCOL_VERSION = "structural-record-delivery-calibration-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "STRUCTURAL_RECORD_DELIVERY_CALIBRATION.md"
LINEAGES = learned.LINEAGES
CASES = ("a_up", "a_down", "b_up", "b_down")

COLD = "cold"
PRIOR_STRING_CONTAINER = "prior_scoped_string_container"
SCOPED_CONTROL_RECORD = "scoped_control_record"
DIRECT_EFFECT_TABLE = "direct_control_effect_table"
EFFECT_SENTENCE = "control_effect_sentence"
CURRENT_FAMILY_TABLE = "current_family_effect_table"
CONDITIONS = (
    COLD,
    PRIOR_STRING_CONTAINER,
    SCOPED_CONTROL_RECORD,
    DIRECT_EFFECT_TABLE,
    EFFECT_SENTENCE,
    CURRENT_FAMILY_TABLE,
)

REPEATS = 4
PLANNED_LOGICAL_CALLS = len(LINEAGES) * len(CASES) * len(CONDITIONS) * REPEATS
PHYSICAL_CALL_CEILING = 200
MAX_RETRIES = 8

PARTICIPANT_SYSTEM = """You are the action-authoring component of a cold practitioner. You have no memory outside this request.

DOMAIN RULES
Each device has two displayed controls. Exactly one moves position up by one and the other moves position down by one. The action hold leaves position unchanged. The first displayed control is the first non-hold string in allowed_actions. The second displayed control is the second non-hold string.

Any nonempty retained_material in this calibration has already been selected as applicable to the current device. It may express the control effects as a JSON table, a scoped JSON record, a JSON string inside instrument_records, or a sentence. Use the stated effects to choose the displayed control that moves position toward the target. If position already equals target, choose hold.

OUTPUT INTERFACE
Return exactly one JSON object with the single key action. Its value must be one exact string from allowed_actions. Do not add keys or commentary."""


class CalibrationRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


@dataclass(frozen=True)
class Case:
    state: LineageState
    profile: LineageProfile
    description: str
    design: learned.Design


@dataclass(frozen=True)
class Lineage:
    name: str
    cases: dict[str, Case]


def make_lineage(name: str, index: int) -> Lineage:
    designs = learned.DESIGN_SETS[index - 1]
    cases = {}
    for case_index, case_name in enumerate(CASES, 1):
        position_name = case_name[0]
        design = designs[position_name]
        profile = LineageProfile(
            opaque(f"{name}:{case_name}:family"), design.increasing_slot
        )
        position = 5100 + index * 487 + case_index * 97
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
        cases[case_name] = Case(
            state, profile, design.later_description, design
        )
    return Lineage(name, cases)


LINEAGE_DATA = {
    name: make_lineage(name, index) for index, name in enumerate(LINEAGES, 1)
}


def effect_table(design: learned.Design) -> dict[str, str]:
    first = (
        learned.INCREASES
        if design.increasing_slot == learned.FIRST_INCREASES
        else learned.DECREASES
    )
    return {
        "first_displayed_control_effect": first,
        "second_displayed_control_effect": (
            learned.DECREASES if first == learned.INCREASES else learned.INCREASES
        ),
    }


def material_for(condition: str, case: Case) -> str:
    table = effect_table(case.design)
    scope = {
        "beacon_class": case.design.beacon,
        "housing_class": case.design.housing,
    }
    if condition == COLD:
        return ""
    if condition == PRIOR_STRING_CONTAINER:
        return base.canonical_json_bytes({
            "instrument_records": [learned.static_record(case.design)]
        }).decode()
    if condition == SCOPED_CONTROL_RECORD:
        return base.canonical_json_bytes({
            "effect_table": table,
            "scope": scope,
        }).decode()
    if condition == DIRECT_EFFECT_TABLE:
        return base.canonical_json_bytes(table).decode()
    if condition == EFFECT_SENTENCE:
        first_word = "increases" if table["first_displayed_control_effect"] == learned.INCREASES else "decreases"
        second_word = "decreases" if first_word == "increases" else "increases"
        return (
            f"The first displayed control {first_word} position. "
            f"The second displayed control {second_word} position."
        )
    if condition == CURRENT_FAMILY_TABLE:
        return base.canonical_json_bytes({
            "controller_family": case.state.controller_family,
            **table,
        }).decode()
    raise AssertionError(condition)


def action_body(case: Case, material: str) -> bytes:
    record = {
        "device": learned.public_device(case.state, case.description),
        "responsibility": ACTION_RESPONSIBILITY,
        "retained_material": material,
    }
    return learned.canonical_envelope(
        base.MODEL,
        PARTICIPANT_SYSTEM,
        f"ACTION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",
        base.ACTION_SETTINGS,
    )


def specimen() -> dict[str, Any]:
    return {
        "cases": list(CASES),
        "conditions": list(CONDITIONS),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "lineages": {
            name: {
                "cases": {
                    case_name: {
                        "device": learned.public_device(case.state, case.description),
                        "expected_action": oracle_action(case.state, case.profile),
                        "material_sha256": {
                            condition: base.sha256(material_for(condition, case).encode())
                            for condition in CONDITIONS
                        },
                    }
                    for case_name, case in lineage.cases.items()
                }
            }
            for name, lineage in LINEAGE_DATA.items()
        },
    }


def schedule() -> tuple[tuple[int, str, str, str], ...]:
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_index, case in enumerate(CASES):
            for condition_index in range(len(CONDITIONS)):
                condition = CONDITIONS[(repeat - 1 + condition_index) % len(CONDITIONS)]
                shift = (repeat + case_index + condition_index) % len(LINEAGES)
                order = LINEAGES[shift:] + LINEAGES[:shift]
                rows.extend((repeat, name, case, condition) for name in order)
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
    with configured_recorder():
        recorder = prior.Recorder(transport, evidence_dir)
        if evidence_dir is not None:
            (evidence_dir / "specimen.json").write_bytes(
                base.canonical_json_bytes(specimen())
            )
        calls = []
        for logical_index, (repeat, name, case_name, condition) in enumerate(schedule(), 1):
            case = LINEAGE_DATA[name].cases[case_name]
            material = material_for(condition, case)
            body = action_body(case, material)
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
            calls.append({
                "responsibility": "calibration_action",
                "lineage": name,
                "case": case_name,
                "condition": condition,
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
            })

    distributions = {
        condition: {
            case_name: {
                "assigned": len(cell := [
                    row for row in calls
                    if row["condition"] == condition and row["case"] == case_name
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
        for condition in CONDITIONS
    }

    def total(condition: str, cases: tuple[str, ...]) -> int:
        return sum(distributions[condition][case]["correct_actions"] for case in cases)

    scores = {condition: total(condition, CASES) for condition in CONDITIONS}
    design_scores = {
        condition: {
            "a": total(condition, ("a_up", "a_down")),
            "b": total(condition, ("b_up", "b_down")),
        }
        for condition in CONDITIONS
    }
    direction_scores = {
        condition: {
            "up": total(condition, ("a_up", "b_up")),
            "down": total(condition, ("a_down", "b_down")),
        }
        for condition in CONDITIONS
    }
    valid_by_condition = {
        condition: all(
            distributions[condition][case]["invalid_or_unavailable"] <= 1
            for case in CASES
        )
        for condition in CONDITIONS
    }
    engaged = (
        scores[CURRENT_FAMILY_TABLE] >= 29
        and all(score >= 14 for score in design_scores[CURRENT_FAMILY_TABLE].values())
        and all(score >= 14 for score in direction_scores[CURRENT_FAMILY_TABLE].values())
        and valid_by_condition[CURRENT_FAMILY_TABLE]
    )
    usable_forms = [
        condition
        for condition in (
            PRIOR_STRING_CONTAINER,
            SCOPED_CONTROL_RECORD,
            DIRECT_EFFECT_TABLE,
            EFFECT_SENTENCE,
        )
        if scores[condition] >= 29
        and all(score >= 14 for score in design_scores[condition].values())
        and all(score >= 14 for score in direction_scores[condition].values())
        and scores[CURRENT_FAMILY_TABLE] - scores[condition] <= 2
        and valid_by_condition[condition]
    ]
    verdict_class = (
        "not_engaged" if not engaged
        else "usable_form_found" if usable_forms
        else "null"
    )
    packet = {
        "attempts": recorder.attempts,
        "calls": calls,
        "calibration_verdict": {
            "class": verdict_class,
            "scope": "structural_record_delivery_calibration",
        },
        "design_scores": design_scores,
        "direction_scores": direction_scores,
        "formation_verdict": None,
        "logical_calls": len(calls),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "request_distributions": distributions,
        "retries": recorder.retries,
        "scores": scores,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "usable_forms": usable_forms,
        "valid_by_condition": valid_by_condition,
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise CalibrationRefusal("retained_specimen_mismatch")
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
            raise CalibrationRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise CalibrationRefusal("evidence_replay_mismatch")
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
        args.evidence_dir = Path("evidence") / f"structural-record-delivery-{run_id}"
    started = time.monotonic()
    receipt = base.collect_provider_receipt()
    if not receipt["valid"]:
        raise CalibrationRefusal("provider_identity_mismatch")
    packet = execute(base.live_transport, args.evidence_dir)
    (args.evidence_dir / "provider.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    replay_evidence(args.evidence_dir)
    print(json.dumps({
        "calibration_verdict": packet["calibration_verdict"],
        "elapsed_seconds": time.monotonic() - started,
        "evidence_dir": str(args.evidence_dir),
        "logical_calls": packet["logical_calls"],
        "physical_attempts": packet["physical_attempts"],
        "usable_forms": packet["usable_forms"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
