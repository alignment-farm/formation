"""Distinguish mapping use from first-mentioned-slot copying.

Prospective exploratory note
----------------------------
Question: does the action distribution follow an invariant controller mapping
or the first slot mentioned in an equivalent retained rule?
Observation of interest: compare empty material with increase-first and
decrease-first wordings on fresh same-family upward and downward cases, plus an
opposite-profile non-transfer case.
Model/interface: exact ``ai/qwen3:14B-Q6_K`` Docker Model Runner artifact and
the preceding implicit JSON retained-material interface. The two rules express
the same mapping and differ only in clause order.
Budget: three conditions by three cases by eight repeats; 72 logical calls and
at most 76 physical attempts. Only transport failures may be retried, at most
four times.
Stopping condition: stop after the fixed schedule or either ceiling. Preserve
malformed and unavailable outputs.
Evidence destination: ``evidence/retained-rule-clause-order-<run-id>/``.

This is an interface interpretation trial, not a Formation comparison.
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

from contact.distributional_developmental_comparison import (
    ACTION_SETTINGS,
    ACTION_SYSTEM,
    MODEL,
    MODEL_DIGEST,
    canonical_json_bytes,
    collect_provider_receipt,
    exposed_result,
    live_transport,
    parse_action,
    parse_content,
    public_device,
    sha256,
)
from micro_environment.unselected_lineage_behavior import (
    FIRST_INCREASES,
    SECOND_INCREASES,
    LineageProfile,
    LineageState,
    ProposalReceipt,
    apply_committed_action,
)
from unselected_lineage_specimen import ACTION_RESPONSIBILITY, oracle_action


PROTOCOL_VERSION = "retained-rule-clause-order-trial-v1"
EMPTY = "empty"
INCREASE_FIRST = "increase_first"
DECREASE_FIRST = "decrease_first"
CONDITIONS = (EMPTY, INCREASE_FIRST, DECREASE_FIRST)
CASES = ("same_family_up", "same_family_down", "other_family_up")
REPEATS = 8
PLANNED_LOGICAL_CALLS = len(CONDITIONS) * len(CASES) * REPEATS
PHYSICAL_CALL_CEILING = 76
MAX_RETRIES = 4


class ClauseOrderRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


PRIMARY_PROFILE = LineageProfile(opaque("primary-family"), SECOND_INCREASES)
OTHER_PROFILE = LineageProfile(opaque("other-family"), FIRST_INCREASES)
CASE_STATES = {
    "same_family_up": LineageState(
        PRIMARY_PROFILE.controller_family,
        opaque("same-up-device"),
        384,
        385,
        (opaque("same-up-first"), opaque("same-up-second")),
    ),
    "same_family_down": LineageState(
        PRIMARY_PROFILE.controller_family,
        opaque("same-down-device"),
        767,
        766,
        (opaque("same-down-first"), opaque("same-down-second")),
    ),
    "other_family_up": LineageState(
        OTHER_PROFILE.controller_family,
        opaque("other-up-device"),
        119,
        120,
        (opaque("other-up-first"), opaque("other-up-second")),
    ),
}


def profile_for(case: str) -> LineageProfile:
    return OTHER_PROFILE if case == "other_family_up" else PRIMARY_PROFILE


def retained_material(condition: str) -> str:
    family = PRIMARY_PROFILE.controller_family
    if condition == EMPTY:
        return ""
    if condition == INCREASE_FIRST:
        return (
            f"For controller family {family}, the second displayed control increases position "
            "and the first displayed control decreases position."
        )
    if condition == DECREASE_FIRST:
        return (
            f"For controller family {family}, the first displayed control decreases position "
            "and the second displayed control increases position."
        )
    raise ClauseOrderRefusal("unknown_condition")


def request_body(case: str, condition: str) -> bytes:
    state = CASE_STATES[case]
    record = {
        "device": public_device(state),
        "responsibility": ACTION_RESPONSIBILITY,
        "retained_material": retained_material(condition),
    }
    user = f"ACTION REQUEST\n{canonical_json_bytes(record).decode()}\n/no_think"
    return canonical_json_bytes({
        "messages": [{"role": "system", "content": ACTION_SYSTEM}, {"role": "user", "content": user}],
        "model": MODEL,
        **ACTION_SETTINGS,
    })


def specimen() -> dict[str, Any]:
    return {
        "cases": [
            {
                "case": case,
                "device": public_device(state),
                "expected_action": oracle_action(state, profile_for(case)),
            }
            for case, state in CASE_STATES.items()
        ],
        "conditions": list(CONDITIONS),
        "material_sha256": {condition: sha256(retained_material(condition).encode()) for condition in CONDITIONS},
        "model": MODEL,
        "model_digest": MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
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
        raise ClauseOrderRefusal("schedule_size_mismatch")
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
            (evidence_dir / "specimen.json").write_bytes(canonical_json_bytes(specimen()))
        self.physical = 0
        self.retries = 0
        self.attempts: list[dict[str, Any]] = []

    def call(self, logical_index: int, body: bytes) -> tuple[int | None, str | None, str, bool, object]:
        final = None
        for attempt in (1, 2):
            if self.physical >= PHYSICAL_CALL_CEILING:
                raise ClauseOrderRefusal("physical_call_ceiling")
            self.physical += 1
            status = None
            raw = b""
            error = None
            try:
                status, raw = self.transport(body)
            except ConnectionError as exc:
                error = str(exc)
            retryable = error is not None or status in {408, 429, 500, 502, 503, 504}
            invocation = f"cv{logical_index:03d}"
            meta = {
                "attempt": attempt,
                "error": error,
                "http_status": status,
                "invocation": invocation,
                "logical_index": logical_index,
                "request_sha256": sha256(body),
                "response_sha256": sha256(raw),
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
            raise ClauseOrderRefusal("logical_call_not_completed")
        status, error, raw = final
        content, available, provider = parse_content(raw, status)
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
        body = request_body(case, condition)
        status, error, content, content_available, usage = recorder.call(logical_index, body)
        availability, action = parse_action(content, state)
        if status != 200 or error is not None:
            availability, action = "unavailable", None
        provider_available = status == 200 and error is None and content_available
        proposal = ProposalReceipt(provider_available, (action or content) if provider_available else "")
        result = apply_committed_action(state, profile_for(case), proposal)
        material = retained_material(condition)
        calls.append({
            "action": action,
            "availability": availability,
            "case": case,
            "condition": condition,
            "correct_action": availability == "available" and action == oracle_action(state, profile_for(case)),
            "external_result": exposed_result(result),
            "invocation": f"cv{logical_index:03d}",
            "logical_index": logical_index,
            "proposal": asdict(proposal),
            "provider_usage": usage,
            "repeat": repeat,
            "request_sha256": sha256(body),
            "retained_material_sha256": sha256(material.encode()),
        })
    distributions = {
        condition: {
            case: _distribution([row for row in calls if row["condition"] == condition and row["case"] == case])
            for case in CASES
        }
        for condition in CONDITIONS
    }
    pairs = (
        ("increase_first_minus_empty", INCREASE_FIRST, EMPTY),
        ("decrease_first_minus_empty", DECREASE_FIRST, EMPTY),
        ("decrease_first_minus_increase_first", DECREASE_FIRST, INCREASE_FIRST),
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
        "comparisons": comparisons,
        "formation_verdict": None,
        "logical_calls": len(calls),
        "model": MODEL,
        "model_digest": MODEL_DIGEST,
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "request_distributions": distributions,
        "retries": recorder.retries,
        "specimen_sha256": sha256(canonical_json_bytes(specimen())),
        "validation_verdict": None,
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != canonical_json_bytes(specimen()):
        raise ClauseOrderRefusal("retained_specimen_mismatch")
    retained = json.loads((evidence_dir / "packet.json").read_bytes())
    entries = []
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        request = (evidence_dir / "attempts" / f"{stem}.request.json").read_bytes()
        response = (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes()
        if sha256(request) != meta["request_sha256"] or sha256(response) != meta["response_sha256"]:
            raise ClauseOrderRefusal("retained_attempt_hash_mismatch")
        entries.append((request, response, meta))
    position = 0

    def replay_transport(body: bytes) -> tuple[int, bytes]:
        nonlocal position
        if position >= len(entries):
            raise ClauseOrderRefusal("missing_retained_attempt")
        request, response, meta = entries[position]
        position += 1
        if request != body:
            raise ClauseOrderRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(replay_transport)
    if position != len(entries) or canonical_json_bytes(replayed) != canonical_json_bytes(retained):
        raise ClauseOrderRefusal("evidence_replay_mismatch")
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
        args.evidence_dir = Path("evidence") / f"retained-rule-clause-order-{stamp}"
    started = time.monotonic()
    receipt = collect_provider_receipt()
    if not receipt["valid"]:
        raise ClauseOrderRefusal("provider_identity_mismatch")
    packet = execute(live_transport, args.evidence_dir)
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
