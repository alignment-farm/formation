"""Evaluate source-grounded admission on the retained revision proposals."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from contact import distributional_developmental_comparison as base
from contact import learned_clerical_instrument_exploration as learned


PROTOCOL_VERSION = "source-grounded-revision-admission-v1"
ROOT = Path(__file__).parents[1]
SPEC_PATH = ROOT / "docs" / "SOURCE_GROUNDED_REVISION_ADMISSION.md"
SOURCE_DIR = ROOT / "evidence" / "learned-clerical-revision-20260820T174848Z"
SOURCE_PACKET_SHA256 = "9387ac057bebe2fb1ca422e268f470dc8d424a6b9577dbcf8799665abc2bec7f"
SOURCE_SPECIMEN_SHA256 = "5bd2e2e82991312bdb03ad159711e7cf40e1bc47bcff84cce0fdad06658e2cfe"
CONDITIONS = ("revised", "hidden")
LINEAGES = ("lineage_01", "lineage_02")
DESIGN_POSITIONS = ("a", "b")
ADMITTED = "admitted"
QUARANTINED = "quarantined"


class AdmissionDiagnosticRefusal(ValueError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode()


@dataclass(frozen=True)
class SensoryReceipt:
    lineage: str
    design_position: str
    condition: str
    source_occurrence_sha256: str
    sensory_request_sha256: str
    sensory_projection_sha256: str
    selected_actuator: str | None
    movement_direction: str | None


@dataclass(frozen=True)
class RecordProposal:
    lineage: str
    design_position: str
    condition: str
    record_lineage_id: str
    old_record_version_id: str
    proposed_record_version_id: str
    proposed_version: int
    sensory_request_sha256: str
    source_occurrence_sha256: str
    record: dict[str, str] | None


def parse_request_record(request_bytes: bytes) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        envelope = json.loads(request_bytes)
        messages = envelope["messages"]
        user = messages[1]["content"]
        if len(messages) != 2 or not user.startswith("SENSORY REPORT\n"):
            raise AdmissionDiagnosticRefusal("invalid_sensory_request_shape")
        record = json.loads(user.split("\n", 1)[1].rsplit("\n", 1)[0])
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
        raise AdmissionDiagnosticRefusal("invalid_sensory_request") from exc
    if (
        envelope.get("model") != learned.INSTRUMENT_MODEL
        or type(record) is not dict
        or set(record) != {"actuator_report", "device_report", "gauge_report"}
    ):
        raise AdmissionDiagnosticRefusal("invalid_sensory_request_contract")
    return envelope, record


def measurement_values(report: dict[str, Any]) -> tuple[str | None, str | None]:
    actuator = {
        "The first displayed actuator was engaged.": "first",
        "The second displayed actuator was engaged.": "second",
    }.get(report["actuator_report"])
    movement = {
        "The position gauge rose by one mark.": "increased",
        "The position gauge fell by one mark.": "decreased",
    }.get(report["gauge_report"])
    return actuator, movement


def structurally_complete(record: object) -> bool:
    return (
        type(record) is dict
        and set(record) == {"first_control_effect", "second_control_effect"}
        and {
            record["first_control_effect"],
            record["second_control_effect"],
        } == {learned.INCREASES, learned.DECREASES}
    )


def decide(receipt: SensoryReceipt, proposal: RecordProposal) -> dict[str, Any]:
    reasons = []
    if proposal.lineage != receipt.lineage:
        reasons.append("lineage_mismatch")
    if proposal.design_position != receipt.design_position:
        reasons.append("design_position_mismatch")
    if proposal.condition != receipt.condition:
        reasons.append("condition_mismatch")
    if proposal.sensory_request_sha256 != receipt.sensory_request_sha256:
        reasons.append("sensory_request_mismatch")
    if proposal.source_occurrence_sha256 != receipt.source_occurrence_sha256:
        reasons.append("source_occurrence_mismatch")
    if receipt.selected_actuator not in {"first", "second"}:
        reasons.append("selected_actuator_missing")
    if receipt.movement_direction not in {"increased", "decreased"}:
        reasons.append("movement_direction_missing")
    if not structurally_complete(proposal.record):
        reasons.append("record_structure_incomplete")
    status = ADMITTED if not reasons else QUARANTINED
    return {
        "active_record_version_id": (
            proposal.proposed_record_version_id
            if status == ADMITTED
            else proposal.old_record_version_id
        ),
        "active_version": proposal.proposed_version if status == ADMITTED else 1,
        "condition": proposal.condition,
        "design_position": proposal.design_position,
        "lineage": proposal.lineage,
        "proposal_record_sha256": sha256(canonical(proposal.record)),
        "proposed_record_version_id": proposal.proposed_record_version_id,
        "reasons": reasons,
        "sensory_projection_sha256": receipt.sensory_projection_sha256,
        "sensory_request_sha256": receipt.sensory_request_sha256,
        "source_occurrence_sha256": receipt.source_occurrence_sha256,
        "status": status,
    }


def specimen() -> dict[str, Any]:
    return {
        "conditions": list(CONDITIONS),
        "decision_inputs": [
            "exact sensory request binding",
            "exact source occurrence binding",
            "selected actuator availability",
            "movement direction availability",
            "record structural completeness",
        ],
        "design_positions": list(DESIGN_POSITIONS),
        "lineages": list(LINEAGES),
        "new_model_call_budget": 0,
        "protocol_version": PROTOCOL_VERSION,
        "source_packet_sha256": SOURCE_PACKET_SHA256,
        "source_specimen_sha256": SOURCE_SPECIMEN_SHA256,
        "spec_sha256": sha256(SPEC_PATH.read_bytes()),
    }


def load_source(source_dir: Path = SOURCE_DIR) -> tuple[dict[str, Any], dict[str, bytes]]:
    packet_bytes = (source_dir / "packet.json").read_bytes()
    specimen_bytes = (source_dir / "specimen.json").read_bytes()
    if sha256(packet_bytes) != SOURCE_PACKET_SHA256:
        raise AdmissionDiagnosticRefusal("source_packet_mismatch")
    if sha256(specimen_bytes) != SOURCE_SPECIMEN_SHA256:
        raise AdmissionDiagnosticRefusal("source_specimen_mismatch")
    packet = json.loads(packet_bytes)
    if (
        packet.get("revision_verdict", {}).get("class") != "revision_candidate"
        or packet.get("formation_verdict") is not None
    ):
        raise AdmissionDiagnosticRefusal("source_result_ineligible")

    requests: dict[str, bytes] = {}
    for meta_path in sorted((source_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        meta = json.loads(meta_path.read_text())
        request_bytes = (source_dir / "attempts" / f"{stem}.request.json").read_bytes()
        if sha256(request_bytes) != meta["request_sha256"]:
            raise AdmissionDiagnosticRefusal("retained_request_hash_mismatch")
        prior = requests.setdefault(meta["request_sha256"], request_bytes)
        if prior != request_bytes:
            raise AdmissionDiagnosticRefusal("request_hash_collision")
    return packet, requests


def source_version(
    packet: dict[str, Any], condition: str, lineage: str, position: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    key = "record_versions" if condition == "revised" else "hidden_comparator_versions"
    versions = packet[key][lineage][position]
    if len(versions) != 2 or versions[0]["version"] != 1 or versions[1]["version"] != 2:
        raise AdmissionDiagnosticRefusal("invalid_source_version_lineage")
    return versions[0], versions[1]


def build_pair(
    packet: dict[str, Any],
    requests: dict[str, bytes],
    call: dict[str, Any],
) -> tuple[SensoryReceipt, RecordProposal]:
    condition = call["consequence_condition"]
    lineage = call["lineage"]
    position = call["design_position"]
    request_sha = call["request_sha256"]
    try:
        request_bytes = requests[request_sha]
    except KeyError as exc:
        raise AdmissionDiagnosticRefusal("missing_retained_sensory_request") from exc
    _, report = parse_request_record(request_bytes)
    actuator, movement = measurement_values(report)
    old_version, proposed_version = source_version(
        packet, condition, lineage, position
    )
    source_hash = proposed_version["source_occurrence"]["external_result_sha256"]
    receipt = SensoryReceipt(
        lineage=lineage,
        design_position=position,
        condition=condition,
        source_occurrence_sha256=source_hash,
        sensory_request_sha256=request_sha,
        sensory_projection_sha256=sha256(canonical(report)),
        selected_actuator=actuator,
        movement_direction=movement,
    )
    proposal = RecordProposal(
        lineage=lineage,
        design_position=position,
        condition=condition,
        record_lineage_id=proposed_version["record_lineage_id"],
        old_record_version_id=old_version["record_version_id"],
        proposed_record_version_id=proposed_version["record_version_id"],
        proposed_version=2,
        sensory_request_sha256=request_sha,
        source_occurrence_sha256=source_hash,
        record=proposed_version["record"],
    )
    return receipt, proposal


def execute(source_dir: Path = SOURCE_DIR) -> dict[str, Any]:
    packet, requests = load_source(source_dir)
    calls = [
        row
        for row in packet["calls"]
        if row["responsibility"] == "revision_transcription"
    ]
    expected_keys = {
        (condition, lineage, position)
        for condition in CONDITIONS
        for lineage in LINEAGES
        for position in DESIGN_POSITIONS
    }
    actual_keys = {
        (row["consequence_condition"], row["lineage"], row["design_position"])
        for row in calls
    }
    if actual_keys != expected_keys or len(calls) != len(expected_keys):
        raise AdmissionDiagnosticRefusal("source_sensory_call_set_mismatch")

    pairs = [build_pair(packet, requests, row) for row in calls]
    decisions = [decide(receipt, proposal) for receipt, proposal in pairs]
    exposed_admitted = sum(
        item["condition"] == "revised" and item["status"] == ADMITTED
        for item in decisions
    )
    hidden_quarantined = sum(
        item["condition"] == "hidden" and item["status"] == QUARANTINED
        for item in decisions
    )

    exposed_receipt, exposed_proposal = next(
        pair
        for pair in pairs
        if pair[0].condition == "revised"
        and pair[0].lineage == LINEAGES[0]
        and pair[0].design_position == DESIGN_POSITIONS[0]
    )
    hidden_receipt, _ = next(
        pair
        for pair in pairs
        if pair[0].condition == "hidden"
        and pair[0].lineage == LINEAGES[0]
        and pair[0].design_position == DESIGN_POSITIONS[0]
    )
    hidden_same_claim = RecordProposal(
        **{
            **asdict(exposed_proposal),
            "condition": hidden_receipt.condition,
            "proposed_record_version_id": "same-claim-hidden-comparator",
            "sensory_request_sha256": hidden_receipt.sensory_request_sha256,
            "source_occurrence_sha256": hidden_receipt.source_occurrence_sha256,
        }
    )
    exposed_same_claim = decide(exposed_receipt, exposed_proposal)
    hidden_same_claim_decision = decide(hidden_receipt, hidden_same_claim)

    inverted_record = {
        "first_control_effect": exposed_proposal.record["second_control_effect"],
        "second_control_effect": exposed_proposal.record["first_control_effect"],
    }
    inverted_proposal = RecordProposal(
        **{
            **asdict(exposed_proposal),
            "proposed_record_version_id": "inverted-content-comparator",
            "record": inverted_record,
        }
    )
    inverted_decision = decide(exposed_receipt, inverted_proposal)

    bindings_complete = all(
        len(item["sensory_request_sha256"]) == 64
        and len(item["source_occurrence_sha256"]) == 64
        for item in decisions
    )
    conforms = (
        exposed_admitted == 4
        and hidden_quarantined == 4
        and all(
            item["active_version"] == (2 if item["condition"] == "revised" else 1)
            for item in decisions
        )
        and exposed_same_claim["proposal_record_sha256"]
        == hidden_same_claim_decision["proposal_record_sha256"]
        and exposed_same_claim["status"] == ADMITTED
        and hidden_same_claim_decision["status"] == QUARANTINED
        and inverted_decision["status"] == ADMITTED
        and bindings_complete
    )
    return {
        "bindings_complete": bindings_complete,
        "decisions": decisions,
        "exposed_admitted": exposed_admitted,
        "formation_verdict": None,
        "hidden_quarantined": hidden_quarantined,
        "model_calls": 0,
        "protocol_version": PROTOCOL_VERSION,
        "semantic_blindness_comparator": {
            "inverted_claim_sha256": inverted_decision["proposal_record_sha256"],
            "inverted_claim_status": inverted_decision["status"],
            "original_claim_sha256": exposed_same_claim["proposal_record_sha256"],
            "original_claim_status": exposed_same_claim["status"],
        },
        "same_claim_source_comparator": {
            "claim_sha256": exposed_same_claim["proposal_record_sha256"],
            "complete_source_status": exposed_same_claim["status"],
            "missing_movement_reasons": hidden_same_claim_decision["reasons"],
            "missing_movement_status": hidden_same_claim_decision["status"],
        },
        "source_packet_sha256": SOURCE_PACKET_SHA256,
        "source_specimen_sha256": SOURCE_SPECIMEN_SHA256,
        "specimen_sha256": sha256(canonical(specimen())),
        "verdict": {
            "class": "conforms" if conforms else "does_not_conform",
            "scope": "source_grounded_revision_admission",
        },
    }


def write_evidence(output_dir: Path, packet: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "specimen.json").write_bytes(canonical(specimen()))
    (output_dir / "packet.json").write_bytes(canonical(packet))


def replay_evidence(output_dir: Path) -> dict[str, Any]:
    retained_specimen = (output_dir / "specimen.json").read_bytes()
    if retained_specimen != canonical(specimen()):
        raise AdmissionDiagnosticRefusal("retained_specimen_mismatch")
    retained_packet = json.loads((output_dir / "packet.json").read_bytes())
    replayed = execute()
    if canonical(replayed) != canonical(retained_packet):
        raise AdmissionDiagnosticRefusal("deterministic_replay_mismatch")
    return replayed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args(argv)
    packet = execute()
    output_dir = args.evidence_dir
    if output_dir is None:
        print(json.dumps(packet, sort_keys=True))
        return 0
    write_evidence(output_dir, packet)
    replay_evidence(output_dir)
    print(json.dumps({
        "evidence_dir": str(output_dir),
        "exposed_admitted": packet["exposed_admitted"],
        "hidden_quarantined": packet["hidden_quarantined"],
        "model_calls": packet["model_calls"],
        "verdict": packet["verdict"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
