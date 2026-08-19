"""Run the bounded two-world calibration mechanism-discovery contact."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Callable

from contact.exploratory_developmental_contact import (
    ENDPOINT,
    INSPECT_TAG,
    MODEL,
    MODEL_DIGEST,
    InvocationFailure,
    LiveInvoker,
    ProviderAttempt,
    canonical_json_bytes,
    collect_provider_receipt,
    sha256_bytes,
)
from micro_environment.calibration_gap import (
    FIRST_INCREASES,
    HOLD,
    REQUEST_CALIBRATION,
    SECOND_INCREASES,
    CalibrationProfile,
    CalibrationResult,
    CalibrationState,
    apply_calibration_action,
)


PROTOCOL_VERSION = "calibration-mechanism-discovery-v0"
PLANNED_LOGICAL_CALLS = 69
PHYSICAL_CALL_CEILING = 72
NONE_OFFER = "NONE"

ACTOR_SETTINGS: dict[str, object] = {
    "max_tokens": 128,
    "temperature": 0.6,
    "top_p": 0.95,
    "stream": False,
    "response_format": {"type": "json_object"},
}
INTERPRETER_SETTINGS: dict[str, object] = {
    "max_tokens": 256,
    "temperature": 0.6,
    "top_p": 0.95,
    "stream": False,
    "response_format": {"type": "json_object"},
}

PUBLIC_RULE = (
    "Each controller family keeps one calibration across its devices. One "
    "ordered control slot increases position and the other decreases it. "
    "Device-specific control names may change. Different controller families "
    "are independently calibrated. Choose the least-cost warranted action. "
    "If position already equals target, choose `hold`. If this decision has "
    "no experience establishing the current family's calibration, choose "
    "`request_calibration` rather than guess."
)


@dataclass(frozen=True, slots=True)
class Probe:
    probe_id: str
    relation: str
    state: CalibrationState
    profile: CalibrationProfile
    expected_action: str


@dataclass(frozen=True, slots=True)
class World:
    world_id: str
    acquisition: CalibrationState
    acquisition_profile: CalibrationProfile
    probes: tuple[Probe, ...]


WORLD_A = World(
    "world-a",
    CalibrationState("noru-17", "noru-seed", 0, 1, "dax", "lume"),
    CalibrationProfile("noru-17", FIRST_INCREASES),
    (
        Probe(
            "a-same-increase",
            "same_family_increase",
            CalibrationState("noru-17", "opal-unit", 10, 11, "sile", "toru"),
            CalibrationProfile("noru-17", FIRST_INCREASES),
            "sile",
        ),
        Probe(
            "a-same-decrease",
            "same_family_decrease",
            CalibrationState("noru-17", "quill-unit", 10, 9, "nemi", "vask"),
            CalibrationProfile("noru-17", FIRST_INCREASES),
            "vask",
        ),
        Probe(
            "a-unobserved-decoy",
            "unobserved_family_decoy",
            CalibrationState("noru-17b", "noru-seed-echo", 3, 4, "kiri", "pavo"),
            CalibrationProfile("noru-17b", SECOND_INCREASES),
            REQUEST_CALIBRATION,
        ),
        Probe(
            "a-current",
            "current_state_sufficient",
            CalibrationState("noru-17", "ember-unit", 5, 5, "zori", "meka"),
            CalibrationProfile("noru-17", FIRST_INCREASES),
            HOLD,
        ),
    ),
)

WORLD_B = World(
    "world-b",
    CalibrationState("tavi-42", "tavi-seed", 0, 1, "brin", "sova"),
    CalibrationProfile("tavi-42", SECOND_INCREASES),
    (
        Probe(
            "b-same-increase",
            "same_family_increase",
            CalibrationState("tavi-42", "river-unit", 20, 21, "fenu", "gora"),
            CalibrationProfile("tavi-42", SECOND_INCREASES),
            "gora",
        ),
        Probe(
            "b-same-decrease",
            "same_family_decrease",
            CalibrationState("tavi-42", "stone-unit", 20, 19, "havi", "jora"),
            CalibrationProfile("tavi-42", SECOND_INCREASES),
            "havi",
        ),
        Probe(
            "b-unobserved-decoy",
            "unobserved_family_decoy",
            CalibrationState("tavi-42b", "tavi-seed-echo", 7, 8, "kelo", "mavi"),
            CalibrationProfile("tavi-42b", FIRST_INCREASES),
            REQUEST_CALIBRATION,
        ),
        Probe(
            "b-current",
            "current_state_sufficient",
            CalibrationState("tavi-42", "willow-unit", 6, 6, "peli", "ranu"),
            CalibrationProfile("tavi-42", SECOND_INCREASES),
            HOLD,
        ),
    ),
)

WORLDS = (WORLD_A, WORLD_B)
OFFERS = (
    "no_persistence",
    "raw_occurrence",
    "authored_interpretation",
    "governed_candidate",
)

INTERFACE_STATE = CalibrationState(
    "interface-family", "interface-device", 4, 4, "loki", "senu"
)
INTERFACE_PROFILE = CalibrationProfile("interface-family", FIRST_INCREASES)


class DuplicateKey(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKey(key)
        value[key] = item
    return value


@dataclass(frozen=True, slots=True)
class ActionParse:
    action: str | None
    refusal: str | None


def permitted_actions(state: CalibrationState) -> tuple[str, ...]:
    return (state.first_control, state.second_control, REQUEST_CALIBRATION, HOLD)


def parse_action(content: object, state: CalibrationState) -> ActionParse:
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
    if action not in permitted_actions(state):
        return ActionParse(None, "action_not_permitted")
    return ActionParse(action, None)


@dataclass(frozen=True, slots=True)
class CandidateParse:
    candidate: dict[str, str] | None
    refusal: str | None


def parse_candidate(content: object) -> CandidateParse:
    if type(content) is not str:
        return CandidateParse(None, "content_not_string")
    try:
        decoded = json.loads(
            content,
            object_pairs_hook=_unique_object,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
    except (json.JSONDecodeError, DuplicateKey, ValueError):
        return CandidateParse(None, "invalid_json")
    required = {"controller_family", "increasing_slot", "scope", "counterevidence"}
    if type(decoded) is not dict or set(decoded) != required:
        return CandidateParse(None, "invalid_candidate_object")
    if any(type(decoded[key]) is not str for key in required):
        return CandidateParse(None, "candidate_fields_not_strings")
    if decoded["increasing_slot"] not in ("first", "second"):
        return CandidateParse(None, "unknown_increasing_slot")
    if decoded["scope"] != "same_controller_family":
        return CandidateParse(None, "unknown_scope")
    if decoded["controller_family"] == "" or decoded["counterevidence"].strip() == "":
        return CandidateParse(None, "empty_candidate_field")
    return CandidateParse(decoded, None)


ACTOR_SYSTEM = f"""You are the action-selection component of a cold practitioner.
Public operating rule:
{PUBLIC_RULE}

Return exactly one JSON object with the single string field `action`.
The value must be one of the four permitted actions listed in the current request.
Return no prose and no Markdown fence."""


def actor_user_prompt(state: CalibrationState, offer: str) -> str:
    actions = permitted_actions(state)
    return "\n".join(
        (
            "Current device:",
            f"controller_family: {state.controller_family}",
            f"device_id: {state.device_id}",
            f"position: {state.position}",
            f"target: {state.target}",
            f"first_control: {state.first_control}",
            f"second_control: {state.second_control}",
            "",
            "Permitted actions:",
            *(f"- {action}" for action in actions),
            "",
            "Runtime developmental offer:",
            "---BEGIN OFFER---",
            offer,
            "---END OFFER---",
            "",
            "/no_think",
        )
    )


def actor_envelope(state: CalibrationState, offer: str = NONE_OFFER) -> dict[str, object]:
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": ACTOR_SYSTEM},
            {"role": "user", "content": actor_user_prompt(state, offer)},
        ],
        **ACTOR_SETTINGS,
    }


INTERPRETER_SYSTEM = f"""You are the candidate author inside a formation runtime.
Public operating rule:
{PUBLIC_RULE}

Use only the supplied acquisition occurrence. Return exactly one JSON object with:
- controller_family: the public family supported by the occurrence
- increasing_slot: `first` or `second`
- scope: exactly `same_controller_family`
- counterevidence: a nonempty string naming an observation that would count against the claim
Do not add fields, prose, or a Markdown fence."""


def interpretation_envelope(experience: dict[str, object]) -> dict[str, object]:
    prompt = (
        "Exact acquisition occurrence:\n"
        + json.dumps(experience, indent=2, sort_keys=True, ensure_ascii=False)
        + "\n\n/no_think"
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
    state: CalibrationState | None = None
    profile: CalibrationProfile | None = None
    world_id: str | None = None
    offer_key: str | None = None
    probe_id: str | None = None
    relation: str | None = None
    repetition: int | None = None
    expected_action: str | None = None
    activated: bool | None = None

    @property
    def request_body(self) -> bytes:
        return canonical_json_bytes(self.envelope)


def derive_increasing_slot(experience: dict[str, object]) -> str | None:
    action = experience.get("surfaced_action")
    state = experience.get("state")
    result = experience.get("environment_result")
    if type(state) is not dict or type(result) is not dict:
        return None
    if action == REQUEST_CALIBRATION:
        slot = result.get("increasing_slot")
        if slot == FIRST_INCREASES:
            return "first"
        if slot == SECOND_INCREASES:
            return "second"
        return None
    first_control = state.get("first_control")
    second_control = state.get("second_control")
    if action not in (first_control, second_control):
        return None
    before = result.get("position_before")
    after = result.get("position_after")
    if type(before) is not int or type(after) is not int or abs(after - before) != 1:
        return None
    selected = "first" if action == first_control else "second"
    if after > before:
        return selected
    return "second" if selected == "first" else "first"


def govern_candidate(
    content: object, experience: dict[str, object]
) -> dict[str, object]:
    parsed = parse_candidate(content)
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
            reasons.append("acquisition_mapping_unidentifiable")
        elif candidate["increasing_slot"] != derived:
            reasons.append("candidate_transition_mismatch")
    return {
        "admitted": not reasons,
        "refusals": reasons,
        "candidate": candidate,
        "runtime_derived_increasing_slot": derived,
        "source_family": family,
    }


def offer_materials(
    experience: dict[str, object], interpretation: str, governance: dict[str, object]
) -> dict[str, str]:
    return {
        "no_persistence": NONE_OFFER,
        "raw_occurrence": json.dumps(
            experience, indent=2, sort_keys=True, ensure_ascii=False
        ),
        "authored_interpretation": interpretation,
        "governed_candidate": interpretation,
    }


def governed_activates(
    governance: dict[str, object], state: CalibrationState
) -> bool:
    candidate = governance.get("candidate")
    return bool(
        governance.get("admitted") is True
        and type(candidate) is dict
        and candidate.get("controller_family") == state.controller_family
        and state.position != state.target
    )


def later_schedule(
    world_material: dict[str, dict[str, object]], start_index: int = 6
) -> tuple[LogicalCall, ...]:
    calls: list[LogicalCall] = []
    index = start_index
    for repetition in (1, 2):
        for probe_index in range(4):
            for world_index, world in enumerate(WORLDS):
                probe = world.probes[probe_index]
                material = world_material[world.world_id]
                offers = material["offers"]
                governance = material["governance"]
                shift = (probe_index + world_index + repetition - 1) % len(OFFERS)
                order = OFFERS[shift:] + OFFERS[:shift]
                for offer_key in order:
                    activated = None
                    offer = offers[offer_key]
                    if offer_key == "governed_candidate":
                        activated = governed_activates(governance, probe.state)
                        if not activated:
                            offer = NONE_OFFER
                    calls.append(
                        LogicalCall(
                            index,
                            f"{probe.probe_id}-{offer_key}-r{repetition}",
                            "actor",
                            actor_envelope(probe.state, offer),
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


Invoker = Callable[[LogicalCall, int], ProviderAttempt]


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
                "world_id": call.world_id,
                "offer_key": call.offer_key,
                "probe_id": call.probe_id,
                "relation": call.relation,
                "repetition": call.repetition,
                "activated": call.activated,
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
        physical_ceiling: int = PHYSICAL_CALL_CEILING,
    ) -> None:
        self.invoker = invoker
        self.writer = writer
        self.physical_ceiling = physical_ceiling
        self.physical_attempts = 0
        self.logical_records: list[dict[str, object]] = []
        self.governance: dict[str, dict[str, object]] = {}

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
                        **{**asdict(attempt), "retry_of_attempt": 1}
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
                    **{**asdict(attempt), "retry_of_attempt": 1}
                )
            self.writer.write_attempt(call, attempt)
            return attempt
        raise AssertionError("unreachable")

    def record_actor(
        self, call: LogicalCall, attempt: ProviderAttempt
    ) -> dict[str, object]:
        if call.state is None or call.profile is None:
            raise ContactStop("actor_environment_missing")
        parsed = parse_action(attempt.content, call.state)
        result: CalibrationResult | None = None
        if parsed.action is not None:
            result = apply_calibration_action(call.state, call.profile, parsed.action)
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
                for offer_key in OFFERS:
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
            "evidence_class": "exploratory_mechanism_observation_only",
            "contact_state": state,
            "stop_reason": stop_reason,
            "model": MODEL,
            "model_digest": MODEL_DIGEST,
            "planned_logical_calls": PLANNED_LOGICAL_CALLS,
            "completed_logical_calls": len(self.logical_records),
            "physical_call_ceiling": self.physical_ceiling,
            "physical_attempts": self.physical_attempts,
            "governance": self.governance,
            "cells": cells,
            "formation_verdict": None,
        }


def _world_record(world: World) -> dict[str, object]:
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
    return {
        "protocol": PROTOCOL_VERSION,
        "model": MODEL,
        "inspect_tag": INSPECT_TAG,
        "model_digest": MODEL_DIGEST,
        "endpoint": ENDPOINT,
        "public_rule": PUBLIC_RULE,
        "actor_settings": ACTOR_SETTINGS,
        "interpreter_settings": INTERPRETER_SETTINGS,
        "none_offer": NONE_OFFER,
        "offers": list(OFFERS),
        "interface_state": asdict(INTERFACE_STATE),
        "worlds": [_world_record(world) for world in WORLDS],
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
    runner = ContactRunner(invoker, writer, physical_ceiling)
    if provider_receipt.get("valid") is not True:
        summary = runner.summary("stopped", "provider_receipt_invalid")
        writer.write_json("summary.json", summary)
        return summary

    try:
        interface = LogicalCall(
            1,
            "interface-disposable",
            "actor",
            actor_envelope(INTERFACE_STATE),
            state=INTERFACE_STATE,
            profile=INTERFACE_PROFILE,
        )
        interface_record = runner.record_actor(interface, runner.invoke(interface))
        if interface_record["surfaced_action"] is None:
            summary = runner.summary("stopped", "interface_action_unobservable")
            writer.write_json("summary.json", summary)
            return summary

        world_material: dict[str, dict[str, object]] = {}
        logical_index = 2
        for world in WORLDS:
            acquisition_call = LogicalCall(
                logical_index,
                f"{world.world_id}-acquisition",
                "actor",
                actor_envelope(world.acquisition),
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

            interpreter_call = LogicalCall(
                logical_index,
                f"{world.world_id}-interpretation",
                "interpreter",
                interpretation_envelope(experience),
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
            runner.writer.write_logical(interpreter_call, interpreter_record)
            writer.write_json(f"{world.world_id}-interpretation.json", interpreter_record)
            writer.write_json(f"{world.world_id}-governance.json", governance)
            runner.governance[world.world_id] = governance
            world_material[world.world_id] = {
                "experience": experience,
                "interpretation": interpretation,
                "governance": governance,
                "offers": offer_materials(experience, interpretation, governance),
            }
            logical_index += 1

        for call in later_schedule(world_material, start_index=logical_index):
            runner.record_actor(call, runner.invoke(call))
    except ContactStop as stop:
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
