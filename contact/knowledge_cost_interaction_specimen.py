"""Conform public diagnostic coverage, terminal hold, and external probe cost."""

from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from contact import distributional_developmental_comparison as base
from micro_environment import knowledge_cost_interaction as domain


PROTOCOL_VERSION = "knowledge-cost-interaction-specimen-v1"
SPEC_PATH = (
    Path(__file__).parents[1] / "docs" / "KNOWLEDGE_COST_INTERACTION_SPECIMEN.md"
)

COVERED = "covered"
UNCOVERED = "uncovered"
DEVICE_CLASSES = (COVERED, UNCOVERED)
PROFILE_0 = "profile_0"
PROFILE_1 = "profile_1"
PROFILE_NAMES = (PROFILE_0, PROFILE_1)

COVERED_ALPHABET = ("steady_pattern", "pulsed_pattern")
UNCOVERED_ALPHABET = ("banded_pattern", "broken_pattern")

RECORDS = (
    {
        "record_id": "record-steady-first",
        "diagnostic_signal": COVERED_ALPHABET[0],
        "observed_task_slot": domain.FIRST_SLOT,
    },
    {
        "record_id": "record-pulsed-second",
        "diagnostic_signal": COVERED_ALPHABET[1],
        "observed_task_slot": domain.SECOND_SLOT,
    },
)

FROZEN_PREDICTIONS = (
    "coverage_not_correctness_drives_first_action",
    "removal_crosses_covered_and_uncovered_alphabets",
    "first_and_second_action_scores_remain_separate",
)

PROPOSED_CONDITIONS = (
    "learned_costly",
    "removal_costly",
    "supplied_costly",
    "reversed_costly",
    "learned_free",
    "removal_free",
)


class KnowledgeCostSpecimenRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


def make_state(device_class: str, cost_mode: str) -> domain.KnowledgeCostState:
    if device_class not in DEVICE_CLASSES:
        raise KnowledgeCostSpecimenRefusal("unknown_device_class")
    if cost_mode not in domain.COST_MODES:
        raise KnowledgeCostSpecimenRefusal("unknown_cost_mode")
    alphabet = COVERED_ALPHABET if device_class == COVERED else UNCOVERED_ALPHABET
    return domain.KnowledgeCostState(
        opaque(f"{device_class}-device"),
        (
            opaque(f"{device_class}-first-task"),
            opaque(f"{device_class}-second-task"),
        ),
        opaque(f"{device_class}-diagnostic"),
        alphabet,
        cost_mode,
    )


STATES = {
    (device_class, cost_mode): make_state(device_class, cost_mode)
    for device_class in DEVICE_CLASSES
    for cost_mode in domain.COST_MODES
}

PROFILES = {
    (device_class, profile_name): domain.KnowledgeCostProfile(
        STATES[(device_class, domain.COSTLY)].device,
        profile_name,
        domain.FIRST_SLOT if profile_name == PROFILE_0 else domain.SECOND_SLOT,
        (
            COVERED_ALPHABET if device_class == COVERED else UNCOVERED_ALPHABET
        )[0 if profile_name == PROFILE_0 else 1],
    )
    for device_class in DEVICE_CLASSES
    for profile_name in PROFILE_NAMES
}


def result_value(result: domain.KnowledgeCostResult) -> dict[str, Any]:
    return asdict(result)


def exact_match_receipt(signal: object) -> dict[str, Any]:
    if type(signal) is not str or not signal:
        raise KnowledgeCostSpecimenRefusal("observed_signal_must_be_text")
    return {
        "observed_signal": signal,
        "applicable_record_ids": [
            record["record_id"]
            for record in RECORDS
            if record["diagnostic_signal"] == signal
        ],
    }


def capture_refusal(call: Callable[[], Any]) -> str | None:
    try:
        call()
    except (domain.KnowledgeCostRefusal, KnowledgeCostSpecimenRefusal, TypeError) as exc:
        return str(exc)
    return None


def refusal_witnesses() -> dict[str, str | None]:
    state = STATES[(COVERED, domain.COSTLY)]
    profile = PROFILES[(COVERED, PROFILE_0)]
    return {
        "exact_state": capture_refusal(
            lambda: domain.apply_action(asdict(state), profile, domain.HOLD)
        ),
        "exact_profile": capture_refusal(
            lambda: domain.apply_action(state, asdict(profile), domain.HOLD)
        ),
        "unknown_action": capture_refusal(
            lambda: domain.apply_action(state, profile, "unknown")
        ),
        "profile_device_mismatch": capture_refusal(
            lambda: domain.apply_action(
                state,
                domain.KnowledgeCostProfile(
                    "other-device", PROFILE_0, domain.FIRST_SLOT, COVERED_ALPHABET[0]
                ),
                domain.HOLD,
            )
        ),
        "profile_signal_outside_alphabet": capture_refusal(
            lambda: domain.apply_action(
                state,
                domain.KnowledgeCostProfile(
                    state.device, PROFILE_0, domain.FIRST_SLOT, UNCOVERED_ALPHABET[0]
                ),
                domain.HOLD,
            )
        ),
        "equal_alphabet_signals": capture_refusal(
            lambda: domain.KnowledgeCostState(
                "device", ("first", "second"), "diagnostic", ("same", "same"), domain.COSTLY
            )
        ),
        "unknown_cost": capture_refusal(
            lambda: domain.KnowledgeCostState(
                "device", ("first", "second"), "diagnostic", ("a", "b"), "unknown"
            )
        ),
        "invalid_first_state": capture_refusal(
            lambda: domain.KnowledgeCostState(
                "device",
                ("first", "second"),
                "diagnostic",
                ("a", "b"),
                domain.COSTLY,
                domain.CONSUMED,
            )
        ),
        "invalid_post_diagnostic_window": capture_refusal(
            lambda: domain.KnowledgeCostState(
                "device",
                ("first", "second"),
                "diagnostic",
                ("a", "b"),
                domain.COSTLY,
                domain.AVAILABLE,
                domain.INTACT,
                domain.POST_DIAGNOSTIC,
                "a",
            )
        ),
        "empty_receipt_signal": capture_refusal(lambda: exact_match_receipt("")),
    }


def build_packet() -> dict[str, Any]:
    initial_rows: dict[str, Any] = {}
    trajectories: dict[str, Any] = {}
    profile_public_hashes: dict[str, set[str]] = {}
    repeat_rows: dict[str, Any] = {}
    case_specs: list[
        tuple[str, str, str, domain.KnowledgeCostState, domain.KnowledgeCostProfile, str]
    ] = []
    before_states = {
        key: asdict(state) for key, state in STATES.items()
    }
    distinct_repeat_objects = True

    for device_class in DEVICE_CLASSES:
        for cost_mode in domain.COST_MODES:
            state = STATES[(device_class, cost_mode)]
            state_hash = base.sha256(base.canonical_json_bytes(asdict(state)))
            identity_key = f"{device_class}:{cost_mode}"
            profile_public_hashes[identity_key] = set()
            for profile_name in PROFILE_NAMES:
                profile = PROFILES[(device_class, profile_name)]
                profile_public_hashes[identity_key].add(state_hash)
                actions = (*state.task_controls, state.diagnostic_control, domain.HOLD)
                for action in actions:
                    key = f"{device_class}:{cost_mode}:{profile_name}:{action}"
                    result = domain.apply_action(state, profile, action)
                    repeated_result = domain.apply_action(state, profile, action)
                    initial_rows[key] = result_value(result)
                    repeat_rows[key] = result_value(repeated_result)
                    distinct_repeat_objects = (
                        distinct_repeat_objects
                        and result is not repeated_result
                        and result.state_after is not repeated_result.state_after
                    )
                    case_specs.append(
                        (device_class, cost_mode, profile_name, state, profile, action)
                    )

                probe = domain.apply_action(state, profile, state.diagnostic_control)
                receipt = exact_match_receipt(probe.diagnostic_signal)
                matching_record = next(
                    (
                        record
                        for record in RECORDS
                        if record["diagnostic_signal"] == probe.diagnostic_signal
                    ),
                    None,
                )
                if matching_record is None:
                    continuation_action = domain.HOLD
                else:
                    continuation_action = state.task_controls[
                        0
                        if matching_record["observed_task_slot"] == domain.FIRST_SLOT
                        else 1
                    ]
                continuation = domain.apply_action(
                    probe.state_after, profile, continuation_action
                )
                repeated_diagnostic = domain.apply_action(
                    probe.state_after, profile, state.diagnostic_control
                )
                after_terminal = domain.apply_action(
                    continuation.state_after, profile, domain.HOLD
                )
                trajectories[
                    f"{device_class}:{cost_mode}:{profile_name}"
                ] = {
                    "continuation": result_value(continuation),
                    "post_terminal_refusal": result_value(after_terminal),
                    "probe": result_value(probe),
                    "receipt": receipt,
                    "repeated_diagnostic_refusal": result_value(repeated_diagnostic),
                }

    task_outcomes_exact = all(
        initial_rows[
            f"{device_class}:{cost_mode}:{profile_name}:{state.task_controls[index]}"
        ]["task_status_after"]
        == expected
        for device_class in DEVICE_CLASSES
        for cost_mode in domain.COST_MODES
        for profile_name in PROFILE_NAMES
        for index, expected in (
            (0, domain.COMPLETED if profile_name == PROFILE_0 else domain.FAILED),
            (1, domain.FAILED if profile_name == PROFILE_0 else domain.COMPLETED),
        )
        for state in (STATES[(device_class, cost_mode)],)
    )
    holds_terminal_exact = all(
        initial_rows[
            f"{device_class}:{cost_mode}:{profile_name}:{domain.HOLD}"
        ]["phase_after"]
        == domain.TERMINAL
        and initial_rows[
            f"{device_class}:{cost_mode}:{profile_name}:{domain.HOLD}"
        ]["service_window_after"]
        == domain.AVAILABLE
        and initial_rows[
            f"{device_class}:{cost_mode}:{profile_name}:{domain.HOLD}"
        ]["abstained"]
        for device_class in DEVICE_CLASSES
        for cost_mode in domain.COST_MODES
        for profile_name in PROFILE_NAMES
    )
    cost_transitions_exact = all(
        row["probe"]["service_window_after"]
        == (domain.CONSUMED if cost_mode == domain.COSTLY else domain.AVAILABLE)
        and row["probe"]["service_window_consumed"]
        == (cost_mode == domain.COSTLY)
        and row["probe"]["information_acquired"]
        and row["probe"]["task_status_after"] == domain.INTACT
        for key, row in trajectories.items()
        for cost_mode in (key.split(":")[1],)
    )
    receipts_exact = all(
        len(row["receipt"]["applicable_record_ids"])
        == (1 if key.split(":")[0] == COVERED else 0)
        for key, row in trajectories.items()
    )
    continuations_exact = all(
        (
            row["continuation"]["task_status_after"] == domain.COMPLETED
            if key.split(":")[0] == COVERED
            else row["continuation"]["task_status_after"] == domain.HELD
        )
        and row["repeated_diagnostic_refusal"]["reason"]
        == "diagnostic_already_used"
        and row["post_terminal_refusal"]["reason"] == "terminal_episode"
        for key, row in trajectories.items()
    )
    public_identity_exact = all(
        len(hashes) == 1 for hashes in profile_public_hashes.values()
    )
    cost_equal_across_devices = all(
        STATES[(COVERED, cost_mode)].diagnostic_cost
        == STATES[(UNCOVERED, cost_mode)].diagnostic_cost
        for cost_mode in domain.COST_MODES
    )
    distinct_outcome_fields = all(
        {
            "task_outcome",
            "information_acquired",
            "service_window_consumed",
            "abstained",
        }.issubset(row)
        for row in initial_rows.values()
    )
    repeat_values_equal = initial_rows == repeat_rows
    reverse_rows = {}
    for device_class, cost_mode, profile_name, state, profile, action in reversed(
        case_specs
    ):
        key = f"{device_class}:{cost_mode}:{profile_name}:{action}"
        reverse_rows[key] = result_value(domain.apply_action(state, profile, action))
    order_independent = initial_rows == reverse_rows
    input_immutable = before_states == {
        key: asdict(state) for key, state in STATES.items()
    }
    refusals = refusal_witnesses()
    conforms = all(
        (
            task_outcomes_exact,
            holds_terminal_exact,
            cost_transitions_exact,
            receipts_exact,
            continuations_exact,
            public_identity_exact,
            cost_equal_across_devices,
            distinct_outcome_fields,
            repeat_values_equal,
            distinct_repeat_objects,
            order_independent,
            input_immutable,
            all(refusals.values()),
        )
    )

    return {
        "device_states": {
            f"{device_class}:{cost_mode}": asdict(state)
            for (device_class, cost_mode), state in STATES.items()
        },
        "formation_verdict": None,
        "frozen_predictions": list(FROZEN_PREDICTIONS),
        "initial_transitions": initial_rows,
        "logical_model_calls": 0,
        "profiles": {
            f"{device_class}:{profile_name}": asdict(profile)
            for (device_class, profile_name), profile in PROFILES.items()
        },
        "proposed_contact_conditions": list(PROPOSED_CONDITIONS),
        "protocol_version": PROTOCOL_VERSION,
        "record_fixtures": list(RECORDS),
        "refusal_witnesses": refusals,
        "scores": {
            "cost_equal_across_devices": int(cost_equal_across_devices),
            "cost_transitions_exact": int(cost_transitions_exact),
            "distinct_outcome_fields": int(distinct_outcome_fields),
            "distinct_repeat_objects": int(distinct_repeat_objects),
            "first_action_holds_terminal": int(holds_terminal_exact),
            "input_immutable": int(input_immutable),
            "order_independent": int(order_independent),
            "post_diagnostic_rules_exact": int(continuations_exact),
            "profile_public_identities": sum(
                len(hashes) == 1 for hashes in profile_public_hashes.values()
            ),
            "receipt_assignments_exact": int(receipts_exact),
            "refusals_exact": sum(bool(value) for value in refusals.values()),
            "repeat_values_equal": int(repeat_values_equal),
            "task_outcomes_exact": int(task_outcomes_exact),
        },
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "specimen_verdict": {
            "class": "conforms" if conforms else "does_not_conform",
            "finding": "knowledge_cost_interaction_world_available" if conforms else None,
            "scope": "knowledge_cost_interaction_specimen",
        },
        "trajectories": trajectories,
    }


def write_evidence(evidence_dir: Path) -> dict[str, Any]:
    evidence_dir.mkdir(parents=True, exist_ok=False)
    packet = build_packet()
    (evidence_dir / "packet.json").write_bytes(base.canonical_json_bytes(packet))
    return packet


def replay_evidence(evidence_dir: Path) -> dict[str, Any]:
    retained = (evidence_dir / "packet.json").read_bytes()
    replayed = build_packet()
    if retained != base.canonical_json_bytes(replayed):
        raise KnowledgeCostSpecimenRefusal("evidence_replay_mismatch")
    return replayed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args(argv)
    evidence_dir = args.evidence_dir or Path("evidence") / (
        "knowledge-cost-interaction-specimen-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    packet = write_evidence(evidence_dir)
    replay_evidence(evidence_dir)
    print(
        json.dumps(
            {
                "evidence_dir": str(evidence_dir),
                "logical_model_calls": 0,
                "specimen_verdict": packet["specimen_verdict"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
