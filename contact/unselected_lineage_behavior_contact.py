"""Materialize the reviewed unselected-lineage behavior charter."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time
from typing import Any, Callable, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from micro_environment.unselected_lineage_behavior import (
    APPLIED,
    HELD,
    HOLD,
    LineageActionResult,
    LineageProfile,
    LineageState,
    ProposalReceipt,
    apply_committed_action,
)
from unselected_lineage_specimen import (
    ABLATION,
    ACTION_RESPONSIBILITY,
    AUTHORSHIP_RESPONSIBILITY,
    BRANCHES,
    NO_PERSISTENCE,
    RAW_PERSISTENCE,
    RESULT_EXPOSED,
    RESULT_WITHHELD,
    ROLES,
    STATIC_INSTRUCTION,
    WITHHELD_SENTINEL,
    canonical_json_bytes,
    oracle_action,
)


PROTOCOL_VERSION = "unselected-lineage-behavior-contact-v1"
MODEL = "ai/qwen3:14B-Q6_K"
INSPECT_TAG = "docker.io/ai/qwen3:14B-Q6_K"
MODEL_DIGEST = "sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219"
ENDPOINT = "http://localhost:12434/engines/llama.cpp/v1/chat/completions"
DMR_VERSION = "v1.2.6"
DOCKER_DESKTOP_PLATFORM = "Docker Desktop 4.87.0 (236836)"
DOCKER_ENGINE_VERSION = "29.7.2"
LLAMA_BACKEND_BUILD = "b9879-metal"
LLAMA_BACKEND_DIGEST = "sha256:b70706f473b4043ca3e0c32704a7fda3412b83bceef0564684187b8011230de8"
CHAT_TEMPLATE_UTF8_LENGTH = 4_100
CHAT_TEMPLATE_SHA256 = "57f1fd00f0013a2be96aa79b857391f27e23df5b5f847072b524c897e24d0361"
TEMPLATE_RENDERER_IMPLEMENTATION = "jinja2-3.1.6"
TOKENIZER_UTF8_LENGTH = 11_422_654
TOKENIZER_SHA256 = "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
TOKENIZER_IMPLEMENTATION = "tokenizers-0.23.1"

MANIFEST_LENGTH = 7_720
MANIFEST_SHA256 = "4e1ab920415374e818a4d3afc5ed20acce64a1078098e127b9fd0e74312c0f3e"
WITNESS_LENGTH = 3_954
WITNESS_SHA256 = "a6e55d2da9a2812f370eb0c80c071231d1bfde7fb3aa85c090faf8faa09f7b36"
MANIFEST_PATH = Path(__file__).parents[1] / "docs" / "UNSELECTED_LINEAGE_LIVE_MANIFEST.json"
WITNESS_PATH = Path(__file__).parents[1] / "docs" / "UNSELECTED_LINEAGE_LEAKAGE_WITNESS.json"

PLANNED_LOGICAL_CALLS = 109
PHYSICAL_CALL_CEILING = 112
PLANNED_COMPLETION_ALLOWANCE = 5_280
PHYSICAL_COMPLETION_CONTINGENCY = 6_048
MAX_RETRIES = 3

SMOKE_RECEIPT = {
    "mode": "smoke_no_contact",
    "protocol_version": PROTOCOL_VERSION,
    "side_effects_entered": False,
}

FIXED_FIELD_NAMES = [
    "allowed_actions", "application_status", "available", "committed_proposal",
    "content", "controller_family", "device", "external_result",
    "movement_direction", "occurrence", "position", "position_after",
    "public_device", "reason", "responsibility", "retained_material",
    "selected_slot", "target", "target_reached",
]

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

DISPOSABLE_DEVICE = {
    "allowed_actions": ["16b40f96edd2e3a427f6", "3d5ec1e8e57cb97d362b", HOLD],
    "controller_family": "691997dfb3c2244c6340",
    "device": "4149894d5a4eff252c99",
    "position": 0,
    "target": 0,
}


class ContactRefusal(ValueError):
    """The packet or retained evidence violates its frozen charter."""


class DuplicateKey(ValueError):
    pass


def canonical_json(value: Any) -> str:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as error:
        raise ContactRefusal("value_is_not_canonical_json") from error


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


def strict_json(text: object) -> Any:
    if type(text) is not str:
        raise ContactRefusal("json_content_must_be_text")
    try:
        return json.loads(
            text,
            object_pairs_hook=_object,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
    except (json.JSONDecodeError, DuplicateKey, ValueError) as error:
        raise ContactRefusal("invalid_json_content") from error


def load_published(path: Path, length: int, digest: str) -> dict[str, Any]:
    value = strict_json(path.read_text(encoding="utf-8"))
    if type(value) is not dict:
        raise ContactRefusal("published_artifact_must_be_object")
    raw = canonical_json_bytes(value)
    if len(raw) != length or sha256_bytes(raw) != digest:
        raise ContactRefusal("published_artifact_binding_mismatch")
    return value


def public_state(value: dict[str, Any]) -> LineageState:
    if set(value) != {"allowed_actions", "controller_family", "device", "position", "target"}:
        raise ContactRefusal("public_device_fields_mismatch")
    actions = value["allowed_actions"]
    if type(actions) is not list or len(actions) != 3 or actions[2] != HOLD:
        raise ContactRefusal("allowed_actions_mismatch")
    return LineageState(
        value["controller_family"],
        value["device"],
        value["position"],
        value["target"],
        (actions[0], actions[1]),
    )


def public_device(state: LineageState) -> dict[str, Any]:
    return {
        "allowed_actions": [*state.controls, HOLD],
        "controller_family": state.controller_family,
        "device": state.device,
        "position": state.position,
        "target": state.target,
    }


def static_lesson(block: dict[str, Any]) -> str:
    profile = block["profile"]
    first = profile["increasing_slot"] == "first_increases"
    increasing, decreasing = ("first", "second") if first else ("second", "first")
    return (
        f"For controller family {profile['controller_family']}, the {increasing} "
        f"displayed control increases position and the {decreasing} displayed control decreases position."
    )


def profile(block: dict[str, Any]) -> LineageProfile:
    value = block["profile"]
    return LineageProfile(value["controller_family"], value["increasing_slot"])


def _direction(state: LineageState) -> str:
    if state.target == state.position:
        return "unchanged"
    return "up" if state.target > state.position else "down"


def _slot(state: LineageState, action: str) -> str | None:
    if action == HOLD:
        return None
    return "first" if state.controls.index(action) == 0 else "second"


def _fixed_surface(block: dict[str, Any]) -> bytes:
    return canonical_json_bytes({
        "acquisition": block["acquisition"]["public_device"],
        "action_responsibility": ACTION_RESPONSIBILITY,
        "action_system": ACTION_SYSTEM,
        "action_user_literals": ["ACTION REQUEST", "/no_think"],
        "authorship_responsibility": AUTHORSHIP_RESPONSIBILITY,
        "authorship_system": AUTHORSHIP_SYSTEM,
        "authorship_user_literals": ["AUTHORSHIP REQUEST", "/no_think"],
        "field_names": FIXED_FIELD_NAMES,
        "raw_fields": ["external_result", "occurrence"],
        "static": static_lesson(block),
        "withheld_sentinel": WITHHELD_SENTINEL,
    })


def construct_witness(manifest: dict[str, Any]) -> dict[str, Any]:
    if manifest.get("protocol_version") != "unselected-lineage-live-manifest-v1":
        raise ContactRefusal("manifest_protocol_mismatch")
    blocks = manifest.get("blocks")
    if type(blocks) is not list or len(blocks) != 4:
        raise ContactRefusal("manifest_blocks_mismatch")
    identifiers: list[str] = []
    witness_blocks = []
    crosses = []
    for block in blocks:
        hidden_profile = profile(block)
        acquisition = public_state(block["acquisition"]["public_device"])
        acquisition_expected = oracle_action(acquisition, hidden_profile)
        if acquisition_expected != block["acquisition"]["oracle_action"]:
            raise ContactRefusal("acquisition_oracle_mismatch")
        identifiers.append(hidden_profile.controller_family)
        fixed = _fixed_surface(block)
        cases = block["cases"]
        case_rows = []
        later_tokens: list[str] = []
        for case in cases:
            state = public_state(case["public_device"])
            expected = oracle_action(state, hidden_profile)
            if expected != case["oracle_action"]:
                raise ContactRefusal("case_oracle_mismatch")
            identifiers.extend((state.device, *state.controls, case["coordinate"]))
            later_tokens.extend((state.device, *state.controls))
            case_rows.append({
                "coordinate": case["coordinate"],
                "correct_slot": _slot(state, expected),
                "hidden_role": case["hidden_role"],
                "target_direction": _direction(state),
            })
        identifiers.extend((acquisition.device, *acquisition.controls))
        by_role = {case["hidden_role"]: case for case in cases}
        use = public_state(by_role["acquisition_use"]["public_device"])
        transfer = public_state(by_role["transfer"]["public_device"])
        current = public_state(by_role["already_current_non_transfer"]["public_device"])
        if _direction(use) != _direction(acquisition):
            raise ContactRefusal("acquisition_use_direction_mismatch")
        if _slot(transfer, oracle_action(transfer, hidden_profile)) == _slot(acquisition, acquisition_expected):
            raise ContactRefusal("transfer_slot_not_opposite")
        if oracle_action(current, hidden_profile) != HOLD:
            raise ContactRefusal("already_current_not_hold")
        copy = by_role["copy_control"]
        copy_action = copy["oracle_action"]
        branch_role_values = [*BRANCHES, *ROLES]
        visible_fixed = b"\n".join((ACTION_SYSTEM.encode(), AUTHORSHIP_SYSTEM.encode(), fixed))
        if any(value.encode() in visible_fixed for value in branch_role_values):
            raise ContactRefusal("model_visible_branch_or_role_label")
        witness_blocks.append({
            "acquisition_correct_slot": _slot(acquisition, acquisition_expected),
            "acquisition_direction": _direction(acquisition),
            "block": block["block"],
            "case_roles": case_rows,
            "copy_action": copy_action,
            "copy_action_absent_from_fixed_surface": copy_action.encode() not in fixed,
            "fixed_surface_sha256": sha256_bytes(fixed),
            "later_tokens_absent_from_fixed_surface": all(token.encode() not in fixed for token in later_tokens),
            "static_lesson_sha256": sha256_bytes(static_lesson(block).encode()),
        })
        crosses.append([hidden_profile.increasing_slot, _direction(acquisition)])
    if len(identifiers) != 80 or len(set(identifiers)) != 80:
        raise ContactRefusal("identifier_uniqueness_mismatch")
    return {
        "blocks": witness_blocks,
        "identifier_count": 80,
        "identifiers_unique": True,
        "manifest_sha256": sha256_bytes(canonical_json_bytes(manifest)),
        "model_visible_branch_or_role_labels": False,
        "profile_direction_cross": crosses,
        "protocol_version": "unselected-lineage-leakage-witness-v1",
    }


def action_request(device: dict[str, Any], retained_material: str) -> dict[str, Any]:
    return {
        "device": device,
        "responsibility": ACTION_RESPONSIBILITY,
        "retained_material": retained_material,
    }


def action_user(device: dict[str, Any], retained_material: str) -> str:
    return f"ACTION REQUEST\n{canonical_json(action_request(device, retained_material))}\n/no_think"


def authorship_user(material: dict[str, Any]) -> str:
    return f"AUTHORSHIP REQUEST\n{canonical_json(material)}\n/no_think"


def envelope(system: str, user: str, settings: dict[str, Any]) -> dict[str, Any]:
    return {
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "model": MODEL,
        **settings,
    }


@dataclass(frozen=True, slots=True)
class ProviderContent:
    available: bool
    content: str

    def __post_init__(self) -> None:
        if type(self.available) is not bool or type(self.content) is not str:
            raise ContactRefusal("invalid_provider_content_receipt")
        if not self.available and self.content != "":
            raise ContactRefusal("unavailable_provider_content_must_be_empty")


@dataclass(frozen=True, slots=True)
class ActionParse:
    valid: bool
    action: str | None
    reason: str | None


def parse_action(receipt: ProviderContent, allowed_actions: Iterable[str]) -> ActionParse:
    if not receipt.available:
        return ActionParse(False, None, "provider_content_unavailable")
    try:
        value = strict_json(receipt.content)
    except ContactRefusal:
        return ActionParse(False, None, "action_envelope_invalid")
    if type(value) is not dict or list(value) != ["action"] or type(value["action"]) is not str:
        return ActionParse(False, None, "action_envelope_invalid")
    action = value["action"]
    if action not in tuple(allowed_actions):
        return ActionParse(False, action, "action_not_listed")
    return ActionParse(True, action, None)


def proposal_from_content(receipt: ProviderContent, parsed: ActionParse) -> ProposalReceipt:
    if not receipt.available:
        return ProposalReceipt(False, "")
    if parsed.action is not None:
        return ProposalReceipt(True, parsed.action)
    return ProposalReceipt(True, receipt.content)


def exposed_result(result: LineageActionResult) -> dict[str, Any]:
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


def authorship_material(
    state: LineageState,
    proposal: ProposalReceipt,
    result: LineageActionResult,
    expose: bool,
) -> dict[str, Any]:
    return {
        "external_result": exposed_result(result) if expose else WITHHELD_SENTINEL,
        "occurrence": occurrence(state, proposal),
        "responsibility": AUTHORSHIP_RESPONSIBILITY,
    }


def raw_foreground(state: LineageState, proposal: ProposalReceipt, result: LineageActionResult) -> str:
    return canonical_json({"external_result": exposed_result(result), "occurrence": occurrence(state, proposal)})


@dataclass(frozen=True, slots=True)
class Intermediate:
    available: bool
    content: str
    invocation: str
    byte_length: int
    content_sha256: str
    provider_usage: object
    copied_acquisition_strings: tuple[str, ...]
    copied_result_strings: tuple[str, ...]


def _result_strings(result: LineageActionResult) -> tuple[str, ...]:
    values = exposed_result(result).values()
    return tuple(str(value) for value in values if value is not None and type(value) in (str, int))


def make_intermediate(
    content: ProviderContent,
    invocation: str,
    state: LineageState,
    proposal: ProposalReceipt,
    result: LineageActionResult,
    provider_usage: object,
) -> Intermediate:
    acquisition_strings = (*state.controls, HOLD, proposal.content)
    result_strings = _result_strings(result)
    return Intermediate(
        content.available,
        content.content,
        invocation,
        len(content.content.encode("utf-8")),
        sha256_bytes(content.content.encode("utf-8")),
        provider_usage,
        tuple(value for value in acquisition_strings if value and value in content.content),
        tuple(value for value in result_strings if value and value in content.content),
    )


def branch_materials(
    block: dict[str, Any],
    acquisition_proposal: ProposalReceipt,
    acquisition_result: LineageActionResult,
    withheld: Intermediate,
    exposed: Intermediate,
) -> dict[str, tuple[str, Intermediate | None]]:
    return {
        NO_PERSISTENCE: ("", None),
        RAW_PERSISTENCE: (
            raw_foreground(public_state(block["acquisition"]["public_device"]), acquisition_proposal, acquisition_result),
            None,
        ),
        RESULT_WITHHELD: (withheld.content if withheld.available else "", withheld),
        RESULT_EXPOSED: (exposed.content if exposed.available else "", exposed),
        ABLATION: ("", exposed),
        STATIC_INSTRUCTION: (static_lesson(block), None),
    }


@dataclass(frozen=True, slots=True)
class LogicalCall:
    index: int
    invocation: str
    responsibility: str
    block: str | None
    branch: str | None
    case: str | None
    envelope: dict[str, Any]

    @property
    def request_body(self) -> bytes:
        return canonical_json_bytes(self.envelope)


def make_call(
    index: int,
    responsibility: str,
    system: str,
    user: str,
    settings: dict[str, Any],
    *,
    block: str | None = None,
    branch: str | None = None,
    case: str | None = None,
) -> LogicalCall:
    return LogicalCall(
        index,
        f"iv{index:03d}",
        responsibility,
        block,
        branch,
        case,
        envelope(system, user, settings),
    )


def render_chat(chat_template: str, system: str, user: str) -> str:
    try:
        import jinja2
        from jinja2.sandbox import ImmutableSandboxedEnvironment
    except ImportError as error:
        raise ContactRefusal("jinja2_package_unavailable") from error
    if f"jinja2-{jinja2.__version__}" != TEMPLATE_RENDERER_IMPLEMENTATION:
        raise ContactRefusal("template_renderer_implementation_mismatch")
    environment = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True)
    environment.globals["raise_exception"] = lambda message: (_ for _ in ()).throw(ContactRefusal(message))
    return environment.from_string(chat_template).render(
        messages=(
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ),
        add_generation_prompt=True,
    )


def later_coordinates(manifest: dict[str, Any]) -> tuple[tuple[int, dict[str, Any], str, dict[str, Any]], ...]:
    blocks = manifest["blocks"]
    rows = []
    for case_round in range(4):
        for branch_round in range(6):
            for block_index, block in enumerate(blocks):
                index = 14 + ((case_round * 6 + branch_round) * 4 + block_index)
                branch = block["branch_order"][branch_round]
                coordinate = block["case_order"][case_round]
                case = next(value for value in block["cases"] if value["coordinate"] == coordinate)
                rows.append((index, block, branch, case))
    if len(rows) != 96 or rows[0][0] != 14 or rows[-1][0] != 109:
        raise ContactRefusal("later_schedule_mismatch")
    return tuple(rows)


def provider_content(envelope_value: object, http_status: int | None) -> ProviderContent:
    if http_status != 200 or type(envelope_value) is not dict:
        return ProviderContent(False, "")
    choices = envelope_value.get("choices")
    if type(choices) is not list or len(choices) != 1 or type(choices[0]) is not dict:
        return ProviderContent(False, "")
    message = choices[0].get("message")
    if type(message) is not dict or type(message.get("content")) is not str:
        return ProviderContent(False, "")
    return ProviderContent(True, message["content"])


@dataclass(frozen=True, slots=True)
class ProviderAttempt:
    request_body: bytes
    response_body: bytes
    response_envelope: object
    http_status: int | None
    error: str | None = None
    retryable: bool = False
    started_at: str | None = None
    ended_at: str | None = None
    elapsed_seconds: float | None = None


def provider_metadata(value: object) -> dict[str, Any]:
    if type(value) is not dict:
        return {"choice_count": None, "finish_reason": None, "model": None, "reasoning_content": None, "usage": None}
    choices = value.get("choices")
    choice = choices[0] if type(choices) is list and len(choices) == 1 and type(choices[0]) is dict else None
    message = choice.get("message") if type(choice) is dict and type(choice.get("message")) is dict else None
    return {
        "choice_count": len(choices) if type(choices) is list else None,
        "finish_reason": choice.get("finish_reason") if type(choice) is dict else None,
        "model": value.get("model"),
        "reasoning_content": message.get("reasoning_content") if type(message) is dict else None,
        "usage": value.get("usage"),
    }


Invoker = Callable[[LogicalCall, int], ProviderAttempt]
TokenCounter = Callable[[str], int]


@dataclass(frozen=True, slots=True)
class RenderAuditor:
    chat_template: str
    token_counter: TokenCounter

    def __post_init__(self) -> None:
        raw = self.chat_template.encode("utf-8")
        if len(raw) != CHAT_TEMPLATE_UTF8_LENGTH or sha256_bytes(raw) != CHAT_TEMPLATE_SHA256:
            raise ContactRefusal("chat_template_binding_mismatch")

    def audit(self, call: LogicalCall) -> dict[str, Any]:
        messages = call.envelope.get("messages")
        if type(messages) is not list or len(messages) != 2:
            raise ContactRefusal("render_messages_mismatch")
        if [message.get("role") for message in messages if type(message) is dict] != ["system", "user"]:
            raise ContactRefusal("render_roles_mismatch")
        rendered = render_chat(self.chat_template, messages[0]["content"], messages[1]["content"])
        return {
            "bindings": {
                "add_generation_prompt": True,
                "enable_thinking": "omitted_undefined",
                "tools": "omitted",
            },
            "rendered_utf8_length": len(rendered.encode("utf-8")),
            "rendered_sha256": sha256_bytes(rendered.encode("utf-8")),
            "prompt_tokens": self.token_counter(rendered),
        }


class PinnedTokenCounter:
    def __init__(self, tokenizer_path: Path, chat_template: str) -> None:
        body = tokenizer_path.read_bytes()
        if len(body) != TOKENIZER_UTF8_LENGTH or sha256_bytes(body) != TOKENIZER_SHA256:
            raise ContactRefusal("tokenizer_binding_mismatch")
        try:
            import tokenizers
            from tokenizers import Tokenizer
        except ImportError as error:
            raise ContactRefusal("tokenizers_package_unavailable") from error
        if f"tokenizers-{tokenizers.__version__}" != TOKENIZER_IMPLEMENTATION:
            raise ContactRefusal("tokenizer_implementation_mismatch")
        self.tokenizer = Tokenizer.from_file(str(tokenizer_path))
        self.render_auditor = RenderAuditor(chat_template, self.count_rendered)

    def count_rendered(self, rendered: str) -> int:
        return len(self.tokenizer.encode(rendered, add_special_tokens=False).ids)


@dataclass(frozen=True, slots=True)
class PacketResult:
    manifest: dict[str, Any]
    witness: dict[str, Any]
    calls: tuple[dict[str, Any], ...]
    attempts: tuple[dict[str, Any], ...]
    action_receipts: tuple[dict[str, Any], ...]
    acquisition_results: dict[str, LineageActionResult]
    intermediates: dict[tuple[str, str], Intermediate]
    later: tuple[dict[str, Any], ...]
    report: dict[str, Any]


class PacketRunner:
    def __init__(
        self,
        invoker: Invoker,
        *,
        physical_ceiling: int = PHYSICAL_CALL_CEILING,
        retry_ceiling: int = MAX_RETRIES,
        completion_ceiling: int = PHYSICAL_COMPLETION_CONTINGENCY,
        render_auditor: RenderAuditor | None = None,
    ) -> None:
        self.invoker = invoker
        self.physical_ceiling = physical_ceiling
        self.retry_ceiling = retry_ceiling
        self.completion_ceiling = completion_ceiling
        self.physical = 0
        self.retries = 0
        self.reserved_completion = 0
        self.render_auditor = render_auditor
        self.attempts: list[dict[str, Any]] = []
        self.calls: list[dict[str, Any]] = []

    def _attempt(self, call: LogicalCall) -> ProviderContent:
        max_tokens = call.envelope["max_tokens"]
        render_audit = None if self.render_auditor is None else self.render_auditor.audit(call)
        for attempt_index in (1, 2):
            retry = attempt_index == 2
            if retry and self.retries >= self.retry_ceiling:
                break
            if self.physical >= self.physical_ceiling or self.reserved_completion + max_tokens > self.completion_ceiling:
                break
            self.physical += 1
            self.reserved_completion += max_tokens
            if retry:
                self.retries += 1
            attempt = self.invoker(call, attempt_index)
            if attempt.request_body != call.request_body:
                raise ContactRefusal("request_bytes_drifted")
            self.attempts.append({
                "attempt": attempt_index,
                "invocation": call.invocation,
                "request_body": attempt.request_body,
                "response_body": attempt.response_body,
                "response_envelope": attempt.response_envelope,
                "http_status": attempt.http_status,
                "error": attempt.error,
                "retryable": attempt.retryable,
                "retry_of": 1 if retry else None,
                "started_at": attempt.started_at,
                "ended_at": attempt.ended_at,
                "elapsed_seconds": attempt.elapsed_seconds,
                "provider_metadata": provider_metadata(attempt.response_envelope),
            })
            if (
                attempt.retryable
                and attempt.http_status is None
                and attempt_index == 1
                and self.retries < self.retry_ceiling
                and self.physical < self.physical_ceiling
                and self.reserved_completion + max_tokens <= self.completion_ceiling
            ):
                continue
            receipt = provider_content(attempt.response_envelope, attempt.http_status)
            self.calls.append({
                "index": call.index,
                "invocation": call.invocation,
                "responsibility": call.responsibility,
                "block": call.block,
                "branch": call.branch,
                "case": call.case,
                "request_body": call.request_body,
                "provider_content": asdict(receipt),
                "provider_metadata": provider_metadata(attempt.response_envelope),
                "render_audit": render_audit,
            })
            return receipt
        receipt = ProviderContent(False, "")
        self.calls.append({
            "index": call.index,
            "invocation": call.invocation,
            "responsibility": call.responsibility,
            "block": call.block,
            "branch": call.branch,
            "case": call.case,
            "request_body": call.request_body,
            "provider_content": asdict(receipt),
            "provider_metadata": provider_metadata({}),
            "render_audit": render_audit,
        })
        return receipt

    def action(self, call: LogicalCall, state: LineageState, hidden_profile: LineageProfile) -> dict[str, Any]:
        content = self._attempt(call)
        parsed = parse_action(content, (*state.controls, HOLD))
        proposal = proposal_from_content(content, parsed)
        result = apply_committed_action(state, hidden_profile, proposal)
        expected = oracle_action(state, hidden_profile)
        return {
            "call": call,
            "provider_content": content,
            "parse": parsed,
            "proposal": proposal,
            "result": result,
            "interface_valid": parsed.valid,
            "environment_valid": result.status in (APPLIED, HELD),
            "correct_action": parsed.valid and proposal.content == expected,
            "target_reached": result.target_reached,
            "expected_action": expected,
        }


def _authorship_calls(manifest: dict[str, Any], acquisition: dict[str, dict[str, Any]]) -> tuple[LogicalCall, ...]:
    calls = []
    index = 6
    for block in manifest["blocks"]:
        row = acquisition[block["block"]]
        for branch in block["authorship_order"]:
            expose = branch == RESULT_EXPOSED
            material = authorship_material(row["state"], row["proposal"], row["result"], expose)
            calls.append(make_call(
                index,
                "intermediate_authorship",
                AUTHORSHIP_SYSTEM,
                authorship_user(material),
                AUTHORSHIP_SETTINGS,
                block=block["block"],
                branch=branch,
            ))
            index += 1
    return tuple(calls)


def _score_later(manifest: dict[str, Any], later: list[dict[str, Any]], acquisition: dict[str, dict[str, Any]]) -> dict[str, Any]:
    block_map = {block["block"]: block for block in manifest["blocks"]}
    expected_coordinates = {
        (block["block"], branch, case["coordinate"], case["hidden_role"])
        for block in manifest["blocks"] for branch in BRANCHES for case in block["cases"]
    }
    actual = {(row["block"], row["branch"], row["case"], row["role"]) for row in later}
    if actual != expected_coordinates or len(later) != len(actual):
        raise ContactRefusal("later_denominator_mismatch")
    for row in later:
        block = block_map[row["block"]]
        case = next(value for value in block["cases"] if value["coordinate"] == row["case"])
        state = public_state(case["public_device"])
        if row["result"] != apply_committed_action(state, profile(block), row["proposal"]):
            raise ContactRefusal("later_result_physics_mismatch")
    output: dict[str, Any] = {"assigned": 96, "branches": {}}
    for branch in BRANCHES:
        output["branches"][branch] = {}
        for role in ROLES:
            rows = [row for row in later if row["branch"] == branch and row["role"] == role]
            counts: dict[str, Any] = {
                "assigned": len(rows),
                "provider_content_available": sum(row["provider_content"].available for row in rows),
                "action_interface_valid": sum(row["interface_valid"] for row in rows),
                "environment_application_valid": sum(row["environment_valid"] for row in rows),
                "correct_action": sum(row["correct_action"] for row in rows),
                "invalid_or_unavailable": sum(not row["interface_valid"] for row in rows),
                "actions": {},
                "acquisition_status": {},
            }
            for row in rows:
                key = row["proposal"].content if row["proposal"].available else "<provider-content-unavailable>"
                counts["actions"][key] = counts["actions"].get(key, 0) + 1
                status = acquisition[row["block"]]["result"].status
                counts["acquisition_status"][status] = counts["acquisition_status"].get(status, 0) + 1
            output["branches"][branch][role] = counts
    output["formation_verdict"] = None
    output["validation_verdict"] = None
    comparisons = (
        ("raw_minus_no_persistence", RAW_PERSISTENCE, NO_PERSISTENCE),
        ("static_minus_no_persistence", STATIC_INSTRUCTION, NO_PERSISTENCE),
        ("withheld_minus_no_persistence", RESULT_WITHHELD, NO_PERSISTENCE),
        ("exposed_minus_withheld", RESULT_EXPOSED, RESULT_WITHHELD),
        ("exposed_minus_ablation", RESULT_EXPOSED, ABLATION),
        ("ablation_minus_no_persistence", ABLATION, NO_PERSISTENCE),
    )
    paired = []
    for block in manifest["blocks"]:
        for role in ROLES:
            rows = {(row["branch"]): row for row in later if row["block"] == block["block"] and row["role"] == role}
            for name, left, right in comparisons:
                left_row, right_row = rows[left], rows[right]
                paired.append({
                    "block": block["block"],
                    "role": role,
                    "comparison": name,
                    "correct_action_delta": int(left_row["correct_action"]) - int(right_row["correct_action"]),
                    "interface_valid_delta": int(left_row["interface_valid"]) - int(right_row["interface_valid"]),
                    "environment_valid_delta": int(left_row["environment_valid"]) - int(right_row["environment_valid"]),
                    "proposal_equal": left_row["proposal"] == right_row["proposal"],
                    "result_equal": left_row["result"] == right_row["result"],
                })
    output["paired_facts"] = paired
    return output


def _request_audit(calls: list[dict[str, Any]], later: list[dict[str, Any]]) -> dict[str, Any]:
    authorship = []
    for block in sorted({row["block"] for row in calls if row["responsibility"] == "intermediate_authorship"}):
        rows = {row["branch"]: row for row in calls if row["block"] == block and row["responsibility"] == "intermediate_authorship"}
        exposed, withheld = rows[RESULT_EXPOSED], rows[RESULT_WITHHELD]
        authorship.append({
            "block": block,
            "exposed_request_sha256": sha256_bytes(exposed["request_body"]),
            "withheld_request_sha256": sha256_bytes(withheld["request_body"]),
            "request_byte_delta": len(exposed["request_body"]) - len(withheld["request_body"]),
            "prompt_token_delta": (
                exposed["render_audit"]["prompt_tokens"] - withheld["render_audit"]["prompt_tokens"]
                if exposed["render_audit"] is not None and withheld["render_audit"] is not None else None
            ),
        })
    matched = []
    keys = sorted({(row["block"], row["case"]) for row in later})
    for block, case in keys:
        rows = {row["branch"]: row for row in later if row["block"] == block and row["case"] == case}
        no = rows[NO_PERSISTENCE]
        branches = {}
        for branch in BRANCHES:
            row = rows[branch]
            call_record = next(value for value in calls if value["invocation"] == row["call"].invocation)
            no_call = next(value for value in calls if value["invocation"] == no["call"].invocation)
            branches[branch] = {
                "request_sha256": sha256_bytes(row["call"].request_body),
                "request_byte_delta_from_no_persistence": len(row["call"].request_body) - len(no["call"].request_body),
                "prompt_token_delta_from_no_persistence": (
                    call_record["render_audit"]["prompt_tokens"] - no_call["render_audit"]["prompt_tokens"]
                    if call_record["render_audit"] is not None and no_call["render_audit"] is not None else None
                ),
                "foreground_utf8_length": len(row["delivered"].encode("utf-8")),
                "foreground_sha256": sha256_bytes(row["delivered"].encode("utf-8")),
            }
        matched.append({
            "block": block,
            "case": case,
            "branches": branches,
            "no_persistence_ablation_request_equal": rows[NO_PERSISTENCE]["call"].request_body == rows[ABLATION]["call"].request_body,
        })
    return {"authorship": authorship, "later": matched}


def run_packet(
    invoker: Invoker,
    *,
    physical_ceiling: int = PHYSICAL_CALL_CEILING,
    render_auditor: RenderAuditor | None = None,
) -> PacketResult:
    manifest = load_published(MANIFEST_PATH, MANIFEST_LENGTH, MANIFEST_SHA256)
    published_witness = load_published(WITNESS_PATH, WITNESS_LENGTH, WITNESS_SHA256)
    witness = construct_witness(manifest)
    if witness != published_witness:
        raise ContactRefusal("constructed_witness_mismatch")
    runner = PacketRunner(invoker, physical_ceiling=physical_ceiling, render_auditor=render_auditor)
    action_receipts: list[dict[str, Any]] = []

    disposable = make_call(1, "disposable_interface", ACTION_SYSTEM, action_user(DISPOSABLE_DEVICE, ""), ACTION_SETTINGS)
    disposable_content = runner._attempt(disposable)
    disposable_parse = parse_action(disposable_content, DISPOSABLE_DEVICE["allowed_actions"])
    disposable_proposal = proposal_from_content(disposable_content, disposable_parse)
    action_receipts.append({
        "invocation": "iv001",
        "block": None,
        "branch": None,
        "case": None,
        "provider_content": disposable_content,
        "parse": disposable_parse,
        "proposal": disposable_proposal,
        "result": None,
        "interface_valid": disposable_parse.valid,
        "environment_valid": None,
        "expected_action": None,
        "correct_action": None,
    })
    if not disposable_parse.valid:
        report = {"interface_stop": True, "formation_verdict": None, "validation_verdict": None}
        return PacketResult(manifest, witness, tuple(runner.calls), tuple(runner.attempts), tuple(action_receipts), {}, {}, (), report)

    acquisition: dict[str, dict[str, Any]] = {}
    for block_index, block in enumerate(manifest["blocks"]):
        state = public_state(block["acquisition"]["public_device"])
        call = make_call(2 + block_index, "acquisition_action", ACTION_SYSTEM, action_user(public_device(state), ""), ACTION_SETTINGS, block=block["block"])
        row = runner.action(call, state, profile(block))
        row["state"] = state
        acquisition[block["block"]] = row
        action_receipts.append({
            "invocation": call.invocation,
            "block": block["block"],
            "branch": None,
            "case": None,
            **{key: row[key] for key in ("provider_content", "parse", "proposal", "result", "interface_valid", "environment_valid", "expected_action", "correct_action")},
        })

    intermediates: dict[tuple[str, str], Intermediate] = {}
    for call in _authorship_calls(manifest, acquisition):
        content = runner._attempt(call)
        upstream = acquisition[call.block or ""]
        usage = runner.calls[-1]["provider_metadata"]["usage"]
        intermediates[(call.block or "", call.branch or "")] = make_intermediate(
            content,
            call.invocation,
            upstream["state"],
            upstream["proposal"],
            upstream["result"],
            usage,
        )

    later_rows: list[dict[str, Any]] = []
    for index, block, branch, case in later_coordinates(manifest):
        block_id = block["block"]
        withheld = intermediates[(block_id, RESULT_WITHHELD)]
        exposed = intermediates[(block_id, RESULT_EXPOSED)]
        upstream = acquisition[block_id]
        materials = branch_materials(block, upstream["proposal"], upstream["result"], withheld, exposed)
        delivered, hidden = materials[branch]
        state = public_state(case["public_device"])
        call = make_call(index, "later_action", ACTION_SYSTEM, action_user(public_device(state), delivered), ACTION_SETTINGS, block=block_id, branch=branch, case=case["coordinate"])
        row = runner.action(call, state, profile(block))
        row.update({"block": block_id, "branch": branch, "case": case["coordinate"], "role": case["hidden_role"], "delivered": delivered, "hidden_intermediate": hidden})
        later_rows.append(row)
        action_receipts.append({
            "invocation": call.invocation,
            "block": block_id,
            "branch": branch,
            "case": case["coordinate"],
            **{key: row[key] for key in ("provider_content", "parse", "proposal", "result", "interface_valid", "environment_valid", "expected_action", "correct_action")},
        })

    report = _score_later(manifest, later_rows, acquisition)
    report.update({
        "interface_stop": False,
        "logical_calls": len(runner.calls),
        "physical_attempts": runner.physical,
        "retries": runner.retries,
        "reserved_completion_tokens": runner.reserved_completion,
        "request_audit": _request_audit(runner.calls, later_rows),
    })
    return PacketResult(
        manifest,
        witness,
        tuple(runner.calls),
        tuple(runner.attempts),
        tuple(action_receipts),
        {key: value["result"] for key, value in acquisition.items()},
        intermediates,
        tuple(later_rows),
        report,
    )


def _result_json(result: LineageActionResult) -> dict[str, Any]:
    return asdict(result)


def packet_projection(packet: PacketResult) -> dict[str, Any]:
    later = []
    for row in packet.later:
        hidden = row["hidden_intermediate"]
        later.append({
            "block": row["block"],
            "branch": row["branch"],
            "case": row["case"],
            "role": row["role"],
            "invocation": row["call"].invocation,
            "request_sha256": sha256_bytes(row["call"].request_body),
            "provider_content": asdict(row["provider_content"]),
            "parse": asdict(row["parse"]),
            "proposal": asdict(row["proposal"]),
            "result": _result_json(row["result"]),
            "interface_valid": row["interface_valid"],
            "environment_valid": row["environment_valid"],
            "correct_action": row["correct_action"],
            "target_reached": row["target_reached"],
            "expected_action": row["expected_action"],
            "delivered": row["delivered"],
            "hidden_intermediate": None if hidden is None else asdict(hidden),
        })
    return {
        "protocol_version": PROTOCOL_VERSION,
        "manifest_sha256": sha256_bytes(canonical_json_bytes(packet.manifest)),
        "witness_sha256": sha256_bytes(canonical_json_bytes(packet.witness)),
        "calls": [{
            **{key: value for key, value in row.items() if key != "request_body"},
            "request_sha256": sha256_bytes(row["request_body"]),
        } for row in packet.calls],
        "attempts": [{
            **{key: value for key, value in row.items() if key not in {"request_body", "response_body", "response_envelope"}},
            "request_sha256": sha256_bytes(row["request_body"]),
            "response_sha256": sha256_bytes(row["response_body"]),
        } for row in packet.attempts],
        "action_receipts": [{
            **{key: value for key, value in row.items() if key not in {"provider_content", "parse", "proposal", "result"}},
            "provider_content": asdict(row["provider_content"]),
            "parse": asdict(row["parse"]),
            "proposal": asdict(row["proposal"]),
            "result": None if row["result"] is None else _result_json(row["result"]),
        } for row in packet.action_receipts],
        "acquisition_results": {key: _result_json(value) for key, value in packet.acquisition_results.items()},
        "intermediates": [
            {"block": block, "branch": branch, **asdict(value)}
            for (block, branch), value in sorted(packet.intermediates.items())
        ],
        "later": later,
        "report": packet.report,
    }


class EvidenceWriter:
    def __init__(self, directory: Path) -> None:
        try:
            directory.mkdir(parents=True, exist_ok=False)
        except FileExistsError as error:
            raise ContactRefusal("evidence_directory_not_fresh") from error
        self.directory = directory
        (directory / "attempts").mkdir()

    def write(self, packet: PacketResult, *, physical_ceiling: int = PHYSICAL_CALL_CEILING) -> None:
        if any(row.get("render_audit") is None for row in packet.calls):
            raise ContactRefusal("evidence_requires_render_audits")
        (self.directory / "manifest.canonical.json").write_bytes(canonical_json_bytes(packet.manifest))
        (self.directory / "witness.canonical.json").write_bytes(canonical_json_bytes(packet.witness))
        for number, attempt in enumerate(packet.attempts, 1):
            stem = f"{number:03d}-{attempt['invocation']}-a{attempt['attempt']}"
            (self.directory / "attempts" / f"{stem}.request.json").write_bytes(attempt["request_body"])
            (self.directory / "attempts" / f"{stem}.response.bin").write_bytes(attempt["response_body"])
            meta = {
                "attempt": attempt["attempt"],
                "error": attempt["error"],
                "http_status": attempt["http_status"],
                "invocation": attempt["invocation"],
                "provider_metadata": attempt["provider_metadata"],
                "retry_of": attempt["retry_of"],
                "retryable": attempt["retryable"],
                "started_at": attempt["started_at"],
                "ended_at": attempt["ended_at"],
                "elapsed_seconds": attempt["elapsed_seconds"],
            }
            (self.directory / "attempts" / f"{stem}.meta.json").write_text(
                json.dumps(meta, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
        record = {
            "physical_ceiling": physical_ceiling,
            "projection": packet_projection(packet),
        }
        (self.directory / "packet.json").write_text(
            json.dumps(record, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )


def _decode_envelope(raw: bytes) -> object:
    try:
        return strict_json(raw.decode("utf-8"))
    except (UnicodeDecodeError, ContactRefusal):
        return {}


def replay_evidence(directory: Path, render_auditor: RenderAuditor) -> PacketResult:
    record = strict_json((directory / "packet.json").read_text(encoding="utf-8"))
    if type(record) is not dict or set(record) != {"physical_ceiling", "projection"}:
        raise ContactRefusal("evidence_packet_shape_mismatch")
    manifest_raw = (directory / "manifest.canonical.json").read_bytes()
    witness_raw = (directory / "witness.canonical.json").read_bytes()
    if len(manifest_raw) != MANIFEST_LENGTH or sha256_bytes(manifest_raw) != MANIFEST_SHA256:
        raise ContactRefusal("retained_manifest_mismatch")
    if len(witness_raw) != WITNESS_LENGTH or sha256_bytes(witness_raw) != WITNESS_SHA256:
        raise ContactRefusal("retained_witness_mismatch")
    attempts: dict[tuple[str, int], ProviderAttempt] = {}
    for meta_path in sorted((directory / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        meta = strict_json(meta_path.read_text(encoding="utf-8"))
        request_body = (directory / "attempts" / f"{stem}.request.json").read_bytes()
        response_body = (directory / "attempts" / f"{stem}.response.bin").read_bytes()
        attempts[(meta["invocation"], meta["attempt"])] = ProviderAttempt(
            request_body,
            response_body,
            _decode_envelope(response_body),
            meta["http_status"],
            meta["error"],
            meta["retryable"],
            meta["started_at"],
            meta["ended_at"],
            meta["elapsed_seconds"],
        )

    def replay_invoker(call: LogicalCall, attempt_index: int) -> ProviderAttempt:
        try:
            return attempts[(call.invocation, attempt_index)]
        except KeyError as error:
            raise ContactRefusal("missing_retained_attempt") from error

    replayed = run_packet(
        replay_invoker,
        physical_ceiling=record["physical_ceiling"],
        render_auditor=render_auditor,
    )
    regenerated = packet_projection(replayed)
    for section in (
        "manifest_sha256", "witness_sha256", "calls", "attempts",
        "action_receipts", "acquisition_results", "intermediates", "later", "report",
    ):
        if canonical_json_bytes(regenerated[section]) != canonical_json_bytes(record["projection"][section]):
            raise ContactRefusal(f"integrity_projection_mismatch:{section}")
    return replayed


class DockerInvoker:
    """Dormant live transport; execution requires a later contact decision."""

    def __init__(self, endpoint: str = ENDPOINT, timeout_seconds: int = 300) -> None:
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds

    def __call__(self, call: LogicalCall, attempt_index: int) -> ProviderAttempt:
        request = Request(
            self.endpoint,
            data=call.request_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        started = datetime.now(timezone.utc)
        clock = time.monotonic()
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read()
                status = response.status
        except HTTPError as error:
            body = error.read()
            ended = datetime.now(timezone.utc)
            return ProviderAttempt(call.request_body, body, _decode_envelope(body), error.code, f"http_{error.code}", False, started.isoformat(), ended.isoformat(), time.monotonic() - clock)
        except (URLError, TimeoutError) as error:
            ended = datetime.now(timezone.utc)
            return ProviderAttempt(call.request_body, b"", {}, None, repr(error), True, started.isoformat(), ended.isoformat(), time.monotonic() - clock)
        ended = datetime.now(timezone.utc)
        return ProviderAttempt(call.request_body, body, _decode_envelope(body), status, None, False, started.isoformat(), ended.isoformat(), time.monotonic() - clock)


CommandRunner = Callable[[tuple[str, ...]], dict[str, Any]]
EndpointReader = Callable[[], dict[str, Any]]


def shell_command(command: tuple[str, ...]) -> dict[str, Any]:
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    return {
        "command": list(command),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def endpoint_receipt() -> dict[str, Any]:
    url = "http://localhost:12434/engines/v1/models"
    try:
        with urlopen(Request(url, method="GET"), timeout=10) as response:
            body = response.read()
            return {
                "url": url,
                "status": response.status,
                "body": body.decode("utf-8", errors="replace"),
                "body_sha256": sha256_bytes(body),
            }
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        return {"url": url, "error": repr(error)}


def collect_provider_receipt(
    command_runner: CommandRunner = shell_command,
    endpoint_reader: EndpointReader = endpoint_receipt,
) -> dict[str, Any]:
    commands = {
        "model_version": ("docker", "model", "version"),
        "model_status": ("docker", "model", "status"),
        "model_list": ("docker", "model", "list"),
        "model_inspect": ("docker", "model", "inspect", MODEL),
        "docker_version": ("docker", "version", "--format", "{{json .}}"),
    }
    receipts = {name: command_runner(command) for name, command in commands.items()}
    endpoint = endpoint_reader()
    reasons = []
    for name, receipt in receipts.items():
        if receipt.get("returncode") != 0:
            reasons.append(f"{name}_failed")
    inspection = None
    chat_template = None
    try:
        inspection = strict_json(receipts["model_inspect"]["stdout"])
        if inspection.get("id") != MODEL_DIGEST or INSPECT_TAG not in inspection.get("tags", []):
            reasons.append("model_identity_mismatch")
        gguf = inspection["config"]["gguf"]
        chat_template = gguf["tokenizer.chat_template"]
        raw = chat_template.encode("utf-8")
        if len(raw) != CHAT_TEMPLATE_UTF8_LENGTH or sha256_bytes(raw) != CHAT_TEMPLATE_SHA256:
            reasons.append("chat_template_mismatch")
        if inspection["config"].get("architecture") != "qwen3":
            reasons.append("architecture_mismatch")
    except (ContactRefusal, KeyError, TypeError, AttributeError):
        reasons.append("model_inspect_invalid")
    if DMR_VERSION not in str(receipts["model_version"].get("stdout", "")):
        reasons.append("model_runner_version_mismatch")
    version_text = str(receipts["model_version"].get("stdout", ""))
    if version_text.count(DMR_VERSION) < 2:
        reasons.append("model_runner_client_server_mismatch")
    status_text = str(receipts["model_status"].get("stdout", ""))
    if LLAMA_BACKEND_BUILD not in status_text or LLAMA_BACKEND_DIGEST not in status_text:
        reasons.append("llama_backend_mismatch")
    try:
        docker = strict_json(receipts["docker_version"]["stdout"])
        if docker["Client"]["Version"] != DOCKER_ENGINE_VERSION:
            reasons.append("docker_client_version_mismatch")
        if docker["Server"]["Version"] != DOCKER_ENGINE_VERSION:
            reasons.append("docker_engine_version_mismatch")
        if docker["Server"]["Platform"]["Name"] != DOCKER_DESKTOP_PLATFORM:
            reasons.append("docker_desktop_platform_mismatch")
    except (ContactRefusal, KeyError, TypeError):
        reasons.append("docker_version_invalid")
    if endpoint.get("status") != 200:
        reasons.append("endpoint_unavailable")
    return {
        "valid": not reasons,
        "refusals": reasons,
        "commands": receipts,
        "endpoint": endpoint,
        "inspection": inspection,
        "chat_template": chat_template,
    }


@dataclass(frozen=True, slots=True)
class CliConfig:
    live: bool
    smoke_no_contact: bool
    evidence_dir: Path | None
    tokenizer_json: Path | None


def parse_cli(argv: list[str] | None = None) -> CliConfig:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--live", action="store_true", help="execute the separately authorized live packet")
    modes.add_argument("--smoke-no-contact", action="store_true", help="verify module launch without contact-adjacent side effects")
    parser.add_argument("--evidence-dir", type=Path)
    parser.add_argument("--tokenizer-json", type=Path)
    args = parser.parse_args(argv)
    if args.smoke_no_contact:
        if args.evidence_dir is not None or args.tokenizer_json is not None:
            parser.error("--smoke-no-contact accepts no evidence or tokenizer path")
        return CliConfig(False, True, None, None)
    if not args.live:
        parser.error("no default execution path; --live requires a separate live-contact decision")
    if args.evidence_dir is None or args.tokenizer_json is None:
        parser.error("--live requires --evidence-dir and --tokenizer-json")
    return CliConfig(True, False, args.evidence_dir, args.tokenizer_json)


def main(argv: list[str] | None = None) -> int:
    args = parse_cli(argv)
    if args.smoke_no_contact:
        print(canonical_json_bytes(SMOKE_RECEIPT).decode("utf-8"))
        return 0
    writer = EvidenceWriter(args.evidence_dir)
    receipt = collect_provider_receipt()
    (args.evidence_dir / "provider.json").write_text(
        json.dumps(receipt, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if not receipt["valid"] or type(receipt["chat_template"]) is not str:
        raise ContactRefusal("provider_preflight_failed")
    counter = PinnedTokenCounter(args.tokenizer_json, receipt["chat_template"])
    packet = run_packet(DockerInvoker(), render_auditor=counter.render_auditor)
    writer.write(packet)
    replay_evidence(args.evidence_dir, counter.render_auditor)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
