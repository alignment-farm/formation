from dataclasses import asdict
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from contact.structured_output_interface_trial import (
    MODELS,
    PAIR_LABELS,
    SAMPLING,
    TASKS,
    Attempt,
    LiveInvoker,
    assert_pair_isolation,
    call_state,
    request_envelope,
    run_live,
    run_model,
    schedule,
)


CORRECT = {"selection": '{"answer":["alder","clover"]}', "ordered_update": '{"answer":29}'}


class FakeInvoker:
    def __init__(self, outputs=None, empty_once=None):
        self.outputs = {} if outputs is None else outputs
        self.empty_once = empty_once
        self.calls = []

    def __call__(self, model, call):
        key = (model.model_key, call.task.task_id, call.condition)
        seen = sum(item == key for item in self.calls)
        self.calls.append(key)
        output = self.outputs.get(key, CORRECT[call.task.task_id])
        if self.empty_once == key and seen == 0:
            output = ""
        envelope = request_envelope(model, call)
        return Attempt(
            call.logical_index, 1, call.call_id, call.task.task_id, call.condition,
            call.task.seed, model.model_key, model.live_identifier, call.task.prompt,
            output, envelope, {"choices": [{"message": {"content": output}}]},
            "2026-08-15T00:00:00+00:00", "2026-08-15T00:00:01+00:00", 1.0,
        )


class StructuredOutputInterfaceTrialTests(unittest.TestCase):
    def test_prompts_schemas_oracles_and_seeds_match_charter(self):
        document = (Path(__file__).parents[1] / "docs" / "STRUCTURED_OUTPUT_INTERFACE_TRIAL.md").read_text()
        headings = ("Task A: conjunctive selection", "Task B: ordered state update")
        for task, heading in zip(TASKS, headings, strict=True):
            section = document.split("## " + heading, 1)[1].split("## ", 1)[0]
            prompt = section.split("Exact prompt for both conditions:\n\n```text\n", 1)[1].split("\n```", 1)[0]
            oracle = json.loads(section.split("Oracle answer:\n\n```json\n", 1)[1].split("\n```", 1)[0])
            schema = json.loads(section.split("Exact constrained `response_format`:\n\n```json\n", 1)[1].split("\n```", 1)[0])
            self.assertEqual(task.prompt, prompt)
            self.assertEqual(task.oracle_answer, oracle)
            self.assertEqual(task.response_format, schema)
        self.assertEqual([task.seed for task in TASKS], [4001, 4002])

    def test_models_and_sampling_are_inherited_exactly(self):
        self.assertEqual([model.model_key for model in MODELS], ["google/gemma-3-270m", "google/gemma-3-1b"])
        self.assertEqual(SAMPLING, {
            "frequency_penalty": 0, "max_tokens": 256, "presence_penalty": 0,
            "repeat_penalty": 1, "stream": False, "temperature": 0.2,
            "top_k": 40, "top_p": 0.95,
        })

    def test_request_isolation_and_absent_bare_field(self):
        for model in MODELS:
            for task in TASKS:
                assert_pair_isolation(model, task)
                calls = {call.condition: call for call in schedule(model) if call.task == task}
                bare = request_envelope(model, calls["bare"])
                constrained = request_envelope(model, calls["constrained"])
                self.assertNotIn("response_format", bare)
                self.assertEqual(constrained["response_format"], task.response_format)
                constrained.pop("response_format")
                self.assertEqual(bare, constrained)

    def test_schedule_reverses_1b_but_pair_keys_remain_unique(self):
        self.assertEqual([call.condition for call in schedule(MODELS[0])], ["bare", "constrained", "bare", "constrained"])
        self.assertEqual([call.condition for call in schedule(MODELS[1])], ["constrained", "bare", "constrained", "bare"])
        for model in MODELS:
            keys = [(call.task.task_id, call.condition) for call in schedule(model)]
            self.assertEqual(len(keys), len(set(keys)))

    def test_all_nine_pair_transitions_are_distinct(self):
        self.assertEqual(len(PAIR_LABELS), 9)
        self.assertEqual(len(set(PAIR_LABELS.values())), 9)
        self.assertEqual(call_state("gate_fail"), "invalid")
        self.assertEqual(call_state("wrong_answer"), "valid_wrong")
        self.assertEqual(call_state("full_pass"), "valid_correct")

    def test_run_model_executes_all_calls_and_orders_pairs_bare_first(self):
        outputs = {
            (MODELS[0].model_key, "selection", "bare"): "not json",
            (MODELS[0].model_key, "selection", "constrained"): CORRECT["selection"],
            (MODELS[0].model_key, "ordered_update", "bare"): '{"answer":30}',
            (MODELS[0].model_key, "ordered_update", "constrained"): '{"answer":31}',
        }
        invoker = FakeInvoker(outputs)
        with tempfile.TemporaryDirectory() as parent:
            summary = run_model(invoker, MODELS[0], Path(parent) / "model")
        self.assertEqual(len(invoker.calls), 4)
        self.assertEqual([pair["pair_label"] for pair in summary["pairs"]], ["invalid_to_correct", "wrong_to_wrong"])
        self.assertEqual(summary["pairs"][0]["bare_call_state"], "invalid")
        self.assertEqual(summary["pairs"][0]["constrained_call_state"], "valid_correct")

        reverse = FakeInvoker(outputs)
        with tempfile.TemporaryDirectory() as parent:
            reversed_summary = run_model(reverse, MODELS[1], Path(parent) / "model")
        self.assertEqual(reverse.calls[0][2], "constrained")
        self.assertEqual(reversed_summary["pairs"][0]["bare_call_id"], "selection-bare")
        self.assertEqual(reversed_summary["pairs"][0]["constrained_call_id"], "selection-constrained")

    def test_empty_retries_once_and_preserves_condition_receipts(self):
        key = (MODELS[1].model_key, "selection", "constrained")
        invoker = FakeInvoker(empty_once=key)
        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "model"
            run_model(invoker, MODELS[1], directory)
            first = json.loads((directory / "01-selection-constrained-a1.json").read_text())
            second = json.loads((directory / "01-selection-constrained-a2.json").read_text())
        self.assertEqual(len(invoker.calls), 5)
        self.assertEqual(first["call_label"], "retry_pending")
        self.assertIsNone(first["call_state"])
        self.assertEqual(second["call_state"], "valid_correct")
        self.assertEqual(first["response_format"], TASKS[0].response_format)

    def test_post_storage_request_drift_refuses(self):
        class Drifting(FakeInvoker):
            def __call__(self, model, call):
                attempt = super().__call__(model, call)
                return Attempt(**{**asdict(attempt), "request_envelope": {**attempt.request_envelope, "temperature": 0.9}})

        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "model"
            summary = run_model(Drifting(), MODELS[0], directory)
            record = json.loads((directory / "01-selection-bare-a1.json").read_text())
        self.assertEqual(summary["trial_status"], "aborted")
        self.assertEqual(summary["abort_reason"], "request_contract_rejected")
        self.assertIsNone(record["call_label"])
        self.assertIsNone(record["call_state"])
        self.assertEqual(summary["pairs"], [])

    def test_live_invoker_scores_content_not_reasoning(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *_): return False
            def read(self):
                return json.dumps({"choices": [{"message": {"content": None, "reasoning_content": CORRECT["selection"]}}]}).encode()

        call = schedule(MODELS[0])[0]
        with patch("contact.structured_output_interface_trial.urlopen", return_value=Response()):
            attempt = LiveInvoker(MODELS[0])(MODELS[0], call)
        self.assertEqual(attempt.output, "")
        self.assertNotIn("response_format", attempt.request_envelope)

        class NonString(Response):
            def read(self):
                return json.dumps({"choices": [{"message": {"content": []}}]}).encode()

        from contact.structured_output_interface_trial import ContactAbort
        with patch("contact.structured_output_interface_trial.urlopen", return_value=NonString()):
            with self.assertRaises(ContactAbort) as caught:
                LiveInvoker(MODELS[0])(MODELS[0], call)
        self.assertEqual(caught.exception.reason, "provider_envelope_invalid")
        self.assertIsNotNone(caught.exception.attempt)

    def test_provider_abort_retains_nullable_attempt_and_stops(self):
        class Broken(FakeInvoker):
            def __call__(self, model, call):
                from contact.structured_output_interface_trial import ContactAbort
                attempt = super().__call__(model, call)
                raise ContactAbort("provider_envelope_invalid", attempt)

        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "model"
            summary = run_model(Broken(), MODELS[0], directory)
            record = json.loads((directory / "01-selection-bare-a1.json").read_text())
        self.assertEqual(summary["trial_status"], "aborted")
        self.assertEqual(summary["abort_reason"], "provider_envelope_invalid")
        self.assertIsNone(record["gate_refusal"])
        self.assertIsNone(record["decoded_answer"])
        self.assertEqual(record["oracle_answer"], ["alder", "clover"])

    def test_abort_on_second_empty_attempt_retains_first_retry(self):
        from contact.structured_output_interface_trial import ContactAbort

        class EmptyThenAbort(FakeInvoker):
            def __call__(self, model, call):
                attempt = super().__call__(model, call)
                if len(self.calls) == 1:
                    return Attempt(**{**asdict(attempt), "output": ""})
                raise ContactAbort("infrastructure_invalid", attempt)

        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "model"
            summary = run_model(EmptyThenAbort(), MODELS[0], directory)
            first = json.loads((directory / "01-selection-bare-a1.json").read_text())
            second = json.loads((directory / "01-selection-bare-a2.json").read_text())
        self.assertEqual(summary["abort_reason"], "infrastructure_invalid")
        self.assertEqual(first["call_label"], "retry_pending")
        self.assertEqual(first["retry_reason"], "no_model_content")
        self.assertIsNone(second["call_label"])
        self.assertEqual(second["retry_of_attempt"], 1)

    def test_whitespace_does_not_retry_and_second_empty_is_terminal_invalid(self):
        whitespace_key = (MODELS[0].model_key, "selection", "bare")
        whitespace = FakeInvoker({whitespace_key: "   "})
        with tempfile.TemporaryDirectory() as parent:
            result = run_model(whitespace, MODELS[0], Path(parent) / "white")
        self.assertEqual(len(whitespace.calls), 4)
        self.assertEqual(result["calls"][0]["call_state"], "invalid")

        class TwoEmpty(FakeInvoker):
            def __call__(self, model, call):
                attempt = super().__call__(model, call)
                if call.logical_index == 1:
                    return Attempt(**{**asdict(attempt), "output": ""})
                return attempt

        two_empty = TwoEmpty()
        with tempfile.TemporaryDirectory() as parent:
            result = run_model(two_empty, MODELS[0], Path(parent) / "empty")
        self.assertEqual(len(two_empty.calls), 5)
        self.assertEqual(result["calls"][0]["call_state"], "invalid")
        self.assertEqual(result["calls"][0]["gate_refusal"], "empty_output")

    def test_live_orchestration_orders_pairs_and_records_late_infrastructure_abort(self):
        state = {"loaded": None}
        invoker = FakeInvoker()

        def fake_run(command, **_):
            if command == ("lms", "--version"):
                return SimpleNamespace(returncode=0, stdout="CLI test\n", stderr="")
            if command == ("lms", "runtime", "ls"):
                return SimpleNamespace(returncode=0, stdout="runtime\n", stderr="")
            if command == ("lms", "server", "start"):
                return SimpleNamespace(returncode=0, stdout="", stderr="started\n")
            if command == ("lms", "unload", "--all"):
                state["loaded"] = None
                return SimpleNamespace(returncode=0, stdout="", stderr="")
            if command[:2] == ("lms", "load"):
                model = next(item for item in MODELS if item.model_key == command[2])
                if model == MODELS[1]:
                    raise RuntimeError("fake load failure")
                state["loaded"] = model
                return SimpleNamespace(returncode=0, stdout="loaded\n", stderr="")
            if command == ("lms", "ps", "--json"):
                model = state["loaded"]
                value = [{"identifier": model.live_identifier, "selectedVariant": model.selected_variant,
                          "contextLength": 8192, "parallel": 1, "vision": False}]
                return SimpleNamespace(returncode=0, stdout=json.dumps(value), stderr="")
            raise AssertionError(command)

        with tempfile.TemporaryDirectory() as parent, \
             patch("contact.structured_output_interface_trial.verify_artifact", side_effect=lambda model: {"model": model.model_key}), \
             patch("contact.structured_output_interface_trial.subprocess.run", side_effect=fake_run), \
             patch("contact.structured_output_interface_trial.LiveInvoker", side_effect=lambda model: invoker):
            summary = run_live(Path(parent) / "evidence")
        self.assertEqual(summary["trial_status"], "aborted")
        self.assertEqual(summary["abort_reason"], "infrastructure_invalid")
        self.assertEqual(len(summary["pairs"]), 2)
        self.assertEqual([pair["task_id"] for pair in summary["pairs"]], ["selection", "ordered_update"])
        self.assertEqual(summary["models"][1]["calls"], [])


if __name__ == "__main__":
    unittest.main()
