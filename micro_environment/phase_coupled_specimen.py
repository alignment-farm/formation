"""Deterministic surfaces around the phase-coupled transition specimen."""

import hashlib
import json
from typing import Any

from micro_environment.phase_coupled_control import (
    HOLD,
    PhaseActionResult,
    PhaseControlRefusal,
    PhaseProfile,
    PhaseState,
    apply_phase_commitment,
)


SPECIMEN_SEED = "formation.phase-coupled-control.specimen.v1"
IDENTIFIER_LENGTH = 16


class PhaseSpecimenRefusal(ValueError):
    """A serialization, identifier, action object, or score is out of contract."""


def opaque_identifier(seed: object, namespace: object, counter: object) -> str:
    """Return one deterministic domain-separated lowercase hexadecimal token."""

    if type(seed) is not str or seed == "":
        raise PhaseSpecimenRefusal("seed_must_be_text")
    if type(namespace) is not str or namespace == "":
        raise PhaseSpecimenRefusal("namespace_must_be_text")
    if type(counter) is not int or counter < 0:
        raise PhaseSpecimenRefusal("counter_must_be_nonnegative_integer")
    payload = json.dumps(
        ["phase-coupled-control-v1", seed, namespace, counter],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:IDENTIFIER_LENGTH]


def make_profile(
    family_counter: int, phase_zero_increasing_slot: int, *, seed: str = SPECIMEN_SEED
) -> PhaseProfile:
    family = opaque_identifier(seed, "family", family_counter)
    phase_counter = family_counter * 2
    phases = (
        opaque_identifier(seed, "phase", phase_counter),
        opaque_identifier(seed, "phase", phase_counter + 1),
    )
    return PhaseProfile(family, phases, phase_zero_increasing_slot)


def make_state(
    profile: PhaseProfile,
    device_counter: int,
    phase_index: int,
    position: int,
    target: int,
    *,
    seed: str = SPECIMEN_SEED,
) -> PhaseState:
    if type(profile) is not PhaseProfile:
        raise PhaseSpecimenRefusal("exact_phase_profile_required")
    if type(device_counter) is not int or device_counter < 0:
        raise PhaseSpecimenRefusal("device_counter_must_be_nonnegative_integer")
    if type(phase_index) is not int or phase_index not in (0, 1):
        raise PhaseSpecimenRefusal("phase_index_must_be_zero_or_one")
    device = opaque_identifier(seed, "device", device_counter)
    control_counter = device_counter * 2
    controls = (
        opaque_identifier(seed, "control", control_counter),
        opaque_identifier(seed, "control", control_counter + 1),
    )
    exposed = {profile.controller_family, *profile.phases, device, *controls}
    if len(exposed) != 6:
        raise PhaseSpecimenRefusal("opaque_identifier_collision")
    return PhaseState(
        controller_family=profile.controller_family,
        device=device,
        phase=profile.phases[phase_index],
        position=position,
        target=target,
        controls=controls,
    )


def canonical_json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise PhaseSpecimenRefusal("value_is_not_canonical_json") from exc


def _public_state(state: PhaseState) -> dict[str, Any]:
    return {
        "controller_family": state.controller_family,
        "device": state.device,
        "phase": state.phase,
        "position": state.position,
        "target": state.target,
        "controls": list(state.controls),
    }


def _public_consequence(result: PhaseActionResult) -> dict[str, Any]:
    return {
        "position_after": result.position_after,
        "movement_direction": result.movement_direction,
        "phase_after": result.phase_after,
        "target_reached": result.target_reached,
    }


def acquisition_occurrence(
    state: PhaseState, profile: PhaseProfile, actions: tuple[str, str]
) -> dict[str, Any]:
    try:
        results = apply_phase_commitment(state, profile, actions)
    except PhaseControlRefusal as exc:
        raise PhaseSpecimenRefusal(str(exc)) from exc
    return {
        "steps": [
            {
                "action": result.action,
                "before": _public_state(result.before),
                "consequence": _public_consequence(result),
            }
            for result in results
        ]
    }


def occurrence_bytes(
    state: PhaseState, profile: PhaseProfile, actions: tuple[str, str]
) -> bytes:
    return canonical_json_bytes(acquisition_occurrence(state, profile, actions))


def offer_envelope(material: Any) -> bytes:
    return b"EXPERIENCE-DERIVED MATERIAL\n" + canonical_json_bytes(
        {"material": material}
    )


def permitted_actions(state: object, *, commitment: bool) -> tuple[str, ...]:
    if type(state) is not PhaseState:
        raise PhaseSpecimenRefusal("exact_phase_state_required")
    return state.controls if commitment else (*state.controls, HOLD)


def validate_action_object(
    value: object, state: object, *, commitment: bool
) -> tuple[str, ...]:
    if type(state) is not PhaseState:
        raise PhaseSpecimenRefusal("exact_phase_state_required")
    if type(value) is not dict or set(value) != {"actions"}:
        raise PhaseSpecimenRefusal("exact_action_object_required")
    actions = value["actions"]
    required_length = 2 if commitment else 1
    if type(actions) is not list or len(actions) != required_length:
        raise PhaseSpecimenRefusal("wrong_action_count")
    permitted = permitted_actions(state, commitment=commitment)
    if any(type(action) is not str or action not in permitted for action in actions):
        raise PhaseSpecimenRefusal("unlisted_action")
    return tuple(actions)
