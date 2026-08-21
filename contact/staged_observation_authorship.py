"""Test a model-written direct observation before full table authorship."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Callable

from contact import distributional_developmental_comparison as base
from contact import representation_class_exploration as forms
from micro_environment.unselected_lineage_behavior import SECOND_INCREASES, LineageProfile, LineageState, ProposalReceipt, apply_committed_action


PROTOCOL_VERSION = "staged-observation-authorship-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "STAGED_OBSERVATION_AUTHORSHIP.md"
WORLDS = tuple(f"world_{index:02d}" for index in range(1, 9))
DIRECT = "direct_raw"
STAGED = "staged_observation"
REMOVED = "observation_removed"
CONDITIONS = (DIRECT, STAGED, REMOVED)
REPEATS = 3
PLANNED_LOGICAL_CALLS = len(WORLDS) * 2 + len(WORLDS) * len(CONDITIONS) * REPEATS
PHYSICAL_CALL_CEILING = 96
MAX_RETRIES = 8


class StagedObservationRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


@dataclass(frozen=True)
class World:
    name: str
    profile: LineageProfile
    acquisition: LineageState


def make_world(name: str, index: int) -> World:
    profile = LineageProfile(opaque(f"{name}:family"), SECOND_INCREASES)
    position = 400 + index * 83
    up = index % 2 == 1
    return World(name, profile, LineageState(
        profile.controller_family,
        opaque(f"{name}:device"),
        position,
        position + (1 if up else -1),
        (opaque(f"{name}:first"), opaque(f"{name}:second")),
    ))


WORLD_DATA = {name: make_world(name, index) for index, name in enumerate(WORLDS, 1)}

OBSERVATION_SYSTEM = """You record one directly observed environment fact in a controlled cold-model experiment. You have no memory outside this request.

Read controller_family from occurrence.public_device. Read selected_slot and movement_direction from external_result.
Return exactly one JSON object with these keys in this order:
{"controller_family":"<controller_family>","observed_slot":"<first or second>","observed_effect":"<increases_position or decreases_position>"}
Use only the supplied fields. Return no markdown, commentary, action strings, or extra keys."""

STAGED_TABLE_SYSTEM = """You author a complete retained effect table in a controlled cold-model experiment. You have no memory outside this request.

The public device identifies the controller family. The model-authored observation states what one displayed slot did. Within one family, one displayed slot increases position and the other decreases it. Infer the unobserved slot from that complement.
Return exactly one JSON object with these keys in this order:
{"controller_family":"<controller_family>","first_displayed_control_effect":"<increases_position or decreases_position>","second_displayed_control_effect":"<decreases_position or increases_position>"}
Return no markdown, commentary, action strings, or extra keys."""


def expected_observation(world: World, selected_slot: str, movement: str) -> str:
    return json.dumps({
        "controller_family": world.profile.controller_family,
        "observed_slot": selected_slot,
        "observed_effect": "decreases_position" if movement == "decreased" else "increases_position",
    }, ensure_ascii=True, separators=(",", ":"))


def expected_table(world: World, opposite: bool = False) -> str:
    return forms.expected_representation(world, "effect_table", opposite=opposite)


def action_body(world: World) -> bytes:
    return base.action_body(world.acquisition, "")


def observation_body(world: World, proposal: ProposalReceipt, result: Any) -> bytes:
    record = {"external_result": base.exposed_result(result), "occurrence": base.occurrence(world.acquisition, proposal)}
    return base.envelope(OBSERVATION_SYSTEM, f"OBSERVATION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think", {**base.AUTHORSHIP_SETTINGS, "max_tokens": 128})


def final_body(world: World, proposal: ProposalReceipt, result: Any, observation: str, condition: str) -> bytes:
    if condition == DIRECT:
        record = {"external_result": base.exposed_result(result), "occurrence": base.occurrence(world.acquisition, proposal), "responsibility": "Author the complete effect table."}
        system = forms.AUTHORSHIP_SYSTEMS["effect_table"]
    else:
        record = {"authored_observation": observation if condition == STAGED else "", "public_device": base.public_device(world.acquisition), "responsibility": "Author the complete effect table."}
        system = STAGED_TABLE_SYSTEM
    return base.envelope(system, f"TABLE REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think", {**base.AUTHORSHIP_SETTINGS, "max_tokens": 160})


def specimen() -> dict[str, Any]:
    return {
        "conditions": list(CONDITIONS), "model": base.MODEL, "model_digest": base.MODEL_DIGEST,
        "observation_system_sha256": base.sha256(OBSERVATION_SYSTEM.encode()),
        "physical_call_ceiling": PHYSICAL_CALL_CEILING, "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION, "repeats": REPEATS,
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "staged_table_system_sha256": base.sha256(STAGED_TABLE_SYSTEM.encode()),
        "worlds": {name: {"acquisition": base.public_device(world.acquisition), "expected_table_sha256": base.sha256(expected_table(world).encode())} for name, world in WORLD_DATA.items()},
    }


def final_schedule():
    rows = []
    for repeat in range(1, REPEATS + 1):
        for offset in range(len(CONDITIONS)):
            condition = CONDITIONS[(repeat - 1 + offset) % len(CONDITIONS)]
            shift = (repeat + offset) % len(WORLDS)
            for name in WORLDS[shift:] + WORLDS[:shift]:
                rows.append((repeat, name, condition))
    return tuple(rows)


Transport = Callable[[bytes], tuple[int, bytes]]


class Recorder:
    def __init__(self, transport: Transport, evidence_dir: Path | None):
        self.transport = transport; self.attempts_dir = None; self.physical = 0; self.retries = 0; self.attempts = []
        if evidence_dir is not None:
            evidence_dir.mkdir(parents=True, exist_ok=False); self.attempts_dir = evidence_dir / "attempts"; self.attempts_dir.mkdir()
            (evidence_dir / "specimen.json").write_bytes(base.canonical_json_bytes(specimen()))

    def call(self, logical_index: int, body: bytes):
        final = None
        for attempt in (1, 2):
            if self.physical >= PHYSICAL_CALL_CEILING: raise StagedObservationRefusal("physical_call_ceiling")
            self.physical += 1; status, raw, error = None, b"", None
            try: status, raw = self.transport(body)
            except ConnectionError as exc: error = str(exc)
            retryable = error is not None or status in {408, 429, 500, 502, 503, 504}
            meta = {"attempt": attempt, "error": error, "http_status": status, "logical_index": logical_index, "request_sha256": base.sha256(body), "response_sha256": base.sha256(raw), "retryable": retryable}
            self.attempts.append(meta)
            if self.attempts_dir is not None:
                stem = f"{self.physical:03d}-so{logical_index:03d}-a{attempt}"; (self.attempts_dir / f"{stem}.request.json").write_bytes(body); (self.attempts_dir / f"{stem}.response.bin").write_bytes(raw); (self.attempts_dir / f"{stem}.meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
            if retryable and attempt == 1 and self.retries < MAX_RETRIES: self.retries += 1; continue
            final = status, error, raw; break
        if final is None: raise StagedObservationRefusal("logical_call_not_completed")
        status, error, raw = final; content, available, provider = base.parse_content(raw, status)
        return status, error, content, available, provider.get("usage")


def execute(transport: Transport, evidence_dir: Path | None = None):
    recorder = Recorder(transport, evidence_dir); calls = []; experiences = {}; observations = {}
    for index, name in enumerate(WORLDS, 1):
        world = WORLD_DATA[name]; body = action_body(world); status, error, content, ca, usage = recorder.call(index, body); availability, action = base.parse_action(content, world.acquisition)
        if status != 200 or error is not None: availability, action = "unavailable", None
        proposal = ProposalReceipt(status == 200 and error is None and ca, (action or content) if status == 200 and error is None and ca else ""); result = apply_committed_action(world.acquisition, world.profile, proposal); experiences[name] = proposal, result
        calls.append({"responsibility": "acquisition", "world": name, "action": action, "external_result": base.exposed_result(result), "provider_usage": usage, "request_sha256": base.sha256(body)})
    for index, name in enumerate(WORLDS, len(WORLDS) + 1):
        world = WORLD_DATA[name]; proposal, result = experiences[name]; body = observation_body(world, proposal, result); status, error, content, ca, usage = recorder.call(index, body); available = status == 200 and error is None and ca; result_fields = base.exposed_result(result); expected = expected_observation(world, result_fields.get("selected_slot", ""), result_fields.get("movement_direction", "")) if result_fields.get("selected_slot") in {"first", "second"} else ""; observation = content if available else ""; observations[name] = observation
        calls.append({"responsibility": "observation_authorship", "world": name, "content": observation, "exact_observation": observation == expected, "provider_usage": usage, "request_sha256": base.sha256(body)})
    finals = []
    for index, (repeat, name, condition) in enumerate(final_schedule(), len(WORLDS) * 2 + 1):
        world = WORLD_DATA[name]; proposal, result = experiences[name]; body = final_body(world, proposal, result, observations[name], condition); status, error, content, ca, usage = recorder.call(index, body); available = status == 200 and error is None and ca
        row = {"responsibility": "table_authorship", "world": name, "condition": condition, "repeat": repeat, "content": content if available else "", "available": available, "exact_correct": available and content == expected_table(world), "provider_usage": usage, "request_sha256": base.sha256(body)}; finals.append(row); calls.append(row)
    distributions = {name: {condition: {"assigned": len(rows := [r for r in finals if r["world"] == name and r["condition"] == condition]), "exact_correct": sum(r["exact_correct"] for r in rows), "invalid_or_unavailable": sum(not r["available"] for r in rows), "distinct_contents": len(Counter(r["content"] for r in rows))} for condition in CONDITIONS} for name in WORLDS}
    result_fields = {name: base.exposed_result(experiences[name][1]) for name in WORLDS}; slots = Counter(r.get("selected_slot", "unavailable") for r in result_fields.values()); exact_observations = sum(c["exact_observation"] for c in calls if c["responsibility"] == "observation_authorship"); engaged = slots["first"] >= 2 and slots["second"] >= 2 and exact_observations >= 7
    supported = engaged; second_improvements = 0
    for name in WORLDS:
        staged, direct, removed = (distributions[name][key] for key in (STAGED, DIRECT, REMOVED)); supported &= staged["exact_correct"] >= 2 and staged["exact_correct"] - removed["exact_correct"] >= 2 and staged["exact_correct"] >= direct["exact_correct"] and staged["invalid_or_unavailable"] <= 1
        if result_fields[name].get("selected_slot") == "second" and staged["exact_correct"] - direct["exact_correct"] >= 2: second_improvements += 1
    supported &= second_improvements >= 3
    verdict = {"class": "not_engaged" if not engaged else "candidate_found" if supported else "null", "scope": "staged_observation_authorship"}
    packet = {"attempts": recorder.attempts, "calls": calls, "exact_observations": exact_observations, "formation_verdict": None, "logical_calls": len(calls), "model": base.MODEL, "model_digest": base.MODEL_DIGEST, "physical_attempts": recorder.physical, "protocol_version": PROTOCOL_VERSION, "request_distributions": distributions, "retries": recorder.retries, "selected_slot_counts": dict(sorted(slots.items())), "staged_authorship_verdict": verdict, "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen()))}
    if evidence_dir is not None: (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path):
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()): raise StagedObservationRefusal("retained_specimen_mismatch")
    packet_name = "packet.corrected.json" if (evidence_dir / "packet.corrected.json").exists() else "packet.json"
    retained = json.loads((evidence_dir / packet_name).read_bytes()); entries = []
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json"); meta = json.loads(meta_path.read_text()); req = (evidence_dir / "attempts" / f"{stem}.request.json").read_bytes(); res = (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes(); entries.append((req, res, meta))
    pos = 0
    def transport(body):
        nonlocal pos
        req, res, meta = entries[pos]; pos += 1
        if req != body: raise StagedObservationRefusal("retained_request_mismatch")
        if meta["error"] is not None: raise ConnectionError(meta["error"])
        return meta["http_status"], res
    replayed = execute(transport)
    if pos != len(entries) or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained): raise StagedObservationRefusal("evidence_replay_mismatch")
    return replayed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--live", action="store_true"); parser.add_argument("--evidence-dir", type=Path); args = parser.parse_args(argv)
    if not args.live: print(json.dumps({"mode": "smoke_no_contact", "planned_logical_calls": PLANNED_LOGICAL_CALLS, "side_effects_entered": False}, sort_keys=True)); return 0
    if args.evidence_dir is None: args.evidence_dir = Path("evidence") / f"staged-observation-authorship-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    started = time.monotonic(); receipt = base.collect_provider_receipt()
    if not receipt["valid"]: raise StagedObservationRefusal("provider_identity_mismatch")
    packet = execute(base.live_transport, args.evidence_dir); (args.evidence_dir / "provider.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n"); replay_evidence(args.evidence_dir)
    print(json.dumps({"elapsed_seconds": time.monotonic() - started, "evidence_dir": str(args.evidence_dir), "logical_calls": packet["logical_calls"], "physical_attempts": packet["physical_attempts"], "staged_authorship_verdict": packet["staged_authorship_verdict"]}, sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
