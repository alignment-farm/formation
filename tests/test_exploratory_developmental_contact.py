import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from contact.exploratory_developmental_contact import (
    ACQUISITION_STATE,
    ACTOR_SETTINGS,
    ENDPOINT,
    INSPECT_TAG,
    MODEL,
    MODEL_DIGEST,
    OFFERS,
    PHYSICAL_CALL_CEILING,
    PLANNED_LOGICAL_CALLS,
    PROBES,
    STATIC_LESSON,
    ActionParse,
    InvocationFailure,
    LiveInvoker,
    LogicalCall,
    ProviderAttempt,
    actor_envelope,
    canonical_json_bytes,
    collect_provider_receipt,
    later_schedule,
    parse_action,
    run_contact,
)
from micro_environment.revision_gated_release import REBUILD_THEN_RELEASE, RELEASE


def valid_receipt():
    return {
        "valid": True,
        "refusals": [],
        "endpoint": ENDPOINT,
        "parsed_inspection": {"id": MODEL_DIGEST, "tags": [INSPECT_TAG]},
    }


class FakeInvoker:
    def __init__(self, overrides=None):
        self.overrides = {} if overrides is None else overrides
        self.calls = []

    def content_for(self, call):
        if call.call_id in self.overrides:
            return self.overrides[call.call_id]
        if call.responsibility == "interpreter":
            return (
                "The result may suggest rebuilding when revisions differ. "
                "One encounter cannot establish the full scope; an equal-revision "
                "case or a reversed mismatch could count against this interpretation."
            )
        action = (
            RELEASE
            if call.situation is not None
            and call.situation.artifact_revision == call.situation.authority_revision
            else REBUILD_THEN_RELEASE
        )
        if call.call_id == "acquisition":
            action = RELEASE
        return json.dumps({"action": action}, separators=(",", ":"))

    def __call__(self, call, attempt_index):
        self.calls.append((call, attempt_index))
        content = self.content_for(call)
        message = {
            "role": "assistant",
            "content": content,
            "reasoning_content": "not an action",
        }
        envelope = {
            "model": MODEL,
            "choices": [
                {"index": 0, "message": message, "finish_reason": "stop"}
            ],
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


class ExploratoryDevelopmentalContactTests(unittest.TestCase):
    def test_action_parser_is_strict_and_scores_no_task_quality(self):
        self.assertEqual(parse_action('{"action":"release"}'), ActionParse(RELEASE, None))
        self.assertEqual(
            parse_action('{"action":"rebuild_then_release"}'),
            ActionParse(REBUILD_THEN_RELEASE, None),
        )
        refusals = {
            "": "empty_content",
            "not json": "invalid_json",
            '{"action":"release","action":"release"}': "invalid_json",
            '{"action":"release","extra":1}': "invalid_action_object",
            '{"action":1}': "action_not_string",
            '{"action":"wait"}': "unknown_action",
        }
        for content, reason in refusals.items():
            with self.subTest(content=content):
                self.assertEqual(parse_action(content).refusal, reason)
        self.assertEqual(parse_action(None).refusal, "content_not_string")

    def test_schedule_is_exact_rotating_and_actor_interface_is_identical(self):
        offers = {
            "no_offer": None,
            "raw_experience": "raw",
            "runtime_interpretation": "interpretation",
            "frozen_lesson": STATIC_LESSON,
        }
        calls = later_schedule(offers)
        self.assertEqual(len(calls), 24)
        self.assertEqual([call.logical_index for call in calls], list(range(4, 28)))
        self.assertEqual(
            [call.offer_key for call in calls[:4]],
            ["no_offer", "raw_experience", "runtime_interpretation", "frozen_lesson"],
        )
        self.assertEqual(
            [call.offer_key for call in calls[12:16]],
            ["frozen_lesson", "no_offer", "raw_experience", "runtime_interpretation"],
        )
        for call in calls:
            for key, value in ACTOR_SETTINGS.items():
                self.assertEqual(call.envelope[key], value)
            self.assertEqual(call.envelope["model"], MODEL)
            self.assertNotIn(str(call.offer_key), call.envelope["messages"][1]["content"])
            self.assertNotIn(str(call.probe_id), call.envelope["messages"][1]["content"])
        self.assertEqual(
            {(call.probe_id, call.offer_key, call.repetition) for call in calls},
            {
                (probe.probe_id, offer, repetition)
                for probe in PROBES
                for offer in OFFERS
                for repetition in (1, 2)
            },
        )

    def test_full_fake_contact_retains_exact_requests_and_completes_all_calls(self):
        invoker = FakeInvoker()
        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "evidence"
            summary = run_contact(invoker, directory, valid_receipt())
            acquisition = json.loads((directory / "acquisition_experience.json").read_text())
            interpretation = json.loads((directory / "runtime_interpretation.json").read_text())
            requests = list((directory / "calls").glob("*.request.json"))
            first_request = (directory / "calls/01-interface-disposable-a1.request.json").read_bytes()
        self.assertEqual(summary["contact_state"], "complete")
        self.assertIsNone(summary["formation_verdict"])
        self.assertEqual(summary["completed_logical_calls"], PLANNED_LOGICAL_CALLS)
        self.assertEqual(summary["physical_attempts"], PLANNED_LOGICAL_CALLS)
        self.assertEqual(len(summary["cells"]), 12)
        self.assertTrue(all(len(cell["actions"]) == 2 for cell in summary["cells"]))
        self.assertEqual(len(invoker.calls), 27)
        self.assertEqual(len(requests), 27)
        self.assertEqual(first_request, invoker.calls[0][0].request_body)
        self.assertEqual(acquisition["surfaced_action"], RELEASE)
        self.assertEqual(acquisition["environment_result"]["observation"], "stale_dependency")
        self.assertEqual(interpretation["author"], "cold_model")

    def test_interpreter_sees_only_acquisition_and_offers_keep_authorship_separate(self):
        invoker = FakeInvoker()
        with tempfile.TemporaryDirectory() as parent:
            run_contact(invoker, Path(parent) / "evidence", valid_receipt())
        interpreter_call = next(call for call, _ in invoker.calls if call.responsibility == "interpreter")
        interpreter_prompt = interpreter_call.envelope["messages"][1]["content"]
        self.assertIn('"artifact_revision": 7', interpreter_prompt)
        self.assertIn("stale_dependency", interpreter_prompt)
        self.assertNotIn("later-adjacent", interpreter_prompt)
        self.assertNotIn("41", interpreter_prompt)
        self.assertNotIn(STATIC_LESSON, interpreter_prompt)
        self.assertNotIn("frozen_lesson", interpreter_prompt)

        raw_call = next(call for call, _ in invoker.calls if call.offer_key == "raw_experience")
        interpreted_call = next(
            call for call, _ in invoker.calls if call.offer_key == "runtime_interpretation"
        )
        lesson_call = next(call for call, _ in invoker.calls if call.offer_key == "frozen_lesson")
        self.assertIn("stale_dependency", raw_call.envelope["messages"][1]["content"])
        self.assertIn("One encounter cannot", interpreted_call.envelope["messages"][1]["content"])
        self.assertIn(STATIC_LESSON, lesson_call.envelope["messages"][1]["content"])

    def test_unobservable_interface_stops_without_a_model_search(self):
        invoker = FakeInvoker({"interface-disposable": "not json"})
        with tempfile.TemporaryDirectory() as parent:
            summary = run_contact(invoker, Path(parent) / "evidence", valid_receipt())
        self.assertEqual(summary["contact_state"], "stopped")
        self.assertEqual(summary["stop_reason"], "interface_action_unobservable")
        self.assertEqual(summary["physical_attempts"], 1)
        self.assertEqual(summary["completed_logical_calls"], 1)

    def test_unobservable_acquisition_stops_without_synthesizing_consequence(self):
        invoker = FakeInvoker({"acquisition": '{"action":"wait"}'})
        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "evidence"
            summary = run_contact(invoker, directory, valid_receipt())
            logical = json.loads((directory / "calls/02-acquisition.logical.json").read_text())
        self.assertEqual(summary["stop_reason"], "acquisition_action_unobservable")
        self.assertIsNone(logical["environment_result"])
        self.assertEqual(summary["physical_attempts"], 2)

    def test_wrong_and_invalid_later_behavior_is_retained_without_retry_or_stop(self):
        invoker = FakeInvoker({"later-adjacent-no_offer-r1": '{"action":"wait"}'})
        with tempfile.TemporaryDirectory() as parent:
            summary = run_contact(invoker, Path(parent) / "evidence", valid_receipt())
        self.assertEqual(summary["contact_state"], "complete")
        self.assertEqual(summary["physical_attempts"], 27)
        cell = next(
            item
            for item in summary["cells"]
            if item["probe_id"] == "later-adjacent" and item["offer_key"] == "no_offer"
        )
        self.assertIn("unknown_action", cell["action_refusals"])
        self.assertIn(None, cell["environment_dispositions"])

    def test_transport_failure_alone_retries_once_and_spends_physical_budget(self):
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

        invoker = RetryOnce()
        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "evidence"
            summary = run_contact(invoker, directory, valid_receipt())
            retry = json.loads(
                (directory / "calls/01-interface-disposable-a2.meta.json").read_text()
            )
        self.assertEqual(summary["contact_state"], "complete")
        self.assertEqual(summary["physical_attempts"], 28)
        self.assertEqual(retry["retry_of_attempt"], 1)

    def test_request_drift_and_budget_exhaustion_fail_closed(self):
        class SlotDrift(FakeInvoker):
            def __call__(self, call, attempt_index):
                attempt = super().__call__(call, attempt_index)
                return ProviderAttempt(
                    attempt.logical_index,
                    attempt.attempt_index,
                    attempt.call_id,
                    attempt.request_body + b" ",
                    attempt.response_body,
                    attempt.response_envelope,
                    attempt.message,
                    attempt.content,
                    attempt.http_status,
                    attempt.started_at,
                    attempt.ended_at,
                    attempt.elapsed_seconds,
                )

        with tempfile.TemporaryDirectory() as parent:
            drifted = run_contact(SlotDrift(), Path(parent) / "drift", valid_receipt())
            exhausted = run_contact(
                FakeInvoker(), Path(parent) / "budget", valid_receipt(), physical_ceiling=1
            )
        self.assertEqual(drifted["stop_reason"], "request_bytes_drifted")
        self.assertEqual(drifted["completed_logical_calls"], 0)
        self.assertEqual(exhausted["stop_reason"], "physical_call_ceiling_reached")
        self.assertEqual(exhausted["physical_attempts"], 1)

    def test_live_invoker_uses_docker_endpoint_without_auth_and_scores_content_only(self):
        captured = {}

        class Response:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self):
                return canonical_json_bytes(
                    {
                        "choices": [
                            {
                                "message": {
                                    "role": "assistant",
                                    "content": '{"action":"release"}',
                                    "reasoning_content": '{"action":"rebuild_then_release"}',
                                },
                                "finish_reason": "stop",
                            }
                        ]
                    }
                )

        def fake_open(request, timeout):
            captured["url"] = request.full_url
            captured["headers"] = dict(request.header_items())
            captured["data"] = request.data
            captured["timeout"] = timeout
            return Response()

        call = LogicalCall(
            1,
            "interface-disposable",
            "actor",
            actor_envelope(ACQUISITION_STATE),
            situation=ACQUISITION_STATE,
        )
        with patch("contact.exploratory_developmental_contact.urlopen", side_effect=fake_open):
            attempt = LiveInvoker()(call, 1)
        self.assertEqual(captured["url"], ENDPOINT)
        self.assertEqual(captured["data"], call.request_body)
        self.assertNotIn("Authorization", captured["headers"])
        self.assertEqual(parse_action(attempt.content).action, RELEASE)
        self.assertEqual(
            attempt.message["reasoning_content"], '{"action":"rebuild_then_release"}'
        )

    def test_provider_receipt_binds_exact_model_and_running_llama_engine(self):
        inspection = {
            "id": MODEL_DIGEST,
            "tags": [INSPECT_TAG],
            "config": {"architecture": "qwen3"},
        }

        def fake_command(command):
            stdout = {
                "version": "Client v1.2.6\nServer v1.2.6",
                "status": "llama.cpp  Running",
                "list": "qwen3:14B-Q6_K",
                "inspect": json.dumps(inspection),
            }[command[2]]
            return {"command": list(command), "returncode": 0, "stdout": stdout, "stderr": ""}

        with patch(
            "contact.exploratory_developmental_contact._run_command",
            side_effect=fake_command,
        ):
            receipt = collect_provider_receipt()
        self.assertTrue(receipt["valid"])
        self.assertEqual(receipt["parsed_inspection"]["id"], MODEL_DIGEST)

    def test_contact_brief_and_code_share_load_bearing_literals(self):
        root = Path(__file__).resolve().parents[1]
        brief = (root / "docs/EXPLORATORY_DEVELOPMENTAL_CONTACT.md").read_text()
        normalized = " ".join(
            line.strip().removeprefix("> ") for line in brief.splitlines()
        )
        self.assertIn(MODEL, brief)
        self.assertIn(MODEL_DIGEST, brief)
        self.assertIn(ENDPOINT, brief)
        self.assertIn(STATIC_LESSON, normalized)
        self.assertIn(f"{PLANNED_LOGICAL_CALLS} planned logical calls", brief)
        self.assertIn(f"hard ceiling is {PHYSICAL_CALL_CEILING}", brief)


if __name__ == "__main__":
    unittest.main()
