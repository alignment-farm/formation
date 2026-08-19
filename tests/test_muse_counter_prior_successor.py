import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from contact import calibration_mechanism_discovery as base
from contact.exploratory_developmental_contact import (
    ENDPOINT,
    ProviderAttempt,
    canonical_json_bytes,
)
from contact.muse_counter_prior_successor import (
    ACTOR_SETTINGS,
    INTERPRETER_SETTINGS,
    MODEL,
    MODEL_ARCHITECTURE,
    MODEL_DIGEST,
    PROTOCOL_VERSION,
    actor_envelope,
    collect_provider_receipt,
    interpretation_envelope,
    later_schedule,
    run_contact,
)
from micro_environment import HOLD, REQUEST_CALIBRATION


def valid_receipt():
    return {
        "valid": True,
        "refusals": [],
        "endpoint": ENDPOINT,
        "parsed_inspection": {
            "id": MODEL_DIGEST,
            "tags": [MODEL],
            "config": {"architecture": MODEL_ARCHITECTURE},
        },
    }


def experience_for(world):
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


def candidate_for(world):
    return json.dumps(
        {
            "controller_family": world.acquisition.controller_family,
            "increasing_slot": "first" if world is base.WORLD_A else "second",
            "scope": "same_controller_family",
            "counterevidence": "A same-family transition moves oppositely.",
        }
    )


def material():
    result = {}
    for world in base.WORLDS:
        experience = experience_for(world)
        interpretation = candidate_for(world)
        governance = base.govern_candidate(interpretation, experience)
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
            world = next(w for w in base.WORLDS if w.world_id == call.world_id)
            content = candidate_for(world)
        elif call.call_id == "interface-disposable":
            content = json.dumps({"action": HOLD})
        elif call.call_id.endswith("-acquisition"):
            content = json.dumps({"action": REQUEST_CALIBRATION})
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


class MuseCounterPriorSuccessorTests(unittest.TestCase):
    def test_model_native_envelopes_bind_exact_model_and_remove_qwen_instruction(self):
        actor = actor_envelope(base.WORLD_A.acquisition)
        interpreter = interpretation_envelope(experience_for(base.WORLD_A))
        self.assertEqual(actor["model"], MODEL)
        self.assertEqual(interpreter["model"], MODEL)
        self.assertNotIn("/no_think", json.dumps(actor))
        self.assertNotIn("/no_think", json.dumps(interpreter))
        for key, value in ACTOR_SETTINGS.items():
            self.assertEqual(actor[key], value)
        for key, value in INTERPRETER_SETTINGS.items():
            self.assertEqual(interpreter[key], value)

    def test_successor_schedule_preserves_all_consumed_cases_and_assignments(self):
        predecessor = base.later_schedule(material())
        successor = later_schedule(material())
        self.assertEqual(len(successor), 64)
        for old, new in zip(predecessor, successor, strict=True):
            self.assertEqual(
                (
                    old.logical_index,
                    old.call_id,
                    old.state,
                    old.profile,
                    old.expected_action,
                    old.activated,
                ),
                (
                    new.logical_index,
                    new.call_id,
                    new.state,
                    new.profile,
                    new.expected_action,
                    new.activated,
                ),
            )
            self.assertEqual(new.envelope["model"], MODEL)

    def test_successor_requests_exclude_harness_labels(self):
        forbidden = list(base.OFFERS) + [
            "world-a",
            "world-b",
            "same_family_increase",
            "unobserved_family_decoy",
            "expected_action",
        ]
        for call in later_schedule(material()):
            text = call.request_body.decode()
            for value in forbidden:
                self.assertNotIn(value, text)

    def test_provider_receipt_binds_exact_muse_artifact(self):
        inspection = {
            "id": MODEL_DIGEST,
            "tags": [MODEL],
            "config": {"architecture": MODEL_ARCHITECTURE},
        }

        def fake_command(command):
            stdout = {
                "version": "Client v1.2.6 Server v1.2.6",
                "status": "llama.cpp Running",
                "list": MODEL,
                "inspect": json.dumps(inspection),
            }[command[2]]
            return {"command": list(command), "returncode": 0, "stdout": stdout, "stderr": ""}

        with patch(
            "contact.muse_counter_prior_successor._run_command",
            side_effect=fake_command,
        ):
            receipt = collect_provider_receipt()
        self.assertTrue(receipt["valid"])
        self.assertEqual(receipt["parsed_inspection"]["id"], MODEL_DIGEST)

    def test_full_fake_successor_completes_and_records_its_own_identity(self):
        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "evidence"
            summary = run_contact(FakeInvoker(), directory, valid_receipt())
            protocol = json.loads((directory / "protocol.json").read_text())
            requests = list((directory / "calls").glob("*.request.json"))
        self.assertEqual(summary["contact_state"], "complete")
        self.assertEqual(summary["completed_logical_calls"], 69)
        self.assertEqual(summary["model"], MODEL)
        self.assertEqual(summary["model_digest"], MODEL_DIGEST)
        self.assertEqual(summary["protocol"], PROTOCOL_VERSION)
        self.assertEqual(protocol["model_native_adjustments"][0], "qwen_no_think_instruction_omitted")
        self.assertEqual(len(requests), 69)
        self.assertIsNone(summary["formation_verdict"])

    def test_unobservable_interface_stops_without_another_model(self):
        with tempfile.TemporaryDirectory() as parent:
            summary = run_contact(
                FakeInvoker({"interface-disposable": "not json"}),
                Path(parent) / "evidence",
                valid_receipt(),
            )
        self.assertEqual(summary["stop_reason"], "interface_action_unobservable")
        self.assertEqual(summary["physical_attempts"], 1)
        self.assertEqual(summary["model"], MODEL)


if __name__ == "__main__":
    unittest.main()
