"""Test whether a generic consumption instruction engages retained material.

Prospective exploratory note
----------------------------
Question: does explicitly telling the cold action model how to evaluate the
``retained_material`` field make a static controller-family rule change action
distributions, while leaving an opposite-profile family unaffected?
Observation of interest: the interaction between interface wording (implicit
or explicit consumption) and retained content (empty or static rule) across
same-family upward and downward cases plus one non-transfer family.
Model/interface: exact ``ai/qwen3:14B-Q6_K`` Docker Model Runner artifact. The
explicit interface adds one generic consumption paragraph and no mapping,
action token, or case answer.
Budget: four conditions by three fresh cases by eight repeats; 96 logical calls
and at most 100 physical attempts. Only transport failures may be retried, at
most four times.
Stopping condition: stop after the fixed schedule or either ceiling. Preserve
malformed and unavailable outputs.
Evidence destination: ``evidence/retained-material-consumption-<run-id>/``.

This is an interface trial. Success would show selective content-mediated
influence, not formation or acquired competence.
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
    ACTION_SYSTEM as IMPLICIT_SYSTEM,
    ENDPOINT,
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
    HOLD,
    SECOND_INCREASES,
    LineageProfile,
    LineageState,
    ProposalReceipt,
    apply_committed_action,
)
from unselected_lineage_specimen import ACTION_RESPONSIBILITY, oracle_action


PROTOCOL_VERSION = "retained-material-consumption-trial-v1"
IMPLICIT_EMPTY = "implicit_empty"
IMPLICIT_STATIC = "implicit_static"
EXPLICIT_EMPTY = "explicit_empty"
EXPLICIT_STATIC = "explicit_static"
CONDITIONS = (IMPLICIT_EMPTY, IMPLICIT_STATIC, EXPLICIT_EMPTY, EXPLICIT_STATIC)
CASES = ("same_family_up", "same_family_down", "other_family_up")
REPEATS = 8
PLANNED_LOGICAL_CALLS = len(CONDITIONS) * len(CASES) * REPEATS
PHYSICAL_CALL_CEILING = 100
MAX_RETRIES = 4

EXPLICIT_SYSTEM = IMPLICIT_SYSTEM + """

RETAINED MATERIAL
The request contains a retained_material field. It may be empty, irrelevant, or a rule derived from prior experience. Before choosing an action, evaluate whether that material applies to the current controller_family. Use applicable material and ignore material scoped to another family. Do not copy action strings from another device."""


class ConsumptionRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


PRIMARY_PROFILE = LineageProfile(opaque("primary-family"), SECOND_INCREASES)
OTHER_PROFILE = LineageProfile(opaque("other-family"), FIRST_INCREASES)
CASE_STATES = {
    "same_family_up": LineageState(
        PRIMARY_PROFILE.controller_family,
        opaque("same-up-device"),
        271,
        272,
        (opaque("same-up-first"), opaque("same-up-second")),
    ),
    "same_family_down": LineageState(
        PRIMARY_PROFILE.controller_family,
        opaque("same-down-device"),
        946,
        945,
        (opaque("same-down-first"), opaque("same-down-second")),
    ),
    "other_family_up": LineageState(
        OTHER_PROFILE.controller_family,
        opaque("other-up-device"),
        538,
        539,
        (opaque("other-up-first"), opaque("other-up-second")),
    ),
}


def profile_for(case: str) -> LineageProfile:
    return OTHER_PROFILE if case == "other_family_up" else PRIMARY_PROFILE


def static_instruction() -> str:
    return (
        f"For controller family {PRIMARY_PROFILE.controller_family}, the second displayed control "
        "increases position and the first displayed control decreases position."
    )


def condition_surface(condition: str) -> tuple[str, str]:
    if condition not in CONDITIONS:
        raise ConsumptionRefusal("unknown_condition")
    system = EXPLICIT_SYSTEM if condition in (EXPLICIT_EMPTY, EXPLICIT_STATIC) else IMPLICIT_SYSTEM
    material = static_instruction() if condition in (IMPLICIT_STATIC, EXPLICIT_STATIC) else ""
    return system, material


def request_body(case: str, condition: str) -> bytes:
    state = CASE_STATES[case]
    system, material = condition_surface(condition)
    record = {
        "device": public_device(state),
        "responsibility": ACTION_RESPONSIBILITY,
        "retained_material": material,
    }
    user = f"ACTION REQUEST\n{canonical_json_bytes(record).decode()}\n/no_think"
    return canonical_json_bytes({
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
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
        "explicit_instruction_sha256": sha256(EXPLICIT_SYSTEM.encode()),
        "model": MODEL,
        "model_digest": MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "static_instruction_sha256": sha256(static_instruction().encode()),
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
        raise ConsumptionRefusal("schedule_size_mismatch")
    return tuple(rows)


Transport = Callable[[bytes], tuple[int, bytes]]


class Recorder:
    def __init__(self, transport: Transport, evidence_dir: Path | None) -> None:
        self.transport = transport
        self.evidence_dir = evidence_dir
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
                raise ConsumptionRefusal("physical_call_ceiling")
            self.physical += 1
            status = None
            raw = b""
            error = None
            try:
                status, raw = self.transport(body)
            except ConnectionError as exc:
                error = str(exc)
            retryable = error is not None or status in {408, 429, 500, 502, 503, 504}
            invocation = f"rv{logical_index:03d}"
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
            raise ConsumptionRefusal("logical_call_not_completed")
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
        proposal_content = (action or content) if provider_available else ""
        proposal = ProposalReceipt(provider_available, proposal_content)
        result = apply_committed_action(state, profile_for(case), proposal)
        _, material = condition_surface(condition)
        calls.append({
            "action": action,
            "availability": availability,
            "case": case,
            "condition": condition,
            "correct_action": availability == "available" and action == oracle_action(state, profile_for(case)),
            "external_result": exposed_result(result),
            "invocation": f"rv{logical_index:03d}",
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
        ("implicit_static_minus_empty", IMPLICIT_STATIC, IMPLICIT_EMPTY),
        ("explicit_static_minus_empty", EXPLICIT_STATIC, EXPLICIT_EMPTY),
        ("explicit_empty_minus_implicit_empty", EXPLICIT_EMPTY, IMPLICIT_EMPTY),
        ("explicit_static_minus_implicit_static", EXPLICIT_STATIC, IMPLICIT_STATIC),
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
        raise ConsumptionRefusal("retained_specimen_mismatch")
    retained = json.loads((evidence_dir / "packet.json").read_bytes())
    entries = []
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        request = (evidence_dir / "attempts" / f"{stem}.request.json").read_bytes()
        response = (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes()
        if sha256(request) != meta["request_sha256"] or sha256(response) != meta["response_sha256"]:
            raise ConsumptionRefusal("retained_attempt_hash_mismatch")
        entries.append((request, response, meta))
    position = 0

    def replay_transport(body: bytes) -> tuple[int, bytes]:
        nonlocal position
        if position >= len(entries):
            raise ConsumptionRefusal("missing_retained_attempt")
        request, response, meta = entries[position]
        position += 1
        if request != body:
            raise ConsumptionRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(replay_transport)
    if position != len(entries) or canonical_json_bytes(replayed) != canonical_json_bytes(retained):
        raise ConsumptionRefusal("evidence_replay_mismatch")
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
        args.evidence_dir = Path("evidence") / f"retained-material-consumption-{stamp}"
    started = time.monotonic()
    receipt = collect_provider_receipt()
    if not receipt["valid"]:
        raise ConsumptionRefusal("provider_identity_mismatch")
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
