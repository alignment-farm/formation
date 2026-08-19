"""Run the reviewed occurrence-accounting authorship-only contact."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import unicodedata
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
from micro_environment.phase_coupled_control import PhaseProfile, PhaseState
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
from contact.phase_coupled_exploratory_contact import PUBLIC_RULE, public_state


PROTOCOL_VERSION = "occurrence-accounting-exploratory-contact-v0"
PLANNED_LOGICAL_CALLS = 37
PHYSICAL_CALL_CEILING = 40
SAMPLES_PER_CONDITION = 2
TOKEN_DELTA_CEILING = 24
CONTENT_CONTROL_SEED = "formation.occurrence-accounting.content-control.v1"
CONTENT_CONTROL_ALPHABET = "ghijkmnpqrstuvwxyz"

AUTHOR_SETTINGS: dict[str, object] = {
    "max_tokens": 256,
    "temperature": 0.6,
    "top_p": 0.95,
    "stream": False,
    "response_format": {"type": "json_object"},
}
ACTOR_SETTINGS: dict[str, object] = {**AUTHOR_SETTINGS, "max_tokens": 128}

ACCOUNT_RESPONSIBILITY = """Give a faithful account of what happened in this occurrence using only what
the record supports. Include any uncertainty. In the account value, do not
propose a future change or action."""

AUTHORSHIP_RESPONSIBILITY = """State one reusable change in preparedness that the experience warrants,
including where it applies and what later observation should count against it."""

STATIC_EXPANSION = (
    "Before proposing, inspect what the occurrence itself supports and what remains\n"
    "uncertain."
)

ACTOR_SYSTEM = f"""You are the action-selection component of a cold practitioner. You have no
memory outside this request.

PUBLIC OPERATING RULE
{PUBLIC_RULE}

Return exactly one JSON object with the single key "actions". Its value must be
an array containing exactly the requested number of entries. Every entry must
be copied exactly from PERMITTED ACTIONS. Do not add keys or commentary."""

ACCOUNT_SYSTEM = f"""You are the occurrence-accounting component of a cold practitioner. You have
no memory outside this request.

PUBLIC OPERATING RULE
{PUBLIC_RULE}

Return exactly one JSON object with the single key "account". Its value must be
a string or null. Do not add keys or commentary."""

CANDIDATE_SYSTEM = f"""You are the candidate author inside a formation runtime. You have no memory
outside this request.

PUBLIC OPERATING RULE
{PUBLIC_RULE}

Return exactly one JSON object with only "change" and "counterevidence". Each
value may be a string or null. Do not add keys or commentary."""

SAME_RESPONSE_SYSTEM = f"""You are the occurrence-accounting and candidate-authoring component of a cold
practitioner. You have no memory outside this request.

PUBLIC OPERATING RULE
{PUBLIC_RULE}

Return exactly one JSON object whose keys, in order, are "account", "change",
and "counterevidence". Each value may be a string or null. Do not add keys or
commentary."""

CONDITIONS = (
    "direct",
    "withheld",
    "delivered",
    "occurrence_repeated",
    "static_expanded",
    "same_response",
    "restatement",
    "content_control",
)

PUBLIC_FORMATION_CONDITIONS = {
    "direct": "direct_null",
    "withheld": "withheld_null",
    "delivered": "exact_account_output",
    "occurrence_repeated": "exact_occurrence_repeated",
    "static_expanded": "static_expanded_instruction",
    "same_response": "same_response_sequence",
    "restatement": "deterministic_restatement",
    "content_control": "account_content_control",
}

ROUND_ORDERS: dict[tuple[int, str], tuple[str, ...]] = {
    (1, "world-e"): CONDITIONS,
    (1, "world-f"): (
        "static_expanded", "same_response", "restatement", "content_control",
        "direct", "withheld", "delivered", "occurrence_repeated",
    ),
    (2, "world-e"): (
        "delivered", "occurrence_repeated", "static_expanded", "same_response",
        "restatement", "content_control", "direct", "withheld",
    ),
    (2, "world-f"): (
        "restatement", "content_control", "direct", "withheld", "delivered",
        "occurrence_repeated", "static_expanded", "same_response",
    ),
}


@dataclass(frozen=True, slots=True)
class World:
    world_id: str
    state: PhaseState
    profile: PhaseProfile


WORLD_E_PROFILE = make_profile(5, 0)
WORLD_F_PROFILE = make_profile(6, 1)
INTERFACE_PROFILE = make_profile(7, 0)
WORLD_E = World("world-e", make_state(WORLD_E_PROFILE, 20, 0, 0, 2), WORLD_E_PROFILE)
WORLD_F = World("world-f", make_state(WORLD_F_PROFILE, 21, 0, 0, 2), WORLD_F_PROFILE)
WORLDS = (WORLD_E, WORLD_F)
INTERFACE_STATE = make_state(INTERFACE_PROFILE, 22, 0, 3, 3)


class DuplicateKey(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


def _decode_object(content: object) -> tuple[dict[str, object] | None, str | None]:
    if type(content) is not str:
        return None, "content_not_string"
    try:
        value = json.loads(
            content,
            object_pairs_hook=_unique_object,
            parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
        )
    except (json.JSONDecodeError, DuplicateKey, ValueError):
        return None, "invalid_json"
    if type(value) is not dict:
        return None, "object_required"
    return value, None


@dataclass(frozen=True, slots=True)
class ActionParse:
    actions: tuple[str, ...] | None
    refusal: str | None


def parse_actions(content: object, state: PhaseState, commitment: bool) -> ActionParse:
    value, refusal = _decode_object(content)
    if refusal is not None:
        return ActionParse(None, refusal)
    try:
        actions = validate_action_object(value, state, commitment=commitment)
    except (PhaseSpecimenRefusal, ValueError):
        return ActionParse(None, "invalid_action_object")
    return ActionParse(actions, None)


@dataclass(frozen=True, slots=True)
class AccountParse:
    account_object: dict[str, str | None] | None
    refusal: str | None

    @property
    def nonempty(self) -> bool:
        return (
            self.account_object is not None
            and type(self.account_object["account"]) is str
            and self.account_object["account"] != ""
        )


def parse_account(content: object) -> AccountParse:
    value, refusal = _decode_object(content)
    if refusal is not None:
        return AccountParse(None, refusal)
    if set(value) != {"account"}:
        return AccountParse(None, "invalid_account_object")
    account = value["account"]
    if account is not None and type(account) is not str:
        return AccountParse(None, "invalid_account_value")
    return AccountParse({"account": account}, None)


@dataclass(frozen=True, slots=True)
class CandidateParse:
    candidate: dict[str, str | None] | None
    account: str | None = None
    refusal: str | None = None


def parse_candidate(content: object, *, same_response: bool = False) -> CandidateParse:
    value, refusal = _decode_object(content)
    if refusal is not None:
        return CandidateParse(None, refusal=refusal)
    if same_response:
        if tuple(value) != ("account", "change", "counterevidence"):
            return CandidateParse(None, refusal="invalid_same_response_key_order")
        account = value["account"]
        if account is not None and type(account) is not str:
            return CandidateParse(None, refusal="invalid_same_response_account")
    else:
        if set(value) != {"change", "counterevidence"}:
            return CandidateParse(None, refusal="invalid_candidate_object")
        account = None
    candidate = {key: value[key] for key in ("change", "counterevidence")}
    if any(item is not None and type(item) is not str for item in candidate.values()):
        return CandidateParse(None, account=account, refusal="invalid_candidate_value")
    return CandidateParse(candidate, account=account)


def govern_candidate(
    parsed: CandidateParse, occurrence: dict[str, object], controls: tuple[str, str]
) -> dict[str, object]:
    reasons: list[str] = []
    if parsed.refusal is not None:
        reasons.append(parsed.refusal)
    if parsed.candidate is not None:
        for key in ("change", "counterevidence"):
            value = parsed.candidate[key]
            if type(value) is not str or value.strip() == "":
                reasons.append(f"{key}_not_nonempty_string")
            elif any(token in value for token in controls):
                reasons.append(f"{key}_copies_acquisition_control")
    return {
        "admitted": parsed.candidate is not None and not reasons,
        "refusals": reasons,
        "source_occurrence_sha256": hashlib.sha256(
            canonical_json_bytes(occurrence)
        ).hexdigest(),
    }


def actor_user_prompt(state: PhaseState, action_count: int) -> str:
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
            offer_envelope(None).decode("utf-8"),
            "",
            f"Return exactly {action_count} action entry or entries in one actions array.",
            "/no_think",
        )
    )


def actor_envelope(state: PhaseState, action_count: int) -> dict[str, object]:
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": ACTOR_SYSTEM},
            {"role": "user", "content": actor_user_prompt(state, action_count)},
        ],
        **ACTOR_SETTINGS,
    }


def account_envelope(occurrence: dict[str, object]) -> dict[str, object]:
    user = "\n".join(
        (
            "PRACTICE OCCURRENCE",
            canonical_json_bytes(occurrence).decode("utf-8"),
            "",
            "ACCOUNTING RESPONSIBILITY",
            ACCOUNT_RESPONSIBILITY,
            "/no_think",
        )
    )
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": ACCOUNT_SYSTEM},
            {"role": "user", "content": user},
        ],
        **AUTHOR_SETTINGS,
    }


def candidate_envelope(
    occurrence: dict[str, object], material: object, *, static_expanded: bool = False
) -> dict[str, object]:
    responsibility = AUTHORSHIP_RESPONSIBILITY
    if static_expanded:
        responsibility = f"{responsibility}\n{STATIC_EXPANSION}"
    user = "\n".join(
        (
            "SOURCE OCCURRENCE",
            canonical_json_bytes(occurrence).decode("utf-8"),
            "",
            "ADDITIONAL RUNTIME MATERIAL",
            canonical_json_bytes({"material": material}).decode("utf-8"),
            "",
            "AUTHORSHIP RESPONSIBILITY",
            responsibility,
            "/no_think",
        )
    )
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": CANDIDATE_SYSTEM},
            {"role": "user", "content": user},
        ],
        **AUTHOR_SETTINGS,
    }


def same_response_envelope(occurrence: dict[str, object]) -> dict[str, object]:
    user = "\n".join(
        (
            "PRACTICE OCCURRENCE",
            canonical_json_bytes(occurrence).decode("utf-8"),
            "",
            "ACCOUNTING RESPONSIBILITY",
            ACCOUNT_RESPONSIBILITY,
            "",
            "CANDIDATE AUTHORSHIP RESPONSIBILITY",
            AUTHORSHIP_RESPONSIBILITY,
            "/no_think",
        )
    )
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SAME_RESPONSE_SYSTEM},
            {"role": "user", "content": user},
        ],
        **AUTHOR_SETTINGS,
    }


def deterministic_restatement(occurrence: dict[str, object]) -> str:
    steps = occurrence.get("steps")
    if type(steps) is not list or not steps:
        raise ValueError("occurrence_steps_required")
    first = steps[0]
    before = first["before"]
    text = (
        f"Recorded family {before['controller_family']}; device {before['device']}; "
        f"initial controls [{before['controls'][0]}, {before['controls'][1]}]; "
        f"initial phase {before['phase']}; initial position {before['position']}; "
        f"target {before['target']}."
    )
    parts = [text]
    for index, step in enumerate(steps, 1):
        before = step["before"]
        consequence = step["consequence"]
        reached = "true" if consequence["target_reached"] else "false"
        parts.append(
            f"Step {index}: action {step['action']}; before phase {before['phase']}; "
            f"before position {before['position']}; movement "
            f"{consequence['movement_direction']}; after phase "
            f"{consequence['phase_after']}; after position "
            f"{consequence['position_after']}; target reached {reached}."
        )
    return " ".join(parts)


def _seeded_control_stream() -> str:
    digest = hashlib.sha256(CONTENT_CONTROL_SEED.encode("utf-8")).digest()
    return "".join(CONTENT_CONTROL_ALPHABET[value % len(CONTENT_CONTROL_ALPHABET)] for value in digest)


def content_control(account_object: dict[str, str | None]) -> dict[str, str]:
    account = account_object.get("account")
    if type(account) is not str or account == "":
        raise ValueError("nonempty_account_required")
    target = len(canonical_json_bytes(account_object))
    empty_size = len(canonical_json_bytes({"account": ""}))
    character_count = target - empty_size
    if character_count <= 0:
        raise ValueError("positive_content_control_unavailable")
    stream = _seeded_control_stream()
    value = (stream * math.ceil(character_count / len(stream)))[:character_count]
    result = {"account": value}
    if len(canonical_json_bytes(result)) != target:
        raise ValueError("content_control_length_mismatch")
    return result


def account_diagnostic(
    parsed: AccountParse, occurrence: dict[str, object], controls: tuple[str, str]
) -> dict[str, object]:
    if parsed.account_object is None:
        return {"class": "not_classified", "reason": parsed.refusal}
    account = parsed.account_object["account"]
    if account is None:
        return {"class": "not_classified", "reason": "account_null"}
    if account == "":
        return {"class": "not_classified", "reason": "account_empty"}
    normalized = unicodedata.normalize("NFKC", account).casefold()
    field_names: set[str] = set()

    def collect(value: object) -> None:
        if type(value) is dict:
            for key, item in value.items():
                field_names.add(key)
                collect(item)
        elif type(value) is list:
            for item in value:
                collect(item)

    collect(occurrence)
    return {
        "class": "indeterminate",
        "reason": "no_semantic_account_scorer",
        "copied_acquisition_controls": [token for token in controls if token in normalized],
        "copied_occurrence_field_names": [
            name for name in sorted(field_names) if name.casefold() in normalized
        ],
        "relation_already_present_remains_live": True,
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
    activated: bool | None = None
    commitment: bool = False
    material: object = None
    fork_point: str | None = None
    account_receipt: str | None = None
    account_is_request_parent: bool = False
    same_response: bool = False
    formation_condition: str | None = None

    @property
    def request_body(self) -> bytes:
        return canonical_json_bytes(self.envelope)


Invoker = Callable[[LogicalCall, int], ProviderAttempt]


def _condition_envelope(
    condition: str,
    occurrence: dict[str, object],
    account_object: dict[str, str | None] | None,
    control_object: dict[str, str] | None,
) -> tuple[dict[str, object], object, bool]:
    if condition in ("direct", "withheld"):
        return candidate_envelope(occurrence, None), None, False
    if condition == "delivered":
        if account_object is None:
            raise ValueError("account_unavailable")
        return candidate_envelope(occurrence, account_object), account_object, False
    if condition == "occurrence_repeated":
        return candidate_envelope(occurrence, occurrence), occurrence, False
    if condition == "static_expanded":
        return candidate_envelope(occurrence, None, static_expanded=True), None, False
    if condition == "same_response":
        return same_response_envelope(occurrence), None, True
    if condition == "restatement":
        material = deterministic_restatement(occurrence)
        return candidate_envelope(occurrence, material), material, False
    if condition == "content_control":
        if control_object is None:
            raise ValueError("content_control_unavailable")
        return candidate_envelope(occurrence, control_object), control_object, False
    raise ValueError("unknown_condition")


def candidate_schedule(world_data: dict[str, dict[str, object]]) -> tuple[LogicalCall, ...]:
    calls: list[LogicalCall] = []
    logical_index = 6
    for round_number in (1, 2):
        for world in WORLDS:
            data = world_data.get(world.world_id)
            for condition in ROUND_ORDERS[(round_number, world.world_id)]:
                current_index = logical_index
                logical_index += 1
                if data is None:
                    continue
                account_object = data.get("account_object")
                control_object = data.get("content_control")
                if condition == "delivered" and account_object is None:
                    continue
                if condition == "content_control" and control_object is None:
                    continue
                envelope, material, same_response = _condition_envelope(
                    condition,
                    data["occurrence"],
                    account_object,
                    control_object,
                )
                account_group = condition in ("withheld", "delivered", "content_control")
                calls.append(
                    LogicalCall(
                        current_index,
                        f"{world.world_id}-{condition}-r{round_number}",
                        "candidate",
                        envelope,
                        world_id=world.world_id,
                        offer_key=condition,
                        repetition=round_number,
                        material=material,
                        fork_point="post-account" if account_group else "occurrence-root",
                        account_receipt=(
                            f"{world.world_id}-account" if account_group else None
                        ),
                        account_is_request_parent=condition in ("delivered", "content_control"),
                        same_response=same_response,
                        formation_condition=PUBLIC_FORMATION_CONDITIONS[condition],
                    )
                )
    if logical_index != PLANNED_LOGICAL_CALLS + 1:
        raise ValueError("schedule_slot_drift")
    return tuple(calls)


def _prompt_tokens(attempt: ProviderAttempt) -> int | None:
    envelope = attempt.response_envelope
    usage = envelope.get("usage") if type(envelope) is dict else None
    value = usage.get("prompt_tokens") if type(usage) is dict else None
    return value if type(value) is int else None


def _completion_tokens(attempt: ProviderAttempt) -> int | None:
    envelope = attempt.response_envelope
    usage = envelope.get("usage") if type(envelope) is dict else None
    value = usage.get("completion_tokens") if type(usage) is dict else None
    return value if type(value) is int else None


class ContactRunner(BaseRunner):
    def __init__(self, invoker: Invoker, writer: EvidenceWriter, physical_ceiling: int) -> None:
        super().__init__(invoker, writer, physical_ceiling)
        self.accounts: dict[str, dict[str, object]] = {}
        self.world_data: dict[str, dict[str, object]] = {}

    def record_actor(self, call: LogicalCall, attempt: ProviderAttempt) -> dict[str, object]:
        if call.state is None:
            raise ContactStop("actor_state_missing")
        parsed = parse_actions(attempt.content, call.state, call.commitment)
        record = {
            "logical_index": call.logical_index,
            "call_id": call.call_id,
            "responsibility": "actor",
            "world_id": call.world_id,
            "state": public_state(call.state),
            "content": attempt.content,
            "message": attempt.message,
            "surfaced_actions": parsed.actions,
            "action_refusal": parsed.refusal,
            "prompt_tokens": _prompt_tokens(attempt),
            "completion_tokens": _completion_tokens(attempt),
            "request_sha256": hashlib.sha256(call.request_body).hexdigest(),
            "actor_material_bytes": offer_envelope(None).decode("utf-8"),
        }
        self.logical_records.append(record)
        self.writer.write_logical(call, record)
        return record

    def record_account(
        self,
        call: LogicalCall,
        attempt: ProviderAttempt,
        occurrence: dict[str, object],
        controls: tuple[str, str],
    ) -> dict[str, object]:
        parsed = parse_account(attempt.content)
        diagnostic = account_diagnostic(parsed, occurrence, controls)
        account_object = parsed.account_object if parsed.nonempty else None
        record = {
            "logical_index": call.logical_index,
            "call_id": call.call_id,
            "responsibility": "account",
            "world_id": call.world_id,
            "content": attempt.content,
            "message": attempt.message,
            "account_object": parsed.account_object,
            "account_refusal": parsed.refusal,
            "account_nonempty": parsed.nonempty,
            "account_class": diagnostic,
            "prompt_tokens": _prompt_tokens(attempt),
            "completion_tokens": _completion_tokens(attempt),
            "request_sha256": hashlib.sha256(call.request_body).hexdigest(),
            "response_sha256": hashlib.sha256(attempt.response_body).hexdigest(),
            "source_occurrence_sha256": hashlib.sha256(
                canonical_json_bytes(occurrence)
            ).hexdigest(),
            "fork_point": "occurrence-root",
        }
        self.logical_records.append(record)
        self.writer.write_logical(call, record)
        self.accounts[call.world_id] = record
        if call.world_id in self.world_data:
            self.world_data[call.world_id]["account_object"] = account_object
            if account_object is not None:
                try:
                    self.world_data[call.world_id]["content_control"] = content_control(
                        account_object
                    )
                except ValueError as error:
                    self.world_data[call.world_id]["content_control_error"] = str(error)
        return record

    def record_candidate(
        self, call: LogicalCall, attempt: ProviderAttempt
    ) -> dict[str, object]:
        data = self.world_data[call.world_id]
        parsed = parse_candidate(attempt.content, same_response=call.same_response)
        comparison = (
            None
            if parsed.candidate is None
            else canonical_json_bytes(
                {
                    "change": parsed.candidate["change"],
                    "counterevidence": parsed.candidate["counterevidence"],
                }
            )
        )
        governance = govern_candidate(
            parsed, data["occurrence"], data["controls"]
        )
        record = {
            "logical_index": call.logical_index,
            "call_id": call.call_id,
            "responsibility": "candidate",
            "world_id": call.world_id,
            "condition": call.offer_key,
            "public_formation_condition": call.formation_condition,
            "round": call.repetition,
            "fork_point": call.fork_point,
            "account_receipt": call.account_receipt,
            "account_is_request_parent": call.account_is_request_parent,
            "content": attempt.content,
            "message": attempt.message,
            "same_response_account": parsed.account if call.same_response else None,
            "candidate": parsed.candidate,
            "candidate_refusal": parsed.refusal,
            "candidate_comparison_utf8": (
                None if comparison is None else comparison.decode("utf-8")
            ),
            "candidate_comparison_sha256": (
                None if comparison is None else hashlib.sha256(comparison).hexdigest()
            ),
            "governance": governance,
            "prompt_tokens": _prompt_tokens(attempt),
            "completion_tokens": _completion_tokens(attempt),
            "request_sha256": hashlib.sha256(call.request_body).hexdigest(),
            "material_utf8_length": len(
                canonical_json_bytes({"material": call.material})
            ),
        }
        self.logical_records.append(record)
        self.writer.write_logical(call, record)
        return record

    def _world_comparison(self, world: World) -> dict[str, object]:
        records = [
            item
            for item in self.logical_records
            if item.get("responsibility") == "candidate"
            and item.get("world_id") == world.world_id
        ]
        if world.world_id not in self.world_data:
            return {
                "world_id": world.world_id,
                "available": False,
                "reason": "acquisition_occurrence_unavailable",
                "account_delivery_conditioned_exact_candidate_difference": False,
            }
        conditions: dict[str, dict[str, object]] = {}
        for condition in CONDITIONS:
            members = [item for item in records if item["condition"] == condition]
            values = [item["candidate_comparison_utf8"] for item in members]
            available = len(members) == SAMPLES_PER_CONDITION and all(
                value is not None for value in values
            )
            stable = available and len(set(values)) == 1
            conditions[condition] = {
                "samples": values,
                "logical_indices": [item["logical_index"] for item in members],
                "request_sha256": [item["request_sha256"] for item in members],
                "available": available,
                "internally_stable": stable,
                "stable_value": values[0] if stable else None,
            }

        direct_hashes = set(conditions["direct"]["request_sha256"])
        withheld_hashes = set(conditions["withheld"]["request_sha256"])
        request_identical = (
            len(direct_hashes) == 1
            and direct_hashes == withheld_hashes
            and len(conditions["direct"]["request_sha256"]) == 2
            and len(conditions["withheld"]["request_sha256"]) == 2
        )
        delivered_records = {
            item["round"]: item for item in records if item["condition"] == "delivered"
        }
        control_records = {
            item["round"]: item
            for item in records
            if item["condition"] == "content_control"
        }
        token_deltas = []
        for round_number in (1, 2):
            delivered = delivered_records.get(round_number)
            control = control_records.get(round_number)
            if delivered is None or control is None:
                token_deltas.append(None)
                continue
            left = delivered["prompt_tokens"]
            right = control["prompt_tokens"]
            token_deltas.append(
                abs(left - right) if type(left) is int and type(right) is int else None
            )
        prompt_mass_available = all(
            type(delta) is int and delta <= TOKEN_DELTA_CEILING
            for delta in token_deltas
        )
        stable_values = {
            key: value["stable_value"] for key, value in conditions.items()
        }
        all_stable = all(value["internally_stable"] for value in conditions.values())
        withheld_matches_direct = (
            conditions["withheld"]["internally_stable"]
            and conditions["direct"]["internally_stable"]
            and stable_values["withheld"] == stable_values["direct"]
        )
        delivery_differs = (
            conditions["delivered"]["internally_stable"]
            and conditions["direct"]["internally_stable"]
            and stable_values["delivered"] != stable_values["direct"]
        )
        carryover_invalid = (
            conditions["withheld"]["internally_stable"]
            and conditions["delivered"]["internally_stable"]
            and conditions["direct"]["internally_stable"]
            and stable_values["withheld"] == stable_values["delivered"]
            and stable_values["delivered"] != stable_values["direct"]
        )
        collapse_map = {
            "static_expanded": "instruction-equivalent",
            "same_response": "generated-intermediate-equivalent",
            "occurrence_repeated": "repetition-equivalent",
            "restatement": "restatement-equivalent",
            "content_control": "prompt-mass-equivalent",
        }
        collapses = [
            label
            for condition, label in collapse_map.items()
            if conditions[condition]["internally_stable"]
            and conditions["delivered"]["internally_stable"]
            and stable_values[condition] == stable_values["delivered"]
            and (condition != "content_control" or prompt_mass_available)
        ]
        label_available = (
            all_stable
            and prompt_mass_available
            and request_identical
            and withheld_matches_direct
            and delivery_differs
            and not carryover_invalid
            and not collapses
        )
        unavailable = [
            condition for condition, value in conditions.items() if not value["available"]
        ]
        unstable = [
            condition
            for condition, value in conditions.items()
            if value["available"] and not value["internally_stable"]
        ]
        return {
            "world_id": world.world_id,
            "weak_label_available": label_available,
            "all_required_conditions_available_and_stable": (
                all_stable and prompt_mass_available
            ),
            "conditions": conditions,
            "direct_withheld_request_bytes_identical": request_identical,
            "withheld_matches_direct": withheld_matches_direct,
            "delivered_differs_from_direct": delivery_differs,
            "carryover_pattern_delivery_contrast_invalid": carryover_invalid,
            "prompt_token_deltas": token_deltas,
            "prompt_mass_comparison_available": prompt_mass_available,
            "unavailable_conditions": unavailable,
            "unstable_conditions": unstable,
            "collapse_labels": collapses,
            "account_delivery_conditioned_exact_candidate_difference": label_available,
            "claim_language": (
                "account-delivery-conditioned exact candidate difference"
                if label_available
                else "comparison unavailable or no stable exact difference"
            ),
            "relation_already_present_remains_live": True,
            "formation_verdict": None,
            "validation_verdict": None,
        }

    def summary(self, state: str, stop_reason: str | None) -> dict[str, object]:
        attempts = self.logical_records
        prompt_values = [item.get("prompt_tokens") for item in attempts]
        completion_values = [item.get("completion_tokens") for item in attempts]
        interface = next(
            (item for item in attempts if item.get("call_id") == "interface-disposable"),
            None,
        )
        acquisitions = [
            item
            for item in attempts
            if item.get("responsibility") == "actor"
            and str(item.get("call_id", "")).endswith("-acquisition")
        ]
        return {
            "protocol": PROTOCOL_VERSION,
            "evidence_class": "exploratory_authorship_observation_only",
            "contact_state": state,
            "stop_reason": stop_reason,
            "model": MODEL,
            "model_digest": MODEL_DIGEST,
            "planned_logical_calls": PLANNED_LOGICAL_CALLS,
            "completed_logical_calls": len(self.logical_records),
            "physical_call_ceiling": self.physical_ceiling,
            "physical_attempts": self.physical_attempts,
            "usage": {
                "prompt_tokens": sum(value for value in prompt_values if type(value) is int),
                "completion_tokens": sum(
                    value for value in completion_values if type(value) is int
                ),
            },
            "interface_observability": (
                None
                if interface is None
                else {
                    "observable": interface["surfaced_actions"] is not None,
                    "surfaced_actions": interface["surfaced_actions"],
                    "action_refusal": interface["action_refusal"],
                }
            ),
            "acquisitions": [
                {
                    "world_id": item["world_id"],
                    "observable": item["surfaced_actions"] is not None,
                    "surfaced_actions": item["surfaced_actions"],
                    "action_refusal": item["action_refusal"],
                }
                for item in acquisitions
            ],
            "accounts": self.accounts,
            "world_comparisons": [self._world_comparison(world) for world in WORLDS],
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
        "author_settings": AUTHOR_SETTINGS,
        "conditions": CONDITIONS,
        "public_formation_conditions": PUBLIC_FORMATION_CONDITIONS,
        "round_orders": {
            f"round-{round_number}-{world_id}": order
            for (round_number, world_id), order in ROUND_ORDERS.items()
        },
        "worlds": [
            {
                "world_id": world.world_id,
                "state": public_state(world.state),
                "profile": asdict(world.profile),
            }
            for world in WORLDS
        ],
        "interface_state": public_state(INTERFACE_STATE),
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "samples_per_condition": SAMPLES_PER_CONDITION,
        "token_delta_ceiling": TOKEN_DELTA_CEILING,
        "content_control_seed": CONTENT_CONTROL_SEED,
        "content_control_alphabet": CONTENT_CONTROL_ALPHABET,
        "content_control_derivation": (
            "sha256(seed) bytes mapped modulo alphabet, repeated then truncated to the "
            "ASCII character count required for exact canonical object byte length"
        ),
        "account_semantic_classes_emitted": ("indeterminate", "not_classified"),
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
        interface_call = LogicalCall(
            1,
            "interface-disposable",
            "actor",
            actor_envelope(INTERFACE_STATE, 1),
            state=INTERFACE_STATE,
            profile=INTERFACE_PROFILE,
        )
        interface = runner.record_actor(interface_call, runner.invoke(interface_call))
        if interface["surfaced_actions"] is None:
            raise ContactStop("interface_action_unobservable")

        for index, world in enumerate(WORLDS, 2):
            call = LogicalCall(
                index,
                f"{world.world_id}-acquisition",
                "actor",
                actor_envelope(world.state, 2),
                state=world.state,
                profile=world.profile,
                world_id=world.world_id,
                commitment=True,
            )
            record = runner.record_actor(call, runner.invoke(call))
            actions = record["surfaced_actions"]
            if actions is None:
                continue
            occurrence = acquisition_occurrence(world.state, world.profile, actions)
            runner.world_data[world.world_id] = {
                "occurrence": occurrence,
                "controls": world.state.controls,
                "account_object": None,
                "content_control": None,
            }
            writer.write_json(f"{world.world_id}-occurrence.json", occurrence)

        for index, world in enumerate(WORLDS, 4):
            if world.world_id not in runner.world_data:
                continue
            occurrence = runner.world_data[world.world_id]["occurrence"]
            call = LogicalCall(
                index,
                f"{world.world_id}-account",
                "account",
                account_envelope(occurrence),
                world_id=world.world_id,
                fork_point="occurrence-root",
            )
            runner.record_account(
                call,
                runner.invoke(call),
                occurrence,
                world.state.controls,
            )

        schedule = candidate_schedule(runner.world_data)
        for call in schedule:
            runner.record_candidate(call, runner.invoke(call))
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
