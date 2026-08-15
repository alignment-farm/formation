"""Execute the frozen SQLite nullable anti-join contact charter."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import tempfile
import time
from typing import Callable


MODEL = "composer-2.5"
CASE_ORDER = ("V2", "N1", "V1", "N2", "V3")
CONDITION_ORDER = ("cold", "raw", "lesson")
TASK_TEMPLATE = """You are writing one SQLite query.

Database:
{schema}

Question: {question}

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence."""
RAW_TEMPLATE = """Prior SQLite occurrence:

Task:
{task}

Query returned by the model:
{query}

SQLite rows:
{rows}

External check: incorrect.

Use this prior occurrence only if it is relevant to the current task.

Current task follows.

{current}"""
LESSON_REQUEST_TEMPLATE = """Review this SQLite attempt after its external result.

Task:
{task}

Query returned by the model:
{query}

SQLite rows:
{rows}

External check: incorrect.

Explain what caused this result. State any rule you infer from it. Do not solve or discuss any other task."""
LESSON_TEMPLATE = """Prior model-authored lesson:

{lesson}

Use this lesson only if it is relevant to the current task.

Current task follows.

{current}"""


@dataclass(frozen=True, slots=True)
class Task:
    case_id: str
    schema: str
    question: str
    oracle_rows: tuple[tuple[object, ...], ...]
    require_filtered_not_in: bool = False

    def prompt(self) -> str:
        return TASK_TEMPLATE.format(schema=self.schema, question=self.question)


EXPLORATION = Task(
    "E1",
    """CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER);
INSERT INTO customers VALUES (1,'Ada'),(2,'Bex'),(3,'Cy');
INSERT INTO orders VALUES (10,1),(11,NULL);""",
    "return customer names for customers who have never placed an order, ordered by name.",
    (("Bex",), ("Cy",)),
)
TASKS = {
    "V1": Task(
        "V1",
        """CREATE TABLE packages(id INTEGER PRIMARY KEY, label TEXT NOT NULL);
CREATE TABLE scans(id INTEGER PRIMARY KEY, package_ref INTEGER);
INSERT INTO packages VALUES (1,'amber'),(2,'blue'),(3,'copper');
INSERT INTO scans VALUES (20,2),(21,NULL);""",
        "return labels of packages that have never been scanned, ordered by label.",
        (("amber",), ("copper",)),
    ),
    "V2": Task(
        "V2",
        """CREATE TABLE authors(id INTEGER PRIMARY KEY, handle TEXT NOT NULL);
CREATE TABLE reviews(id INTEGER PRIMARY KEY, author_id INTEGER);
INSERT INTO authors VALUES (4,'elm'),(5,'fir'),(6,'gum');
INSERT INTO reviews VALUES (30,4),(31,NULL),(32,6);""",
        "return handles of authors with no review, ordered by handle.",
        (("fir",),),
    ),
    "V3": Task(
        "V3",
        """CREATE TABLE ports(number INTEGER PRIMARY KEY);
CREATE TABLE reservations(port_number INTEGER);
INSERT INTO ports VALUES (8000),(8001),(8002),(8003);
INSERT INTO reservations VALUES (8001),(NULL),(8003);""",
        "return unreserved port numbers in ascending order.",
        ((8000,), (8002,)),
    ),
    "N1": Task(
        "N1",
        """CREATE TABLE jobs(id INTEGER PRIMARY KEY, state TEXT NOT NULL);
INSERT INTO jobs VALUES (1,'ready'),(2,'held'),(3,'done'),(4,'ready');""",
        "return job ids whose state is neither held nor done, ordered by id.",
        ((1,), (4,)),
    ),
    "N2": Task(
        "N2",
        """CREATE TABLE devices(id INTEGER PRIMARY KEY, label TEXT NOT NULL);
CREATE TABLE leases(device_id INTEGER);
INSERT INTO devices VALUES (1,'a'),(2,'b'),(3,'c');
INSERT INTO leases VALUES (1),(NULL);""",
        "using NOT IN with a subquery that contains the exact filter WHERE device_id IS NOT NULL, return unleased device labels ordered by label.",
        (("b",), ("c",)),
        True,
    ),
}


class ContactProtocolError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Score:
    accepted_query: bool
    correct_rows: bool
    constraint_met: bool
    rows: tuple[tuple[object, ...], ...] | None
    refusal: str | None

    @property
    def passed(self) -> bool:
        return self.accepted_query and self.correct_rows and self.constraint_met


def encode_rows(rows: tuple[tuple[object, ...], ...]) -> str:
    return json.dumps(
        [list(row) for row in rows], ensure_ascii=True, separators=(",", ":")
    )


def normalize_ascii_whitespace(value: str) -> str:
    return re.sub(r"[\t\n\r\f\v ]+", " ", value).strip()


def score_query(task: Task, raw_output: str) -> Score:
    query = raw_output.strip()
    if not query:
        return Score(False, False, False, None, "empty_output")
    if "```" in query:
        return Score(False, False, False, None, "markdown_fence")
    first = re.match(r"[A-Za-z]+", query)
    if first is None or first.group(0).upper() != "SELECT":
        return Score(False, False, False, None, "select_required")
    connection = sqlite3.connect(":memory:")
    try:
        connection.executescript(task.schema)
        connection.execute("PRAGMA query_only=ON")
        try:
            rows = tuple(connection.execute(query).fetchall())
        except sqlite3.Error as error:
            return Score(False, False, False, None, f"sqlite:{type(error).__name__}")
    finally:
        connection.close()
    normalized = normalize_ascii_whitespace(query).upper()
    constraint_met = not task.require_filtered_not_in or (
        "NOT IN" in normalized and "WHERE DEVICE_ID IS NOT NULL" in normalized
    )
    return Score(True, rows == task.oracle_rows, constraint_met, rows, None)


def mechanically_engaged(raw_output: str, score: Score) -> bool:
    normalized = normalize_ascii_whitespace(raw_output).upper()
    return (
        score.accepted_query
        and "NOT IN" in normalized
        and score.rows == ()
        and not score.correct_rows
    )


def classify_exploration(outputs: tuple[str, str, str]) -> tuple[str, tuple[Score, ...]]:
    scores = tuple(score_query(EXPLORATION, output) for output in outputs)
    engaged = sum(
        mechanically_engaged(output, score)
        for output, score in zip(outputs, scores, strict=True)
    )
    correct = sum(score.passed for score in scores)
    if engaged >= 2:
        return "engaged", scores
    if correct >= 2:
        return "not_engaged", scores
    return "unstable", scores


def first_acquisition_index(outputs: tuple[str, str, str], scores: tuple[Score, ...]) -> int:
    for index, (output, score) in enumerate(zip(outputs, scores, strict=True), 1):
        if mechanically_engaged(output, score):
            return index
    raise ContactProtocolError("engaged_acquisition_missing")


@dataclass(frozen=True, slots=True)
class Attempt:
    logical_index: int
    attempt_index: int
    condition: str
    case_id: str
    prompt: str
    output: str
    command: tuple[str, ...]
    workspace: str
    workspace_was_empty: bool
    started_at: str
    ended_at: str
    elapsed_seconds: float
    exit_code: int
    agent_version: str
    no_resume: bool
    retry_reason: str | None
    retry_of_attempt: int | None


Invoker = Callable[[str, int, str, str], Attempt]


def live_invoker(prompt: str, logical_index: int, condition: str, case_id: str) -> Attempt:
    with tempfile.TemporaryDirectory(prefix="formation-sqlite-contact-") as workspace:
        workspace_path = Path(workspace)
        was_empty = not any(workspace_path.iterdir())
        command = (
            "agent",
            "-p",
            "--mode",
            "ask",
            "--model",
            MODEL,
            "--trust",
            "--workspace",
            workspace,
            prompt,
        )
        version = subprocess.run(
            ("agent", "--version"), capture_output=True, text=True, check=True
        ).stdout.strip()
        started = datetime.now(timezone.utc)
        clock = time.monotonic()
        process = subprocess.run(command, capture_output=True, text=True)
        elapsed = time.monotonic() - clock
        ended = datetime.now(timezone.utc)
        return Attempt(
            logical_index,
            1,
            condition,
            case_id,
            prompt,
            process.stdout,
            command[:-1] + ("<exact-prompt>",),
            workspace,
            was_empty,
            started.isoformat(),
            ended.isoformat(),
            elapsed,
            process.returncode,
            version,
            True,
            None,
            None,
        )


def write_attempt(directory: Path, attempt: Attempt) -> None:
    stem = (
        f"{attempt.logical_index:02d}-{attempt.condition}-{attempt.case_id}"
        f"-a{attempt.attempt_index}"
    )
    (directory / f"{stem}.prompt.txt").write_text(attempt.prompt)
    (directory / f"{stem}.output.txt").write_text(attempt.output)
    metadata = asdict(attempt)
    metadata["prompt_sha256"] = hashlib.sha256(attempt.prompt.encode()).hexdigest()
    metadata["output_sha256"] = hashlib.sha256(attempt.output.encode()).hexdigest()
    metadata.pop("prompt")
    metadata.pop("output")
    (directory / f"{stem}.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    )


def invoke_with_retry(
    invoker: Invoker,
    prompt: str,
    logical_index: int,
    condition: str,
    case_id: str,
) -> tuple[Attempt, ...]:
    first = invoker(prompt, logical_index, condition, case_id)
    if first.output:
        return (first,)
    first = replace(first, retry_reason="no_model_output")
    second = invoker(prompt, logical_index, condition, case_id)
    second = replace(
        second,
        attempt_index=2,
        retry_reason="no_model_output",
        retry_of_attempt=1,
    )
    return (first, second)


def assemble_validation_prompt(
    condition: str,
    task: Task,
    acquisition_prompt: str,
    acquisition_query: str,
    acquisition_rows: str,
    lesson: str,
) -> str:
    current = task.prompt()
    if condition == "cold":
        return current
    if condition == "raw":
        return RAW_TEMPLATE.format(
            task=acquisition_prompt,
            query=acquisition_query,
            rows=acquisition_rows,
            current=current,
        )
    if condition == "lesson":
        return LESSON_TEMPLATE.format(lesson=lesson, current=current)
    raise ContactProtocolError("unknown_condition")


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


def _score_record(score: Score) -> dict[str, object]:
    return {
        "accepted_query": score.accepted_query,
        "correct_rows": score.correct_rows,
        "constraint_met": score.constraint_met,
        "passed": score.passed,
        "rows": None if score.rows is None else [list(row) for row in score.rows],
        "refusal": score.refusal,
    }


def run_protocol(invoker: Invoker, evidence_directory: Path) -> dict[str, object]:
    evidence_directory.mkdir(parents=True, exist_ok=False)
    exploration_attempts = []
    for logical_index in range(1, 4):
        exploration_attempts.append(
            _final_attempt(
                invoker,
                evidence_directory,
                EXPLORATION.prompt(),
                logical_index,
                "exploration",
                "E1",
            )
        )
    outputs = tuple(attempt.output for attempt in exploration_attempts)
    if len(outputs) != 3:
        raise ContactProtocolError("three_exploration_outputs_required")
    status, scores = classify_exploration(outputs)
    summary: dict[str, object] = {
        "protocol": "sqlite-nullable-antijoin-contact-v0",
        "model": MODEL,
        "exploration_status": status,
        "exploration": [
            {
                "call_index": index,
                "score": _score_record(score),
                "mechanically_engaged": mechanically_engaged(output, score),
            }
            for index, (output, score) in enumerate(
                zip(outputs, scores, strict=True), 1
            )
        ],
        "validation": [],
    }
    if status != "engaged":
        _write_summary(evidence_directory, summary)
        return summary

    acquisition_index = first_acquisition_index(outputs, scores)
    acquisition_query = outputs[acquisition_index - 1]
    acquisition_score = score_query(EXPLORATION, acquisition_query)
    if acquisition_score.rows is None:
        raise ContactProtocolError("acquisition_rows_required")
    acquisition_rows = encode_rows(acquisition_score.rows)
    summary["acquisition_call_index"] = acquisition_index
    summary["acquisition_query"] = acquisition_query
    summary["acquisition_rows"] = acquisition_rows
    summary["acquisition_oracle_rows"] = encode_rows(EXPLORATION.oracle_rows)
    summary["sqlite_version"] = sqlite3.sqlite_version

    lesson_prompt = LESSON_REQUEST_TEMPLATE.format(
        task=EXPLORATION.prompt(),
        query=acquisition_query,
        rows=acquisition_rows,
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

    logical_index = 5
    validation = []
    for condition in CONDITION_ORDER:
        for case_id in CASE_ORDER:
            task = TASKS[case_id]
            prompt = assemble_validation_prompt(
                condition,
                task,
                EXPLORATION.prompt(),
                acquisition_query,
                acquisition_rows,
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
            score = score_query(task, attempt.output)
            validation.append(
                {
                    "call_index": logical_index,
                    "condition": condition,
                    "case_id": case_id,
                    "score": _score_record(score),
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
            if item["condition"] == condition and item["score"]["passed"]
        )
        for condition in CONDITION_ORDER
    }
    _write_summary(evidence_directory, summary)
    return summary


def _write_summary(directory: Path, summary: dict[str, object]) -> None:
    (directory / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the reviewed SQLite cold-contact protocol."
    )
    parser.add_argument(
        "--evidence-directory", type=Path, required=True
    )
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
