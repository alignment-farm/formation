"""Explore revision of a staged effect table after a relation change."""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Callable

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


PROTOCOL_VERSION = "staged-table-revision-exploration-v1"
SPEC_PATH = Path(__file__).parents[1] / "docs" / "STAGED_TABLE_REVISION_EXPLORATION.md"
WORLDS = tuple(f"world_{index:02d}" for index in range(1, 5))
PRE_CASES = ("pre_up", "pre_down")
POST_CASES = ("same_up", "same_down", "other_up", "other_down")
PRE_COLD = "pre_cold"
PRE_OLD = "pre_old_table"
PRE_BRANCHES = (PRE_COLD, PRE_OLD)
POST_COLD = "post_cold"
STALE = "stale_old_table"
RAW_COUNTER = "old_table_plus_raw_counterexperience"
REVISED = "exposed_revised_table"
HIDDEN = "hidden_consequence_revised_table"
REMOVED = "exposed_revision_removed"
STATIC_NEW = "supplied_new_table"
UNGATED = "exposed_revised_ungated"
POST_BRANCHES = (
    POST_COLD,
    STALE,
    RAW_COUNTER,
    REVISED,
    HIDDEN,
    REMOVED,
    STATIC_NEW,
    UNGATED,
)
REPEATS = 3
LINEAGE_CALLS = len(WORLDS) * 8
PRE_ACTION_CALLS = len(WORLDS) * len(PRE_CASES) * len(PRE_BRANCHES) * REPEATS
POST_ACTION_CALLS = len(WORLDS) * len(POST_CASES) * len(POST_BRANCHES) * REPEATS
PLANNED_LOGICAL_CALLS = LINEAGE_CALLS + PRE_ACTION_CALLS + POST_ACTION_CALLS
PHYSICAL_CALL_CEILING = 472
MAX_RETRIES = 8

REVISION_SYSTEM = """You revise one retained effect table in a controlled cold-model experiment. You have no memory outside this request.

The prior table was written from an earlier direct observation. The new model-authored observation records a later direct environment result and may supersede the prior table. Use the new observation as the current evidence. Within one controller family, one displayed slot increases position and the other decreases it. Infer the unobserved slot from that complement.
Return exactly one JSON object with these keys in this order:
{"controller_family":"<controller_family>","first_displayed_control_effect":"<increases_position or decreases_position>","second_displayed_control_effect":"<decreases_position or increases_position>"}
Return no markdown, commentary, action strings, or extra keys."""


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


@dataclass(frozen=True)
class World:
    name: str
    profile: LineageProfile
    new_profile: LineageProfile
    acquisition: LineageState
    pre_cases: dict[str, LineageState]
    counter_state: LineageState
    post_cases: dict[str, LineageState]
    post_profiles: dict[str, LineageProfile]


def make_world(name: str, index: int) -> World:
    initial_slot = FIRST_INCREASES if index % 2 else SECOND_INCREASES
    new_slot = SECOND_INCREASES if initial_slot == FIRST_INCREASES else FIRST_INCREASES
    family = opaque(f"{name}:family")
    profile = LineageProfile(family, initial_slot)
    new_profile = LineageProfile(family, new_slot)
    position = 1100 + index * 251
    acquisition = LineageState(
        family,
        opaque(f"{name}:acquisition-device"),
        position,
        position - 1,
        (opaque(f"{name}:acquisition-first"), opaque(f"{name}:acquisition-second")),
    )
    pre_cases = {}
    for case_index, case in enumerate(PRE_CASES, 1):
        case_position = 2500 + index * 397 + case_index * 79
        pre_cases[case] = LineageState(
            family,
            opaque(f"{name}:{case}:device"),
            case_position,
            case_position + (1 if case.endswith("up") else -1),
            (opaque(f"{name}:{case}:first"), opaque(f"{name}:{case}:second")),
        )
    counter_position = 3900 + index * 283
    counter_state = LineageState(
        family,
        opaque(f"{name}:counter-device"),
        counter_position,
        counter_position - 1,
        (opaque(f"{name}:counter-first"), opaque(f"{name}:counter-second")),
    )
    post_cases = {}
    post_profiles = {}
    for case_index, case in enumerate(POST_CASES, 1):
        matching = case.startswith("same")
        case_profile = new_profile if matching else LineageProfile(
            opaque(f"{name}:{case}:family"), initial_slot
        )
        case_position = 4700 + index * 521 + case_index * 83
        post_cases[case] = LineageState(
            case_profile.controller_family,
            opaque(f"{name}:{case}:device"),
            case_position,
            case_position + (1 if case.endswith("up") else -1),
            (opaque(f"{name}:{case}:first"), opaque(f"{name}:{case}:second")),
        )
        post_profiles[case] = case_profile
    return World(
        name, profile, new_profile, acquisition, pre_cases, counter_state,
        post_cases, post_profiles
    )


WORLD_DATA = {name: make_world(name, index) for index, name in enumerate(WORLDS, 1)}


def table_for_profile(profile: LineageProfile) -> str:
    second_increases = profile.increasing_slot == SECOND_INCREASES
    return base.canonical_json_bytes({
        "controller_family": profile.controller_family,
        "first_displayed_control_effect": (
            "decreases_position" if second_increases else "increases_position"
        ),
        "second_displayed_control_effect": (
            "increases_position" if second_increases else "decreases_position"
        ),
    }).decode()


def initial_table(world: World) -> str:
    return table_for_profile(world.profile)


def revised_table(world: World) -> str:
    return table_for_profile(world.new_profile)


def observation_body(
    state: LineageState,
    proposal: ProposalReceipt,
    result: Any,
    expose: bool,
) -> bytes:
    record = {
        "external_result": base.exposed_result(result) if expose else forms.WITHHELD_SENTINEL,
        "occurrence": base.occurrence(state, proposal),
    }
    return base.envelope(
        prior.staged.OBSERVATION_SYSTEM,
        f"OBSERVATION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",
        {**base.AUTHORSHIP_SETTINGS, "max_tokens": 128},
    )


def staged_table_body(state: LineageState, observation: str) -> bytes:
    record = {
        "authored_observation": observation,
        "public_device": base.public_device(state),
        "responsibility": "Author the complete effect table.",
    }
    return base.envelope(
        prior.staged.STAGED_TABLE_SYSTEM,
        f"TABLE REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",
        {**base.AUTHORSHIP_SETTINGS, "max_tokens": 160},
    )


def revision_body(world: World, old_table: str, observation: str) -> bytes:
    record = {
        "authored_observation": observation,
        "prior_effect_table": old_table,
        "public_device": base.public_device(world.counter_state),
        "responsibility": "Return the complete current effect table.",
    }
    return base.envelope(
        REVISION_SYSTEM,
        f"REVISION REQUEST\n{base.canonical_json_bytes(record).decode()}\n/no_think",
        {**base.AUTHORSHIP_SETTINGS, "max_tokens": 160},
    )


def specimen() -> dict[str, Any]:
    return {
        "lineage_calls": LINEAGE_CALLS,
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "observation_system_sha256": base.sha256(prior.staged.OBSERVATION_SYSTEM.encode()),
        "physical_call_ceiling": PHYSICAL_CALL_CEILING,
        "planned_logical_calls": PLANNED_LOGICAL_CALLS,
        "post_action_calls": POST_ACTION_CALLS,
        "post_branches": list(POST_BRANCHES),
        "post_cases": list(POST_CASES),
        "pre_action_calls": PRE_ACTION_CALLS,
        "pre_branches": list(PRE_BRANCHES),
        "pre_cases": list(PRE_CASES),
        "protocol_version": PROTOCOL_VERSION,
        "repeats": REPEATS,
        "revision_system_sha256": base.sha256(REVISION_SYSTEM.encode()),
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "worlds": {
            name: {
                "acquisition": base.public_device(world.acquisition),
                "counter_state": base.public_device(world.counter_state),
                "initial_table_sha256": base.sha256(initial_table(world).encode()),
                "new_table_sha256": base.sha256(revised_table(world).encode()),
                "post_cases": {
                    case: {
                        "device": base.public_device(state),
                        "expected_action": oracle_action(state, world.post_profiles[case]),
                    }
                    for case, state in world.post_cases.items()
                },
                "pre_cases": {
                    case: {
                        "device": base.public_device(state),
                        "expected_action": oracle_action(state, world.profile),
                    }
                    for case, state in world.pre_cases.items()
                },
            }
            for name, world in WORLD_DATA.items()
        },
    }


def rotated_schedule(cases, branches):
    rows = []
    for repeat in range(1, REPEATS + 1):
        for case_index, case in enumerate(cases):
            for branch_index in range(len(branches)):
                branch = branches[(repeat - 1 + branch_index) % len(branches)]
                shift = (repeat + case_index + branch_index) % len(WORLDS)
                order = WORLDS[shift:] + WORLDS[:shift]
                rows.extend((repeat, name, case, branch) for name in order)
    return tuple(rows)


def pre_schedule():
    return rotated_schedule(PRE_CASES, PRE_BRANCHES)


def post_schedule():
    return rotated_schedule(POST_CASES, POST_BRANCHES)


@contextmanager
def configured_recorder():
    original = {
        "PHYSICAL_CALL_CEILING": prior.PHYSICAL_CALL_CEILING,
        "MAX_RETRIES": prior.MAX_RETRIES,
    }
    try:
        prior.PHYSICAL_CALL_CEILING = PHYSICAL_CALL_CEILING
        prior.MAX_RETRIES = MAX_RETRIES
        yield
    finally:
        prior.PHYSICAL_CALL_CEILING = original["PHYSICAL_CALL_CEILING"]
        prior.MAX_RETRIES = original["MAX_RETRIES"]


Transport = Callable[[bytes], tuple[int, bytes]]


def available_content(call_result):
    status, error, content, content_available, usage = call_result
    available = status == 200 and error is None and content_available
    return (content if available else ""), usage


def call_action(recorder, logical_index, state, profile, material):
    body = prior.action_body(state, material)
    status, error, content, content_available, usage = recorder.call(logical_index, body)
    availability, action = base.parse_action(content, state)
    if status != 200 or error is not None:
        availability, action = "unavailable", None
    provider_available = status == 200 and error is None and content_available
    proposal = ProposalReceipt(
        provider_available,
        (action or content) if provider_available else "",
    )
    result = apply_committed_action(state, profile, proposal)
    return body, availability, action, proposal, result, usage


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
            body, availability, action, proposal, result, usage = call_action(
                recorder, logical_index, world.acquisition, world.profile, ""
            )
            calls.append({
                "responsibility": "initial_acquisition",
                "world": name,
                "action": action,
                "availability": availability,
                "external_result": base.exposed_result(result),
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
            })
            logical_index += 1
            body = observation_body(world.acquisition, proposal, result, True)
            observation, usage = available_content(recorder.call(logical_index, body))
            fields = base.exposed_result(result)
            expected = prior.staged.expected_observation(
                world, fields.get("selected_slot", ""), fields.get("movement_direction", "")
            )
            calls.append({
                "responsibility": "initial_observation",
                "world": name,
                "content": observation,
                "exact": observation == expected,
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
            })
            logical_index += 1
            body = staged_table_body(world.acquisition, observation)
            old_table, usage = available_content(recorder.call(logical_index, body))
            calls.append({
                "responsibility": "initial_table",
                "world": name,
                "content": old_table,
                "exact": old_table == initial_table(world),
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
            })
            artifacts[name] = {
                "initial_proposal": proposal,
                "initial_result": result,
                "old_table": old_table,
            }

        pre_actions = []
        for repeat, name, case, branch in pre_schedule():
            logical_index += 1
            world = WORLD_DATA[name]
            state = world.pre_cases[case]
            material = artifacts[name]["old_table"] if branch == PRE_OLD else ""
            body, availability, action, proposal, result, usage = call_action(
                recorder, logical_index, state, world.profile, material
            )
            row = {
                "responsibility": "pre_change_action",
                "world": name,
                "case": case,
                "branch": branch,
                "repeat": repeat,
                "action": action,
                "availability": availability,
                "correct_action": (
                    availability == "available" and action == oracle_action(state, world.profile)
                ),
                "external_result": base.exposed_result(result),
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
            }
            pre_actions.append(row)
            calls.append(row)

        for name in WORLDS:
            world = WORLD_DATA[name]
            artifact = artifacts[name]
            logical_index += 1
            body, availability, action, proposal, result, usage = call_action(
                recorder,
                logical_index,
                world.counter_state,
                world.new_profile,
                artifact["old_table"],
            )
            old_policy_consistent = (
                availability == "available"
                and action == oracle_action(world.counter_state, world.profile)
            )
            calls.append({
                "responsibility": "counterexperience_action",
                "world": name,
                "action": action,
                "availability": availability,
                "old_policy_consistent": old_policy_consistent,
                "new_policy_correct": (
                    availability == "available"
                    and action == oracle_action(world.counter_state, world.new_profile)
                ),
                "external_result": base.exposed_result(result),
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
            })
            observations = {}
            for exposure, expose in (("exposed", True), ("hidden", False)):
                logical_index += 1
                body = observation_body(world.counter_state, proposal, result, expose)
                observation, usage = available_content(recorder.call(logical_index, body))
                fields = base.exposed_result(result)
                expected = prior.staged.expected_observation(
                    world, fields.get("selected_slot", ""), fields.get("movement_direction", "")
                )
                calls.append({
                    "responsibility": "counter_observation",
                    "world": name,
                    "exposure": exposure,
                    "content": observation,
                    "exact": observation == expected,
                    "provider_usage": usage,
                    "request_sha256": base.sha256(body),
                })
                observations[exposure] = observation
            revisions = {}
            for exposure in ("exposed", "hidden"):
                logical_index += 1
                body = revision_body(world, artifact["old_table"], observations[exposure])
                revision, usage = available_content(recorder.call(logical_index, body))
                calls.append({
                    "responsibility": "table_revision",
                    "world": name,
                    "exposure": exposure,
                    "content": revision,
                    "exact": revision == revised_table(world),
                    "provider_usage": usage,
                    "request_sha256": base.sha256(body),
                })
                revisions[exposure] = revision
            artifact.update({
                "counter_proposal": proposal,
                "counter_result": result,
                "exposed_revision": revisions["exposed"],
                "hidden_revision": revisions["hidden"],
            })

        post_actions = []
        for repeat, name, case, branch in post_schedule():
            logical_index += 1
            world = WORLD_DATA[name]
            state = world.post_cases[case]
            profile = world.post_profiles[case]
            matching = case.startswith("same")
            artifact = artifacts[name]
            if branch == POST_COLD:
                material = ""
            elif branch in (STALE, REMOVED):
                material = artifact["old_table"] if matching else ""
            elif branch == RAW_COUNTER:
                material = base.canonical_json_bytes({
                    "counterexperience": base.experience_record(
                        world.counter_state,
                        artifact["counter_proposal"],
                        artifact["counter_result"],
                    ),
                    "prior_effect_table": artifact["old_table"],
                }).decode() if matching else ""
            elif branch == REVISED:
                material = artifact["exposed_revision"] if matching else ""
            elif branch == HIDDEN:
                material = artifact["hidden_revision"] if matching else ""
            elif branch == STATIC_NEW:
                material = revised_table(world) if matching else ""
            elif branch == UNGATED:
                material = artifact["exposed_revision"]
            else:  # pragma: no cover
                raise AssertionError(branch)
            body, availability, action, proposal, result, usage = call_action(
                recorder, logical_index, state, profile, material
            )
            row = {
                "responsibility": "post_change_action",
                "world": name,
                "case": case,
                "branch": branch,
                "repeat": repeat,
                "action": action,
                "availability": availability,
                "correct_action": (
                    availability == "available" and action == oracle_action(state, profile)
                ),
                "external_result": base.exposed_result(result),
                "provider_usage": usage,
                "request_sha256": base.sha256(body),
                "retained_material_sha256": base.sha256(material.encode()),
            }
            post_actions.append(row)
            calls.append(row)

    def distributions(rows, cases, branches):
        return {
            name: {
                branch: {
                    case: {
                        "assigned": len(cell := [
                            row for row in rows
                            if row["world"] == name
                            and row["branch"] == branch
                            and row["case"] == case
                        ]),
                        "correct_actions": sum(row["correct_action"] for row in cell),
                        "invalid_or_unavailable": sum(
                            row["availability"] != "available" for row in cell
                        ),
                        "distinct_outcomes": len(Counter(
                            row["action"] or f"<{row['availability']}>" for row in cell
                        )),
                    }
                    for case in cases
                }
                for branch in branches
            }
            for name in WORLDS
        }

    pre_dist = distributions(pre_actions, PRE_CASES, PRE_BRANCHES)
    post_dist = distributions(post_actions, POST_CASES, POST_BRANCHES)

    def total(dist, branch, cases):
        return sum(
            dist[name][branch][case]["correct_actions"]
            for name in WORLDS for case in cases
        )

    pre_scores = {branch: total(pre_dist, branch, PRE_CASES) for branch in PRE_BRANCHES}
    matching_cases = ("same_up", "same_down")
    unrelated_cases = ("other_up", "other_down")
    post_matching = {
        branch: total(post_dist, branch, matching_cases) for branch in POST_BRANCHES
    }
    post_unrelated = {
        branch: total(post_dist, branch, unrelated_cases) for branch in POST_BRANCHES
    }
    direction_scores = {
        "up": total(post_dist, REVISED, ("same_up",)),
        "down": total(post_dist, REVISED, ("same_down",)),
        "static_up": total(post_dist, STATIC_NEW, ("same_up",)),
        "static_down": total(post_dist, STATIC_NEW, ("same_down",)),
    }
    exact_counts = {
        "initial_observations": sum(
            row["exact"] for row in calls if row["responsibility"] == "initial_observation"
        ),
        "initial_tables": sum(
            row["exact"] for row in calls if row["responsibility"] == "initial_table"
        ),
        "exposed_counter_observations": sum(
            row["exact"] for row in calls
            if row["responsibility"] == "counter_observation" and row["exposure"] == "exposed"
        ),
        "exposed_revisions": sum(
            row["exact"] for row in calls
            if row["responsibility"] == "table_revision" and row["exposure"] == "exposed"
        ),
    }
    old_policy_consistent = sum(
        row["old_policy_consistent"] for row in calls
        if row["responsibility"] == "counterexperience_action"
    )
    every_post_cell_valid = all(
        post_dist[name][branch][case]["invalid_or_unavailable"] <= 1
        for name in WORLDS for branch in POST_BRANCHES for case in POST_CASES
    )
    unrelated_loss = post_unrelated[POST_COLD] - post_unrelated[REVISED]
    gate_errors_prevented = post_unrelated[REVISED] - post_unrelated[UNGATED]
    engaged = (
        all(count == len(WORLDS) for count in exact_counts.values())
        and pre_scores[PRE_OLD] >= 21
        and old_policy_consistent >= 3
        and post_matching[STATIC_NEW] >= 21
    )
    harmful = engaged and unrelated_loss >= 4
    candidate = (
        engaged
        and post_matching[REVISED] >= 21
        and direction_scores["up"] >= 10
        and direction_scores["down"] >= 10
        and all(
            post_matching[REVISED] - post_matching[branch] >= 8
            for branch in (POST_COLD, STALE, REMOVED)
        )
        and all(
            post_matching[REVISED] - post_matching[branch] >= 6
            for branch in (RAW_COUNTER, HIDDEN)
        )
        and post_matching[STATIC_NEW] - post_matching[REVISED] <= 3
        and unrelated_loss <= 2
        and every_post_cell_valid
    )
    verdict_class = (
        "not_engaged" if not engaged
        else "harmful" if harmful
        else "candidate_found" if candidate
        else "null"
    )
    packet = {
        "attempts": recorder.attempts,
        "calls": calls,
        "counter_actions_old_policy_consistent": old_policy_consistent,
        "direction_scores": direction_scores,
        "every_post_branch_case_valid": every_post_cell_valid,
        "exact_authorship_counts": exact_counts,
        "formation_verdict": None,
        "gate_errors_prevented": gate_errors_prevented,
        "logical_calls": len(calls),
        "model": base.MODEL,
        "model_digest": base.MODEL_DIGEST,
        "physical_attempts": recorder.physical,
        "post_change_distributions": post_dist,
        "post_matching_scores": post_matching,
        "post_unrelated_scores": post_unrelated,
        "pre_change_distributions": pre_dist,
        "pre_change_scores": pre_scores,
        "protocol_version": PROTOCOL_VERSION,
        "retries": recorder.retries,
        "revision_verdict": {
            "class": verdict_class,
            "scope": "staged_table_revision_exploration",
        },
        "specimen_sha256": base.sha256(base.canonical_json_bytes(specimen())),
        "unrelated_loss": unrelated_loss,
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
        args.evidence_dir = Path("evidence") / f"staged-table-revision-{run_id}"
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
        "revision_verdict": packet["revision_verdict"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
