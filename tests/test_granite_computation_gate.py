from dataclasses import asdict
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from contact.granite_computation_gate import (
    MODEL, PROMPTS, SAMPLING, TASKS, LiveInvoker, load_command,
    request_envelope, run_gate, run_live, validate_loaded_instance,
)
from contact.structured_output_interface_trial import Attempt, ContactAbort


CORRECT = {
    "filtered_ordering": '{"answer":["ash","maple"]}',
    "ordered_operations": '{"answer":17}',
    "latest_enabled_revisions": '{"answer":["oak"]}',
    "dependency_reachability": '{"answer":["clay","fuel","kiln","mold"]}',
}


class FakeInvoker:
    def __init__(self, outputs=None, empty_once=False):
        self.outputs = {} if outputs is None else outputs
        self.empty_once = empty_once
        self.calls = []

    def __call__(self, model, task):
        self.calls.append(task.task_id)
        output = self.outputs.get(task.task_id, CORRECT[task.task_id])
        if self.empty_once and len(self.calls) == 1:
            output = ""
        return Attempt(
            task.logical_index, 1, task.task_id, task.task_id, "constrained",
            task.seed, model.model_key, model.live_identifier, task.prompt, output,
            request_envelope(task), {"choices": [{"message": {"content": output}}]},
            "2026-08-15T00:00:00+00:00", "2026-08-15T00:00:01+00:00", 1.0,
        )


class GraniteComputationGateTests(unittest.TestCase):
    def test_document_locks_prompts_oracles_schemas_and_seeds(self):
        document = (Path(__file__).parents[1] / "docs" / "GRANITE_COMPUTATION_GATE.md").read_text()
        headings = ("Task 1: filtered ordering", "Task 2: ordered operations",
                    "Task 3: latest enabled revisions", "Task 4: dependency reachability")
        for task, heading in zip(TASKS, headings, strict=True):
            section = document.split("## " + heading, 1)[1].split("## ", 1)[0]
            self.assertEqual(task.prompt, section.split("Exact prompt:\n\n```text\n", 1)[1].split("\n```", 1)[0])
            self.assertEqual(task.oracle_answer, json.loads(section.split("Bare oracle value:\n\n```json\n", 1)[1].split("\n```", 1)[0]))
            self.assertEqual(task.response_format, json.loads(section.split("Exact `response_format`:\n\n```json\n", 1)[1].split("\n```", 1)[0]))
        self.assertEqual([task.seed for task in TASKS], [5001, 5002, 5003, 5004])
        self.assertEqual(tuple(task.prompt for task in TASKS), PROMPTS)

    def test_model_artifact_constants_and_request_surface(self):
        self.assertEqual(asdict(MODEL), {
            "name": "Granite 4.0 H Tiny", "model_key": "ibm/granite-4-h-tiny",
            "selected_variant": "ibm/granite-4-h-tiny@q4_k_m",
            "live_identifier": "formation-granite-computation-gate",
            "relative_file": "lmstudio-community/granite-4.0-h-tiny-GGUF/granite-4.0-h-tiny-Q4_K_M.gguf",
            "byte_count": 4230975936,
            "sha256": "064bea0136420b38d0b65697fa5e772e28b112eee1757aacc7f64eba6bf37810",
            "template_characters": 6099,
            "template_sha256": "fed2756d2d24e127b951dcf139d0b03ab7db8ef23a456128ebc9c2db4901d476",
        })
        for task in TASKS:
            envelope = request_envelope(task)
            self.assertEqual(set(envelope), {"model", "messages", "seed", "response_format", *SAMPLING.keys()})
            self.assertEqual(envelope["seed"], task.seed)
            self.assertEqual(envelope["model"], MODEL.live_identifier)
            self.assertEqual(envelope["messages"], [{"role": "user", "content": task.prompt}])
            self.assertEqual(envelope["response_format"], task.response_format)
        self.assertEqual(load_command(MODEL), (
            "lms", "load", MODEL.model_key, "--gpu", "max", "--context-length", "8192",
            "--parallel", "1", "--no-speculative-draft-mtp", "--identifier", MODEL.live_identifier, "-y",
        ))
        instance = {"identifier": MODEL.live_identifier, "selectedVariant": MODEL.selected_variant,
                    "contextLength": 8192, "parallel": 1, "vision": False}
        self.assertIs(validate_loaded_instance(MODEL, [instance]), instance)

    def test_four_correct_pass_and_any_failure_closes_after_all_calls(self):
        with tempfile.TemporaryDirectory() as parent:
            passed = run_gate(FakeInvoker(), Path(parent) / "pass")
        self.assertEqual(passed["candidate_result"], "gate_pass")
        failures = {"filtered_ordering": '{"answer":[]}', "ordered_operations": "```json\n{\"answer\":17}\n```"}
        invoker = FakeInvoker(failures)
        with tempfile.TemporaryDirectory() as parent:
            failed = run_gate(invoker, Path(parent) / "fail")
        self.assertEqual(len(invoker.calls), 4)
        self.assertEqual(failed["candidate_result"], "computation_unreliable")
        self.assertEqual([item["call_state"] for item in failed["calls"][:2]], ["valid_wrong", "invalid"])

    def test_exact_empty_retries_but_whitespace_does_not(self):
        retry = FakeInvoker(empty_once=True)
        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "retry"
            result = run_gate(retry, directory)
            first = json.loads((directory / "01-filtered_ordering-a1.json").read_text())
        self.assertEqual(result["candidate_result"], "gate_pass")
        self.assertEqual(len(retry.calls), 5)
        self.assertEqual(first["call_label"], "retry_pending")
        whitespace = FakeInvoker({"filtered_ordering": "   "})
        with tempfile.TemporaryDirectory() as parent:
            result = run_gate(whitespace, Path(parent) / "white")
        self.assertEqual(len(whitespace.calls), 4)
        self.assertEqual(result["calls"][0]["gate_refusal"], "empty_output")

    def test_request_drift_aborts_with_nullable_record(self):
        class Drift(FakeInvoker):
            def __call__(self, model, task):
                attempt = super().__call__(model, task)
                return Attempt(**{**asdict(attempt), "request_envelope": {**attempt.request_envelope, "seed": 9}})
        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "drift"
            result = run_gate(Drift(), directory)
            record = json.loads((directory / "01-filtered_ordering-a1.json").read_text())
        self.assertEqual(result["packet_status"], "aborted")
        self.assertEqual(result["abort_reason"], "request_contract_rejected")
        self.assertIsNone(result["candidate_result"])
        self.assertIsNone(record["call_state"])

    def test_provider_abort_is_retained(self):
        class Abort(FakeInvoker):
            def __call__(self, model, task):
                attempt = super().__call__(model, task)
                raise ContactAbort("provider_envelope_invalid", attempt)
        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "abort"
            result = run_gate(Abort(), directory)
            record = json.loads((directory / "01-filtered_ordering-a1.json").read_text())
        self.assertEqual(result["abort_reason"], "provider_envelope_invalid")
        self.assertIsNone(record["call_label"])

    def test_second_empty_and_empty_then_abort_paths(self):
        class TwoEmpty(FakeInvoker):
            def __call__(self, model, task):
                attempt = super().__call__(model, task)
                if task.logical_index == 1:
                    return Attempt(**{**asdict(attempt), "output": ""})
                return attempt
        with tempfile.TemporaryDirectory() as parent:
            result = run_gate(TwoEmpty(), Path(parent) / "empty")
        self.assertEqual(result["calls"][0]["gate_refusal"], "empty_output")
        self.assertEqual(result["calls"][0]["call_state"], "invalid")

        class EmptyAbort(FakeInvoker):
            def __call__(self, model, task):
                attempt = super().__call__(model, task)
                if len(self.calls) == 1:
                    return Attempt(**{**asdict(attempt), "output": ""})
                raise ContactAbort("infrastructure_invalid", attempt)
        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "abort"
            result = run_gate(EmptyAbort(), directory)
            first = json.loads((directory / "01-filtered_ordering-a1.json").read_text())
            second = json.loads((directory / "01-filtered_ordering-a2.json").read_text())
        self.assertEqual(result["abort_reason"], "infrastructure_invalid")
        self.assertEqual(first["call_label"], "retry_pending")
        self.assertIsNone(second["call_label"])

    def test_live_invoker_uses_visible_content_only(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *_): return False
            def read(self):
                return json.dumps({"choices": [{"message": {"content": None, "reasoning_content": CORRECT["filtered_ordering"]}}]}).encode()
        with patch("contact.granite_computation_gate.urlopen", return_value=Response()):
            attempt = LiveInvoker()(MODEL, TASKS[0])
        self.assertEqual(attempt.output, "")

        class BadResponse(Response):
            def read(self): return json.dumps({"choices": [{"message": {"content": []}}]}).encode()
        with patch("contact.granite_computation_gate.urlopen", return_value=BadResponse()):
            with self.assertRaises(ContactAbort) as caught:
                LiveInvoker()(MODEL, TASKS[0])
        self.assertEqual(caught.exception.reason, "provider_envelope_invalid")
        self.assertEqual(caught.exception.attempt.response_envelope["choices"][0]["message"]["content"], [])

    def test_mid_packet_abort_retains_prior_calls(self):
        class LaterAbort(FakeInvoker):
            def __call__(self, model, task):
                attempt = super().__call__(model, task)
                if task.logical_index == 3:
                    raise ContactAbort("provider_envelope_invalid", attempt)
                return attempt
        with tempfile.TemporaryDirectory() as parent:
            result = run_gate(LaterAbort(), Path(parent) / "later")
        self.assertEqual(len(result["calls"]), 2)
        self.assertEqual(result["packet_status"], "aborted")
        self.assertIsNone(result["candidate_result"])

    def test_live_orchestration_loads_exact_model_and_unloads(self):
        commands = []
        def fake_run(command, **_):
            commands.append(command)
            if command == ("lms", "--version"):
                return SimpleNamespace(returncode=0, stdout="CLI test\n", stderr="")
            if command == ("lms", "runtime", "ls"):
                return SimpleNamespace(returncode=0, stdout="runtime\n", stderr="")
            if command == ("lms", "server", "start"):
                return SimpleNamespace(returncode=0, stdout="", stderr="started\n")
            if command == ("lms", "unload", "--all"):
                return SimpleNamespace(returncode=0, stdout="", stderr="")
            if command == load_command(MODEL):
                return SimpleNamespace(returncode=0, stdout="loaded\n", stderr="")
            if command == ("lms", "ps", "--json"):
                value = [{"identifier": MODEL.live_identifier, "selectedVariant": MODEL.selected_variant,
                          "contextLength": 8192, "parallel": 1, "vision": False}]
                return SimpleNamespace(returncode=0, stdout=json.dumps(value), stderr="")
            raise AssertionError(command)
        invoker = FakeInvoker()
        with tempfile.TemporaryDirectory() as parent, \
             patch("contact.granite_computation_gate.verify_artifact", return_value={"verified": True}), \
             patch("contact.granite_computation_gate.subprocess.run", side_effect=fake_run), \
             patch("contact.granite_computation_gate.LiveInvoker", return_value=invoker):
            result = run_live(Path(parent) / "evidence")
        self.assertEqual(result["candidate_result"], "gate_pass")
        self.assertEqual(len(invoker.calls), 4)
        self.assertGreaterEqual(commands.count(("lms", "unload", "--all")), 2)


if __name__ == "__main__":
    unittest.main()
