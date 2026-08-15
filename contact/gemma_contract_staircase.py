"""Run the reviewed Gemma 270M-to-1B structured-action staircase."""

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
from urllib.request import Request, urlopen

from contact.model_admission import _read_gguf_template


SAMPLING = {
    "frequency_penalty": 0,
    "max_tokens": 256,
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
    live_identifier: str
    relative_file: str
    byte_count: int
    sha256: str
    template_characters: int
    template_sha256: str


MODELS = (
    ModelConfig(
        "Gemma 3 270M Instruct QAT",
        "google/gemma-3-270m",
        "google/gemma-3-270m@q4_0",
        "formation-gemma-screen-270m",
        "lmstudio-community/gemma-3-270m-it-qat-GGUF/gemma-3-270m-it-qat-Q4_0.gguf",
        241410208,
        "5f4b2e17722e510122c464573b880587f4983347a40e5472b858d5a3c1ab8095",
        1532,
        "7de1c58e208eda46e9c7f86397df37ec49883aeece39fb961e0a6b24088dd3c4",
    ),
    ModelConfig(
        "Gemma 3 1B Instruct QAT",
        "google/gemma-3-1b",
        "google/gemma-3-1b@q4_0",
        "formation-gemma-screen-1b",
        "lmstudio-community/gemma-3-1B-it-QAT-GGUF/gemma-3-1B-it-QAT-Q4_0.gguf",
        720425472,
        "b25d35b00fe699ef52bf399fa579f2c56664897c013aeba2686965fdb6265f0f",
        1532,
        "7de1c58e208eda46e9c7f86397df37ec49883aeece39fb961e0a6b24088dd3c4",
    ),
)

TASK_1_PROMPT = """Compute the requested result from this JSON input:
{"records":[{"label":"cove","kept":false},{"label":"brim","kept":true},{"label":"dawn","kept":true}]}

Return the labels whose kept value is true, sorted alphabetically.
Return exactly one JSON object with the single key "answer". Its value must be a JSON array of strings. Return no prose or Markdown fence.
Your complete response has a limit of 256 tokens."""

TASK_2_PROMPT = """Compute the requested result from this JSON input:
{"entries":[{"zone":"west","count":4},{"zone":"east","count":3},{"zone":"west","count":-1},{"zone":"east","count":5}]}

Sum count for each zone. Return one [zone,total] pair per zone, sorted alphabetically by zone.
Return exactly one JSON object with the single key "answer". Its value must be a JSON array of two-item arrays. Return no prose or Markdown fence.
Your complete response has a limit of 256 tokens."""

TASK_3_PROMPT = """Compute the requested result from this JSON input:
{"start":12,"changes":[4,-7,3,-2]}

Starting at start, apply each change from left to right. Return the final integer.
Return exactly one JSON object with the single key "answer". Return no prose or Markdown fence.
Your complete response has a limit of 256 tokens."""

TASK_4_PROMPT = """Compute the requested result from this JSON input:
{"items":[{"id":"p","kind":"task","ready":true,"score":1},{"id":"q","kind":"note","ready":true,"score":4},{"id":"r","kind":"task","ready":false,"score":5},{"id":"s","kind":"task","ready":true,"score":3}]}

Return ids of items whose kind is exactly "task", whose ready value is true, and whose score is at least 2. Sort ids alphabetically.
Return exactly one JSON object with the single key "answer". Its value must be a JSON array of strings. Return no prose or Markdown fence.
Your complete response has a limit of 256 tokens."""


@dataclass(frozen=True, slots=True)
class Task:
    logical_index: int
    call_id: str
    seed: int
    prompt: str
    oracle_answer: object


TASKS = (
    Task(1, "selection", 3001, TASK_1_PROMPT, ["brim", "dawn"]),
    Task(2, "grouped-totals", 3002, TASK_2_PROMPT, [["east", 8], ["west", 3]]),
    Task(3, "ordered-updates", 3003, TASK_3_PROMPT, 10),
    Task(4, "conjunctive-filter", 3004, TASK_4_PROMPT, ["s"]),
)


class DuplicateKey(ValueError):
    pass


class NonfiniteConstant(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


def _nonfinite(value: str) -> object:
    raise NonfiniteConstant(value)


def exact_equal(left: object, right: object) -> bool:
    if type(left) is not type(right):
        return False
    if type(left) is list:
        return len(left) == len(right) and all(
            exact_equal(a, b) for a, b in zip(left, right, strict=True)
        )
    if type(left) is dict:
        return left.keys() == right.keys() and all(
            exact_equal(left[key], right[key]) for key in left
        )
    return left == right


def score_output(raw_output: str, oracle_answer: object) -> dict[str, object]:
    if "```" in raw_output:
        return {"gate_refusal": "markdown_fence", "decoded_answer": None, "oracle_answer": oracle_answer, "call_label": "gate_fail"}
    output = raw_output.strip()
    if not output:
        return {"gate_refusal": "empty_output", "decoded_answer": None, "oracle_answer": oracle_answer, "call_label": "gate_fail"}
    try:
        decoded = json.loads(
            output,
            object_pairs_hook=_unique_object,
            parse_constant=_nonfinite,
        )
    except DuplicateKey:
        return {"gate_refusal": "duplicate_key", "decoded_answer": None, "oracle_answer": oracle_answer, "call_label": "gate_fail"}
    except NonfiniteConstant:
        return {"gate_refusal": "nonfinite_constant", "decoded_answer": None, "oracle_answer": oracle_answer, "call_label": "gate_fail"}
    except json.JSONDecodeError:
        return {"gate_refusal": "invalid_json", "decoded_answer": None, "oracle_answer": oracle_answer, "call_label": "gate_fail"}
    if type(decoded) is not dict or set(decoded) != {"answer"}:
        return {"gate_refusal": "exact_object_required", "decoded_answer": None, "oracle_answer": oracle_answer, "call_label": "gate_fail"}
    answer = decoded["answer"]
    return {
        "gate_refusal": None,
        "decoded_answer": answer,
        "oracle_answer": oracle_answer,
        "call_label": "full_pass" if exact_equal(answer, oracle_answer) else "wrong_answer",
    }


@dataclass(frozen=True, slots=True)
class Attempt:
    logical_index: int
    attempt_index: int
    call_id: str
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


Invoker = Callable[[ModelConfig, Task], Attempt]


def invoke_with_retry(invoker: Invoker, model: ModelConfig, task: Task) -> tuple[Attempt, ...]:
    first = invoker(model, task)
    if first.output != "":
        return (first,)
    first = replace(first, retry_reason="no_model_content")
    second = replace(
        invoker(model, task),
        attempt_index=2,
        retry_reason="no_model_content",
        retry_of_attempt=1,
    )
    return (first, second)


def _write_attempt(
    directory: Path,
    attempt: Attempt,
    report: dict[str, object] | None,
    oracle_answer: object,
    packet_receipt: dict[str, object],
) -> None:
    stem = f"{attempt.logical_index:02d}-{attempt.call_id}-a{attempt.attempt_index}"
    (directory / f"{stem}.prompt.txt").write_text(attempt.prompt)
    (directory / f"{stem}.output.txt").write_text(attempt.output)
    record = asdict(attempt)
    record["prompt_sha256"] = hashlib.sha256(attempt.prompt.encode()).hexdigest()
    record["output_sha256"] = hashlib.sha256(attempt.output.encode()).hexdigest()
    record["packet_receipt"] = packet_receipt
    record["gate_refusal"] = None if report is None else report["gate_refusal"]
    record["decoded_answer"] = None if report is None else report["decoded_answer"]
    record["oracle_answer"] = oracle_answer
    record["call_label"] = "retry_pending" if report is None else report["call_label"]
    record.pop("prompt")
    record.pop("output")
    (directory / f"{stem}.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")


def run_model(
    invoker: Invoker,
    model: ModelConfig,
    directory: Path,
    packet_receipt: dict[str, object] | None = None,
) -> dict[str, object]:
    directory.mkdir(parents=True, exist_ok=False)
    receipt = {} if packet_receipt is None else packet_receipt
    calls = []
    for task in TASKS:
        attempts = invoke_with_retry(invoker, model, task)
        final = attempts[-1]
        report = score_output(final.output, task.oracle_answer)
        for attempt in attempts:
            _write_attempt(
                directory,
                attempt,
                report if attempt is final else None,
                task.oracle_answer,
                receipt,
            )
        calls.append(
            {
                "logical_index": task.logical_index,
                "call_id": task.call_id,
                "seed": task.seed,
                **report,
            }
        )
        if report["call_label"] != "full_pass":
            summary = {
                "model": asdict(model),
                "packet_receipt": receipt,
                "calls": calls,
                "stopping_call": task.logical_index,
                "terminal_result": "contract_unreliable",
            }
            (directory / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
            return summary
    summary = {
        "model": asdict(model),
        "packet_receipt": receipt,
        "calls": calls,
        "stopping_call": 4,
        "terminal_result": "screen_pass",
    }
    (directory / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


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
    return {
        "path": str(path),
        "byte_count": model.byte_count,
        "sha256": digest,
        "template_characters": len(template),
        "template_sha256": template_digest,
    }


def load_command(model: ModelConfig) -> tuple[str, ...]:
    return (
        "lms",
        "load",
        model.model_key,
        "--gpu",
        "max",
        "--context-length",
        "8192",
        "--parallel",
        "1",
        "--no-speculative-draft-mtp",
        "--identifier",
        model.live_identifier,
        "-y",
    )


def validate_loaded_instance(model: ModelConfig, loaded: object) -> dict[str, object]:
    if (
        type(loaded) is not list
        or len(loaded) != 1
        or type(loaded[0]) is not dict
        or loaded[0].get("identifier") != model.live_identifier
        or loaded[0].get("selectedVariant") != model.selected_variant
        or loaded[0].get("contextLength") != 8192
        or loaded[0].get("parallel") != 1
        or loaded[0].get("vision") is not False
    ):
        raise ValueError("exact_text_only_model_load_required")
    return loaded[0]


class LiveInvoker:
    def __init__(self, model: ModelConfig, server_url: str = "http://127.0.0.1:1234/v1/chat/completions") -> None:
        self.model = model
        self.server_url = server_url

    def __call__(self, model: ModelConfig, task: Task) -> Attempt:
        if model != self.model:
            raise ValueError("exact_loaded_model_required")
        envelope = {
            "model": model.live_identifier,
            "messages": [{"role": "user", "content": task.prompt}],
            **SAMPLING,
            "seed": task.seed,
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
        try:
            content = response_envelope["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise ValueError("provider_envelope_invalid") from error
        if content is not None and type(content) is not str:
            raise ValueError("provider_envelope_invalid")
        output = "" if content is None else content
        return Attempt(
            task.logical_index,
            1,
            task.call_id,
            task.seed,
            model.model_key,
            model.live_identifier,
            task.prompt,
            output,
            envelope,
            response_envelope,
            started.isoformat(),
            ended.isoformat(),
            elapsed,
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
        "command": ["lms", "server", "start"],
        "exit_code": server_start.returncode,
        "stdout": server_start.stdout,
        "stderr": server_start.stderr,
    }
    summaries = []
    try:
        for model in MODELS:
            subprocess.run(("lms", "unload", "--all"), check=False, capture_output=True, text=True)
            command = load_command(model)
            load_process = subprocess.run(command, check=True, capture_output=True, text=True)
            loaded = json.loads(subprocess.run(("lms", "ps", "--json"), check=True, capture_output=True, text=True).stdout)
            instance = validate_loaded_instance(model, loaded)
            packet_receipt = {
                "model": asdict(model),
                "artifact_verification": artifact_records[model.model_key],
                "cli_version": cli_version,
                "runtime_inventory": runtime_inventory,
                "server": server_receipt,
                "load": {
                    "command": list(command),
                    "exit_code": load_process.returncode,
                    "stdout": load_process.stdout,
                    "stderr": load_process.stderr,
                    "instance": instance,
                },
                "sampling_without_seed": SAMPLING,
                "text_only": True,
                "projector_attached": False,
                "adapter_attached": False,
                "speculative_decoding": False,
                "tools": False,
                "history_reuse": False,
            }
            summaries.append(
                run_model(
                    LiveInvoker(model),
                    model,
                    evidence_directory / model.live_identifier,
                    packet_receipt,
                )
            )
            subprocess.run(("lms", "unload", "--all"), check=False, capture_output=True, text=True)
    finally:
        subprocess.run(("lms", "unload", "--all"), check=False, capture_output=True, text=True)
    summary = {
        "protocol": "gemma-contract-staircase-v0",
        "evidence_class": "exploratory_only",
        "models": summaries,
        "artifact_verification": artifact_records,
    }
    (evidence_directory / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the reviewed Gemma structured-action staircase.")
    parser.add_argument("--evidence-directory", type=Path, required=True)
    parser.add_argument("--run-contact", action="store_true")
    arguments = parser.parse_args()
    if not arguments.run_contact:
        parser.error("--run-contact is required")
    print(json.dumps(run_live(arguments.evidence_directory), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
