import json
from pathlib import Path
import tempfile
import unittest

from contact import calibration_mechanism_discovery as base
from contact.explicit_consequence_contact import (
    PROTOCOL_VERSION,
    WORLD_C,
    WORLD_D,
    WORLDS,
    derive_increasing_slot,
    govern_candidate,
    later_schedule,
    run_contact,
)
from contact.exploratory_developmental_contact import (
    ENDPOINT,
    INSPECT_TAG,
    MODEL,
    MODEL_DIGEST,
    ProviderAttempt,
    canonical_json_bytes,
)
from micro_environment import HOLD


def valid_receipt():
    return {
        "valid": True,
        "refusals": [],
        "endpoint": ENDPOINT,
        "parsed_inspection": {"id": MODEL_DIGEST, "tags": [INSPECT_TAG]},
    }


def candidate_for(world):
    return json.dumps(
        {
            "controller_family": world.acquisition.controller_family,
            "increasing_slot": "first" if world is WORLD_C else "second",
            "scope": "same_controller_family",
            "counterevidence": "A same-family selected slot moves oppositely.",
        },
        separators=(",", ":"),
    )


def explicit_experience(world):
    state = world.acquisition
    first_increases = world is WORLD_C
    return {
        "state": {
            "controller_family": state.controller_family,
            "device_id": state.device_id,
            "position": state.position,
            "target": state.target,
            "first_control": state.first_control,
            "second_control": state.second_control,
        },
        "model_message": {
            "role": "assistant",
            "content": json.dumps({"action": state.first_control}),
        },
        "surfaced_action": state.first_control,
        "environment_result": {
            "action": state.first_control,
            "controller_family": state.controller_family,
            "device_id": state.device_id,
            "position_before": 999,
            "position_after": -999,
            "target": state.target,
            "observation": "target_reached" if first_increases else "target_not_reached",
            "selected_slot": "first",
            "movement_direction": "increased" if first_increases else "decreased",
            "increasing_slot": None,
        },
    }


def material():
    result = {}
    for world in WORLDS:
        experience = explicit_experience(world)
        interpretation = candidate_for(world)
        governance = govern_candidate(interpretation, experience)
        result[world.world_id] = {
            "experience": experience,
            "interpretation": interpretation,
            "governance": governance,
            "offers": base.offer_materials(experience, interpretation, governance),
        }
    return result


class FakeInvoker:
    def __init__(self, overrides=None):
        self.overrides = {} if overrides is None else overrides
        self.calls = []

    def __call__(self, call, attempt_index):
        self.calls.append((call, attempt_index))
        if call.call_id in self.overrides:
            content = self.overrides[call.call_id]
        elif call.responsibility == "interpreter":
            world = next(w for w in WORLDS if w.world_id == call.world_id)
            content = candidate_for(world)
        elif call.call_id == "interface-disposable":
            content = json.dumps({"action": HOLD})
        elif call.call_id.endswith("-acquisition"):
            world = next(w for w in WORLDS if w.world_id == call.world_id)
            content = json.dumps({"action": world.acquisition.first_control})
        else:
            content = json.dumps({"action": call.expected_action})
        message = {"role": "assistant", "content": content, "reasoning_content": "kept"}
        envelope = {
            "model": MODEL,
            "choices": [{"message": message, "finish_reason": "stop"}],
        }
        return ProviderAttempt(
            call.logical_index,
            attempt_index,
            call.call_id,
            call.request_body,
            canonical_json_bytes(envelope),
            envelope,
            message,
            content,
            200,
            "start",
            "end",
            1.0,
        )


class ExplicitConsequenceContactTests(unittest.TestCase):
    def test_candidate_derivation_uses_explicit_facts_not_numeric_fallback(self):
        c = explicit_experience(WORLD_C)
        d = explicit_experience(WORLD_D)
        self.assertEqual(derive_increasing_slot(c), "first")
        self.assertEqual(derive_increasing_slot(d), "second")
        d["environment_result"]["position_before"] = -100000
        d["environment_result"]["position_after"] = 100000
        self.assertEqual(derive_increasing_slot(d), "second")

    def test_governor_admits_matching_explicit_candidate_and_refuses_prior(self):
        experience = explicit_experience(WORLD_D)
        admitted = govern_candidate(candidate_for(WORLD_D), experience)
        self.assertTrue(admitted["admitted"])
        self.assertEqual(
            admitted["derivation_surface"],
            "selected_slot_and_movement_direction_only",
        )
        wrong = json.loads(candidate_for(WORLD_D))
        wrong["increasing_slot"] = "first"
        refused = govern_candidate(json.dumps(wrong), experience)
        self.assertIn(
            "candidate_explicit_consequence_mismatch", refused["refusals"]
        )

    def test_fresh_worlds_are_mirrored_and_tokens_do_not_recur(self):
        self.assertNotEqual(
            WORLD_C.acquisition_profile.increasing_slot,
            WORLD_D.acquisition_profile.increasing_slot,
        )
        for world in WORLDS:
            acquisition = {
                world.acquisition.first_control,
                world.acquisition.second_control,
            }
            later = {
                token
                for probe in world.probes
                for token in (probe.state.first_control, probe.state.second_control)
            }
            self.assertTrue(acquisition.isdisjoint(later))
            self.assertEqual(len(later), 8)

    def test_schedule_has_64_balanced_calls_and_governed_deactivation_identity(self):
        calls = later_schedule(material())
        self.assertEqual(len(calls), 64)
        self.assertEqual([call.logical_index for call in calls], list(range(6, 70)))
        for world in WORLDS:
            for probe in world.probes[2:]:
                members = [
                    call
                    for call in calls
                    if call.world_id == world.world_id
                    and call.probe_id == probe.probe_id
                    and call.repetition == 1
                ]
                no_offer = next(c for c in members if c.offer_key == "no_persistence")
                governed = next(c for c in members if c.offer_key == "governed_candidate")
                self.assertFalse(governed.activated)
                self.assertEqual(governed.request_body, no_offer.request_body)

    def test_requests_exclude_new_harness_labels(self):
        forbidden = [
            "world-c",
            "world-d",
            *base.OFFERS,
            "same_family_increase",
            "unobserved_family_decoy",
            "expected_action",
        ]
        for call in later_schedule(material()):
            text = call.request_body.decode()
            for value in forbidden:
                self.assertNotIn(value, text)

    def test_full_fake_contact_completes_with_explicit_evidence_and_null_verdict(self):
        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "evidence"
            summary = run_contact(FakeInvoker(), directory, valid_receipt())
            acquisition = json.loads((directory / "world-d-acquisition.json").read_text())
            protocol = json.loads((directory / "protocol.json").read_text())
        self.assertEqual(summary["contact_state"], "complete")
        self.assertEqual(summary["completed_logical_calls"], 69)
        self.assertEqual(summary["protocol"], PROTOCOL_VERSION)
        self.assertEqual(
            acquisition["environment_result"]["movement_direction"], "decreased"
        )
        self.assertTrue(protocol["consequence_representation"]["numeric_fallback_forbidden"])
        self.assertIsNone(summary["formation_verdict"])

    def test_wrong_later_behavior_remains_observed_without_retry(self):
        override = {"d-same-increase-raw_occurrence-r1": '{"action":"ivar"}'}
        with tempfile.TemporaryDirectory() as parent:
            summary = run_contact(
                FakeInvoker(override), Path(parent) / "evidence", valid_receipt()
            )
        self.assertEqual(summary["contact_state"], "complete")
        self.assertEqual(summary["physical_attempts"], 69)

    def test_unobservable_interface_stops_without_representation_repair(self):
        with tempfile.TemporaryDirectory() as parent:
            summary = run_contact(
                FakeInvoker({"interface-disposable": "not json"}),
                Path(parent) / "evidence",
                valid_receipt(),
            )
        self.assertEqual(summary["stop_reason"], "interface_action_unobservable")
        self.assertEqual(summary["physical_attempts"], 1)


if __name__ == "__main__":
    unittest.main()
