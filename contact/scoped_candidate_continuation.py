"""Continue one acquired candidate under ablated, ungated, and scoped delivery.

Prospective exploratory note
----------------------------
Question: can an exact public-family delivery gate preserve the acquired
candidate's effect on new matching-family devices while preventing its observed
negative transfer to a different family?
Observation of interest: repeated action distributions for candidate ablation,
ungated delivery, and exact-family-scoped delivery on fresh same-family upward
and downward cases plus one opposite-profile non-transfer case.
Model/interface: exact ``ai/qwen3:14B-Q6_K`` Docker Model Runner artifact and
the same action interface. The candidate bytes and source family are bound to
the completed canonical-authorship evidence. The gate compares public family
strings only; it does not parse, interpret, or rewrite the candidate.
Budget: three conditions by three cases by eight repeats; 72 logical calls and
at most 76 physical attempts. Only transport failures may be retried, at most
four times.
Stopping condition: stop after the fixed schedule or either ceiling. Preserve
malformed and unavailable outputs.
Evidence destination: ``evidence/scoped-candidate-continuation-<run-id>/``.

This is exploratory lineage continuation, not Formation validation.
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
    SECOND_INCREASES,
    LineageProfile,
    LineageState,
    ProposalReceipt,
    apply_committed_action,
)
from unselected_lineage_specimen import ACTION_RESPONSIBILITY, oracle_action


PROTOCOL_VERSION = "scoped-candidate-continuation-v1"
SOURCE_EVIDENCE = Path(__file__).parents[1] / "evidence" / "canonical-mapping-authorship-20260819T235351Z"
ABLATION = "candidate_ablation"
UNGATED = "candidate_ungated"
SCOPED = "candidate_scoped"
CONDITIONS = (ABLATION, UNGATED, SCOPED)
CASES = ("same_family_up", "same_family_down", "other_family_up")
REPEATS = 8
PLANNED_LOGICAL_CALLS = len(CONDITIONS) * len(CASES) * REPEATS
PHYSICAL_CALL_CEILING = 76
MAX_RETRIES = 4


class ScopedContinuationRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


def load_candidate() -> tuple[str, str, str]:
    packet_bytes = (SOURCE_EVIDENCE / "packet.json").read_bytes()
    packet = json.loads(packet_bytes)
    candidate = packet["authored_intermediate"]["content"]
    family = packet["acquisition"]["external_result"]
    specimen = json.loads((SOURCE_EVIDENCE / "specimen.json").read_bytes())
    source_family = specimen["acquisition"]["controller_family"]
    if packet["authored_intermediate"]["available"] is not True:
        raise ScopedContinuationRefusal("source_candidate_unavailable")
    if packet["authored_intermediate"]["exact_static_match"] is not True:
        raise ScopedContinuationRefusal("source_candidate_not_exact_static")
    if source_family not in candidate:
        raise ScopedContinuationRefusal("source_family_absent_from_candidate")
    if family.get("application_status") != "applied":
        raise ScopedContinuationRefusal("source_result_not_applied")
    return candidate, source_family, base.sha256(packet_bytes)


CANDIDATE, SOURCE_FAMILY, SOURCE_PACKET_SHA256 = load_candidate()
PRIMARY_PROFILE = LineageProfile(SOURCE_FAMILY, SECOND_INCREASES)
OTHER_PROFILE = LineageProfile(opaque("other-family"), FIRST_INCREASES)
CASE_STATES = {
    "same_family_up": LineageState(
        SOURCE_FAMILY,
        opaque("same-up-device"),
        356,
        357,
        (opaque("same-up-first"), opaque("same-up-second")),
    ),
    "same_family_down": LineageState(
        SOURCE_FAMILY,
        opaque("same-down-device"),
        925,
        924,
        (opaque("same-down-first"), opaque("same-down-second")),
    ),
    "other_family_up": LineageState(
        OTHER_PROFILE.controller_family,
        opaque("other-up-device"),
        183,
        184,
        (opaque("other-up-first"), opaque("other-up-second")),
    ),
}


def profile_for(case: str) -> LineageProfile:
    return OTHER_PROFILE if case == "other_family_up" else PRIMARY_PROFILE


def delivered_material(condition: str, state: LineageState) -> str:
    if condition == ABLATION:
        return ""
    if condition == UNGATED:
        return CANDIDATE
    if condition == SCOPED:
        return CANDIDATE if state.controller_family == SOURCE_FAMILY else ""
    raise ScopedContinuationRefusal("unknown_condition")


def request_body(case: str, condition: str) -> bytes:
    state = CASE_STATES[case]
    record = {
        "device": base.public_device(state),
        "responsibility": ACTION_RESPONSIBILITY,
        "retained_material": delivered_material(condition, state),
    }
    user = f"ACTION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think"
    return base.envelope(base.ACTION_SYSTEM, user, base.ACTION_SETTINGS)


def specimen() -> dict[str, Any]:
    return {
        "candidate_sha256": base.sha256(CANDIDATE.encode()),
        "cases": [
            {
                "case": case,
                "device": base.public_device(state),
                "expected_action": oracle_action(state, profile_for(case)),
            }
            for case, state in CASE_STATES.items()
        ],
        "conditions": list(CONDITIONS),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "source_family": SOURCE_FAMILY,
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
    if len(rows) != PLANNED_LOGICAL_CALLS:
        raise ScopedContinuationRefusal("schedule_size_mismatch")
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
                raise ScopedContinuationRefusal("physical_call_ceiling")
            self.physical += 1
            status = None
            raw = b""
            error = None
            try:
                status, raw = self.transport(body)
            except ConnectionError as exc:
                error = str(exc)
            retryable = error is not None or status in {408, 429, 500, 502, 503, 504}
            invocation = f"sv{logical_index:03d}"
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
            raise ScopedContinuationRefusal("logical_call_not_completed")
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


def _total_variation(left: dict[str, int], right: dict[str, int]) -> float:
    keys = set(left) | set(right)
    return sum(abs(left.get(key, 0) / REPEATS - right.get(key, 0) / REPEATS) for key in keys) / 2


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    recorder = Recorder(transport, evidence_dir)
    calls = []
    for logical_index, (repeat, case, condition) in enumerate(schedule(), 1):
        state = CASE_STATES[case]
        material = delivered_material(condition, state)
        body = request_body(case, condition)
        status, error, content, content_available, usage = recorder.call(logical_index, body)
        availability, action = base.parse_action(content, state)
        if status != 200 or error is not None:
            availability, action = "unavailable", None
        provider_available = status == 200 and error is None and content_available
        proposal = ProposalReceipt(provider_available, (action or content) if provider_available else "")
        result = apply_committed_action(state, profile_for(case), proposal)
        calls.append({
            "action": action,
            "availability": availability,
            "case": case,
            "condition": condition,
            "correct_action": availability == "available" and action == oracle_action(state, profile_for(case)),
            "delivered_candidate": material == CANDIDATE,
            "external_result": base.exposed_result(result),
            "invocation": f"sv{logical_index:03d}",
            "logical_index": logical_index,
            "proposal": asdict(proposal),
            "provider_usage": usage,
            "repeat": repeat,
            "request_sha256": base.sha256(body),
            "retained_material_sha256": base.sha256(material.encode()),
        })
    distributions = {
        condition: {
            case: _distribution([row for row in calls if row["condition"] == condition and row["case"] == case])
            for case in CASES
        }
        for condition in CONDITIONS
    }
    pairs = (
        ("ungated_minus_ablation", UNGATED, ABLATION),
        ("scoped_minus_ablation", SCOPED, ABLATION),
        ("scoped_minus_ungated", SCOPED, UNGATED),
    )
    comparisons = {
        name: {
            case: {
                "correct_action_delta": distributions[left][case]["correct_actions"] - distributions[right][case]["correct_actions"],
                "total_variation_distance": _total_variation(
                    distributions[left][case]["action_counts"], distributions[right][case]["action_counts"]
                ),
            }
            for case in CASES
        }
        for name, left, right in pairs
    }
    packet = {
        "attempts": recorder.attempts,
        "calls": calls,
        "candidate": {
            "content": CANDIDATE,
            "content_sha256": base.sha256(CANDIDATE.encode()),
            "source_family": SOURCE_FAMILY,
            "source_packet_sha256": SOURCE_PACKET_SHA256,
        },
        "comparisons": comparisons,
        "formation_verdict": None,
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
        raise ScopedContinuationRefusal("retained_specimen_mismatch")
    retained = json.loads((evidence_dir / "packet.json").read_bytes())
    entries = []
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        request = (evidence_dir / "attempts" / f"{stem}.request.json").read_bytes()
        response = (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes()
        if base.sha256(request) != meta["request_sha256"] or base.sha256(response) != meta["response_sha256"]:
            raise ScopedContinuationRefusal("retained_attempt_hash_mismatch")
        entries.append((request, response, meta))
    position = 0

    def replay_transport(body: bytes) -> tuple[int, bytes]:
        nonlocal position
        if position >= len(entries):
            raise ScopedContinuationRefusal("missing_retained_attempt")
        request, response, meta = entries[position]
        position += 1
        if request != body:
            raise ScopedContinuationRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(replay_transport)
    if position != len(entries) or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained):
        raise ScopedContinuationRefusal("evidence_replay_mismatch")
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
        args.evidence_dir = Path("evidence") / f"scoped-candidate-continuation-{stamp}"
    started = time.monotonic()
    receipt = base.collect_provider_receipt()
    if not receipt["valid"]:
        raise ScopedContinuationRefusal("provider_identity_mismatch")
    packet = execute(base.live_transport, args.evidence_dir)
    (args.evidence_dir / "provider.json").write_text(
        json.dumps(receipt, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    replay_evidence(args.evidence_dir)
    print(json.dumps({
        "elapsed_seconds": time.monotonic() - started,
        "evidence_dir": str(args.evidence_dir),
        "logical_calls": packet["logical_calls"],
        "physical_attempts": packet["physical_attempts"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
