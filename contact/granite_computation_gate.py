"""Run the reviewed Granite four-call computation gate."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from contact.gemma_contract_staircase import (
    SAMPLING, ModelConfig, exact_equal, load_command, score_output,
    validate_loaded_instance, verify_artifact,
)
from contact.structured_output_interface_trial import (
    Attempt, ContactAbort, _write_abort_attempt, _write_attempt, call_state,
)


MODEL = ModelConfig(
    "Granite 4.0 H Tiny", "ibm/granite-4-h-tiny",
    "ibm/granite-4-h-tiny@q4_k_m", "formation-granite-computation-gate",
    "lmstudio-community/granite-4.0-h-tiny-GGUF/granite-4.0-h-tiny-Q4_K_M.gguf",
    4230975936,
    "064bea0136420b38d0b65697fa5e772e28b112eee1757aacc7f64eba6bf37810",
    6099, "fed2756d2d24e127b951dcf139d0b03ab7db8ef23a456128ebc9c2db4901d476",
)

PROMPTS = (
    """Compute the requested result from this JSON input:
{"jobs":[{"id":"maple","ready":true,"priority":3},{"id":"cedar","ready":false,"priority":9},{"id":"ash","ready":true,"priority":5},{"id":"birch","ready":true,"priority":1}]}

Return the ids of jobs whose ready value is true and whose priority is at least 3. Sort by priority from highest to lowest, breaking ties alphabetically by id.
Return exactly one JSON object with the single key "answer". Its value must be a JSON array of strings. Return no prose or Markdown fence.
Your complete response has a limit of 256 tokens.""",
    """Compute the requested result from this JSON input:
{"start":9,"operations":[{"kind":"add","value":5},{"kind":"triple"},{"kind":"subtract","value":8},{"kind":"halve"}]}

Begin with start. Apply the operations from left to right. Add increases the current value, triple multiplies it by 3, subtract removes value, and halve divides the current value by 2. All intermediate and final values in this input are integers. Return the final integer.
Return exactly one JSON object with the single key "answer". Return no prose or Markdown fence.
Your complete response has a limit of 256 tokens.""",
    """Compute the requested result from this JSON input:
{"records":[{"name":"iris","revision":1,"enabled":true},{"name":"oak","revision":2,"enabled":true},{"name":"iris","revision":3,"enabled":false},{"name":"pine","revision":1,"enabled":true},{"name":"oak","revision":4,"enabled":true},{"name":"pine","revision":2,"enabled":false}]}

For each name, select only its record with the greatest revision. Keep the name only when that selected record has enabled equal to true. Return the kept names sorted alphabetically.
Return exactly one JSON object with the single key "answer". Its value must be a JSON array of strings. Return no prose or Markdown fence.
Your complete response has a limit of 256 tokens.""",
    """Compute the requested result from this JSON input:
{"start":["forge"],"dependencies":{"forge":["kiln","mold"],"kiln":["fuel"],"mold":["clay","fuel"],"fuel":[],"clay":[],"unused":["sand"],"sand":[]}}

Starting from every name in start, repeatedly follow dependencies. Return every reachable dependency, but do not include the starting names. Include each name once and sort the result alphabetically. Do not follow entries that are not reachable from start.
Return exactly one JSON object with the single key "answer". Its value must be a JSON array of strings. Return no prose or Markdown fence.
Your complete response has a limit of 256 tokens.""",
)


def _schema(name: str, answer: dict[str, object]) -> dict[str, object]:
    return {"type": "json_schema", "json_schema": {"name": name, "strict": True, "schema": {
        "type": "object", "properties": {"answer": answer},
        "required": ["answer"], "additionalProperties": False,
    }}}


@dataclass(frozen=True, slots=True)
class Task:
    logical_index: int
    task_id: str
    seed: int
    prompt: str
    oracle_answer: object
    response_format: dict[str, object]


TASKS = (
    Task(1, "filtered_ordering", 5001, PROMPTS[0], ["ash", "maple"],
         _schema("filtered_ordering_answer", {"type": "array", "items": {"type": "string"}})),
    Task(2, "ordered_operations", 5002, PROMPTS[1], 17,
         _schema("ordered_operations_answer", {"type": "integer"})),
    Task(3, "latest_enabled_revisions", 5003, PROMPTS[2], ["oak"],
         _schema("latest_enabled_revisions_answer", {"type": "array", "items": {"type": "string"}})),
    Task(4, "dependency_reachability", 5004, PROMPTS[3], ["clay", "fuel", "kiln", "mold"],
         _schema("dependency_reachability_answer", {"type": "array", "items": {"type": "string"}})),
)


def request_envelope(task: Task) -> dict[str, object]:
    return {
        "model": MODEL.live_identifier,
        "messages": [{"role": "user", "content": task.prompt}],
        **SAMPLING, "seed": task.seed, "response_format": task.response_format,
    }


class LiveInvoker:
    def __init__(self, server_url: str = "http://127.0.0.1:1234/v1/chat/completions") -> None:
        self.server_url = server_url

    def __call__(self, model: ModelConfig, task: Task) -> Attempt:
        if model != MODEL:
            raise ValueError("exact_loaded_model_required")
        envelope = request_envelope(task)
        started = datetime.now(timezone.utc)
        clock = time.monotonic()
        request = Request(self.server_url, data=json.dumps(envelope).encode(), headers={
            "Content-Type": "application/json", "Authorization": "Bearer lm-studio",
        }, method="POST")
        try:
            with urlopen(request, timeout=180) as response:
                raw = response.read()
        except HTTPError as error:
            body = error.read().decode(errors="replace")
            attempt = self._attempt(task, envelope, "", {"http_status": error.code, "body": body}, started, clock)
            reason = "request_contract_rejected" if 400 <= error.code < 500 else "infrastructure_invalid"
            raise ContactAbort(reason, attempt) from error
        except (URLError, TimeoutError, OSError) as error:
            attempt = self._attempt(task, envelope, "", {"transport_error": type(error).__name__, "message": str(error)}, started, clock)
            raise ContactAbort("infrastructure_invalid", attempt) from error
        try:
            response_envelope = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            attempt = self._attempt(task, envelope, "", {"raw_body": raw.decode(errors="replace")}, started, clock)
            raise ContactAbort("provider_envelope_invalid", attempt) from error
        try:
            content = response_envelope["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            attempt = self._attempt(task, envelope, "", response_envelope, started, clock)
            raise ContactAbort("provider_envelope_invalid", attempt) from error
        if content is not None and type(content) is not str:
            attempt = self._attempt(task, envelope, "", response_envelope, started, clock)
            raise ContactAbort("provider_envelope_invalid", attempt)
        return self._attempt(task, envelope, "" if content is None else content, response_envelope, started, clock)

    @staticmethod
    def _attempt(task: Task, envelope: dict[str, object], output: str,
                 response: dict[str, object], started: datetime, clock: float) -> Attempt:
        ended = datetime.now(timezone.utc)
        return Attempt(
            task.logical_index, 1, task.task_id, task.task_id, "constrained", task.seed,
            MODEL.model_key, MODEL.live_identifier, task.prompt, output, envelope, response,
            started.isoformat(), ended.isoformat(), time.monotonic() - clock,
        )


def _invoke_with_retry(invoker, task: Task) -> tuple[Attempt, ...]:
    first = invoker(MODEL, task)
    if first.output != "":
        return (first,)
    first = replace(first, retry_reason="no_model_content")
    try:
        second = replace(invoker(MODEL, task), attempt_index=2,
                         retry_reason="no_model_content", retry_of_attempt=1)
    except ContactAbort as abort:
        abort.prior_attempts = (first,)
        if abort.attempt is not None:
            abort.attempt = replace(abort.attempt, attempt_index=2,
                                    retry_reason="no_model_content", retry_of_attempt=1)
        raise
    return (first, second)


def run_gate(invoker, directory: Path, receipt: dict[str, object] | None = None) -> dict[str, object]:
    directory.mkdir(parents=True, exist_ok=False)
    packet_receipt = {} if receipt is None else receipt
    calls = []
    for task in TASKS:
        try:
            attempts = _invoke_with_retry(invoker, task)
        except ContactAbort as abort:
            for prior in abort.prior_attempts:
                _write_attempt(directory, prior, None, task.oracle_answer, task.response_format, packet_receipt)
            if abort.attempt is not None:
                _write_abort_attempt(directory, abort.attempt, task.oracle_answer, task.response_format, packet_receipt)
            return _finish(directory, calls, "aborted", abort.reason, None, packet_receipt)
        final = attempts[-1]
        if not exact_equal(final.request_envelope, request_envelope(task)):
            for prior in attempts[:-1]:
                _write_attempt(directory, prior, None, task.oracle_answer, task.response_format, packet_receipt)
            _write_abort_attempt(directory, final, task.oracle_answer, task.response_format, packet_receipt)
            return _finish(directory, calls, "aborted", "request_contract_rejected", None, packet_receipt)
        report = score_output(final.output, task.oracle_answer)
        for attempt in attempts:
            _write_attempt(directory, attempt, report if attempt is final else None,
                           task.oracle_answer, task.response_format, packet_receipt)
        calls.append({"logical_index": task.logical_index, "call_id": task.task_id,
                      "task_id": task.task_id, "condition": "constrained", "seed": task.seed,
                      **report, "call_state": call_state(str(report["call_label"]))})
    result = "gate_pass" if all(call["call_state"] == "valid_correct" for call in calls) else "computation_unreliable"
    return _finish(directory, calls, "complete", None, result, packet_receipt)


def _finish(directory: Path, calls: list[dict[str, object]], status: str,
            abort_reason: str | None, result: str | None,
            receipt: dict[str, object]) -> dict[str, object]:
    summary = {"model": asdict(MODEL), "packet_receipt": receipt, "calls": calls,
               "packet_status": status, "abort_reason": abort_reason,
               "candidate_result": result}
    (directory / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def run_live(directory: Path) -> dict[str, object]:
    directory.mkdir(parents=True, exist_ok=False)
    artifact = verify_artifact(MODEL)
    cli = subprocess.run(("lms", "--version"), check=True, capture_output=True, text=True).stdout.strip()
    runtime = subprocess.run(("lms", "runtime", "ls"), check=True, capture_output=True, text=True).stdout
    server = subprocess.run(("lms", "server", "start"), check=False, capture_output=True, text=True)
    if server.returncode and "already" not in (server.stdout + server.stderr).lower():
        raise ValueError("lm_studio_server_unavailable")
    try:
        subprocess.run(("lms", "unload", "--all"), check=False, capture_output=True, text=True)
        command = load_command(MODEL)
        loaded = subprocess.run(command, check=True, capture_output=True, text=True)
        instance = validate_loaded_instance(MODEL, json.loads(subprocess.run(
            ("lms", "ps", "--json"), check=True, capture_output=True, text=True).stdout))
        receipt = {
            "model": asdict(MODEL), "artifact_verification": artifact,
            "cli_version": cli, "runtime_inventory": runtime,
            "server": {"command": ["lms", "server", "start"], "exit_code": server.returncode,
                       "stdout": server.stdout, "stderr": server.stderr},
            "load": {"command": list(command), "exit_code": loaded.returncode,
                     "stdout": loaded.stdout, "stderr": loaded.stderr, "instance": instance},
            "sampling_without_seed": SAMPLING, "text_only": True,
            "projector_attached": False, "adapter_attached": False,
            "speculative_decoding": False, "tools": False, "history_reuse": False,
        }
        summary = run_gate(LiveInvoker(), directory / MODEL.live_identifier, receipt)
    finally:
        subprocess.run(("lms", "unload", "--all"), check=False, capture_output=True, text=True)
    top = {"protocol": "granite-computation-gate-v0", "evidence_class": "exploratory_only",
           "artifact_verification": artifact, **summary}
    (directory / "summary.json").write_text(json.dumps(top, indent=2, sort_keys=True) + "\n")
    return top


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the reviewed Granite computation gate.")
    parser.add_argument("--evidence-directory", type=Path, required=True)
    parser.add_argument("--run-contact", action="store_true")
    args = parser.parse_args()
    if not args.run_contact:
        parser.error("--run-contact is required")
    print(json.dumps(run_live(args.evidence_directory), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
