"""Run the reviewed Qwen 3.5 9B MLX computation gate."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from contact.gemma_contract_staircase import exact_equal, score_output
from contact.structured_output_interface_trial import (
    Attempt, ContactAbort, _write_abort_attempt, _write_attempt, call_state,
)


SAMPLING = {
    "frequency_penalty": 0, "max_tokens": 1024, "presence_penalty": 0,
    "repeat_penalty": 1, "stream": False, "temperature": 0.2,
    "top_k": 40, "top_p": 0.95,
}


@dataclass(frozen=True, slots=True)
class Model:
    name: str = "Qwen 3.5 9B MLX 4bit"
    model_key: str = "qwen/qwen3.5-9b"
    selected_variant: str = "qwen/qwen3.5-9b@4bit"
    live_identifier: str = "formation-qwen-computation-gate"


MODEL = Model()
PACKAGE_RELATIVE = "lmstudio-community/Qwen3.5-9B-MLX-4bit"
PACKAGE_FILES = {
    "chat_template.jinja": (7756, "a4aee8afcf2e0711942cf848899be66016f8d14a889ff9ede07bca099c28f715"),
    "config.json": (3331, "a96942cb6a8a1d3f1d17514d81a1925d04362a6a3233b389d13012211baaa9f8"),
    "model-00001-of-00002.safetensors": (5349771292, "973cc1efdedb4d327993fb9c27865f0bcfd9015897d5f0ca9ffb6cda6a0768e5"),
    "model-00002-of-00002.safetensors": (600449850, "597dae0ed72b60acc07382e8ea0cdb9509c54128e07b0eaa9cf4996373d5ca7d"),
    "model.safetensors.index.json": (123592, "dd023913fb87cfdae27fb11dcf695117c925833796ccac3c64117d6652d8ff1e"),
    "preprocessor_config.json": (390, "27225450ac9c6529872ee1924fcb0962ff5634834f817040f444118116f4e516"),
    "processor_config.json": (991, "45fc17c8dd2474af6b493b52483c26c0584b0082d368c480f9fa611e73070040"),
    "tokenizer.json": (19989325, "06b9509352d2af50381ab2247e083b80d32d5c0aba91c272ca9ff729b6a0e523"),
    "tokenizer_config.json": (9187, "fa71760892f5c601d345e626ebd602055825a50beed7ee160709c95fffa475f0"),
    "video_preprocessor_config.json": (385, "7768af27c1fafa9cc9011c1dc20067e03f8915e03b63504550e11d5066986d13"),
    "vocab.json": (6722759, "ce99b4cb2983d118806ce0a8b777a35b093e2000a503ebde25853284c9dfa003"),
}
HUB_FILES = {
    "model.yaml": (1695, "41e997d0ab4ca5572918e33c1c5284c5a9c4032ce3affe40b33ad76d7706746b"),
    "manifest.json": (770, "c19d54c5855a8c596dd6197f715ffff20fc06dead920fce8faba9353edc6c8d1"),
}

PROMPTS = (
    """Compute the requested result from this JSON input:
{"items":[{"code":"elm","active":true,"score":7,"cost":6},{"code":"fir","active":false,"score":10,"cost":2},{"code":"yew","active":true,"score":7,"cost":4},{"code":"oak","active":true,"score":5,"cost":8},{"code":"ash","active":true,"score":9,"cost":3}]}

Keep items whose active value is true and whose cost is at most 6. Sort by score from highest to lowest, breaking ties alphabetically by code. Return the codes.
Return exactly one JSON object with the single key "answer". Its value must be a JSON array of strings. Return no prose or Markdown fence.
Your complete response has a limit of 1024 tokens.""",
    """Compute the requested result from this JSON input:
{"start":20,"operations":[{"kind":"add","value":6},{"kind":"double"},{"kind":"subtract","value":10},{"kind":"halve"}]}

Begin with start and apply every operation from left to right. Add increases the current value, double multiplies it by 2, subtract removes value, and halve divides the current value by 2. All intermediate and final values are integers. Return the final integer.
Return exactly one JSON object with the single key "answer". Return no prose or Markdown fence.
Your complete response has a limit of 1024 tokens.""",
    """Compute the requested result from this JSON input:
{"records":[{"name":"alpha","revision":1,"enabled":false},{"name":"beta","revision":2,"enabled":true},{"name":"gamma","revision":1,"enabled":false},{"name":"alpha","revision":3,"enabled":true},{"name":"beta","revision":4,"enabled":false},{"name":"gamma","revision":2,"enabled":true}]}

For each name, select only its record with the greatest revision. Keep the name only when that selected record has enabled equal to true. Return the kept names sorted alphabetically.
Return exactly one JSON object with the single key "answer". Its value must be a JSON array of strings. Return no prose or Markdown fence.
Your complete response has a limit of 1024 tokens.""",
    """Compute the requested result from this JSON input:
{"start":["hub"],"dependencies":{"hub":["north","south"],"north":["leaf1","shared"],"south":["leaf2","shared"],"leaf1":[],"leaf2":[],"shared":[],"isolated":["ghost"],"ghost":[]}}

Starting from every name in start, repeatedly follow dependencies. Return every reachable dependency, but do not include the starting names. Include each name once and sort the result alphabetically. Do not follow entries that are not reachable from start.
Return exactly one JSON object with the single key "answer". Its value must be a JSON array of strings. Return no prose or Markdown fence.
Your complete response has a limit of 1024 tokens.""",
)


def _schema(name: str, answer: dict[str, object]) -> dict[str, object]:
    return {"type": "json_schema", "json_schema": {"name": name, "strict": True, "schema": {
        "type": "object", "properties": {"answer": answer}, "required": ["answer"],
        "additionalProperties": False,
    }}}


@dataclass(frozen=True, slots=True)
class Task:
    logical_index: int
    task_id: str
    seed: int
    prompt: str
    oracle_answer: object
    response_format: dict[str, object]


ARRAY = {"type": "array", "items": {"type": "string"}}
TASKS = (
    Task(1, "filtered_ordering", 6001, PROMPTS[0], ["ash", "elm", "yew"], _schema("filtered_ordering_answer", ARRAY)),
    Task(2, "ordered_operations", 6002, PROMPTS[1], 21, _schema("ordered_operations_answer", {"type": "integer"})),
    Task(3, "latest_enabled_revisions", 6003, PROMPTS[2], ["alpha", "gamma"], _schema("latest_enabled_revisions_answer", ARRAY)),
    Task(4, "dependency_reachability", 6004, PROMPTS[3], ["leaf1", "leaf2", "north", "shared", "south"], _schema("dependency_reachability_answer", ARRAY)),
)


def _digest(path: Path) -> str:
    builder = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            builder.update(block)
    return builder.hexdigest()


def verify_package() -> dict[str, object]:
    package = Path.home() / ".lmstudio" / "models" / PACKAGE_RELATIVE
    actual = {path.name for path in package.iterdir() if path.is_file()}
    if actual != set(PACKAGE_FILES):
        raise ValueError("model_package_file_set_mismatch")
    records = []
    for name, (size, digest) in sorted(PACKAGE_FILES.items()):
        path = package / name
        if path.stat().st_size != size or _digest(path) != digest:
            raise ValueError("model_package_binding_mismatch")
        records.append({"relative_path": name, "byte_count": size, "sha256": digest})
    hub = Path.home() / ".lmstudio" / "hub" / "models" / "qwen" / "qwen3.5-9b"
    controls = []
    for name, (size, digest) in sorted(HUB_FILES.items()):
        path = hub / name
        if not path.is_file() or path.stat().st_size != size or _digest(path) != digest:
            raise ValueError("hub_control_binding_mismatch")
        controls.append({"path": str(path), "byte_count": size, "sha256": digest})
    model_yaml = (hub / "model.yaml").read_text()
    if not all(value in model_yaml for value in ("key: enableThinking", "defaultValue: true", "type: setJinjaVariable", "variable: enable_thinking")):
        raise ValueError("hub_thinking_control_mismatch")
    return {"package_path": str(package), "package_files": records, "hub_control_files": controls}


def load_command() -> tuple[str, ...]:
    return ("lms", "load", MODEL.model_key, "--gpu", "max", "--parallel", "1",
            "--no-speculative-draft-mtp", "--identifier", MODEL.live_identifier, "-y")


def validate_loaded(value: object) -> dict[str, object]:
    if (type(value) is not list or len(value) != 1 or type(value[0]) is not dict):
        raise ValueError("exact_single_model_load_required")
    item = value[0]
    required = {"identifier": MODEL.live_identifier, "selectedVariant": MODEL.selected_variant,
                "format": "safetensors", "contextLength": 262144, "parallel": 1, "vision": True}
    if any(item.get(key) != expected for key, expected in required.items()):
        raise ValueError("exact_qwen_load_required")
    return item


def request_envelope(task: Task) -> dict[str, object]:
    return {"model": MODEL.live_identifier, "messages": [{"role": "user", "content": task.prompt}],
            **SAMPLING, "seed": task.seed, "response_format": task.response_format}


class LiveInvoker:
    def __init__(self, url: str = "http://127.0.0.1:1234/v1/chat/completions") -> None:
        self.url = url

    def __call__(self, model: Model, task: Task) -> Attempt:
        if model != MODEL:
            raise ValueError("exact_loaded_model_required")
        envelope = request_envelope(task)
        started, clock = datetime.now(timezone.utc), time.monotonic()
        request = Request(self.url, data=json.dumps(envelope).encode(), headers={"Content-Type": "application/json", "Authorization": "Bearer lm-studio"}, method="POST")
        try:
            with urlopen(request, timeout=300) as response:
                raw = response.read()
        except HTTPError as error:
            attempt = self._attempt(task, envelope, "", {"http_status": error.code, "body": error.read().decode(errors="replace")}, started, clock)
            raise ContactAbort("request_contract_rejected" if 400 <= error.code < 500 else "infrastructure_invalid", attempt) from error
        except (URLError, TimeoutError, OSError) as error:
            attempt = self._attempt(task, envelope, "", {"transport_error": type(error).__name__, "message": str(error)}, started, clock)
            raise ContactAbort("infrastructure_invalid", attempt) from error
        try:
            response = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise ContactAbort("provider_envelope_invalid", self._attempt(task, envelope, "", {"raw_body": raw.decode(errors="replace")}, started, clock)) from error
        try:
            content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise ContactAbort("provider_envelope_invalid", self._attempt(task, envelope, "", response, started, clock)) from error
        if content is not None and type(content) is not str:
            raise ContactAbort("provider_envelope_invalid", self._attempt(task, envelope, "", response, started, clock))
        return self._attempt(task, envelope, "" if content is None else content, response, started, clock)

    @staticmethod
    def _attempt(task, envelope, output, response, started, clock):
        ended = datetime.now(timezone.utc)
        return Attempt(task.logical_index, 1, task.task_id, task.task_id, "constrained", task.seed,
                       MODEL.model_key, MODEL.live_identifier, task.prompt, output, envelope, response,
                       started.isoformat(), ended.isoformat(), time.monotonic() - clock)


def _invoke(invoker, task):
    first = invoker(MODEL, task)
    if first.output != "": return (first,)
    first = replace(first, retry_reason="no_model_content")
    try:
        second = replace(invoker(MODEL, task), attempt_index=2, retry_reason="no_model_content", retry_of_attempt=1)
    except ContactAbort as abort:
        abort.prior_attempts = (first,)
        if abort.attempt: abort.attempt = replace(abort.attempt, attempt_index=2, retry_reason="no_model_content", retry_of_attempt=1)
        raise
    return (first, second)


def _finish(directory, calls, status, reason, result, receipt):
    summary = {"model": asdict(MODEL), "packet_receipt": receipt, "calls": calls,
               "packet_status": status, "abort_reason": reason, "candidate_result": result}
    (directory / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def run_gate(invoker, directory: Path, receipt=None):
    directory.mkdir(parents=True, exist_ok=False)
    receipt = {} if receipt is None else receipt
    calls = []
    for task in TASKS:
        try: attempts = _invoke(invoker, task)
        except ContactAbort as abort:
            for prior in abort.prior_attempts: _write_attempt(directory, prior, None, task.oracle_answer, task.response_format, receipt)
            if abort.attempt: _write_abort_attempt(directory, abort.attempt, task.oracle_answer, task.response_format, receipt)
            return _finish(directory, calls, "aborted", abort.reason, None, receipt)
        final = attempts[-1]
        if not exact_equal(final.request_envelope, request_envelope(task)):
            for prior in attempts[:-1]: _write_attempt(directory, prior, None, task.oracle_answer, task.response_format, receipt)
            _write_abort_attempt(directory, final, task.oracle_answer, task.response_format, receipt)
            return _finish(directory, calls, "aborted", "request_contract_rejected", None, receipt)
        report = score_output(final.output, task.oracle_answer)
        for attempt in attempts: _write_attempt(directory, attempt, report if attempt is final else None, task.oracle_answer, task.response_format, receipt)
        calls.append({"logical_index": task.logical_index, "call_id": task.task_id, "task_id": task.task_id,
                      "condition": "constrained", "seed": task.seed, **report,
                      "call_state": call_state(str(report["call_label"]))})
    result = "gate_pass" if all(call["call_state"] == "valid_correct" for call in calls) else "computation_unreliable"
    return _finish(directory, calls, "complete", None, result, receipt)


def run_live(directory: Path):
    directory.mkdir(parents=True, exist_ok=False)
    package = verify_package()
    cli = subprocess.run(("lms", "--version"), check=True, capture_output=True, text=True).stdout.strip()
    runtime = subprocess.run(("lms", "runtime", "ls"), check=True, capture_output=True, text=True).stdout
    server = subprocess.run(("lms", "server", "start"), check=False, capture_output=True, text=True)
    if server.returncode and "already" not in (server.stdout + server.stderr).lower(): raise ValueError("lm_studio_server_unavailable")
    try:
        subprocess.run(("lms", "unload", "--all"), check=False, capture_output=True, text=True)
        command = load_command(); loaded = subprocess.run(command, check=True, capture_output=True, text=True)
        instance = validate_loaded(json.loads(subprocess.run(("lms", "ps", "--json"), check=True, capture_output=True, text=True).stdout))
        receipt = {"model": asdict(MODEL), "package_verification": package, "cli_version": cli,
                   "runtime_inventory": runtime, "server": {"command": ["lms", "server", "start"], "exit_code": server.returncode, "stdout": server.stdout, "stderr": server.stderr},
                   "load": {"command": list(command), "exit_code": loaded.returncode, "stdout": loaded.stdout, "stderr": loaded.stderr, "instance": instance},
                   "sampling_without_seed": SAMPLING, "text_string_only": True, "image_input": False,
                   "video_input": False, "audio_input": False, "content_parts": False, "projector_argument": False,
                   "adapter_attached": False, "tools": False, "history_reuse": False,
                   "authored_system_message": False, "default_thinking": True}
        summary = run_gate(LiveInvoker(), directory / MODEL.live_identifier, receipt)
    finally: subprocess.run(("lms", "unload", "--all"), check=False, capture_output=True, text=True)
    top = {"protocol": "qwen-computation-gate-v0", "evidence_class": "exploratory_only", "package_verification": package, **summary}
    (directory / "summary.json").write_text(json.dumps(top, indent=2, sort_keys=True) + "\n")
    return top


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--evidence-directory", type=Path, required=True); parser.add_argument("--run-contact", action="store_true")
    args = parser.parse_args()
    if not args.run_contact: parser.error("--run-contact is required")
    print(json.dumps(run_live(args.evidence_directory), indent=2, sort_keys=True))


if __name__ == "__main__": main()
