"""Run the clerical selected-effect projection exploration."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any, Callable

from contact import clerical_source_support_verifier as verifier
from contact import distributional_developmental_comparison as base
from contact import learned_clerical_instrument_exploration as learned
from contact import source_grounded_revision_admission as admission
from contact import staged_clerical_instrument_successor as staged


PROTOCOL_VERSION = "clerical-selected-effect-projection-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "CLERICAL_SELECTED_EFFECT_PROJECTION.md"
REPEATS = 3
PLANNED_LOGICAL_CALLS = 48
PHYSICAL_CALL_CEILING = 56
MAX_RETRIES = 8

PROJECTION_SETTINGS = {
    "max_tokens": 32,
    "response_format": {"type": "json_object"},
    "stream": False,
    "temperature": 0.2,
    "top_p": 0.9,
}

PROJECTION_SYSTEM = """You are a clerical field-projection component. You have no memory outside this request.

You receive an observed_actuator value and a proposed effect record with named fields for the first and second displayed controls.

If observed_actuator is first, copy first_control_effect. If observed_actuator is second, copy second_control_effect.

Return exactly one JSON object with the single key claimed_selected_effect. Copy the exact value increases_position or decreases_position from the selected field. Do not judge source support. Do not add commentary."""


class ProjectionRefusal(ValueError):
    pass


@dataclass(frozen=True)
class ProjectionCase:
    pair_id: str
    pair_class: str
    lineage: str
    design_position: str
    observed_actuator: str
    proposed_record: dict[str, str]
    expected_effect: str
    source_transcription_sha256: str

    @property
    def combination(self) -> str:
        return f"{self.observed_actuator}_{self.expected_effect}"


def projection_body(case: ProjectionCase) -> bytes:
    record = {
        "observed_actuator": case.observed_actuator,
        "proposed_effect_record": case.proposed_record,
    }
    return learned.canonical_envelope(
        learned.INSTRUMENT_MODEL,
        PROJECTION_SYSTEM,
        f"FIELD PROJECTION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",
        PROJECTION_SETTINGS,
    )


def parse_effect(content: str) -> tuple[str, str | None]:
    try:
        value = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return "invalid", None
    if (
        type(value) is not dict
        or set(value) != {"claimed_selected_effect"}
        or value["claimed_selected_effect"]
        not in {learned.INCREASES, learned.DECREASES}
    ):
        return "invalid", None
    return "available", value["claimed_selected_effect"]


def load_cases() -> tuple[ProjectionCase, ...]:
    packet, _ = admission.load_source()
    source_rows = [
        row
        for row in packet["calls"]
        if row["responsibility"] in {"old_transcription", "revision_transcription"}
    ]
    cases = []
    for pair in verifier.load_pairs():
        matches = [
            row for row in source_rows
            if row["request_sha256"] == pair.sensory_request_sha256
        ]
        if len(matches) != 1:
            raise ProjectionRefusal("source_transcription_set_mismatch")
        transcript_text = matches[0]["content"]
        transcript = staged.parse_transcription(transcript_text)
        if transcript is None:
            raise ProjectionRefusal("source_transcription_invalid")
        observed = transcript["observed_actuator"]
        field = f"{observed}_control_effect"
        cases.append(ProjectionCase(
            pair_id=pair.pair_id,
            pair_class=pair.pair_class,
            lineage=pair.lineage,
            design_position=pair.design_position,
            observed_actuator=observed,
            proposed_record=pair.proposed_record,
            expected_effect=pair.proposed_record[field],
            source_transcription_sha256=admission.sha256(transcript_text.encode()),
        ))
    if len(cases) != 16:
        raise ProjectionRefusal("projection_case_count_mismatch")
    return tuple(cases)


def schedule(cases: tuple[ProjectionCase, ...]) -> tuple[tuple[int, ProjectionCase], ...]:
    by_pair = {case.pair_id: case for case in cases}
    verifier_pairs = verifier.load_pairs()
    rows = [
        (repeat, by_pair[pair.pair_id])
        for repeat, pair in verifier.schedule(verifier_pairs)
    ]
    return tuple(rows)


def specimen() -> dict[str, Any]:
    cases = load_cases()
    return {
        "cases": [
            {
                "combination": case.combination,
                "design_position": case.design_position,
                "expected_effect": case.expected_effect,
                "lineage": case.lineage,
                "pair_class": case.pair_class,
                "pair_id": case.pair_id,
                "request_sha256": base.sha256(projection_body(case)),
                "source_transcription_sha256": case.source_transcription_sha256,
            }
            for case in cases
        ],
        "instrument_model": learned.INSTRUMENT_MODEL,
        "instrument_model_digest": learned.INSTRUMENT_MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "projection_system_sha256": admission.sha256(PROJECTION_SYSTEM.encode()),
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "source_packet_sha256": admission.SOURCE_PACKET_SHA256,
        "source_specimen_sha256": admission.SOURCE_SPECIMEN_SHA256,
        "spec_sha256": admission.sha256(SPEC_PATH.read_bytes()),
    }


Transport = Callable[[bytes], tuple[int, bytes]]


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    cases = load_cases()
    rows = schedule(cases)
    if len(rows) != PLANNED_LOGICAL_CALLS:
        raise ProjectionRefusal("logical_schedule_mismatch")
    recorder = verifier.Recorder(transport, evidence_dir)
    if evidence_dir is not None:
        (evidence_dir / "specimen.json").write_bytes(
            base.canonical_json_bytes(specimen())
        )
    calls = []
    for logical_index, (repeat, case) in enumerate(rows, 1):
        body = projection_body(case)
        status, error, content, content_available, usage = recorder.call(
            logical_index, body
        )
        availability, effect = parse_effect(content)
        if status != 200 or error is not None or not content_available:
            availability, effect = "unavailable", None
        calls.append({
            "availability": availability,
            "combination": case.combination,
            "correct": availability == "available" and effect == case.expected_effect,
            "design_position": case.design_position,
            "expected_effect": case.expected_effect,
            "lineage": case.lineage,
            "model_effect": effect,
            "pair_class": case.pair_class,
            "pair_id": case.pair_id,
            "provider_usage": usage,
            "repeat": repeat,
            "request_sha256": base.sha256(body),
            "responsibility": "selected_effect_projection",
        })

    class_scores = {}
    for pair_class in verifier.PAIR_CLASSES:
        cell = [row for row in calls if row["pair_class"] == pair_class]
        class_scores[pair_class] = {
            "assigned": len(cell),
            "correct": sum(row["correct"] for row in cell),
            "invalid_or_unavailable": sum(
                row["availability"] != "available" for row in cell
            ),
        }
    combinations = sorted({case.combination for case in cases})
    combination_scores = {}
    for combination in combinations:
        cell = [row for row in calls if row["combination"] == combination]
        combination_scores[combination] = {
            "assigned": len(cell),
            "correct": sum(row["correct"] for row in cell),
            "effects": dict(sorted(Counter(
                row["model_effect"] or f"<{row['availability']}>" for row in cell
            ).items())),
        }
    valid = sum(row["availability"] == "available" for row in calls)
    exact = sum(row["correct"] for row in calls)
    engaged = valid >= 46
    candidate = (
        engaged
        and exact >= 46
        and all(class_scores[item]["correct"] >= 11 for item in verifier.PAIR_CLASSES)
        and all(
            cell["correct"] >= cell["assigned"] - 1
            for cell in combination_scores.values()
        )
    )
    verdict_class = (
        "not_engaged" if not engaged else "projection_candidate" if candidate else "null"
    )
    packet = {
        "attempts": recorder.attempts,
        "calls": calls,
        "class_scores": class_scores,
        "combination_scores": combination_scores,
        "exact_projections": exact,
        "formation_verdict": None,
        "logical_calls": len(calls),
        "physical_attempts": recorder.physical,
        "projection_verdict": {
            "class": verdict_class,
            "scope": "clerical_selected_effect_projection",
        },
        "protocol_version": PROTOCOL_VERSION,
        "retries": recorder.retries,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "valid_outputs": valid,
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise ProjectionRefusal("retained_specimen_mismatch")
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
            raise ProjectionRefusal("missing_retained_attempt")
        request, response, meta = entries[position]
        position += 1
        if request != body:
            raise ProjectionRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise ProjectionRefusal("evidence_replay_mismatch")
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
        "clerical-selected-effect-projection-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    receipt = learned.collect_provider_receipt()
    if not receipt["valid"]:
        raise ProjectionRefusal("provider_identity_mismatch")
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
        "projection_verdict": packet["projection_verdict"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
