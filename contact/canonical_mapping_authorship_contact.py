"""Test consequence-derived authorship in an influential canonical form.

Prospective exploratory note
----------------------------
Question: can the cold model use one acquisition occurrence and external result
to author a correct first-then-second controller mapping whose later delivery
changes action distributions relative to authored ablation and raw occurrence?
Observation of interest: exact authored content, its relation to the frozen
static mapping, and repeated action distributions on same-family upward and
downward cases plus an opposite-profile non-transfer case.
Model/interface: exact ``ai/qwen3:14B-Q6_K`` Docker Model Runner artifact. The
authorship prompt fixes a generic first-then-second sentence grammar but does
not supply the family identifier, observed movement, inferred movement, or
mapping answer.
Budget: one acquisition action, one authorship call, then four branches by
three cases by eight repeats; 98 logical calls and at most 102 physical
attempts. Only transport failures may be retried, at most four times.
Stopping condition: stop after the fixed schedule or either ceiling. Deliver
authored text exactly as returned and preserve malformed or unavailable output.
Evidence destination: ``evidence/canonical-mapping-authorship-<run-id>/``.

This is exploratory. A positive result would identify a candidate
experience-to-authorship-to-action path, not establish Formation or validation.
"""

from __future__ import annotations

import argparse
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


PROTOCOL_VERSION = "canonical-mapping-authorship-contact-v1"
AUTHORED_ABLATION = "authored_ablation"
RAW_PERSISTENCE = "raw_persistence"
AUTHORED_DELIVERY = "authored_delivery"
STATIC_INSTRUCTION = "static_instruction"
BRANCHES = (AUTHORED_ABLATION, RAW_PERSISTENCE, AUTHORED_DELIVERY, STATIC_INSTRUCTION)
CASES = ("same_family_up", "same_family_down", "other_family_up")
REPEATS = 8
PLANNED_LOGICAL_CALLS = 2 + len(BRANCHES) * len(CASES) * REPEATS
PHYSICAL_CALL_CEILING = 102

AUTHORSHIP_RESPONSIBILITY = (
    "Author one retained controller-family mapping from the supplied occurrence and external result. "
    "Use the required first-then-second sentence grammar and return only that sentence."
)
AUTHORSHIP_SYSTEM = """You are the retained-guidance author in a controlled cold-model experiment. You have no memory outside this request.

The record contains one committed action and an environment-issued result. Within a controller family, one displayed slot always increases position by one and the other always decreases it by one. Use selected_slot and movement_direction to derive the observed slot, then infer the opposite slot.

Return exactly one sentence with this grammar:
For controller family <controller_family>, the first displayed control <increases or decreases> position and the second displayed control <decreases or increases> position.

Replace every bracketed item with facts derived from the record. Describe the first displayed control before the second. Do not include action strings, brackets, labels, or commentary."""


class CanonicalAuthorshipRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


PRIMARY_PROFILE = LineageProfile(opaque("primary-family"), SECOND_INCREASES)
OTHER_PROFILE = LineageProfile(opaque("other-family"), FIRST_INCREASES)
ACQUISITION = LineageState(
    PRIMARY_PROFILE.controller_family,
    opaque("acquisition-device"),
    642,
    643,
    (opaque("acquisition-first"), opaque("acquisition-second")),
)
CASE_STATES = {
    "same_family_up": LineageState(
        PRIMARY_PROFILE.controller_family,
        opaque("same-up-device"),
        215,
        216,
        (opaque("same-up-first"), opaque("same-up-second")),
    ),
    "same_family_down": LineageState(
        PRIMARY_PROFILE.controller_family,
        opaque("same-down-device"),
        874,
        873,
        (opaque("same-down-first"), opaque("same-down-second")),
    ),
    "other_family_up": LineageState(
        OTHER_PROFILE.controller_family,
        opaque("other-up-device"),
        491,
        492,
        (opaque("other-up-first"), opaque("other-up-second")),
    ),
}


def profile_for(case: str) -> LineageProfile:
    return OTHER_PROFILE if case == "other_family_up" else PRIMARY_PROFILE


def static_instruction() -> str:
    return (
        f"For controller family {PRIMARY_PROFILE.controller_family}, the first displayed control "
        "decreases position and the second displayed control increases position."
    )


def action_body(state: LineageState, retained_material: str) -> bytes:
    record = {
        "device": base.public_device(state),
        "responsibility": ACTION_RESPONSIBILITY,
        "retained_material": retained_material,
    }
    user = f"ACTION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think"
    return base.envelope(base.ACTION_SYSTEM, user, base.ACTION_SETTINGS)


def authorship_body(state: LineageState, proposal: ProposalReceipt, result: Any) -> bytes:
    record = {
        **base.experience_record(state, proposal, result),
        "responsibility": AUTHORSHIP_RESPONSIBILITY,
    }
    user = f"AUTHORSHIP REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think"
    return base.envelope(AUTHORSHIP_SYSTEM, user, {**base.AUTHORSHIP_SETTINGS, "max_tokens": 128})


def specimen() -> dict[str, Any]:
    return {
        "acquisition": base.public_device(ACQUISITION),
        "authorship_system_sha256": base.sha256(AUTHORSHIP_SYSTEM.encode()),
        "branches": list(BRANCHES),
        "cases": [
            {
                "case": case,
                "device": base.public_device(state),
                "expected_action": oracle_action(state, profile_for(case)),
            }
            for case, state in CASE_STATES.items()
        ],
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "static_instruction_sha256": base.sha256(static_instruction().encode()),
    }


def schedule() -> tuple[tuple[int, str, str], ...]:
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_offset in range(len(CASES)):
            case = CASES[(repeat - 1 + case_offset) % len(CASES)]
            for branch_offset in range(len(BRANCHES)):
                branch = BRANCHES[(repeat - 1 + branch_offset) % len(BRANCHES)]
                rows.append((repeat, case, branch))
    if len(rows) != PLANNED_LOGICAL_CALLS - 2:
        raise CanonicalAuthorshipRefusal("schedule_size_mismatch")
    return tuple(rows)


Transport = Callable[[bytes], tuple[int, bytes]]


class Recorder(base.Recorder):
    def __init__(self, transport: Transport, evidence_dir: Path | None) -> None:
        self.transport = transport
        self.evidence_dir = evidence_dir
        self.attempts_dir = None
        if evidence_dir is not None:
            evidence_dir.mkdir(parents=True, exist_ok=False)
            self.attempts_dir = evidence_dir / "attempts"
            self.attempts_dir.mkdir()
            (evidence_dir / "specimen.json").write_bytes(base.canonical_json_bytes(specimen()))
        self.physical = 0
        self.retries = 0
        self.attempts = []


def _materials(proposal: ProposalReceipt, result: Any, authored: str) -> dict[str, str]:
    raw = base.canonical_json_bytes(base.experience_record(ACQUISITION, proposal, result)).decode()
    return {
        AUTHORED_ABLATION: "",
        RAW_PERSISTENCE: raw,
        AUTHORED_DELIVERY: authored,
        STATIC_INSTRUCTION: static_instruction(),
    }


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    recorder = Recorder(transport, evidence_dir)
    calls = []

    acquisition_request = action_body(ACQUISITION, "")
    status, _, error, received = recorder.call(1, "av001", acquisition_request)
    availability, action = base.parse_action(received["content"], ACQUISITION)
    provider_available = status == 200 and error is None and received["content_available"]
    proposal = ProposalReceipt(provider_available, (action or received["content"]) if provider_available else "")
    result = apply_committed_action(ACQUISITION, PRIMARY_PROFILE, proposal)
    calls.append({
        "action": action,
        "availability": availability if status == 200 and error is None else "unavailable",
        "correct_action": availability == "available" and action == oracle_action(ACQUISITION, PRIMARY_PROFILE),
        "invocation": "av001",
        "logical_index": 1,
        "provider_usage": received["provider_usage"],
        "request_sha256": base.sha256(acquisition_request),
        "responsibility": "acquisition_action",
    })

    author_request = authorship_body(ACQUISITION, proposal, result)
    author_status, _, author_error, author_received = recorder.call(2, "av002", author_request)
    authored_available = author_status == 200 and author_error is None and author_received["content_available"]
    authored = author_received["content"] if authored_available else ""
    calls.append({
        "available": authored_available,
        "content": authored,
        "content_sha256": base.sha256(authored.encode()),
        "exact_static_match": authored == static_instruction(),
        "invocation": "av002",
        "logical_index": 2,
        "provider_usage": author_received["provider_usage"],
        "request_sha256": base.sha256(author_request),
        "responsibility": "intermediate_authorship",
    })

    materials = _materials(proposal, result, authored)
    later = []
    for logical_index, (repeat, case, branch) in enumerate(schedule(), 3):
        state = CASE_STATES[case]
        body = action_body(state, materials[branch])
        status, _, error, received = recorder.call(logical_index, f"av{logical_index:03d}", body)
        availability, action = base.parse_action(received["content"], state)
        if status != 200 or error is not None:
            availability, action = "unavailable", None
        provider_available = status == 200 and error is None and received["content_available"]
        later_proposal = ProposalReceipt(provider_available, (action or received["content"]) if provider_available else "")
        later_result = apply_committed_action(state, profile_for(case), later_proposal)
        row = {
            "action": action,
            "availability": availability,
            "branch": branch,
            "case": case,
            "correct_action": availability == "available" and action == oracle_action(state, profile_for(case)),
            "external_result": base.exposed_result(later_result),
            "invocation": f"av{logical_index:03d}",
            "logical_index": logical_index,
            "proposal": asdict(later_proposal),
            "provider_usage": received["provider_usage"],
            "repeat": repeat,
            "request_sha256": base.sha256(body),
            "retained_material_sha256": base.sha256(materials[branch].encode()),
        }
        later.append(row)
        calls.append({**row, "responsibility": "later_action"})

    distributions = {
        branch: {
            case: base._distribution([row for row in later if row["branch"] == branch and row["case"] == case])
            for case in CASES
        }
        for branch in BRANCHES
    }
    comparisons = {}
    for branch in (RAW_PERSISTENCE, AUTHORED_DELIVERY, STATIC_INSTRUCTION):
        comparisons[f"{branch}_minus_{AUTHORED_ABLATION}"] = {
            case: {
                "correct_action_delta": distributions[branch][case]["correct_actions"] - distributions[AUTHORED_ABLATION][case]["correct_actions"],
                "total_variation_distance": base._total_variation(
                    distributions[branch][case]["action_counts"], distributions[AUTHORED_ABLATION][case]["action_counts"]
                ),
            }
            for case in CASES
        }
    packet = {
        "acquisition": {
            "action": calls[0]["action"],
            "correct_action": calls[0]["correct_action"],
            "external_result": base.exposed_result(result),
            "proposal": asdict(proposal),
        },
        "attempts": recorder.attempts,
        "authored_intermediate": calls[1],
        "branch_materials": {
            branch: {"sha256": base.sha256(material.encode()), "utf8_length": len(material.encode())}
            for branch, material in materials.items()
        },
        "calls": calls,
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
        raise CanonicalAuthorshipRefusal("retained_specimen_mismatch")
    retained = json.loads((evidence_dir / "packet.json").read_bytes())
    entries = []
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        request = (evidence_dir / "attempts" / f"{stem}.request.json").read_bytes()
        response = (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes()
        if base.sha256(request) != meta["request_sha256"] or base.sha256(response) != meta["response_sha256"]:
            raise CanonicalAuthorshipRefusal("retained_attempt_hash_mismatch")
        entries.append((request, response, meta))
    position = 0

    def replay_transport(body: bytes) -> tuple[int, bytes]:
        nonlocal position
        if position >= len(entries):
            raise CanonicalAuthorshipRefusal("missing_retained_attempt")
        request, response, meta = entries[position]
        position += 1
        if request != body:
            raise CanonicalAuthorshipRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(replay_transport)
    if position != len(entries) or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained):
        raise CanonicalAuthorshipRefusal("evidence_replay_mismatch")
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
        args.evidence_dir = Path("evidence") / f"canonical-mapping-authorship-{stamp}"
    started = time.monotonic()
    receipt = base.collect_provider_receipt()
    if not receipt["valid"]:
        raise CanonicalAuthorshipRefusal("provider_identity_mismatch")
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
