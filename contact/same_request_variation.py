"""Measure action variation across repeated byte-identical Qwen requests.

Prospective exploratory note
----------------------------
Question: how often does the current cold-model interface change its action on
an identical request, and does that variation differ across selected cases?
Observation of interest: the action distribution for each request, especially
the request that produced the packet's only apparent branch difference.
Model/interface: the exact ``ai/qwen3:14B-Q6_K`` Docker Model Runner request
bodies retained by the completed unselected-lineage contact.
Budget: four requests, eight calls per request, 32 logical calls and at most 36
physical attempts. Only transport failures may be retried.
Stopping condition: stop after the fixed schedule or physical ceiling; retain
unavailable and malformed outputs rather than replacing them.
Evidence destination: ``evidence/same-request-variation-<run-id>/``.

This is a repeatability measurement, not a developmental comparison. It has no
Formation or validation verdict.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PROTOCOL_VERSION = "same-request-variation-v1"
MODEL = "ai/qwen3:14B-Q6_K"
MODEL_DIGEST = "sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219"
ENDPOINT = "http://localhost:12434/engines/llama.cpp/v1/chat/completions"
SOURCE_EVIDENCE = Path(__file__).parents[1] / "evidence" / "unselected-lineage-behavior-contact-20260819-contact"
SOURCE_INVOCATIONS = ("iv077", "iv087", "iv088", "iv089")
REPEATS = 8
PLANNED_LOGICAL_CALLS = len(SOURCE_INVOCATIONS) * REPEATS
PHYSICAL_CALL_CEILING = 36
MAX_RETRIES = 1


class VariationRefusal(ValueError):
    pass


@dataclass(frozen=True)
class SourceRequest:
    invocation: str
    request: bytes
    request_sha256: str
    allowed_actions: tuple[str, str, str]
    original_outputs: tuple[str, ...]
    original_correctness: tuple[bool, ...]


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _request_path(invocation: str) -> Path:
    matches = sorted((SOURCE_EVIDENCE / "attempts").glob(f"*-{invocation}-a1.request.json"))
    if len(matches) != 1:
        raise VariationRefusal(f"source_request_missing:{invocation}")
    return matches[0]


def load_sources() -> tuple[SourceRequest, ...]:
    packet = json.loads((SOURCE_EVIDENCE / "packet.json").read_text(encoding="utf-8"))
    later = packet["projection"]["later"]
    result = []
    for invocation in SOURCE_INVOCATIONS:
        raw = _request_path(invocation).read_bytes()
        body = json.loads(raw)
        if canonical_json_bytes(body) != raw:
            raise VariationRefusal(f"source_request_not_canonical:{invocation}")
        if body.get("model") != MODEL:
            raise VariationRefusal(f"source_model_mismatch:{invocation}")
        user = json.loads(body["messages"][1]["content"].removeprefix("ACTION REQUEST\n").removesuffix("\n/no_think"))
        actions = tuple(user["device"]["allowed_actions"])
        row = next(item for item in later if item["invocation"] == invocation)
        same = [item for item in later if item["request_sha256"] == row["request_sha256"]]
        if sha256(raw) != row["request_sha256"]:
            raise VariationRefusal(f"source_hash_mismatch:{invocation}")
        result.append(SourceRequest(
            invocation, raw, sha256(raw), actions,
            tuple(item["proposal"].get("content", "<unavailable>") for item in same),
            tuple(bool(item["correct_action"]) for item in same),
        ))
    return tuple(result)


def schedule(sources: tuple[SourceRequest, ...]) -> tuple[tuple[int, SourceRequest], ...]:
    return tuple((repeat, source) for repeat in range(1, REPEATS + 1) for source in sources)


def parse_provider(raw: bytes, allowed: tuple[str, str, str]) -> tuple[str, str | None, dict[str, Any]]:
    try:
        envelope = json.loads(raw)
        choice = envelope["choices"][0]
        content = choice["message"]["content"]
        value = json.loads(content)
        if type(value) is not dict or set(value) != {"action"} or value["action"] not in allowed:
            return "invalid", None, envelope
        return "available", value["action"], envelope
    except (KeyError, IndexError, TypeError, UnicodeDecodeError, json.JSONDecodeError):
        return "invalid", None, {}


Transport = Callable[[bytes], tuple[int, bytes]]


def live_transport(body: bytes) -> tuple[int, bytes]:
    request = Request(ENDPOINT, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=120) as response:
            return response.status, response.read()
    except HTTPError as error:
        return error.code, error.read()
    except URLError as error:
        raise ConnectionError(str(error)) from error


def run(transport: Transport, evidence_dir: Path, *, clock: Callable[[], float] = time.monotonic) -> dict[str, Any]:
    sources = load_sources()
    evidence_dir.mkdir(parents=True, exist_ok=False)
    attempts_dir = evidence_dir / "attempts"
    attempts_dir.mkdir()
    attempts = []
    calls = []
    physical = 0
    started = clock()
    for index, (repeat, source) in enumerate(schedule(sources), 1):
        final = None
        for attempt in range(1, MAX_RETRIES + 2):
            if physical >= PHYSICAL_CALL_CEILING:
                raise VariationRefusal("physical_call_ceiling")
            physical += 1
            name = f"{physical:03d}-sv{index:03d}-a{attempt}"
            (attempts_dir / f"{name}.request.json").write_bytes(source.request)
            status = None
            raw = b""
            error = None
            try:
                status, raw = transport(source.request)
            except ConnectionError as exc:
                error = str(exc)
            (attempts_dir / f"{name}.response.bin").write_bytes(raw)
            retryable = error is not None or status in {408, 429, 500, 502, 503, 504}
            meta = {"attempt": attempt, "error": error, "http_status": status, "logical_index": index,
                    "request_sha256": source.request_sha256, "response_sha256": sha256(raw),
                    "retryable": retryable, "source_invocation": source.invocation}
            (attempts_dir / f"{name}.meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
            attempts.append(meta)
            if retryable and attempt <= MAX_RETRIES:
                continue
            final = (status, raw, error)
            break
        assert final is not None
        status, raw, error = final
        availability, action, envelope = parse_provider(raw, source.allowed_actions) if status == 200 and error is None else ("unavailable", None, {})
        calls.append({"action": action, "availability": availability, "logical_index": index,
                      "repeat": repeat, "request_sha256": source.request_sha256,
                      "source_invocation": source.invocation,
                      "provider_usage": envelope.get("usage")})
    distributions = {}
    for source in sources:
        rows = [row for row in calls if row["source_invocation"] == source.invocation]
        counts = Counter(row["action"] if row["action"] is not None else f"<{row['availability']}>" for row in rows)
        distributions[source.invocation] = {
            "action_counts": dict(sorted(counts.items())),
            "distinct_outcomes": len(counts),
            "original_correctness": list(source.original_correctness),
            "original_outputs": list(source.original_outputs),
            "request_sha256": source.request_sha256,
        }
    packet = {
        "attempts": attempts, "calls": calls, "elapsed_seconds": clock() - started,
        "formation_verdict": None, "logical_calls": len(calls), "model": MODEL,
        "model_digest": MODEL_DIGEST, "physical_attempts": physical,
        "protocol_version": PROTOCOL_VERSION, "request_distributions": distributions,
        "validation_verdict": None,
    }
    (evidence_dir / "packet.json").write_bytes(canonical_json_bytes(packet))
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args(argv)
    if not args.live:
        print(json.dumps({"mode": "smoke_no_contact", "planned_logical_calls": PLANNED_LOGICAL_CALLS, "side_effects_entered": False}, sort_keys=True))
        return 0
    if args.evidence_dir is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        args.evidence_dir = Path("evidence") / f"same-request-variation-{stamp}"
    packet = run(live_transport, args.evidence_dir)
    print(json.dumps({"evidence_dir": str(args.evidence_dir), "logical_calls": packet["logical_calls"], "physical_attempts": packet["physical_attempts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
