"""Run the reviewed paired bare-versus-JSON-schema interface trial."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from contact.gemma_contract_staircase import (
    MODELS,
    SAMPLING,
    ModelConfig,
    exact_equal,
    load_command,
    score_output,
    validate_loaded_instance,
    verify_artifact,
)


SELECTION_PROMPT = """Compute the requested result from this JSON input:
{"records":[{"tag":"alder","open":true,"rank":2},{"tag":"birch","open":false,"rank":8},{"tag":"clover","open":true,"rank":5},{"tag":"drift","open":true,"rank":1}]}

Return tags of records whose open value is true and whose rank is at least 2. Sort the tags alphabetically.
Return exactly one JSON object with the single key "answer". Its value must be a JSON array of strings. Return no prose or Markdown fence.
Your complete response has a limit of 256 tokens."""

UPDATE_PROMPT = """Compute the requested result from this JSON input:
{"start":17,"operations":[{"kind":"subtract","value":4},{"kind":"double"},{"kind":"add","value":3}]}

Begin with start. Apply the operations from left to right: subtract removes value, double multiplies the current result by 2, and add increases it by value. Return the final integer.
Return exactly one JSON object with the single key "answer". Return no prose or Markdown fence.
Your complete response has a limit of 256 tokens."""

SELECTION_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "selection_answer",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {"answer": {"type": "array", "items": {"type": "string"}}},
            "required": ["answer"],
            "additionalProperties": False,
        },
    },
}

UPDATE_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "update_answer",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {"answer": {"type": "integer"}},
            "required": ["answer"],
            "additionalProperties": False,
        },
    },
}


@dataclass(frozen=True, slots=True)
class Task:
    task_id: str
    seed: int
    prompt: str
    oracle_answer: object
    response_format: dict[str, object]


TASKS = (
    Task("selection", 4001, SELECTION_PROMPT, ["alder", "clover"], SELECTION_SCHEMA),
    Task("ordered_update", 4002, UPDATE_PROMPT, 29, UPDATE_SCHEMA),
)


@dataclass(frozen=True, slots=True)
class LogicalCall:
    logical_index: int
    task: Task
    condition: str

    @property
    def call_id(self) -> str:
        return f"{self.task.task_id}-{self.condition}"


def schedule(model: ModelConfig) -> tuple[LogicalCall, ...]:
    conditions = ("bare", "constrained") if model == MODELS[0] else ("constrained", "bare")
    return tuple(
        LogicalCall(index, task, condition)
        for index, (task, condition) in enumerate(
            ((task, condition) for task in TASKS for condition in conditions), start=1
        )
    )


def request_envelope(model: ModelConfig, call: LogicalCall) -> dict[str, object]:
    envelope = {
        "model": model.live_identifier,
        "messages": [{"role": "user", "content": call.task.prompt}],
        **SAMPLING,
        "seed": call.task.seed,
    }
    if call.condition == "constrained":
        envelope["response_format"] = call.task.response_format
    return envelope


def assert_pair_isolation(model: ModelConfig, task: Task) -> None:
    bare = request_envelope(model, LogicalCall(0, task, "bare"))
    constrained = request_envelope(model, LogicalCall(0, task, "constrained"))
    if "response_format" in bare or constrained.get("response_format") != task.response_format:
        raise ValueError("request_contract_rejected")
    stripped = {key: value for key, value in constrained.items() if key != "response_format"}
    if not exact_equal(bare, stripped):
        raise ValueError("request_contract_rejected")


PAIR_LABELS = {
    ("invalid", "valid_correct"): "invalid_to_correct",
    ("invalid", "valid_wrong"): "invalid_to_wrong",
    ("invalid", "invalid"): "invalid_to_invalid",
    ("valid_wrong", "valid_correct"): "wrong_to_correct",
    ("valid_wrong", "valid_wrong"): "wrong_to_wrong",
    ("valid_wrong", "invalid"): "wrong_to_invalid",
    ("valid_correct", "valid_correct"): "correct_to_correct",
    ("valid_correct", "valid_wrong"): "correct_to_wrong",
    ("valid_correct", "invalid"): "correct_to_invalid",
}


def call_state(call_label: str) -> str:
    return {
        "gate_fail": "invalid",
        "wrong_answer": "valid_wrong",
        "full_pass": "valid_correct",
    }[call_label]


@dataclass(frozen=True, slots=True)
class Attempt:
    logical_index: int
    attempt_index: int
    call_id: str
    task_id: str
    condition: str
    seed: int
    model_key: str
    live_identifier: str
    prompt: str
    output: str
    request_envelope: dict[str, object]
    response_envelope: dict[str, object]
    started_at: str
    ended_at: str
    elapsed_seconds: float
    retry_reason: str | None = None
    retry_of_attempt: int | None = None


Invoker = Callable[[ModelConfig, LogicalCall], Attempt]


class ContactAbort(RuntimeError):
    def __init__(self, reason: str, attempt: Attempt | None = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.attempt = attempt
        self.prior_attempts: tuple[Attempt, ...] = ()


def invoke_with_retry(invoker: Invoker, model: ModelConfig, call: LogicalCall) -> tuple[Attempt, ...]:
    first = invoker(model, call)
    if first.output != "":
        return (first,)
    first = replace(first, retry_reason="no_model_content")
    try:
        second = replace(
            invoker(model, call), attempt_index=2,
            retry_reason="no_model_content", retry_of_attempt=1,
        )
    except ContactAbort as abort:
        abort.prior_attempts = (first,)
        if abort.attempt is not None:
            abort.attempt = replace(
                abort.attempt, attempt_index=2,
                retry_reason="no_model_content", retry_of_attempt=1,
            )
        raise
    return (first, second)


def _write_attempt(
    directory: Path,
    attempt: Attempt,
    report: dict[str, object] | None,
    oracle: object,
    response_format: dict[str, object] | None,
    packet_receipt: dict[str, object],
) -> None:
    stem = f"{attempt.logical_index:02d}-{attempt.call_id}-a{attempt.attempt_index}"
    (directory / f"{stem}.prompt.txt").write_text(attempt.prompt)
    (directory / f"{stem}.output.txt").write_text(attempt.output)
    record = asdict(attempt)
    record.update({
        "prompt_sha256": hashlib.sha256(attempt.prompt.encode()).hexdigest(),
        "output_sha256": hashlib.sha256(attempt.output.encode()).hexdigest(),
        "packet_receipt": packet_receipt,
        "response_format": response_format,
        "gate_refusal": None if report is None else report["gate_refusal"],
        "decoded_answer": None if report is None else report["decoded_answer"],
        "oracle_answer": oracle,
        "call_label": "retry_pending" if report is None else report["call_label"],
        "call_state": None if report is None else call_state(str(report["call_label"])),
    })
    record.pop("prompt")
    record.pop("output")
    (directory / f"{stem}.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")


def _write_abort_attempt(
    directory: Path, attempt: Attempt, oracle: object,
    response_format: dict[str, object] | None, packet_receipt: dict[str, object],
) -> None:
    stem = f"{attempt.logical_index:02d}-{attempt.call_id}-a{attempt.attempt_index}"
    (directory / f"{stem}.prompt.txt").write_text(attempt.prompt)
    (directory / f"{stem}.output.txt").write_text(attempt.output)
    record = asdict(attempt)
    record.update({
        "prompt_sha256": hashlib.sha256(attempt.prompt.encode()).hexdigest(),
        "output_sha256": hashlib.sha256(attempt.output.encode()).hexdigest(),
        "packet_receipt": packet_receipt, "response_format": response_format,
        "gate_refusal": None, "decoded_answer": None, "oracle_answer": oracle,
        "call_label": None, "call_state": None,
    })
    record.pop("prompt")
    record.pop("output")
    (directory / f"{stem}.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")


def _pair_records(model: ModelConfig, calls: list[dict[str, object]]) -> list[dict[str, object]]:
    pairs = []
    for task in TASKS:
        members = {item["condition"]: item for item in calls if item["task_id"] == task.task_id}
        if set(members) != {"bare", "constrained"}:
            continue
        bare, constrained = members["bare"], members["constrained"]
        key = (str(bare["call_state"]), str(constrained["call_state"]))
        pairs.append({
            "model_key": model.model_key,
            "task_id": task.task_id,
            "bare_call_id": bare["call_id"],
            "bare_call_state": bare["call_state"],
            "constrained_call_id": constrained["call_id"],
            "constrained_call_state": constrained["call_state"],
            "pair_label": PAIR_LABELS[key],
        })
    return pairs


def run_model(
    invoker: Invoker,
    model: ModelConfig,
    directory: Path,
    packet_receipt: dict[str, object] | None = None,
) -> dict[str, object]:
    directory.mkdir(parents=True, exist_ok=False)
    receipt = {} if packet_receipt is None else packet_receipt
    for task in TASKS:
        assert_pair_isolation(model, task)
    calls = []
    for call in schedule(model):
        try:
            attempts = invoke_with_retry(invoker, model, call)
        except ContactAbort as abort:
            for prior in abort.prior_attempts:
                _write_attempt(
                    directory, prior, None, call.task.oracle_answer,
                    call.task.response_format if call.condition == "constrained" else None,
                    receipt,
                )
            if abort.attempt is not None:
                _write_abort_attempt(
                    directory, abort.attempt, call.task.oracle_answer,
                    call.task.response_format if call.condition == "constrained" else None,
                    receipt,
                )
            summary = {
                "model": asdict(model), "packet_receipt": receipt, "calls": calls,
                "pairs": _pair_records(model, calls), "trial_status": "aborted",
                "abort_reason": abort.reason,
            }
            (directory / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
            return summary
        final = attempts[-1]
        expected = request_envelope(model, call)
        if not exact_equal(final.request_envelope, expected):
            for prior in attempts[:-1]:
                _write_attempt(
                    directory, prior, None, call.task.oracle_answer,
                    call.task.response_format if call.condition == "constrained" else None,
                    receipt,
                )
            _write_abort_attempt(
                directory, final, call.task.oracle_answer,
                call.task.response_format if call.condition == "constrained" else None,
                receipt,
            )
            summary = {
                "model": asdict(model), "packet_receipt": receipt, "calls": calls,
                "pairs": _pair_records(model, calls), "trial_status": "aborted",
                "abort_reason": "request_contract_rejected",
            }
            (directory / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
            return summary
        report = score_output(final.output, call.task.oracle_answer)
        for attempt in attempts:
            _write_attempt(
                directory, attempt, report if attempt is final else None,
                call.task.oracle_answer,
                call.task.response_format if call.condition == "constrained" else None,
                receipt,
            )
        calls.append({
            "logical_index": call.logical_index,
            "call_id": call.call_id,
            "task_id": call.task.task_id,
            "condition": call.condition,
            "seed": call.task.seed,
            **report,
            "call_state": call_state(str(report["call_label"])),
        })
    summary = {
        "model": asdict(model), "packet_receipt": receipt,
        "calls": calls, "pairs": _pair_records(model, calls),
        "trial_status": "complete", "abort_reason": None,
    }
    (directory / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


class LiveInvoker:
    def __init__(self, model: ModelConfig, server_url: str = "http://127.0.0.1:1234/v1/chat/completions") -> None:
        self.model = model
        self.server_url = server_url

    def __call__(self, model: ModelConfig, call: LogicalCall) -> Attempt:
        if model != self.model:
            raise ValueError("exact_loaded_model_required")
        envelope = request_envelope(model, call)
        started = datetime.now(timezone.utc)
        clock = time.monotonic()
        request = Request(
            self.server_url, data=json.dumps(envelope).encode(),
            headers={"Content-Type": "application/json", "Authorization": "Bearer lm-studio"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=180) as response:
                raw_response = response.read()
        except HTTPError as error:
            body = error.read().decode(errors="replace")
            elapsed = time.monotonic() - clock
            ended = datetime.now(timezone.utc)
            attempt = Attempt(
                call.logical_index, 1, call.call_id, call.task.task_id, call.condition,
                call.task.seed, model.model_key, model.live_identifier, call.task.prompt,
                "", envelope, {"http_status": error.code, "body": body},
                started.isoformat(), ended.isoformat(), elapsed,
            )
            reason = "request_contract_rejected" if 400 <= error.code < 500 else "infrastructure_invalid"
            raise ContactAbort(reason, attempt) from error
        except (URLError, TimeoutError, OSError) as error:
            elapsed = time.monotonic() - clock
            ended = datetime.now(timezone.utc)
            attempt = Attempt(
                call.logical_index, 1, call.call_id, call.task.task_id, call.condition,
                call.task.seed, model.model_key, model.live_identifier, call.task.prompt,
                "", envelope, {"transport_error": type(error).__name__, "message": str(error)},
                started.isoformat(), ended.isoformat(), elapsed,
            )
            raise ContactAbort("infrastructure_invalid", attempt) from error
        elapsed = time.monotonic() - clock
        ended = datetime.now(timezone.utc)
        try:
            response_envelope = json.loads(raw_response)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            attempt = Attempt(
                call.logical_index, 1, call.call_id, call.task.task_id, call.condition,
                call.task.seed, model.model_key, model.live_identifier, call.task.prompt,
                "", envelope, {"raw_body": raw_response.decode(errors="replace")},
                started.isoformat(), ended.isoformat(), elapsed,
            )
            raise ContactAbort("provider_envelope_invalid", attempt) from error
        try:
            content = response_envelope["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            attempt = Attempt(
                call.logical_index, 1, call.call_id, call.task.task_id, call.condition,
                call.task.seed, model.model_key, model.live_identifier, call.task.prompt,
                "", envelope, response_envelope, started.isoformat(), ended.isoformat(), elapsed,
            )
            raise ContactAbort("provider_envelope_invalid", attempt) from error
        if content is not None and type(content) is not str:
            attempt = Attempt(
                call.logical_index, 1, call.call_id, call.task.task_id, call.condition,
                call.task.seed, model.model_key, model.live_identifier, call.task.prompt,
                "", envelope, response_envelope, started.isoformat(), ended.isoformat(), elapsed,
            )
            raise ContactAbort("provider_envelope_invalid", attempt)
        output = "" if content is None else content
        return Attempt(
            call.logical_index, 1, call.call_id, call.task.task_id, call.condition,
            call.task.seed, model.model_key, model.live_identifier, call.task.prompt,
            output, envelope, response_envelope, started.isoformat(), ended.isoformat(), elapsed,
        )


def run_live(evidence_directory: Path) -> dict[str, object]:
    evidence_directory.mkdir(parents=True, exist_ok=False)
    artifact_records = {model.model_key: verify_artifact(model) for model in MODELS}
    cli_version = subprocess.run(("lms", "--version"), check=True, capture_output=True, text=True).stdout.strip()
    runtime_inventory = subprocess.run(("lms", "runtime", "ls"), check=True, capture_output=True, text=True).stdout
    server_start = subprocess.run(("lms", "server", "start"), check=False, capture_output=True, text=True)
    if server_start.returncode != 0 and "already" not in (server_start.stdout + server_start.stderr).lower():
        raise ValueError("lm_studio_server_unavailable")
    server_receipt = {
        "command": ["lms", "server", "start"], "exit_code": server_start.returncode,
        "stdout": server_start.stdout, "stderr": server_start.stderr,
    }
    summaries = []
    try:
        for model in MODELS:
            try:
                subprocess.run(("lms", "unload", "--all"), check=False, capture_output=True, text=True)
                command = load_command(model)
                loaded_process = subprocess.run(command, check=True, capture_output=True, text=True)
                inventory = json.loads(subprocess.run(("lms", "ps", "--json"), check=True, capture_output=True, text=True).stdout)
                instance = validate_loaded_instance(model, inventory)
                receipt = {
                    "model": asdict(model), "artifact_verification": artifact_records[model.model_key],
                    "cli_version": cli_version, "runtime_inventory": runtime_inventory,
                    "server": server_receipt,
                    "load": {"command": list(command), "exit_code": loaded_process.returncode,
                             "stdout": loaded_process.stdout, "stderr": loaded_process.stderr,
                             "instance": instance},
                    "sampling_without_seed": SAMPLING, "text_only": True,
                    "projector_attached": False, "adapter_attached": False,
                    "speculative_decoding": False, "tools": False, "history_reuse": False,
                }
                model_summary = run_model(LiveInvoker(model), model, evidence_directory / model.live_identifier, receipt)
                summaries.append(model_summary)
                subprocess.run(("lms", "unload", "--all"), check=False, capture_output=True, text=True)
                if model_summary["trial_status"] == "aborted":
                    break
            except Exception as error:
                if not summaries:
                    raise
                summaries.append({
                    "model": asdict(model), "packet_receipt": {
                        "model": asdict(model),
                        "artifact_verification": artifact_records[model.model_key],
                        "cli_version": cli_version, "runtime_inventory": runtime_inventory,
                        "server": server_receipt,
                        "infrastructure_error": {"type": type(error).__name__, "message": str(error)},
                    },
                    "calls": [], "pairs": [], "trial_status": "aborted",
                    "abort_reason": "infrastructure_invalid",
                })
                break
    finally:
        subprocess.run(("lms", "unload", "--all"), check=False, capture_output=True, text=True)
    pairs = [pair for summary in summaries for pair in summary["pairs"]]
    aborted = next((item for item in summaries if item["trial_status"] == "aborted"), None)
    summary = {
        "protocol": "structured-output-interface-trial-v0",
        "evidence_class": "exploratory_only", "models": summaries,
        "artifact_verification": artifact_records, "pairs": pairs,
        "trial_status": "aborted" if aborted else "complete",
        "abort_reason": None if aborted is None else aborted["abort_reason"],
    }
    (evidence_directory / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the reviewed structured-output interface trial.")
    parser.add_argument("--evidence-directory", type=Path, required=True)
    parser.add_argument("--run-contact", action="store_true")
    arguments = parser.parse_args()
    if not arguments.run_contact:
        parser.error("--run-contact is required")
    print(json.dumps(run_live(arguments.evidence_directory), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
