"""Compare staged relation-sentence and effect-table consumption."""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Callable

from contact import balanced_relation_staged_validation as balanced
from contact import distributional_developmental_comparison as base
from contact import representation_class_exploration as forms
from contact import staged_chain_validation as prior
from micro_environment.unselected_lineage_behavior import (
    FIRST_INCREASES,
    SECOND_INCREASES,
    LineageProfile,
    LineageState,
    ProposalReceipt,
    apply_committed_action,
)
from unselected_lineage_specimen import oracle_action


PROTOCOL_VERSION = "staged-representation-consumption-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "STAGED_REPRESENTATION_CONSUMPTION.md"
WORLDS = tuple(f"world_{index:02d}" for index in range(1, 7))
CASES = prior.CASES
COLD = "cold"
RAW = "raw_experience"
SENTENCE = "authored_sentence_scoped"
TABLE = "authored_table_scoped"
SENTENCE_UNGATED = "authored_sentence_ungated"
TABLE_UNGATED = "authored_table_ungated"
STATIC_SENTENCE = "supplied_sentence_scoped"
STATIC_TABLE = "supplied_table_scoped"
BRANCHES = (
    COLD,
    RAW,
    SENTENCE,
    TABLE,
    SENTENCE_UNGATED,
    TABLE_UNGATED,
    STATIC_SENTENCE,
    STATIC_TABLE,
)
REPEATS = 3
AUTHORSHIP_CALLS = len(WORLDS) * 4
LATER_CALLS = len(WORLDS) * len(CASES) * len(BRANCHES) * REPEATS
PLANNED_LOGICAL_CALLS = AUTHORSHIP_CALLS + LATER_CALLS
PHYSICAL_CALL_CEILING = 608
MAX_RETRIES = 8

STAGED_SENTENCE_SYSTEM = """You author one retained relation sentence in a controlled cold-model experiment. You have no memory outside this request.

The public device identifies the controller family. The model-authored observation states what one displayed slot did. Within one family, one displayed slot increases position and the other decreases it. Infer the unobserved slot from that complement.
Return exactly one sentence in this form:
For controller family <controller_family>, the first displayed control <increases or decreases> position and the second displayed control <decreases or increases> position.
Return no markdown, commentary, action strings, brackets, or labels."""


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


def make_world(name: str, index: int) -> prior.World:
    increasing_slot = FIRST_INCREASES if index % 2 else SECOND_INCREASES
    profile = LineageProfile(opaque(f"{name}:family"), increasing_slot)
    position = 900 + index * 229
    acquisition = LineageState(
        profile.controller_family,
        opaque(f"{name}:acquisition-device"),
        position,
        position - 1,
        (opaque(f"{name}:acquisition-first"), opaque(f"{name}:acquisition-second")),
    )
    opposite = SECOND_INCREASES if increasing_slot == FIRST_INCREASES else FIRST_INCREASES
    cases = {}
    profiles = {}
    for case_index, case in enumerate(CASES, 1):
        matching = case.startswith("same")
        case_profile = profile if matching else LineageProfile(
            opaque(f"{name}:{case}:family"), opposite
        )
        position = 1800 + index * 487 + case_index * 71
        cases[case] = LineageState(
            case_profile.controller_family,
            opaque(f"{name}:{case}:device"),
            position,
            position + (1 if case.endswith("up") else -1),
            (opaque(f"{name}:{case}:first"), opaque(f"{name}:{case}:second")),
        )
        profiles[case] = case_profile
    return prior.World(name, profile, acquisition, cases, profiles)


WORLD_DATA = {name: make_world(name, index) for index, name in enumerate(WORLDS, 1)}


def expected_sentence(world: prior.World) -> str:
    return forms.expected_representation(world, "relation_sentence")


def expected_table(world: prior.World) -> str:
    return forms.expected_representation(world, "effect_table")


def sentence_body(world: prior.World, observation: str) -> bytes:
    record = {
        "authored_observation": observation,
        "public_device": base.public_device(world.acquisition),
        "responsibility": "Author the complete controller relation sentence.",
    }
    return base.envelope(
        STAGED_SENTENCE_SYSTEM,
        f"SENTENCE REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",
        {**base.AUTHORSHIP_SETTINGS, "max_tokens": 128},
    )


def specimen() -> dict[str, Any]:
    return {
        "authorship_calls": AUTHORSHIP_CALLS,
        "branches": list(BRANCHES),
        "cases": list(CASES),
        "later_calls": LATER_CALLS,
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "observation_system_sha256": base.sha256(prior.staged.OBSERVATION_SYSTEM.encode()),
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "protocol_version": PROTOCOL_VERSION,
        "relation_groups": {
            relation: [
                name for name, world in WORLD_DATA.items()
                if world.profile.increasing_slot == relation
            ]
            for relation in (FIRST_INCREASES, SECOND_INCREASES)
        },
        "repeats": REPEATS,
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "staged_sentence_system_sha256": base.sha256(STAGED_SENTENCE_SYSTEM.encode()),
        "staged_table_system_sha256": base.sha256(prior.staged.STAGED_TABLE_SYSTEM.encode()),
        "worlds": {
            name: {
                "acquisition": base.public_device(world.acquisition),
                "cases": {
                    case: {
                        "device": base.public_device(state),
                        "expected_action": oracle_action(state, world.case_profiles[case]),
                    }
                    for case, state in world.cases.items()
                },
                "expected_sentence_sha256": base.sha256(expected_sentence(world).encode()),
                "expected_table_sha256": base.sha256(expected_table(world).encode()),
            }
            for name, world in WORLD_DATA.items()
        },
    }


def later_schedule() -> tuple[tuple[int, str, str, str], ...]:
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_index, case in enumerate(CASES):
            for branch_index in range(len(BRANCHES)):
                branch = BRANCHES[(repeat - 1 + branch_index) % len(BRANCHES)]
                shift = (repeat + case_index + branch_index) % len(WORLDS)
                order = WORLDS[shift:] + WORLDS[:shift]
                rows.extend((repeat, name, case, branch) for name in order)
    return tuple(rows)


@contextmanager
def configured_recorder():
    replacements = {
        "PHYSICAL_CALL_CEILING": PHYSICAL_CALL_CEILING,
        "MAX_RETRIES": MAX_RETRIES,
    }
    original = {name: getattr(prior, name) for name in replacements}
    try:
        for name, value in replacements.items():
            setattr(prior, name, value)
        yield
    finally:
        for name, value in original.items():
            setattr(prior, name, value)


Transport = Callable[[bytes], tuple[int, bytes]]


def available_content(call_result: tuple[Any, ...]) -> tuple[str, Any]:
    status, error, content, content_available, usage = call_result
    available = status == 200 and error is None and content_available
    return (content if available else ""), usage


def execute(transport: Transport, evidence_dir: Path | None = None) -> dict[str, Any]:
    with configured_recorder():
        recorder = prior.Recorder(transport, evidence_dir)
        if evidence_dir is not None:
            (evidence_dir / "specimen.json").write_bytes(base.canonical_json_bytes(specimen()))
        calls = []
        artifacts = {}
        logical_index = 0

        for name in WORLDS:
            world = WORLD_DATA[name]
            logical_index += 1
            body = prior.action_body(world.acquisition, "")
            status, error, content, content_available, usage = recorder.call(logical_index, body)
            availability, action = base.parse_action(content, world.acquisition)
            if status != 200 or error is not None:
                availability, action = "unavailable", None
            provider_available = status == 200 and error is None and content_available
            proposal = ProposalReceipt(
                provider_available,
                (action or content) if provider_available else "",
            )
            result = apply_committed_action(world.acquisition, world.profile, proposal)
            calls.append({
                "responsibility": "acquisition",
                "world": name,
                "action": action,
                "availability": availability,
                "external_result": base.exposed_result(result),
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
            })

            logical_index += 1
            body = prior.observation_body(world, proposal, result, True)
            observation, usage = available_content(recorder.call(logical_index, body))
            fields = base.exposed_result(result)
            expected_observation = prior.staged.expected_observation(
                world,
                fields.get("selected_slot", ""),
                fields.get("movement_direction", ""),
            )
            calls.append({
                "responsibility": "observation_authorship",
                "world": name,
                "content": observation,
                "exact": observation == expected_observation,
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
            })

            logical_index += 1
            body = sentence_body(world, observation)
            sentence, usage = available_content(recorder.call(logical_index, body))
            calls.append({
                "responsibility": "sentence_authorship",
                "world": name,
                "content": sentence,
                "exact": sentence == expected_sentence(world),
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
            })

            logical_index += 1
            body = prior.staged_table_body(world, observation)
            table, usage = available_content(recorder.call(logical_index, body))
            calls.append({
                "responsibility": "table_authorship",
                "world": name,
                "content": table,
                "exact": table == expected_table(world),
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
            })
            artifacts[name] = {
                "proposal": proposal,
                "result": result,
                "sentence": sentence,
                "table": table,
            }

        later = []
        for repeat, name, case, branch in later_schedule():
            logical_index += 1
            world = WORLD_DATA[name]
            state = world.cases[case]
            matching = case.startswith("same")
            artifact = artifacts[name]
            if branch == COLD:
                material = ""
            elif branch == RAW:
                material = base.canonical_json_bytes(base.experience_record(
                    world.acquisition, artifact["proposal"], artifact["result"]
                )).decode()
            elif branch == SENTENCE:
                material = artifact["sentence"] if matching else ""
            elif branch == TABLE:
                material = artifact["table"] if matching else ""
            elif branch == SENTENCE_UNGATED:
                material = artifact["sentence"]
            elif branch == TABLE_UNGATED:
                material = artifact["table"]
            elif branch == STATIC_SENTENCE:
                material = expected_sentence(world) if matching else ""
            elif branch == STATIC_TABLE:
                material = expected_table(world) if matching else ""
            else:  # pragma: no cover
                raise AssertionError(branch)

            body = prior.action_body(state, material)
            status, error, content, content_available, usage = recorder.call(
                logical_index, body
            )
            availability, action = base.parse_action(content, state)
            if status != 200 or error is not None:
                availability, action = "unavailable", None
            provider_available = status == 200 and error is None and content_available
            receipt = ProposalReceipt(
                provider_available,
                (action or content) if provider_available else "",
            )
            external_result = apply_committed_action(
                state, world.case_profiles[case], receipt
            )
            row = {
                "responsibility": "later_action",
                "world": name,
                "case": case,
                "branch": branch,
                "repeat": repeat,
                "action": action,
                "availability": availability,
                "correct_action": (
                    availability == "available"
                    and action == oracle_action(state, world.case_profiles[case])
                ),
                "external_result": base.exposed_result(external_result),
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
                "retained_material_sha256": base.sha256(material.encode()),
            }
            later.append(row)
            calls.append(row)

    distributions = {
        name: {
            branch: {
                case: {
                    "assigned": len(rows := [
                        row for row in later
                        if row["world"] == name
                        and row["branch"] == branch
                        and row["case"] == case
                    ]),
                    "correct_actions": sum(row["correct_action"] for row in rows),
                    "invalid_or_unavailable": sum(
                        row["availability"] != "available" for row in rows
                    ),
                    "distinct_outcomes": len(Counter(
                        row["action"] or f"<{row['availability']}>" for row in rows
                    )),
                }
                for case in CASES
            }
            for branch in BRANCHES
        }
        for name in WORLDS
    }

    def total(branch: str, cases: tuple[str, ...], worlds=WORLDS) -> int:
        return sum(
            distributions[name][branch][case]["correct_actions"]
            for name in worlds
            for case in cases
        )

    matching_cases = ("same_up", "same_down")
    unrelated_cases = ("other_up", "other_down")
    matching_scores = {branch: total(branch, matching_cases) for branch in BRANCHES}
    unrelated_scores = {branch: total(branch, unrelated_cases) for branch in BRANCHES}
    every_cell_valid = all(
        distributions[name][branch][case]["invalid_or_unavailable"] <= 1
        for name in WORLDS
        for branch in BRANCHES
        for case in CASES
    )
    exact_counts = {
        responsibility: sum(
            row["exact"] for row in calls if row["responsibility"] == responsibility
        )
        for responsibility in (
            "observation_authorship",
            "sentence_authorship",
            "table_authorship",
        )
    }
    format_results = {}
    for label, branch, ungated, supplied in (
        ("sentence", SENTENCE, SENTENCE_UNGATED, STATIC_SENTENCE),
        ("table", TABLE, TABLE_UNGATED, STATIC_TABLE),
    ):
        direction_scores = {
            "up": total(branch, ("same_up",)),
            "down": total(branch, ("same_down",)),
        }
        relation_scores = {}
        for relation in (FIRST_INCREASES, SECOND_INCREASES):
            names = tuple(
                name for name, world in WORLD_DATA.items()
                if world.profile.increasing_slot == relation
            )
            relation_scores[relation] = total(branch, matching_cases, names)
        unrelated_loss = unrelated_scores[COLD] - unrelated_scores[branch]
        prevented = unrelated_scores[branch] - unrelated_scores[ungated]
        usable = (
            matching_scores[branch] >= 30
            and all(score >= 14 for score in direction_scores.values())
            and all(score >= 14 for score in relation_scores.values())
            and matching_scores[supplied] - matching_scores[branch] <= 3
            and unrelated_loss <= 2
            and prevented >= 10
            and every_cell_valid
        )
        format_results[label] = {
            "direction_scores": direction_scores,
            "family_check_errors_prevented": prevented,
            "relation_scores": relation_scores,
            "unrelated_loss": unrelated_loss,
            "usable": usable,
        }
    engaged = (
        all(count == len(WORLDS) for count in exact_counts.values())
        and matching_scores[STATIC_SENTENCE] >= 30
        and matching_scores[STATIC_TABLE] >= 30
    )
    sentence_usable = format_results["sentence"]["usable"]
    table_usable = format_results["table"]["usable"]
    if not engaged:
        verdict_class = "not_engaged"
    elif not sentence_usable and not table_usable:
        verdict_class = "null"
    elif sentence_usable and not table_usable:
        verdict_class = "sentence_preferred"
    elif table_usable and not sentence_usable:
        verdict_class = "table_preferred"
    elif (
        matching_scores[SENTENCE] - matching_scores[TABLE] >= 4
        and unrelated_scores[SENTENCE] >= unrelated_scores[TABLE]
    ):
        verdict_class = "sentence_preferred"
    elif (
        matching_scores[TABLE] - matching_scores[SENTENCE] >= 4
        and unrelated_scores[TABLE] >= unrelated_scores[SENTENCE]
    ):
        verdict_class = "table_preferred"
    else:
        verdict_class = "both_usable"

    packet = {
        "attempts": recorder.attempts,
        "calls": calls,
        "every_branch_case_valid": every_cell_valid,
        "exact_authorship_counts": exact_counts,
        "formation_verdict": None,
        "format_results": format_results,
        "logical_calls": len(calls),
        "matching_scores": matching_scores,
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "physical_attempts": recorder.physical,
        "protocol_version": PROTOCOL_VERSION,
        "representation_verdict": {
            "class": verdict_class,
            "scope": "staged_representation_consumption",
        },
        "request_distributions": distributions,
        "retries": recorder.retries,
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "unrelated_scores": unrelated_scores,
    }
    if evidence_dir is not None:
        (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    if (evidence_dir / "specimen.json").read_bytes() != base.canonical_json_bytes(specimen()):
        raise prior.ValidationRefusal("retained_specimen_mismatch")
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
            raise prior.ValidationRefusal("retained_request_mismatch")
        if meta["error"] is not None:
            raise ConnectionError(meta["error"])
        return meta["http_status"], response

    replayed = execute(transport)
    if (
        position != len(entries)
        or base.canonical_json_bytes(replayed) != base.canonical_json_bytes(retained)
    ):
        raise prior.ValidationRefusal("evidence_replay_mismatch")
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
        args.evidence_dir = Path("evidence") / f"staged-representation-consumption-{run_id}"
    started = time.monotonic()
    receipt = base.collect_provider_receipt()
    if not receipt["valid"]:
        raise prior.ValidationRefusal("provider_identity_mismatch")
    packet = execute(base.live_transport, args.evidence_dir)
    (args.evidence_dir / "provider.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    replay_evidence(args.evidence_dir)
    print(json.dumps({
        "elapsed_seconds": time.monotonic() - started,
        "evidence_dir": str(args.evidence_dir),
        "logical_calls": packet["logical_calls"],
        "physical_attempts": packet["physical_attempts"],
        "representation_verdict": packet["representation_verdict"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
