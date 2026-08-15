"""Run the frozen exploratory admission packet for two local small models."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import struct
import subprocess
import time
from typing import Callable
from urllib.request import Request, urlopen

from contact.python_boundary_contact import (
    EXPLORATION_PROMPT,
    EXPLORATION_VECTORS,
    VECTORS,
    Vector,
    refused_results,
    run_vector,
    validate_source,
)
from contact.sqlite_contact import normalize_ascii_whitespace


PYTHON_DIRECT_PROMPT = """Write this Python function:

    parse_revisions(payload)

Contract:
- payload is a dictionary with exactly the keys "artifact_revision" and "authority_revision";
- both values must have exact Python type int; bool is invalid even though bool is a subclass of int;
- both values must be at least zero;
- return (artifact_revision, authority_revision);
- raise ValueError for every invalid input.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence."""

ANCHOR_P1_PROMPT = """Write this Python function:

    join_pair(payload)

Contract:
- payload must be a list containing exactly two values;
- each value must have exact Python type str;
- return the two strings joined by one colon;
- raise ValueError for every invalid input.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence."""

ANCHOR_P2_PROMPT = """Write this Python function:

    require_ready(payload)

Contract:
- payload must have exact Python type str;
- if payload is exactly "ready", return "ready";
- raise ValueError for every other input.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence."""

ANCHOR_S1_PROMPT = """You are writing one SQLite query.

Database:
CREATE TABLE devices(id INTEGER PRIMARY KEY, label TEXT NOT NULL, enabled INTEGER NOT NULL);

Question: return labels of enabled devices, ordered by label.

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence."""

ANCHOR_S2_PROMPT = """You are writing one SQLite query.

Database:
CREATE TABLE entries(category TEXT NOT NULL, amount INTEGER NOT NULL);

Question: return each category and the sum of its amounts, ordered by category.

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence."""

SQLITE_COLD_PROMPT = """You are writing one SQLite query.

Database:
CREATE TABLE vessels(id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE inspections(id INTEGER PRIMARY KEY, vessel_id INTEGER);

Question: return names of vessels that have never been inspected, ordered by name.

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence."""

SQLITE_DIRECT_PROMPT = """You are writing one SQLite query.

Database:
CREATE TABLE packages(id INTEGER PRIMARY KEY, label TEXT NOT NULL);
CREATE TABLE scans(id INTEGER PRIMARY KEY, package_id INTEGER);

Question: return labels of packages that have never been scanned, ordered by label. The query must remain correct when scans.package_id contains NULL. In SQLite, use NOT EXISTS, or if you use NOT IN, exclude NULL inside its subquery.

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence."""

SAMPLING = {
    "frequency_penalty": 0,
    "max_tokens": 768,
    "presence_penalty": 0,
    "repeat_penalty": 1,
    "stream": False,
    "temperature": 0.2,
    "top_k": 40,
    "top_p": 0.95,
}


@dataclass(frozen=True, slots=True)
class ModelConfig:
    name: str
    model_key: str
    selected_variant: str
    indexed_artifact: str
    relative_file: str
    byte_count: int
    sha256: str
    template_characters: int
    template_sha256: str
    family_order: tuple[str, str]


MODELS = (
    ModelConfig(
        "Ministral 3B",
        "mistralai/ministral-3-3b",
        "mistralai/ministral-3-3b@q4_k_m",
        "mistralai/ministral-3-3b@lmstudio-community/Ministral-3-3B-Instruct-2512-GGUF/Ministral-3-3B-Instruct-2512-Q4_K_M.gguf",
        "lmstudio-community/Ministral-3-3B-Instruct-2512-GGUF/Ministral-3-3B-Instruct-2512-Q4_K_M.gguf",
        2146498240,
        "ee46f8f2cc4acf15e89699563e23b4a3919dce2e9ce7c44b53778d6590318e96",
        7753,
        "d28d7df94f0fd7e8d0075a22c473333d6e7dd2bc4c36c83e8b975300a0fb94bc",
        ("Python", "SQLite"),
    ),
    ModelConfig(
        "Nemotron 4B",
        "nvidia/nemotron-3-nano-4b",
        "nvidia/nemotron-3-nano-4b@q4_k_m",
        "nvidia/nemotron-3-nano-4b@lmstudio-community/NVIDIA-Nemotron-3-Nano-4B-GGUF/NVIDIA-Nemotron-3-Nano-4B-Q4_K_M.gguf",
        "lmstudio-community/NVIDIA-Nemotron-3-Nano-4B-GGUF/NVIDIA-Nemotron-3-Nano-4B-Q4_K_M.gguf",
        2837072896,
        "083af225449463dd7c38bebc888f9dcad187b834d8b15e08c297dda37c968b50",
        10504,
        "ab7813c3abdd9cb655905a410728b26c7884eca45ddfab8d9f931553485a7862",
        ("SQLite", "Python"),
    ),
)


def _returns(test_id: str, input_repr: str, value: str, kind: str) -> Vector:
    return Vector(test_id, input_repr, f"return:{value}", value, kind)


def _refuses(test_id: str, input_repr: str) -> Vector:
    return Vector(test_id, input_repr, "raises:ValueError")


ANCHOR_P1_VECTORS = (
    _returns("A-P1-01", "['north', 'gate']", "'north:gate'", "str"),
    _returns("A-P1-02", "['', '']", "':'", "str"),
    _refuses("A-P1-03", "None"), _refuses("A-P1-04", "('north', 'gate')"),
    _refuses("A-P1-05", "[]"), _refuses("A-P1-06", "['north']"),
    _refuses("A-P1-07", "['north', 'gate', 'west']"),
    _refuses("A-P1-08", "[1, 'gate']"),
    _refuses("A-P1-09", "['north', None]"),
)
ANCHOR_P2_VECTORS = (
    _returns("A-P2-01", "'ready'", "'ready'", "str"),
    _refuses("A-P2-02", "'Ready'"), _refuses("A-P2-03", "''"),
    _refuses("A-P2-04", "None"), _refuses("A-P2-05", "['ready']"),
    _refuses("A-P2-06", "1"),
)


@dataclass(frozen=True, slots=True)
class DatabaseVector:
    test_id: str
    ddl: str
    inserts: str
    expected: tuple[tuple[object, ...], ...]
    held: bool


ANCHOR_S1_VECTORS = (
    DatabaseVector("A-S1-01", "CREATE TABLE devices(id INTEGER PRIMARY KEY, label TEXT NOT NULL, enabled INTEGER NOT NULL);", "INSERT INTO devices VALUES (1,'ash',1),(2,'birch',0),(3,'cedar',1);", (("ash",), ("cedar",)), False),
    DatabaseVector("A-S1-02", "CREATE TABLE devices(id INTEGER PRIMARY KEY, label TEXT NOT NULL, enabled INTEGER NOT NULL);", "INSERT INTO devices VALUES (7,'zinc',0),(8,'amber',1),(9,'moss',0);", (("amber",),), False),
)
ANCHOR_S2_VECTORS = (
    DatabaseVector("A-S2-01", "CREATE TABLE entries(category TEXT NOT NULL, amount INTEGER NOT NULL);", "INSERT INTO entries VALUES ('a',2),('b',5),('a',3);", (("a", 5), ("b", 5)), False),
    DatabaseVector("A-S2-02", "CREATE TABLE entries(category TEXT NOT NULL, amount INTEGER NOT NULL);", "INSERT INTO entries VALUES ('west',4),('east',1),('west',-1),('east',6);", (("east", 7), ("west", 3)), False),
)
SQLITE_COLD_VECTORS = (
    DatabaseVector("S-C-O01", "CREATE TABLE vessels(id INTEGER PRIMARY KEY, name TEXT NOT NULL); CREATE TABLE inspections(id INTEGER PRIMARY KEY, vessel_id INTEGER);", "INSERT INTO vessels VALUES (1,'dune'),(2,'flint'),(3,'glass'); INSERT INTO inspections VALUES (10,1);", (("flint",), ("glass",)), False),
    DatabaseVector("S-C-O02", "CREATE TABLE vessels(id INTEGER PRIMARY KEY, name TEXT NOT NULL); CREATE TABLE inspections(id INTEGER PRIMARY KEY, vessel_id INTEGER);", "INSERT INTO vessels VALUES (4,'elm'),(8,'fir'),(9,'gum'); INSERT INTO inspections VALUES (20,8),(21,9);", (("elm",),), False),
    DatabaseVector("S-C-H01", "CREATE TABLE vessels(id INTEGER PRIMARY KEY, name TEXT NOT NULL); CREATE TABLE inspections(id INTEGER PRIMARY KEY, vessel_id INTEGER);", "INSERT INTO vessels VALUES (10,'amber'),(11,'blue'),(12,'copper'); INSERT INTO inspections VALUES (30,11),(31,NULL);", (("amber",), ("copper",)), True),
    DatabaseVector("S-C-H02", "CREATE TABLE vessels(id INTEGER PRIMARY KEY, name TEXT NOT NULL); CREATE TABLE inspections(id INTEGER PRIMARY KEY, vessel_id INTEGER);", "INSERT INTO vessels VALUES (21,'ibis'),(22,'jay'),(23,'kite'),(24,'loon'); INSERT INTO inspections VALUES (40,22),(41,NULL),(42,24);", (("ibis",), ("kite",)), True),
)
SQLITE_DIRECT_VECTORS = (
    DatabaseVector("S-D-O01", "CREATE TABLE packages(id INTEGER PRIMARY KEY, label TEXT NOT NULL); CREATE TABLE scans(id INTEGER PRIMARY KEY, package_id INTEGER);", "INSERT INTO packages VALUES (1,'red'),(2,'teal'); INSERT INTO scans VALUES (10,1);", (("teal",),), False),
    DatabaseVector("S-D-O02", "CREATE TABLE packages(id INTEGER PRIMARY KEY, label TEXT NOT NULL); CREATE TABLE scans(id INTEGER PRIMARY KEY, package_id INTEGER);", "INSERT INTO packages VALUES (5,'oak'),(6,'pine'),(7,'yew'); INSERT INTO scans VALUES (20,6);", (("oak",), ("yew",)), False),
    DatabaseVector("S-D-H01", "CREATE TABLE packages(id INTEGER PRIMARY KEY, label TEXT NOT NULL); CREATE TABLE scans(id INTEGER PRIMARY KEY, package_id INTEGER);", "INSERT INTO packages VALUES (20,'north'),(21,'south'); INSERT INTO scans VALUES (30,NULL),(31,20);", (("south",),), True),
    DatabaseVector("S-D-H02", "CREATE TABLE packages(id INTEGER PRIMARY KEY, label TEXT NOT NULL); CREATE TABLE scans(id INTEGER PRIMARY KEY, package_id INTEGER);", "INSERT INTO packages VALUES (30,'quartz'),(31,'reed'),(32,'stone'),(33,'wheat'); INSERT INTO scans VALUES (40,31),(41,NULL),(42,33);", (("quartz",), ("stone",)), True),
)


@dataclass(frozen=True, slots=True)
class CallSpec:
    logical_index: int
    call_id: str
    family: str
    condition: str
    seed: int
    prompt: str


def schedule(model: ModelConfig) -> tuple[CallSpec, ...]:
    calls = [
        CallSpec(1, "A-P1", "anchor", "anchor", 1001, ANCHOR_P1_PROMPT),
        CallSpec(2, "A-P2", "anchor", "anchor", 1002, ANCHOR_P2_PROMPT),
        CallSpec(3, "A-S1", "anchor", "anchor", 1003, ANCHOR_S1_PROMPT),
        CallSpec(4, "A-S2", "anchor", "anchor", 1004, ANCHOR_S2_PROMPT),
    ]
    prompts = {
        ("Python", "cold"): EXPLORATION_PROMPT,
        ("Python", "direct_rule"): PYTHON_DIRECT_PROMPT,
        ("SQLite", "cold"): SQLITE_COLD_PROMPT,
        ("SQLite", "direct_rule"): SQLITE_DIRECT_PROMPT,
    }
    index = 5
    for family in model.family_order:
        for condition in ("cold", "direct_rule"):
            for repetition, seed in enumerate((1101, 1102, 1103), 1):
                calls.append(CallSpec(index, f"{family}-{condition}-{repetition}", family, condition, seed, prompts[(family, condition)]))
                index += 1
    return tuple(calls)


def _python_report(source: str, function_name: str, vectors: tuple[Vector, ...]) -> dict[str, object]:
    refusal = validate_source(source, function_name)
    tests = refused_results(vectors) if refusal else tuple(
        run_vector(source, function_name, vector) for vector in vectors
    )
    return {"gate_refusal": refusal, "function_name": function_name, "tests": list(tests)}


def _query_gate(output: str) -> str | None:
    query = output.strip()
    if not query:
        return "empty_output"
    if "```" in query:
        return "markdown_fence"
    normalized = normalize_ascii_whitespace(query)
    if not normalized.upper().startswith("SELECT "):
        return "select_required"
    return None


def _sqlite_report(output: str, vectors: tuple[DatabaseVector, ...]) -> dict[str, object]:
    refusal = _query_gate(output)
    results = []
    if refusal:
        return {"gate_refusal": refusal, "tests": []}
    query = output.strip()
    for vector in vectors:
        connection = sqlite3.connect(":memory:")
        try:
            connection.executescript(vector.ddl)
            connection.executescript(vector.inserts)
            connection.execute("PRAGMA query_only=ON")
            try:
                rows = tuple(connection.execute(query).fetchall())
                error = None
            except sqlite3.Error as caught:
                rows = None
                error = type(caught).__name__
        finally:
            connection.close()
        results.append({"test_id": vector.test_id, "held": vector.held, "expected": [list(row) for row in vector.expected], "rows": None if rows is None else [list(row) for row in rows], "error": error, "passed": rows == vector.expected})
    return {"gate_refusal": None, "tests": results}


def _target_label(report: dict[str, object], family: str) -> str:
    tests = report["tests"]
    if report["gate_refusal"] is not None or not tests:
        return "gate_fail"
    if family == "Python":
        held_ids = {"V1-15", "V1-16", "V1-17", "V1-18"}
        held = [item for item in tests if str(item["test_id"]).startswith("E-H") or item["test_id"] in held_ids]
        ordinary = [item for item in tests if item not in held]
    else:
        held = [item for item in tests if item["held"]]
        ordinary = [item for item in tests if not item["held"]]
    if not ordinary or not held or not all(item["passed"] for item in ordinary):
        return "ordinary_fail"
    if all(item["passed"] for item in held):
        return "full_pass"
    if family == "Python":
        if all(item["passed"] or item["process_status"] == "returned" for item in held) and any(item["process_status"] == "returned" and not item["passed"] for item in held):
            return "boundary_miss"
    elif all(item["error"] is None for item in held) and any(not item["passed"] for item in held):
        return "boundary_miss"
    return "ordinary_fail"


def family_label(cold: tuple[str, str, str], direct: tuple[str, str, str]) -> str:
    combined = cold + direct
    if any(item in {"gate_fail", "ordinary_fail"} for item in combined):
        return "ordinary_fragile"
    cold_miss = cold.count("boundary_miss")
    cold_pass = cold.count("full_pass")
    direct_pass = direct.count("full_pass")
    if cold_miss >= 2 and direct_pass >= 2:
        return "in_band"
    if cold_pass >= 2:
        return "cold_ceiling"
    if cold_miss >= 2 and direct_pass < 2:
        return "not_teachable"
    raise ValueError("incomplete_family_classifier")


def terminal_label(cells: dict[str, str]) -> str:
    admitted = [name for name in ("Python", "SQLite") if cells[name] == "in_band"]
    if admitted:
        return "admitted:" + ",".join(admitted)
    if all(cells[name] == "cold_ceiling" for name in ("Python", "SQLite")):
        return "cold_ceiling"
    if any(value == "not_teachable" for value in cells.values()) and all(value in {"not_teachable", "cold_ceiling"} for value in cells.values()):
        return "not_teachable_here"
    return "mixed_unstable"


@dataclass(frozen=True, slots=True)
class Attempt:
    logical_index: int
    attempt_index: int
    call_id: str
    family: str
    condition: str
    seed: int
    prompt: str
    output: str
    request_envelope: dict[str, object]
    response_envelope: dict[str, object]
    started_at: str
    ended_at: str
    elapsed_seconds: float
    retry_reason: str | None
    retry_of_attempt: int | None


Invoker = Callable[[ModelConfig, CallSpec], Attempt]


def invoke_with_retry(invoker: Invoker, model: ModelConfig, spec: CallSpec) -> tuple[Attempt, ...]:
    first = invoker(model, spec)
    if first.output:
        return (first,)
    first = replace(first, retry_reason="no_model_output")
    second = replace(invoker(model, spec), attempt_index=2, retry_reason="no_model_output", retry_of_attempt=1)
    return (first, second)


def _write_attempt(
    directory: Path,
    attempt: Attempt,
    report: dict[str, object],
    label: str,
    packet_receipt: dict[str, object],
) -> None:
    stem = f"{attempt.logical_index:02d}-{attempt.call_id}-a{attempt.attempt_index}"
    (directory / f"{stem}.prompt.txt").write_text(attempt.prompt)
    (directory / f"{stem}.output.txt").write_text(attempt.output)
    record = asdict(attempt)
    record["prompt_sha256"] = hashlib.sha256(attempt.prompt.encode()).hexdigest()
    record["output_sha256"] = hashlib.sha256(attempt.output.encode()).hexdigest()
    record["oracle_report"] = report
    record["call_label"] = label
    record["packet_receipt"] = packet_receipt
    record.pop("prompt")
    record.pop("output")
    (directory / f"{stem}.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")


def _score(spec: CallSpec, output: str) -> tuple[dict[str, object], str]:
    if spec.call_id == "A-P1":
        report = _python_report(output, "join_pair", ANCHOR_P1_VECTORS)
        return report, "full_pass" if report["gate_refusal"] is None and all(item["passed"] for item in report["tests"]) else "anchor_fail"
    if spec.call_id == "A-P2":
        report = _python_report(output, "require_ready", ANCHOR_P2_VECTORS)
        return report, "full_pass" if report["gate_refusal"] is None and all(item["passed"] for item in report["tests"]) else "anchor_fail"
    if spec.call_id == "A-S1":
        report = _sqlite_report(output, ANCHOR_S1_VECTORS)
        return report, "full_pass" if report["gate_refusal"] is None and all(item["passed"] for item in report["tests"]) else "anchor_fail"
    if spec.call_id == "A-S2":
        report = _sqlite_report(output, ANCHOR_S2_VECTORS)
        return report, "full_pass" if report["gate_refusal"] is None and all(item["passed"] for item in report["tests"]) else "anchor_fail"
    if spec.family == "Python":
        report = _python_report(output, "parse_limits" if spec.condition == "cold" else "parse_revisions", EXPLORATION_VECTORS if spec.condition == "cold" else VECTORS["V1"])
    else:
        report = _sqlite_report(output, SQLITE_COLD_VECTORS if spec.condition == "cold" else SQLITE_DIRECT_VECTORS)
    return report, _target_label(report, spec.family)


def run_model(
    invoker: Invoker,
    model: ModelConfig,
    directory: Path,
    packet_receipt: dict[str, object] | None = None,
) -> dict[str, object]:
    directory.mkdir(parents=True, exist_ok=False)
    packet_receipt = {} if packet_receipt is None else packet_receipt
    calls = []
    labels: dict[tuple[str, str], list[str]] = {}
    for spec in schedule(model):
        attempts = invoke_with_retry(invoker, model, spec)
        final = attempts[-1]
        report, label = _score(spec, final.output)
        for attempt in attempts:
            _write_attempt(
                directory,
                attempt,
                report if attempt is final else {},
                label if attempt is final else "retry_pending",
                packet_receipt,
            )
        calls.append({"logical_index": spec.logical_index, "call_id": spec.call_id, "family": spec.family, "condition": spec.condition, "seed": spec.seed, "label": label, "report": report})
        if spec.family == "anchor" and label != "full_pass":
            summary = {"model": asdict(model), "packet_receipt": packet_receipt, "terminal_result": "contract_unreliable", "stopping_call": spec.logical_index, "calls": calls, "family_cells": {}}
            (directory / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
            return summary
        if spec.family != "anchor":
            labels.setdefault((spec.family, spec.condition), []).append(label)
    cells = {}
    for family in ("Python", "SQLite"):
        cells[family] = family_label(tuple(labels[(family, "cold")]), tuple(labels[(family, "direct_rule")]))
    summary = {"model": asdict(model), "packet_receipt": packet_receipt, "terminal_result": terminal_label(cells), "stopping_call": 16, "calls": calls, "family_cells": cells}
    (directory / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def _read_gguf_template(path: Path) -> str:
    formats = {0: "B", 1: "b", 2: "H", 3: "h", 4: "I", 5: "i", 6: "f", 7: "?", 10: "Q", 11: "q", 12: "d"}
    with path.open("rb") as stream:
        def read(kind: str) -> object:
            size = struct.calcsize("<" + kind)
            return struct.unpack("<" + kind, stream.read(size))[0]
        def string() -> str:
            return stream.read(read("Q")).decode()
        def value(kind: int, keep: bool = False) -> object:
            if kind == 8:
                result = string()
                return result if keep else None
            if kind == 9:
                inner, count = read("I"), read("Q")
                for _ in range(count):
                    value(inner, False)
                return None
            result = read(formats[kind])
            return result if keep else None
        if stream.read(4) != b"GGUF":
            raise ValueError("exact_gguf_required")
        read("I"); read("Q"); count = read("Q")
        found = None
        for _ in range(count):
            key, kind = string(), read("I")
            retained = value(kind, key == "tokenizer.chat_template")
            if key == "tokenizer.chat_template":
                found = retained
        if type(found) is not str:
            raise ValueError("embedded_chat_template_required")
        return found


def verify_artifact(model: ModelConfig) -> dict[str, object]:
    path = Path.home() / ".lmstudio" / "models" / model.relative_file
    if not path.is_file() or path.stat().st_size != model.byte_count:
        raise ValueError("model_artifact_size_mismatch")
    digest_builder = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest_builder.update(block)
    digest = digest_builder.hexdigest()
    if digest != model.sha256:
        raise ValueError("model_artifact_digest_mismatch")
    template = _read_gguf_template(path)
    template_digest = hashlib.sha256(template.encode()).hexdigest()
    if len(template) != model.template_characters or template_digest != model.template_sha256:
        raise ValueError("model_chat_template_mismatch")
    return {"path": str(path), "byte_count": model.byte_count, "sha256": digest, "template_characters": len(template), "template_sha256": template_digest}


class LiveInvoker:
    def __init__(self, model: ModelConfig, server_url: str = "http://127.0.0.1:1234/v1/chat/completions") -> None:
        self.model = model
        self.identifier = "formation-admission-" + ("mistral" if "mistral" in model.model_key else "nemotron")
        self.server_url = server_url

    def __call__(self, model: ModelConfig, spec: CallSpec) -> Attempt:
        if model is not self.model:
            raise ValueError("exact_loaded_model_required")
        envelope = {"model": self.identifier, "messages": [{"role": "user", "content": spec.prompt}], **SAMPLING, "seed": spec.seed}
        started = datetime.now(timezone.utc); clock = time.monotonic()
        request = Request(self.server_url, data=json.dumps(envelope).encode(), headers={"Content-Type": "application/json", "Authorization": "Bearer lm-studio"}, method="POST")
        with urlopen(request, timeout=180) as response:
            response_envelope = json.loads(response.read())
        elapsed = time.monotonic() - clock; ended = datetime.now(timezone.utc)
        output = response_envelope["choices"][0]["message"].get("content") or ""
        return Attempt(spec.logical_index, 1, spec.call_id, spec.family, spec.condition, spec.seed, spec.prompt, output, envelope, response_envelope, started.isoformat(), ended.isoformat(), elapsed, None, None)


def run_live(evidence_directory: Path) -> dict[str, object]:
    evidence_directory.mkdir(parents=True, exist_ok=False)
    artifact_records = {model.model_key: verify_artifact(model) for model in MODELS}
    cli_version = subprocess.run(
        ("lms", "--version"), check=True, capture_output=True, text=True
    ).stdout.strip()
    runtime_inventory = subprocess.run(
        ("lms", "runtime", "ls"), check=True, capture_output=True, text=True
    ).stdout
    server_start = subprocess.run(
        ("lms", "server", "start"), check=False, capture_output=True, text=True
    )
    if server_start.returncode != 0 and "already" not in (
        server_start.stdout + server_start.stderr
    ).lower():
        raise ValueError("lm_studio_server_unavailable")
    server_receipt = {
        "command": ["lms", "server", "start"],
        "exit_code": server_start.returncode,
        "stdout": server_start.stdout,
        "stderr": server_start.stderr,
    }
    model_summaries = []
    projector = (
        Path.home()
        / ".lmstudio/models/lmstudio-community/Ministral-3-3B-Instruct-2512-GGUF/mmproj-Ministral-3-3B-Instruct-2512-F16.gguf"
    )
    projector_hold = projector.with_name(projector.name + ".formation-held")
    if projector_hold.exists() and not projector.exists():
        projector_hold.replace(projector)
    if projector_hold.exists():
        raise ValueError("ambiguous_ministral_projector_state")
    try:
        for model in MODELS:
            subprocess.run(("lms", "unload", "--all"), check=False, capture_output=True, text=True)
            identifier = "formation-admission-" + ("mistral" if "mistral" in model.model_key else "nemotron")
            held_projector = False
            try:
                if model is MODELS[0]:
                    if not projector.is_file():
                        raise ValueError("ministral_projector_required_for_recoverable_hold")
                    projector.replace(projector_hold)
                    held_projector = True
                load_command = ("lms", "load", model.model_key, "--gpu", "max", "--context-length", "8192", "--parallel", "1", "--no-speculative-draft-mtp", "--identifier", identifier, "-y")
                load_process = subprocess.run(load_command, check=True, capture_output=True, text=True)
                loaded = json.loads(subprocess.run(("lms", "ps", "--json"), check=True, capture_output=True, text=True).stdout)
                if (
                    len(loaded) != 1
                    or loaded[0].get("identifier") != identifier
                    or loaded[0].get("selectedVariant") != model.selected_variant
                    or loaded[0].get("contextLength") != 8192
                    or loaded[0].get("parallel") != 1
                    or loaded[0].get("vision") is not False
                ):
                    raise ValueError("exact_text_only_model_load_required")
                packet_receipt = {
                    "model": asdict(model),
                    "artifact_verification": artifact_records[model.model_key],
                    "cli_version": cli_version,
                    "runtime_inventory": runtime_inventory,
                    "server": server_receipt,
                    "load": {
                        "command": list(load_command),
                        "exit_code": load_process.returncode,
                        "stdout": load_process.stdout,
                        "stderr": load_process.stderr,
                        "instance": loaded[0],
                    },
                    "text_only": True,
                    "projector_attached": False,
                    "speculative_decoding": False,
                    "tools": False,
                    "history_reuse": False,
                }
                model_dir = evidence_directory / identifier
                summary = run_model(
                    LiveInvoker(model), model, model_dir, packet_receipt
                )
                model_summaries.append(summary)
            finally:
                subprocess.run(("lms", "unload", "--all"), check=False, capture_output=True, text=True)
                if held_projector and projector_hold.exists():
                    projector_hold.replace(projector)
    finally:
        subprocess.run(("lms", "unload", "--all"), check=False, capture_output=True, text=True)
        if projector_hold.exists() and not projector.exists():
            projector_hold.replace(projector)
    summary = {"protocol": "small-model-admission-exploration-v0", "evidence_class": "exploratory_only", "models": model_summaries, "artifact_verification": artifact_records}
    (evidence_directory / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the reviewed local small-model admission exploration.")
    parser.add_argument("--evidence-directory", type=Path, required=True)
    parser.add_argument("--run-contact", action="store_true")
    arguments = parser.parse_args()
    if not arguments.run_contact:
        parser.error("--run-contact is required")
    print(json.dumps(run_live(arguments.evidence_directory), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
