"""Run the reviewed corrected Nemotron admission successor."""

from __future__ import annotations

import argparse
import ast
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
from typing import Callable
from urllib.request import Request, urlopen

from contact.model_admission import (
    Attempt,
    ModelConfig,
    SAMPLING,
    family_label,
    terminal_label,
    verify_artifact,
)


MODEL = ModelConfig(
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
)

ANCHOR_P1_PROMPT = """Write this Python function:

    combine_labels(payload)

Contract:
- payload must be a tuple containing exactly two values;
- each value must have exact Python type str;
- return the two strings joined by one slash;
- raise ValueError for every invalid input.

Execution environment:
- available builtins are ValueError, TypeError, all, any, bool, dict, int, isinstance, len, list, set, str, tuple, and type;
- no other builtin, import, file, network, dynamic execution, or additional definition is available.
- each input runs in a fresh process with a one-second CPU and wall-clock limit, an empty working directory, and no writable file;
- do not mutate payload or write to stdout or stderr.

Source requirements:
- define one top-level synchronous function with the requested name and exactly one ordinary positional-or-keyword argument named payload; do not use a positional-only argument, default, variadic argument, or keyword-only argument; annotations are allowed;
- do not use another top-level statement, decorator, class, async function, nested function or class, lambda, import, global, nonlocal, await, yield, yield from, exec, eval, compile, open, or dunder attribute.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence."""

ANCHOR_P2_PROMPT = """Write this Python function:

    accept_mode(payload)

Contract:
- payload must have exact Python type str;
- if payload is exactly "active", return "active";
- raise ValueError for every other input.

Execution environment:
- available builtins are ValueError, TypeError, all, any, bool, dict, int, isinstance, len, list, set, str, tuple, and type;
- no other builtin, import, file, network, dynamic execution, or additional definition is available.
- each input runs in a fresh process with a one-second CPU and wall-clock limit, an empty working directory, and no writable file;
- do not mutate payload or write to stdout or stderr.

Source requirements:
- define one top-level synchronous function with the requested name and exactly one ordinary positional-or-keyword argument named payload; do not use a positional-only argument, default, variadic argument, or keyword-only argument; annotations are allowed;
- do not use another top-level statement, decorator, class, async function, nested function or class, lambda, import, global, nonlocal, await, yield, yield from, exec, eval, compile, open, or dunder attribute.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence."""

PYTHON_COLD_PROMPT = """Write this Python function:

    parse_versions(payload)

Contract:
- payload is a dictionary with exactly the keys "client_version" and "server_version";
- both values must be Python integers;
- both values must be at least zero;
- client_version must be less than or equal to server_version;
- return (client_version, server_version);
- raise ValueError for every invalid input.

Execution environment:
- available builtins are ValueError, TypeError, all, any, bool, dict, int, isinstance, len, list, set, str, tuple, and type;
- no other builtin, import, file, network, dynamic execution, or additional definition is available.
- each input runs in a fresh process with a one-second CPU and wall-clock limit, an empty working directory, and no writable file;
- do not mutate payload or write to stdout or stderr.

Source requirements:
- define one top-level synchronous function with the requested name and exactly one ordinary positional-or-keyword argument named payload; do not use a positional-only argument, default, variadic argument, or keyword-only argument; annotations are allowed;
- do not use another top-level statement, decorator, class, async function, nested function or class, lambda, import, global, nonlocal, await, yield, yield from, exec, eval, compile, open, or dunder attribute.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence."""

PYTHON_DIRECT_PROMPT = """Write this Python function:

    parse_slots(payload)

Contract:
- payload is a dictionary with exactly the keys "used_slots" and "total_slots";
- both values must have exact Python type int; bool is invalid even though bool is a subclass of int;
- both values must be at least zero;
- used_slots must be less than or equal to total_slots;
- return (used_slots, total_slots);
- raise ValueError for every invalid input.

Execution environment:
- available builtins are ValueError, TypeError, all, any, bool, dict, int, isinstance, len, list, set, str, tuple, and type;
- no other builtin, import, file, network, dynamic execution, or additional definition is available.
- each input runs in a fresh process with a one-second CPU and wall-clock limit, an empty working directory, and no writable file;
- do not mutate payload or write to stdout or stderr.

Source requirements:
- define one top-level synchronous function with the requested name and exactly one ordinary positional-or-keyword argument named payload; do not use a positional-only argument, default, variadic argument, or keyword-only argument; annotations are allowed;
- do not use another top-level statement, decorator, class, async function, nested function or class, lambda, import, global, nonlocal, await, yield, yield from, exec, eval, compile, open, or dunder attribute.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence."""

ANCHOR_S1_PROMPT = """You are writing one SQLite query.

Database:
CREATE TABLE endpoints(id INTEGER PRIMARY KEY, hostname TEXT NOT NULL, online INTEGER NOT NULL);

Question: return hostnames of online endpoints, ordered by hostname.

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence."""

ANCHOR_S2_PROMPT = """You are writing one SQLite query.

Database:
CREATE TABLE readings(sensor TEXT NOT NULL, value INTEGER NOT NULL);

Question: return each sensor and the sum of its values, ordered by sensor.

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence."""

SQLITE_COLD_PROMPT = """You are writing one SQLite query.

Database:
CREATE TABLE volumes(id INTEGER PRIMARY KEY, title TEXT NOT NULL);
CREATE TABLE loans(id INTEGER PRIMARY KEY, volume_id INTEGER);

Question: return titles of volumes that have never been loaned, ordered by title.

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence."""

SQLITE_DIRECT_PROMPT = """You are writing one SQLite query.

Database:
CREATE TABLE depots(id INTEGER PRIMARY KEY, code TEXT NOT NULL);
CREATE TABLE shipments(id INTEGER PRIMARY KEY, depot_id INTEGER);

Question: return codes of depots with no shipment, ordered by code. A NULL shipment depot does not identify any depot and must not remove unrelated rows. Express absence with a correlated NOT EXISTS condition.

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence."""


@dataclass(frozen=True, slots=True)
class PythonVector:
    test_id: str
    input_repr: str
    expected: str
    return_repr: str | None = None
    return_type: str | None = None
    held: bool = False


def _returns(test_id: str, input_repr: str, value: str, kind: str) -> PythonVector:
    return PythonVector(test_id, input_repr, f"return:{value}", value, kind)


def _refuses(test_id: str, input_repr: str, held: bool = False) -> PythonVector:
    return PythonVector(test_id, input_repr, "raises:ValueError", held=held)


ANCHOR_P1_VECTORS = (
    _returns("C-P1-01", "('east', 'wing')", "'east/wing'", "str"),
    _returns("C-P1-02", "('', '')", "'/'", "str"),
    _refuses("C-P1-03", "None"),
    _refuses("C-P1-04", "['east', 'wing']"),
    _refuses("C-P1-05", "()"),
    _refuses("C-P1-06", "('east',)"),
    _refuses("C-P1-07", "('east', 'wing', 'roof')"),
    _refuses("C-P1-08", "(1, 'wing')"),
    _refuses("C-P1-09", "('east', None)"),
)
ANCHOR_P2_VECTORS = (
    _returns("C-P2-01", "'active'", "'active'", "str"),
    _refuses("C-P2-02", "'Active'"),
    _refuses("C-P2-03", "''"),
    _refuses("C-P2-04", "None"),
    _refuses("C-P2-05", "['active']"),
    _refuses("C-P2-06", "1"),
)
PYTHON_COLD_VECTORS = (
    _returns("C-PY-O01", "{'client_version': 0, 'server_version': 4}", "(0, 4)", "tuple"),
    _returns("C-PY-O02", "{'client_version': 6, 'server_version': 6}", "(6, 6)", "tuple"),
    _refuses("C-PY-O03", "None"),
    _refuses("C-PY-O04", "[0, 4]"),
    _refuses("C-PY-O05", "{}"),
    _refuses("C-PY-O06", "{'client_version': 0}"),
    _refuses("C-PY-O07", "{'server_version': 4}"),
    _refuses("C-PY-O08", "{'client_version': 0, 'server_version': 4, 'channel': 'blue'}"),
    _refuses("C-PY-O09", "{'client_version': '0', 'server_version': 4}"),
    _refuses("C-PY-O10", "{'client_version': 0.0, 'server_version': 4}"),
    _refuses("C-PY-O11", "{'client_version': None, 'server_version': 4}"),
    _refuses("C-PY-O12", "{'client_version': [0], 'server_version': 4}"),
    _refuses("C-PY-O13", "{'client_version': 0, 'server_version': '4'}"),
    _refuses("C-PY-O14", "{'client_version': 0, 'server_version': 4.0}"),
    _refuses("C-PY-O15", "{'client_version': 0, 'server_version': None}"),
    _refuses("C-PY-O16", "{'client_version': 0, 'server_version': [4]}"),
    _refuses("C-PY-O17", "{'client_version': -1, 'server_version': 4}"),
    _refuses("C-PY-O18", "{'client_version': 0, 'server_version': -1}"),
    _refuses("C-PY-O19", "{'client_version': 5, 'server_version': 4}"),
    _refuses("C-PY-H01", "{'client_version': True, 'server_version': 4}", True),
    _refuses("C-PY-H02", "{'client_version': 0, 'server_version': False}", True),
    _refuses("C-PY-H03", "{'client_version': False, 'server_version': True}", True),
)
PYTHON_DIRECT_VECTORS = (
    _returns("D-PY-O01", "{'used_slots': 0, 'total_slots': 5}", "(0, 5)", "tuple"),
    _returns("D-PY-O02", "{'used_slots': 7, 'total_slots': 7}", "(7, 7)", "tuple"),
    _refuses("D-PY-O03", "None"),
    _refuses("D-PY-O04", "[0, 5]"),
    _refuses("D-PY-O05", "{}"),
    _refuses("D-PY-O06", "{'used_slots': 0}"),
    _refuses("D-PY-O07", "{'total_slots': 5}"),
    _refuses("D-PY-O08", "{'used_slots': 0, 'total_slots': 5, 'source': 'green'}"),
    _refuses("D-PY-O09", "{'used_slots': '0', 'total_slots': 5}"),
    _refuses("D-PY-O10", "{'used_slots': 0.0, 'total_slots': 5}"),
    _refuses("D-PY-O11", "{'used_slots': None, 'total_slots': 5}"),
    _refuses("D-PY-O12", "{'used_slots': [0], 'total_slots': 5}"),
    _refuses("D-PY-O13", "{'used_slots': 0, 'total_slots': '5'}"),
    _refuses("D-PY-O14", "{'used_slots': 0, 'total_slots': 5.0}"),
    _refuses("D-PY-O15", "{'used_slots': 0, 'total_slots': None}"),
    _refuses("D-PY-O16", "{'used_slots': 0, 'total_slots': [5]}"),
    _refuses("D-PY-O17", "{'used_slots': -2, 'total_slots': 5}"),
    _refuses("D-PY-O18", "{'used_slots': 0, 'total_slots': -2}"),
    _refuses("D-PY-O19", "{'used_slots': 8, 'total_slots': 7}"),
    _refuses("D-PY-H01", "{'used_slots': True, 'total_slots': 5}", True),
    _refuses("D-PY-H02", "{'used_slots': False, 'total_slots': 5}", True),
    _refuses("D-PY-H03", "{'used_slots': 0, 'total_slots': True}", True),
    _refuses("D-PY-H04", "{'used_slots': 0, 'total_slots': False}", True),
)


@dataclass(frozen=True, slots=True)
class DatabaseVector:
    test_id: str
    ddl: str
    inserts: str
    expected: tuple[tuple[object, ...], ...]
    held: bool


ANCHOR_S1_VECTORS = (
    DatabaseVector("C-S1-01", "CREATE TABLE endpoints(id INTEGER PRIMARY KEY, hostname TEXT NOT NULL, online INTEGER NOT NULL);", "INSERT INTO endpoints VALUES (1,'cairn',1),(2,'delta',0),(3,'ember',1);", (("cairn",), ("ember",)), False),
    DatabaseVector("C-S1-02", "CREATE TABLE endpoints(id INTEGER PRIMARY KEY, hostname TEXT NOT NULL, online INTEGER NOT NULL);", "INSERT INTO endpoints VALUES (8,'willow',0),(9,'larch',1),(10,'spruce',0);", (("larch",),), False),
)
ANCHOR_S2_VECTORS = (
    DatabaseVector("C-S2-01", "CREATE TABLE readings(sensor TEXT NOT NULL, value INTEGER NOT NULL);", "INSERT INTO readings VALUES ('r',4),('s',7),('r',2);", (("r", 6), ("s", 7)), False),
    DatabaseVector("C-S2-02", "CREATE TABLE readings(sensor TEXT NOT NULL, value INTEGER NOT NULL);", "INSERT INTO readings VALUES ('north',5),('south',3),('north',-2),('south',8);", (("north", 3), ("south", 11)), False),
)
SQLITE_COLD_VECTORS = (
    DatabaseVector("C-Q-O01", "CREATE TABLE volumes(id INTEGER PRIMARY KEY, title TEXT NOT NULL); CREATE TABLE loans(id INTEGER PRIMARY KEY, volume_id INTEGER);", "INSERT INTO volumes VALUES (1,'fjord'),(2,'grove'),(3,'heath'); INSERT INTO loans VALUES (10,1);", (("grove",), ("heath",)), False),
    DatabaseVector("C-Q-O02", "CREATE TABLE volumes(id INTEGER PRIMARY KEY, title TEXT NOT NULL); CREATE TABLE loans(id INTEGER PRIMARY KEY, volume_id INTEGER);", "INSERT INTO volumes VALUES (5,'mire'),(8,'nook'),(9,'orchard'); INSERT INTO loans VALUES (20,8),(21,9);", (("mire",),), False),
    DatabaseVector("C-Q-H01", "CREATE TABLE volumes(id INTEGER PRIMARY KEY, title TEXT NOT NULL); CREATE TABLE loans(id INTEGER PRIMARY KEY, volume_id INTEGER);", "INSERT INTO volumes VALUES (11,'pearl'),(12,'quill'),(13,'rune'); INSERT INTO loans VALUES (30,12),(31,NULL);", (("pearl",), ("rune",)), True),
    DatabaseVector("C-Q-H02", "CREATE TABLE volumes(id INTEGER PRIMARY KEY, title TEXT NOT NULL); CREATE TABLE loans(id INTEGER PRIMARY KEY, volume_id INTEGER);", "INSERT INTO volumes VALUES (21,'tarn'),(22,'umber'),(23,'vale'),(24,'wold'); INSERT INTO loans VALUES (40,22),(41,NULL),(42,24);", (("tarn",), ("vale",)), True),
)
SQLITE_DIRECT_VECTORS = (
    DatabaseVector("D-Q-O01", "CREATE TABLE depots(id INTEGER PRIMARY KEY, code TEXT NOT NULL); CREATE TABLE shipments(id INTEGER PRIMARY KEY, depot_id INTEGER);", "INSERT INTO depots VALUES (2,'ax'),(4,'by'); INSERT INTO shipments VALUES (10,2);", (("by",),), False),
    DatabaseVector("D-Q-O02", "CREATE TABLE depots(id INTEGER PRIMARY KEY, code TEXT NOT NULL); CREATE TABLE shipments(id INTEGER PRIMARY KEY, depot_id INTEGER);", "INSERT INTO depots VALUES (6,'cz'),(7,'du'),(9,'ev'); INSERT INTO shipments VALUES (20,7);", (("cz",), ("ev",)), False),
    DatabaseVector("D-Q-H01", "CREATE TABLE depots(id INTEGER PRIMARY KEY, code TEXT NOT NULL); CREATE TABLE shipments(id INTEGER PRIMARY KEY, depot_id INTEGER);", "INSERT INTO depots VALUES (12,'fw'),(13,'gx'); INSERT INTO shipments VALUES (30,NULL),(31,12);", (("gx",),), True),
    DatabaseVector("D-Q-H02", "CREATE TABLE depots(id INTEGER PRIMARY KEY, code TEXT NOT NULL); CREATE TABLE shipments(id INTEGER PRIMARY KEY, depot_id INTEGER);", "INSERT INTO depots VALUES (30,'hy'),(31,'iz'),(32,'ja'),(33,'kb'); INSERT INTO shipments VALUES (40,31),(41,NULL),(42,33);", (("hy",), ("ja",)), True),
)


DISALLOWED_NODES = (
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.Global,
    ast.Import,
    ast.ImportFrom,
    ast.Lambda,
    ast.Nonlocal,
    ast.Await,
    ast.Yield,
    ast.YieldFrom,
)
DISALLOWED_CALLS = {"compile", "eval", "exec", "open"}


def validate_source(source: str, function_name: str) -> str | None:
    if "```" in source:
        return "markdown_fence"
    try:
        tree = ast.parse(source.strip())
    except SyntaxError:
        return "syntax_error"
    if len(tree.body) != 1 or type(tree.body[0]) is not ast.FunctionDef:
        return "one_function_required"
    function = tree.body[0]
    if function.name != function_name or function.decorator_list:
        return "exact_function_required"
    arguments = function.args
    if (
        arguments.posonlyargs
        or len(arguments.args) != 1
        or arguments.args[0].arg != "payload"
        or arguments.vararg is not None
        or arguments.kwarg is not None
        or arguments.kwonlyargs
        or arguments.defaults
    ):
        return "exact_payload_signature_required"
    nodes = tuple(ast.walk(tree))
    if any(isinstance(node, DISALLOWED_NODES) for node in nodes):
        return "disallowed_syntax"
    if any(isinstance(node, ast.FunctionDef) and node is not function for node in nodes):
        return "nested_definition"
    if any(isinstance(node, ast.Attribute) and node.attr.startswith("__") for node in nodes):
        return "dunder_attribute"
    if any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in DISALLOWED_CALLS
            for node in nodes
    ):
        return "disallowed_call"
    return None


CHILD = r'''import ast, copy, io, json, resource, sys
resource.setrlimit(resource.RLIMIT_CPU, (1, 2))
resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
request = json.loads(sys.stdin.read())
allowed = {name: value for name, value in {
    "ValueError": ValueError, "TypeError": TypeError, "all": all, "any": any,
    "bool": bool, "dict": dict, "int": int, "isinstance": isinstance,
    "len": len, "list": list, "set": set, "str": str, "tuple": tuple,
    "type": type,
}.items()}
namespace = {"__builtins__": allowed}
exec(compile(request["source"], "<participant>", "exec"), namespace)
value = ast.literal_eval(request["input_repr"])
before = copy.deepcopy(value)
stdout, stderr = io.StringIO(), io.StringIO()
oldout, olderr = sys.stdout, sys.stderr
sys.stdout, sys.stderr = stdout, stderr
status, returned, exception_type = "returned", None, None
try:
    returned = namespace[request["function_name"]](value)
except BaseException as error:
    status, exception_type = "raised", type(error).__name__
finally:
    sys.stdout, sys.stderr = oldout, olderr
mutated = value != before or type(value) is not type(before)
if request["expected"] == "raises:ValueError":
    passed = status == "raised" and exception_type == "ValueError"
else:
    passed = status == "returned" and type(returned).__name__ == request["return_type"] and repr(returned) == request["return_repr"]
if stdout.getvalue() or stderr.getvalue() or mutated:
    passed = False
result = {
    "exception_type": exception_type, "expected": request["expected"],
    "held": request["held"], "input_repr": request["input_repr"],
    "mutated": mutated, "passed": passed, "process_status": status,
    "returned_repr": None if status != "returned" else repr(returned),
    "stderr": stderr.getvalue(), "stdout": stdout.getvalue(),
    "test_id": request["test_id"],
}
oldout.write(json.dumps(result, ensure_ascii=True, separators=(",", ":"), sort_keys=True))
'''


def refused_results(vectors: tuple[PythonVector, ...]) -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "exception_type": None,
            "expected": vector.expected,
            "held": vector.held,
            "input_repr": vector.input_repr,
            "mutated": False,
            "passed": False,
            "process_status": "refused",
            "returned_repr": None,
            "stderr": "",
            "stdout": "",
            "test_id": vector.test_id,
        }
        for vector in vectors
    )


def run_vector(source: str, function_name: str, vector: PythonVector) -> dict[str, object]:
    request = {
        "source": source.strip(),
        "function_name": function_name,
        "test_id": vector.test_id,
        "input_repr": vector.input_repr,
        "expected": vector.expected,
        "return_repr": vector.return_repr,
        "return_type": vector.return_type,
        "held": vector.held,
    }
    with tempfile.TemporaryDirectory(prefix="formation-nemotron-vector-") as workspace:
        try:
            process = subprocess.run(
                (sys.executable, "-I", "-S", "-c", CHILD),
                input=json.dumps(request),
                capture_output=True,
                text=True,
                cwd=workspace,
                timeout=1.0,
                env={"PATH": ""},
            )
        except subprocess.TimeoutExpired:
            result = refused_results((vector,))[0]
            result["process_status"] = "timeout"
            return result
    if process.returncode == -signal.SIGXCPU:
        result = refused_results((vector,))[0]
        result["process_status"] = "timeout"
        result["stderr"] = process.stderr
        return result
    if process.returncode != 0:
        result = refused_results((vector,))[0]
        result["process_status"] = "crashed"
        result["stderr"] = process.stderr
        return result
    try:
        return json.loads(process.stdout)
    except json.JSONDecodeError:
        result = refused_results((vector,))[0]
        result["process_status"] = "crashed"
        result["stdout"] = process.stdout
        result["stderr"] = process.stderr
        return result


def _python_report(source: str, function_name: str, vectors: tuple[PythonVector, ...]) -> dict[str, object]:
    refusal = validate_source(source, function_name)
    tests = refused_results(vectors) if refusal else tuple(
        run_vector(source, function_name, vector) for vector in vectors
    )
    return {"gate_refusal": refusal, "function_name": function_name, "tests": list(tests)}


def normalize_ascii_whitespace(value: str) -> str:
    return re.sub(r"[\t\n\r\f\v ]+", " ", value).strip().upper()


def _query_gate(output: str) -> str | None:
    query = output.strip()
    if not query:
        return "empty_output"
    if "```" in query:
        return "markdown_fence"
    first = re.match(r"[A-Za-z]+", query)
    if first is None or first.group(0).upper() != "SELECT":
        return "select_required"
    return None


def _sqlite_report(
    output: str,
    vectors: tuple[DatabaseVector, ...],
    require_not_exists: bool = False,
) -> dict[str, object]:
    refusal = _query_gate(output)
    if refusal:
        return {"gate_refusal": refusal, "constraint_met": False, "tests": []}
    query = output.strip()
    constraint_met = not require_not_exists or "NOT EXISTS" in normalize_ascii_whitespace(query)
    results = []
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
        results.append(
            {
                "test_id": vector.test_id,
                "held": vector.held,
                "expected": [list(row) for row in vector.expected],
                "rows": None if rows is None else [list(row) for row in rows],
                "error": error,
                "passed": rows == vector.expected,
            }
        )
    return {"gate_refusal": None, "constraint_met": constraint_met, "tests": results}


def _target_label(report: dict[str, object], family: str) -> str:
    tests = report["tests"]
    if report["gate_refusal"] is not None or not tests:
        return "gate_fail"
    ordinary = [item for item in tests if not item["held"]]
    held = [item for item in tests if item["held"]]
    if not ordinary or not held or not all(item["passed"] for item in ordinary):
        return "ordinary_fail"
    if family == "SQLite" and not report["constraint_met"]:
        return "ordinary_fail"
    if all(item["passed"] for item in held):
        return "full_pass"
    if family == "Python":
        qualified = [
            item["process_status"] == "returned"
            and not item["mutated"]
            and item["stdout"] == ""
            and item["stderr"] == ""
            for item in held
        ]
        if all(item["passed"] or miss for item, miss in zip(held, qualified, strict=True)) and any(qualified):
            return "boundary_miss"
    elif all(item["error"] is None for item in held) and any(not item["passed"] for item in held):
        return "boundary_miss"
    return "ordinary_fail"


@dataclass(frozen=True, slots=True)
class CallSpec:
    logical_index: int
    call_id: str
    family: str
    condition: str
    seed: int
    prompt: str


def schedule() -> tuple[CallSpec, ...]:
    calls = [
        CallSpec(1, "C-P1", "anchor", "anchor", 2001, ANCHOR_P1_PROMPT),
        CallSpec(2, "C-P2", "anchor", "anchor", 2002, ANCHOR_P2_PROMPT),
        CallSpec(3, "C-S1", "anchor", "anchor", 2003, ANCHOR_S1_PROMPT),
        CallSpec(4, "C-S2", "anchor", "anchor", 2004, ANCHOR_S2_PROMPT),
    ]
    prompts = {
        ("SQLite", "cold"): SQLITE_COLD_PROMPT,
        ("SQLite", "direct_rule"): SQLITE_DIRECT_PROMPT,
        ("Python", "cold"): PYTHON_COLD_PROMPT,
        ("Python", "direct_rule"): PYTHON_DIRECT_PROMPT,
    }
    index = 5
    for family in MODEL.family_order:
        for condition in ("cold", "direct_rule"):
            for repetition, seed in enumerate((2101, 2102, 2103), 1):
                calls.append(
                    CallSpec(
                        index,
                        f"{family}-{condition}-{repetition}",
                        family,
                        condition,
                        seed,
                        prompts[(family, condition)],
                    )
                )
                index += 1
    return tuple(calls)


def _score(spec: CallSpec, output: str) -> tuple[dict[str, object], str]:
    if spec.call_id == "C-P1":
        report = _python_report(output, "combine_labels", ANCHOR_P1_VECTORS)
        return report, "full_pass" if report["gate_refusal"] is None and all(item["passed"] for item in report["tests"]) else "anchor_fail"
    if spec.call_id == "C-P2":
        report = _python_report(output, "accept_mode", ANCHOR_P2_VECTORS)
        return report, "full_pass" if report["gate_refusal"] is None and all(item["passed"] for item in report["tests"]) else "anchor_fail"
    if spec.call_id == "C-S1":
        report = _sqlite_report(output, ANCHOR_S1_VECTORS)
        return report, "full_pass" if report["gate_refusal"] is None and all(item["passed"] for item in report["tests"]) else "anchor_fail"
    if spec.call_id == "C-S2":
        report = _sqlite_report(output, ANCHOR_S2_VECTORS)
        return report, "full_pass" if report["gate_refusal"] is None and all(item["passed"] for item in report["tests"]) else "anchor_fail"
    if spec.family == "Python":
        report = _python_report(
            output,
            "parse_versions" if spec.condition == "cold" else "parse_slots",
            PYTHON_COLD_VECTORS if spec.condition == "cold" else PYTHON_DIRECT_VECTORS,
        )
    else:
        report = _sqlite_report(
            output,
            SQLITE_COLD_VECTORS if spec.condition == "cold" else SQLITE_DIRECT_VECTORS,
            require_not_exists=spec.condition == "direct_rule",
        )
    return report, _target_label(report, spec.family)


Invoker = Callable[[ModelConfig, CallSpec], Attempt]


def invoke_with_retry(invoker: Invoker, spec: CallSpec) -> tuple[Attempt, ...]:
    first = invoker(MODEL, spec)
    if first.output:
        return (first,)
    first = replace(first, retry_reason="no_model_output")
    second = replace(
        invoker(MODEL, spec),
        attempt_index=2,
        retry_reason="no_model_output",
        retry_of_attempt=1,
    )
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


def run_model(
    invoker: Invoker,
    directory: Path,
    packet_receipt: dict[str, object] | None = None,
) -> dict[str, object]:
    directory.mkdir(parents=True, exist_ok=False)
    receipt = {} if packet_receipt is None else packet_receipt
    calls = []
    labels: dict[tuple[str, str], list[str]] = {}
    for spec in schedule():
        attempts = invoke_with_retry(invoker, spec)
        final = attempts[-1]
        report, label = _score(spec, final.output)
        for attempt in attempts:
            _write_attempt(
                directory,
                attempt,
                report if attempt is final else {},
                label if attempt is final else "retry_pending",
                receipt,
            )
        calls.append(
            {
                "logical_index": spec.logical_index,
                "call_id": spec.call_id,
                "family": spec.family,
                "condition": spec.condition,
                "seed": spec.seed,
                "label": label,
                "report": report,
            }
        )
        if spec.family == "anchor" and label != "full_pass":
            summary = {
                "model": asdict(MODEL),
                "packet_receipt": receipt,
                "terminal_result": "contract_unreliable",
                "stopping_call": spec.logical_index,
                "calls": calls,
                "family_cells": {},
            }
            (directory / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
            return summary
        if spec.family != "anchor":
            labels.setdefault((spec.family, spec.condition), []).append(label)
    cells = {
        family: family_label(
            tuple(labels[(family, "cold")]),
            tuple(labels[(family, "direct_rule")]),
        )
        for family in ("Python", "SQLite")
    }
    summary = {
        "model": asdict(MODEL),
        "packet_receipt": receipt,
        "terminal_result": terminal_label(cells),
        "stopping_call": 16,
        "calls": calls,
        "family_cells": cells,
    }
    (directory / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


LIVE_IDENTIFIER = "formation-admission-nemotron-successor"


def load_command() -> tuple[str, ...]:
    return (
        "lms",
        "load",
        MODEL.model_key,
        "--gpu",
        "max",
        "--context-length",
        "8192",
        "--parallel",
        "1",
        "--no-speculative-draft-mtp",
        "--identifier",
        LIVE_IDENTIFIER,
        "-y",
    )


def validate_loaded_instance(loaded: object) -> dict[str, object]:
    if (
        type(loaded) is not list
        or len(loaded) != 1
        or type(loaded[0]) is not dict
        or loaded[0].get("identifier") != LIVE_IDENTIFIER
        or loaded[0].get("selectedVariant") != MODEL.selected_variant
        or loaded[0].get("contextLength") != 8192
        or loaded[0].get("parallel") != 1
        or loaded[0].get("vision") is not False
    ):
        raise ValueError("exact_text_only_model_load_required")
    return loaded[0]


class LiveInvoker:
    def __init__(self, server_url: str = "http://127.0.0.1:1234/v1/chat/completions") -> None:
        self.identifier = LIVE_IDENTIFIER
        self.server_url = server_url

    def __call__(self, model: ModelConfig, spec: CallSpec) -> Attempt:
        if model != MODEL:
            raise ValueError("exact_nemotron_model_required")
        envelope = {
            "model": self.identifier,
            "messages": [{"role": "user", "content": spec.prompt}],
            **SAMPLING,
            "seed": spec.seed,
        }
        started = datetime.now(timezone.utc)
        clock = time.monotonic()
        request = Request(
            self.server_url,
            data=json.dumps(envelope).encode(),
            headers={"Content-Type": "application/json", "Authorization": "Bearer lm-studio"},
            method="POST",
        )
        with urlopen(request, timeout=180) as response:
            response_envelope = json.loads(response.read())
        elapsed = time.monotonic() - clock
        ended = datetime.now(timezone.utc)
        output = response_envelope["choices"][0]["message"].get("content") or ""
        return Attempt(
            spec.logical_index,
            1,
            spec.call_id,
            spec.family,
            spec.condition,
            spec.seed,
            spec.prompt,
            output,
            envelope,
            response_envelope,
            started.isoformat(),
            ended.isoformat(),
            elapsed,
            None,
            None,
        )


def run_live(evidence_directory: Path) -> dict[str, object]:
    evidence_directory.mkdir(parents=True, exist_ok=False)
    artifact_record = verify_artifact(MODEL)
    cli_version = subprocess.run(("lms", "--version"), check=True, capture_output=True, text=True).stdout.strip()
    runtime_inventory = subprocess.run(("lms", "runtime", "ls"), check=True, capture_output=True, text=True).stdout
    server_start = subprocess.run(("lms", "server", "start"), check=False, capture_output=True, text=True)
    if server_start.returncode != 0 and "already" not in (server_start.stdout + server_start.stderr).lower():
        raise ValueError("lm_studio_server_unavailable")
    server_receipt = {
        "command": ["lms", "server", "start"],
        "exit_code": server_start.returncode,
        "stdout": server_start.stdout,
        "stderr": server_start.stderr,
    }
    subprocess.run(("lms", "unload", "--all"), check=False, capture_output=True, text=True)
    try:
        command = load_command()
        load_process = subprocess.run(command, check=True, capture_output=True, text=True)
        loaded = json.loads(subprocess.run(("lms", "ps", "--json"), check=True, capture_output=True, text=True).stdout)
        loaded_instance = validate_loaded_instance(loaded)
        packet_receipt = {
            "model": asdict(MODEL),
            "artifact_verification": artifact_record,
            "cli_version": cli_version,
            "runtime_inventory": runtime_inventory,
            "server": server_receipt,
            "load": {
                "command": list(command),
                "exit_code": load_process.returncode,
                "stdout": load_process.stdout,
                "stderr": load_process.stderr,
                "instance": loaded_instance,
            },
            "text_only": True,
            "projector_attached": False,
            "speculative_decoding": False,
            "tools": False,
            "history_reuse": False,
        }
        model_summary = run_model(
            LiveInvoker(),
            evidence_directory / LIVE_IDENTIFIER,
            packet_receipt,
        )
    finally:
        subprocess.run(("lms", "unload", "--all"), check=False, capture_output=True, text=True)
    summary = {
        "protocol": "nemotron-admission-successor-v1",
        "evidence_class": "exploratory_only",
        "model": model_summary,
        "artifact_verification": artifact_record,
    }
    (evidence_directory / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the reviewed corrected Nemotron admission successor.")
    parser.add_argument("--evidence-directory", type=Path, required=True)
    parser.add_argument("--run-contact", action="store_true")
    arguments = parser.parse_args()
    if not arguments.run_contact:
        parser.error("--run-contact is required")
    print(json.dumps(run_live(arguments.evidence_directory), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
