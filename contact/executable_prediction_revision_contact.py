"""Run the reviewed executable-prediction revision contact."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import time

from contact.exploratory_developmental_contact import InvocationFailure, ProviderAttempt


PROTOCOL_VERSION = "executable-prediction-revision-contact-v1"
MODEL = "ai/qwen3:14B-Q6_K"
INSPECT_TAG = "docker.io/ai/qwen3:14B-Q6_K"
MODEL_DIGEST = "sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219"
ENDPOINT = "http://localhost:12434/engines/llama.cpp/v1/chat/completions"
DMR_VERSION = "v1.2.6"
DOCKER_DESKTOP_PLATFORM = "Docker Desktop 4.87.0 (236836)"
LLAMA_BACKEND_BUILD = "b9879-metal"
LLAMA_BACKEND_DIGEST = "sha256:b70706f473b4043ca3e0c32704a7fda3412b83bceef0564684187b8011230de8"
CHAT_TEMPLATE_UTF8_LENGTH = 4_100
CHAT_TEMPLATE_SHA256 = "57f1fd00f0013a2be96aa79b857391f27e23df5b5f847072b524c897e24d0361"
DOCKER_ENGINE_VERSION = "29.7.2"
CANONICAL_JSON_VERSION = "executable-prediction-canonical-json-v1"
RECOGNIZER_VERSION = "executable-prediction-rule-recognizer-v1"
EVALUATOR_VERSION = "executable-prediction-rule-evaluator-v1"
WITNESS_VERSION = "executable-prediction-witness-v1"
TEMPLATE_RENDERER_IMPLEMENTATION = "jinja2-3.1.6"

PLANNED_LOGICAL_CALLS = 35
PHYSICAL_CALL_CEILING = 38
PLANNED_COMPLETION_ALLOWANCE = 18_816
PHYSICAL_COMPLETION_CONTINGENCY = 21_888
CASE_MANIFEST_UTF8_LENGTH = 2_473
CASE_MANIFEST_SHA256 = "2a07f9b6b4982af60df69353f5893f04d4fcc9b537140f0226bf9e1eafd2084b"
WITNESS_UTF8_LENGTH = 45_357
WITNESS_SHA256 = "754169a7eeb1ab36ce3a0172551022c48fd2d16dd9b76152b0b52847ba11333e"
STATIC_RULE_SHA256 = {
    "J": "f315863c5f69ced00aadd5f03c5e5e18fba8ec94bb17dbba0156149621d9a7c8",
    "K": "6d366d96ce11104227d63ef08b7335190c49d31456eed026db23e07dda79d521",
}

ORDINARY_SETTINGS = {
    "max_tokens": 512,
    "stream": False,
    "temperature": 0.6,
    "top_p": 0.95,
}
ACQUISITION_SETTINGS = {
    **ORDINARY_SETTINGS,
    "max_tokens": 128,
    "response_format": {"type": "json_object"},
}
SAME_RESPONSE_SETTINGS = {
    **ORDINARY_SETTINGS,
    "max_tokens": 1024,
    "response_format": {"type": "json_object"},
}

ACQUISITION_SYSTEM = """You are a cold predictor. You have no memory outside this request. Return one
JSON object with the single key "prediction". Its value must be one token from
the supplied prediction vocabulary. Do not add keys or commentary."""

RULE_SYSTEM_TEMPLATE = """You are the rule-authoring component of a cold practitioner. You have no memory
outside this request.

PUBLIC INPUT FIELDS
facet, mark, zone

PREDICTION VOCABULARY
<PREDICTION_VOCABULARY_JSON>

RULE OUTPUT
Your complete response is one rule. Any response string is a rule with global
scope that predicts that exact string.

To author conditional scope or predictions, respond with RULE_AST_V1 on the
first line followed by one JSON object:
{"when":<boolean-expression>,"predict":<string-expression>}

A string expression is exactly one of:
{"lit":<string>}
{"field":<field-name-string>}
{"if":[<boolean-expression>,<string-expression>,<string-expression>]}

A boolean expression is exactly one of:
{"bool":<true-or-false>}
{"exists":<field-name-string>}
{"eq":[<string-expression>,<string-expression>]}
{"neq":[<string-expression>,<string-expression>]}
{"and":[<boolean-expression>,<boolean-expression>]}
{"or":[<boolean-expression>,<boolean-expression>]}
{"not":<boolean-expression>}

Use only public fields and the evidence supplied in this request. Do not add an
explanation outside the rule."""

SAME_RESPONSE_SUFFIX = """SAME-RESPONSE ENVELOPE
Return exactly one JSON object with keys "parent" and "successor" in that order.
Each value must be either a string containing one complete raw rule under RULE
OUTPUT or null for unavailable content. Do not add keys or commentary."""


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_json_bytes(value: object) -> bytes:
    return canonical_json(value).encode("utf-8")


def render_chat(chat_template: str, system: str, user: str) -> str:
    try:
        import jinja2
        from jinja2.sandbox import ImmutableSandboxedEnvironment
    except ImportError as error:
        raise ValueError("jinja2_package_unavailable") from error
    if f"jinja2-{jinja2.__version__}" != TEMPLATE_RENDERER_IMPLEMENTATION:
        raise ValueError("template_renderer_implementation_mismatch")
    environment = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True)
    environment.globals["raise_exception"] = lambda message: (_ for _ in ()).throw(ValueError(message))
    return environment.from_string(chat_template).render(
        messages=(
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ),
        add_generation_prompt=True,
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


@dataclass(frozen=True, slots=True)
class Case:
    coordinate: str
    hidden_role: str
    input: dict[str, str]
    oracle_result: str


@dataclass(frozen=True, slots=True)
class World:
    world: str
    prediction_vocabulary: tuple[str, str]
    cases: tuple[Case, ...]
    static_lesson: str
    visible_parent: str
    visible_coordinate: str

    def case(self, number: int) -> Case:
        return self.cases[number]


WORLD_J = World(
    "J", ("zafren", "ulmec"),
    (
        Case("J0", "acquisition", {"facet": "fira", "mark": "mela", "zone": "zuna"}, "ulmec"),
        Case("J1", "primary_test", {"facet": "fira", "mark": "melo", "zone": "zuna"}, "zafren"),
        Case("J2", "transfer", {"facet": "firo", "mark": "mela", "zone": "zuna"}, "zafren"),
        Case("J3", "transfer", {"facet": "firo", "mark": "melo", "zone": "zuna"}, "ulmec"),
        Case("J4", "non_transfer", {"facet": "fira", "mark": "mela", "zone": "zuno"}, "zafren"),
        Case("J5", "non_transfer", {"facet": "fira", "mark": "melo", "zone": "zuno"}, "ulmec"),
        Case("J6", "copy_control", {"facet": "fira", "mark": "mela", "zone": "zuni"}, "zafren"),
        Case("J7", "copy_control", {"facet": "firo", "mark": "melo", "zone": "zuni"}, "ulmec"),
        Case("J8", "later_revision_test", {"facet": "firo", "mark": "mela", "zone": "zuno"}, "ulmec"),
    ),
    """zone zuna: zafren exactly when exactly one of facet=fira and mark=mela is true;
otherwise ulmec
zone zuno: reverse the zuna result
zone zuni: zafren when facet=fira; otherwise ulmec""",
    "CONTROLJQPXMV", "pvj01",
)
WORLD_K = World(
    "K", ("qoril", "vesan"),
    (
        Case("K0", "acquisition", {"facet": "dara", "mark": "kela", "zone": "puna"}, "vesan"),
        Case("K1", "primary_test", {"facet": "dara", "mark": "kelo", "zone": "puna"}, "qoril"),
        Case("K2", "transfer", {"facet": "daro", "mark": "kela", "zone": "puna"}, "qoril"),
        Case("K3", "transfer", {"facet": "daro", "mark": "kelo", "zone": "puna"}, "vesan"),
        Case("K4", "non_transfer", {"facet": "dara", "mark": "kela", "zone": "puno"}, "qoril"),
        Case("K5", "non_transfer", {"facet": "dara", "mark": "kelo", "zone": "puno"}, "vesan"),
        Case("K6", "copy_control", {"facet": "dara", "mark": "kela", "zone": "puni"}, "qoril"),
        Case("K7", "copy_control", {"facet": "daro", "mark": "kelo", "zone": "puni"}, "vesan"),
        Case("K8", "later_revision_test", {"facet": "daro", "mark": "kela", "zone": "puno"}, "vesan"),
    ),
    """zone puna: qoril exactly when exactly one of facet=dara and mark=kela is true;
otherwise vesan
zone puno: reverse the puna result
zone puni: qoril when facet=dara; otherwise vesan""",
    "CONTROLKZRWHD", "pvk01",
)
WORLDS = (WORLD_J, WORLD_K)
REPORT_CONDITIONS = (
    "parent", "repeated_parent", "selected_successor", "repeated_successor",
    "result_withheld", "parent_withheld", "same_response",
    "repeated_occurrence", "deterministic_restatement", "visible_material",
    "static_instruction", "later_successor", "later_repeated_successor",
    "later_result_withheld", "later_parent_withheld", "later_same_response",
)


def case_manifest() -> dict[str, object]:
    return {
        "protocol_version": "executable-prediction-case-manifest-v1",
        "worlds": [
            {
                "world": world.world,
                "prediction_vocabulary": list(world.prediction_vocabulary),
                "cases": [asdict(case) for case in world.cases],
            }
            for world in WORLDS
        ],
    }


def _selector(public_input: dict[str, str]) -> dict[str, object]:
    comparisons = [
        {"eq": [{"field": key}, {"lit": public_input[key]}]}
        for key in ("facet", "mark", "zone")
    ]
    return {"and": [{"and": comparisons[:2]}, comparisons[2]]}


def _lookup_rule(world: World, second_coordinates: set[str]) -> str:
    prediction: dict[str, object] = {"lit": world.prediction_vocabulary[0]}
    selected = [case for case in world.cases if case.coordinate in second_coordinates]
    for case in reversed(selected):
        prediction = {
            "if": [
                _selector(case.input),
                {"lit": world.prediction_vocabulary[1]},
                prediction,
            ]
        }
    return "RULE_AST_V1\n" + canonical_json(
        {"when": {"bool": True}, "predict": prediction}
    )


def witness_artifact() -> dict[str, object]:
    worlds: list[dict[str, object]] = []
    for world in WORLDS:
        truth = {case.coordinate: case.oracle_result for case in world.cases}
        prefixes = (
            ("after_acquisition", [world.case(0).coordinate]),
            ("after_primary", [world.case(0).coordinate, world.case(1).coordinate]),
            ("after_later", [world.case(0).coordinate, world.case(1).coordinate, world.case(8).coordinate]),
        )
        pairs: list[dict[str, object]] = []
        for prefix, revealed in prefixes:
            base = {
                coordinate for coordinate in revealed
                if truth[coordinate] == world.prediction_vocabulary[1]
            }
            for number in range(2, 8):
                heldout = world.case(number).coordinate
                left_raw = _lookup_rule(world, base)
                right_raw = _lookup_rule(world, base | {heldout})
                pairs.append({
                    "heldout": heldout,
                    "left_raw": left_raw,
                    "left_vector": [
                        world.prediction_vocabulary[1] if case.coordinate in base else world.prediction_vocabulary[0]
                        for case in world.cases
                    ],
                    "prefix": prefix,
                    "revealed": revealed,
                    "right_raw": right_raw,
                    "right_vector": [
                        world.prediction_vocabulary[1] if case.coordinate in base | {heldout} else world.prediction_vocabulary[0]
                        for case in world.cases
                    ],
                })
        second = {
            case.coordinate for case in world.cases
            if case.oracle_result == world.prediction_vocabulary[1]
        }
        worlds.append({
            "pairs": pairs,
            "static_rule_raw": _lookup_rule(world, second),
            "static_rule_vector": [case.oracle_result for case in world.cases],
            "world": world.world,
        })
    return {"protocol_version": "executable-prediction-witness-v1", "worlds": worlds}


class DuplicateKey(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKey(key)
        value[key] = item
    return value


def _scalar_string(value: object) -> bool:
    if type(value) is not str:
        return False
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def _string_expr(value: object) -> bool:
    if type(value) is not dict or len(value) != 1:
        return False
    if "lit" in value:
        return _scalar_string(value["lit"])
    if "field" in value:
        return _scalar_string(value["field"])
    if "if" in value:
        args = value["if"]
        return type(args) is list and len(args) == 3 and _bool_expr(args[0]) and _string_expr(args[1]) and _string_expr(args[2])
    return False


def _bool_expr(value: object) -> bool:
    if type(value) is not dict or len(value) != 1:
        return False
    if "bool" in value:
        return type(value["bool"]) is bool
    if "exists" in value:
        return _scalar_string(value["exists"])
    if "not" in value:
        return _bool_expr(value["not"])
    for key in ("eq", "neq"):
        if key in value:
            args = value[key]
            return type(args) is list and len(args) == 2 and all(_string_expr(item) for item in args)
    for key in ("and", "or"):
        if key in value:
            args = value[key]
            return type(args) is list and len(args) == 2 and all(_bool_expr(item) for item in args)
    return False


@dataclass(frozen=True, slots=True)
class Rule:
    raw: str
    kind: str
    tree: dict[str, object] | None


def recognize_rule(content: object) -> Rule | None:
    if not _scalar_string(content):
        return None
    assert type(content) is str
    marker = "RULE_AST_V1\n"
    if content.startswith(marker):
        try:
            tree = json.loads(
                content[len(marker):], object_pairs_hook=_unique_object,
                parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
            )
            if type(tree) is dict and set(tree) == {"when", "predict"} and _bool_expr(tree["when"]) and _string_expr(tree["predict"]):
                return Rule(content, "ast_rule", tree)
        except (json.JSONDecodeError, DuplicateKey, ValueError, RecursionError):
            pass
    return Rule(content, "literal_rule", None)


MISSING = object()
UNKNOWN = object()


def _eval_string(expr: dict[str, object], public_input: dict[str, str]) -> object:
    if "lit" in expr:
        return expr["lit"]
    if "field" in expr:
        return public_input.get(str(expr["field"]), MISSING)
    condition = _eval_bool(expr["if"][0], public_input)  # type: ignore[index]
    if condition is UNKNOWN:
        return UNKNOWN
    return _eval_string(expr["if"][1 if condition else 2], public_input)  # type: ignore[index]


def _eval_bool(expr: dict[str, object], public_input: dict[str, str]) -> object:
    if "bool" in expr:
        return expr["bool"]
    if "exists" in expr:
        return expr["exists"] in public_input
    if "not" in expr:
        value = _eval_bool(expr["not"], public_input)  # type: ignore[arg-type]
        return UNKNOWN if value is UNKNOWN else not value
    for key in ("eq", "neq"):
        if key in expr:
            left = _eval_string(expr[key][0], public_input)  # type: ignore[index]
            right = _eval_string(expr[key][1], public_input)  # type: ignore[index]
            if MISSING in (left, right) or UNKNOWN in (left, right):
                return UNKNOWN
            equal = left == right
            return equal if key == "eq" else not equal
    key = "and" if "and" in expr else "or"
    left = _eval_bool(expr[key][0], public_input)  # type: ignore[index]
    right = _eval_bool(expr[key][1], public_input)  # type: ignore[index]
    if key == "and":
        if left is False or right is False:
            return False
        if left is UNKNOWN or right is UNKNOWN:
            return UNKNOWN
        return True
    if left is True or right is True:
        return True
    if left is UNKNOWN or right is UNKNOWN:
        return UNKNOWN
    return False


def evaluate_rule(rule: Rule | None, public_input: dict[str, str]) -> dict[str, object]:
    if rule is None:
        return {"status": "rule_unavailable", "value": None}
    if rule.kind == "literal_rule":
        return {"status": "prediction", "value": rule.raw}
    assert rule.tree is not None
    when = _eval_bool(rule.tree["when"], public_input)  # type: ignore[arg-type]
    if when is False:
        return {"status": "out_of_scope", "value": None}
    if when is UNKNOWN:
        return {"status": "evaluation_unavailable", "value": None}
    value = _eval_string(rule.tree["predict"], public_input)  # type: ignore[arg-type]
    if value is MISSING or value is UNKNOWN:
        return {"status": "evaluation_unavailable", "value": None}
    return {"status": "prediction", "value": value}


def rule_vector(rule: Rule | None, world: World) -> list[dict[str, object]]:
    return [evaluate_rule(rule, case.input) for case in world.cases]


def acquisition_prompt(public_input: dict[str, str], vocabulary: tuple[str, str]) -> str:
    return f"""PUBLIC INPUT
{canonical_json(public_input)}

PREDICTION VOCABULARY
{canonical_json(list(vocabulary))}

Choose one prediction.
/no_think"""


def rule_system(world: World) -> str:
    return RULE_SYSTEM_TEMPLATE.replace(
        "<PREDICTION_VOCABULARY_JSON>", canonical_json(list(world.prediction_vocabulary)), 1
    )


def ordinary_prompt(occurrence: dict[str, object], material: dict[str, object]) -> str:
    return f"""FIRST EXPERIENCE
{canonical_json(occurrence)}

RUNTIME MATERIAL
{canonical_json(material)}

AUTHORSHIP RESPONSIBILITY
Author the one prediction rule you can support now from the supplied evidence.
Your complete response becomes the first retained attempt for this condition.
/no_think"""


def same_system(world: World) -> str:
    return rule_system(world) + "\n\n" + SAME_RESPONSE_SUFFIX


def first_same_prompt(world: World, occurrence: dict[str, object]) -> str:
    case = world.case(1)
    primary = {"input": case.input, "result": {"authority": "environment_oracle", "value": case.oracle_result}}
    return f"""FIRST EXPERIENCE
{canonical_json(occurrence)}

PRIMARY EXPERIENCE
{canonical_json(primary)}

SAME-RESPONSE RESPONSIBILITY
First author the parent you would support if PRIMARY EXPERIENCE were absent.
Then author the successor you support using all supplied evidence.
Return both through the required envelope.
/no_think"""


def later_same_prompt(world: World, occurrence: dict[str, object], parent_raw: str | None) -> str:
    case = world.case(8)
    later = {"input": case.input, "result": {"authority": "environment_oracle", "value": case.oracle_result}}
    return f"""FIRST EXPERIENCE
{canonical_json(occurrence)}

CURRENT PARENT
{canonical_json(parent_raw)}

LATER EXPERIENCE
{canonical_json(later)}

SAME-RESPONSE RESPONSIBILITY
Put CURRENT PARENT unchanged in "parent", including JSON null when it is null.
Author one successor using all supplied evidence and put it in "successor".
Return both through the required envelope.
/no_think"""


def static_prompt(world: World) -> str:
    return f"""STATIC LESSON
{world.static_lesson}

AUTHORSHIP RESPONSIBILITY
Author the one prediction rule that expresses STATIC LESSON.
Your complete response becomes the first retained attempt for this condition.
/no_think"""


def base_material() -> dict[str, object]:
    return {
        "additional_experience": None,
        "external_result": {"status": "not_available", "value": None},
        "parent_attempt_coordinate": None,
        "parent_raw": None,
        "test_input": None,
        "trial": {"status": "not_available", "value": None},
    }


def selected_material(parent_coordinate: str, parent_raw: str | None, trial: dict[str, object], case: Case, *, withhold: bool = False) -> dict[str, object]:
    return {
        "additional_experience": None,
        "external_result": {"status": "result_not_revealed", "value": None} if withhold else {"status": "revealed", "value": case.oracle_result},
        "parent_attempt_coordinate": parent_coordinate,
        "parent_raw": parent_raw,
        "test_input": case.input,
        "trial": trial,
    }


def parent_withheld_material(case: Case) -> dict[str, object]:
    return {
        "additional_experience": None,
        "external_result": {"status": "revealed", "value": case.oracle_result},
        "parent_attempt_coordinate": None,
        "parent_raw": None,
        "test_input": case.input,
        "trial": {"status": "not_available", "value": None},
    }


def parse_acquisition(content: object, vocabulary: tuple[str, str]) -> str | None:
    if type(content) is not str:
        return None
    try:
        value = json.loads(content, object_pairs_hook=_unique_object, parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)))
    except (json.JSONDecodeError, DuplicateKey, ValueError):
        return None
    if type(value) is not dict or list(value) != ["prediction"]:
        return None
    prediction = value["prediction"]
    return prediction if type(prediction) is str and prediction in vocabulary else None


def parse_same_response(content: object) -> tuple[object, object] | None:
    if type(content) is not str:
        return None
    try:
        pairs = json.loads(content, object_pairs_hook=lambda items: items, parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)))
    except (json.JSONDecodeError, ValueError):
        return None
    if type(pairs) is not list or [key for key, _ in pairs] != ["parent", "successor"]:
        return None
    values = [value for _, value in pairs]
    if any(value is not None and type(value) is not str for value in values):
        return None
    return values[0], values[1]


@dataclass(frozen=True, slots=True)
class LogicalCall:
    logical_index: int
    call_id: str
    responsibility: str
    envelope: dict[str, object]
    condition: str
    world_id: str | None = None
    runtime_material: dict[str, object] | None = None

    @property
    def request_body(self) -> bytes:
        return canonical_json_bytes(self.envelope)


def _envelope(system: str, user: str, settings: dict[str, object]) -> dict[str, object]:
    return {"model": MODEL, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}], **settings}


def make_call(index: int, condition: str, system: str, user: str, settings: dict[str, object], world: World | None = None) -> LogicalCall:
    return LogicalCall(index, f"iv{index:02d}", "acquisition" if index <= 3 else "rule_authorship", _envelope(system, user, settings), condition, None if world is None else world.world)


class EvidenceWriter:
    def __init__(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=False)
        self.directory = directory
        self.calls = directory / "calls"
        self.calls.mkdir()

    def write_json(self, relative: str, value: object) -> None:
        (self.directory / relative).write_text(json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def write_canonical(self, relative: str, value: object) -> None:
        (self.directory / relative).write_bytes(canonical_json_bytes(value))

    def write_attempt(self, call: LogicalCall, attempt: ProviderAttempt) -> None:
        stem = f"{call.logical_index:02d}-{call.call_id}-a{attempt.attempt_index}"
        (self.calls / f"{stem}.request.json").write_bytes(attempt.request_body)
        (self.calls / f"{stem}.response.json").write_bytes(attempt.response_body)
        choice = attempt.response_envelope.get("choices", [None])[0] if type(attempt.response_envelope) is dict and type(attempt.response_envelope.get("choices")) is list and attempt.response_envelope.get("choices") else None
        self.write_json(f"calls/{stem}.meta.json", {
            "logical_index": call.logical_index, "attempt_index": attempt.attempt_index,
            "call_id": call.call_id, "condition": call.condition, "world_id": call.world_id,
            "request_sha256": sha256_bytes(attempt.request_body), "response_sha256": sha256_bytes(attempt.response_body),
            "response_envelope": attempt.response_envelope, "message": attempt.message,
            "http_status": attempt.http_status, "started_at": attempt.started_at,
            "ended_at": attempt.ended_at, "elapsed_seconds": attempt.elapsed_seconds,
            "error": attempt.error, "retry_of_attempt": attempt.retry_of_attempt,
            "usage": attempt.response_envelope.get("usage") if type(attempt.response_envelope) is dict else None,
            "finish_reason": choice.get("finish_reason") if type(choice) is dict else None,
        })

    def write_logical(self, call: LogicalCall, record: object) -> None:
        self.write_json(f"calls/{call.logical_index:02d}-{call.call_id}.logical.json", record)


Invoker = Callable[[LogicalCall, int], ProviderAttempt]


class ContactStop(RuntimeError):
    pass


class ContactRunner:
    def __init__(self, invoker: Invoker, writer: EvidenceWriter, physical_ceiling: int = PHYSICAL_CALL_CEILING) -> None:
        self.invoker = invoker
        self.writer = writer
        self.physical_ceiling = physical_ceiling
        self.physical_attempts = 0
        self.records: list[dict[str, object]] = []
        self.physical_completion_tokens = 0
        self.logical_completion_tokens = 0

    def _account_usage(self, attempt: ProviderAttempt, *, logical: bool) -> None:
        envelope = attempt.response_envelope
        usage = envelope.get("usage") if type(envelope) is dict else None
        tokens = usage.get("completion_tokens") if type(usage) is dict else None
        if type(tokens) is int and tokens >= 0:
            self.physical_completion_tokens += tokens
            if logical:
                self.logical_completion_tokens += tokens

    def invoke(self, call: LogicalCall) -> ProviderAttempt:
        for attempt_index in (1, 2):
            if self.physical_attempts >= self.physical_ceiling:
                raise ContactStop("physical_call_ceiling_reached")
            self.physical_attempts += 1
            try:
                attempt = self.invoker(call, attempt_index)
            except InvocationFailure as failure:
                attempt = failure.attempt
                if attempt_index == 2:
                    attempt = ProviderAttempt(**{**asdict(attempt), "retry_of_attempt": 1})
                self.writer.write_attempt(call, attempt)
                self._account_usage(attempt, logical=False)
                if failure.retryable and attempt_index == 1:
                    continue
                raise ContactStop(failure.reason) from failure
            if attempt.request_body != call.request_body:
                self.writer.write_attempt(call, attempt)
                raise ContactStop("request_bytes_drifted")
            if attempt_index == 2:
                attempt = ProviderAttempt(**{**asdict(attempt), "retry_of_attempt": 1})
            self.writer.write_attempt(call, attempt)
            self._account_usage(attempt, logical=True)
            return attempt
        raise AssertionError("unreachable")

    def record(self, call: LogicalCall, attempt: ProviderAttempt, record: dict[str, object]) -> dict[str, object]:
        trial_receipt = None
        consequence_receipt = None
        if call.runtime_material is not None:
            material = call.runtime_material
            if material.get("test_input") is not None and material.get("trial") != {"status": "not_available", "value": None}:
                trial_receipt = {
                    "authority": "rule_evaluator",
                    "evaluator_version": EVALUATOR_VERSION,
                    "input": material["test_input"],
                    "observation": material["trial"],
                }
            external = material.get("external_result")
            if type(external) is dict and external.get("status") in {"revealed", "result_not_revealed"}:
                world = WORLD_J if call.world_id == "J" else WORLD_K
                matching = [case for case in world.cases if case.input == material.get("test_input")]
                if len(matching) == 1:
                    consequence_receipt = {
                        "authority": "environment_oracle",
                        "input": material.get("test_input"),
                        "value": matching[0].oracle_result,
                        "delivered_to_model": external.get("status") == "revealed",
                    }
        complete = {
            "logical_index": call.logical_index,
            "invocation_coordinate": call.call_id,
            "output_coordinate": f"{call.call_id}.content",
            "condition": call.condition,
            "world_id": call.world_id,
            "content": attempt.content,
            "runtime_material": call.runtime_material,
            "trial_receipt": trial_receipt,
            "consequence_receipt": consequence_receipt,
            **record,
        }
        self.records.append(complete)
        self.writer.write_logical(call, complete)
        return complete


def _occurrence(case: Case, prediction: str | None) -> dict[str, object]:
    return {
        "input": case.input,
        "prediction": {"status": "available", "value": prediction} if prediction is not None else {"status": "prediction_unavailable", "value": None},
        "result": {"authority": "environment_oracle", "value": case.oracle_result},
    }


def _ordinary_call(index: int, condition: str, world: World, occurrence: dict[str, object], material: dict[str, object]) -> LogicalCall:
    call = make_call(index, condition, rule_system(world), ordinary_prompt(occurrence, material), ORDINARY_SETTINGS, world)
    return LogicalCall(**{**asdict(call), "runtime_material": material})


def _rule_record(content: object, world: World) -> dict[str, object]:
    rule = recognize_rule(content)
    vector = rule_vector(rule, world)
    correctness = [
        item["status"] == "prediction" and item["value"] == case.oracle_result
        for item, case in zip(vector, world.cases)
    ]
    by_role: dict[str, dict[str, int]] = {}
    for case, correct in zip(world.cases, correctness):
        cell = by_role.setdefault(case.hidden_role, {"correct": 0, "assigned": 0})
        cell["assigned"] += 1
        cell["correct"] += int(correct)
    return {
        "content": content,
        "recognizer_version": RECOGNIZER_VERSION,
        "evaluator_version": EVALUATOR_VERSION,
        "rule": None if rule is None else asdict(rule),
        "recognized_kind": "rule_unavailable" if rule is None else rule.kind,
        "vector": vector,
        "correctness": correctness,
        "correctness_by_role": by_role,
    }


def _invoke_rule(runner: ContactRunner, call: LogicalCall, world: World) -> dict[str, object]:
    attempt = runner.invoke(call)
    return runner.record(call, attempt, _rule_record(attempt.content, world))


def _restatement(world: World) -> str:
    case = world.case(1)
    return f"The public input was {case.input['facet']}, {case.input['mark']}, {case.input['zone']}. The environment result was {case.oracle_result}."


def _pair_projection(parent: dict[str, object] | None, successor: dict[str, object] | None, world: World, test_case_number: int = 1) -> dict[str, object]:
    parent_vector = None if parent is None else parent.get("vector")
    successor_vector = None if successor is None else successor.get("vector")
    changes = []
    role_counts: dict[str, dict[str, int]] = {}
    if type(parent_vector) is list and type(successor_vector) is list:
        for case, left, right in zip(world.cases, parent_vector, successor_vector):
            left_correct = left.get("status") == "prediction" and left.get("value") == case.oracle_result
            right_correct = right.get("status") == "prediction" and right.get("value") == case.oracle_result
            became_out = left.get("status") == "prediction" and right.get("status") == "out_of_scope"
            became_claimed = left.get("status") == "out_of_scope" and right.get("status") == "prediction"
            item = {
                "coordinate": case.coordinate, "hidden_role": case.hidden_role,
                "parent": left, "successor": right, "changed": left != right,
                "oracle_result": case.oracle_result,
                "parent_correct": left_correct, "successor_correct": right_correct,
                "wrong_or_unavailable_to_correct": not left_correct and right_correct,
                "correct_to_wrong_or_out_of_scope": left_correct and not right_correct,
                "became_out_of_scope": became_out, "became_claimed": became_claimed,
            }
            changes.append(item)
            counts = role_counts.setdefault(case.hidden_role, {
                "assigned": 0, "parent_correct": 0, "successor_correct": 0,
                "changed": 0, "wrong_or_unavailable_to_correct": 0,
                "correct_to_wrong_or_out_of_scope": 0,
                "became_out_of_scope": 0, "became_claimed": 0,
            })
            counts["assigned"] += 1
            for key in tuple(counts)[1:]:
                counts[key] += int(item[key])
    parent_rule = None if parent is None else parent.get("rule")
    successor_rule = None if successor is None else successor.get("rule")
    test_parent = None if parent_vector is None else parent_vector[test_case_number]
    parent_test_in_scope = type(test_parent) is dict and test_parent.get("status") == "prediction"
    return {
        "parent_available": parent is not None and parent.get("recognized_kind") != "rule_unavailable",
        "successor_available": successor is not None and successor.get("recognized_kind") != "rule_unavailable",
        "raw_equal": None if parent is None or successor is None else parent.get("content") == successor.get("content"),
        "recognized_form_equal": None if parent_rule is None or successor_rule is None else parent_rule == successor_rule,
        "ast_equal": None if parent is None or successor is None or parent.get("recognized_kind") != "ast_rule" or successor.get("recognized_kind") != "ast_rule" else parent_rule == successor_rule,
        "vector_equal": None if parent_vector is None or successor_vector is None else parent_vector == successor_vector,
        "parent_test_in_scope": parent_test_in_scope,
        "parent_test_prediction_differed_from_result": parent_test_in_scope and test_parent.get("value") != world.case(test_case_number).oracle_result,
        "parent_test_prediction_equaled_result": parent_test_in_scope and test_parent.get("value") == world.case(test_case_number).oracle_result,
        "test_coordinate": world.case(test_case_number).coordinate,
        "role_counts": role_counts,
        "changes": changes,
    }


def _validate_frozen_artifacts() -> tuple[dict[str, object], dict[str, object]]:
    manifest = case_manifest()
    witness = witness_artifact()
    manifest_bytes = canonical_json_bytes(manifest)
    witness_bytes = canonical_json_bytes(witness)
    if len(manifest_bytes) != CASE_MANIFEST_UTF8_LENGTH or sha256_bytes(manifest_bytes) != CASE_MANIFEST_SHA256:
        raise ValueError("case_manifest_binding_mismatch")
    if len(witness_bytes) != WITNESS_UTF8_LENGTH or sha256_bytes(witness_bytes) != WITNESS_SHA256:
        raise ValueError("witness_binding_mismatch")
    for world_data in witness["worlds"]:  # type: ignore[index]
        world = WORLD_J if world_data["world"] == "J" else WORLD_K
        if sha256_bytes(world_data["static_rule_raw"].encode("utf-8")) != STATIC_RULE_SHA256[world.world]:
            raise ValueError("static_rule_binding_mismatch")
        for pair in world_data["pairs"]:
            left = recognize_rule(pair["left_raw"])
            right = recognize_rule(pair["right_raw"])
            if [item["value"] for item in rule_vector(left, world)] != pair["left_vector"] or [item["value"] for item in rule_vector(right, world)] != pair["right_vector"]:
                raise ValueError("witness_evaluation_mismatch")
            revealed = set(pair["revealed"])
            for case, left_value, right_value in zip(world.cases, pair["left_vector"], pair["right_vector"]):
                if case.coordinate in revealed and (left_value != case.oracle_result or right_value != case.oracle_result):
                    raise ValueError("witness_prefix_disagreement")
            heldout_index = int(pair["heldout"][1:])
            if pair["left_vector"][heldout_index] == pair["right_vector"][heldout_index]:
                raise ValueError("witness_heldout_agreement")
    return manifest, witness


def _run_world_first_cycle(runner: ContactRunner, world: World, occurrence: dict[str, object], parent: dict[str, object], start: int) -> dict[str, dict[str, object]]:
    primary = world.case(1)
    parent_rule = recognize_rule(parent.get("content"))
    trial = evaluate_rule(parent_rule, primary.input)
    parent_coordinate = str(parent["output_coordinate"])
    selected_mat = selected_material(parent_coordinate, parent.get("content") if type(parent.get("content")) is str else None, trial, primary)
    selected = _invoke_rule(runner, _ordinary_call(start, "selected_successor", world, occurrence, selected_mat), world)
    repeated = _invoke_rule(runner, _ordinary_call(start + 1, "repeated_successor", world, occurrence, selected_mat), world)
    withheld = _invoke_rule(runner, _ordinary_call(start + 2, "result_withheld", world, occurrence, selected_material(parent_coordinate, selected_mat["parent_raw"], trial, primary, withhold=True)), world)
    no_parent = _invoke_rule(runner, _ordinary_call(start + 3, "parent_withheld", world, occurrence, parent_withheld_material(primary)), world)
    same_call = make_call(start + 4, "same_response", same_system(world), first_same_prompt(world, occurrence), SAME_RESPONSE_SETTINGS, world)
    same_attempt = runner.invoke(same_call)
    parsed_same = parse_same_response(same_attempt.content)
    same_record: dict[str, object] = {
        "output_coordinate": None,
        "output_coordinates": {"parent": f"iv{start + 4:02d}.parent", "successor": f"iv{start + 4:02d}.successor"},
        "consequence_receipt": {"authority": "environment_oracle", "input": primary.input, "value": primary.oracle_result},
        "envelope_available": parsed_same is not None, "parent": None, "successor": None,
    }
    if parsed_same is not None:
        same_record["parent"] = _rule_record(parsed_same[0], world)
        same_record["successor"] = _rule_record(parsed_same[1], world)
    same = runner.record(same_call, same_attempt, same_record)
    repeated_material = base_material()
    repeated_material["additional_experience"] = occurrence
    repeated_occurrence = _invoke_rule(runner, _ordinary_call(start + 5, "repeated_occurrence", world, occurrence, repeated_material), world)
    restatement_material = base_material()
    restatement_material["additional_experience"] = _restatement(world)
    restatement = _invoke_rule(runner, _ordinary_call(start + 6, "deterministic_restatement", world, occurrence, restatement_material), world)
    visible_trial = {"status": "prediction", "value": world.visible_parent}
    visible = _invoke_rule(runner, _ordinary_call(start + 7, "visible_material", world, occurrence, selected_material(world.visible_coordinate, world.visible_parent, visible_trial, primary)), world)
    static_call = make_call(start + 8, "static_instruction", rule_system(world), static_prompt(world), ORDINARY_SETTINGS, world)
    static = _invoke_rule(runner, static_call, world)
    return {"selected": selected, "repeated": repeated, "withheld": withheld, "parent_withheld": no_parent, "same": same, "repeated_occurrence": repeated_occurrence, "restatement": restatement, "visible": visible, "static": static}


def _run_later_cycle(runner: ContactRunner, world: World, occurrence: dict[str, object], selected: dict[str, object], start: int) -> dict[str, dict[str, object]]:
    later = world.case(8)
    selected_rule = recognize_rule(selected.get("content"))
    trial = evaluate_rule(selected_rule, later.input)
    raw = selected.get("content") if type(selected.get("content")) is str else None
    parent_coordinate = str(selected["output_coordinate"])
    material = selected_material(parent_coordinate, raw, trial, later)
    successor = _invoke_rule(runner, _ordinary_call(start, "later_successor", world, occurrence, material), world)
    repeated = _invoke_rule(runner, _ordinary_call(start + 1, "later_repeated_successor", world, occurrence, material), world)
    withheld = _invoke_rule(runner, _ordinary_call(start + 2, "later_result_withheld", world, occurrence, selected_material(parent_coordinate, raw, trial, later, withhold=True)), world)
    no_parent = _invoke_rule(runner, _ordinary_call(start + 3, "later_parent_withheld", world, occurrence, parent_withheld_material(later)), world)
    same_call = make_call(start + 4, "later_same_response", same_system(world), later_same_prompt(world, occurrence, raw), SAME_RESPONSE_SETTINGS, world)
    attempt = runner.invoke(same_call)
    parsed = parse_same_response(attempt.content)
    same_record: dict[str, object] = {
        "output_coordinate": None,
        "output_coordinates": {"parent": f"iv{start + 4:02d}.parent", "successor": f"iv{start + 4:02d}.successor"},
        "consequence_receipt": {"authority": "environment_oracle", "input": later.input, "value": later.oracle_result},
        "envelope_available": parsed is not None, "parent": None, "successor": None,
    }
    if parsed is not None:
        same_record["parent"] = _rule_record(parsed[0], world)
        same_record["successor"] = _rule_record(parsed[1], world)
    same = runner.record(same_call, attempt, same_record)
    return {"selected": successor, "repeated": repeated, "withheld": withheld, "parent_withheld": no_parent, "same": same}


def _condition_report(records: list[dict[str, object]]) -> list[dict[str, object]]:
    report = []
    for name in REPORT_CONDITIONS:
        members = [record for record in records if record.get("condition") == name]
        report.append({
            "condition": name,
            "assigned_world_units": 2,
            "completed_count": len(members),
            "content_available_count": sum(type(record.get("content")) is str for record in members),
            "literal_rule_count": sum(record.get("recognized_kind") == "literal_rule" for record in members),
            "ast_rule_count": sum(record.get("recognized_kind") == "ast_rule" for record in members),
        })
    return report


def _world_condition_report(records: list[dict[str, object]]) -> list[dict[str, object]]:
    report: list[dict[str, object]] = []
    for condition in REPORT_CONDITIONS:
        for world in ("J", "K"):
            members = [record for record in records if record.get("condition") == condition and record.get("world_id") == world]
            record = members[0] if len(members) == 1 else None
            report.append({
                "condition": condition,
                "world": world,
                "assigned": 1,
                "completed": record is not None,
                "invocation_coordinate": None if record is None else record.get("invocation_coordinate"),
                "output_coordinate": None if record is None else record.get("output_coordinate"),
                "recognized_kind": None if record is None else record.get("recognized_kind"),
                "vector": None if record is None else record.get("vector"),
                "correctness_by_role": None if record is None else record.get("correctness_by_role"),
                "same_response_parent": None if record is None else record.get("parent"),
                "same_response_successor": None if record is None else record.get("successor"),
            })
    return report


def _atomic_fact_report(records: list[dict[str, object]], comparisons: list[dict[str, object]]) -> list[dict[str, object]]:
    boolean_keys = (
        "parent_available", "successor_available", "raw_equal",
        "recognized_form_equal", "ast_equal", "vector_equal",
        "parent_test_in_scope", "parent_test_prediction_differed_from_result",
        "parent_test_prediction_equaled_result", "comparator_vector_equal_selected",
        "complete_vector_equal_selected",
    )
    output = []
    for condition in REPORT_CONDITIONS:
        members = [record for record in records if record.get("condition") == condition]
        compared = [item for item in comparisons if item.get("condition") == condition]
        facts: dict[str, dict[str, int]] = {
            "completed": {"count": len(members), "assigned_world_units": 2},
            "provider_content_available": {"count": sum(type(item.get("content")) is str for item in members), "assigned_world_units": 2},
            "literal_rule": {"count": sum(item.get("recognized_kind") == "literal_rule" for item in members), "assigned_world_units": 2},
            "ast_rule": {"count": sum(item.get("recognized_kind") == "ast_rule" for item in members), "assigned_world_units": 2},
            "rule_unavailable": {"count": sum(item.get("recognized_kind") == "rule_unavailable" for item in members), "assigned_world_units": 2},
        }
        if condition in {"same_response", "later_same_response"}:
            for slot in ("parent", "successor"):
                for kind in ("literal_rule", "ast_rule", "rule_unavailable"):
                    facts[f"{slot}_{kind}"] = {
                        "count": sum(
                            (type(item.get(slot)) is not dict and kind == "rule_unavailable")
                            or (type(item.get(slot)) is dict and item[slot].get("recognized_kind") == kind)
                            for item in members
                        ),
                        "assigned_world_units": 2,
                    }
        for key in boolean_keys:
            facts[key] = {"count": sum(item.get(key) is True for item in compared), "assigned_world_units": 2}
        role_sums: dict[str, int] = {}
        for item in compared:
            for role, counts in item.get("role_counts", {}).items():
                for key, value in counts.items():
                    role_sums[f"{role}.{key}"] = role_sums.get(f"{role}.{key}", 0) + value
        output.append({
            "condition": condition,
            "assigned_world_units": 2,
            "facts": facts,
            "per_role_sums": {key: {"sum": value, "assigned_world_units": 2} for key, value in sorted(role_sums.items())},
        })
    return output


def protocol_record() -> dict[str, object]:
    return {
        "protocol": PROTOCOL_VERSION, "model": MODEL, "inspect_tag": INSPECT_TAG,
        "model_digest": MODEL_DIGEST, "endpoint": ENDPOINT,
        "ordinary_settings": ORDINARY_SETTINGS, "acquisition_settings": ACQUISITION_SETTINGS,
        "same_response_settings": SAME_RESPONSE_SETTINGS,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_completion_allowance": PLANNED_COMPLETION_ALLOWANCE,
        "physical_completion_contingency": PHYSICAL_COMPLETION_CONTINGENCY,
        "instrument_versions": {
            "canonical_json": CANONICAL_JSON_VERSION,
            "rule_recognizer": RECOGNIZER_VERSION,
            "rule_evaluator": EVALUATOR_VERSION,
            "witness_constructor": WITNESS_VERSION,
        },
        "invocation_coordinates": [f"iv{index:02d}" for index in range(1, 36)],
        "terminal_summary": {"formation_verdict": None, "validation_verdict": None},
    }


def protocol_proposals(witness: dict[str, object]) -> dict[str, object]:
    static_by_world = {item["world"]: item for item in witness["worlds"]}
    visible = []
    static = []
    for world in WORLDS:
        rule = recognize_rule(world.visible_parent)
        trial = evaluate_rule(rule, world.case(1).input)
        visible.append({
            "proposal_coordinate": world.visible_coordinate,
            "author": "deterministic_protocol_constructor",
            "raw": world.visible_parent,
            "recognized_rule": None if rule is None else asdict(rule),
            "recognizer_version": RECOGNIZER_VERSION,
            "trial_receipt": {
                "authority": "rule_evaluator", "evaluator_version": EVALUATOR_VERSION,
                "input": world.case(1).input, "observation": trial,
            },
            "consequence_receipt": {
                "authority": "environment_oracle", "input": world.case(1).input,
                "value": world.case(1).oracle_result,
            },
        })
        item = static_by_world[world.world]
        static.append({
            "proposal_coordinate": "svj01" if world.world == "J" else "svk01",
            "author": "deterministic_protocol_constructor",
            "raw": item["static_rule_raw"], "vector": item["static_rule_vector"],
            "recognizer_version": RECOGNIZER_VERSION, "evaluator_version": EVALUATOR_VERSION,
        })
    return {"visible_material": visible, "static_rule_ceiling": static}


class RetainedReplayInvoker:
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.meta: dict[tuple[int, int], dict[str, object]] = {}
        for path in (directory / "calls").glob("*.meta.json"):
            value = json.loads(path.read_text())
            self.meta[(value["logical_index"], value["attempt_index"])] = value

    def __call__(self, call: LogicalCall, attempt_index: int) -> ProviderAttempt:
        meta = self.meta[(call.logical_index, attempt_index)]
        stem = f"{call.logical_index:02d}-{call.call_id}-a{attempt_index}"
        body = (self.directory / "calls" / f"{stem}.response.json").read_bytes()
        try:
            envelope = json.loads(body)
            choices = envelope.get("choices") if type(envelope) is dict else None
            message = choices[0].get("message") if type(choices) is list and choices and type(choices[0]) is dict else None
            content = message.get("content") if type(message) is dict else None
        except (json.JSONDecodeError, UnicodeDecodeError):
            envelope, message, content = meta.get("response_envelope"), meta.get("message"), None
        attempt = ProviderAttempt(
            call.logical_index, attempt_index, call.call_id, call.request_body,
            body, envelope, message, content, meta.get("http_status"),
            str(meta.get("started_at")), str(meta.get("ended_at")),
            float(meta.get("elapsed_seconds", 0.0)), meta.get("error"),
            meta.get("retry_of_attempt"),
        )
        if meta.get("error") is not None:
            reason = str(meta["error"])
            raise InvocationFailure(reason, attempt, reason == "transport_failure" and meta.get("http_status") is None)
        return attempt


def _replay_semantic_audit(directory: Path) -> dict[str, object]:
    comparisons: list[dict[str, object]] = []
    try:
        provider = json.loads((directory / "provider.json").read_text())
        actual_summary = json.loads((directory / "summary.json").read_text())
        with tempfile.TemporaryDirectory(prefix="formation-epr-integrity-") as temporary:
            expected = Path(temporary) / "expected"
            run_contact(
                RetainedReplayInvoker(directory), expected, provider,
                physical_ceiling=actual_summary.get("physical_call_ceiling", PHYSICAL_CALL_CEILING),
                perform_integrity=False,
            )
            for pattern in ("*.request.json", "*.logical.json"):
                actual_paths = sorted((directory / "calls").glob(pattern))
                expected_paths = sorted((expected / "calls").glob(pattern))
                names_equal = [path.name for path in actual_paths] == [path.name for path in expected_paths]
                values_equal = names_equal and all(
                    actual.read_bytes() == regenerated.read_bytes()
                    for actual, regenerated in zip(actual_paths, expected_paths)
                )
                comparisons.append({"surface": pattern, "valid": values_equal})
            for relative in ("protocol-proposals.json", "summary.json"):
                actual = json.loads((directory / relative).read_text())
                regenerated = json.loads((expected / relative).read_text())
                comparisons.append({"surface": relative, "valid": actual == regenerated})
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ContactStop, InvocationFailure):
        comparisons.append({"surface": "replay", "valid": False})
    return {"valid": bool(comparisons) and all(item["valid"] for item in comparisons), "comparisons": comparisons}


def integrity_audit(directory: Path) -> dict[str, object]:
    checks: list[dict[str, object]] = []
    valid = True
    for meta_path in sorted((directory / "calls").glob("*.meta.json")):
        meta = json.loads(meta_path.read_text())
        stem = meta_path.name.removesuffix(".meta.json")
        request = (directory / "calls" / f"{stem}.request.json").read_bytes()
        response = (directory / "calls" / f"{stem}.response.json").read_bytes()
        item_valid = sha256_bytes(request) == meta["request_sha256"] and sha256_bytes(response) == meta["response_sha256"]
        valid = valid and item_valid
        checks.append({"stem": stem, "valid": item_valid})
    artifact_checks = {
        "case_manifest": len((directory / "case-manifest.json").read_bytes()) == CASE_MANIFEST_UTF8_LENGTH and sha256_bytes((directory / "case-manifest.json").read_bytes()) == CASE_MANIFEST_SHA256,
        "witness": len((directory / "witness.json").read_bytes()) == WITNESS_UTF8_LENGTH and sha256_bytes((directory / "witness.json").read_bytes()) == WITNESS_SHA256,
    }
    binding_checks: list[dict[str, object]] = []
    try:
        bindings = json.loads((directory / "integrity-bindings.json").read_text())
        for relative, expected in bindings["sha256"].items():
            path = directory / relative
            item_valid = path.is_file() and sha256_bytes(path.read_bytes()) == expected
            binding_checks.append({"path": relative, "valid": item_valid})
            valid = valid and item_valid
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        valid = False
    semantic_checks: list[dict[str, object]] = []
    logical_records = []
    for path in sorted((directory / "calls").glob("*.logical.json")):
        try:
            record = json.loads(path.read_text())
            logical_records.append(record)
            item_valid = record.get("invocation_coordinate") == f"iv{record['logical_index']:02d}"
            world = WORLD_J if record.get("world_id") == "J" else WORLD_K if record.get("world_id") == "K" else None
            if world is not None and "recognized_kind" in record:
                recomputed = _rule_record(record.get("content"), world)
                item_valid = item_valid and all(record.get(key) == recomputed.get(key) for key in ("rule", "recognized_kind", "vector", "correctness", "correctness_by_role"))
            material = record.get("runtime_material")
            if world is not None and type(material) is dict and material.get("test_input") is not None and material.get("parent_attempt_coordinate") is not None:
                expected_trial = evaluate_rule(recognize_rule(material.get("parent_raw")), material["test_input"])
                item_valid = item_valid and material.get("trial") == expected_trial
            semantic_checks.append({"path": str(path.relative_to(directory)), "valid": item_valid})
            valid = valid and item_valid
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            semantic_checks.append({"path": str(path.relative_to(directory)), "valid": False})
            valid = False
    try:
        summary = json.loads((directory / "summary.json").read_text())
        summary_valid = (
            summary.get("formation_verdict") is None
            and summary.get("validation_verdict") is None
            and summary.get("completed_logical_calls") == len(logical_records)
            and summary.get("condition_report") == _condition_report(logical_records)
            and summary.get("world_condition_report") == _world_condition_report(logical_records)
            and summary.get("atomic_fact_report") == _atomic_fact_report(logical_records, summary.get("comparisons", []))
        )
    except (OSError, json.JSONDecodeError):
        summary_valid = False
    semantic_checks.append({"path": "summary.json:recomputed", "valid": summary_valid})
    replay = _replay_semantic_audit(directory)
    valid = valid and summary_valid and all(artifact_checks.values()) and replay["valid"]
    return {"valid": valid, "attempts_checked": len(checks), "checks": checks, "artifact_checks": artifact_checks, "binding_checks": binding_checks, "semantic_checks": semantic_checks, "replay": replay}


def write_integrity_bindings(directory: Path, writer: EvidenceWriter) -> dict[str, object]:
    paths = ["protocol.json", "provider.json", "case-manifest.json", "witness.json", "protocol-proposals.json", "summary.json"]
    paths.extend(str(path.relative_to(directory)) for path in sorted((directory / "calls").glob("*")) if path.is_file())
    value = {"sha256": {relative: sha256_bytes((directory / relative).read_bytes()) for relative in paths}}
    writer.write_json("integrity-bindings.json", value)
    return value


def run_contact(invoker: Invoker, directory: Path, provider_receipt: dict[str, object], physical_ceiling: int = PHYSICAL_CALL_CEILING, *, perform_integrity: bool = True) -> dict[str, object]:
    writer = EvidenceWriter(directory)
    manifest, witness = _validate_frozen_artifacts()
    writer.write_json("protocol.json", protocol_record())
    writer.write_json("provider.json", provider_receipt)
    writer.write_canonical("case-manifest.json", manifest)
    writer.write_canonical("witness.json", witness)
    writer.write_json("protocol-proposals.json", protocol_proposals(witness))
    runner = ContactRunner(invoker, writer, physical_ceiling)
    state, stop_reason = "completed", None
    world_data: dict[str, dict[str, object]] = {}
    comparisons: list[dict[str, object]] = []
    try:
        if provider_receipt.get("valid") is not True:
            raise ContactStop("provider_receipt_invalid")
        interface_input = {"facet": "sava", "mark": "temi", "zone": "woku"}
        interface_call = make_call(1, "disposable_interface", ACQUISITION_SYSTEM, acquisition_prompt(interface_input, ("bren", "cavo")), ACQUISITION_SETTINGS)
        interface_attempt = runner.invoke(interface_call)
        interface_prediction = parse_acquisition(interface_attempt.content, ("bren", "cavo"))
        runner.record(interface_call, interface_attempt, {"output_coordinate": "iv01.prediction", "prediction": interface_prediction, "available": interface_prediction is not None})
        if interface_prediction is None:
            raise ContactStop("disposable_interface_unavailable")

        for index, world in ((2, WORLD_J), (3, WORLD_K)):
            case = world.case(0)
            call = make_call(index, "acquisition", ACQUISITION_SYSTEM, acquisition_prompt(case.input, world.prediction_vocabulary), ACQUISITION_SETTINGS, world)
            attempt = runner.invoke(call)
            prediction = parse_acquisition(attempt.content, world.prediction_vocabulary)
            occurrence = _occurrence(case, prediction)
            record = runner.record(call, attempt, {"output_coordinate": f"iv{index:02d}.prediction", "prediction": prediction, "available": prediction is not None, "occurrence": occurrence})
            world_data[world.world] = {"occurrence": occurrence, "acquisition": record}

        parents: dict[str, dict[str, object]] = {}
        for index, world in ((4, WORLD_J), (5, WORLD_K)):
            parents[world.world] = _invoke_rule(runner, _ordinary_call(index, "parent", world, world_data[world.world]["occurrence"], base_material()), world)
        for index, world in ((6, WORLD_J), (7, WORLD_K)):
            repeated = _invoke_rule(runner, _ordinary_call(index, "repeated_parent", world, world_data[world.world]["occurrence"], base_material()), world)
            comparisons.append({"world": world.world, "condition": "repeated_parent", **_pair_projection(parents[world.world], repeated, world)})

        first_j = _run_world_first_cycle(runner, WORLD_J, world_data["J"]["occurrence"], parents["J"], 8)
        first_k = _run_world_first_cycle(runner, WORLD_K, world_data["K"]["occurrence"], parents["K"], 17)
        first = {"J": first_j, "K": first_k}
        for world in WORLDS:
            bundle = first[world.world]
            comparisons.append({"world": world.world, "condition": "selected_successor", **_pair_projection(parents[world.world], bundle["selected"], world)})
            comparisons.append({"world": world.world, "condition": "repeated_successor", **_pair_projection(bundle["selected"], bundle["repeated"], world)})
            comparisons.append({"world": world.world, "condition": "result_withheld", **_pair_projection(parents[world.world], bundle["withheld"], world)})
            visible_parent = {"content": world.visible_parent, **_rule_record(world.visible_parent, world)}
            comparisons.append({"world": world.world, "condition": "visible_material", **_pair_projection(visible_parent, bundle["visible"], world)})
            for key in ("parent_withheld", "repeated_occurrence", "restatement", "static"):
                name = {"restatement": "deterministic_restatement", "static": "static_instruction"}.get(key, key)
                comparisons.append({"world": world.world, "condition": name, "comparator_vector_equal_selected": bundle[key].get("vector") == bundle["selected"].get("vector")})
            same_parent = bundle["same"].get("parent")
            same_successor = bundle["same"].get("successor")
            comparisons.append({
                "world": world.world, "condition": "same_response",
                **_pair_projection(same_parent if type(same_parent) is dict else None, same_successor if type(same_successor) is dict else None, world),
                "complete_vector_equal_selected": type(same_successor) is dict and same_successor.get("vector") == bundle["selected"].get("vector"),
            })

        later_j = _run_later_cycle(runner, WORLD_J, world_data["J"]["occurrence"], first_j["selected"], 26)
        later_k = _run_later_cycle(runner, WORLD_K, world_data["K"]["occurrence"], first_k["selected"], 31)
        for world, bundle in ((WORLD_J, later_j), (WORLD_K, later_k)):
            parent = first[world.world]["selected"]
            comparisons.append({"world": world.world, "condition": "later_successor", **_pair_projection(parent, bundle["selected"], world, 8)})
            comparisons.append({"world": world.world, "condition": "later_repeated_successor", **_pair_projection(bundle["selected"], bundle["repeated"], world, 8)})
            comparisons.append({"world": world.world, "condition": "later_result_withheld", **_pair_projection(parent, bundle["withheld"], world, 8)})
            comparisons.append({"world": world.world, "condition": "later_parent_withheld", "comparator_vector_equal_selected": bundle["parent_withheld"].get("vector") == bundle["selected"].get("vector")})
            same_parent = bundle["same"].get("parent")
            same_successor = bundle["same"].get("successor")
            comparisons.append({
                "world": world.world, "condition": "later_same_response",
                **_pair_projection(same_parent if type(same_parent) is dict else None, same_successor if type(same_successor) is dict else None, world, 8),
                "complete_vector_equal_selected": type(same_successor) is dict and same_successor.get("vector") == bundle["selected"].get("vector"),
            })
    except ContactStop as stop:
        state, stop_reason = "stopped", str(stop)

    summary = {
        "protocol": PROTOCOL_VERSION, "evidence_class": "exploratory_observation_only",
        "contact_state": state, "stop_reason": stop_reason, "model": MODEL,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "completed_logical_calls": len(runner.records),
        "physical_call_ceiling": physical_ceiling,
        "physical_attempts": runner.physical_attempts,
        "completion_usage": {
            "logical_completion_tokens": runner.logical_completion_tokens,
            "physical_completion_tokens": runner.physical_completion_tokens,
            "planned_logical_allowance": PLANNED_COMPLETION_ALLOWANCE,
            "physical_contingency_ceiling": PHYSICAL_COMPLETION_CONTINGENCY,
        },
        "condition_report": _condition_report(runner.records),
        "world_condition_report": _world_condition_report(runner.records),
        "atomic_fact_report": _atomic_fact_report(runner.records, comparisons),
        "comparisons": comparisons,
        "static_rule_ceiling": [
            {"world": item["world"], "proposal_coordinate": "svj01" if item["world"] == "J" else "svk01", "raw_sha256": STATIC_RULE_SHA256[item["world"]], "vector": item["static_rule_vector"]}
            for item in witness["worlds"]
        ],
        "formation_verdict": None, "validation_verdict": None,
    }
    writer.write_json("summary.json", summary)
    if not perform_integrity:
        return summary
    write_integrity_bindings(directory, writer)
    audit = integrity_audit(directory)
    writer.write_json("integrity.json", audit)
    return {**summary, "integrity": audit}


class LiveInvoker:
    def __init__(self, endpoint: str = ENDPOINT, timeout_seconds: int = 300) -> None:
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds

    def __call__(self, call: LogicalCall, attempt_index: int) -> ProviderAttempt:
        started = datetime.now(timezone.utc)
        clock = time.monotonic()
        request = Request(self.endpoint, data=call.request_body, headers={"Content-Type": "application/json"}, method="POST")
        try:
            response = urlopen(request, timeout=self.timeout_seconds)
        except HTTPError as error:
            body = error.read()
            attempt = ProviderAttempt(call.logical_index, attempt_index, call.call_id, call.request_body, body, {"http_status": error.code, "body": body.decode(errors="replace")}, None, None, error.code, started.isoformat(), datetime.now(timezone.utc).isoformat(), time.monotonic() - clock, f"http_{error.code}")
            raise InvocationFailure(f"http_{error.code}", attempt, False) from error
        except (URLError, TimeoutError, OSError) as error:
            attempt = ProviderAttempt(call.logical_index, attempt_index, call.call_id, call.request_body, b"", {"transport_error": repr(error)}, None, None, None, started.isoformat(), datetime.now(timezone.utc).isoformat(), time.monotonic() - clock, "transport_failure")
            raise InvocationFailure("transport_failure", attempt, True) from error
        try:
            with response:
                status = response.status
                response_headers = dict(response.headers.items())
                body = response.read()
        except (TimeoutError, OSError) as error:
            attempt = ProviderAttempt(call.logical_index, attempt_index, call.call_id, call.request_body, b"", {"post_response_transport_error": repr(error)}, None, None, getattr(response, "status", None), started.isoformat(), datetime.now(timezone.utc).isoformat(), time.monotonic() - clock, "post_response_transport_failure")
            raise InvocationFailure("post_response_transport_failure", attempt, False) from error
        ended = datetime.now(timezone.utc)
        try:
            envelope = json.loads(body)
            choices = envelope.get("choices") if type(envelope) is dict else None
            if type(choices) is not list or len(choices) != 1 or type(choices[0]) is not dict or type(choices[0].get("message")) is not dict:
                raise ValueError("one_message_required")
            message = choices[0]["message"]
            content = message.get("content")
            envelope["_formation_transport"] = {"response_headers": response_headers}
        except (json.JSONDecodeError, ValueError) as error:
            attempt = ProviderAttempt(call.logical_index, attempt_index, call.call_id, call.request_body, body, {"provider_envelope_error": str(error)}, None, None, status, started.isoformat(), ended.isoformat(), time.monotonic() - clock, "provider_envelope_invalid")
            raise InvocationFailure("provider_envelope_invalid", attempt, False) from error
        return ProviderAttempt(call.logical_index, attempt_index, call.call_id, call.request_body, body, envelope, message, content, status, started.isoformat(), ended.isoformat(), time.monotonic() - clock)


def _run_command(command: tuple[str, ...]) -> dict[str, object]:
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    return {"command": list(command), "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def _endpoint_receipt() -> dict[str, object]:
    url = "http://localhost:12434/engines/v1/models"
    try:
        with urlopen(Request(url, method="GET"), timeout=10) as response:
            body = response.read()
            return {"url": url, "status": response.status, "body": body.decode("utf-8", errors="replace"), "body_sha256": sha256_bytes(body)}
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        return {"url": url, "error": repr(error)}


def collect_provider_receipt() -> dict[str, object]:
    version = _run_command(("docker", "model", "version"))
    status = _run_command(("docker", "model", "status"))
    inventory = _run_command(("docker", "model", "list"))
    inspection = _run_command(("docker", "model", "inspect", MODEL))
    docker_version = _run_command(("docker", "version", "--format", "{{json .}}"))
    endpoint_receipt = _endpoint_receipt()
    reasons: list[str] = []
    parsed_inspection = None
    render_audit = None
    for name, value in (("version", version), ("status", status), ("inventory", inventory), ("inspection", inspection), ("docker_version", docker_version)):
        if value["returncode"] != 0:
            reasons.append(f"{name}_command_failed")
    try:
        parsed_inspection = json.loads(str(inspection["stdout"]))
        if parsed_inspection.get("id") != MODEL_DIGEST or INSPECT_TAG not in parsed_inspection.get("tags", []):
            reasons.append("model_identity_mismatch")
        template_text = parsed_inspection["config"]["gguf"]["tokenizer.chat_template"]
        template = template_text.encode("utf-8")
        if len(template) != CHAT_TEMPLATE_UTF8_LENGTH or sha256_bytes(template) != CHAT_TEMPLATE_SHA256:
            reasons.append("chat_template_mismatch")
        rendered = render_chat(
            template_text,
            ACQUISITION_SYSTEM,
            acquisition_prompt({"facet": "sava", "mark": "temi", "zone": "woku"}, ("bren", "cavo")),
        ).encode("utf-8")
        render_audit = {
            "renderer_implementation": TEMPLATE_RENDERER_IMPLEMENTATION,
            "bindings": {"tools": "omitted", "add_generation_prompt": True, "enable_thinking": "omitted_undefined"},
            "messages": ["system", "user"],
            "rendered_utf8_length": len(rendered),
            "rendered_sha256": sha256_bytes(rendered),
        }
    except (json.JSONDecodeError, KeyError, TypeError, AttributeError, ValueError):
        reasons.append("inspection_invalid")
    if str(version["stdout"]).count(DMR_VERSION) < 2:
        reasons.append("docker_model_runner_version_mismatch")
    if LLAMA_BACKEND_BUILD not in str(status["stdout"]) or LLAMA_BACKEND_DIGEST not in str(status["stdout"]):
        reasons.append("llama_backend_mismatch")
    if "qwen3:14B-Q6_K" not in str(inventory["stdout"]):
        reasons.append("model_not_in_inventory")
    try:
        parsed_docker = json.loads(str(docker_version["stdout"]))
        if parsed_docker["Server"]["Platform"]["Name"] != DOCKER_DESKTOP_PLATFORM:
            reasons.append("docker_desktop_version_mismatch")
        if parsed_docker["Server"]["Version"] != DOCKER_ENGINE_VERSION:
            reasons.append("docker_engine_version_mismatch")
    except (json.JSONDecodeError, KeyError, TypeError):
        reasons.append("docker_version_invalid")
    if endpoint_receipt.get("status") != 200:
        reasons.append("endpoint_unreachable")
    return {"valid": not reasons, "refusals": reasons, "version": version, "status": status, "inventory": inventory, "inspection": inspection, "parsed_inspection": parsed_inspection, "docker_version": docker_version, "endpoint_receipt": endpoint_receipt, "render_audit": render_audit}


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
