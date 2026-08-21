"""Execute the frozen canonical mapping scope-gate successor validation."""

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

from contact import candidate_nontransfer_sweep as sweep
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


PROTOCOL_VERSION = "canonical-mapping-scope-gate-validation-v1"
SOURCE_EVIDENCE = Path(__file__).parents[1] / "evidence" / "canonical-mapping-candidate-validation-20260820T000646Z"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "CANONICAL_MAPPING_SCOPE_GATE_VALIDATION.md"
ABLATION = "candidate_ablation"
UNGATED = "candidate_ungated"
SCOPED = "candidate_scoped"
CONDITIONS = (ABLATION, UNGATED, SCOPED)
CASES = ("same_up", "same_down", "other_up", "other_down")
WORLDS = ("world_a", "world_b")
REPEATS = 4
PLANNED_LOGICAL_CALLS = len(WORLDS) * len(CONDITIONS) * len(CASES) * REPEATS
PHYSICAL_CALL_CEILING = 100


class ScopeGateValidationRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


def load_sources() -> tuple[dict[str, str], dict[str, str], str]:
    raw = (SOURCE_EVIDENCE / "packet.json").read_bytes()
    packet = json.loads(raw)
    specimen = json.loads((SOURCE_EVIDENCE / "specimen.json").read_bytes())
    candidates = {
        row["world"]: row["content"]
        for row in packet["candidates"]
        if row["exposure"] == "result_exposed" and row["exact_static_match"]
    }
    families = {name: specimen["worlds"][name]["acquisition"]["controller_family"] for name in WORLDS}
    if set(candidates) != set(WORLDS):
        raise ScopeGateValidationRefusal("source_candidates_mismatch")
    return candidates, families, base.sha256(raw)


CANDIDATES, SOURCE_FAMILIES, SOURCE_PACKET_SHA256 = load_sources()
SOURCE_PROFILES = {name: LineageProfile(SOURCE_FAMILIES[name], SECOND_INCREASES) for name in WORLDS}
OTHER_PROFILES = {name: LineageProfile(opaque(f"{name}:other-family"), FIRST_INCREASES) for name in WORLDS}


def make_state(name: str, case: str, index: int) -> LineageState:
    source = case.startswith("same_")
    family = SOURCE_FAMILIES[name] if source else OTHER_PROFILES[name].controller_family
    up = case.endswith("up")
    position = 240 + index * 71
    return LineageState(
        family,
        opaque(f"{name}:{case}:device"),
        position,
        position + (1 if up else -1),
        (opaque(f"{name}:{case}:first"), opaque(f"{name}:{case}:second")),
    )


CASE_STATES = {
    name: {case: make_state(name, case, world_index * 4 + case_index) for case_index, case in enumerate(CASES, 1)}
    for world_index, name in enumerate(WORLDS)
}


def profile_for(name: str, case: str) -> LineageProfile:
    return SOURCE_PROFILES[name] if case.startswith("same_") else OTHER_PROFILES[name]


def delivered(name: str, case: str, condition: str) -> str:
    if condition == ABLATION:
        return ""
    if condition == UNGATED:
        return CANDIDATES[name]
    if condition == SCOPED:
        state = CASE_STATES[name][case]
        return CANDIDATES[name] if state.controller_family == SOURCE_FAMILIES[name] else ""
    raise ScopeGateValidationRefusal("unknown_condition")


def request_body(name: str, case: str, condition: str) -> bytes:
    state = CASE_STATES[name][case]
    record = {
        "device": base.public_device(state),
        "responsibility": ACTION_RESPONSIBILITY,
        "retained_material": delivered(name, case, condition),
    }
    user = f"ACTION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think"
    return base.envelope(base.ACTION_SYSTEM, user, base.ACTION_SETTINGS)


def specimen() -> dict[str, Any]:
    return {
        "candidates": {name: base.sha256(value.encode()) for name, value in CANDIDATES.items()},
        "cases": {
            name: {
                case: {
                    "device": base.public_device(state),
                    "expected_action": oracle_action(state, profile_for(name, case)),
                }
                for case, state in cases.items()
            }
            for name, cases in CASE_STATES.items()
        },
        "conditions": list(CONDITIONS),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "source_packet_sha256": SOURCE_PACKET_SHA256,
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
    }


def schedule() -> tuple[tuple[int, str, str, str], ...]:
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_offset in range(len(CASES)):
            case = CASES[(repeat - 1 + case_offset) % len(CASES)]
            for condition_offset in range(len(CONDITIONS)):
                condition = CONDITIONS[(repeat - 1 + condition_offset) % len(CONDITIONS)]
                order = WORLDS if (repeat + case_offset + condition_offset) % 2 else tuple(reversed(WORLDS))
                for name in order:
                    rows.append((repeat, name, case, condition))
    return tuple(rows)


Transport = Callable[[bytes], tuple[int, bytes]]


class Recorder(sweep.Recorder):
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
        self.attempts = []


def _distribution(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "assigned": len(rows),
        "correct_actions": sum(bool(row["correct_action"]) for row in rows),
        "invalid_or_unavailable": sum(row["availability"] != "available" for row in rows),
        "distinct_outcomes": len(Counter(row["action"] or f"<{row['availability']}>" for row in rows)),
    }


def _verdict(distributions: dict[str, dict[str, dict[str, dict[str, int]]]]) -> dict[str, str]:
    for name in WORLDS:
        for case in ("same_up", "same_down"):
            if distributions[name][UNGATED][case]["correct_actions"] < 3:
                return {"class": "not_engaged", "scope": "candidate_scope_gate"}
        for case in ("other_up", "other_down"):
            if distributions[name][SCOPED][case]["correct_actions"] <= distributions[name][ABLATION][case]["correct_actions"] - 2:
                return {"class": "harmful", "scope": "candidate_scope_gate"}
    supported = True
    for name in WORLDS:
        for case in ("same_up", "same_down"):
            scoped = distributions[name][SCOPED][case]["correct_actions"]
            supported &= scoped >= 3
            supported &= scoped - distributions[name][ABLATION][case]["correct_actions"] >= 3
            supported &= abs(scoped - distributions[name][UNGATED][case]["correct_actions"]) <= 1
        for case in ("other_up", "other_down"):
            supported &= distributions[name][SCOPED][case]["correct_actions"] >= distributions[name][ABLATION][case]["correct_actions"] - 1
        supported &= distributions[name][SCOPED]["other_down"]["correct_actions"] - distributions[name][UNGATED]["other_down"]["correct_actions"] >= 3
        for condition in CONDITIONS:
            for case in CASES:
                supported &= distributions[name][condition][case]["invalid_or_unavailable"] <= 1
    return {"class": "supported" if supported else "null", "scope": "candidate_scope_gate"}


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    recorder = Recorder(transport, evidence_dir)
    calls = []
    for logical_index, (repeat, name, case, condition) in enumerate(schedule(), 1):
        state = CASE_STATES[name][case]
        body = request_body(name, case, condition)
        status, error, content, content_available, usage = recorder.call(logical_index, body)
        availability, action = base.parse_action(content, state)
        if status != 200 or error is not None:
            availability, action = "unavailable", None
        provider_available = status == 200 and error is None and content_available
        proposal = ProposalReceipt(provider_available, (action or content) if provider_available else "")
        result = apply_committed_action(state, profile_for(name, case), proposal)
        calls.append({
            "action": action,
            "availability": availability,
            "case": case,
            "condition": condition,
            "correct_action": availability == "available" and action == oracle_action(state, profile_for(name, case)),
            "external_result": base.exposed_result(result),
            "invocation": f"gv{logical_index:03d}",
            "logical_index": logical_index,
            "proposal": asdict(proposal),
            "provider_usage": usage,
            "repeat": repeat,
            "request_sha256": base.sha256(body),
            "world": name,
        })
    distributions = {
        name: {
            condition: {
                case: _distribution([row for row in calls if row["world"] == name and row["condition"] == condition and row["case"] == case])
                for case in CASES
            }
            for condition in CONDITIONS
        }
        for name in WORLDS
    }
    verdict = _verdict(distributions)
    packet = {
        "attempts": recorder.attempts,
        "calls": calls,
        "formation_verdict": None,
        "logical_calls": len(calls),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "request_distributions": distributions,
        "retries": recorder.retries,
        "scope_gate_validation_verdict": verdict,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "validation_verdict": verdict,
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise ScopeGateValidationRefusal("retained_specimen_mismatch")
    retained = json.loads((evidence_dir / "packet.json").read_bytes())
    entries = []
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        meta = json.loads(meta_path.read_text())
        request = (evidence_dir / "attempts" / f"{stem}.request.json").read_bytes()
        response = (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes()
        entries.append((request, response, meta))
    position = 0
    def replay_transport(body: bytes) -> tuple[int, bytes]:
        nonlocal position
        request, response, meta = entries[position]
        position += 1
        if request != body or base.sha256(response) != meta["response_sha256"]:
            raise ScopeGateValidationRefusal("retained_attempt_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response
    replayed = execute(replay_transport)
    if position != len(entries) or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained):
        raise ScopeGateValidationRefusal("evidence_replay_mismatch")
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
        args.evidence_dir = Path("evidence") / f"canonical-mapping-scope-gate-validation-{stamp}"
    started = time.monotonic()
    receipt = base.collect_provider_receipt()
    if not receipt["valid"]:
        raise ScopeGateValidationRefusal("provider_identity_mismatch")
    packet = execute(base.live_transport, args.evidence_dir)
    (args.evidence_dir / "provider.json").write_text(json.dumps(receipt, ensure_ascii=True, indent=2, sort_keys=True) + "\n")
    replay_evidence(args.evidence_dir)
    print(json.dumps({"elapsed_seconds": time.monotonic() - started, "evidence_dir": str(args.evidence_dir), "logical_calls": packet["logical_calls"], "physical_attempts": packet["physical_attempts"], "scope_gate_validation_verdict": packet["scope_gate_validation_verdict"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
