"""Conform the irreversible-task and lower-cost diagnostic environment."""

from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from contact import distributional_developmental_comparison as base
from micro_environment import asymmetric_suspension as domain


PROTOCOL_VERSION = "asymmetric-suspension-domain-specimen-v1"
SPEC_PATH = (
    Path(__file__).parents[1] / "docs" / "ASYMMETRIC_SUSPENSION_DOMAIN.md"
)


class DomainSpecimenRefusal(ValueError):
    pass


def opaque(label: str) -> str:
    return hashlib.sha256(f"{PROTOCOL_VERSION}:{label}".encode()).hexdigest()[:20]


PUBLIC_STATE = domain.SuspensionState(
    opaque("device"),
    (opaque("first-task"), opaque("second-task")),
    opaque("diagnostic"),
)
PROFILES = {
    "profile_0": domain.SuspensionProfile(
        PUBLIC_STATE.device, "profile_0", domain.FIRST_SLOT, domain.STEADY
    ),
    "profile_1": domain.SuspensionProfile(
        PUBLIC_STATE.device, "profile_1", domain.SECOND_SLOT, domain.PULSED
    ),
}
ACTIONS = (*PUBLIC_STATE.task_controls, PUBLIC_STATE.diagnostic_control, domain.HOLD)
DIAGNOSTIC_INTERPRETER = {
    domain.STEADY: domain.FIRST_SLOT,
    domain.PULSED: domain.SECOND_SLOT,
}


def result_value(result: domain.SuspensionResult) -> dict[str, Any]:
    return asdict(result)


def run_cases(order: tuple[tuple[str, str], ...]) -> dict[str, dict[str, Any]]:
    rows = {}
    for profile_name, action in order:
        result = domain.apply_action(PUBLIC_STATE, PROFILES[profile_name], action)
        key = f"{profile_name}:{action}"
        rows[key] = {
            "action": action,
            "profile_role": profile_name,
            "public_state_sha256": base.sha256(
                base.canonical_json_bytes(asdict(PUBLIC_STATE))
            ),
            "result": result_value(result),
        }
    return rows


CANONICAL_ORDER = tuple(
    (profile_name, action)
    for profile_name in PROFILES
    for action in ACTIONS
)


def capture_refusal(call: Callable[[], Any]) -> str | None:
    try:
        call()
    except (domain.AsymmetricSuspensionRefusal, TypeError) as exc:
        return str(exc)
    return None


def refusal_witnesses() -> dict[str, str | None]:
    return {
        "exact_state": capture_refusal(lambda: domain.apply_action(
            {**asdict(PUBLIC_STATE), "expected_result": "completed"},
            PROFILES["profile_0"],
            PUBLIC_STATE.task_controls[0],
        )),
        "exact_profile": capture_refusal(lambda: domain.apply_action(
            PUBLIC_STATE,
            asdict(PROFILES["profile_0"]),
            PUBLIC_STATE.task_controls[0],
        )),
        "non_text_action": capture_refusal(lambda: domain.apply_action(
            PUBLIC_STATE, PROFILES["profile_0"], None
        )),
        "unknown_action": capture_refusal(lambda: domain.apply_action(
            PUBLIC_STATE, PROFILES["profile_0"], "unknown"
        )),
        "profile_device_mismatch": capture_refusal(lambda: domain.apply_action(
            PUBLIC_STATE,
            domain.SuspensionProfile(
                "other-device", "profile_0", domain.FIRST_SLOT, domain.STEADY
            ),
            PUBLIC_STATE.task_controls[0],
        )),
        "equal_task_controls": capture_refusal(lambda: domain.SuspensionState(
            "device", ("same", "same"), "diagnostic"
        )),
        "hold_control_collision": capture_refusal(lambda: domain.SuspensionState(
            "device", (domain.HOLD, "second"), "diagnostic"
        )),
        "unknown_status": capture_refusal(lambda: domain.SuspensionState(
            "device", ("first", "second"), "diagnostic", "unknown"
        )),
    }


def build_packet() -> dict[str, Any]:
    before = asdict(PUBLIC_STATE)
    canonical = run_cases(CANONICAL_ORDER)
    reverse = run_cases(tuple(reversed(CANONICAL_ORDER)))
    repeated = run_cases(CANONICAL_ORDER)
    after = asdict(PUBLIC_STATE)

    task_matrix = {
        profile_name: [
            canonical[f"{profile_name}:{action}"]["result"]["status_after"]
            for action in PUBLIC_STATE.task_controls
        ]
        for profile_name in PROFILES
    }
    diagnostic_results = {
        profile_name: canonical[
            f"{profile_name}:{PUBLIC_STATE.diagnostic_control}"
        ]["result"]
        for profile_name in PROFILES
    }
    hold_results = {
        profile_name: canonical[f"{profile_name}:{domain.HOLD}"]["result"]
        for profile_name in PROFILES
    }

    probe_trajectories = {}
    for profile_name, profile in PROFILES.items():
        probe = domain.apply_action(
            PUBLIC_STATE, profile, PUBLIC_STATE.diagnostic_control
        )
        selected_slot = DIAGNOSTIC_INTERPRETER[probe.diagnostic_signal]
        selected_action = PUBLIC_STATE.task_controls[
            0 if selected_slot == domain.FIRST_SLOT else 1
        ]
        task = domain.apply_action(PUBLIC_STATE, profile, selected_action)
        probe_trajectories[profile_name] = {
            "interpreted_slot": selected_slot,
            "probe": result_value(probe),
            "task": result_value(task),
            "total_step_cost": probe.step_cost + task.step_cost,
        }

    terminal_results = {}
    for terminal_status in (domain.COMPLETED, domain.FAILED):
        terminal_state = domain.SuspensionState(
            PUBLIC_STATE.device,
            PUBLIC_STATE.task_controls,
            PUBLIC_STATE.diagnostic_control,
            terminal_status,
        )
        terminal_results[terminal_status] = result_value(domain.apply_action(
            terminal_state,
            PROFILES["profile_0"],
            PUBLIC_STATE.diagnostic_control,
        ))

    refusals = refusal_witnesses()
    task_exact = (
        task_matrix["profile_0"] == [domain.COMPLETED, domain.FAILED]
        and task_matrix["profile_1"] == [domain.FAILED, domain.COMPLETED]
    )
    diagnostic_exact = (
        diagnostic_results["profile_0"]["diagnostic_signal"] == domain.STEADY
        and diagnostic_results["profile_1"]["diagnostic_signal"] == domain.PULSED
        and all(row["status_after"] == domain.INTACT for row in diagnostic_results.values())
    )
    hold_exact = all(
        row["status_after"] == domain.INTACT
        and row["diagnostic_signal"] is None
        and row["observation"] == domain.HELD
        for row in hold_results.values()
    )
    trajectories_exact = all(
        row["task"]["status_after"] == domain.COMPLETED
        and row["total_step_cost"] == 2
        for row in probe_trajectories.values()
    )
    terminal_exact = all(
        row["disposition"] == domain.REFUSED
        and row["reason"] == "terminal_state"
        and row["status_before"] == status
        and row["status_after"] == status
        for status, row in terminal_results.items()
    )
    repeat_values_equal = canonical == repeated
    distinct_repeat_objects = all(
        canonical[key] is not repeated[key] for key in canonical
    )
    public_hashes = {
        row["public_state_sha256"] for row in canonical.values()
    }
    conforms = all((
        task_exact,
        diagnostic_exact,
        hold_exact,
        trajectories_exact,
        terminal_exact,
        before == after,
        canonical == reverse,
        repeat_values_equal,
        distinct_repeat_objects,
        len(public_hashes) == 1,
        all(refusals.values()),
    ))
    return {
        "actions": list(ACTIONS),
        "canonical_results": canonical,
        "diagnostic_interpreter_for_scoring": DIAGNOSTIC_INTERPRETER,
        "formation_verdict": None,
        "logical_model_calls": 0,
        "probe_trajectories": probe_trajectories,
        "profiles": {
            name: asdict(profile) for name, profile in PROFILES.items()
        },
        "protocol_version": PROTOCOL_VERSION,
        "public_state": asdict(PUBLIC_STATE),
        "refusal_witnesses": refusals,
        "scores": {
            "diagnostic_transitions_exact": int(diagnostic_exact),
            "distinct_repeat_objects": int(distinct_repeat_objects),
            "hold_transitions_exact": int(hold_exact),
            "input_immutable": int(before == after),
            "order_independent": int(canonical == reverse),
            "probe_trajectories_exact": int(trajectories_exact),
            "public_state_identities": len(public_hashes),
            "refusals_exact": sum(bool(value) for value in refusals.values()),
            "repeat_values_equal": int(repeat_values_equal),
            "task_transitions_exact": int(task_exact),
            "terminal_refusals_exact": int(terminal_exact),
        },
        "spec_sha256": base.sha256(SPEC_PATH.read_bytes()),
        "specimen_verdict": {
            "class": "conforms" if conforms else "does_not_conform",
            "finding": "asymmetric_probe_domain_available" if conforms else None,
            "scope": "asymmetric_suspension_domain",
        },
        "task_matrix": task_matrix,
        "terminal_results": terminal_results,
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
        raise DomainSpecimenRefusal("evidence_replay_mismatch")
    return replayed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args(argv)
    evidence_dir = args.evidence_dir or Path("evidence") / (
        "asymmetric-suspension-domain-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    packet = write_evidence(evidence_dir)
    replay_evidence(evidence_dir)
    print(json.dumps({
        "evidence_dir": str(evidence_dir),
        "logical_model_calls": 0,
        "specimen_verdict": packet["specimen_verdict"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
