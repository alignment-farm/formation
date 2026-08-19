"""Run the reviewed exact-draft challenge authorship-only contact."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone
import time
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from contact.calibration_mechanism_discovery import (
    ContactRunner as BaseRunner,
    ContactStop,
    EvidenceWriter,
)
from contact.exploratory_developmental_contact import (
    ENDPOINT,
    INSPECT_TAG,
    InvocationFailure,
    MODEL,
    MODEL_DIGEST,
    ProviderAttempt,
)
from contact.occurrence_accounting_exploratory_contact import (
    ACTOR_SETTINGS,
    ACTOR_SYSTEM,
    CandidateParse,
    _completion_tokens,
    _decode_object,
    _prompt_tokens,
    actor_envelope,
    deterministic_restatement,
    govern_candidate,
    parse_actions,
)
from contact.phase_coupled_exploratory_contact import PUBLIC_RULE, public_state
from micro_environment.phase_coupled_control import PhaseProfile, PhaseState
from micro_environment.phase_coupled_specimen import (
    acquisition_occurrence,
    canonical_json_bytes,
    make_profile,
    make_state,
    offer_envelope,
)


PROTOCOL_VERSION = "draft-challenge-exploratory-contact-v0"
PLANNED_LOGICAL_CALLS = 39
PHYSICAL_CALL_CEILING = 42
SAMPLES_PER_CONDITION = 2
SINGLE_CALL_BUDGET = 256
SAME_RESPONSE_BUDGET = 512
MAX_COMPLETION_ALLOWANCE = 10_624

DMR_VERSION = "v1.2.6"
DOCKER_DESKTOP_PLATFORM = "Docker Desktop 4.87.0 (236836)"
LLAMA_BACKEND_BUILD = "b9879-metal"
LLAMA_BACKEND_DIGEST = (
    "sha256:b70706f473b4043ca3e0c32704a7fda3412b83bceef0564684187b8011230de8"
)

TOKENIZER_REVISION = "7d3da9c56f02b22d31dc1ca97c7ee628d1e2e237"
TOKENIZER_UTF8_LENGTH = 11_422_654
TOKENIZER_SHA256 = "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
TOKENIZER_IMPLEMENTATION = "tokenizers-0.23.1"
TEMPLATE_RENDERER_IMPLEMENTATION = "jinja2-3.1.6"
CHAT_TEMPLATE_UTF8_LENGTH = 4_100
CHAT_TEMPLATE_SHA256 = "57f1fd00f0013a2be96aa79b857391f27e23df5b5f847072b524c897e24d0361"
MASS_CONTROL_SEED = "formation.draft-challenge.prompt-mass.v1"
MASS_CONTROL_ALPHABET = "GHIJKLMNOPQRSTUVWXYZ"
MASS_CONTROL_MAX_PREFIX = 8_192

AUTHOR_SETTINGS: dict[str, object] = {
    "max_tokens": SINGLE_CALL_BUDGET,
    "temperature": 0.6,
    "top_p": 0.95,
    "stream": False,
    "response_format": {"type": "json_object"},
}
SAME_RESPONSE_SETTINGS: dict[str, object] = {
    **AUTHOR_SETTINGS,
    "max_tokens": SAME_RESPONSE_BUDGET,
}

AUTHORSHIP_RESPONSIBILITY = """State one reusable change in preparedness that the experience warrants,
including where it applies and what later observation should count against it."""

CHALLENGE_RESPONSIBILITY = """Review the exact prior model output supplied as `draft_content` using only the
public rule and source occurrence. Return the candidate you can support now.
Keep only claims supported by those sources, state where they apply, and state
what later observation would count against them. Use null for both fields if
you withdraw the prior attempt or cannot support a candidate."""

STATIC_RESPONSIBILITY = """Review using only the public rule and source occurrence. Return the candidate
you can support now. Keep only claims supported by those sources, state where
they apply, and state what later observation would count against them. Use null
for both fields if you cannot support a candidate."""

CANDIDATE_SYSTEM = f"""You are the candidate author inside a formation runtime. You have no memory
outside this request.

PUBLIC OPERATING RULE
{PUBLIC_RULE}

Return exactly one JSON object with only "change" and "counterevidence". Each
value may be a string or null. Do not add keys or commentary."""

SAME_RESPONSE_SYSTEM = f"""You are the candidate drafting and review component of a cold practitioner. You
have no memory outside this request.

PUBLIC OPERATING RULE
{PUBLIC_RULE}

Return exactly one JSON object whose keys, in order, are "draft" and "final".
Each value must be an object with only "change" and "counterevidence". Each
field value may be a string or null. Do not add keys or commentary."""

CONDITIONS = (
    "direct_candidate",
    "draft_withheld",
    "exact_draft_replay",
    "static_challenge_withheld_draft",
    "exact_draft_challenge",
    "same_response_draft_challenge",
    "occurrence_repeated",
    "deterministic_restatement",
    "draft_prompt_mass_control",
)

DOWNSTREAM_ALIASES = {
    "withheld": "draft_withheld",
    "replay": "exact_draft_replay",
    "static": "static_challenge_withheld_draft",
    "challenge": "exact_draft_challenge",
    "same response": "same_response_draft_challenge",
    "repeated": "occurrence_repeated",
    "restatement": "deterministic_restatement",
    "mass": "draft_prompt_mass_control",
}

ROUND_ORDERS: dict[tuple[int, str], tuple[str, ...]] = {
    (1, "world-g"): (
        "withheld", "replay", "static", "challenge", "same response",
        "repeated", "restatement", "mass",
    ),
    (1, "world-h"): (
        "mass", "restatement", "repeated", "same response", "challenge",
        "static", "replay", "withheld",
    ),
    (2, "world-g"): (
        "challenge", "same response", "repeated", "restatement", "mass",
        "withheld", "replay", "static",
    ),
    (2, "world-h"): (
        "static", "replay", "withheld", "mass", "restatement", "repeated",
        "same response", "challenge",
    ),
}


@dataclass(frozen=True, slots=True)
class World:
    world_id: str
    state: PhaseState
    profile: PhaseProfile


WORLD_G_PROFILE = make_profile(8, 0)
WORLD_H_PROFILE = make_profile(9, 1)
INTERFACE_PROFILE = make_profile(10, 0)
WORLD_G = World("world-g", make_state(WORLD_G_PROFILE, 23, 0, 0, 2), WORLD_G_PROFILE)
WORLD_H = World("world-h", make_state(WORLD_H_PROFILE, 24, 0, 0, 2), WORLD_H_PROFILE)
WORLDS = (WORLD_G, WORLD_H)
INTERFACE_STATE = make_state(INTERFACE_PROFILE, 25, 0, 3, 3)

DIRECT_IDENTIFIERS = {
    "world-g": ("candidate-g-direct-1", "candidate-g-direct-2"),
    "world-h": ("candidate-h-direct-1", "candidate-h-direct-2"),
}


def candidate_user_prompt(
    occurrence: dict[str, object],
    material: object,
    responsibility: str = "base",
) -> str:
    if responsibility == "base":
        header = "AUTHORSHIP RESPONSIBILITY"
        text = AUTHORSHIP_RESPONSIBILITY
    elif responsibility == "static":
        header = "STATIC REVIEW RESPONSIBILITY"
        text = STATIC_RESPONSIBILITY
    elif responsibility == "challenge":
        header = "CHALLENGE RESPONSIBILITY"
        text = CHALLENGE_RESPONSIBILITY
    else:
        raise ValueError("unknown_responsibility")
    return "\n".join(
        (
            "SOURCE OCCURRENCE",
            canonical_json_bytes(occurrence).decode("utf-8"),
            "",
            "ADDITIONAL RUNTIME MATERIAL",
            canonical_json_bytes({"material": material}).decode("utf-8"),
            "",
            header,
            text,
            "/no_think",
        )
    )


def candidate_envelope(
    occurrence: dict[str, object],
    material: object,
    responsibility: str = "base",
) -> dict[str, object]:
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": CANDIDATE_SYSTEM},
            {
                "role": "user",
                "content": candidate_user_prompt(occurrence, material, responsibility),
            },
        ],
        **AUTHOR_SETTINGS,
    }


def same_response_envelope(occurrence: dict[str, object]) -> dict[str, object]:
    user = "\n".join(
        (
            "SOURCE OCCURRENCE",
            canonical_json_bytes(occurrence).decode("utf-8"),
            "",
            "FIRST DRAFT RESPONSIBILITY",
            AUTHORSHIP_RESPONSIBILITY,
            "",
            "REVIEW RESPONSIBILITY",
            "Review the draft you just wrote using only the public rule and source",
            "occurrence. Return the candidate you can support now. Keep only claims supported",
            "by those sources, state where they apply, and state what later observation would",
            "count against them. Use null for both fields if you withdraw the draft or cannot",
            "support a candidate.",
            "/no_think",
        )
    )
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SAME_RESPONSE_SYSTEM},
            {"role": "user", "content": user},
        ],
        **SAME_RESPONSE_SETTINGS,
    }


def _valid_candidate(value: object) -> dict[str, str | None] | None:
    if type(value) is not dict or set(value) != {"change", "counterevidence"}:
        return None
    candidate = {key: value[key] for key in ("change", "counterevidence")}
    if any(item is not None and type(item) is not str for item in candidate.values()):
        return None
    return candidate


def parse_candidate(content: object, *, same_response: bool = False) -> CandidateParse:
    value, refusal = _decode_object(content)
    if refusal is not None:
        return CandidateParse(None, refusal=refusal)
    if same_response:
        if tuple(value) != ("draft", "final"):
            return CandidateParse(None, refusal="invalid_same_response_key_order")
        draft = _valid_candidate(value["draft"])
        final = _valid_candidate(value["final"])
        if draft is None or final is None:
            return CandidateParse(None, refusal="invalid_same_response_objects")
        try:
            draft_bytes = canonical_json_bytes(draft)
        except (UnicodeEncodeError, ValueError):
            return CandidateParse(None, refusal="candidate_comparison_unencodable")
        return CandidateParse(final, account=draft_bytes.decode("utf-8"))
    candidate = _valid_candidate(value)
    if candidate is None:
        return CandidateParse(None, refusal="invalid_candidate_object")
    return CandidateParse(candidate)


def unicode_scalar_string(value: object) -> bool:
    return type(value) is str and all(
        not 0xD800 <= ord(character) <= 0xDFFF for character in value
    )


def draft_material(value: object) -> dict[str, str] | None:
    if not unicode_scalar_string(value):
        return None
    try:
        canonical_json_bytes({"material": {"draft_content": value}})
    except ValueError:
        return None
    return {"draft_content": value}


def render_chat(chat_template: str, system: str, user: str) -> str:
    """Apply the verified inspect template with the chartered bindings."""
    try:
        import jinja2
        from jinja2.sandbox import ImmutableSandboxedEnvironment
    except ImportError as error:
        raise ValueError("jinja2_package_unavailable") from error
    implementation = f"jinja2-{jinja2.__version__}"
    if implementation != TEMPLATE_RENDERER_IMPLEMENTATION:
        raise ValueError("template_renderer_implementation_mismatch")
    environment = ImmutableSandboxedEnvironment(
        trim_blocks=True,
        lstrip_blocks=True,
    )

    def raise_exception(message: str) -> None:
        raise ValueError(message)

    environment.globals["raise_exception"] = raise_exception
    template = environment.from_string(chat_template)
    return template.render(
        messages=(
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ),
        add_generation_prompt=True,
        # `tools` and `enable_thinking` are intentionally omitted/undefined.
    )


TokenCounter = Callable[[str, str], int]


class DraftLiveInvoker:
    """HTTP transport that preserves missing or non-string content as evidence."""

    def __init__(self, endpoint: str = ENDPOINT, timeout_seconds: int = 300) -> None:
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds

    def __call__(self, call: LogicalCall, attempt_index: int) -> ProviderAttempt:
        request_body = call.request_body
        started = datetime.now(timezone.utc)
        clock = time.monotonic()
        request = Request(
            self.endpoint,
            data=request_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                response_body = response.read()
                http_status = response.status
        except HTTPError as error:
            response_body = error.read()
            attempt = ProviderAttempt(
                call.logical_index, attempt_index, call.call_id, request_body,
                response_body,
                {"http_status": error.code, "body": response_body.decode(errors="replace")},
                None, None, error.code, started.isoformat(),
                datetime.now(timezone.utc).isoformat(), time.monotonic() - clock,
                f"http_{error.code}",
            )
            raise InvocationFailure(f"http_{error.code}", attempt, False) from error
        except (URLError, TimeoutError, OSError) as error:
            attempt = ProviderAttempt(
                call.logical_index, attempt_index, call.call_id, request_body, b"",
                {"transport_error": repr(error)}, None, None, None,
                started.isoformat(), datetime.now(timezone.utc).isoformat(),
                time.monotonic() - clock, "transport_failure",
            )
            raise InvocationFailure("transport_failure", attempt, True) from error

        ended = datetime.now(timezone.utc)
        elapsed = time.monotonic() - clock
        try:
            envelope = json.loads(response_body)
            if type(envelope) is not dict:
                raise ValueError("response_object_required")
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as error:
            attempt = ProviderAttempt(
                call.logical_index, attempt_index, call.call_id, request_body,
                response_body, {"provider_envelope_error": str(error)}, None, None,
                http_status, started.isoformat(), ended.isoformat(), elapsed,
                "provider_envelope_invalid",
            )
            raise InvocationFailure("provider_envelope_invalid", attempt, False) from error

        message = None
        content = None
        choices = envelope.get("choices")
        if type(choices) is list and len(choices) == 1 and type(choices[0]) is dict:
            possible = choices[0].get("message")
            if type(possible) is dict:
                message = possible
                content = possible.get("content")
        return ProviderAttempt(
            call.logical_index, attempt_index, call.call_id, request_body,
            response_body, envelope, message, content, http_status,
            started.isoformat(), ended.isoformat(), elapsed,
        )


class PinnedTokenCounter:
    def __init__(self, path: Path, chat_template: str) -> None:
        body = path.read_bytes()
        if len(body) != TOKENIZER_UTF8_LENGTH:
            raise ValueError("tokenizer_length_mismatch")
        if hashlib.sha256(body).hexdigest() != TOKENIZER_SHA256:
            raise ValueError("tokenizer_hash_mismatch")
        try:
            from tokenizers import Tokenizer
            import tokenizers
        except ImportError as error:
            raise ValueError("tokenizers_package_unavailable") from error
        self.implementation = f"tokenizers-{tokenizers.__version__}"
        if self.implementation != TOKENIZER_IMPLEMENTATION:
            raise ValueError("tokenizer_implementation_mismatch")
        template_bytes = chat_template.encode("utf-8")
        if len(template_bytes) != CHAT_TEMPLATE_UTF8_LENGTH:
            raise ValueError("chat_template_length_mismatch")
        if hashlib.sha256(template_bytes).hexdigest() != CHAT_TEMPLATE_SHA256:
            raise ValueError("chat_template_hash_mismatch")
        self.renderer_implementation = TEMPLATE_RENDERER_IMPLEMENTATION
        self.chat_template = chat_template
        self.tokenizer = Tokenizer.from_file(str(path))

    def __call__(self, system: str, user: str) -> int:
        return len(
            self.tokenizer.encode(
                render_chat(self.chat_template, system, user),
                add_special_tokens=False,
            ).ids
        )


def _control_characters():
    counter = 0
    while True:
        digest = hashlib.sha256(
            canonical_json_bytes([MASS_CONTROL_SEED, counter])
        ).digest()
        for value in digest:
            yield MASS_CONTROL_ALPHABET[value % len(MASS_CONTROL_ALPHABET)]
        counter += 1


@dataclass(frozen=True, slots=True)
class MassControl:
    value: str
    target_prompt_tokens: int
    control_prompt_tokens: int
    prefix_length: int
    request_sha256: str


def construct_mass_control(
    target_prompt_tokens: int,
    occurrence: dict[str, object],
    token_counter: TokenCounter,
) -> MassControl | None:
    stream = _control_characters()
    prefix = ""
    for length in range(MASS_CONTROL_MAX_PREFIX + 1):
        user = candidate_user_prompt(
            occurrence,
            {"draft_content": prefix},
            "challenge",
        )
        count = token_counter(CANDIDATE_SYSTEM, user)
        if count == target_prompt_tokens:
            envelope = candidate_envelope(
                occurrence, {"draft_content": prefix}, "challenge"
            )
            return MassControl(
                prefix,
                target_prompt_tokens,
                count,
                length,
                hashlib.sha256(canonical_json_bytes(envelope)).hexdigest(),
            )
        if length < MASS_CONTROL_MAX_PREFIX:
            prefix += next(stream)
    return None


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
    draft_receipt: str | None = None
    draft_is_request_parent: bool = False
    same_response: bool = False
    formation_condition: str | None = None

    @property
    def request_body(self) -> bytes:
        return canonical_json_bytes(self.envelope)


Invoker = Callable[[LogicalCall, int], ProviderAttempt]


def direct_calls(world_data: dict[str, dict[str, object]]) -> tuple[LogicalCall, ...]:
    slots = (
        (4, WORLD_G, 1),
        (5, WORLD_H, 1),
        (6, WORLD_G, 2),
        (7, WORLD_H, 2),
    )
    calls = []
    for index, world, sample in slots:
        data = world_data.get(world.world_id)
        if data is None:
            continue
        call_id = DIRECT_IDENTIFIERS[world.world_id][sample - 1]
        calls.append(
            LogicalCall(
                index,
                call_id,
                "candidate",
                candidate_envelope(data["occurrence"], None),
                world_id=world.world_id,
                offer_key="direct_candidate",
                repetition=sample,
                material=None,
                fork_point="occurrence-root",
                formation_condition="direct_candidate",
            )
        )
    return tuple(calls)


def _condition_envelope(
    condition: str,
    occurrence: dict[str, object],
    source_material: dict[str, str] | None,
    mass: MassControl | None,
) -> tuple[dict[str, object], object, bool]:
    if condition == "draft_withheld":
        return candidate_envelope(occurrence, None), None, False
    if condition == "exact_draft_replay":
        if source_material is None:
            raise ValueError("source_material_unavailable")
        return candidate_envelope(occurrence, source_material), source_material, False
    if condition == "static_challenge_withheld_draft":
        return candidate_envelope(occurrence, None, "static"), None, False
    if condition == "exact_draft_challenge":
        if source_material is None:
            raise ValueError("source_material_unavailable")
        return (
            candidate_envelope(occurrence, source_material, "challenge"),
            source_material,
            False,
        )
    if condition == "same_response_draft_challenge":
        return same_response_envelope(occurrence), None, True
    if condition == "occurrence_repeated":
        return candidate_envelope(occurrence, occurrence), occurrence, False
    if condition == "deterministic_restatement":
        material = deterministic_restatement(occurrence)
        return candidate_envelope(occurrence, material), material, False
    if condition == "draft_prompt_mass_control":
        if mass is None:
            raise ValueError("mass_control_unavailable")
        material = {"draft_content": mass.value}
        return candidate_envelope(occurrence, material, "challenge"), material, False
    raise ValueError("unknown_condition")


def downstream_calls(world_data: dict[str, dict[str, object]]) -> tuple[LogicalCall, ...]:
    calls: list[LogicalCall] = []
    logical_index = 8
    for round_number in (1, 2):
        for world in WORLDS:
            data = world_data.get(world.world_id)
            for alias in ROUND_ORDERS[(round_number, world.world_id)]:
                current_index = logical_index
                logical_index += 1
                if data is None:
                    continue
                condition = DOWNSTREAM_ALIASES[alias]
                source_material = data.get("source_material")
                mass = data.get("mass_control")
                if condition in ("exact_draft_replay", "exact_draft_challenge") and source_material is None:
                    continue
                if condition == "draft_prompt_mass_control" and mass is None:
                    continue
                envelope, material, same_response = _condition_envelope(
                    condition, data["occurrence"], source_material, mass
                )
                draft_group = condition in (
                    "draft_withheld",
                    "exact_draft_replay",
                    "static_challenge_withheld_draft",
                    "exact_draft_challenge",
                    "draft_prompt_mass_control",
                )
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
                        fork_point="post-source" if draft_group else "occurrence-root",
                        draft_receipt=(
                            DIRECT_IDENTIFIERS[world.world_id][0]
                            if draft_group
                            else None
                        ),
                        draft_is_request_parent=condition in (
                            "exact_draft_replay", "exact_draft_challenge"
                        ),
                        same_response=same_response,
                        formation_condition=condition,
                    )
                )
    if logical_index != PLANNED_LOGICAL_CALLS + 1:
        raise ValueError("schedule_slot_drift")
    return tuple(calls)


class ContactRunner(BaseRunner):
    def __init__(self, invoker: Invoker, writer: EvidenceWriter, physical_ceiling: int) -> None:
        super().__init__(invoker, writer, physical_ceiling)
        self.world_data: dict[str, dict[str, object]] = {}
        self.parsed_candidates: dict[str, CandidateParse] = {}
        self.calls_by_id: dict[str, LogicalCall] = {}

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
            "response_sha256": hashlib.sha256(attempt.response_body).hexdigest(),
            "actor_material_bytes": offer_envelope(None).decode("utf-8"),
        }
        self.logical_records.append(record)
        self.calls_by_id[call.call_id] = call
        self.writer.write_logical(call, record)
        return record

    def record_candidate(self, call: LogicalCall, attempt: ProviderAttempt) -> dict[str, object]:
        parsed = parse_candidate(attempt.content, same_response=call.same_response)
        comparison = None
        comparison_refusal = None
        if parsed.candidate is not None:
            try:
                comparison = canonical_json_bytes(
                    {
                        "change": parsed.candidate["change"],
                        "counterevidence": parsed.candidate["counterevidence"],
                    }
                )
            except (UnicodeEncodeError, ValueError):
                comparison_refusal = "candidate_comparison_unencodable"
        record = {
            "logical_index": call.logical_index,
            "call_id": call.call_id,
            "responsibility": "candidate",
            "world_id": call.world_id,
            "condition": call.offer_key,
            "public_formation_condition": call.formation_condition,
            "round": call.repetition,
            "fork_point": call.fork_point,
            "draft_receipt": call.draft_receipt,
            "draft_is_request_parent": call.draft_is_request_parent,
            "content": attempt.content,
            "message": attempt.message,
            "same_response_draft_canonical": (
                parsed.account if call.same_response else None
            ),
            "candidate": parsed.candidate,
            "candidate_refusal": parsed.refusal,
            "candidate_comparison_refusal": comparison_refusal,
            "candidate_comparison_utf8": (
                None if comparison is None else comparison.decode("utf-8")
            ),
            "candidate_comparison_sha256": (
                None if comparison is None else hashlib.sha256(comparison).hexdigest()
            ),
            "governance": None,
            "governance_deferred": True,
            "prompt_tokens": _prompt_tokens(attempt),
            "completion_tokens": _completion_tokens(attempt),
            "request_sha256": hashlib.sha256(call.request_body).hexdigest(),
            "response_sha256": hashlib.sha256(attempt.response_body).hexdigest(),
            "material_utf8_length": len(canonical_json_bytes({"material": call.material})),
        }
        self.logical_records.append(record)
        self.parsed_candidates[call.call_id] = parsed
        self.calls_by_id[call.call_id] = call
        self.writer.write_logical(call, record)
        return record

    def apply_governance(self) -> None:
        for record in self.logical_records:
            if record.get("responsibility") != "candidate":
                continue
            call_id = str(record["call_id"])
            parsed = self.parsed_candidates[call_id]
            data = self.world_data[str(record["world_id"])]
            record["governance"] = govern_candidate(
                parsed, data["occurrence"], data["controls"]
            )
            record["governance_deferred"] = False
            self.writer.write_logical(self.calls_by_id[call_id], record)

    def _condition_summary(self, world_id: str) -> dict[str, dict[str, object]]:
        records = [
            item
            for item in self.logical_records
            if item.get("responsibility") == "candidate"
            and item.get("world_id") == world_id
        ]
        result = {}
        for condition in CONDITIONS:
            members = [item for item in records if item["condition"] == condition]
            values = [item["candidate_comparison_utf8"] for item in members]
            available = len(members) == SAMPLES_PER_CONDITION and all(
                value is not None for value in values
            )
            stable = available and len(set(values)) == 1
            result[condition] = {
                "samples": values,
                "raw_content": [item["content"] for item in members],
                "logical_indices": [item["logical_index"] for item in members],
                "request_sha256": [item["request_sha256"] for item in members],
                "prompt_tokens": [item["prompt_tokens"] for item in members],
                "available": available,
                "internally_stable": stable,
                "stable_value": values[0] if stable else None,
            }
        return result

    def _world_comparison(self, world: World) -> dict[str, object]:
        data = self.world_data.get(world.world_id)
        if data is None:
            return {
                "world_id": world.world_id,
                "available": False,
                "reason": "acquisition_occurrence_unavailable",
                "mechanism_label": None,
                "formation_verdict": None,
                "validation_verdict": None,
            }
        conditions = self._condition_summary(world.world_id)
        direct = conditions["direct_candidate"]
        withheld = conditions["draft_withheld"]
        challenge = conditions["exact_draft_challenge"]
        source_comparison = data.get("source_candidate_comparison_utf8")
        source_string = data.get("source_content")

        request_identity = (
            len(direct["request_sha256"]) == SAMPLES_PER_CONDITION
            and len(withheld["request_sha256"]) == SAMPLES_PER_CONDITION
            and len(set(direct["request_sha256"] + withheld["request_sha256"])) == 1
        )
        audit_stable = direct["internally_stable"] and withheld["internally_stable"]
        audit_matches = audit_stable and direct["stable_value"] == withheld["stable_value"]
        audit_invalid = not request_identity
        audit_unstable = request_identity and not audit_stable
        audit_failed = request_identity and audit_stable and not audit_matches
        carryover_invalid = (
            request_identity
            and audit_stable
            and challenge["internally_stable"]
            and withheld["stable_value"] == challenge["stable_value"]
            and challenge["stable_value"] != direct["stable_value"]
        )
        audit_pass = request_identity and audit_matches and not carryover_invalid

        challenge_anchor = challenge["internally_stable"]
        source_member = (
            source_comparison is not None
            and direct["internally_stable"]
            and source_comparison == direct["stable_value"]
        )
        challenge_source_match = (
            challenge_anchor
            and source_comparison is not None
            and challenge["stable_value"] == source_comparison
        )
        raw_matches = [
            value == source_string
            for value in challenge["raw_content"]
            if type(value) is str and type(source_string) is str
        ]

        mass_meta = data.get("mass_control_record")
        local_parity = bool(
            type(mass_meta) is dict
            and mass_meta.get("target_prompt_tokens")
            == mass_meta.get("control_prompt_tokens")
        )
        challenge_tokens = challenge["prompt_tokens"]
        mass_tokens = conditions["draft_prompt_mass_control"]["prompt_tokens"]
        provider_parity = (
            len(challenge_tokens) == SAMPLES_PER_CONDITION
            and len(mass_tokens) == SAMPLES_PER_CONDITION
            and all(type(value) is int for value in challenge_tokens + mass_tokens)
            and len(set(challenge_tokens + mass_tokens)) == 1
        )
        prompt_mass_available = local_parity and provider_parity

        collapse_map = {
            "exact_draft_replay": "draft-priming-equivalent",
            "static_challenge_withheld_draft": "static-review-equivalent",
            "same_response_draft_challenge": "generated-intermediate-equivalent",
            "occurrence_repeated": "repetition-equivalent",
            "deterministic_restatement": "restatement-equivalent",
            "draft_prompt_mass_control": "prompt-mass-equivalent",
        }
        collapses = []
        if audit_pass and challenge_anchor and not challenge_source_match:
            for condition, label in collapse_map.items():
                current = conditions[condition]
                if (
                    current["internally_stable"]
                    and current["stable_value"] == challenge["stable_value"]
                    and (condition != "draft_prompt_mass_control" or prompt_mass_available)
                ):
                    collapses.append(label)

        all_stable = all(value["internally_stable"] for value in conditions.values())
        complete_gate = (
            audit_pass
            and challenge_anchor
            and source_member
            and all_stable
            and prompt_mass_available
            and not challenge_source_match
            and not collapses
        )
        double_null = canonical_json_bytes(
            {"change": None, "counterevidence": None}
        ).decode("utf-8")
        mechanism_label = None
        if complete_gate:
            mechanism_label = (
                "draft-challenge-associated exact candidate withdrawal"
                if challenge["stable_value"] == double_null
                else "draft-challenge-associated exact candidate revision"
            )

        unavailable = [key for key, value in conditions.items() if not value["available"]]
        unstable = [
            key
            for key, value in conditions.items()
            if value["available"] and not value["internally_stable"]
        ]
        return {
            "world_id": world.world_id,
            "conditions": conditions,
            "source_draft_identifier": DIRECT_IDENTIFIERS[world.world_id][0],
            "source_content": source_string,
            "source_candidate_comparison_utf8": source_comparison,
            "source_candidate_member_of_stable_direct": source_member,
            "direct_withheld_request_bytes_identical": request_identity,
            "withheld_audit_invalid": audit_invalid,
            "withheld_audit_unstable": audit_unstable,
            "withheld_audit_failed": audit_failed,
            "withheld_matches_direct": audit_matches,
            "carryover_pattern_challenge_contrast_invalid": carryover_invalid,
            "challenge_anchor_available_and_stable": challenge_anchor,
            "exact_challenge_source_candidate_match": challenge_source_match,
            "exact_challenge_source_raw_output_matches": raw_matches,
            "local_prompt_token_parity": local_parity,
            "provider_prompt_token_parity": provider_parity,
            "prompt_mass_comparison_available": prompt_mass_available,
            "collapse_labels": collapses,
            "unavailable_conditions": unavailable,
            "unstable_conditions": unstable,
            "mechanism_label": mechanism_label,
            "claim_language": mechanism_label or "per-condition observation only",
            "formation_verdict": None,
            "validation_verdict": None,
        }

    def summary(self, state: str, stop_reason: str | None) -> dict[str, object]:
        prompt_values = [item.get("prompt_tokens") for item in self.logical_records]
        completion_values = [item.get("completion_tokens") for item in self.logical_records]
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
            "governance_applied_after_authorship": all(
                item.get("governance_deferred") is False
                for item in self.logical_records
                if item.get("responsibility") == "candidate"
            ),
            "world_comparisons": [self._world_comparison(world) for world in WORLDS],
            "formation_verdict": None,
            "validation_verdict": None,
        }


def freeze_mass_controls(
    runner: ContactRunner,
    token_counter: TokenCounter | None,
    writer: EvidenceWriter,
) -> None:
    for world in WORLDS:
        data = runner.world_data.get(world.world_id)
        if data is None:
            continue
        source = data.get("source_content")
        material = draft_material(source)
        data["source_material"] = material
        record: dict[str, object] = {
            "world_id": world.world_id,
            "source_draft_identifier": DIRECT_IDENTIFIERS[world.world_id][0],
            "source_content_sha256": (
                hashlib.sha256(source.encode("utf-8")).hexdigest()
                if unicode_scalar_string(source)
                else None
            ),
            "source_material_available": material is not None,
            "mass_control_available": False,
            "tokenizer_implementation": getattr(
                token_counter, "implementation", None
            ),
            "template_renderer_implementation": getattr(
                token_counter, "renderer_implementation", None
            ),
        }
        if material is not None and token_counter is not None:
            try:
                target_user = candidate_user_prompt(
                    data["occurrence"], material, "challenge"
                )
                target = token_counter(CANDIDATE_SYSTEM, target_user)
                control = construct_mass_control(
                    target, data["occurrence"], token_counter
                )
            except (UnicodeEncodeError, ValueError) as error:
                control = None
                data["mass_control_error"] = f"tokenizer_failure:{error}"
                record["error"] = data["mass_control_error"]
            if control is not None:
                data["mass_control"] = control
                record.update(asdict(control))
                record["mass_control_available"] = True
                record["value_utf8"] = control.value
                record["value_utf8_length"] = len(control.value.encode("utf-8"))
                record["value_sha256"] = hashlib.sha256(
                    control.value.encode("utf-8")
                ).hexdigest()
            elif "mass_control_error" not in data:
                data["mass_control_error"] = "no_prefix_with_exact_token_count"
                record["error"] = data["mass_control_error"]
        elif material is None:
            data["mass_control_error"] = "source_material_unavailable"
            record["error"] = data["mass_control_error"]
        else:
            data["mass_control_error"] = "tokenizer_unavailable"
            record["error"] = data["mass_control_error"]
        data["mass_control_record"] = record
        writer.write_json(f"{world.world_id}-mass-control.json", record)


def _protocol_record() -> dict[str, object]:
    return {
        "protocol": PROTOCOL_VERSION,
        "model": MODEL,
        "inspect_tag": INSPECT_TAG,
        "model_digest": MODEL_DIGEST,
        "endpoint": ENDPOINT,
        "docker_model_runner_version": DMR_VERSION,
        "docker_desktop_platform": DOCKER_DESKTOP_PLATFORM,
        "llama_backend_build": LLAMA_BACKEND_BUILD,
        "llama_backend_digest": LLAMA_BACKEND_DIGEST,
        "public_rule": PUBLIC_RULE,
        "actor_system": ACTOR_SYSTEM,
        "candidate_system": CANDIDATE_SYSTEM,
        "same_response_system": SAME_RESPONSE_SYSTEM,
        "authorship_responsibility": AUTHORSHIP_RESPONSIBILITY,
        "static_responsibility": STATIC_RESPONSIBILITY,
        "challenge_responsibility": CHALLENGE_RESPONSIBILITY,
        "actor_settings": ACTOR_SETTINGS,
        "author_settings": AUTHOR_SETTINGS,
        "same_response_settings": SAME_RESPONSE_SETTINGS,
        "conditions": CONDITIONS,
        "direct_identifiers": DIRECT_IDENTIFIERS,
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
        "single_call_budget": SINGLE_CALL_BUDGET,
        "same_response_budget": SAME_RESPONSE_BUDGET,
        "max_completion_allowance": MAX_COMPLETION_ALLOWANCE,
        "tokenizer_revision": TOKENIZER_REVISION,
        "tokenizer_utf8_length": TOKENIZER_UTF8_LENGTH,
        "tokenizer_sha256": TOKENIZER_SHA256,
        "tokenizer_implementation": TOKENIZER_IMPLEMENTATION,
        "template_renderer_implementation": TEMPLATE_RENDERER_IMPLEMENTATION,
        "chat_template_utf8_length": CHAT_TEMPLATE_UTF8_LENGTH,
        "chat_template_sha256": CHAT_TEMPLATE_SHA256,
        "chat_template_bindings": {
            "tools": "omitted",
            "add_generation_prompt": True,
            "enable_thinking": "omitted_undefined",
            "add_special_tokens": False,
        },
        "mass_control_seed": MASS_CONTROL_SEED,
        "mass_control_alphabet": MASS_CONTROL_ALPHABET,
        "mass_control_max_prefix": MASS_CONTROL_MAX_PREFIX,
        "governance_timing": "after_all_authorship_calls_or_packet_stop",
        "formation_and_validation_verdicts_forbidden": True,
    }


def integrity_audit(directory: Path) -> dict[str, object]:
    checked = []
    valid = True
    for meta_path in sorted((directory / "calls").glob("*.meta.json")):
        meta = json.loads(meta_path.read_text())
        stem = meta_path.name.removesuffix(".meta.json")
        request_path = directory / "calls" / f"{stem}.request.json"
        response_path = directory / "calls" / f"{stem}.response.json"
        request_hash = hashlib.sha256(request_path.read_bytes()).hexdigest()
        response_hash = hashlib.sha256(response_path.read_bytes()).hexdigest()
        item_valid = (
            request_hash == meta["request_sha256"]
            and response_hash == meta["response_sha256"]
        )
        valid = valid and item_valid
        checked.append({"stem": stem, "valid": item_valid})
    return {"valid": valid, "attempts_checked": len(checked), "checks": checked}


class DraftEvidenceWriter(EvidenceWriter):
    """Write decoded non-scalar provider strings without losing raw receipts."""

    def write_json(self, relative: str, value: object) -> None:
        (self.directory / relative).write_text(
            json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )


def run_contact(
    invoker: Invoker,
    directory: Path,
    provider_receipt: dict[str, object],
    token_counter: TokenCounter | None,
    physical_ceiling: int = PHYSICAL_CALL_CEILING,
) -> dict[str, object]:
    writer = DraftEvidenceWriter(directory)
    writer.write_json("protocol.json", _protocol_record())
    writer.write_json("provider.json", provider_receipt)
    runner = ContactRunner(invoker, writer, physical_ceiling)
    if provider_receipt.get("valid") is not True:
        summary = runner.summary("stopped", "provider_receipt_invalid")
        writer.write_json("summary.json", summary)
        audit = integrity_audit(directory)
        writer.write_json("integrity.json", audit)
        return summary

    state = "completed"
    stop_reason = None
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
            }
            writer.write_json(f"{world.world_id}-occurrence.json", occurrence)

        for call in direct_calls(runner.world_data):
            record = runner.record_candidate(call, runner.invoke(call))
            if call.call_id == DIRECT_IDENTIFIERS[str(call.world_id)][0]:
                data = runner.world_data[str(call.world_id)]
                data["source_content"] = record["content"]
                data["source_candidate_comparison_utf8"] = record[
                    "candidate_comparison_utf8"
                ]
                data["source_response_sha256"] = record["response_sha256"]

        freeze_mass_controls(runner, token_counter, writer)
        for call in downstream_calls(runner.world_data):
            runner.record_candidate(call, runner.invoke(call))
    except ContactStop as stop:
        state = "stopped"
        stop_reason = str(stop)

    runner.apply_governance()
    summary = runner.summary(state, stop_reason)
    writer.write_json("summary.json", summary)
    audit = integrity_audit(directory)
    summary["integrity"] = audit
    writer.write_json("integrity.json", audit)
    writer.write_json("summary.json", summary)
    return summary


def _run_command(command: tuple[str, ...]) -> dict[str, object]:
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    return {
        "command": list(command),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _endpoint_receipt() -> dict[str, object]:
    url = "http://localhost:12434/engines/v1/models"
    try:
        with urlopen(Request(url, method="GET"), timeout=10) as response:
            body = response.read()
            return {
                "url": url,
                "status": response.status,
                "body_sha256": hashlib.sha256(body).hexdigest(),
                "body": body.decode("utf-8", errors="replace"),
            }
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        return {"url": url, "error": repr(error)}


def _tokenizer_receipt(path: Path) -> dict[str, object]:
    try:
        body = path.read_bytes()
    except OSError as error:
        return {"valid": False, "path": str(path), "error": repr(error)}
    reasons = []
    if len(body) != TOKENIZER_UTF8_LENGTH:
        reasons.append("tokenizer_length_mismatch")
    digest = hashlib.sha256(body).hexdigest()
    if digest != TOKENIZER_SHA256:
        reasons.append("tokenizer_hash_mismatch")
    try:
        parsed = json.loads(body)
        tokens = {item["id"]: item["content"] for item in parsed["added_tokens"]}
        if tokens.get(151643) != "<|endoftext|>" or tokens.get(151645) != "<|im_end|>":
            reasons.append("tokenizer_special_ids_mismatch")
    except (json.JSONDecodeError, KeyError, TypeError):
        reasons.append("tokenizer_json_invalid")
    return {
        "valid": not reasons,
        "path": str(path),
        "utf8_length": len(body),
        "sha256": digest,
        "refusals": reasons,
    }


def collect_provider_receipt(tokenizer_path: Path) -> dict[str, object]:
    version = _run_command(("docker", "model", "version"))
    status = _run_command(("docker", "model", "status"))
    inventory = _run_command(("docker", "model", "list"))
    inspection = _run_command(("docker", "model", "inspect", MODEL))
    docker_version = _run_command(("docker", "version", "--format", "{{json .}}"))
    endpoint = _endpoint_receipt()
    tokenizer = _tokenizer_receipt(tokenizer_path)
    reasons = []
    for name, record in (
        ("version", version),
        ("status", status),
        ("inventory", inventory),
        ("inspection", inspection),
        ("docker_version", docker_version),
    ):
        if record["returncode"] != 0:
            reasons.append(f"{name}_command_failed")
    parsed_inspection = None
    if inspection["returncode"] == 0:
        try:
            parsed_inspection = json.loads(str(inspection["stdout"]))
            if parsed_inspection.get("id") != MODEL_DIGEST:
                reasons.append("model_digest_mismatch")
            if INSPECT_TAG not in parsed_inspection.get("tags", []):
                reasons.append("model_tag_mismatch")
            gguf = parsed_inspection["config"]["gguf"]
            template = gguf["tokenizer.chat_template"].encode("utf-8")
            if len(template) != CHAT_TEMPLATE_UTF8_LENGTH:
                reasons.append("chat_template_length_mismatch")
            if hashlib.sha256(template).hexdigest() != CHAT_TEMPLATE_SHA256:
                reasons.append("chat_template_hash_mismatch")
        except (json.JSONDecodeError, KeyError, TypeError, AttributeError):
            reasons.append("inspection_invalid")
    version_text = str(version["stdout"])
    if version_text.count(DMR_VERSION) < 2:
        reasons.append("docker_model_runner_version_mismatch")
    status_text = str(status["stdout"])
    if LLAMA_BACKEND_BUILD not in status_text or LLAMA_BACKEND_DIGEST not in status_text:
        reasons.append("llama_backend_mismatch")
    if "qwen3:14B-Q6_K" not in str(inventory["stdout"]):
        reasons.append("model_not_in_inventory")
    if docker_version["returncode"] == 0:
        try:
            parsed_docker = json.loads(str(docker_version["stdout"]))
            if parsed_docker["Server"]["Platform"]["Name"] != DOCKER_DESKTOP_PLATFORM:
                reasons.append("docker_desktop_version_mismatch")
        except (json.JSONDecodeError, KeyError, TypeError):
            reasons.append("docker_version_invalid")
    if endpoint.get("status") != 200:
        reasons.append("endpoint_unreachable")
    return {
        "valid": not reasons,
        "refusals": reasons,
        "endpoint": ENDPOINT,
        "version": version,
        "status": status,
        "inventory": inventory,
        "inspection": inspection,
        "parsed_inspection": parsed_inspection,
        "docker_version": docker_version,
        "endpoint_receipt": endpoint,
        "tokenizer": tokenizer,
        "mass_instrument_available": tokenizer["valid"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--tokenizer-json", type=Path, required=True)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if not args.live:
        raise SystemExit("live contact requires --live")
    receipt = collect_provider_receipt(args.tokenizer_json)
    token_counter = None
    if receipt.get("mass_instrument_available"):
        try:
            chat_template = receipt["parsed_inspection"]["config"]["gguf"][
                "tokenizer.chat_template"
            ]
            token_counter = PinnedTokenCounter(args.tokenizer_json, chat_template)
            receipt["tokenizer_implementation"] = token_counter.implementation
            receipt["template_renderer_implementation"] = (
                token_counter.renderer_implementation
            )
        except (KeyError, TypeError, ValueError) as error:
            receipt["mass_instrument_available"] = False
            receipt["tokenizer_load_error"] = str(error)
    summary = run_contact(
        DraftLiveInvoker(), args.evidence_dir, receipt, token_counter
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["contact_state"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
