"""Measure self-scoping across fresh nonmatching controller families.

Prospective exploratory note
----------------------------
Question: how often do the two validated model-authored family mappings change
action on fresh nonmatching families where applying either mapping would be
wrong?
Observation of interest: per-case action distributions for empty delivery and
each ungated candidate across eight fresh opposite-profile families, balanced
between upward and downward targets.
Model/interface: exact ``ai/qwen3:14B-Q6_K`` Docker Model Runner artifact and
the unchanged action interface. Candidate bytes are bound to the completed
two-world validation evidence.
Budget: eight cases by three conditions by four repeats; 96 logical calls and
at most 100 physical attempts. Only transport failures may be retried, at most
four times.
Stopping condition: stop after the fixed schedule or either ceiling. Preserve
malformed and unavailable outputs.
Evidence destination: ``evidence/candidate-nontransfer-sweep-<run-id>/``.

This is exploratory. It estimates where an exact-family gate could matter; it
does not revise the completed null validation.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Callable

from contact import distributional_developmental_comparison as base
from micro_environment.unselected_lineage_behavior import (
    FIRST_INCREASES,
    LineageProfile,
    LineageState,
    ProposalReceipt,
    apply_committed_action,
)
from unselected_lineage_specimen import ACTION_RESPONSIBILITY, oracle_action


PROTOCOL_VERSION = "candidate-nontransfer-sweep-v1"
SOURCE_EVIDENCE = Path(__file__).parents[1] / "evidence" / "canonical-mapping-candidate-validation-20260820T000646Z"
EMPTY = "empty"
CANDIDATE_A = "candidate_a"
CANDIDATE_B = "candidate_b"
CONDITIONS = (EMPTY, CANDIDATE_A, CANDIDATE_B)
CASES = tuple(f"nontransfer_{index:02d}" for index in range(1, 9))
REPEATS = 4
PLANNED_LOGICAL_CALLS = len(CONDITIONS) * len(CASES) * REPEATS
PHYSICAL_CALL_CEILING = 100
MAX_RETRIES = 4


class NontransferSweepRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


def load_candidates() -> tuple[dict[str, str], str]:
    raw = (SOURCE_EVIDENCE / "packet.json").read_bytes()
    packet = json.loads(raw)
    rows = [row for row in packet["candidates"] if row["exposure"] == "result_exposed"]
    if len(rows) != 2 or not all(row["exact_static_match"] for row in rows):
        raise NontransferSweepRefusal("source_candidates_mismatch")
    return {CANDIDATE_A: rows[0]["content"], CANDIDATE_B: rows[1]["content"]}, base.sha256(raw)


CANDIDATES, SOURCE_PACKET_SHA256 = load_candidates()
PROFILES = {case: LineageProfile(opaque(f"{case}:family"), FIRST_INCREASES) for case in CASES}
CASE_STATES = {
    case: LineageState(
        PROFILES[case].controller_family,
        opaque(f"{case}:device"),
        300 + index * 37,
        300 + index * 37 + (1 if index % 2 else -1),
        (opaque(f"{case}:first"), opaque(f"{case}:second")),
    )
    for index, case in enumerate(CASES, 1)
}


def material(condition: str) -> str:
    if condition == EMPTY:
        return ""
    try:
        return CANDIDATES[condition]
    except KeyError as error:
        raise NontransferSweepRefusal("unknown_condition") from error


def request_body(case: str, condition: str) -> bytes:
    state = CASE_STATES[case]
    record = {
        "device": base.public_device(state),
        "responsibility": ACTION_RESPONSIBILITY,
        "retained_material": material(condition),
    }
    user = f"ACTION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think"
    return base.envelope(base.ACTION_SYSTEM, user, base.ACTION_SETTINGS)


def specimen() -> dict[str, Any]:
    return {
        "candidates": {key: base.sha256(value.encode()) for key, value in CANDIDATES.items()},
        "cases": {
            case: {
                "device": base.public_device(state),
                "expected_action": oracle_action(state, PROFILES[case]),
            }
            for case, state in CASE_STATES.items()
        },
        "conditions": list(CONDITIONS),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "source_packet_sha256": SOURCE_PACKET_SHA256,
    }


def schedule() -> tuple[tuple[int, str, str], ...]:
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_offset in range(len(CASES)):
            case = CASES[(repeat - 1 + case_offset) % len(CASES)]
            for condition_offset in range(len(CONDITIONS)):
                condition = CONDITIONS[(repeat - 1 + condition_offset) % len(CONDITIONS)]
                rows.append((repeat, case, condition))
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
                raise NontransferSweepRefusal("physical_call_ceiling")
            self.physical += 1
            status = None
            raw = b""
            error = None
            try:
                status, raw = self.transport(body)
            except ConnectionError as exc:
                error = str(exc)
            retryable = error is not None or status in {408, 429, 500, 502, 503, 504}
            invocation = f"nv{logical_index:03d}"
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
                    json.dumps(meta, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8"
                )
            if retryable and attempt == 1 and self.retries < MAX_RETRIES:
                self.retries += 1
                continue
            final = status, error, raw
            break
        if final is None:
            raise NontransferSweepRefusal("logical_call_not_completed")
        status, error, raw = final
        content, available, provider = base.parse_content(raw, status)
        return status, error, content, available, provider.get("usage")


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    recorder = Recorder(transport, evidence_dir)
    calls = []
    for logical_index, (repeat, case, condition) in enumerate(schedule(), 1):
        state = CASE_STATES[case]
        body = request_body(case, condition)
        status, error, content, content_available, usage = recorder.call(logical_index, body)
        availability, action = base.parse_action(content, state)
        if status != 200 or error is not None:
            availability, action = "unavailable", None
        provider_available = status == 200 and error is None and content_available
        proposal = ProposalReceipt(provider_available, (action or content) if provider_available else "")
        result = apply_committed_action(state, PROFILES[case], proposal)
        calls.append({
            "action": action,
            "availability": availability,
            "case": case,
            "condition": condition,
            "correct_action": availability == "available" and action == oracle_action(state, PROFILES[case]),
            "external_result": base.exposed_result(result),
            "invocation": f"nv{logical_index:03d}",
            "logical_index": logical_index,
            "proposal": asdict(proposal),
            "provider_usage": usage,
            "repeat": repeat,
            "request_sha256": base.sha256(body),
        })
    distributions = {
        condition: {
            case: {
                "action_counts": dict(sorted(Counter(
                    row["action"] if row["action"] is not None else f"<{row['availability']}>"
                    for row in calls if row["condition"] == condition and row["case"] == case
                ).items())),
                "correct_actions": sum(
                    bool(row["correct_action"]) for row in calls
                    if row["condition"] == condition and row["case"] == case
                ),
            }
            for case in CASES
        }
        for condition in CONDITIONS
    }
    harmful_cells = {
        condition: [
            case for case in CASES
            if distributions[EMPTY][case]["correct_actions"] - distributions[condition][case]["correct_actions"] >= 3
        ]
        for condition in (CANDIDATE_A, CANDIDATE_B)
    }
    packet = {
        "attempts": recorder.attempts,
        "calls": calls,
        "formation_verdict": None,
        "harmful_cells": harmful_cells,
        "logical_calls": len(calls),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "request_distributions": distributions,
        "retries": recorder.retries,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "validation_verdict": None,
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise NontransferSweepRefusal("retained_specimen_mismatch")
    retained = json.loads((evidence_dir / "packet.json").read_bytes())
    entries = []
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        request = (evidence_dir / "attempts" / f"{stem}.request.json").read_bytes()
        response = (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes()
        if base.sha256(request) != meta["request_sha256"] or base.sha256(response) != meta["response_sha256"]:
            raise NontransferSweepRefusal("retained_attempt_hash_mismatch")
        entries.append((request, response, meta))
    position = 0

    def replay_transport(body: bytes) -> tuple[int, bytes]:
        nonlocal position
        request, response, meta = entries[position]
        position += 1
        if request != body:
            raise NontransferSweepRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(replay_transport)
    if position != len(entries) or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained):
        raise NontransferSweepRefusal("evidence_replay_mismatch")
    return replayed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args(argv)
    if not args.live:
        print(json.dumps({"mode": "smoke_no_contact", "planned_logical_calls": PLANNED_LOGICAL_CALLS, "side_effects_entered": False}, sort_keys=True))
        return 0
    if args.evidence_dir is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        args.evidence_dir = Path("evidence") / f"candidate-nontransfer-sweep-{stamp}"
    started = time.monotonic()
    receipt = base.collect_provider_receipt()
    if not receipt["valid"]:
        raise NontransferSweepRefusal("provider_identity_mismatch")
    packet = execute(base.live_transport, args.evidence_dir)
    (args.evidence_dir / "provider.json").write_text(json.dumps(receipt, ensure_ascii=True, indent=2, sort_keys=True) + "\n")
    replay_evidence(args.evidence_dir)
    print(json.dumps({"elapsed_seconds": time.monotonic() - started, "evidence_dir": str(args.evidence_dir), "logical_calls": packet["logical_calls"], "physical_attempts": packet["physical_attempts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
