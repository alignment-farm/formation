"""Calibrate whether cold calls consume known-correct representation forms."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Callable

from contact import distributional_developmental_comparison as base
from micro_environment.unselected_lineage_behavior import (
    FIRST_INCREASES,
    SECOND_INCREASES,
    LineageProfile,
    LineageState,
    ProposalReceipt,
    apply_committed_action,
)
from unselected_lineage_specimen import ACTION_RESPONSIBILITY, oracle_action


PROTOCOL_VERSION = "representation-consumption-calibration-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "REPRESENTATION_CONSUMPTION_CALIBRATION.md"
FORMATS = ("relation_sentence", "effect_table", "target_policy")
EMPTY = "empty"
CONDITIONS = (EMPTY, *FORMATS)
MATCHING_CASES = ("same_up", "same_down")
NONMATCHING_CASES = ("other_up", "other_down")
CASES = (*MATCHING_CASES, *NONMATCHING_CASES)
SOURCES = ("source_a", "source_b", "source_c", "source_d")
REPEATS = 4
PLANNED_LOGICAL_CALLS = len(SOURCES) * len(CASES) * len(CONDITIONS) * REPEATS
PHYSICAL_CALL_CEILING = 264
MAX_RETRIES = 8


class ConsumptionCalibrationRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


@dataclass(frozen=True)
class Source:
    name: str
    profile: LineageProfile
    other_profile: LineageProfile
    cases: dict[str, LineageState]


def make_source(name: str, index: int) -> Source:
    profile = LineageProfile(opaque(f"{name}:family"), SECOND_INCREASES)
    other_profile = LineageProfile(opaque(f"{name}:other-family"), FIRST_INCREASES)
    offset = index * 113
    cases = {
        "same_up": LineageState(
            profile.controller_family,
            opaque(f"{name}:same-up-device"),
            210 + offset,
            211 + offset,
            (opaque(f"{name}:same-up-first"), opaque(f"{name}:same-up-second")),
        ),
        "same_down": LineageState(
            profile.controller_family,
            opaque(f"{name}:same-down-device"),
            810 + offset,
            809 + offset,
            (opaque(f"{name}:same-down-first"), opaque(f"{name}:same-down-second")),
        ),
        "other_up": LineageState(
            other_profile.controller_family,
            opaque(f"{name}:other-up-device"),
            1410 + offset,
            1411 + offset,
            (opaque(f"{name}:other-up-first"), opaque(f"{name}:other-up-second")),
        ),
        "other_down": LineageState(
            other_profile.controller_family,
            opaque(f"{name}:other-down-device"),
            2010 + offset,
            2009 + offset,
            (opaque(f"{name}:other-down-first"), opaque(f"{name}:other-down-second")),
        ),
    }
    return Source(name, profile, other_profile, cases)


SOURCE_DATA = {name: make_source(name, index) for index, name in enumerate(SOURCES, 1)}


def profile_for(source: Source, case: str) -> LineageProfile:
    return source.profile if case in MATCHING_CASES else source.other_profile


def representation(source: Source, representation_format: str) -> str:
    family = source.profile.controller_family
    if representation_format == "relation_sentence":
        return (
            f"For controller family {family}, the first displayed control decreases position "
            "and the second displayed control increases position."
        )
    if representation_format == "effect_table":
        return base.canonical_json_bytes({
            "controller_family": family,
            "first_displayed_control_effect": "decreases_position",
            "second_displayed_control_effect": "increases_position",
        }).decode()
    if representation_format == "target_policy":
        return base.canonical_json_bytes({
            "controller_family": family,
            "target_above_position": "second_displayed_control",
            "target_below_position": "first_displayed_control",
        }).decode()
    raise ConsumptionCalibrationRefusal("unknown_representation_format")


def material(source: Source, condition: str) -> str:
    return "" if condition == EMPTY else representation(source, condition)


def scoped_material(source: Source, state: LineageState, condition: str) -> str:
    return material(source, condition) if state.controller_family == source.profile.controller_family else ""


def action_body(source: Source, case: str, condition: str) -> bytes:
    state = source.cases[case]
    record = {
        "device": base.public_device(state),
        "responsibility": ACTION_RESPONSIBILITY,
        "retained_material": material(source, condition),
    }
    user = f"ACTION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think"
    return base.envelope(base.ACTION_SYSTEM, user, base.ACTION_SETTINGS)


def specimen() -> dict[str, Any]:
    return {
        "cases": list(CASES),
        "conditions": list(CONDITIONS),
        "formats": list(FORMATS),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "sources": {
            name: {
                "cases": {
                    case: {
                        "device": base.public_device(state),
                        "expected_action": oracle_action(state, profile_for(source, case)),
                    }
                    for case, state in source.cases.items()
                },
                "representations": {
                    representation_format: base.sha256(representation(source, representation_format).encode())
                    for representation_format in FORMATS
                },
            }
            for name, source in SOURCE_DATA.items()
        },
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
    }


def schedule() -> tuple[tuple[int, str, str, str], ...]:
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_offset, case in enumerate(CASES):
            for condition_offset in range(len(CONDITIONS)):
                condition = CONDITIONS[(repeat - 1 + condition_offset) % len(CONDITIONS)]
                shift = (repeat + case_offset + condition_offset) % len(SOURCES)
                order = SOURCES[shift:] + SOURCES[:shift]
                for name in order:
                    rows.append((repeat, name, case, condition))
    if len(rows) != PLANNED_LOGICAL_CALLS:
        raise ConsumptionCalibrationRefusal("schedule_size_mismatch")
    return tuple(rows)


Transport = Callable[[bytes], tuple[int, bytes]]


class Recorder:
    def __init__(self, transport: Transport, evidence_dir: Path | None) -> None:
        self.transport = transport
        self.attempts_dir = None
        if evidence_dir is not None:
            evidence_dir.mkdir(parents=True, exist_ok=False)
            self.attempts_dir = evidence_dir / "attempts"
            self.attempts_dir.mkdir()
            (evidence_dir / "specimen.json").write_bytes(base.canonical_json_bytes(specimen()))
        self.physical = 0
        self.retries = 0
        self.attempts: list[dict[str, Any]] = []

    def call(self, logical_index: int, body: bytes) -> tuple[int | None, str | None, str, bool, object]:
        final = None
        for attempt in (1, 2):
            if self.physical >= PHYSICAL_CALL_CEILING:
                raise ConsumptionCalibrationRefusal("physical_call_ceiling")
            self.physical += 1
            status = None
            raw = b""
            error = None
            try:
                status, raw = self.transport(body)
            except ConnectionError as exc:
                error = str(exc)
            retryable = error is not None or status in {408, 429, 500, 502, 503, 504}
            invocation = f"rc{logical_index:03d}"
            meta = {
                "attempt": attempt,
                "error": error,
                "http_status": status,
                "invocation": invocation,
                "logical_index": logical_index,
                "request_sha256": base.sha256(body),
                "response_sha256": base.sha256(raw),
                "retryable": retryable,
            }
            self.attempts.append(meta)
            if self.attempts_dir is not None:
                stem = f"{self.physical:03d}-{invocation}-a{attempt}"
                (self.attempts_dir / f"{stem}.request.json").write_bytes(body)
                (self.attempts_dir / f"{stem}.response.bin").write_bytes(raw)
                (self.attempts_dir / f"{stem}.meta.json").write_text(
                    json.dumps(meta, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
            if retryable and attempt == 1 and self.retries < MAX_RETRIES:
                self.retries += 1
                continue
            final = status, error, raw
            break
        if final is None:
            raise ConsumptionCalibrationRefusal("logical_call_not_completed")
        status, error, raw = final
        content, available, provider = base.parse_content(raw, status)
        return status, error, content, available, provider.get("usage")


def _distribution(rows: list[dict[str, Any]]) -> dict[str, Any]:
    outcomes = [row["action"] if row["action"] is not None else f"<{row['availability']}>" for row in rows]
    return {
        "action_counts": dict(sorted(Counter(outcomes).items())),
        "assigned": len(rows),
        "correct_actions": sum(bool(row["correct_action"]) for row in rows),
        "invalid_or_unavailable": sum(row["availability"] != "available" for row in rows),
    }


def form_findings(distributions: dict[str, dict[str, dict[str, dict[str, Any]]]]) -> dict[str, dict[str, Any]]:
    findings = {}
    for representation_format in FORMATS:
        matching_failures = []
        harmful_cells = []
        for name in SOURCES:
            for case in MATCHING_CASES:
                with_form = distributions[name][representation_format][case]
                empty = distributions[name][EMPTY][case]
                if not (
                    with_form["correct_actions"] >= 3
                    and with_form["correct_actions"] - empty["correct_actions"] >= 2
                    and with_form["invalid_or_unavailable"] <= 1
                ):
                    matching_failures.append(f"{name}:{case}")
            for case in NONMATCHING_CASES:
                with_form = distributions[name][representation_format][case]["correct_actions"]
                empty = distributions[name][EMPTY][case]["correct_actions"]
                if empty - with_form >= 2:
                    harmful_cells.append(f"{name}:{case}")
        if matching_failures:
            status = "not_consumable"
        elif harmful_cells:
            status = "consumable_requires_gate"
        else:
            status = "consumable_self_scoped"
        findings[representation_format] = {
            "harmful_cells": harmful_cells,
            "matching_failures": matching_failures,
            "status": status,
        }
    return findings


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    recorder = Recorder(transport, evidence_dir)
    calls = []
    for logical_index, (repeat, name, case, condition) in enumerate(schedule(), 1):
        source = SOURCE_DATA[name]
        state = source.cases[case]
        body = action_body(source, case, condition)
        status, error, content, content_available, usage = recorder.call(logical_index, body)
        availability, action = base.parse_action(content, state)
        if status != 200 or error is not None:
            availability, action = "unavailable", None
        provider_available = status == 200 and error is None and content_available
        proposal = ProposalReceipt(provider_available, (action or content) if provider_available else "")
        result = apply_committed_action(state, profile_for(source, case), proposal)
        calls.append({
            "action": action,
            "availability": availability,
            "case": case,
            "condition": condition,
            "correct_action": availability == "available" and action == oracle_action(state, profile_for(source, case)),
            "external_result": base.exposed_result(result),
            "invocation": f"rc{logical_index:03d}",
            "logical_index": logical_index,
            "proposal": asdict(proposal),
            "provider_usage": usage,
            "repeat": repeat,
            "request_sha256": base.sha256(body),
            "retained_material_sha256": base.sha256(material(source, condition).encode()),
            "source": name,
        })
    distributions = {
        name: {
            condition: {
                case: _distribution([
                    row for row in calls
                    if row["source"] == name and row["condition"] == condition and row["case"] == case
                ])
                for case in CASES
            }
            for condition in CONDITIONS
        }
        for name in SOURCES
    }
    findings = form_findings(distributions)
    verdict = {
        "class": "candidate_found" if any(row["status"] != "not_consumable" for row in findings.values()) else "null",
        "scope": "representation_consumption_calibration",
    }
    packet = {
        "attempts": recorder.attempts,
        "calls": calls,
        "consumption_calibration_verdict": verdict,
        "form_findings": findings,
        "formation_verdict": None,
        "logical_calls": len(calls),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "request_distributions": distributions,
        "retries": recorder.retries,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise ConsumptionCalibrationRefusal("retained_specimen_mismatch")
    retained = json.loads((evidence_dir / "packet.json").read_bytes())
    entries = []
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        request = (evidence_dir / "attempts" / f"{stem}.request.json").read_bytes()
        response = (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes()
        if base.sha256(request) != meta["request_sha256"] or base.sha256(response) != meta["response_sha256"]:
            raise ConsumptionCalibrationRefusal("retained_attempt_hash_mismatch")
        entries.append((request, response, meta))
    position = 0

    def replay_transport(body: bytes) -> tuple[int, bytes]:
        nonlocal position
        if position >= len(entries):
            raise ConsumptionCalibrationRefusal("missing_retained_attempt")
        request, response, meta = entries[position]
        position += 1
        if request != body:
            raise ConsumptionCalibrationRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(replay_transport)
    if position != len(entries) or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained):
        raise ConsumptionCalibrationRefusal("evidence_replay_mismatch")
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
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        args.evidence_dir = Path("evidence") / f"representation-consumption-calibration-{stamp}"
    started = time.monotonic()
    receipt = base.collect_provider_receipt()
    if not receipt["valid"]:
        raise ConsumptionCalibrationRefusal("provider_identity_mismatch")
    packet = execute(base.live_transport, args.evidence_dir)
    (args.evidence_dir / "provider.json").write_text(
        json.dumps(receipt, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    replay_evidence(args.evidence_dir)
    print(json.dumps({
        "consumption_calibration_verdict": packet["consumption_calibration_verdict"],
        "elapsed_seconds": time.monotonic() - started,
        "evidence_dir": str(args.evidence_dir),
        "logical_calls": packet["logical_calls"],
        "physical_attempts": packet["physical_attempts"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
