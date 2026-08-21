"""Run the fresh composed revision engagement successor."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any, Callable

from contact import composed_clerical_revision_validation as base_validation
from contact import distributional_developmental_comparison as base
from contact import learned_clerical_instrument_exploration as learned
from contact import learned_clerical_revision_exploration as revision


PROTOCOL_VERSION = "composed-clerical-revision-engagement-successor-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "COMPOSED_CLERICAL_REVISION_ENGAGEMENT_SUCCESSOR.md"
LINEAGES = ("engagement_01", "engagement_02", "engagement_03", "engagement_04")
LINEAGE_DATA = {
    name: revision.make_lineage(name, index)
    for index, name in enumerate(LINEAGES, 1)
}
ENGAGEMENT_BRANCHES = (
    base_validation.SUPPLIED,
    base_validation.ADMITTED,
)
VERDICT_SCOPE = "composed_clerical_revision_engagement_successor"
PLANNED_LOGICAL_CALLS = base_validation.PLANNED_LOGICAL_CALLS
PHYSICAL_CALL_CEILING = base_validation.PHYSICAL_CALL_CEILING


class SuccessorRefusal(ValueError):
    pass


@contextmanager
def configured_validation():
    original = (
        base_validation.PROTOCOL_VERSION,
        base_validation.SPEC_PATH,
        base_validation.LINEAGES,
        base_validation.LINEAGE_DATA,
    )
    try:
        base_validation.PROTOCOL_VERSION = PROTOCOL_VERSION
        base_validation.SPEC_PATH = SPEC_PATH
        base_validation.LINEAGES = LINEAGES
        base_validation.LINEAGE_DATA = LINEAGE_DATA
        yield
    finally:
        (
            base_validation.PROTOCOL_VERSION,
            base_validation.SPEC_PATH,
            base_validation.LINEAGES,
            base_validation.LINEAGE_DATA,
        ) = original


def specimen() -> dict[str, Any]:
    with configured_validation():
        return base_validation.specimen()


Transport = Callable[[bytes], tuple[int, bytes]]


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    with configured_validation():
        return base_validation.execute(
            transport,
            evidence_dir,
            engagement_branches=ENGAGEMENT_BRANCHES,
            verdict_scope=VERDICT_SCOPE,
        )


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise SuccessorRefusal("retained_specimen_mismatch")
    retained = json.loads((evidence_dir / "packet.json").read_bytes())
    entries = []
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        entries.append((
            (evidence_dir / "attempts" / f"{stem}.request.json").read_bytes(),
            (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes(),
            json.loads(meta_path.read_text()),
        ))
    position = 0

    def transport(body: bytes) -> tuple[int, bytes]:
        nonlocal position
        request, response, meta = entries[position]
        position += 1
        if request != body:
            raise SuccessorRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise SuccessorRefusal("evidence_replay_mismatch")
    return replayed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args(argv)
    if not args.live:
        print(json.dumps({
            "mode": "smoke_no_contact",
            "planned_logical_calls": PLANNED_LOGICAL_CALLS,
            "side_effects_entered": False,
        }, sort_keys=True))
        return 0
    evidence_dir = args.evidence_dir or Path("evidence") / (
        "composed-clerical-revision-engagement-successor-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    receipt = learned.collect_provider_receipt()
    if not receipt["valid"]:
        raise SuccessorRefusal("provider_identity_mismatch")
    started = time.monotonic()
    packet = execute(base.live_transport, evidence_dir)
    (evidence_dir / "provider.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    replay_evidence(evidence_dir)
    print(json.dumps({
        "elapsed_seconds": time.monotonic() - started,
        "evidence_dir": str(evidence_dir),
        "logical_calls": packet["logical_calls"],
        "physical_attempts": packet["physical_attempts"],
        "validation_verdict": packet["validation_verdict"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
