"""Run the reviewed phase-coupled exploratory contact."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Callable

from contact.calibration_mechanism_discovery import (
    ContactRunner as BaseRunner,
    ContactStop,
    EvidenceWriter,
)
from contact.exploratory_developmental_contact import (
    ENDPOINT,
    INSPECT_TAG,
    MODEL,
    MODEL_DIGEST,
    LiveInvoker,
    ProviderAttempt,
    collect_provider_receipt,
)
from micro_environment.phase_coupled_control import (
    HOLD,
    PhaseActionResult,
    PhaseProfile,
    PhaseState,
    apply_phase_action,
    apply_phase_commitment,
)
from micro_environment.phase_coupled_specimen import (
    PhaseSpecimenRefusal,
    acquisition_occurrence,
    canonical_json_bytes,
    make_profile,
    make_state,
    offer_envelope,
    permitted_actions,
    validate_action_object,
)
from phase_coupled_specimen_oracle import classify_one_action


PROTOCOL_VERSION = "phase-coupled-exploratory-contact-v0"
PLANNED_LOGICAL_CALLS = 69
PHYSICAL_CALL_CEILING = 72
TOKEN_DELTA_CEILING = 24

ACTOR_SETTINGS: dict[str, object] = {
    "max_tokens": 128,
    "temperature": 0.6,
    "top_p": 0.95,
    "stream": False,
    "response_format": {"type": "json_object"},
}
INTERPRETER_SETTINGS: dict[str, object] = {
    **ACTOR_SETTINGS,
    "max_tokens": 256,
}

PUBLIC_RULE = """Each device has two ordered controls and one of two public phases. In each
phase, exactly one ordered slot increases position by one and the other
decreases it by one. The increasing slot is opposite in the two phases. Every
control action toggles phase. Hold changes neither position nor phase. The
phase-to-slot profile is stable within one controller family. Control strings
have no reusable meaning across devices.
Use current position, target, phase, and any warranted family evidence to choose
an action or committed action sequence. If no warranted profile evidence applies
to the current family, hold rather than guess a control."""

AUTHORSHIP_INSTRUCTION = """State one reusable change in preparedness that the experience warrants,
including where it applies and what later observation should count against it."""

ACTOR_SYSTEM = f"""You are the action-selection component of a cold practitioner. You have no
memory outside this request.

PUBLIC OPERATING RULE
{PUBLIC_RULE}

Return exactly one JSON object with the single key "actions". Its value must be
an array containing exactly the requested number of entries. Every entry must
be copied exactly from PERMITTED ACTIONS. Do not add keys or commentary."""

INTERPRETER_SYSTEM = f"""You are the candidate author inside a formation runtime. You have no memory
outside this request.

PUBLIC OPERATING RULE
{PUBLIC_RULE}

Return exactly one JSON object with only "change" and "counterevidence". Each
value may be a string or null. Do not add keys or commentary."""

COMMITMENT_OFFERS = (
    "no_persistence",
    "raw_occurrence",
    "authored_direct",
    "governed_candidate",
    "presence_ablation",
    "content_ablation",
)
PROBE_OFFERS = COMMITMENT_OFFERS[:4]


@dataclass(frozen=True, slots=True)
class LaterCase:
    case_id: str
    world_id: str
    relation: str
    state: PhaseState
    profile: PhaseProfile
    expected_actions: tuple[str, ...]
    commitment: bool


@dataclass(frozen=True, slots=True)
class World:
    world_id: str
    acquisition: PhaseState
    acquisition_profile: PhaseProfile


PROFILE_A = make_profile(0, 0)
PROFILE_B = make_profile(1, 1)
PROFILE_A_OTHER = make_profile(2, 1)
PROFILE_B_OTHER = make_profile(3, 0)

WORLD_A = World("world-a", make_state(PROFILE_A, 0, 0, 0, 2), PROFILE_A)
WORLD_B = World("world-b", make_state(PROFILE_B, 1, 0, 0, 2), PROFILE_B)
WORLDS = (WORLD_A, WORLD_B)


def _commitment_case(
    case_id: str,
    world: World,
    device_counter: int,
    phase_index: int,
    position: int,
    target: int,
) -> LaterCase:
    state = make_state(
        world.acquisition_profile,
        device_counter,
        phase_index,
        position,
        target,
    )
    phase_slot = world.acquisition_profile.phase_zero_increasing_slot ^ phase_index
    toward = phase_slot if target > position else 1 - phase_slot
    expected = (state.controls[toward], state.controls[1 - toward])
    return LaterCase(
        case_id, world.world_id, "same_family_commitment", state,
        world.acquisition_profile, expected, True
    )


COMMITMENT_CASES = (
    _commitment_case("a-p0-up", WORLD_A, 2, 0, 10, 12),
    _commitment_case("a-p0-down", WORLD_A, 3, 0, 10, 8),
    _commitment_case("a-p1-up", WORLD_A, 4, 1, 20, 22),
    _commitment_case("a-p1-down", WORLD_A, 5, 1, 20, 18),
    _commitment_case("b-p0-up", WORLD_B, 6, 0, 30, 32),
    _commitment_case("b-p0-down", WORLD_B, 7, 0, 30, 28),
    _commitment_case("b-p1-up", WORLD_B, 8, 1, 40, 42),
    _commitment_case("b-p1-down", WORLD_B, 9, 1, 40, 38),
)

_A_OTHER_STATE = make_state(PROFILE_A_OTHER, 10, 0, 4, 5)
_B_OTHER_STATE = make_state(PROFILE_B_OTHER, 11, 1, 9, 8)
_A_CURRENT_STATE = make_state(PROFILE_A, 12, 0, 7, 7)
_B_CURRENT_STATE = make_state(PROFILE_B, 13, 1, 9, 9)

PROBE_CASES = (
    LaterCase("a-other", "world-a", "unobserved_family", _A_OTHER_STATE,
              PROFILE_A_OTHER, (HOLD,), False),
    LaterCase("b-other", "world-b", "unobserved_family", _B_OTHER_STATE,
              PROFILE_B_OTHER, (HOLD,), False),
    LaterCase("a-current", "world-a", "already_current", _A_CURRENT_STATE,
              PROFILE_A, (HOLD,), False),
    LaterCase("b-current", "world-b", "already_current", _B_CURRENT_STATE,
              PROFILE_B, (HOLD,), False),
)

INTERFACE_PROFILE = make_profile(4, 0)
INTERFACE_STATE = make_state(INTERFACE_PROFILE, 14, 0, 3, 3)


class DuplicateKey(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


@dataclass(frozen=True, slots=True)
class ActionParse:
    actions: tuple[str, ...] | None
    refusal: str | None


def parse_actions(content: object, state: PhaseState, commitment: bool) -> ActionParse:
    if type(content) is not str:
        return ActionParse(None, "content_not_string")
    try:
        decoded = json.loads(
            content,
            object_pairs_hook=_unique_object,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
        actions = validate_action_object(decoded, state, commitment=commitment)
    except (json.JSONDecodeError, DuplicateKey, ValueError, PhaseSpecimenRefusal):
        return ActionParse(None, "invalid_action_object")
    return ActionParse(actions, None)


@dataclass(frozen=True, slots=True)
class CandidateParse:
    candidate: dict[str, str | None] | None
    refusal: str | None


def parse_candidate(content: object) -> CandidateParse:
    if type(content) is not str:
        return CandidateParse(None, "content_not_string")
    try:
        decoded = json.loads(
            content,
            object_pairs_hook=_unique_object,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
    except (json.JSONDecodeError, DuplicateKey, ValueError):
        return CandidateParse(None, "invalid_json")
    if type(decoded) is not dict or set(decoded) != {"change", "counterevidence"}:
        return CandidateParse(None, "invalid_candidate_object")
    if any(decoded[key] is not None and type(decoded[key]) is not str for key in decoded):
        return CandidateParse(None, "invalid_candidate_value")
    return CandidateParse(decoded, None)


def govern_candidate(
    parsed: CandidateParse, occurrence: dict[str, object], controls: tuple[str, str]
) -> dict[str, object]:
    reasons: list[str] = []
    if parsed.refusal is not None:
        reasons.append(parsed.refusal)
    candidate = parsed.candidate
    if candidate is not None:
        for key in ("change", "counterevidence"):
            value = candidate[key]
            if type(value) is not str or value.strip() == "":
                reasons.append(f"{key}_not_nonempty_string")
            elif any(token in value for token in controls):
                reasons.append(f"{key}_copies_acquisition_control")
    return {
        "admitted": candidate is not None and not reasons,
        "refusals": reasons,
        "candidate": candidate,
        "occurrence_sha256": hashlib.sha256(canonical_json_bytes(occurrence)).hexdigest(),
    }


def public_state(state: PhaseState) -> dict[str, object]:
    return {
        "controller_family": state.controller_family,
        "controls": list(state.controls),
        "device": state.device,
        "phase": state.phase,
        "position": state.position,
        "target": state.target,
    }


def actor_user_prompt(state: PhaseState, material: object, action_count: int) -> str:
    return "\n".join(
        (
            "PUBLIC STATE",
            canonical_json_bytes(public_state(state)).decode("utf-8"),
            "",
            "PERMITTED ACTIONS",
            canonical_json_bytes(
                list(permitted_actions(state, commitment=action_count == 2))
            ).decode("utf-8"),
            "",
            offer_envelope(material).decode("utf-8"),
            "",
            f"Return exactly {action_count} action entry or entries in one actions array.",
            "/no_think",
        )
    )


def actor_envelope(
    state: PhaseState, material: object, action_count: int
) -> dict[str, object]:
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": ACTOR_SYSTEM},
            {"role": "user", "content": actor_user_prompt(state, material, action_count)},
        ],
        **ACTOR_SETTINGS,
    }


def interpreter_envelope(occurrence: dict[str, object]) -> dict[str, object]:
    user = "\n".join(
        (
            "ACQUISITION OCCURRENCE",
            canonical_json_bytes(occurrence).decode("utf-8"),
            "",
            "AUTHORSHIP INSTRUCTION",
            AUTHORSHIP_INSTRUCTION,
            "/no_think",
        )
    )
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": INTERPRETER_SYSTEM},
            {"role": "user", "content": user},
        ],
        **INTERPRETER_SETTINGS,
    }


@dataclass(frozen=True, slots=True)
class LogicalCall:
    logical_index: int
    call_id: str
    responsibility: str
    envelope: dict[str, object]
    state: PhaseState | None = None
    profile: PhaseProfile | None = None
    world_id: str | None = None
    offer_key: str | None = None
    probe_id: str | None = None
    relation: str | None = None
    repetition: int | None = None
    expected_actions: tuple[str, ...] | None = None
    commitment: bool = False
    activated: bool | None = None
    material: object = None

    @property
    def request_body(self) -> bytes:
        return canonical_json_bytes(self.envelope)

    @property
    def offer_utf8_length(self) -> int:
        return len(canonical_json_bytes({"material": self.material}))


Invoker = Callable[[LogicalCall, int], ProviderAttempt]


def content_ablation(candidate: dict[str, str | None]) -> dict[str, str]:
    result: dict[str, str] = {}
    for key in ("change", "counterevidence"):
        value = candidate[key]
        if type(value) is not str:
            raise ValueError("admitted_candidate_strings_required")
        result[key] = "x" * len(value.encode("utf-8"))
    return result


def offer_material(
    offer_key: str,
    world_material: dict[str, object],
    state: PhaseState,
) -> object:
    occurrence = world_material["occurrence"]
    governance = world_material["governance"]
    candidate = governance["candidate"]
    admitted = governance["admitted"] is True
    authorized = admitted and state.controller_family == world_material["source_family"]
    if offer_key == "no_persistence":
        return None
    if offer_key == "raw_occurrence":
        return occurrence
    if offer_key == "authored_direct":
        return candidate
    if offer_key == "governed_candidate":
        return candidate if authorized else None
    if offer_key == "presence_ablation":
        return None
    if offer_key == "content_ablation":
        return content_ablation(candidate) if authorized and type(candidate) is dict else None
    raise ValueError("unknown_offer")


def later_schedule(
    materials: dict[str, dict[str, object]], start_index: int = 6
) -> tuple[LogicalCall, ...]:
    calls: list[LogicalCall] = []
    index = start_index
    for row, case in enumerate(COMMITMENT_CASES):
        order = COMMITMENT_OFFERS[row % 6 :] + COMMITMENT_OFFERS[: row % 6]
        for offer_key in order:
            material = offer_material(offer_key, materials[case.world_id], case.state)
            calls.append(
                LogicalCall(
                    index,
                    f"{case.case_id}-{offer_key}",
                    "actor",
                    actor_envelope(case.state, material, 2),
                    state=case.state,
                    profile=case.profile,
                    world_id=case.world_id,
                    offer_key=offer_key,
                    probe_id=case.case_id,
                    relation=case.relation,
                    expected_actions=case.expected_actions,
                    commitment=True,
                    activated=(
                        materials[case.world_id]["governance"]["admitted"] is True
                        and case.state.controller_family
                        == materials[case.world_id]["source_family"]
                        if offer_key in ("governed_candidate", "content_ablation")
                        else None
                    ),
                    material=material,
                )
            )
            index += 1
    for row, case in enumerate(PROBE_CASES):
        order = PROBE_OFFERS[row % 4 :] + PROBE_OFFERS[: row % 4]
        for offer_key in order:
            material = offer_material(offer_key, materials[case.world_id], case.state)
            calls.append(
                LogicalCall(
                    index,
                    f"{case.case_id}-{offer_key}",
                    "actor",
                    actor_envelope(case.state, material, 1),
                    state=case.state,
                    profile=case.profile,
                    world_id=case.world_id,
                    offer_key=offer_key,
                    probe_id=case.case_id,
                    relation=case.relation,
                    expected_actions=case.expected_actions,
                    commitment=False,
                    activated=(
                        materials[case.world_id]["governance"]["admitted"] is True
                        and case.state.controller_family
                        == materials[case.world_id]["source_family"]
                        if offer_key == "governed_candidate"
                        else None
                    ),
                    material=material,
                )
            )
            index += 1
    return tuple(calls)


def _prompt_tokens(attempt: ProviderAttempt) -> int | None:
    envelope = attempt.response_envelope
    usage = envelope.get("usage") if type(envelope) is dict else None
    value = usage.get("prompt_tokens") if type(usage) is dict else None
    return value if type(value) is int else None


def _trigrams(value: str) -> frozenset[str]:
    return frozenset(value[index : index + 3] for index in range(max(0, len(value) - 2)))


def _trigram_similarity(left: str, right: str) -> float:
    left_set = _trigrams(left)
    right_set = _trigrams(right)
    union = left_set | right_set
    return 0.0 if not union else len(left_set & right_set) / len(union)


def lexical_diagnostic(
    world: World, governance: dict[str, object]
) -> dict[str, object]:
    candidate = governance.get("candidate")
    if type(candidate) is not dict:
        return {"world_id": world.world_id, "available": False, "reason": "no_parseable_candidate"}
    change = candidate.get("change") if type(candidate.get("change")) is str else ""
    counter = (
        candidate.get("counterevidence")
        if type(candidate.get("counterevidence")) is str
        else ""
    )
    text = f"{change}\n{counter}".replace(world.acquisition.controller_family, "")
    cases = [
        case
        for case in (*COMMITMENT_CASES, *PROBE_CASES)
        if case.world_id == world.world_id
    ]
    scores = {
        case.case_id: _trigram_similarity(
            text, canonical_json_bytes(public_state(case.state)).decode("utf-8")
        )
        for case in cases
    }
    unrelated = next(case for case in cases if case.relation == "unobserved_family")
    same_scores = [
        score
        for case_id, score in scores.items()
        if case_id != unrelated.case_id
        and next(case for case in cases if case.case_id == case_id).state.controller_family
        == world.acquisition.controller_family
    ]
    available = bool(same_scores and scores[unrelated.case_id] > min(same_scores))
    return {
        "world_id": world.world_id,
        "available": available,
        "scores": scores,
        "unrelated_case": unrelated.case_id,
        "strictly_exceeds_one_same_family": available,
        "claim_language": "lexical selectivity unavailable" if not available else "lexical decoy pressure available",
    }


class ContactRunner(BaseRunner):
    def record_actor(
        self, call: LogicalCall, attempt: ProviderAttempt
    ) -> dict[str, object]:
        if call.state is None or call.profile is None:
            raise ContactStop("actor_environment_missing")
        parsed = parse_actions(attempt.content, call.state, call.commitment)
        results: tuple[PhaseActionResult, ...] = ()
        if parsed.actions is not None:
            if call.commitment:
                results = apply_phase_commitment(call.state, call.profile, parsed.actions)
            else:
                results = (apply_phase_action(call.state, call.profile, parsed.actions[0]),)
        warranted = call.state.controller_family == (
            WORLD_A.acquisition.controller_family
            if call.world_id == "world-a"
            else WORLD_B.acquisition.controller_family
        )
        warrant_labels = (
            []
            if parsed.actions is None or call.commitment or call.probe_id is None
            else [
                classify_one_action(
                    call.state,
                    call.profile,
                    parsed.actions[0],
                    warranted_profile_evidence=warranted,
                )
            ]
        )
        record = {
            "logical_index": call.logical_index,
            "call_id": call.call_id,
            "responsibility": "actor",
            "world_id": call.world_id,
            "offer_key": call.offer_key,
            "probe_id": call.probe_id,
            "relation": call.relation,
            "activated": call.activated,
            "state": public_state(call.state),
            "content": attempt.content,
            "message": attempt.message,
            "surfaced_actions": parsed.actions,
            "action_refusal": parsed.refusal,
            "environment_results": [asdict(result) for result in results],
            "expected_actions": call.expected_actions,
            "expected_actions_match": (
                None if call.expected_actions is None else parsed.actions == call.expected_actions
            ),
            "warrant_labels": warrant_labels,
            "prompt_tokens": _prompt_tokens(attempt),
            "request_sha256": hashlib.sha256(call.request_body).hexdigest(),
            "offer_utf8_length": call.offer_utf8_length,
        }
        self.logical_records.append(record)
        self.writer.write_logical(call, record)
        return record

    def record_interpreter(
        self,
        call: LogicalCall,
        attempt: ProviderAttempt,
        occurrence: dict[str, object],
        controls: tuple[str, str],
    ) -> tuple[dict[str, object], dict[str, object]]:
        parsed = parse_candidate(attempt.content)
        governance = govern_candidate(parsed, occurrence, controls)
        record = {
            "logical_index": call.logical_index,
            "call_id": call.call_id,
            "responsibility": "interpreter",
            "world_id": call.world_id,
            "content": attempt.content,
            "message": attempt.message,
            "candidate": parsed.candidate,
            "candidate_refusal": parsed.refusal,
            "governance": governance,
            "prompt_tokens": _prompt_tokens(attempt),
            "occurrence_utf8_length": len(canonical_json_bytes(occurrence)),
            "candidate_utf8_length": (
                None
                if parsed.candidate is None
                else len(canonical_json_bytes(parsed.candidate))
            ),
        }
        self.logical_records.append(record)
        self.writer.write_logical(call, record)
        return record, governance

    def summary(self, state: str, stop_reason: str | None) -> dict[str, object]:
        later = [record for record in self.logical_records if record.get("probe_id")]
        cells = [
            {
                "world_id": record["world_id"],
                "case_id": record["probe_id"],
                "relation": record["relation"],
                "offer_key": record["offer_key"],
                "surfaced_actions": record["surfaced_actions"],
                "expected_actions": record["expected_actions"],
                "expected_actions_match": record["expected_actions_match"],
                "warrant_labels": record["warrant_labels"],
                "action_refusal": record["action_refusal"],
                "terminal_target_reached": (
                    None
                    if not record["environment_results"]
                    else record["environment_results"][-1]["target_reached"]
                ),
                "prompt_tokens": record["prompt_tokens"],
                "offer_utf8_length": record["offer_utf8_length"],
            }
            for record in later
        ]
        content_diagnostics: list[dict[str, object]] = []
        presence_diagnostics: list[dict[str, object]] = []
        request_parity: list[dict[str, object]] = []
        for case in COMMITMENT_CASES:
            members = {
                record["offer_key"]: record
                for record in later
                if record["probe_id"] == case.case_id
            }
            governed = members.get("governed_candidate")
            ablated = members.get("content_ablation")
            if governed is None or ablated is None:
                continue
            g_tokens = governed["prompt_tokens"]
            a_tokens = ablated["prompt_tokens"]
            delta = (
                abs(g_tokens - a_tokens)
                if type(g_tokens) is int and type(a_tokens) is int
                else None
            )
            authorized = governed["activated"] is True
            interpretable = authorized and delta is not None and delta <= TOKEN_DELTA_CEILING
            diagnostic: dict[str, object] = {
                "case_id": case.case_id,
                "authorized": authorized,
                "prompt_token_delta": delta,
                "available": interpretable,
                "interpretable": interpretable,
            }
            if interpretable:
                diagnostic["action_difference"] = (
                    governed["surfaced_actions"] != ablated["surfaced_actions"]
                )
                diagnostic["language"] = "content-associated action difference only"
            else:
                diagnostic["unavailable_reason"] = (
                    "not_authorized"
                    if not authorized
                    else "prompt_token_delta_unavailable_or_exceeded"
                )
            content_diagnostics.append(diagnostic)
            presence = members.get("presence_ablation")
            if presence is not None:
                presence_available = governed["activated"] is True
                presence_diagnostic: dict[str, object] = {
                    "case_id": case.case_id,
                    "authorized": presence_available,
                    "available": presence_available,
                }
                if presence_available:
                    presence_diagnostic["action_difference"] = (
                        governed["surfaced_actions"] != presence["surfaced_actions"]
                    )
                    presence_diagnostic["language"] = (
                        "single-cell governed-versus-presence observation only"
                    )
                else:
                    presence_diagnostic["unavailable_reason"] = "not_authorized"
                presence_diagnostics.append(presence_diagnostic)
        for case in (*COMMITMENT_CASES, *PROBE_CASES):
            members = [record for record in later if record["probe_id"] == case.case_id]
            by_hash: dict[str, list[str]] = {}
            for record in members:
                by_hash.setdefault(record["request_sha256"], []).append(record["offer_key"])
            request_parity.extend(
                {
                    "case_id": case.case_id,
                    "request_sha256": digest,
                    "offers": offers,
                    "surfaced_actions": [
                        record["surfaced_actions"]
                        for record in members
                        if record["request_sha256"] == digest
                    ],
                    "identical_request_equivalence": True,
                    "pairwise_mechanism_comparison_forbidden": True,
                }
                for digest, offers in by_hash.items()
                if len(offers) > 1
            )
        interface_records = [
            record for record in self.logical_records if record["call_id"] == "interface-disposable"
        ]
        acquisition_records = [
            record
            for record in self.logical_records
            if record["responsibility"] == "actor" and record["call_id"].endswith("-acquisition")
        ]
        return {
            "protocol": PROTOCOL_VERSION,
            "evidence_class": "exploratory_mechanism_observation_only",
            "contact_state": state,
            "stop_reason": stop_reason,
            "model": MODEL,
            "model_digest": MODEL_DIGEST,
            "planned_logical_calls": PLANNED_LOGICAL_CALLS,
            "completed_logical_calls": len(self.logical_records),
            "physical_call_ceiling": self.physical_ceiling,
            "physical_attempts": self.physical_attempts,
            "governance": self.governance,
            "interface_observability": (
                None
                if not interface_records
                else {
                    "observable": interface_records[0]["surfaced_actions"] is not None,
                    "surfaced_actions": interface_records[0]["surfaced_actions"],
                    "action_refusal": interface_records[0]["action_refusal"],
                }
            ),
            "acquisitions": [
                {
                    "world_id": record["world_id"],
                    "observable": record["surfaced_actions"] is not None,
                    "surfaced_actions": record["surfaced_actions"],
                    "action_refusal": record["action_refusal"],
                    "environment_results": record["environment_results"],
                }
                for record in acquisition_records
            ],
            "cells": cells,
            "content_diagnostics": content_diagnostics,
            "presence_diagnostics": presence_diagnostics,
            "request_parity_equivalence_classes": request_parity,
            "lexical_diagnostics": [
                lexical_diagnostic(world, self.governance.get(world.world_id, {}))
                for world in WORLDS
            ],
            "formation_verdict": None,
            "validation_verdict": None,
        }


def _protocol_record() -> dict[str, object]:
    return {
        "protocol": PROTOCOL_VERSION,
        "model": MODEL,
        "inspect_tag": INSPECT_TAG,
        "model_digest": MODEL_DIGEST,
        "endpoint": ENDPOINT,
        "public_rule": PUBLIC_RULE,
        "actor_settings": ACTOR_SETTINGS,
        "interpreter_settings": INTERPRETER_SETTINGS,
        "commitment_offers": COMMITMENT_OFFERS,
        "probe_offers": PROBE_OFFERS,
        "worlds": [
            {
                "world_id": world.world_id,
                "acquisition": public_state(world.acquisition),
                "profile": asdict(world.acquisition_profile),
            }
            for world in WORLDS
        ],
        "commitment_cases": [asdict(case) for case in COMMITMENT_CASES],
        "probe_cases": [asdict(case) for case in PROBE_CASES],
        "interface_state": public_state(INTERFACE_STATE),
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "token_delta_ceiling": TOKEN_DELTA_CEILING,
        "formation_and_validation_verdicts_forbidden": True,
    }


def run_contact(
    invoker: Invoker,
    directory: Path,
    provider_receipt: dict[str, object],
    physical_ceiling: int = PHYSICAL_CALL_CEILING,
) -> dict[str, object]:
    writer = EvidenceWriter(directory)
    writer.write_json("protocol.json", _protocol_record())
    writer.write_json("provider.json", provider_receipt)
    runner = ContactRunner(invoker, writer, physical_ceiling)
    if provider_receipt.get("valid") is not True:
        summary = runner.summary("stopped", "provider_receipt_invalid")
        writer.write_json("summary.json", summary)
        return summary

    try:
        interface = LogicalCall(
            1, "interface-disposable", "actor",
            actor_envelope(INTERFACE_STATE, None, 1),
            state=INTERFACE_STATE, profile=INTERFACE_PROFILE, material=None,
        )
        interface_record = runner.record_actor(interface, runner.invoke(interface))
        if interface_record["surfaced_actions"] is None:
            summary = runner.summary("stopped", "interface_action_unobservable")
            writer.write_json("summary.json", summary)
            return summary

        materials: dict[str, dict[str, object]] = {}
        logical_index = 2
        for world in WORLDS:
            acquisition_call = LogicalCall(
                logical_index,
                f"{world.world_id}-acquisition",
                "actor",
                actor_envelope(world.acquisition, None, 2),
                state=world.acquisition,
                profile=world.acquisition_profile,
                world_id=world.world_id,
                commitment=True,
                material=None,
            )
            acquisition = runner.record_actor(
                acquisition_call, runner.invoke(acquisition_call)
            )
            actions = acquisition["surfaced_actions"]
            if actions is None:
                summary = runner.summary(
                    "stopped", f"{world.world_id}_acquisition_pair_unobservable"
                )
                writer.write_json("summary.json", summary)
                return summary
            occurrence = acquisition_occurrence(
                world.acquisition, world.acquisition_profile, actions
            )
            writer.write_json(f"{world.world_id}-occurrence.json", occurrence)
            logical_index += 1
            interpreter_call = LogicalCall(
                logical_index,
                f"{world.world_id}-interpretation",
                "interpreter",
                interpreter_envelope(occurrence),
                world_id=world.world_id,
            )
            _, governance = runner.record_interpreter(
                interpreter_call,
                runner.invoke(interpreter_call),
                occurrence,
                world.acquisition.controls,
            )
            runner.governance[world.world_id] = governance
            materials[world.world_id] = {
                "occurrence": occurrence,
                "governance": governance,
                "source_family": world.acquisition.controller_family,
            }
            logical_index += 1

        schedule = later_schedule(materials, logical_index)
        if len(schedule) != 64 or schedule[-1].logical_index != PLANNED_LOGICAL_CALLS:
            raise ContactStop("schedule_drifted")
        for call in schedule:
            runner.record_actor(call, runner.invoke(call))
        summary = runner.summary("completed", None)
    except ContactStop as stop:
        summary = runner.summary("stopped", str(stop))
    writer.write_json("summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if not args.live:
        raise SystemExit("live contact requires --live")
    receipt = collect_provider_receipt()
    summary = run_contact(LiveInvoker(), args.evidence_dir, receipt)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["contact_state"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
