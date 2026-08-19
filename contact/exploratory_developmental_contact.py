"""Run the bounded Docker Model Runner developmental contact."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from micro_environment.revision_gated_release import (
    REBUILD_THEN_RELEASE,
    RELEASE,
    RevisionResult,
    RevisionState,
    apply_revision_gated_release,
)


PROTOCOL_VERSION = "exploratory-developmental-contact-v0"
MODEL = "ai/qwen3:14B-Q6_K"
INSPECT_TAG = "docker.io/ai/qwen3:14B-Q6_K"
MODEL_DIGEST = "sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219"
ENDPOINT = "http://localhost:12434/engines/llama.cpp/v1/chat/completions"
PLANNED_LOGICAL_CALLS = 27
PHYSICAL_CALL_CEILING = 30

ACTOR_SETTINGS: dict[str, object] = {
    "max_tokens": 128,
    "temperature": 0.6,
    "top_p": 0.95,
    "stream": False,
    "response_format": {"type": "json_object"},
}
INTERPRETER_SETTINGS: dict[str, object] = {
    "max_tokens": 384,
    "temperature": 0.6,
    "top_p": 0.95,
    "stream": False,
}

STATIC_LESSON = (
    "Compare the artifact revision with the authority revision. If they match, "
    "choose `release`. If they differ, choose `rebuild_then_release` so the "
    "artifact is rebuilt to the authority revision before release."
)

INTERFACE_STATE = RevisionState(3, 4)
ACQUISITION_STATE = RevisionState(7, 8)


@dataclass(frozen=True, slots=True)
class Probe:
    probe_id: str
    state: RevisionState


PROBES = (
    Probe("later-adjacent", RevisionState(41, 42)),
    Probe("later-reversed", RevisionState(8, 7)),
    Probe("later-current", RevisionState(2, 2)),
)
OFFERS = ("no_offer", "raw_experience", "runtime_interpretation", "frozen_lesson")


class DuplicateKey(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


@dataclass(frozen=True, slots=True)
class ActionParse:
    action: str | None
    refusal: str | None


def parse_action(content: object) -> ActionParse:
    if type(content) is not str:
        return ActionParse(None, "content_not_string")
    if content == "":
        return ActionParse(None, "empty_content")
    try:
        decoded = json.loads(
            content,
            object_pairs_hook=_unique_object,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
    except (json.JSONDecodeError, DuplicateKey, ValueError):
        return ActionParse(None, "invalid_json")
    if type(decoded) is not dict or set(decoded) != {"action"}:
        return ActionParse(None, "invalid_action_object")
    action = decoded["action"]
    if type(action) is not str:
        return ActionParse(None, "action_not_string")
    if action not in (RELEASE, REBUILD_THEN_RELEASE):
        return ActionParse(None, "unknown_action")
    return ActionParse(action, None)


ACTOR_SYSTEM = """You are the action-selection component of a cold practitioner.
Choose the least work that gets release accepted in the supplied situation.
The only permitted actions are `release` and `rebuild_then_release`.
Return exactly one JSON object with the single string field `action`.
Return no prose and no Markdown fence."""


def actor_user_prompt(state: RevisionState, offer: str | None = None) -> str:
    parts = [
        "Current situation:",
        f"artifact_revision: {state.artifact_revision}",
        f"authority_revision: {state.authority_revision}",
    ]
    if offer is not None:
        parts.extend(("", "Developmental material available for this decision:", offer))
    parts.extend(("", "/no_think"))
    return "\n".join(parts)


def actor_envelope(state: RevisionState, offer: str | None = None) -> dict[str, object]:
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": ACTOR_SYSTEM},
            {"role": "user", "content": actor_user_prompt(state, offer)},
        ],
        **ACTOR_SETTINGS,
    }


INTERPRETER_SYSTEM = """You are the interpreter inside a formation runtime.
Use only the retained encounter and external result supplied below.
Write a short conditional interpretation for later action. State what the
experience may suggest, its uncertainty, and what later evidence would count
against it. Do not claim that the interpretation is true or validated."""


def interpretation_envelope(experience: dict[str, object]) -> dict[str, object]:
    prompt = (
        "Retained acquisition experience:\n"
        + json.dumps(experience, indent=2, sort_keys=True, ensure_ascii=False)
        + "\n\nReturn only the interpretation text.\n\n/no_think"
    )
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": INTERPRETER_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        **INTERPRETER_SETTINGS,
    }


@dataclass(frozen=True, slots=True)
class LogicalCall:
    logical_index: int
    call_id: str
    responsibility: str
    envelope: dict[str, object]
    situation: RevisionState | None = None
    offer_key: str | None = None
    probe_id: str | None = None
    repetition: int | None = None

    @property
    def request_body(self) -> bytes:
        return canonical_json_bytes(self.envelope)


def later_schedule(
    offers: dict[str, str | None], start_index: int = 4
) -> tuple[LogicalCall, ...]:
    calls: list[LogicalCall] = []
    index = start_index
    for repetition in (1, 2):
        for probe_index, probe in enumerate(PROBES):
            shift = (probe_index + (repetition - 1) * 3) % len(OFFERS)
            order = OFFERS[shift:] + OFFERS[:shift]
            for offer_key in order:
                calls.append(
                    LogicalCall(
                        logical_index=index,
                        call_id=f"{probe.probe_id}-{offer_key}-r{repetition}",
                        responsibility="actor",
                        envelope=actor_envelope(probe.state, offers[offer_key]),
                        situation=probe.state,
                        offer_key=offer_key,
                        probe_id=probe.probe_id,
                        repetition=repetition,
                    )
                )
                index += 1
    return tuple(calls)


@dataclass(frozen=True, slots=True)
class ProviderAttempt:
    logical_index: int
    attempt_index: int
    call_id: str
    request_body: bytes
    response_body: bytes
    response_envelope: object
    message: dict[str, object] | None
    content: str | None
    http_status: int | None
    started_at: str
    ended_at: str
    elapsed_seconds: float
    error: str | None = None
    retry_of_attempt: int | None = None


class InvocationFailure(RuntimeError):
    def __init__(self, reason: str, attempt: ProviderAttempt, retryable: bool) -> None:
        super().__init__(reason)
        self.reason = reason
        self.attempt = attempt
        self.retryable = retryable


Invoker = Callable[[LogicalCall, int], ProviderAttempt]


class LiveInvoker:
    def __init__(self, endpoint: str = ENDPOINT, timeout_seconds: int = 300) -> None:
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds

    def __call__(self, call: LogicalCall, attempt_index: int) -> ProviderAttempt:
        request_body = call.request_body
        started = datetime.now(timezone.utc)
        clock = time.monotonic()
        request = Request(
            self.endpoint,
            data=request_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                response_body = response.read()
                http_status = response.status
        except HTTPError as error:
            response_body = error.read()
            attempt = ProviderAttempt(
                call.logical_index,
                attempt_index,
                call.call_id,
                request_body,
                response_body,
                {"http_status": error.code, "body": response_body.decode(errors="replace")},
                None,
                None,
                error.code,
                started.isoformat(),
                datetime.now(timezone.utc).isoformat(),
                time.monotonic() - clock,
                f"http_{error.code}",
            )
            raise InvocationFailure(f"http_{error.code}", attempt, False) from error
        except (URLError, TimeoutError, OSError) as error:
            attempt = ProviderAttempt(
                call.logical_index,
                attempt_index,
                call.call_id,
                request_body,
                b"",
                {"transport_error": repr(error)},
                None,
                None,
                None,
                started.isoformat(),
                datetime.now(timezone.utc).isoformat(),
                time.monotonic() - clock,
                "transport_failure",
            )
            raise InvocationFailure("transport_failure", attempt, True) from error

        ended = datetime.now(timezone.utc)
        elapsed = time.monotonic() - clock
        try:
            envelope = json.loads(response_body)
            if type(envelope) is not dict:
                raise ValueError("response_object_required")
            choices = envelope.get("choices")
            if type(choices) is not list or len(choices) != 1:
                raise ValueError("one_choice_required")
            choice = choices[0]
            if type(choice) is not dict or type(choice.get("message")) is not dict:
                raise ValueError("message_object_required")
            message = choice["message"]
            content = message.get("content")
            if content is not None and type(content) is not str:
                raise ValueError("content_string_or_null_required")
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as error:
            attempt = ProviderAttempt(
                call.logical_index,
                attempt_index,
                call.call_id,
                request_body,
                response_body,
                {"provider_envelope_error": str(error)},
                None,
                None,
                http_status,
                started.isoformat(),
                ended.isoformat(),
                elapsed,
                "provider_envelope_invalid",
            )
            raise InvocationFailure("provider_envelope_invalid", attempt, False) from error
        return ProviderAttempt(
            call.logical_index,
            attempt_index,
            call.call_id,
            request_body,
            response_body,
            envelope,
            message,
            content,
            http_status,
            started.isoformat(),
            ended.isoformat(),
            elapsed,
        )


class EvidenceWriter:
    def __init__(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=False)
        self.directory = directory
        self.calls = directory / "calls"
        self.calls.mkdir()

    def write_json(self, relative: str, value: object) -> None:
        (self.directory / relative).write_text(
            json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        )

    def write_attempt(self, call: LogicalCall, attempt: ProviderAttempt) -> None:
        stem = f"{call.logical_index:02d}-{call.call_id}-a{attempt.attempt_index}"
        (self.calls / f"{stem}.request.json").write_bytes(attempt.request_body)
        (self.calls / f"{stem}.response.json").write_bytes(attempt.response_body)
        self.write_json(
            f"calls/{stem}.meta.json",
            {
                "logical_index": call.logical_index,
                "attempt_index": attempt.attempt_index,
                "call_id": call.call_id,
                "responsibility": call.responsibility,
                "offer_key": call.offer_key,
                "probe_id": call.probe_id,
                "repetition": call.repetition,
                "request_sha256": sha256_bytes(attempt.request_body),
                "response_sha256": sha256_bytes(attempt.response_body),
                "response_envelope": attempt.response_envelope,
                "message": attempt.message,
                "http_status": attempt.http_status,
                "started_at": attempt.started_at,
                "ended_at": attempt.ended_at,
                "elapsed_seconds": attempt.elapsed_seconds,
                "error": attempt.error,
                "retry_of_attempt": attempt.retry_of_attempt,
            },
        )

    def write_logical(self, call: LogicalCall, value: object) -> None:
        self.write_json(f"calls/{call.logical_index:02d}-{call.call_id}.logical.json", value)


class ContactStop(RuntimeError):
    pass


class ContactRunner:
    def __init__(
        self,
        invoker: Invoker,
        writer: EvidenceWriter,
        provider_receipt: dict[str, object],
        physical_ceiling: int = PHYSICAL_CALL_CEILING,
    ) -> None:
        self.invoker = invoker
        self.writer = writer
        self.provider_receipt = provider_receipt
        self.physical_ceiling = physical_ceiling
        self.physical_attempts = 0
        self.logical_records: list[dict[str, object]] = []

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
                    attempt = ProviderAttempt(
                        **{
                            **asdict(attempt),
                            "retry_of_attempt": 1,
                        }
                    )
                self.writer.write_attempt(call, attempt)
                if failure.retryable and attempt_index == 1:
                    continue
                raise ContactStop(failure.reason) from failure
            if attempt.request_body != call.request_body:
                self.writer.write_attempt(call, attempt)
                raise ContactStop("request_bytes_drifted")
            if attempt_index == 2:
                attempt = ProviderAttempt(
                    **{
                        **asdict(attempt),
                        "retry_of_attempt": 1,
                    }
                )
            self.writer.write_attempt(call, attempt)
            return attempt
        raise AssertionError("unreachable")

    def record_actor(
        self, call: LogicalCall, attempt: ProviderAttempt
    ) -> dict[str, object]:
        parsed = parse_action(attempt.content)
        result: RevisionResult | None = None
        if parsed.action is not None and call.situation is not None:
            result = apply_revision_gated_release(call.situation, parsed.action)
        record = {
            "logical_index": call.logical_index,
            "call_id": call.call_id,
            "responsibility": call.responsibility,
            "offer_key": call.offer_key,
            "probe_id": call.probe_id,
            "repetition": call.repetition,
            "situation": None if call.situation is None else asdict(call.situation),
            "message": attempt.message,
            "content": attempt.content,
            "surfaced_action": parsed.action,
            "action_refusal": parsed.refusal,
            "environment_result": None if result is None else asdict(result),
        }
        self.logical_records.append(record)
        self.writer.write_logical(call, record)
        return record

    def summary(self, state: str, stop_reason: str | None) -> dict[str, object]:
        later = [item for item in self.logical_records if item.get("probe_id") is not None]
        cells = []
        for probe in PROBES:
            for offer_key in OFFERS:
                members = [
                    item
                    for item in later
                    if item["probe_id"] == probe.probe_id
                    and item["offer_key"] == offer_key
                ]
                if not members:
                    continue
                actions = [item["surfaced_action"] for item in members]
                cells.append(
                    {
                        "probe_id": probe.probe_id,
                        "offer_key": offer_key,
                        "actions": actions,
                        "action_refusals": [item["action_refusal"] for item in members],
                        "environment_dispositions": [
                            None
                            if item["environment_result"] is None
                            else item["environment_result"]["disposition"]
                            for item in members
                        ],
                        "within_cell_action_disagreement": len(
                            {json.dumps(action) for action in actions}
                        )
                        > 1,
                    }
                )
        return {
            "protocol": PROTOCOL_VERSION,
            "evidence_class": "exploratory_observation_only",
            "contact_state": state,
            "stop_reason": stop_reason,
            "model": MODEL,
            "model_digest": MODEL_DIGEST,
            "planned_logical_calls": PLANNED_LOGICAL_CALLS,
            "completed_logical_calls": len(self.logical_records),
            "physical_call_ceiling": self.physical_ceiling,
            "physical_attempts": self.physical_attempts,
            "cells": cells,
            "formation_verdict": None,
        }


def raw_experience_offer(experience: dict[str, object]) -> str:
    return json.dumps(experience, indent=2, sort_keys=True, ensure_ascii=False)


def _protocol_record() -> dict[str, object]:
    return {
        "protocol": PROTOCOL_VERSION,
        "model": MODEL,
        "inspect_tag": INSPECT_TAG,
        "model_digest": MODEL_DIGEST,
        "endpoint": ENDPOINT,
        "actor_settings": ACTOR_SETTINGS,
        "interpreter_settings": INTERPRETER_SETTINGS,
        "static_lesson": STATIC_LESSON,
        "static_lesson_author": "human_protocol_owner_pre_contact",
        "interface_state": asdict(INTERFACE_STATE),
        "acquisition_state": asdict(ACQUISITION_STATE),
        "probes": [
            {"probe_id": probe.probe_id, "state": asdict(probe.state)}
            for probe in PROBES
        ],
        "offers": list(OFFERS),
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "validation_verdicts_forbidden": True,
    }


def run_contact(
    invoker: Invoker,
    directory: Path,
    provider_receipt: dict[str, object],
    physical_ceiling: int = PHYSICAL_CALL_CEILING,
) -> dict[str, object]:
    writer = EvidenceWriter(directory)
    writer.write_json("protocol.json", _protocol_record())
    writer.write_json("provider.json", provider_receipt)
    runner = ContactRunner(invoker, writer, provider_receipt, physical_ceiling)

    if provider_receipt.get("valid") is not True:
        summary = runner.summary("stopped", "provider_receipt_invalid")
        writer.write_json("summary.json", summary)
        return summary

    try:
        interface_call = LogicalCall(
            1,
            "interface-disposable",
            "actor",
            actor_envelope(INTERFACE_STATE),
            situation=INTERFACE_STATE,
        )
        interface_record = runner.record_actor(interface_call, runner.invoke(interface_call))
        if interface_record["surfaced_action"] is None:
            summary = runner.summary("stopped", "interface_action_unobservable")
            writer.write_json("summary.json", summary)
            return summary

        acquisition_call = LogicalCall(
            2,
            "acquisition",
            "actor",
            actor_envelope(ACQUISITION_STATE),
            situation=ACQUISITION_STATE,
        )
        acquisition = runner.record_actor(
            acquisition_call, runner.invoke(acquisition_call)
        )
        if acquisition["surfaced_action"] is None:
            summary = runner.summary("stopped", "acquisition_action_unobservable")
            writer.write_json("summary.json", summary)
            return summary

        experience = {
            "situation": acquisition["situation"],
            "model_message": acquisition["message"],
            "surfaced_action": acquisition["surfaced_action"],
            "environment_result": acquisition["environment_result"],
        }
        writer.write_json("acquisition_experience.json", experience)

        interpreter_call = LogicalCall(
            3,
            "runtime-interpretation",
            "interpreter",
            interpretation_envelope(experience),
        )
        interpreter_attempt = runner.invoke(interpreter_call)
        interpretation = "" if interpreter_attempt.content is None else interpreter_attempt.content
        interpreter_record = {
            "logical_index": 3,
            "call_id": interpreter_call.call_id,
            "responsibility": "interpreter",
            "offer_key": None,
            "probe_id": None,
            "repetition": None,
            "author": "cold_model",
            "source_experience": "acquisition_experience.json",
            "message": interpreter_attempt.message,
            "content": interpretation,
        }
        runner.logical_records.append(interpreter_record)
        writer.write_logical(interpreter_call, interpreter_record)
        writer.write_json("runtime_interpretation.json", interpreter_record)

        offers: dict[str, str | None] = {
            "no_offer": None,
            "raw_experience": raw_experience_offer(experience),
            "runtime_interpretation": interpretation,
            "frozen_lesson": STATIC_LESSON,
        }
        for call in later_schedule(offers):
            runner.record_actor(call, runner.invoke(call))
    except ContactStop as stop:
        summary = runner.summary("stopped", str(stop))
        writer.write_json("summary.json", summary)
        return summary

    summary = runner.summary("complete", None)
    writer.write_json("summary.json", summary)
    return summary


def _run_command(command: tuple[str, ...]) -> dict[str, object]:
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    return {
        "command": list(command),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def collect_provider_receipt() -> dict[str, object]:
    version = _run_command(("docker", "model", "version"))
    status = _run_command(("docker", "model", "status"))
    inventory = _run_command(("docker", "model", "list"))
    inspection = _run_command(("docker", "model", "inspect", MODEL))
    reasons: list[str] = []
    for name, record in (
        ("version", version),
        ("status", status),
        ("inventory", inventory),
        ("inspection", inspection),
    ):
        if record["returncode"] != 0:
            reasons.append(f"{name}_command_failed")
    parsed_inspection: object = None
    if not reasons:
        try:
            parsed_inspection = json.loads(str(inspection["stdout"]))
            if type(parsed_inspection) is not dict:
                raise ValueError("inspection_object_required")
            if parsed_inspection.get("id") != MODEL_DIGEST:
                reasons.append("model_digest_mismatch")
            if INSPECT_TAG not in parsed_inspection.get("tags", []):
                reasons.append("model_tag_mismatch")
            config = parsed_inspection.get("config")
            if type(config) is not dict or config.get("architecture") != "qwen3":
                reasons.append("model_architecture_mismatch")
        except (json.JSONDecodeError, ValueError):
            reasons.append("inspection_invalid")
    if "llama.cpp" not in str(status["stdout"]) or "Running" not in str(status["stdout"]):
        reasons.append("llama_runner_not_running")
    if "qwen3:14B-Q6_K" not in str(inventory["stdout"]):
        reasons.append("model_not_in_inventory")
    return {
        "valid": not reasons,
        "refusals": reasons,
        "endpoint": ENDPOINT,
        "version": version,
        "status": status,
        "inventory": inventory,
        "inspection": inspection,
        "parsed_inspection": parsed_inspection,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--evidence-dir", type=Path, required=True)
    args = parser.parse_args()
    if not args.live:
        raise SystemExit("live contact requires --live")
    receipt = collect_provider_receipt()
    summary = run_contact(LiveInvoker(), args.evidence_dir, receipt)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
