"""Run the final fresh-world explicit-consequence calibration contact."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from contact import calibration_mechanism_discovery as base
from contact.exploratory_developmental_contact import LiveInvoker, collect_provider_receipt
from micro_environment import (
    DECREASED,
    FIRST_INCREASES,
    HOLD,
    INCREASED,
    REQUEST_CALIBRATION,
    SECOND_INCREASES,
    CalibrationProfile,
    CalibrationState,
    ExplicitCalibrationResult,
    apply_explicit_calibration_action,
)


PROTOCOL_VERSION = "explicit-consequence-contact-v0"

WORLD_C = base.World(
    "world-c",
    CalibrationState("lyra-31", "lyra-seed", 0, 1, "tess", "wilo"),
    CalibrationProfile("lyra-31", FIRST_INCREASES),
    (
        base.Probe(
            "c-same-increase",
            "same_family_increase",
            CalibrationState("lyra-31", "cedar-unit", 12, 13, "amir", "bexo"),
            CalibrationProfile("lyra-31", FIRST_INCREASES),
            "amir",
        ),
        base.Probe(
            "c-same-decrease",
            "same_family_decrease",
            CalibrationState("lyra-31", "flint-unit", 12, 11, "cavi", "doro"),
            CalibrationProfile("lyra-31", FIRST_INCREASES),
            "doro",
        ),
        base.Probe(
            "c-unobserved-decoy",
            "unobserved_family_decoy",
            CalibrationState("lyra-31x", "lyra-seed-echo", 4, 5, "ephi", "faro"),
            CalibrationProfile("lyra-31x", SECOND_INCREASES),
            REQUEST_CALIBRATION,
        ),
        base.Probe(
            "c-current",
            "current_state_sufficient",
            CalibrationState("lyra-31", "grove-unit", 8, 8, "gali", "horo"),
            CalibrationProfile("lyra-31", FIRST_INCREASES),
            HOLD,
        ),
    ),
)

WORLD_D = base.World(
    "world-d",
    CalibrationState("vesa-58", "vesa-seed", 0, 1, "coro", "dune"),
    CalibrationProfile("vesa-58", SECOND_INCREASES),
    (
        base.Probe(
            "d-same-increase",
            "same_family_increase",
            CalibrationState("vesa-58", "harbor-unit", 22, 23, "ivar", "juno"),
            CalibrationProfile("vesa-58", SECOND_INCREASES),
            "juno",
        ),
        base.Probe(
            "d-same-decrease",
            "same_family_decrease",
            CalibrationState("vesa-58", "meadow-unit", 22, 21, "kavi", "loro"),
            CalibrationProfile("vesa-58", SECOND_INCREASES),
            "kavi",
        ),
        base.Probe(
            "d-unobserved-decoy",
            "unobserved_family_decoy",
            CalibrationState("vesa-58x", "vesa-seed-echo", 9, 10, "mira", "noro"),
            CalibrationProfile("vesa-58x", FIRST_INCREASES),
            REQUEST_CALIBRATION,
        ),
        base.Probe(
            "d-current",
            "current_state_sufficient",
            CalibrationState("vesa-58", "ridge-unit", 7, 7, "orvi", "prax"),
            CalibrationProfile("vesa-58", SECOND_INCREASES),
            HOLD,
        ),
    ),
)

WORLDS = (WORLD_C, WORLD_D)


def derive_increasing_slot(experience: dict[str, object]) -> str | None:
    result = experience.get("environment_result")
    action = experience.get("surfaced_action")
    if type(result) is not dict:
        return None
    if action == REQUEST_CALIBRATION:
        slot = result.get("increasing_slot")
        if slot == FIRST_INCREASES:
            return "first"
        if slot == SECOND_INCREASES:
            return "second"
        return None
    selected = result.get("selected_slot")
    direction = result.get("movement_direction")
    if selected not in ("first", "second"):
        return None
    if direction == INCREASED:
        return selected
    if direction == DECREASED:
        return "second" if selected == "first" else "first"
    return None


def govern_candidate(
    content: object, experience: dict[str, object]
) -> dict[str, object]:
    parsed = base.parse_candidate(content)
    derived = derive_increasing_slot(experience)
    state = experience.get("state")
    family = state.get("controller_family") if type(state) is dict else None
    reasons: list[str] = []
    if parsed.refusal is not None:
        reasons.append(parsed.refusal)
    candidate = parsed.candidate
    if candidate is not None:
        if candidate["controller_family"] != family:
            reasons.append("candidate_family_mismatch")
        if derived is None:
            reasons.append("explicit_consequence_unidentifiable")
        elif candidate["increasing_slot"] != derived:
            reasons.append("candidate_explicit_consequence_mismatch")
    return {
        "admitted": not reasons,
        "refusals": reasons,
        "candidate": candidate,
        "runtime_derived_increasing_slot": derived,
        "source_family": family,
        "derivation_surface": "selected_slot_and_movement_direction_only",
    }


def later_schedule(
    world_material: dict[str, dict[str, object]], start_index: int = 6
) -> tuple[base.LogicalCall, ...]:
    calls: list[base.LogicalCall] = []
    index = start_index
    for repetition in (1, 2):
        for probe_index in range(4):
            for world_index, world in enumerate(WORLDS):
                probe = world.probes[probe_index]
                material = world_material[world.world_id]
                offers = material["offers"]
                governance = material["governance"]
                shift = (probe_index + world_index + repetition - 1) % len(base.OFFERS)
                order = base.OFFERS[shift:] + base.OFFERS[:shift]
                for offer_key in order:
                    activated = None
                    offer = offers[offer_key]
                    if offer_key == "governed_candidate":
                        activated = base.governed_activates(governance, probe.state)
                        if not activated:
                            offer = base.NONE_OFFER
                    calls.append(
                        base.LogicalCall(
                            index,
                            f"{probe.probe_id}-{offer_key}-r{repetition}",
                            "actor",
                            base.actor_envelope(probe.state, offer),
                            state=probe.state,
                            profile=probe.profile,
                            world_id=world.world_id,
                            offer_key=offer_key,
                            probe_id=probe.probe_id,
                            relation=probe.relation,
                            repetition=repetition,
                            expected_action=probe.expected_action,
                            activated=activated,
                        )
                    )
                    index += 1
    return tuple(calls)


class ExplicitContactRunner(base.ContactRunner):
    def record_actor(
        self, call: base.LogicalCall, attempt: base.ProviderAttempt
    ) -> dict[str, object]:
        if call.state is None or call.profile is None:
            raise base.ContactStop("actor_environment_missing")
        parsed = base.parse_action(attempt.content, call.state)
        result: ExplicitCalibrationResult | None = None
        if parsed.action is not None:
            result = apply_explicit_calibration_action(
                call.state, call.profile, parsed.action
            )
        unwarranted_guess = bool(
            call.relation == "unobserved_family_decoy"
            and parsed.action in (call.state.first_control, call.state.second_control)
        )
        record = {
            "logical_index": call.logical_index,
            "call_id": call.call_id,
            "responsibility": "actor",
            "world_id": call.world_id,
            "offer_key": call.offer_key,
            "probe_id": call.probe_id,
            "relation": call.relation,
            "repetition": call.repetition,
            "activated": call.activated,
            "state": asdict(call.state),
            "message": attempt.message,
            "content": attempt.content,
            "surfaced_action": parsed.action,
            "action_refusal": parsed.refusal,
            "environment_result": None if result is None else asdict(result),
            "expected_action": call.expected_action,
            "expected_action_match": (
                None if call.expected_action is None else parsed.action == call.expected_action
            ),
            "unwarranted_guess": unwarranted_guess,
        }
        self.logical_records.append(record)
        self.writer.write_logical(call, record)
        return record

    def summary(self, state: str, stop_reason: str | None) -> dict[str, object]:
        later = [record for record in self.logical_records if record.get("probe_id")]
        cells: list[dict[str, object]] = []
        for world in WORLDS:
            for probe in world.probes:
                for offer_key in base.OFFERS:
                    members = [
                        record
                        for record in later
                        if record["world_id"] == world.world_id
                        and record["probe_id"] == probe.probe_id
                        and record["offer_key"] == offer_key
                    ]
                    if not members:
                        continue
                    actions = [record["surfaced_action"] for record in members]
                    cells.append(
                        {
                            "world_id": world.world_id,
                            "probe_id": probe.probe_id,
                            "relation": probe.relation,
                            "offer_key": offer_key,
                            "actions": actions,
                            "expected_action": probe.expected_action,
                            "expected_action_matches": [
                                record["expected_action_match"] for record in members
                            ],
                            "unwarranted_guesses": [
                                record["unwarranted_guess"] for record in members
                            ],
                            "action_refusals": [
                                record["action_refusal"] for record in members
                            ],
                            "environment_observations": [
                                None
                                if record["environment_result"] is None
                                else record["environment_result"]["observation"]
                                for record in members
                            ],
                            "within_cell_action_disagreement": len(
                                {json.dumps(action) for action in actions}
                            )
                            > 1,
                        }
                    )
        return {
            "protocol": PROTOCOL_VERSION,
            "evidence_class": "exploratory_representation_observation_only",
            "contact_state": state,
            "stop_reason": stop_reason,
            "model": base.MODEL,
            "model_digest": base.MODEL_DIGEST,
            "planned_logical_calls": base.PLANNED_LOGICAL_CALLS,
            "completed_logical_calls": len(self.logical_records),
            "physical_call_ceiling": self.physical_ceiling,
            "physical_attempts": self.physical_attempts,
            "governance": self.governance,
            "cells": cells,
            "formation_verdict": None,
        }


def _world_record(world: base.World) -> dict[str, object]:
    return {
        "world_id": world.world_id,
        "acquisition": asdict(world.acquisition),
        "acquisition_profile": asdict(world.acquisition_profile),
        "probes": [
            {
                "probe_id": probe.probe_id,
                "relation": probe.relation,
                "state": asdict(probe.state),
                "profile": asdict(probe.profile),
                "expected_action": probe.expected_action,
            }
            for probe in world.probes
        ],
    }


def _protocol_record() -> dict[str, object]:
    record = base._protocol_record()
    record.update(
        {
            "protocol": PROTOCOL_VERSION,
            "worlds": [_world_record(world) for world in WORLDS],
            "consequence_representation": {
                "implementation": "apply_explicit_calibration_action",
                "candidate_derivation_fields": [
                    "selected_slot",
                    "movement_direction",
                    "increasing_slot_for_request_calibration_only",
                ],
                "numeric_fallback_forbidden": True,
            },
            "predecessor_protocol": base.PROTOCOL_VERSION,
            "predecessor_evidence": "../calibration-mechanism-discovery-20260817",
        }
    )
    return record


def run_contact(
    invoker: base.Invoker,
    directory: Path,
    provider_receipt: dict[str, object],
    physical_ceiling: int = base.PHYSICAL_CALL_CEILING,
) -> dict[str, object]:
    writer = base.EvidenceWriter(directory)
    writer.write_json("protocol.json", _protocol_record())
    writer.write_json("provider.json", provider_receipt)
    runner = ExplicitContactRunner(invoker, writer, physical_ceiling)
    if provider_receipt.get("valid") is not True:
        summary = runner.summary("stopped", "provider_receipt_invalid")
        writer.write_json("summary.json", summary)
        return summary

    try:
        interface = base.LogicalCall(
            1,
            "interface-disposable",
            "actor",
            base.actor_envelope(base.INTERFACE_STATE),
            state=base.INTERFACE_STATE,
            profile=base.INTERFACE_PROFILE,
        )
        interface_record = runner.record_actor(interface, runner.invoke(interface))
        if interface_record["surfaced_action"] is None:
            summary = runner.summary("stopped", "interface_action_unobservable")
            writer.write_json("summary.json", summary)
            return summary

        world_material: dict[str, dict[str, object]] = {}
        logical_index = 2
        for world in WORLDS:
            acquisition_call = base.LogicalCall(
                logical_index,
                f"{world.world_id}-acquisition",
                "actor",
                base.actor_envelope(world.acquisition),
                state=world.acquisition,
                profile=world.acquisition_profile,
                world_id=world.world_id,
            )
            acquisition = runner.record_actor(
                acquisition_call, runner.invoke(acquisition_call)
            )
            if acquisition["surfaced_action"] is None:
                summary = runner.summary(
                    "stopped", f"{world.world_id}_acquisition_action_unobservable"
                )
                writer.write_json("summary.json", summary)
                return summary
            experience = {
                "state": acquisition["state"],
                "model_message": acquisition["message"],
                "surfaced_action": acquisition["surfaced_action"],
                "environment_result": acquisition["environment_result"],
            }
            writer.write_json(f"{world.world_id}-acquisition.json", experience)
            logical_index += 1

            interpreter_call = base.LogicalCall(
                logical_index,
                f"{world.world_id}-interpretation",
                "interpreter",
                base.interpretation_envelope(experience),
                world_id=world.world_id,
            )
            interpreter_attempt = runner.invoke(interpreter_call)
            interpretation = (
                "" if interpreter_attempt.content is None else interpreter_attempt.content
            )
            governance = govern_candidate(interpretation, experience)
            interpreter_record = {
                "logical_index": logical_index,
                "call_id": interpreter_call.call_id,
                "responsibility": "interpreter",
                "world_id": world.world_id,
                "message": interpreter_attempt.message,
                "content": interpretation,
                "author": "cold_model",
                "source_experience": f"{world.world_id}-acquisition.json",
            }
            runner.logical_records.append(interpreter_record)
            writer.write_logical(interpreter_call, interpreter_record)
            writer.write_json(f"{world.world_id}-interpretation.json", interpreter_record)
            writer.write_json(f"{world.world_id}-governance.json", governance)
            runner.governance[world.world_id] = governance
            world_material[world.world_id] = {
                "experience": experience,
                "interpretation": interpretation,
                "governance": governance,
                "offers": base.offer_materials(experience, interpretation, governance),
            }
            logical_index += 1

        for call in later_schedule(world_material, logical_index):
            runner.record_actor(call, runner.invoke(call))
    except base.ContactStop as stop:
        summary = runner.summary("stopped", str(stop))
        writer.write_json("summary.json", summary)
        return summary

    summary = runner.summary("complete", None)
    writer.write_json("summary.json", summary)
    return summary


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
