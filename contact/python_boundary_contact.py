"""Restricted runner for the frozen Python boundary contact charter."""

from __future__ import annotations

import ast
import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

from contact.sqlite_contact import (
    Attempt,
    Invoker,
    live_invoker,
    invoke_with_retry,
    write_attempt,
)


CASE_ORDER = ("V2", "N1", "V1", "N2", "V3")
CONDITION_ORDER = ("cold", "raw", "lesson")
EXPLORATION_PROMPT = """Write this Python function:

    parse_limits(payload)

Contract:
- payload is a dictionary with exactly the keys "soft" and "hard";
- both values must be Python integers;
- 0 <= soft <= hard;
- return (soft, hard);
- raise ValueError for every invalid input.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence."""
PROMPTS = {
    "V1": """Write this Python function:

    parse_revisions(payload)

Contract:
- payload is a dictionary with exactly the keys "artifact_revision" and "authority_revision";
- both values must be Python integers;
- both values must be at least zero;
- return (artifact_revision, authority_revision);
- raise ValueError for every invalid input.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence.""",
    "V2": """Write this Python function:

    parse_window(payload)

Contract:
- payload is a list containing exactly two Python integers: low then high;
- low must be less than or equal to high;
- return (low, high);
- raise ValueError for every invalid input.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence.""",
    "V3": """Write this Python function:

    total_counts(payload)

Contract:
- payload is a dictionary with exactly the keys "primary" and "secondary";
- both values must be non-negative Python integers;
- return their integer sum;
- raise ValueError for every invalid input.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence.""",
    "N1": """Write this Python function:

    parse_feature_flags(payload)

Contract:
- payload is a dictionary with exactly the keys "audit" and "cache";
- both values must be Python booleans;
- return (audit, cache);
- raise ValueError for every invalid input.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence.""",
    "N2": """Write this Python function:

    parse_gate(payload)

Contract:
- payload is a tuple containing exactly two values: enabled then attempts;
- enabled must be a Python boolean;
- attempts must be a non-negative Python integer;
- return (enabled, attempts);
- raise ValueError for every invalid input.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence.""",
}
FUNCTION_NAMES = {
    "E1": "parse_limits",
    "V1": "parse_revisions",
    "V2": "parse_window",
    "V3": "total_counts",
    "N1": "parse_feature_flags",
    "N2": "parse_gate",
}
RAW_TEMPLATE = """Prior Python coding occurrence:

Task:
{task}

Implementation returned by the model:
{source}

Test report:
{report}

Use this prior occurrence only if it is relevant to the current task.

Current task follows.

{current}"""
LESSON_REQUEST_TEMPLATE = """Review this Python implementation after its external tests.

Task:
{task}

Implementation returned by the model:
{source}

Test report:
{report}

Explain what caused the failed tests. State any rule you infer from them. Do not solve or discuss any other task."""
LESSON_TEMPLATE = """Prior model-authored lesson:

{lesson}

Use this lesson only if it is relevant to the current task.

Current task follows.

{current}"""


@dataclass(frozen=True, slots=True)
class Vector:
    test_id: str
    input_repr: str
    expected: str
    return_repr: str | None = None
    return_type: str | None = None


def returns(test_id: str, input_repr: str, value_repr: str, type_name: str) -> Vector:
    return Vector(test_id, input_repr, f"return:{value_repr}", value_repr, type_name)


def refuses(test_id: str, input_repr: str) -> Vector:
    return Vector(test_id, input_repr, "raises:ValueError")


EXPLORATION_VECTORS = (
    returns("E-O01", "{'soft': 0, 'hard': 3}", "(0, 3)", "tuple"),
    returns("E-O02", "{'soft': 2, 'hard': 2}", "(2, 2)", "tuple"),
    refuses("E-O03", "None"), refuses("E-O04", "[0, 3]"),
    refuses("E-O05", "(0, 3)"), refuses("E-O06", "'x'"),
    refuses("E-O07", "{}"), refuses("E-O08", "{'soft': 0}"),
    refuses("E-O09", "{'hard': 3}"),
    refuses("E-O10", "{'soft': 0, 'hard': 3, 'mode': 'x'}"),
    refuses("E-O11", "{'soft': '0', 'hard': 3}"),
    refuses("E-O12", "{'soft': 0.0, 'hard': 3}"),
    refuses("E-O13", "{'soft': None, 'hard': 3}"),
    refuses("E-O14", "{'soft': [0], 'hard': 3}"),
    refuses("E-O15", "{'soft': 0, 'hard': '3'}"),
    refuses("E-O16", "{'soft': 0, 'hard': 3.0}"),
    refuses("E-O17", "{'soft': 0, 'hard': None}"),
    refuses("E-O18", "{'soft': 0, 'hard': [3]}"),
    refuses("E-O19", "{'soft': -1, 'hard': 3}"),
    refuses("E-O20", "{'soft': 0, 'hard': -1}"),
    refuses("E-O21", "{'soft': 4, 'hard': 3}"),
    refuses("E-H01", "{'soft': True, 'hard': 3}"),
    refuses("E-H02", "{'soft': 0, 'hard': False}"),
    refuses("E-H03", "{'soft': False, 'hard': True}"),
)


def _mapping_vectors(prefix: str, left: str, right: str, valid2: tuple[int, int], sum_result: bool = False):
    first_value = "3" if sum_result else "(0, 3)"
    second_value = "4" if sum_result else f"{valid2!r}"
    return (
        returns(f"{prefix}-01", repr({left: 0, right: 3}), first_value, "int" if sum_result else "tuple"),
        returns(f"{prefix}-02", repr({left: valid2[0], right: valid2[1]}), second_value, "int" if sum_result else "tuple"),
        refuses(f"{prefix}-03", "None"), refuses(f"{prefix}-04", "[0, 3]"),
        refuses(f"{prefix}-05", "{}"), refuses(f"{prefix}-06", repr({left: 0})),
        refuses(f"{prefix}-07", repr({right: 3})),
        refuses(f"{prefix}-08", repr({left: 0, right: 3, "other" if sum_result else "source": 1 if sum_result else "x"})),
        refuses(f"{prefix}-09", repr({left: "0", right: 3})),
        refuses(f"{prefix}-10", repr({left: 0, right: 3.0})),
        refuses(f"{prefix}-11", repr({left: None, right: 3})),
        refuses(f"{prefix}-12", repr({left: 0, right: [3]})),
        refuses(f"{prefix}-13", repr({left: -1, right: 3})),
        refuses(f"{prefix}-14", repr({left: 0, right: -1})),
        refuses(f"{prefix}-15", repr({left: True, right: 3})),
        refuses(f"{prefix}-16", repr({left: 0, right: False})),
        refuses(f"{prefix}-17", repr({left: False, right: 3})),
        refuses(f"{prefix}-18", repr({left: 0, right: True})),
    )


VECTORS = {
    "V1": _mapping_vectors("V1", "artifact_revision", "authority_revision", (8, 8)),
    "V3": _mapping_vectors("V3", "primary", "secondary", (2, 2), True),
    "V2": (
        returns("V2-01", "[0, 3]", "(0, 3)", "tuple"),
        returns("V2-02", "[2, 2]", "(2, 2)", "tuple"),
        refuses("V2-03", "None"), refuses("V2-04", "(0, 3)"),
        refuses("V2-05", "{'low': 0, 'high': 3}"), refuses("V2-06", "[]"),
        refuses("V2-07", "[1]"), refuses("V2-08", "[1, 2, 3]"),
        refuses("V2-09", "['0', 3]"), refuses("V2-10", "[0.0, 3]"),
        refuses("V2-11", "[None, 3]"), refuses("V2-12", "[0, '3']"),
        refuses("V2-13", "[0, 3.0]"), refuses("V2-14", "[0, None]"),
        refuses("V2-15", "[4, 3]"), refuses("V2-16", "[True, 3]"),
        refuses("V2-17", "[0, False]"), refuses("V2-18", "[False, 3]"),
        refuses("V2-19", "[0, True]"),
    ),
    "N1": (
        returns("N1-01", "{'audit': False, 'cache': False}", "(False, False)", "tuple"),
        returns("N1-02", "{'audit': False, 'cache': True}", "(False, True)", "tuple"),
        returns("N1-03", "{'audit': True, 'cache': False}", "(True, False)", "tuple"),
        returns("N1-04", "{'audit': True, 'cache': True}", "(True, True)", "tuple"),
        refuses("N1-05", "None"), refuses("N1-06", "[False, True]"),
        refuses("N1-07", "{}"), refuses("N1-08", "{'audit': False}"),
        refuses("N1-09", "{'cache': True}"),
        refuses("N1-10", "{'audit': False, 'cache': True, 'other': False}"),
        refuses("N1-11", "{'audit': 0, 'cache': True}"),
        refuses("N1-12", "{'audit': 1, 'cache': True}"),
        refuses("N1-13", "{'audit': False, 'cache': 0}"),
        refuses("N1-14", "{'audit': False, 'cache': 1}"),
        refuses("N1-15", "{'audit': 'false', 'cache': True}"),
        refuses("N1-16", "{'audit': False, 'cache': None}"),
    ),
    "N2": (
        returns("N2-01", "(True, 0)", "(True, 0)", "tuple"),
        returns("N2-02", "(False, 3)", "(False, 3)", "tuple"),
        refuses("N2-03", "None"), refuses("N2-04", "[True, 0]"),
        refuses("N2-05", "()"), refuses("N2-06", "(True,)"),
        refuses("N2-07", "(True, 0, 1)"), refuses("N2-08", "(0, 0)"),
        refuses("N2-09", "(1, 0)"), refuses("N2-10", "('true', 0)"),
        refuses("N2-11", "(None, 0)"), refuses("N2-12", "(True, True)"),
        refuses("N2-13", "(False, False)"), refuses("N2-14", "(True, '0')"),
        refuses("N2-15", "(True, 0.0)"), refuses("N2-16", "(True, None)"),
        refuses("N2-17", "(True, -1)"),
    ),
}


DISALLOWED_NODES = (
    ast.AsyncFunctionDef, ast.ClassDef, ast.Global, ast.Import, ast.ImportFrom,
    ast.Lambda, ast.Nonlocal, ast.Await, ast.Yield, ast.YieldFrom,
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
        len(arguments.posonlyargs) != 0
        or len(arguments.args) != 1
        or arguments.args[0].arg != "payload"
        or arguments.vararg is not None
        or arguments.kwarg is not None
        or arguments.kwonlyargs
        or arguments.defaults
    ):
        return "exact_payload_signature_required"
    for node in ast.walk(tree):
        if isinstance(node, DISALLOWED_NODES):
            return "disallowed_syntax"
        if isinstance(node, ast.FunctionDef) and node is not function:
            return "nested_definition"
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            return "dunder_attribute"
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in DISALLOWED_CALLS
        ):
            return "disallowed_call"
    return None


CHILD = r'''import ast, copy, io, json, resource, sys
resource.setrlimit(resource.RLIMIT_CPU, (1, 2))
resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
request = json.loads(sys.stdin.read())
allowed = {name: value for name, value in {
    "ValueError": ValueError, "TypeError": TypeError, "bool": bool,
    "dict": dict, "int": int, "isinstance": isinstance, "len": len,
    "list": list, "set": set, "str": str, "tuple": tuple, "type": type,
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
expected_raise = request["expected"] == "raises:ValueError"
if expected_raise:
    passed = status == "raised" and exception_type == "ValueError"
else:
    passed = status == "returned" and type(returned).__name__ == request["return_type"] and repr(returned) == request["return_repr"]
if stdout.getvalue() or stderr.getvalue() or mutated:
    passed = False
result = {
    "exception_type": exception_type, "expected": request["expected"],
    "input_repr": request["input_repr"], "mutated": mutated,
    "passed": passed, "process_status": status,
    "returned_repr": None if status != "returned" else repr(returned),
    "stderr": stderr.getvalue(), "stdout": stdout.getvalue(),
    "test_id": request["test_id"],
}
oldout.write(json.dumps(result, ensure_ascii=True, separators=(",", ":"), sort_keys=True))
'''


def refused_results(vectors: tuple[Vector, ...]) -> tuple[dict[str, object], ...]:
    return tuple({
        "exception_type": None, "expected": vector.expected,
        "input_repr": vector.input_repr, "mutated": False, "passed": False,
        "process_status": "refused", "returned_repr": None, "stderr": "",
        "stdout": "", "test_id": vector.test_id,
    } for vector in vectors)


def run_vector(source: str, function_name: str, vector: Vector) -> dict[str, object]:
    request = {
        "source": source.strip(), "function_name": function_name,
        "test_id": vector.test_id, "input_repr": vector.input_repr,
        "expected": vector.expected, "return_repr": vector.return_repr,
        "return_type": vector.return_type,
    }
    with tempfile.TemporaryDirectory(prefix="formation-python-vector-") as workspace:
        try:
            process = subprocess.run(
                (sys.executable, "-I", "-S", "-c", CHILD),
                input=json.dumps(request), capture_output=True, text=True,
                cwd=workspace, timeout=1.0, env={"PATH": ""},
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


def evaluate_source(
    source: str, case_id: str
) -> tuple[dict[str, object], dict[str, object]]:
    vectors = EXPLORATION_VECTORS if case_id == "E1" else VECTORS[case_id]
    function_name = FUNCTION_NAMES[case_id]
    refusal = validate_source(source, function_name)
    durations: list[dict[str, object]] = []
    if refusal:
        tests = refused_results(vectors)
        durations = [
            {"test_id": vector.test_id, "elapsed_seconds": 0.0}
            for vector in vectors
        ]
    else:
        collected = []
        for vector in vectors:
            started = time.monotonic()
            collected.append(run_vector(source, function_name, vector))
            durations.append({
                "test_id": vector.test_id,
                "elapsed_seconds": time.monotonic() - started,
            })
        tests = tuple(collected)
    report = {
        "function_name": function_name,
        "python_version": sys.version.split()[0],
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "tests": list(tests),
    }
    diagnostics = {
        "source_refusal": refusal,
        "test_durations": durations,
    }
    return report, diagnostics


def report_source(source: str, case_id: str) -> dict[str, object]:
    return evaluate_source(source, case_id)[0]


def encode_report(report: dict[str, object]) -> str:
    return json.dumps(report, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def exploration_shape(report: dict[str, object]) -> tuple[bool, bool]:
    tests = report["tests"]
    ordinary = [item for item in tests if item["test_id"].startswith("E-O")]
    held = [item for item in tests if item["test_id"].startswith("E-H")]
    ordinary_complete = bool(ordinary) and all(item["passed"] for item in ordinary)
    held_complete = bool(held) and all(item["passed"] for item in held)
    held_normal_return = any(
        not item["passed"] and item["process_status"] == "returned"
        for item in held
    )
    return ordinary_complete and held_normal_return, ordinary_complete and held_complete


def classify_exploration(reports: tuple[dict[str, object], ...]) -> str:
    shapes = tuple(exploration_shape(report) for report in reports)
    if sum(shape[0] for shape in shapes) >= 2:
        return "engaged"
    if sum(shape[1] for shape in shapes) >= 2:
        return "not_engaged"
    return "unstable"


def first_acquisition_index(reports: tuple[dict[str, object], ...]) -> int:
    for index, report in enumerate(reports, 1):
        if exploration_shape(report)[0]:
            return index
    raise ValueError("engaged_acquisition_missing")


def assemble_prompt(condition: str, case_id: str, acquisition_source: str, acquisition_report: str, lesson: str) -> str:
    current = PROMPTS[case_id]
    if condition == "cold":
        return current
    if condition == "raw":
        return RAW_TEMPLATE.format(task=EXPLORATION_PROMPT, source=acquisition_source, report=acquisition_report, current=current)
    if condition == "lesson":
        return LESSON_TEMPLATE.format(lesson=lesson, current=current)
    raise ValueError("unknown_condition")


class ContactProtocolError(ValueError):
    pass


def _final_attempt(
    invoker: Invoker,
    directory: Path,
    prompt: str,
    logical_index: int,
    condition: str,
    case_id: str,
) -> Attempt:
    attempts = invoke_with_retry(
        invoker, prompt, logical_index, condition, case_id
    )
    for attempt in attempts:
        write_attempt(directory, attempt)
    return attempts[-1]


def _report_record(
    report: dict[str, object], diagnostics: dict[str, object]
) -> dict[str, object]:
    tests = report["tests"]
    return {
        "report": report,
        "passed_tests": sum(1 for item in tests if item["passed"]),
        "total_tests": len(tests),
        "complete": bool(tests) and all(item["passed"] for item in tests),
        "oracle_diagnostics": diagnostics,
    }


def _write_summary(directory: Path, summary: dict[str, object]) -> None:
    (directory / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )


def run_protocol(invoker: Invoker, evidence_directory: Path) -> dict[str, object]:
    evidence_directory.mkdir(parents=True, exist_ok=False)
    exploration_attempts: list[Attempt] = []
    exploration_reports: list[dict[str, object]] = []
    exploration_diagnostics: list[dict[str, object]] = []
    for logical_index in range(1, 4):
        attempt = _final_attempt(
            invoker,
            evidence_directory,
            EXPLORATION_PROMPT,
            logical_index,
            "exploration",
            "E1",
        )
        exploration_attempts.append(attempt)
        report, diagnostics = evaluate_source(attempt.output, "E1")
        exploration_reports.append(report)
        exploration_diagnostics.append(diagnostics)

    reports = tuple(exploration_reports)
    status = classify_exploration(reports)
    summary: dict[str, object] = {
        "protocol": "python-boundary-contact-v0",
        "model": "composer-2.5",
        "exploration_status": status,
        "exploration": [
            {
                "call_index": index,
                "acquisition_shape": exploration_shape(report)[0],
                "all_tests_complete": exploration_shape(report)[1],
                "input_characters": len(exploration_attempts[index - 1].prompt),
                "output_characters": len(exploration_attempts[index - 1].output),
                **_report_record(report, exploration_diagnostics[index - 1]),
            }
            for index, report in enumerate(reports, 1)
        ],
        "validation": [],
    }
    if status != "engaged":
        summary["contact_status"] = "stopped"
        _write_summary(evidence_directory, summary)
        return summary

    acquisition_index = first_acquisition_index(reports)
    acquisition_source = exploration_attempts[acquisition_index - 1].output
    acquisition_report = encode_report(reports[acquisition_index - 1])
    summary["acquisition_call_index"] = acquisition_index
    summary["acquisition_source_sha256"] = hashlib.sha256(
        acquisition_source.encode()
    ).hexdigest()
    summary["acquisition_report_sha256"] = hashlib.sha256(
        acquisition_report.encode()
    ).hexdigest()

    lesson_prompt = LESSON_REQUEST_TEMPLATE.format(
        task=EXPLORATION_PROMPT,
        source=acquisition_source,
        report=acquisition_report,
    )
    lesson_attempt = _final_attempt(
        invoker,
        evidence_directory,
        lesson_prompt,
        4,
        "lesson_authorship",
        "E1",
    )
    if not lesson_attempt.output:
        summary["contact_status"] = "operational_failure"
        _write_summary(evidence_directory, summary)
        return summary
    lesson = lesson_attempt.output
    summary["lesson_sha256"] = hashlib.sha256(lesson.encode()).hexdigest()
    summary["lesson_input_characters"] = len(lesson_attempt.prompt)
    summary["lesson_output_characters"] = len(lesson)

    validation: list[dict[str, object]] = []
    logical_index = 5
    for condition in CONDITION_ORDER:
        for case_id in CASE_ORDER:
            prompt = assemble_prompt(
                condition,
                case_id,
                acquisition_source,
                acquisition_report,
                lesson,
            )
            attempt = _final_attempt(
                invoker,
                evidence_directory,
                prompt,
                logical_index,
                condition,
                case_id,
            )
            report, diagnostics = evaluate_source(attempt.output, case_id)
            validation.append(
                {
                    "call_index": logical_index,
                    "condition": condition,
                    "case_id": case_id,
                    "input_characters": len(attempt.prompt),
                    "output_characters": len(attempt.output),
                    **_report_record(report, diagnostics),
                }
            )
            logical_index += 1
    if logical_index != 20:
        raise ContactProtocolError("nineteen_logical_calls_required")
    summary["validation"] = validation
    summary["contact_status"] = "complete"
    summary["success_counts"] = {
        condition: sum(
            1
            for item in validation
            if item["condition"] == condition and item["complete"]
        )
        for condition in CONDITION_ORDER
    }
    _write_summary(evidence_directory, summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the reviewed strict Python boundary contact protocol."
    )
    parser.add_argument("--evidence-directory", type=Path, required=True)
    parser.add_argument(
        "--run-contact",
        action="store_true",
        help="Acknowledge that this command will spend the frozen model-call budget.",
    )
    arguments = parser.parse_args()
    if not arguments.run_contact:
        parser.error("--run-contact is required")
    summary = run_protocol(live_invoker, arguments.evidence_directory)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
