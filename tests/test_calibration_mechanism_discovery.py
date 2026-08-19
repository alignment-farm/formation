import json
from pathlib import Path
import tempfile
import unittest

from contact.calibration_mechanism_discovery import (
    ACTOR_SETTINGS,
    NONE_OFFER,
    OFFERS,
    PHYSICAL_CALL_CEILING,
    PLANNED_LOGICAL_CALLS,
    WORLD_A,
    WORLD_B,
    WORLDS,
    ActionParse,
    LogicalCall,
    actor_envelope,
    derive_increasing_slot,
    govern_candidate,
    later_schedule,
    offer_materials,
    parse_action,
    parse_candidate,
    run_contact,
)
from contact.exploratory_developmental_contact import (
    ENDPOINT,
    INSPECT_TAG,
    MODEL,
    MODEL_DIGEST,
    InvocationFailure,
    ProviderAttempt,
    canonical_json_bytes,
)
from micro_environment import HOLD, REQUEST_CALIBRATION


def valid_receipt():
    return {
        "valid": True,
        "refusals": [],
        "endpoint": ENDPOINT,
        "parsed_inspection": {"id": MODEL_DIGEST, "tags": [INSPECT_TAG]},
    }


def request_experience(world):
    state = world.acquisition
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
            "content": json.dumps({"action": REQUEST_CALIBRATION}),
        },
        "surfaced_action": REQUEST_CALIBRATION,
        "environment_result": {
            "action": REQUEST_CALIBRATION,
            "controller_family": state.controller_family,
            "device_id": state.device_id,
            "position_before": state.position,
            "position_after": state.position,
            "target": state.target,
            "observation": "calibration_revealed",
            "increasing_slot": world.acquisition_profile.increasing_slot,
        },
    }


def candidate_content(world):
    slot = "first" if world is WORLD_A else "second"
    return json.dumps(
        {
            "controller_family": world.acquisition.controller_family,
            "increasing_slot": slot,
            "scope": "same_controller_family",
            "counterevidence": "A same-family control moves in the opposite direction.",
        },
        separators=(",", ":"),
    )


def world_material():
    material = {}
    for world in WORLDS:
        experience = request_experience(world)
        interpretation = candidate_content(world)
        governance = govern_candidate(interpretation, experience)
        material[world.world_id] = {
            "experience": experience,
            "interpretation": interpretation,
            "governance": governance,
            "offers": offer_materials(experience, interpretation, governance),
        }
    return material


class FakeInvoker:
    def __init__(self, overrides=None):
        self.overrides = {} if overrides is None else overrides
        self.calls = []

    def content_for(self, call):
        if call.call_id in self.overrides:
            return self.overrides[call.call_id]
        if call.responsibility == "interpreter":
            world = next(item for item in WORLDS if item.world_id == call.world_id)
            return candidate_content(world)
        if call.call_id == "interface-disposable":
            action = HOLD
        elif call.call_id.endswith("-acquisition"):
            action = REQUEST_CALIBRATION
        else:
            action = call.expected_action
        return json.dumps({"action": action}, separators=(",", ":"))

    def __call__(self, call, attempt_index):
        self.calls.append((call, attempt_index))
        content = self.content_for(call)
        message = {
            "role": "assistant",
            "content": content,
            "reasoning_content": "unscored",
        }
        envelope = {
            "model": MODEL,
            "choices": [{"index": 0, "message": message, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
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
            "2026-08-17T00:00:00+00:00",
            "2026-08-17T00:00:01+00:00",
            1.0,
        )


class CalibrationMechanismDiscoveryTests(unittest.TestCase):
    def test_action_parser_is_dynamic_strict_and_content_only(self):
        state = WORLD_A.acquisition
        self.assertEqual(
            parse_action('{"action":"dax"}', state), ActionParse("dax", None)
        )
        refusals = {
            "": "empty_content",
            "not json": "invalid_json",
            '{"action":"dax","action":"dax"}': "invalid_json",
            '{"action":"dax","extra":1}': "invalid_action_object",
            '{"action":1}': "action_not_string",
            '{"action":"brin"}': "action_not_permitted",
        }
        for content, refusal in refusals.items():
            with self.subTest(content=content):
                self.assertEqual(parse_action(content, state).refusal, refusal)

    def test_candidate_parser_and_governor_use_observed_transition_only(self):
        experience = request_experience(WORLD_A)
        content = candidate_content(WORLD_A)
        self.assertIsNotNone(parse_candidate(content).candidate)
        receipt = govern_candidate(content, experience)
        self.assertTrue(receipt["admitted"])
        self.assertEqual(receipt["runtime_derived_increasing_slot"], "first")
        wrong = json.loads(content)
        wrong["increasing_slot"] = "second"
        refused = govern_candidate(json.dumps(wrong), experience)
        self.assertFalse(refused["admitted"])
        self.assertIn("candidate_transition_mismatch", refused["refusals"])

    def test_control_consequences_and_hold_have_exact_identifiability(self):
        first = request_experience(WORLD_A)
        first["surfaced_action"] = "dax"
        first["environment_result"]["action"] = "dax"
        first["environment_result"]["position_after"] = 1
        first["environment_result"]["increasing_slot"] = None
        self.assertEqual(derive_increasing_slot(first), "first")
        first["environment_result"]["position_after"] = -1
        self.assertEqual(derive_increasing_slot(first), "second")
        first["surfaced_action"] = HOLD
        self.assertIsNone(derive_increasing_slot(first))

    def test_two_worlds_are_mirrored_and_later_tokens_cannot_be_copied(self):
        self.assertNotEqual(
            WORLD_A.acquisition_profile.increasing_slot,
            WORLD_B.acquisition_profile.increasing_slot,
        )
        for world in WORLDS:
            acquisition_tokens = {
                world.acquisition.first_control,
                world.acquisition.second_control,
            }
            later_tokens = {
                token
                for probe in world.probes
                for token in (probe.state.first_control, probe.state.second_control)
            }
            self.assertTrue(acquisition_tokens.isdisjoint(later_tokens))
            self.assertEqual(len(later_tokens), 8)

    def test_schedule_is_exact_balanced_rotating_and_interface_identical(self):
        calls = later_schedule(world_material())
        self.assertEqual(len(calls), 64)
        self.assertEqual([call.logical_index for call in calls], list(range(6, 70)))
        self.assertEqual(
            {(call.world_id, call.probe_id, call.offer_key, call.repetition) for call in calls},
            {
                (world.world_id, probe.probe_id, offer, repetition)
                for world in WORLDS
                for probe in world.probes
                for offer in OFFERS
                for repetition in (1, 2)
            },
        )
        self.assertNotEqual(
            [call.offer_key for call in calls[:4]],
            [call.offer_key for call in calls[4:8]],
        )
        for call in calls:
            for key, value in ACTOR_SETTINGS.items():
                self.assertEqual(call.envelope[key], value)

    def test_governed_gate_matches_no_offer_on_other_family_and_current_state(self):
        calls = later_schedule(world_material())
        for world in WORLDS:
            for probe in world.probes[2:]:
                members = [
                    call
                    for call in calls
                    if call.world_id == world.world_id
                    and call.probe_id == probe.probe_id
                    and call.repetition == 1
                ]
                no_offer = next(call for call in members if call.offer_key == "no_persistence")
                governed = next(
                    call for call in members if call.offer_key == "governed_candidate"
                )
                self.assertFalse(governed.activated)
                self.assertEqual(governed.request_body, no_offer.request_body)

    def test_serialized_model_requests_exclude_harness_only_labels(self):
        forbidden = tuple(
            [world.world_id for world in WORLDS]
            + [probe.probe_id for world in WORLDS for probe in world.probes]
            + list(OFFERS)
            + ["same_family_increase", "unobserved_family_decoy", "expected_action"]
        )
        for call in later_schedule(world_material()):
            text = call.request_body.decode()
            for value in forbidden:
                self.assertNotIn(value, text)

    def test_full_fake_contact_completes_69_calls_and_retains_governance(self):
        invoker = FakeInvoker()
        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "evidence"
            summary = run_contact(invoker, directory, valid_receipt())
            requests = list((directory / "calls").glob("*.request.json"))
            governance = json.loads((directory / "world-a-governance.json").read_text())
        self.assertEqual(summary["contact_state"], "complete")
        self.assertEqual(summary["completed_logical_calls"], PLANNED_LOGICAL_CALLS)
        self.assertEqual(summary["physical_attempts"], PLANNED_LOGICAL_CALLS)
        self.assertEqual(len(summary["cells"]), 32)
        self.assertEqual(len(requests), 69)
        self.assertTrue(governance["admitted"])
        self.assertIsNone(summary["formation_verdict"])

    def test_wrong_later_action_and_unwarranted_guess_continue_without_retry(self):
        override = {
            "a-unobserved-decoy-no_persistence-r1": '{"action":"kiri"}',
            "a-same-increase-raw_occurrence-r1": '{"action":"toru"}',
        }
        with tempfile.TemporaryDirectory() as parent:
            summary = run_contact(
                FakeInvoker(override), Path(parent) / "evidence", valid_receipt()
            )
        self.assertEqual(summary["contact_state"], "complete")
        self.assertEqual(summary["physical_attempts"], 69)
        decoy = next(
            cell
            for cell in summary["cells"]
            if cell["probe_id"] == "a-unobserved-decoy"
            and cell["offer_key"] == "no_persistence"
        )
        self.assertIn(True, decoy["unwarranted_guesses"])

    def test_refused_candidate_deactivates_governed_offer_but_contact_continues(self):
        wrong = json.loads(candidate_content(WORLD_A))
        wrong["increasing_slot"] = "second"
        invoker = FakeInvoker({"world-a-interpretation": json.dumps(wrong)})
        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "evidence"
            summary = run_contact(invoker, directory, valid_receipt())
            governed_requests = [
                call
                for call, _ in invoker.calls
                if call.world_id == "world-a" and call.offer_key == "governed_candidate"
            ]
        self.assertEqual(summary["contact_state"], "complete")
        self.assertFalse(summary["governance"]["world-a"]["admitted"])
        self.assertTrue(all(call.activated is False for call in governed_requests))
        self.assertTrue(
            all(NONE_OFFER in call.envelope["messages"][1]["content"] for call in governed_requests)
        )

    def test_unobservable_interface_or_acquisition_stops_without_model_search(self):
        with tempfile.TemporaryDirectory() as parent:
            interface = run_contact(
                FakeInvoker({"interface-disposable": "not json"}),
                Path(parent) / "interface",
                valid_receipt(),
            )
            acquisition = run_contact(
                FakeInvoker({"world-a-acquisition": '{"action":"unknown"}'}),
                Path(parent) / "acquisition",
                valid_receipt(),
            )
        self.assertEqual(interface["stop_reason"], "interface_action_unobservable")
        self.assertEqual(interface["physical_attempts"], 1)
        self.assertEqual(
            acquisition["stop_reason"], "world-a_acquisition_action_unobservable"
        )
        self.assertEqual(acquisition["physical_attempts"], 2)

    def test_transport_failure_alone_retries_and_spends_physical_ceiling(self):
        class RetryOnce(FakeInvoker):
            def __call__(self, call, attempt_index):
                if not self.calls:
                    self.calls.append((call, attempt_index))
                    attempt = ProviderAttempt(
                        call.logical_index,
                        attempt_index,
                        call.call_id,
                        call.request_body,
                        b"",
                        {"transport_error": "offline"},
                        None,
                        None,
                        None,
                        "start",
                        "end",
                        0.1,
                        "transport_failure",
                    )
                    raise InvocationFailure("transport_failure", attempt, True)
                return super().__call__(call, attempt_index)

        with tempfile.TemporaryDirectory() as parent:
            summary = run_contact(
                RetryOnce(), Path(parent) / "evidence", valid_receipt()
            )
        self.assertEqual(summary["contact_state"], "complete")
        self.assertEqual(summary["physical_attempts"], 70)
        self.assertLessEqual(summary["physical_attempts"], PHYSICAL_CALL_CEILING)


if __name__ == "__main__":
    unittest.main()
