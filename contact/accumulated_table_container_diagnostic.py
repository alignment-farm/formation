"""Diagnose ordering and keyed lookup for two retained effect tables."""

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
from contact import staged_table_accumulation_exploration as source
from micro_environment.unselected_lineage_behavior import LineageState, ProposalReceipt, apply_committed_action
from unselected_lineage_specimen import oracle_action


PROTOCOL_VERSION = "accumulated-table-container-diagnostic-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "ACCUMULATED_TABLE_CONTAINER_DIAGNOSTIC.md"
SOURCE_DIR = Path(__file__).parents[1] / "evidence" / "staged-table-accumulation-20260820T140646Z"
SOURCE_PACKET_SHA256 = "c9c12ca3ef2db355bc6832d76db390657179579ca305f945f9949456c11381ab"
SOURCE_SPECIMEN_SHA256 = "9368cbd51181ee400d8da9e6218ee4d2745b8099203e959a460be82b1d673945"
LINEAGES = source.LINEAGES
CASES = ("a_up", "a_down", "b_up", "b_down")
EMPTY = "empty"
LIST_AB = "list_a_then_b"
LIST_BA = "list_b_then_a"
KEYED = "keyed_by_controller_family"
GATED = "family_gated"
CONDITIONS = (EMPTY, LIST_AB, LIST_BA, KEYED, GATED)
REPEATS = 4
PLANNED_LOGICAL_CALLS = len(LINEAGES) * len(CASES) * len(CONDITIONS) * REPEATS
PHYSICAL_CALL_CEILING = 328
MAX_RETRIES = 8


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


@dataclass(frozen=True)
class DiagnosticLineage:
    name: str
    cases: dict[str, LineageState]


def make_lineage(name: str, index: int) -> DiagnosticLineage:
    source_lineage = source.LINEAGE_DATA[name]
    cases = {}
    for case_index, case in enumerate(CASES, 1):
        family = case[0]
        profile = source_lineage.profiles[family]
        position = 6100 + index * 569 + case_index * 107
        cases[case] = LineageState(
            profile.controller_family,
            opaque(f"{name}:{case}:device"),
            position,
            position + (1 if case.endswith("up") else -1),
            (opaque(f"{name}:{case}:first"), opaque(f"{name}:{case}:second")),
        )
    return DiagnosticLineage(name, cases)


LINEAGE_DATA = {
    name: make_lineage(name, index) for index, name in enumerate(LINEAGES, 1)
}


def load_source_tables() -> dict[str, dict[str, str]]:
    packet_bytes = (SOURCE_DIR / "packet.json").read_bytes()
    specimen_bytes = (SOURCE_DIR / "specimen.json").read_bytes()
    if base.sha256(packet_bytes) != SOURCE_PACKET_SHA256:
        raise prior.ValidationRefusal("source_packet_mismatch")
    if base.sha256(specimen_bytes) != SOURCE_SPECIMEN_SHA256:
        raise prior.ValidationRefusal("source_specimen_mismatch")
    packet = json.loads(packet_bytes)
    tables = {name: {} for name in LINEAGES}
    for row in packet["calls"]:
        if row["responsibility"] != "table_authorship":
            continue
        if not row["exact"]:
            raise prior.ValidationRefusal("source_table_not_exact")
        tables[row["lineage"]][row["family_position"]] = row["content"]
    if any(set(families) != {"a", "b"} for families in tables.values()):
        raise prior.ValidationRefusal("source_tables_incomplete")
    return tables


def list_material(first: str, second: str) -> str:
    return base.canonical_json_bytes({"retained_effect_tables": [first, second]}).decode()


def keyed_material(table_a: str, table_b: str) -> str:
    a = json.loads(table_a)
    b = json.loads(table_b)
    return base.canonical_json_bytes({
        "effect_tables_by_controller_family": {
            a["controller_family"]: table_a,
            b["controller_family"]: table_b,
        }
    }).decode()


def specimen() -> dict[str, Any]:
    tables = load_source_tables()
    return {
        "cases": list(CASES),
        "conditions": list(CONDITIONS),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "source_packet_sha256": SOURCE_PACKET_SHA256,
        "source_specimen_sha256": SOURCE_SPECIMEN_SHA256,
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "lineages": {
            name: {
                "cases": {
                    case: {
                        "device": base.public_device(state),
                        "expected_action": oracle_action(
                            state, source.LINEAGE_DATA[name].profiles[case[0]]
                        ),
                    }
                    for case, state in lineage.cases.items()
                },
                "table_sha256": {
                    family: base.sha256(table.encode())
                    for family, table in tables[name].items()
                },
            }
            for name, lineage in LINEAGE_DATA.items()
        },
    }


def schedule():
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
    tables = load_source_tables()
    with configured_recorder():
        recorder = prior.Recorder(transport, evidence_dir)
        if evidence_dir is not None:
            (evidence_dir / "specimen.json").write_bytes(base.canonical_json_bytes(specimen()))
        calls = []
        for logical_index, (repeat, name, case, condition) in enumerate(schedule(), 1):
            lineage = LINEAGE_DATA[name]
            state = lineage.cases[case]
            family = case[0]
            profile = source.LINEAGE_DATA[name].profiles[family]
            table_a, table_b = tables[name]["a"], tables[name]["b"]
            if condition == EMPTY:
                material = ""
            elif condition == LIST_AB:
                material = list_material(table_a, table_b)
            elif condition == LIST_BA:
                material = list_material(table_b, table_a)
            elif condition == KEYED:
                material = keyed_material(table_a, table_b)
            elif condition == GATED:
                material = tables[name][family]
            else:  # pragma: no cover
                raise AssertionError(condition)
            body = prior.action_body(state, material)
            status, error, content, content_available, usage = recorder.call(
                logical_index, body
            )
            availability, action = base.parse_action(content, state)
            if status != 200 or error is not None:
                availability, action = "unavailable", None
            provider_available = status == 200 and error is None and content_available
            receipt = ProposalReceipt(
                provider_available,
                (action or content) if provider_available else "",
            )
            result = apply_committed_action(state, profile, receipt)
            calls.append({
                "responsibility": "diagnostic_action",
                "lineage": name,
                "case": case,
                "condition": condition,
                "repeat": repeat,
                "action": action,
                "availability": availability,
                "correct_action": (
                    availability == "available" and action == oracle_action(state, profile)
                ),
                "external_result": base.exposed_result(result),
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
                "retained_material_sha256": base.sha256(material.encode()),
            })
    distributions = {
        name: {
            condition: {
                case: {
                    "assigned": len(cell := [
                        row for row in calls
                        if row["lineage"] == name
                        and row["condition"] == condition
                        and row["case"] == case
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
            for condition in CONDITIONS
        }
        for name in LINEAGES
    }

    def total(condition, cases):
        return sum(
            distributions[name][condition][case]["correct_actions"]
            for name in LINEAGES for case in cases
        )

    scores = {condition: total(condition, CASES) for condition in CONDITIONS}
    family_scores = {
        condition: {
            "a": total(condition, ("a_up", "a_down")),
            "b": total(condition, ("b_up", "b_down")),
        }
        for condition in CONDITIONS
    }
    every_cell_valid = all(
        distributions[name][condition][case]["invalid_or_unavailable"] <= 1
        for name in LINEAGES for condition in CONDITIONS for case in CASES
    )
    engaged = (
        scores[GATED] >= 58
        and all(score >= 29 for score in family_scores[GATED].values())
        and every_cell_valid
    )
    order_effect = (
        family_scores[LIST_AB]["a"] - family_scores[LIST_AB]["b"] >= 12
        and family_scores[LIST_BA]["b"] - family_scores[LIST_BA]["a"] >= 12
    )
    keyed_usable = (
        scores[KEYED] >= 58
        and all(score >= 29 for score in family_scores[KEYED].values())
        and scores[GATED] - scores[KEYED] <= 4
        and every_cell_valid
    )
    if not engaged:
        verdict_class = "not_engaged"
    elif order_effect and keyed_usable:
        verdict_class = "keyed_repairs_order_bias"
    elif order_effect:
        verdict_class = "order_bias_found"
    elif keyed_usable:
        verdict_class = "keyed_container_found"
    else:
        verdict_class = "null"
    packet = {
        "attempts": recorder.attempts,
        "calls": calls,
        "container_verdict": {
            "class": verdict_class,
            "scope": "accumulated_table_container_diagnostic",
        },
        "every_branch_case_valid": every_cell_valid,
        "family_scores": family_scores,
        "formation_verdict": None,
        "keyed_container_usable": keyed_usable,
        "logical_calls": len(calls),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "order_effect": order_effect,
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "request_distributions": distributions,
        "retries": recorder.retries,
        "scores": scores,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise prior.ValidationRefusal("retained_specimen_mismatch")
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
            raise prior.ValidationRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise prior.ValidationRefusal("evidence_replay_mismatch")
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
        args.evidence_dir = Path("evidence") / f"accumulated-table-container-{run_id}"
    started = time.monotonic()
    receipt = base.collect_provider_receipt()
    if not receipt["valid"]:
        raise prior.ValidationRefusal("provider_identity_mismatch")
    packet = execute(base.live_transport, args.evidence_dir)
    (args.evidence_dir / "provider.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    replay_evidence(args.evidence_dir)
    print(json.dumps({
        "container_verdict": packet["container_verdict"],
        "elapsed_seconds": time.monotonic() - started,
        "evidence_dir": str(args.evidence_dir),
        "logical_calls": packet["logical_calls"],
        "physical_attempts": packet["physical_attempts"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
