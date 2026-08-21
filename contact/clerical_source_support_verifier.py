"""Run the restricted clerical source-support verifier exploration."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any, Callable

from contact import distributional_developmental_comparison as base
from contact import learned_clerical_instrument_exploration as learned
from contact import source_grounded_revision_admission as admission


PROTOCOL_VERSION = "clerical-source-support-verifier-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "CLERICAL_SOURCE_SUPPORT_VERIFIER.md"
PAIR_CLASSES = (
    "old_supported",
    "revision_supported",
    "stale_contradicted",
    "missing_movement",
)
SUPPORTED = "supported"
UNSUPPORTED = "unsupported"
REPEATS = 3
PLANNED_LOGICAL_CALLS = 48
PHYSICAL_CALL_CEILING = 56
MAX_RETRIES = 8

VERIFIER_SETTINGS = {
    "max_tokens": 32,
    "response_format": {"type": "json_object"},
    "stream": False,
    "temperature": 0.2,
    "top_p": 0.9,
}

VERIFIER_SYSTEM = """You are a clerical source-support verifier. You have no memory outside this request.

You receive one sensory report about a device action and one proposed effect record. You do not receive a later action request, controls, position, target, expected action, or score.

Exactly one displayed control increases position and the other decreases it. A selected control observed with a rising gauge supports increases_position for that control. A selected control observed with a falling gauge supports decreases_position for that control. The other control must have the opposite effect.

Return supported only when the source contains both the selected displayed actuator and gauge movement and those measurements support both fields of the proposed record. Return unsupported when a measurement is unavailable or a claimed effect contradicts the measurement.

Return exactly one JSON object with the single key source_support. Its value must be supported or unsupported. Do not add commentary."""


class VerifierRefusal(ValueError):
    pass


@dataclass(frozen=True)
class Pair:
    pair_class: str
    lineage: str
    design_position: str
    sensory_request_sha256: str
    source_occurrence_sha256: str
    sensory_report: dict[str, str]
    proposed_record: dict[str, str]
    expected_label: str

    @property
    def pair_id(self) -> str:
        return admission.sha256(admission.canonical({
            "design_position": self.design_position,
            "lineage": self.lineage,
            "pair_class": self.pair_class,
            "proposed_record": self.proposed_record,
            "sensory_request_sha256": self.sensory_request_sha256,
        }))[:20]


def verification_body(pair: Pair) -> bytes:
    record = {
        "proposed_effect_record": pair.proposed_record,
        "source_sensory_report": pair.sensory_report,
    }
    return learned.canonical_envelope(
        learned.INSTRUMENT_MODEL,
        VERIFIER_SYSTEM,
        f"SOURCE SUPPORT REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",
        VERIFIER_SETTINGS,
    )


def parse_label(content: str) -> tuple[str, str | None]:
    try:
        value = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return "invalid", None
    if (
        type(value) is not dict
        or set(value) != {"source_support"}
        or value["source_support"] not in {SUPPORTED, UNSUPPORTED}
    ):
        return "invalid", None
    return "available", value["source_support"]


def request_report(requests: dict[str, bytes], request_sha: str) -> dict[str, str]:
    try:
        request_bytes = requests[request_sha]
    except KeyError as exc:
        raise VerifierRefusal("missing_source_request") from exc
    _, report = admission.parse_request_record(request_bytes)
    return report


def source_call(
    packet: dict[str, Any], responsibility: str, lineage: str, position: str,
    condition: str | None = None,
) -> dict[str, Any]:
    matches = [
        row
        for row in packet["calls"]
        if row["responsibility"] == responsibility
        and row["lineage"] == lineage
        and row["design_position"] == position
        and (condition is None or row.get("consequence_condition") == condition)
    ]
    if len(matches) != 1:
        raise VerifierRefusal("source_call_set_mismatch")
    return matches[0]


def load_pairs() -> tuple[Pair, ...]:
    packet, requests = admission.load_source()
    pairs = []
    for lineage in admission.LINEAGES:
        for position in admission.DESIGN_POSITIONS:
            old_version = packet["record_versions"][lineage][position][0]
            revised_version = packet["record_versions"][lineage][position][1]
            hidden_version = packet["hidden_comparator_versions"][lineage][position][1]
            old_call = source_call(packet, "old_transcription", lineage, position)
            revised_call = source_call(
                packet, "revision_transcription", lineage, position, "revised"
            )
            hidden_call = source_call(
                packet, "revision_transcription", lineage, position, "hidden"
            )
            old_source_hash = old_version["source_occurrence"]["external_result_sha256"]
            counter_source_hash = revised_version["source_occurrence"]["external_result_sha256"]
            rows = (
                (
                    "old_supported", old_call, old_source_hash,
                    old_version["record"], SUPPORTED,
                ),
                (
                    "revision_supported", revised_call, counter_source_hash,
                    revised_version["record"], SUPPORTED,
                ),
                (
                    "stale_contradicted", revised_call, counter_source_hash,
                    old_version["record"], UNSUPPORTED,
                ),
                (
                    "missing_movement", hidden_call, counter_source_hash,
                    hidden_version["record"], UNSUPPORTED,
                ),
            )
            for pair_class, call, source_hash, record, expected in rows:
                if not admission.structurally_complete(record):
                    raise VerifierRefusal("source_record_incomplete")
                pairs.append(Pair(
                    pair_class=pair_class,
                    lineage=lineage,
                    design_position=position,
                    sensory_request_sha256=call["request_sha256"],
                    source_occurrence_sha256=source_hash,
                    sensory_report=request_report(requests, call["request_sha256"]),
                    proposed_record=record,
                    expected_label=expected,
                ))
    if len(pairs) != 16:
        raise VerifierRefusal("pair_count_mismatch")
    return tuple(pairs)


def schedule(pairs: tuple[Pair, ...]) -> tuple[tuple[int, Pair], ...]:
    by_class = {
        pair_class: [pair for pair in pairs if pair.pair_class == pair_class]
        for pair_class in PAIR_CLASSES
    }
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_index in range(4):
            for class_index in range(len(PAIR_CLASSES)):
                pair_class = PAIR_CLASSES[
                    (repeat - 1 + case_index + class_index) % len(PAIR_CLASSES)
                ]
                rows.append((repeat, by_class[pair_class][case_index]))
    return tuple(rows)


def specimen() -> dict[str, Any]:
    pairs = load_pairs()
    return {
        "instrument_model": learned.INSTRUMENT_MODEL,
        "instrument_model_digest": learned.INSTRUMENT_MODEL_DIGEST,
        "pair_classes": list(PAIR_CLASSES),
        "pairs": [
            {
                "design_position": pair.design_position,
                "expected_label": pair.expected_label,
                "lineage": pair.lineage,
                "pair_class": pair.pair_class,
                "pair_id": pair.pair_id,
                "proposed_record_sha256": admission.sha256(
                    admission.canonical(pair.proposed_record)
                ),
                "request_sha256": admission.sha256(verification_body(pair)),
                "sensory_request_sha256": pair.sensory_request_sha256,
                "source_occurrence_sha256": pair.source_occurrence_sha256,
            }
            for pair in pairs
        ],
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "source_packet_sha256": admission.SOURCE_PACKET_SHA256,
        "source_specimen_sha256": admission.SOURCE_SPECIMEN_SHA256,
        "spec_sha256": admission.sha256(SPEC_PATH.read_bytes()),
        "verifier_system_sha256": admission.sha256(VERIFIER_SYSTEM.encode()),
    }


Transport = Callable[[bytes], tuple[int, bytes]]


class Recorder:
    def __init__(self, transport: Transport, evidence_dir: Path | None):
        self.transport = transport
        self.physical = 0
        self.retries = 0
        self.attempts: list[dict[str, Any]] = []
        self.attempts_dir = None
        if evidence_dir is not None:
            evidence_dir.mkdir(parents=True, exist_ok=False)
            self.attempts_dir = evidence_dir / "attempts"
            self.attempts_dir.mkdir()
            (evidence_dir / "specimen.json").write_bytes(
                base.canonical_json_bytes(specimen())
            )

    def call(self, logical_index: int, body: bytes) -> tuple[Any, ...]:
        final = None
        for attempt in (1, 2):
            if self.physical >= PHYSICAL_CALL_CEILING:
                raise VerifierRefusal("physical_call_ceiling")
            self.physical += 1
            status, raw, error = None, b"", None
            try:
                status, raw = self.transport(body)
            except ConnectionError as exc:
                error = str(exc)
            retryable = error is not None or status in {408, 429, 500, 502, 503, 504}
            meta = {
                "attempt": attempt,
                "error": error,
                "http_status": status,
                "logical_index": logical_index,
                "request_sha256": base.sha256(body),
                "response_sha256": base.sha256(raw),
                "retryable": retryable,
            }
            self.attempts.append(meta)
            if self.attempts_dir is not None:
                stem = f"{self.physical:03d}-sv{logical_index:03d}-a{attempt}"
                (self.attempts_dir / f"{stem}.request.json").write_bytes(body)
                (self.attempts_dir / f"{stem}.response.bin").write_bytes(raw)
                (self.attempts_dir / f"{stem}.meta.json").write_text(
                    json.dumps(meta, indent=2, sort_keys=True) + "\n"
                )
            if retryable and attempt == 1 and self.retries < MAX_RETRIES:
                self.retries += 1
                continue
            final = status, error, raw
            break
        if final is None:
            raise VerifierRefusal("logical_call_not_completed")
        status, error, raw = final
        content, available, provider = base.parse_content(raw, status)
        return status, error, content, available, provider.get("usage")


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    pairs = load_pairs()
    rows = schedule(pairs)
    if len(rows) != PLANNED_LOGICAL_CALLS:
        raise VerifierRefusal("logical_schedule_mismatch")
    recorder = Recorder(transport, evidence_dir)
    calls = []
    for logical_index, (repeat, pair) in enumerate(rows, 1):
        body = verification_body(pair)
        status, error, content, content_available, usage = recorder.call(
            logical_index, body
        )
        availability, label = parse_label(content)
        if status != 200 or error is not None or not content_available:
            availability, label = "unavailable", None
        calls.append({
            "availability": availability,
            "correct": availability == "available" and label == pair.expected_label,
            "design_position": pair.design_position,
            "expected_label": pair.expected_label,
            "lineage": pair.lineage,
            "model_label": label,
            "pair_class": pair.pair_class,
            "pair_id": pair.pair_id,
            "provider_usage": usage,
            "repeat": repeat,
            "request_sha256": base.sha256(body),
            "responsibility": "source_support_verification",
        })

    distributions = {}
    for pair_class in PAIR_CLASSES:
        cell = [row for row in calls if row["pair_class"] == pair_class]
        distributions[pair_class] = {
            "assigned": len(cell),
            "correct": sum(row["correct"] for row in cell),
            "invalid_or_unavailable": sum(
                row["availability"] != "available" for row in cell
            ),
            "labels": dict(sorted(Counter(
                row["model_label"] or f"<{row['availability']}>" for row in cell
            ).items())),
        }
    valid = sum(row["availability"] == "available" for row in calls)
    engaged = valid >= 44
    candidate = (
        engaged
        and all(distributions[item]["correct"] >= 11 for item in PAIR_CLASSES)
        and distributions["stale_contradicted"]["labels"].get(SUPPORTED, 0) <= 1
        and distributions["missing_movement"]["labels"].get(SUPPORTED, 0) <= 1
    )
    verdict_class = (
        "not_engaged" if not engaged else "verifier_candidate" if candidate else "null"
    )
    packet = {
        "attempts": recorder.attempts,
        "calls": calls,
        "distributions": distributions,
        "formation_verdict": None,
        "logical_calls": len(calls),
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "retries": recorder.retries,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "valid_outputs": valid,
        "verifier_verdict": {
            "class": verdict_class,
            "scope": "clerical_source_support_verifier",
        },
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise VerifierRefusal("retained_specimen_mismatch")
    retained = json.loads((evidence_dir / "packet.json").read_bytes())
    entries = []
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        entries.append((
            (evidence_dir / "attempts" / f"{stem}.request.json").read_bytes(),
            (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes(),
            json.loads(meta_path.read_text()),
        ))
    position = 0

    def transport(body: bytes) -> tuple[int, bytes]:
        nonlocal position
        if position >= len(entries):
            raise VerifierRefusal("missing_retained_attempt")
        request, response, meta = entries[position]
        position += 1
        if request != body:
            raise VerifierRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise VerifierRefusal("evidence_replay_mismatch")
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
    evidence_dir = args.evidence_dir or Path("evidence") / (
        "clerical-source-support-verifier-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    receipt = learned.collect_provider_receipt()
    if not receipt["valid"]:
        raise VerifierRefusal("provider_identity_mismatch")
    started = time.monotonic()
    packet = execute(base.live_transport, evidence_dir)
    (evidence_dir / "provider.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    replay_evidence(evidence_dir)
    print(json.dumps({
        "elapsed_seconds": time.monotonic() - started,
        "evidence_dir": str(evidence_dir),
        "logical_calls": packet["logical_calls"],
        "physical_attempts": packet["physical_attempts"],
        "verifier_verdict": packet["verifier_verdict"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
