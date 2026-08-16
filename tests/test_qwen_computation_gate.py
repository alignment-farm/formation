from dataclasses import asdict
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from contact.qwen_computation_gate import (
    HUB_FILES, MODEL, PACKAGE_FILES, PROMPTS, SAMPLING, TASKS, LiveInvoker,
    load_command, request_envelope, run_gate, run_live, validate_loaded,
)
from contact.structured_output_interface_trial import Attempt, ContactAbort


CORRECT = {
    "filtered_ordering": '{"answer":["ash","elm","yew"]}',
    "ordered_operations": '{"answer":21}',
    "latest_enabled_revisions": '{"answer":["alpha","gamma"]}',
    "dependency_reachability": '{"answer":["leaf1","leaf2","north","shared","south"]}',
}


class Fake:
    def __init__(self, outputs=None, empty=False): self.outputs = outputs or {}; self.empty = empty; self.calls = []
    def __call__(self, model, task):
        self.calls.append(task.task_id); output = self.outputs.get(task.task_id, CORRECT[task.task_id])
        if self.empty and len(self.calls) == 1: output = ""
        return Attempt(task.logical_index, 1, task.task_id, task.task_id, "constrained", task.seed,
                       model.model_key, model.live_identifier, task.prompt, output, request_envelope(task),
                       {"choices": [{"message": {"content": output}}]}, "start", "end", 1.0)


class QwenGateTests(unittest.TestCase):
    def test_document_locks_tasks(self):
        doc = (Path(__file__).parents[1] / "docs" / "QWEN_COMPUTATION_GATE.md").read_text()
        headings = ("1. Filtered ordering", "2. Ordered operations", "3. Latest enabled revisions", "4. Dependency reachability")
        for task, heading in zip(TASKS, headings, strict=True):
            section = doc.split("### " + heading, 1)[1].split("### ", 1)[0].split("## ", 1)[0]
            documented = section.split("```text\n", 1)[1].split("\n```", 1)[0]
            self.assertEqual(task.prompt, documented)
            self.assertIn(f"seed `{task.seed}`", section)
        self.assertEqual(tuple(task.prompt for task in TASKS), PROMPTS)
        self.assertEqual([task.oracle_answer for task in TASKS], [["ash", "elm", "yew"], 21, ["alpha", "gamma"], ["leaf1", "leaf2", "north", "shared", "south"]])

    def test_package_constants_and_request(self):
        doc = (Path(__file__).parents[1] / "docs" / "QWEN_COMPUTATION_GATE.md").read_text()
        manifest = doc.split("Before contact, require exactly these package files and SHA-256 bindings:\n\n```text\n", 1)[1].split("\n```", 1)[0]
        documented = {line.split()[0]: line.split()[1] for line in manifest.splitlines()}
        self.assertEqual(documented, {name: value[1] for name, value in PACKAGE_FILES.items()})
        for name, (_, digest) in HUB_FILES.items(): self.assertIn(f"{name} {digest}", doc)
        self.assertEqual(HUB_FILES, {"model.yaml": (1695, "41e997d0ab4ca5572918e33c1c5284c5a9c4032ce3affe40b33ad76d7706746b"), "manifest.json": (770, "c19d54c5855a8c596dd6197f715ffff20fc06dead920fce8faba9353edc6c8d1")})
        self.assertEqual(len(PACKAGE_FILES), 11)
        self.assertEqual(SAMPLING["max_tokens"], 1024)
        for task in TASKS:
            env = request_envelope(task)
            self.assertEqual(set(env), {"model", "messages", "seed", "response_format", *SAMPLING})
            self.assertEqual(env["messages"], [{"role": "user", "content": task.prompt}])
            schema = task.response_format["json_schema"]["schema"]
            self.assertEqual(set(schema), {"type", "properties", "required", "additionalProperties"})
            self.assertEqual(schema["required"], ["answer"]); self.assertFalse(schema["additionalProperties"])
            answer = schema["properties"]["answer"]
            self.assertTrue(set(answer) <= {"type", "items"})
            self.assertFalse({"enum", "const", "pattern", "minimum", "maximum", "minItems", "maxItems"} & set(answer))
            expected_name = task.task_id + "_answer"
            self.assertEqual(task.response_format["json_schema"]["name"], expected_name)
            if task.task_id == "ordered_operations": self.assertEqual(answer, {"type": "integer"})
            else: self.assertEqual(answer, {"type": "array", "items": {"type": "string"}})

    def test_load_contract(self):
        self.assertEqual(load_command(), ("lms", "load", MODEL.model_key, "--gpu", "max", "--parallel", "1", "--no-speculative-draft-mtp", "--identifier", MODEL.live_identifier, "-y"))
        item = {"identifier": MODEL.live_identifier, "selectedVariant": MODEL.selected_variant, "format": "safetensors", "contextLength": 262144, "parallel": 1, "vision": True}
        self.assertIs(validate_loaded([item]), item)
        with self.assertRaises(ValueError): validate_loaded([item, item])

    def test_pass_and_fail_run_all_four(self):
        with tempfile.TemporaryDirectory() as parent: passed = run_gate(Fake(), Path(parent) / "pass")
        self.assertEqual(passed["candidate_result"], "gate_pass")
        fake = Fake({"ordered_operations": '{"answer":20}'})
        with tempfile.TemporaryDirectory() as parent: failed = run_gate(fake, Path(parent) / "fail")
        self.assertEqual(len(fake.calls), 4); self.assertEqual(failed["candidate_result"], "computation_unreliable")

    def test_empty_retry_and_reasoning_is_not_scored(self):
        fake = Fake(empty=True)
        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "retry"; result = run_gate(fake, directory)
            first = json.loads((directory / "01-filtered_ordering-a1.json").read_text())
        self.assertEqual(result["candidate_result"], "gate_pass"); self.assertEqual(len(fake.calls), 5); self.assertEqual(first["call_label"], "retry_pending")

        class Response:
            def __enter__(self): return self
            def __exit__(self, *_): return False
            def read(self): return json.dumps({"choices": [{"message": {"content": None, "reasoning_content": CORRECT["filtered_ordering"]}}]}).encode()
        with patch("contact.qwen_computation_gate.urlopen", return_value=Response()): self.assertEqual(LiveInvoker()(MODEL, TASKS[0]).output, "")

    def test_drift_and_provider_abort(self):
        class Drift(Fake):
            def __call__(self, model, task):
                attempt = super().__call__(model, task)
                return Attempt(**{**asdict(attempt), "request_envelope": {**attempt.request_envelope, "seed": 0}})
        with tempfile.TemporaryDirectory() as parent: drift = run_gate(Drift(), Path(parent) / "drift")
        self.assertEqual(drift["abort_reason"], "request_contract_rejected")
        class Abort(Fake):
            def __call__(self, model, task):
                attempt = super().__call__(model, task); raise ContactAbort("provider_envelope_invalid", attempt)
        with tempfile.TemporaryDirectory() as parent: abort = run_gate(Abort(), Path(parent) / "abort")
        self.assertEqual(abort["packet_status"], "aborted"); self.assertIsNone(abort["candidate_result"])

    def test_whitespace_double_empty_and_empty_abort(self):
        whitespace = Fake({"filtered_ordering": "   "})
        with tempfile.TemporaryDirectory() as parent: result = run_gate(whitespace, Path(parent) / "white")
        self.assertEqual(len(whitespace.calls), 4); self.assertEqual(result["calls"][0]["gate_refusal"], "empty_output")
        class TwoEmpty(Fake):
            def __call__(self, model, task):
                attempt = super().__call__(model, task)
                return Attempt(**{**asdict(attempt), "output": ""}) if task.logical_index == 1 else attempt
        with tempfile.TemporaryDirectory() as parent: result = run_gate(TwoEmpty(), Path(parent) / "two")
        self.assertEqual(result["calls"][0]["call_state"], "invalid")
        class EmptyAbort(Fake):
            def __call__(self, model, task):
                attempt = super().__call__(model, task)
                if len(self.calls) == 1: return Attempt(**{**asdict(attempt), "output": ""})
                raise ContactAbort("infrastructure_invalid", attempt)
        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "abort"; result = run_gate(EmptyAbort(), directory)
            first = json.loads((directory / "01-filtered_ordering-a1.json").read_text())
        self.assertEqual(result["abort_reason"], "infrastructure_invalid"); self.assertEqual(first["call_label"], "retry_pending")

    def test_mid_packet_abort_and_nonstring_content(self):
        class Later(Fake):
            def __call__(self, model, task):
                attempt = super().__call__(model, task)
                if task.logical_index == 3: raise ContactAbort("provider_envelope_invalid", attempt)
                return attempt
        with tempfile.TemporaryDirectory() as parent: result = run_gate(Later(), Path(parent) / "later")
        self.assertEqual(len(result["calls"]), 2)
        class Response:
            def __enter__(self): return self
            def __exit__(self, *_): return False
            def read(self): return json.dumps({"choices": [{"message": {"content": []}}]}).encode()
        with patch("contact.qwen_computation_gate.urlopen", return_value=Response()):
            with self.assertRaises(ContactAbort) as caught: LiveInvoker()(MODEL, TASKS[0])
        self.assertEqual(caught.exception.reason, "provider_envelope_invalid")

    def test_live_orchestration_and_receipt_absences(self):
        commands = []
        def fake_run(command, **_):
            commands.append(command)
            if command == ("lms", "--version"): return SimpleNamespace(returncode=0, stdout="CLI\n", stderr="")
            if command == ("lms", "runtime", "ls"): return SimpleNamespace(returncode=0, stdout="runtime\n", stderr="")
            if command == ("lms", "server", "start"): return SimpleNamespace(returncode=0, stdout="", stderr="started")
            if command == ("lms", "unload", "--all"): return SimpleNamespace(returncode=0, stdout="", stderr="")
            if command == load_command(): return SimpleNamespace(returncode=0, stdout="loaded", stderr="")
            if command == ("lms", "ps", "--json"):
                item = {"identifier": MODEL.live_identifier, "selectedVariant": MODEL.selected_variant, "format": "safetensors", "contextLength": 262144, "parallel": 1, "vision": True}
                return SimpleNamespace(returncode=0, stdout=json.dumps([item]), stderr="")
            raise AssertionError(command)
        fake = Fake()
        with tempfile.TemporaryDirectory() as parent, patch("contact.qwen_computation_gate.verify_package", return_value={"bound": True}), patch("contact.qwen_computation_gate.subprocess.run", side_effect=fake_run), patch("contact.qwen_computation_gate.LiveInvoker", return_value=fake):
            result = run_live(Path(parent) / "evidence")
        receipt = result["packet_receipt"]
        self.assertFalse(receipt["authored_system_message"]); self.assertFalse(receipt["image_input"]); self.assertTrue(receipt["default_thinking"])
        self.assertEqual(len(fake.calls), 4); self.assertGreaterEqual(commands.count(("lms", "unload", "--all")), 2)


if __name__ == "__main__": unittest.main()
