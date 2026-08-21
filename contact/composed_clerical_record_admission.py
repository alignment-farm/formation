"""Compose retained clerk outputs into source-grounded record admission."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from contact import clerical_selected_effect_projection as projection
from contact import clerical_source_support_verifier as verifier
from contact import distributional_developmental_comparison as base
from contact import learned_clerical_instrument_exploration as learned
from contact import source_grounded_revision_admission as admission
from contact import staged_clerical_instrument_successor as staged


PROTOCOL_VERSION = "composed-clerical-record-admission-v1"
ROOT = Path(__file__).parents[1]
SPEC_PATH = ROOT / "docs" / "COMPOSED_CLERICAL_RECORD_ADMISSION.md"
PROJECTION_DIR = ROOT / "evidence" / "clerical-selected-effect-projection-20260820T181202Z"
PROJECTION_PACKET_SHA256 = "00eb809394b53f813635846252a07ff046e9e78dcfeb781dd170ef5d8437756f"
PROJECTION_SPECIMEN_SHA256 = "da533e21e49101bc834e94cd8116c99f467d1e0398b3ab7b918d2c86995993bd"
ADMITTED = "admitted"
QUARANTINED = "quarantined"


class CompositionRefusal(ValueError):
    pass


def specimen() -> dict[str, Any]:
    return {
        "checks": [
            "sensory source completeness",
            "sensory transcription exact copy",
            "record structural completeness",
            "projector exact selected-field copy",
            "projected claim equals transcribed observed effect",
        ],
        "new_model_call_budget": 0,
        "projection_packet_sha256": PROJECTION_PACKET_SHA256,
        "projection_specimen_sha256": PROJECTION_SPECIMEN_SHA256,
        "protocol_version": PROTOCOL_VERSION,
        "revision_packet_sha256": admission.SOURCE_PACKET_SHA256,
        "revision_specimen_sha256": admission.SOURCE_SPECIMEN_SHA256,
        "spec_sha256": admission.sha256(SPEC_PATH.read_bytes()),
    }


def load_projection_evidence(
    evidence_dir: Path = PROJECTION_DIR,
) -> tuple[dict[str, Any], dict[int, tuple[bytes, bytes, dict[str, Any]]]]:
    packet_bytes = (evidence_dir / "packet.json").read_bytes()
    specimen_bytes = (evidence_dir / "specimen.json").read_bytes()
    if admission.sha256(packet_bytes) != PROJECTION_PACKET_SHA256:
        raise CompositionRefusal("projection_packet_mismatch")
    if admission.sha256(specimen_bytes) != PROJECTION_SPECIMEN_SHA256:
        raise CompositionRefusal("projection_specimen_mismatch")
    packet = json.loads(packet_bytes)
    if (
        packet.get("projection_verdict", {}).get("class") != "projection_candidate"
        or packet.get("formation_verdict") is not None
        or packet.get("logical_calls") != 48
    ):
        raise CompositionRefusal("projection_result_ineligible")
    attempts = {}
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        meta = json.loads(meta_path.read_text())
        if meta["attempt"] != 1 or meta["logical_index"] in attempts:
            raise CompositionRefusal("projection_attempt_set_mismatch")
        request = (evidence_dir / "attempts" / f"{stem}.request.json").read_bytes()
        response = (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes()
        if (
            admission.sha256(request) != meta["request_sha256"]
            or admission.sha256(response) != meta["response_sha256"]
            or meta["error"] is not None
            or meta["http_status"] != 200
        ):
            raise CompositionRefusal("projection_attempt_binding_mismatch")
        attempts[meta["logical_index"]] = (request, response, meta)
    if set(attempts) != set(range(1, 49)):
        raise CompositionRefusal("projection_attempt_count_mismatch")
    return packet, attempts


def source_material() -> tuple[
    dict[str, Any],
    dict[str, verifier.Pair],
    dict[str, projection.ProjectionCase],
    dict[str, dict[str, Any]],
]:
    source_packet, _ = admission.load_source()
    pairs = {pair.pair_id: pair for pair in verifier.load_pairs()}
    cases = {case.pair_id: case for case in projection.load_cases()}
    transcriptions = {
        row["request_sha256"]: row
        for row in source_packet["calls"]
        if row["responsibility"] in {"old_transcription", "revision_transcription"}
    }
    if len(pairs) != 16 or len(cases) != 16:
        raise CompositionRefusal("source_case_count_mismatch")
    return source_packet, pairs, cases, transcriptions


def compose_decision(
    pair: verifier.Pair,
    case: projection.ProjectionCase,
    transcript_text: str,
    projected_effect: str | None,
) -> dict[str, Any]:
    raw_actuator, raw_movement = admission.measurement_values(pair.sensory_report)
    transcript = staged.parse_transcription(transcript_text)
    reasons = []
    if raw_actuator is None:
        reasons.append("selected_actuator_missing")
    if raw_movement is None:
        reasons.append("movement_direction_missing")
    if transcript is None:
        reasons.append("sensory_transcription_invalid")
        transcribed_actuator = None
        transcribed_effect = None
    else:
        transcribed_actuator = transcript["observed_actuator"]
        transcribed_effect = transcript["observed_effect"]
        if raw_actuator is not None and transcribed_actuator != raw_actuator:
            reasons.append("transcribed_actuator_mismatch")
        expected_observed_effect = {
            "increased": learned.INCREASES,
            "decreased": learned.DECREASES,
        }.get(raw_movement)
        if (
            expected_observed_effect is not None
            and transcribed_effect != expected_observed_effect
        ):
            reasons.append("transcribed_effect_mismatch")
    if not admission.structurally_complete(pair.proposed_record):
        reasons.append("record_structure_incomplete")
    expected_projection = (
        pair.proposed_record.get(f"{transcribed_actuator}_control_effect")
        if type(pair.proposed_record) is dict
        and transcribed_actuator in {"first", "second"}
        else None
    )
    if projected_effect not in {learned.INCREASES, learned.DECREASES}:
        reasons.append("projected_effect_invalid")
    elif projected_effect != expected_projection:
        reasons.append("projected_field_mismatch")
    if (
        projected_effect in {learned.INCREASES, learned.DECREASES}
        and transcribed_effect in {learned.INCREASES, learned.DECREASES}
        and projected_effect != transcribed_effect
    ):
        reasons.append("claimed_effect_mismatch")
    status = ADMITTED if not reasons else QUARANTINED
    expected_status = (
        ADMITTED
        if pair.pair_class in {"old_supported", "revision_supported"}
        else QUARANTINED
    )
    active_version = (
        2
        if pair.pair_class == "revision_supported" and status == ADMITTED
        else 1
    )
    return {
        "active_version": active_version,
        "correct": status == expected_status,
        "design_position": pair.design_position,
        "expected_status": expected_status,
        "lineage": pair.lineage,
        "pair_class": pair.pair_class,
        "pair_id": pair.pair_id,
        "projected_effect": projected_effect,
        "proposed_record_sha256": admission.sha256(
            admission.canonical(pair.proposed_record)
        ),
        "reasons": reasons,
        "sensory_request_sha256": pair.sensory_request_sha256,
        "source_occurrence_sha256": pair.source_occurrence_sha256,
        "source_transcription_sha256": admission.sha256(transcript_text.encode()),
        "status": status,
    }


def execute(projection_dir: Path = PROJECTION_DIR) -> dict[str, Any]:
    projection_packet, attempts = load_projection_evidence(projection_dir)
    _, pairs, cases, transcriptions = source_material()
    decisions = []
    bindings_complete = True
    for logical_index, call in enumerate(projection_packet["calls"], 1):
        pair = pairs[call["pair_id"]]
        case = cases[call["pair_id"]]
        request, response, meta = attempts[logical_index]
        expected_request = projection.projection_body(case)
        content, available, _ = base.parse_content(response, 200)
        availability, projected_effect = projection.parse_effect(content)
        bound = (
            request == expected_request
            and meta["request_sha256"] == call["request_sha256"]
            and call["request_sha256"] == base.sha256(expected_request)
            and available
            and availability == call["availability"] == "available"
            and projected_effect == call["model_effect"]
            and call["pair_class"] == pair.pair_class
        )
        bindings_complete = bindings_complete and bound
        if not bound:
            raise CompositionRefusal("projection_call_binding_mismatch")
        try:
            transcript_row = transcriptions[pair.sensory_request_sha256]
        except KeyError as exc:
            raise CompositionRefusal("missing_source_transcription") from exc
        if (
            admission.sha256(transcript_row["content"].encode())
            != case.source_transcription_sha256
        ):
            raise CompositionRefusal("source_transcription_binding_mismatch")
        decision = compose_decision(
            pair, case, transcript_row["content"], projected_effect
        )
        decision["logical_index"] = logical_index
        decision["projector_request_sha256"] = call["request_sha256"]
        decision["projector_response_sha256"] = meta["response_sha256"]
        decisions.append(decision)

    class_scores = {}
    for pair_class in verifier.PAIR_CLASSES:
        cell = [item for item in decisions if item["pair_class"] == pair_class]
        class_scores[pair_class] = {
            "admitted": sum(item["status"] == ADMITTED for item in cell),
            "assigned": len(cell),
            "correct": sum(item["correct"] for item in cell),
            "quarantined": sum(item["status"] == QUARANTINED for item in cell),
        }
    conforms = (
        bindings_complete
        and class_scores["old_supported"] == {
            "admitted": 12, "assigned": 12, "correct": 12, "quarantined": 0,
        }
        and class_scores["revision_supported"] == {
            "admitted": 12, "assigned": 12, "correct": 12, "quarantined": 0,
        }
        and class_scores["stale_contradicted"] == {
            "admitted": 0, "assigned": 12, "correct": 12, "quarantined": 12,
        }
        and class_scores["missing_movement"] == {
            "admitted": 0, "assigned": 12, "correct": 12, "quarantined": 12,
        }
        and all(
            item["active_version"]
            == (2 if item["pair_class"] == "revision_supported" else 1)
            for item in decisions
        )
    )
    return {
        "bindings_complete": bindings_complete,
        "class_scores": class_scores,
        "decisions": decisions,
        "formation_verdict": None,
        "model_calls": 0,
        "projection_packet_sha256": PROJECTION_PACKET_SHA256,
        "projection_specimen_sha256": PROJECTION_SPECIMEN_SHA256,
        "protocol_version": PROTOCOL_VERSION,
        "revision_packet_sha256": admission.SOURCE_PACKET_SHA256,
        "specimen_sha256": admission.sha256(admission.canonical(specimen())),
        "verdict": {
            "class": "conforms" if conforms else "does_not_conform",
            "scope": "composed_clerical_record_admission",
        },
    }


def write_evidence(output_dir: Path, packet: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "specimen.json").write_bytes(admission.canonical(specimen()))
    (output_dir / "packet.json").write_bytes(admission.canonical(packet))


def replay_evidence(output_dir: Path) -> dict[str, Any]:
    if (output_dir / "specimen.json").read_bytes() != admission.canonical(specimen()):
        raise CompositionRefusal("retained_specimen_mismatch")
    retained = json.loads((output_dir / "packet.json").read_bytes())
    replayed = execute()
    if admission.canonical(replayed) != admission.canonical(retained):
        raise CompositionRefusal("deterministic_replay_mismatch")
    return replayed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args(argv)
    packet = execute()
    if args.evidence_dir is None:
        print(json.dumps(packet, sort_keys=True))
        return 0
    write_evidence(args.evidence_dir, packet)
    replay_evidence(args.evidence_dir)
    print(json.dumps({
        "evidence_dir": str(args.evidence_dir),
        "model_calls": packet["model_calls"],
        "verdict": packet["verdict"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
