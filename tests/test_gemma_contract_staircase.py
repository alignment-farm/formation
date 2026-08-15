from dataclasses import asdict
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from contact.gemma_contract_staircase import (
    MODELS,
    SAMPLING,
    TASKS,
    Attempt,
    LiveInvoker,
    exact_equal,
    load_command,
    run_live,
    run_model,
    score_output,
    validate_loaded_instance,
)


PASS_OUTPUTS = {
    "selection": '{"answer":["brim","dawn"]}',
    "grouped-totals": '{"answer":[["east",8],["west",3]]}',
    "ordered-updates": '{"answer":10}',
    "conjunctive-filter": '{"answer":["s"]}',
}


class FakeInvoker:
    def __init__(self, failures=None, empty_once=False):
        self.failures = {} if failures is None else failures
        self.empty_once = empty_once
        self.calls = []

    def __call__(self, model, task):
        self.calls.append((model, task))
        output = self.failures.get((model.model_key, task.call_id), PASS_OUTPUTS[task.call_id])
        if self.empty_once and len(self.calls) == 1:
            output = ""
        return Attempt(
            task.logical_index,
            1,
            task.call_id,
            task.seed,
            model.model_key,
            model.live_identifier,
            task.prompt,
            output,
            {"model": model.live_identifier, "seed": task.seed},
            {"choices": [{"message": {"content": output}}]},
            "2026-08-15T00:00:00+00:00",
            "2026-08-15T00:00:01+00:00",
            1.0,
        )


class GemmaContractStaircaseTests(unittest.TestCase):
    def test_prompts_are_byte_equal_to_normative_document(self):
        appendix = (Path(__file__).parents[1] / "docs" / "GEMMA_CONTRACT_STAIRCASE.md").read_text()
        headings = ("Task 1: selection", "Task 2: grouped totals", "Task 3: ordered updates", "Task 4: conjunctive filter")
        for task, heading in zip(TASKS, headings, strict=True):
            section = appendix.split("## " + heading, 1)[1]
            documented = section.split("```text\n", 1)[1].split("\n```", 1)[0]
            self.assertEqual(task.prompt, documented)
            documented_oracle = json.loads(section.split("Oracle:\n\n```json\n", 1)[1].split("\n```", 1)[0])
            self.assertTrue(exact_equal(task.oracle_answer, documented_oracle["answer"]))
        self.assertEqual([task.seed for task in TASKS], [3001, 3002, 3003, 3004])

    def test_model_artifact_constants_are_frozen(self):
        self.assertEqual(
            [asdict(model) for model in MODELS],
            [
                {
                    "name": "Gemma 3 270M Instruct QAT",
                    "model_key": "google/gemma-3-270m",
                    "selected_variant": "google/gemma-3-270m@q4_0",
                    "live_identifier": "formation-gemma-screen-270m",
                    "relative_file": "lmstudio-community/gemma-3-270m-it-qat-GGUF/gemma-3-270m-it-qat-Q4_0.gguf",
                    "byte_count": 241410208,
                    "sha256": "5f4b2e17722e510122c464573b880587f4983347a40e5472b858d5a3c1ab8095",
                    "template_characters": 1532,
                    "template_sha256": "7de1c58e208eda46e9c7f86397df37ec49883aeece39fb961e0a6b24088dd3c4",
                },
                {
                    "name": "Gemma 3 1B Instruct QAT",
                    "model_key": "google/gemma-3-1b",
                    "selected_variant": "google/gemma-3-1b@q4_0",
                    "live_identifier": "formation-gemma-screen-1b",
                    "relative_file": "lmstudio-community/gemma-3-1B-it-QAT-GGUF/gemma-3-1B-it-QAT-Q4_0.gguf",
                    "byte_count": 720425472,
                    "sha256": "b25d35b00fe699ef52bf399fa579f2c56664897c013aeba2686965fdb6265f0f",
                    "template_characters": 1532,
                    "template_sha256": "7de1c58e208eda46e9c7f86397df37ec49883aeece39fb961e0a6b24088dd3c4",
                },
            ],
        )

    def test_oracles_and_exact_type_comparison(self):
        for task in TASKS:
            self.assertEqual(score_output(PASS_OUTPUTS[task.call_id], task.oracle_answer)["call_label"], "full_pass")
        self.assertFalse(exact_equal(True, 1))
        self.assertFalse(exact_equal([1], [True]))
        self.assertTrue(exact_equal({"a": [1, None]}, {"a": [1, None]}))

    def test_gate_refusal_codes_and_wrong_answer(self):
        cases = {
            '```json\n{"answer":10}\n```': "markdown_fence",
            "   ": "empty_output",
            '{"answer":1,"answer":2}': "duplicate_key",
            '{"answer":NaN}': "nonfinite_constant",
            '{"answer":': "invalid_json",
            "[]": "exact_object_required",
            '{"answer":10,"extra":0}': "exact_object_required",
        }
        for output, refusal in cases.items():
            report = score_output(output, 10)
            self.assertEqual(report["gate_refusal"], refusal)
            self.assertEqual(report["call_label"], "gate_fail")
        wrong = score_output('{"answer":true}', 1)
        self.assertIsNone(wrong["gate_refusal"])
        self.assertEqual(wrong["call_label"], "wrong_answer")

    def test_one_model_pass_and_one_early_stop_have_no_synthetic_calls(self):
        invoker = FakeInvoker({(MODELS[0].model_key, "selection"): '{"answer":[]}'})
        with tempfile.TemporaryDirectory() as parent:
            first_dir = Path(parent) / "first"
            second_dir = Path(parent) / "second"
            first = run_model(invoker, MODELS[0], first_dir)
            second = run_model(invoker, MODELS[1], second_dir)
            self.assertEqual(len(list(first_dir.glob("*.prompt.txt"))), 1)
            self.assertEqual(len(list(second_dir.glob("*.prompt.txt"))), 4)
        self.assertEqual(first["terminal_result"], "contract_unreliable")
        self.assertEqual(second["terminal_result"], "screen_pass")
        self.assertEqual(len(invoker.calls), 5)

    def test_exact_empty_retries_once_but_whitespace_does_not(self):
        invoker = FakeInvoker(empty_once=True)
        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "model"
            result = run_model(invoker, MODELS[0], directory)
            first = json.loads((directory / "01-selection-a1.json").read_text())
            second = json.loads((directory / "01-selection-a2.json").read_text())
        self.assertEqual(result["terminal_result"], "screen_pass")
        self.assertEqual(len(invoker.calls), 5)
        self.assertEqual(first["call_label"], "retry_pending")
        self.assertEqual(first["retry_reason"], "no_model_content")
        self.assertEqual(first["oracle_answer"], ["brim", "dawn"])
        self.assertEqual(second["retry_of_attempt"], 1)

        whitespace = FakeInvoker({(MODELS[0].model_key, "selection"): "   "})
        with tempfile.TemporaryDirectory() as parent:
            result = run_model(whitespace, MODELS[0], Path(parent) / "model")
        self.assertEqual(result["terminal_result"], "contract_unreliable")
        self.assertEqual(len(whitespace.calls), 1)

        class TwoEmpty(FakeInvoker):
            def __call__(self, model, task):
                attempt = super().__call__(model, task)
                if task.logical_index == 1:
                    return Attempt(
                        attempt.logical_index, attempt.attempt_index, attempt.call_id,
                        attempt.seed, attempt.model_key, attempt.live_identifier,
                        attempt.prompt, "", attempt.request_envelope,
                        {"choices": [{"message": {"content": ""}}]},
                        attempt.started_at, attempt.ended_at, attempt.elapsed_seconds,
                    )
                return attempt
        two_empty = TwoEmpty()
        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "model"
            result = run_model(two_empty, MODELS[0], directory)
            final = json.loads((directory / "01-selection-a2.json").read_text())
        self.assertEqual(result["terminal_result"], "contract_unreliable")
        self.assertEqual(len(two_empty.calls), 2)
        self.assertEqual(final["gate_refusal"], "empty_output")
        self.assertEqual(final["call_label"], "gate_fail")

    def test_model_and_load_contract(self):
        self.assertEqual([model.selected_variant for model in MODELS], ["google/gemma-3-270m@q4_0", "google/gemma-3-1b@q4_0"])
        for model in MODELS:
            self.assertEqual(
                load_command(model),
                (
                    "lms", "load", model.model_key, "--gpu", "max",
                    "--context-length", "8192", "--parallel", "1",
                    "--no-speculative-draft-mtp", "--identifier", model.live_identifier, "-y",
                ),
            )
            instance = {
                "identifier": model.live_identifier,
                "selectedVariant": model.selected_variant,
                "contextLength": 8192,
                "parallel": 1,
                "vision": False,
            }
            self.assertIs(validate_loaded_instance(model, [instance]), instance)
            with self.assertRaisesRegex(ValueError, "exact_text_only_model_load_required"):
                validate_loaded_instance(model, [{**instance, "vision": True}])

    def test_live_request_and_provider_content_boundary(self):
        class Response:
            def __init__(self, content):
                self.content = content

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self):
                return json.dumps({"choices": [{"message": {"content": self.content, "reasoning_content": '{"answer":[]}'}}]}).encode()

        model, task = MODELS[0], TASKS[0]
        with patch("contact.gemma_contract_staircase.urlopen", return_value=Response(PASS_OUTPUTS[task.call_id])) as opened:
            attempt = LiveInvoker(model)(model, task)
        envelope = json.loads(opened.call_args.args[0].data)
        self.assertEqual(set(envelope), {"model", "messages", "seed", *SAMPLING.keys()})
        self.assertEqual(envelope["messages"], [{"role": "user", "content": task.prompt}])
        self.assertEqual(envelope["model"], model.live_identifier)
        self.assertEqual(attempt.output, PASS_OUTPUTS[task.call_id])

        with patch("contact.gemma_contract_staircase.urlopen", return_value=Response(None)):
            self.assertEqual(LiveInvoker(model)(model, task).output, "")
        with patch("contact.gemma_contract_staircase.urlopen", return_value=Response([])):
            with self.assertRaisesRegex(ValueError, "provider_envelope_invalid"):
                LiveInvoker(model)(model, task)

    def test_live_orchestration_continues_second_model_and_cleans_up(self):
        state = {"loaded": None}
        commands = []

        def fake_run(command, **_):
            commands.append(command)
            if command == ("lms", "--version"):
                return SimpleNamespace(returncode=0, stdout="CLI test\n", stderr="")
            if command == ("lms", "runtime", "ls"):
                return SimpleNamespace(returncode=0, stdout="runtime\n", stderr="")
            if command == ("lms", "server", "start"):
                return SimpleNamespace(returncode=0, stdout="", stderr="started\n")
            if command[:2] == ("lms", "load"):
                state["loaded"] = next(model for model in MODELS if model.model_key == command[2])
                return SimpleNamespace(returncode=0, stdout="loaded\n", stderr="")
            if command == ("lms", "ps", "--json"):
                model = state["loaded"]
                instance = {
                    "identifier": model.live_identifier,
                    "selectedVariant": model.selected_variant,
                    "contextLength": 8192,
                    "parallel": 1,
                    "vision": False,
                }
                return SimpleNamespace(returncode=0, stdout=json.dumps([instance]), stderr="")
            if command == ("lms", "unload", "--all"):
                state["loaded"] = None
                return SimpleNamespace(returncode=0, stdout="", stderr="")
            raise AssertionError(command)

        invoker = FakeInvoker({(MODELS[0].model_key, "selection"): '{"answer":[]}'})
        with tempfile.TemporaryDirectory() as parent, \
             patch("contact.gemma_contract_staircase.verify_artifact", side_effect=lambda model: {"model": model.model_key}) as verified, \
             patch("contact.gemma_contract_staircase.subprocess.run", side_effect=fake_run), \
             patch("contact.gemma_contract_staircase.LiveInvoker", side_effect=lambda model: invoker):
            summary = run_live(Path(parent) / "evidence")
        self.assertEqual([item["terminal_result"] for item in summary["models"]], ["contract_unreliable", "screen_pass"])
        self.assertEqual(verified.call_count, 2)
        self.assertEqual(len(invoker.calls), 5)
        self.assertGreaterEqual(commands.count(("lms", "unload", "--all")), 4)
        for model_summary in summary["models"]:
            receipt = model_summary["packet_receipt"]
            self.assertEqual(receipt["sampling_without_seed"], SAMPLING)
            self.assertFalse(receipt["adapter_attached"])
            self.assertFalse(receipt["projector_attached"])


if __name__ == "__main__":
    unittest.main()
