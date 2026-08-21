"""Parse explicit retained clerk prose before fixed-order rendering."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
from typing import Any, Callable

from contact import canonical_clerical_record_diagnostic as canonical
from contact import distributional_developmental_comparison as base
from contact import learned_clerical_instrument_exploration as learned
from contact import staged_clerical_instrument_successor as source
from micro_environment.unselected_lineage_behavior import (
    FIRST_INCREASES,
    SECOND_INCREASES,
    LineageProfile,
    LineageState,
)
from unselected_lineage_specimen import oracle_action


PROTOCOL_VERSION = "clerical-prose-parser-diagnostic-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "CLERICAL_PROSE_PARSER_DIAGNOSTIC.md"
SOURCE_DIR = canonical.SOURCE_DIR
SOURCE_PACKET_SHA256 = canonical.SOURCE_PACKET_SHA256
SOURCE_SPECIMEN_SHA256 = canonical.SOURCE_SPECIMEN_SHA256

LINEAGES = canonical.LINEAGES
DESIGN_POSITIONS = canonical.DESIGN_POSITIONS
CASES = canonical.CASES
BRANCHES = canonical.BRANCHES
PLANNED_LOGICAL_CALLS = canonical.PLANNED_LOGICAL_CALLS
PHYSICAL_CALL_CEILING = canonical.PHYSICAL_CALL_CEILING

PARSER_SYSTEM = """You are a clerical prose parser. You have no memory outside this request.

You receive two sentences that explicitly state the effect of the first displayed control and the second displayed control. The sentences may appear in either order. Extract the two stated facts. Do not infer an unstated fact.

Return exactly one JSON object with these keys and no others:
{"first_control_effect":"<increases_position or decreases_position>","second_control_effect":"<decreases_position or increases_position>"}
Do not add commentary."""

_ORIGINAL_LOAD = canonical.load_source_artifacts
_ORIGINAL_SOURCE_SCOPES = canonical.source_scopes


class ParserRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


@dataclass(frozen=True)
class LaterCase:
    state: LineageState
    profile: LineageProfile
    description: str
    scope: dict[str, str]
    design_position: str | None


@dataclass(frozen=True)
class Lineage:
    name: str
    designs: dict[str, learned.Design]
    cases: dict[str, LaterCase]
    record_ids: dict[str, str]


def make_lineage(name: str, index: int) -> Lineage:
    designs = learned.DESIGN_SETS[index - 1]
    cases = {}
    for case_index, case_name in enumerate(CASES, 1):
        source_case = source.LINEAGE_DATA[name].cases[case_name]
        if source_case.design_position is not None:
            increasing_slot = designs[source_case.design_position].increasing_slot
        else:
            increasing_slot = (
                FIRST_INCREASES
                if source_case.profile.increasing_slot == FIRST_INCREASES
                else SECOND_INCREASES
            )
        profile = LineageProfile(
            opaque(f"{name}:{case_name}:fresh-family"), increasing_slot
        )
        position = 19100 + index * 523 + case_index * 107
        target = position + (1 if case_name.endswith("up") else -1)
        state = LineageState(
            profile.controller_family,
            opaque(f"{name}:{case_name}:device"),
            position,
            target,
            (
                opaque(f"{name}:{case_name}:first"),
                opaque(f"{name}:{case_name}:second"),
            ),
        )
        cases[case_name] = LaterCase(
            state,
            profile,
            source_case.description,
            source_case.scope,
            source_case.design_position,
        )
    return Lineage(
        name,
        designs,
        cases,
        {position: opaque(f"{name}:{position}:record") for position in DESIGN_POSITIONS},
    )


LINEAGE_DATA = {
    name: make_lineage(name, index) for index, name in enumerate(LINEAGES, 1)
}


def parse_explicit_sentence(content: str) -> dict[str, str] | None:
    matches = re.findall(
        r"The (first|second) displayed control (increases|decreases) position\.",
        content,
    )
    if len(matches) != 2 or {slot for slot, _ in matches} != {"first", "second"}:
        return None
    values = {
        slot: learned.INCREASES if effect == "increases" else learned.DECREASES
        for slot, effect in matches
    }
    if {values["first"], values["second"]} != {learned.INCREASES, learned.DECREASES}:
        return None
    return {
        "first_control_effect": values["first"],
        "second_control_effect": values["second"],
    }


def load_source_artifacts() -> dict[str, Any]:
    artifacts = _ORIGINAL_LOAD()
    packet = json.loads((SOURCE_DIR / "packet.json").read_bytes())
    sentences = {name: {} for name in LINEAGES}
    for row in packet["calls"]:
        if row["responsibility"] != "clerical_sentence":
            continue
        parsed = parse_explicit_sentence(row["content"])
        expected = canonical.expected_record(
            LINEAGE_DATA[row["lineage"]].designs[row["design_position"]]
        )
        if parsed != expected:
            raise ParserRefusal("source_sentence_not_semantically_exact")
        sentences[row["lineage"]][row["design_position"]] = row["content"]
    if any(set(rows) != set(DESIGN_POSITIONS) for rows in sentences.values()):
        raise ParserRefusal("source_sentences_incomplete")
    for name in LINEAGES:
        artifacts[name]["source_scopes"] = _ORIGINAL_SOURCE_SCOPES(artifacts, name)
        artifacts[name]["transcriptions"] = sentences[name]
    return artifacts


def source_scopes(artifacts: dict[str, Any], name: str) -> dict[str, dict[str, str]]:
    return artifacts[name]["source_scopes"]


def parser_body(sentence: str) -> bytes:
    record = {"explicit_effect_account": sentence}
    return learned.canonical_envelope(
        learned.INSTRUMENT_MODEL,
        PARSER_SYSTEM,
        f"PROSE PARSE REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",
        learned.INSTRUMENT_SETTINGS,
    )


def specimen() -> dict[str, Any]:
    artifacts = load_source_artifacts()
    return {
        "branches": list(BRANCHES),
        "cases": list(CASES),
        "instrument_model": learned.INSTRUMENT_MODEL,
        "instrument_model_digest": learned.INSTRUMENT_MODEL_DIGEST,
        "later_calls": canonical.LATER_CALLS,
        "participant_model": base.MODEL,
        "participant_model_digest": base.MODEL_DIGEST,
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "record_calls": canonical.RECORD_CALLS,
        "repeats": canonical.REPEATS,
        "source_packet_sha256": SOURCE_PACKET_SHA256,
        "source_specimen_sha256": SOURCE_SPECIMEN_SHA256,
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "lineages": {
            name: {
                "record_ids": lineage.record_ids,
                "retained_sentence_sha256": {
                    position: base.sha256(
                        artifacts[name]["transcriptions"][position].encode()
                    )
                    for position in DESIGN_POSITIONS
                },
                "cases": {
                    case_name: {
                        "device": learned.public_device(case.state, case.description),
                        "expected_action": oracle_action(case.state, case.profile),
                        "expected_record_ids": canonical.expected_selection(
                            lineage, case_name
                        ),
                        "retained_normalized_scope": artifacts[name]["normalizations"][case_name],
                    }
                    for case_name, case in lineage.cases.items()
                },
            }
            for name, lineage in LINEAGE_DATA.items()
        },
    }


@contextmanager
def configured_canonical_module():
    names = {
        "PROTOCOL_VERSION": PROTOCOL_VERSION,
        "SPEC_PATH": SPEC_PATH,
        "LINEAGE_DATA": LINEAGE_DATA,
        "load_source_artifacts": load_source_artifacts,
        "record_body": parser_body,
        "source_scopes": source_scopes,
        "specimen": specimen,
    }
    old = {name: getattr(canonical, name) for name in names}
    try:
        for name, value in names.items():
            setattr(canonical, name, value)
        yield
    finally:
        for name, value in old.items():
            setattr(canonical, name, value)


Transport = Callable[[bytes], tuple[int, bytes]]


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    with configured_canonical_module():
        packet = canonical.execute(transport, evidence_dir)
    for row in packet["calls"]:
        if row["responsibility"] == "canonical_effect_record":
            row["responsibility"] = "clerical_prose_parse"
    packet["parser_records"] = packet.pop("canonical_records")
    packet["instrument_verdict"]["scope"] = "clerical_prose_parser_diagnostic"
    if packet["instrument_verdict"]["class"] == "canonical_record_only":
        packet["instrument_verdict"]["class"] = "parser_only"
    packet["protocol_version"] = PROTOCOL_VERSION
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise ParserRefusal("retained_specimen_mismatch")
    retained = json.loads((evidence_dir / "packet.json").read_bytes())
    entries = []
    for meta_path in sorted((evidence_dir / "attempts").glob("*.meta.json")):
        stem = meta_path.name.removesuffix(".meta.json")
        meta = json.loads(meta_path.read_text())
        request = (evidence_dir / "attempts" / f"{stem}.request.json").read_bytes()
        response = (evidence_dir / "attempts" / f"{stem}.response.bin").read_bytes()
        entries.append((request, response, meta))
    position = 0

    def transport(body: bytes) -> tuple[int, bytes]:
        nonlocal position
        request, response, meta = entries[position]
        position += 1
        if request != body:
            raise ParserRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise ParserRefusal("evidence_replay_mismatch")
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
    if args.evidence_dir is None:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        args.evidence_dir = Path("evidence") / f"clerical-prose-parser-{run_id}"
    started = time.monotonic()
    receipt = learned.collect_provider_receipt()
    if not receipt["valid"]:
        raise ParserRefusal("provider_identity_mismatch")
    packet = execute(base.live_transport, args.evidence_dir)
    (args.evidence_dir / "provider.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    replay_evidence(args.evidence_dir)
    print(json.dumps({
        "elapsed_seconds": time.monotonic() - started,
        "evidence_dir": str(args.evidence_dir),
        "instrument_verdict": packet["instrument_verdict"],
        "logical_calls": packet["logical_calls"],
        "physical_attempts": packet["physical_attempts"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
