"""Test whether consequence exposure produces two usable lesson forms."""

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
from contact import representation_class_exploration as forms
from micro_environment.unselected_lineage_behavior import SECOND_INCREASES, LineageProfile, LineageState, ProposalReceipt, apply_committed_action
from unselected_lineage_specimen import oracle_action


PROTOCOL_VERSION = "lesson-authorship-calibration-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "LESSON_AUTHORSHIP_CALIBRATION.md"
FORMATS = ("relation_sentence", "effect_table")
EXPOSURES = (forms.EXPOSED, forms.WITHHELD)
WORLDS = tuple(f"world_{index:02d}" for index in range(1, 9))
REPEATS = 3
PLANNED_LOGICAL_CALLS = len(WORLDS) + len(WORLDS) * len(FORMATS) * len(EXPOSURES) * REPEATS
PHYSICAL_CALL_CEILING = 112
MAX_RETRIES = 8


class LessonAuthorshipRefusal(ValueError):
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
    position = 300 + index * 79
    target_up = index % 2 == 1
    state = LineageState(
        profile.controller_family,
        opaque(f"{name}:device"),
        position,
        position + (1 if target_up else -1),
        (opaque(f"{name}:first"), opaque(f"{name}:second")),
    )
    return World(name, profile, state)


WORLD_DATA = {name: make_world(name, index) for index, name in enumerate(WORLDS, 1)}


def expected(world: World, representation_format: str, opposite: bool = False) -> str:
    return forms.expected_representation(world, representation_format, opposite=opposite)


def action_body(world: World) -> bytes:
    return base.action_body(world.acquisition, "")


def authorship_body(world: World, proposal: ProposalReceipt, result: Any, exposure: str, representation_format: str) -> bytes:
    record = {
        "external_result": base.exposed_result(result) if exposure == forms.EXPOSED else forms.WITHHELD_SENTINEL,
        "occurrence": base.occurrence(world.acquisition, proposal),
        "responsibility": "Author the requested retained representation from this record.",
    }
    user = f"AUTHORSHIP REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think"
    return base.envelope(forms.AUTHORSHIP_SYSTEMS[representation_format], user, {**base.AUTHORSHIP_SETTINGS, "max_tokens": 160})


def specimen() -> dict[str, Any]:
    return {
        "formats": list(FORMATS),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "worlds": {
            name: {
                "acquisition": base.public_device(world.acquisition),
                "expected": {key: base.sha256(expected(world, key).encode()) for key in FORMATS},
            }
            for name, world in WORLD_DATA.items()
        },
    }


def authorship_schedule() -> tuple[tuple[int, str, str, str], ...]:
    rows = []
    for repeat in range(1, REPEATS + 1):
        for format_offset in range(len(FORMATS)):
            representation_format = FORMATS[(repeat - 1 + format_offset) % len(FORMATS)]
            for exposure_offset in range(len(EXPOSURES)):
                exposure = EXPOSURES[(repeat - 1 + exposure_offset) % len(EXPOSURES)]
                shift = (repeat + format_offset + exposure_offset) % len(WORLDS)
                for name in WORLDS[shift:] + WORLDS[:shift]:
                    rows.append((repeat, name, representation_format, exposure))
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
        self.attempts = []

    def call(self, logical_index: int, body: bytes):
        final = None
        for attempt in (1, 2):
            if self.physical >= PHYSICAL_CALL_CEILING:
                raise LessonAuthorshipRefusal("physical_call_ceiling")
            self.physical += 1
            status, raw, error = None, b"", None
            try:
                status, raw = self.transport(body)
            except ConnectionError as exc:
                error = str(exc)
            retryable = error is not None or status in {408, 429, 500, 502, 503, 504}
            meta = {
                "attempt": attempt, "error": error, "http_status": status,
                "invocation": f"la{logical_index:03d}", "logical_index": logical_index,
                "request_sha256": base.sha256(body), "response_sha256": base.sha256(raw), "retryable": retryable,
            }
            self.attempts.append(meta)
            if self.attempts_dir is not None:
                stem = f"{self.physical:03d}-la{logical_index:03d}-a{attempt}"
                (self.attempts_dir / f"{stem}.request.json").write_bytes(body)
                (self.attempts_dir / f"{stem}.response.bin").write_bytes(raw)
                (self.attempts_dir / f"{stem}.meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
            if retryable and attempt == 1 and self.retries < MAX_RETRIES:
                self.retries += 1
                continue
            final = status, error, raw
            break
        if final is None:
            raise LessonAuthorshipRefusal("logical_call_not_completed")
        status, error, raw = final
        content, available, provider = base.parse_content(raw, status)
        return status, error, content, available, provider.get("usage")


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    recorder = Recorder(transport, evidence_dir)
    calls, experiences = [], {}
    for logical_index, name in enumerate(WORLDS, 1):
        world = WORLD_DATA[name]
        body = action_body(world)
        status, error, content, content_available, usage = recorder.call(logical_index, body)
        availability, action = base.parse_action(content, world.acquisition)
        if status != 200 or error is not None:
            availability, action = "unavailable", None
        provider_available = status == 200 and error is None and content_available
        proposal = ProposalReceipt(provider_available, (action or content) if provider_available else "")
        result = apply_committed_action(world.acquisition, world.profile, proposal)
        experiences[name] = proposal, result
        calls.append({
            "action": action, "availability": availability,
            "correct_action": availability == "available" and action == oracle_action(world.acquisition, world.profile),
            "external_result": base.exposed_result(result), "logical_index": logical_index,
            "provider_usage": usage, "request_sha256": base.sha256(body),
            "responsibility": "acquisition_action", "world": name,
        })
    authored = []
    for logical_index, (repeat, name, representation_format, exposure) in enumerate(authorship_schedule(), len(WORLDS) + 1):
        world = WORLD_DATA[name]
        proposal, result = experiences[name]
        body = authorship_body(world, proposal, result, exposure, representation_format)
        status, error, content, content_available, usage = recorder.call(logical_index, body)
        available = status == 200 and error is None and content_available
        row = {
            "available": available, "content": content if available else "",
            "exact_correct": available and content == expected(world, representation_format),
            "exact_opposite": available and content == expected(world, representation_format, opposite=True),
            "exposure": exposure, "format": representation_format, "logical_index": logical_index,
            "provider_usage": usage, "repeat": repeat, "request_sha256": base.sha256(body),
            "responsibility": "lesson_authorship", "world": name,
        }
        authored.append(row); calls.append(row)
    distributions = {
        name: {fmt: {exposure: {
            "assigned": len(rows := [r for r in authored if r["world"] == name and r["format"] == fmt and r["exposure"] == exposure]),
            "exact_correct": sum(r["exact_correct"] for r in rows),
            "exact_opposite": sum(r["exact_opposite"] for r in rows),
            "invalid_or_unavailable": sum(not r["available"] for r in rows),
            "distinct_contents": len(Counter(r["content"] for r in rows)),
        } for exposure in EXPOSURES} for fmt in FORMATS} for name in WORLDS
    }
    slots = Counter(base.exposed_result(experiences[name][1]).get("selected_slot", "unavailable") for name in WORLDS)
    engaged = slots["first"] >= 2 and slots["second"] >= 2
    findings = {}
    for fmt in FORMATS:
        failures = []
        for name in WORLDS:
            exposed = distributions[name][fmt][forms.EXPOSED]
            withheld = distributions[name][fmt][forms.WITHHELD]
            if not (exposed["exact_correct"] >= 2 and exposed["exact_correct"] - withheld["exact_correct"] >= 2 and exposed["invalid_or_unavailable"] <= 1 and withheld["invalid_or_unavailable"] <= 1):
                failures.append(name)
        findings[fmt] = {"failures": failures, "status": "authorship_candidate" if engaged and not failures else "not_reliable"}
    verdict = {"class": "not_engaged" if not engaged else "candidate_found" if any(v["status"] == "authorship_candidate" for v in findings.values()) else "null", "scope": "lesson_authorship_calibration"}
    packet = {
        "attempts": recorder.attempts, "calls": calls, "authorship_distributions": distributions,
        "authorship_findings": findings, "authorship_verdict": verdict, "formation_verdict": None,
        "logical_calls": len(calls), "model": base.MODEL, "model_digest": base.MODEL_DIGEST,
        "physical_attempts": recorder.physical, "protocol_version": PROTOCOL_VERSION,
        "retries": recorder.retries, "selected_slot_counts": dict(sorted(slots.items())),
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise LessonAuthorshipRefusal("retained_specimen_mismatch")
    retained = json.loads((evidence_dir / "packet.json").read_bytes())
    entries = []
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json"); meta = json.loads(meta_path.read_text())
        request = (evidence_dir / "attempts" / f"{stem}.request.json").read_bytes(); response = (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes()
        if base.sha256(request) != meta["request_sha256"] or base.sha256(response) != meta["response_sha256"]:
            raise LessonAuthorshipRefusal("retained_attempt_hash_mismatch")
        entries.append((request, response, meta))
    position = 0
    def transport(body: bytes):
        nonlocal position
        request, response, meta = entries[position]; position += 1
        if request != body: raise LessonAuthorshipRefusal("retained_request_mismatch")
        if meta["error"] is not None: raise ConnectionError(meta["error"])
        return meta["http_status"], response
    replayed = execute(transport)
    if position != len(entries) or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained):
        raise LessonAuthorshipRefusal("evidence_replay_mismatch")
    return replayed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--live", action="store_true"); parser.add_argument("--evidence-dir", type=Path); args = parser.parse_args(argv)
    if not args.live:
        print(json.dumps({"mode": "smoke_no_contact", "planned_logical_calls": PLANNED_LOGICAL_CALLS, "side_effects_entered": False}, sort_keys=True)); return 0
    if args.evidence_dir is None:
        args.evidence_dir = Path("evidence") / f"lesson-authorship-calibration-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    started = time.monotonic(); receipt = base.collect_provider_receipt()
    if not receipt["valid"]: raise LessonAuthorshipRefusal("provider_identity_mismatch")
    packet = execute(base.live_transport, args.evidence_dir)
    (args.evidence_dir / "provider.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    replay_evidence(args.evidence_dir)
    print(json.dumps({"authorship_verdict": packet["authorship_verdict"], "elapsed_seconds": time.monotonic() - started, "evidence_dir": str(args.evidence_dir), "logical_calls": packet["logical_calls"], "physical_attempts": packet["physical_attempts"]}, sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
