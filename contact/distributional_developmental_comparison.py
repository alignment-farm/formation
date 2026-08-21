"""Run a fresh distributional developmental comparison.

Prospective exploratory note
----------------------------
Question: does one consequence-exposed, model-authored interpretation shift
later cold-model action distributions relative to the same authored lineage
with delivery ablated, raw occurrence persistence, and a static family rule?
Observation of interest: repeated correct-action and full action distributions
on two new devices from the experienced controller family, while delivered
material stays selective on one device from an opposite-profile family.
Model/interface: ``ai/qwen3:14B-Q6_K`` through Docker Model Runner, using the
same JSON action and plain-text authorship surfaces as the preceding contact.
Budget: one acquisition action, one authorship call, and 96 later actions from
four branches by three cases by eight repeats; 98 logical calls and at most 102
physical attempts. Only transport failures may be retried, at most four times.
Stopping condition: stop after the fixed schedule or either ceiling. Preserve
unavailable and malformed outputs instead of replacing them.
Evidence destination: ``evidence/distributional-developmental-<run-id>/``.

This is exploratory. A distribution shift would show content-mediated
influence under this interface, not formation, transfer validation, or durable
competence.
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
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from contact.unselected_lineage_behavior_contact import collect_provider_receipt
from micro_environment.unselected_lineage_behavior import (
    APPLIED,
    FIRST_INCREASES,
    HELD,
    HOLD,
    SECOND_INCREASES,
    LineageProfile,
    LineageState,
    ProposalReceipt,
    apply_committed_action,
)
from unselected_lineage_specimen import (
    ACTION_RESPONSIBILITY,
    AUTHORSHIP_RESPONSIBILITY,
    oracle_action,
)


PROTOCOL_VERSION = "distributional-developmental-comparison-v1"
MODEL = "ai/qwen3:14B-Q6_K"
MODEL_DIGEST = "sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219"
ENDPOINT = "http://localhost:12434/engines/llama.cpp/v1/chat/completions"

AUTHORED_ABLATION = "authored_ablation"
RAW_PERSISTENCE = "raw_persistence"
AUTHORED_DELIVERY = "authored_delivery"
STATIC_INSTRUCTION = "static_instruction"
BRANCHES = (AUTHORED_ABLATION, RAW_PERSISTENCE, AUTHORED_DELIVERY, STATIC_INSTRUCTION)
CASES = ("same_family_up", "same_family_down", "other_family_up")
REPEATS = 8
PLANNED_LOGICAL_CALLS = 2 + len(BRANCHES) * len(CASES) * REPEATS
PHYSICAL_CALL_CEILING = 102
MAX_RETRIES = 4

ACTION_SETTINGS = {
    "max_tokens": 32,
    "response_format": {"type": "json_object"},
    "stream": False,
    "temperature": 0.6,
    "top_p": 0.95,
}
AUTHORSHIP_SETTINGS = {
    "max_tokens": 256,
    "stream": False,
    "temperature": 0.6,
    "top_p": 0.95,
}

ACTION_SYSTEM = """You are the action-authoring component of a cold practitioner. You have no memory outside this request.

DOMAIN RULES
Each controller family has two displayed controls. Within one family, the first/second movement profile is constant across devices. Exactly one control moves position up by one and the other moves position down by one. The action hold leaves position unchanged. Each new device uses new control strings. Choose the allowed action that moves the current position toward the target. If position already equals target, choose hold.

OUTPUT INTERFACE
Return exactly one JSON object with the single key "action". Its value must be one exact string from allowed_actions. Do not add keys or commentary."""

AUTHORSHIP_SYSTEM = """You are the retained-guidance author in a controlled cold-model experiment. You have no memory outside this request.

Your responsibility is supplied in the request record. Return only the guidance string you choose to preserve. Do not add a label or wrapper."""


class ComparisonRefusal(ValueError):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


PRIMARY_PROFILE = LineageProfile(opaque("primary-family"), SECOND_INCREASES)
OTHER_PROFILE = LineageProfile(opaque("other-family"), FIRST_INCREASES)
ACQUISITION = LineageState(
    PRIMARY_PROFILE.controller_family,
    opaque("acquisition-device"),
    410,
    411,
    (opaque("acquisition-first"), opaque("acquisition-second")),
)
CASE_STATES = {
    "same_family_up": LineageState(
        PRIMARY_PROFILE.controller_family,
        opaque("same-up-device"),
        700,
        701,
        (opaque("same-up-first"), opaque("same-up-second")),
    ),
    "same_family_down": LineageState(
        PRIMARY_PROFILE.controller_family,
        opaque("same-down-device"),
        633,
        632,
        (opaque("same-down-first"), opaque("same-down-second")),
    ),
    "other_family_up": LineageState(
        OTHER_PROFILE.controller_family,
        opaque("other-up-device"),
        812,
        813,
        (opaque("other-up-first"), opaque("other-up-second")),
    ),
}


def public_device(state: LineageState) -> dict[str, Any]:
    return {
        "allowed_actions": [*state.controls, HOLD],
        "controller_family": state.controller_family,
        "device": state.device,
        "position": state.position,
        "target": state.target,
    }


def specimen() -> dict[str, Any]:
    return {
        "acquisition": public_device(ACQUISITION),
        "branches": list(BRANCHES),
        "cases": [
            {
                "case": name,
                "device": public_device(state),
                "expected_action": oracle_action(state, PRIMARY_PROFILE if name != "other_family_up" else OTHER_PROFILE),
            }
            for name, state in CASE_STATES.items()
        ],
        "model": MODEL,
        "model_digest": MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
    }


def static_instruction() -> str:
    return (
        f"For controller family {PRIMARY_PROFILE.controller_family}, the second displayed control "
        "increases position and the first displayed control decreases position."
    )


def action_user(state: LineageState, retained_material: str) -> str:
    value = {
        "device": public_device(state),
        "responsibility": ACTION_RESPONSIBILITY,
        "retained_material": retained_material,
    }
    return f"ACTION REQUEST\n{canonical_json_bytes(value).decode()}\n/no_think"


def exposed_result(result: Any) -> dict[str, Any]:
    if result.status in (APPLIED, HELD):
        return {
            "application_status": result.status,
            "movement_direction": result.movement_direction,
            "position_after": result.position_after,
            "selected_slot": result.selected_slot,
            "target_reached": result.target_reached,
        }
    return {"application_status": result.status, "reason": result.reason}


def occurrence(state: LineageState, proposal: ProposalReceipt) -> dict[str, Any]:
    return {
        "committed_proposal": {"available": proposal.available, "content": proposal.content},
        "public_device": public_device(state),
    }


def experience_record(state: LineageState, proposal: ProposalReceipt, result: Any) -> dict[str, Any]:
    return {"external_result": exposed_result(result), "occurrence": occurrence(state, proposal)}


def authorship_user(state: LineageState, proposal: ProposalReceipt, result: Any) -> str:
    value = {**experience_record(state, proposal, result), "responsibility": AUTHORSHIP_RESPONSIBILITY}
    return f"AUTHORSHIP REQUEST\n{canonical_json_bytes(value).decode()}\n/no_think"


def envelope(system: str, user: str, settings: dict[str, Any]) -> bytes:
    return canonical_json_bytes({
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "model": MODEL,
        **settings,
    })


def action_body(state: LineageState, retained_material: str) -> bytes:
    return envelope(ACTION_SYSTEM, action_user(state, retained_material), ACTION_SETTINGS)


def authorship_body(state: LineageState, proposal: ProposalReceipt, result: Any) -> bytes:
    return envelope(AUTHORSHIP_SYSTEM, authorship_user(state, proposal, result), AUTHORSHIP_SETTINGS)


def parse_content(raw: bytes, status: int | None) -> tuple[str, bool, dict[str, Any]]:
    if status != 200:
        return "", False, {}
    try:
        value = json.loads(raw)
        content = value["choices"][0]["message"]["content"]
        if type(content) is not str:
            return "", False, value
        return content, True, value
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, IndexError, TypeError):
        return "", False, {}


def parse_action(content: str, state: LineageState) -> tuple[str, str | None]:
    try:
        value = json.loads(content)
        if type(value) is not dict or set(value) != {"action"} or value["action"] not in (*state.controls, HOLD):
            return "invalid", None
        return "available", value["action"]
    except (json.JSONDecodeError, TypeError):
        return "invalid", None


def profile_for(case: str) -> LineageProfile:
    return OTHER_PROFILE if case == "other_family_up" else PRIMARY_PROFILE


def schedule() -> tuple[tuple[int, str, str], ...]:
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_offset in range(len(CASES)):
            case = CASES[(repeat - 1 + case_offset) % len(CASES)]
            for branch_offset in range(len(BRANCHES)):
                branch = BRANCHES[(repeat - 1 + branch_offset) % len(BRANCHES)]
                rows.append((repeat, case, branch))
    if len(rows) != PLANNED_LOGICAL_CALLS - 2:
        raise ComparisonRefusal("schedule_size_mismatch")
    return tuple(rows)


Transport = Callable[[bytes], tuple[int, bytes]]


def live_transport(body: bytes) -> tuple[int, bytes]:
    request = Request(ENDPOINT, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=120) as response:
            return response.status, response.read()
    except HTTPError as error:
        return error.code, error.read()
    except (URLError, TimeoutError) as error:
        raise ConnectionError(str(error)) from error


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

    def call(self, logical_index: int, invocation: str, body: bytes) -> tuple[int | None, bytes, str | None, dict[str, Any]]:
        final: tuple[int | None, bytes, str | None] | None = None
        for attempt in (1, 2):
            if self.physical >= PHYSICAL_CALL_CEILING:
                raise ComparisonRefusal("physical_call_ceiling")
            self.physical += 1
            status = None
            raw = b""
            error = None
            try:
                status, raw = self.transport(body)
            except ConnectionError as exc:
                error = str(exc)
            retryable = error is not None or status in {408, 429, 500, 502, 503, 504}
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
            final = status, raw, error
            break
        if final is None:
            raise ComparisonRefusal("logical_call_not_completed")
        status, raw, error = final
        content, content_available, provider = parse_content(raw, status)
        return status, raw, error, {
            "content": content,
            "content_available": content_available,
            "provider_usage": provider.get("usage"),
        }


def _materials(proposal: ProposalReceipt, result: Any, authored: str) -> dict[str, str]:
    raw = canonical_json_bytes(experience_record(ACQUISITION, proposal, result)).decode()
    return {
        AUTHORED_ABLATION: "",
        RAW_PERSISTENCE: raw,
        AUTHORED_DELIVERY: authored,
        STATIC_INSTRUCTION: static_instruction(),
    }


def _distribution(rows: list[dict[str, Any]]) -> dict[str, Any]:
    labels = [row["action"] if row["action"] is not None else f"<{row['availability']}>" for row in rows]
    return {
        "action_counts": dict(sorted(Counter(labels).items())),
        "assigned": len(rows),
        "correct_actions": sum(bool(row["correct_action"]) for row in rows),
        "invalid_or_unavailable": sum(row["availability"] != "available" for row in rows),
    }


def _total_variation(left: dict[str, int], right: dict[str, int]) -> float:
    keys = set(left) | set(right)
    return sum(abs(left.get(key, 0) / REPEATS - right.get(key, 0) / REPEATS) for key in keys) / 2


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    recorder = Recorder(transport, evidence_dir)
    calls: list[dict[str, Any]] = []

    acquisition_body = action_body(ACQUISITION, "")
    status, _, error, received = recorder.call(1, "dv001", acquisition_body)
    availability, action = parse_action(received["content"], ACQUISITION)
    provider_available = status == 200 and error is None and received["content_available"]
    proposal_content = (action or received["content"]) if provider_available else ""
    proposal = ProposalReceipt(provider_available, proposal_content)
    result = apply_committed_action(ACQUISITION, PRIMARY_PROFILE, proposal)
    calls.append({
        "action": action,
        "availability": availability if status == 200 and error is None else "unavailable",
        "correct_action": availability == "available" and action == oracle_action(ACQUISITION, PRIMARY_PROFILE),
        "invocation": "dv001",
        "logical_index": 1,
        "provider_usage": received["provider_usage"],
        "request_sha256": sha256(acquisition_body),
        "responsibility": "acquisition_action",
    })

    author_body = authorship_body(ACQUISITION, proposal, result)
    author_status, _, author_error, authored_received = recorder.call(2, "dv002", author_body)
    authored_available = author_status == 200 and author_error is None and authored_received["content_available"]
    authored = authored_received["content"] if authored_available else ""
    calls.append({
        "available": authored_available,
        "content": authored,
        "content_sha256": sha256(authored.encode()),
        "invocation": "dv002",
        "logical_index": 2,
        "provider_usage": authored_received["provider_usage"],
        "request_sha256": sha256(author_body),
        "responsibility": "intermediate_authorship",
    })

    materials = _materials(proposal, result, authored)
    later = []
    for logical_index, (repeat, case, branch) in enumerate(schedule(), 3):
        state = CASE_STATES[case]
        body = action_body(state, materials[branch])
        status, _, error, received = recorder.call(logical_index, f"dv{logical_index:03d}", body)
        availability, action = parse_action(received["content"], state)
        if status != 200 or error is not None:
            availability, action = "unavailable", None
        provider_available = status == 200 and error is None and received["content_available"]
        proposal_content = (action or received["content"]) if provider_available else ""
        later_proposal = ProposalReceipt(provider_available, proposal_content)
        later_result = apply_committed_action(state, profile_for(case), later_proposal)
        row = {
            "action": action,
            "availability": availability,
            "branch": branch,
            "case": case,
            "correct_action": availability == "available" and action == oracle_action(state, profile_for(case)),
            "external_result": exposed_result(later_result),
            "invocation": f"dv{logical_index:03d}",
            "logical_index": logical_index,
            "proposal": asdict(later_proposal),
            "provider_usage": received["provider_usage"],
            "repeat": repeat,
            "retained_material_sha256": sha256(materials[branch].encode()),
            "retained_material_utf8_length": len(materials[branch].encode()),
            "request_sha256": sha256(body),
        }
        later.append(row)
        calls.append({**row, "responsibility": "later_action"})

    distributions = {
        branch: {case: _distribution([row for row in later if row["branch"] == branch and row["case"] == case]) for case in CASES}
        for branch in BRANCHES
    }
    comparisons = {}
    for branch in (RAW_PERSISTENCE, AUTHORED_DELIVERY, STATIC_INSTRUCTION):
        comparisons[f"{branch}_minus_{AUTHORED_ABLATION}"] = {
            case: {
                "correct_action_delta": distributions[branch][case]["correct_actions"] - distributions[AUTHORED_ABLATION][case]["correct_actions"],
                "total_variation_distance": _total_variation(
                    distributions[branch][case]["action_counts"],
                    distributions[AUTHORED_ABLATION][case]["action_counts"],
                ),
            }
            for case in CASES
        }
    packet = {
        "acquisition": {
            "action": calls[0]["action"],
            "correct_action": calls[0]["correct_action"],
            "external_result": exposed_result(result),
            "proposal": asdict(proposal),
        },
        "attempts": recorder.attempts,
        "authored_intermediate": {
            "available": authored_available,
            "content": authored,
            "content_sha256": sha256(authored.encode()),
        },
        "branch_materials": {
            branch: {
                "sha256": sha256(material.encode()),
                "utf8_length": len(material.encode()),
            }
            for branch, material in materials.items()
        },
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
    retained_specimen = (evidence_dir / "specimen.json").read_bytes()
    if retained_specimen != canonical_json_bytes(specimen()):
        raise ComparisonRefusal("retained_specimen_mismatch")
    retained = json.loads((evidence_dir / "packet.json").read_bytes())
    entries = []
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        request = (evidence_dir / "attempts" / f"{stem}.request.json").read_bytes()
        response = (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes()
        if sha256(request) != meta["request_sha256"] or sha256(response) != meta["response_sha256"]:
            raise ComparisonRefusal("retained_attempt_hash_mismatch")
        entries.append((request, response, meta))
    position = 0

    def replay_transport(body: bytes) -> tuple[int, bytes]:
        nonlocal position
        if position >= len(entries):
            raise ComparisonRefusal("missing_retained_attempt")
        request, response, meta = entries[position]
        position += 1
        if request != body:
            raise ComparisonRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(replay_transport)
    if position != len(entries) or canonical_json_bytes(replayed) != canonical_json_bytes(retained):
        raise ComparisonRefusal("evidence_replay_mismatch")
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
        args.evidence_dir = Path("evidence") / f"distributional-developmental-{stamp}"
    started = time.monotonic()
    receipt = collect_provider_receipt()
    if not receipt["valid"]:
        raise ComparisonRefusal("provider_identity_mismatch")
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
