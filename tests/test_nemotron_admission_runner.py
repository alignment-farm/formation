from dataclasses import asdict
import hashlib
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from contact.model_admission import Attempt
from contact.nemotron_admission import (
    ANCHOR_P1_PROMPT,
    ANCHOR_P1_VECTORS,
    ANCHOR_P2_PROMPT,
    ANCHOR_P2_VECTORS,
    ANCHOR_S1_PROMPT,
    ANCHOR_S1_VECTORS,
    ANCHOR_S2_PROMPT,
    ANCHOR_S2_VECTORS,
    LIVE_IDENTIFIER,
    MODEL,
    PYTHON_COLD_PROMPT,
    PYTHON_COLD_VECTORS,
    PYTHON_DIRECT_PROMPT,
    PYTHON_DIRECT_VECTORS,
    SAMPLING,
    SQLITE_COLD_PROMPT,
    SQLITE_COLD_VECTORS,
    SQLITE_DIRECT_PROMPT,
    SQLITE_DIRECT_VECTORS,
    LiveInvoker,
    _python_report,
    _query_gate,
    _score,
    _sqlite_report,
    load_command,
    run_model,
    schedule,
    validate_loaded_instance,
    validate_source,
)


PYTHON_SOURCES = {
    "C-P1": """def combine_labels(payload):
    if type(payload) is not tuple or len(payload) != 2 or not all(type(item) is str for item in payload):
        raise ValueError
    return payload[0] + '/' + payload[1]""",
    "C-P2": """def accept_mode(payload):
    if type(payload) is not str or payload != 'active':
        raise ValueError
    return 'active'""",
    "Python-cold": """def parse_versions(payload):
    if type(payload) is not dict or set(payload) != {'client_version', 'server_version'}:
        raise ValueError
    left, right = payload['client_version'], payload['server_version']
    if not isinstance(left, int) or not isinstance(right, int) or left < 0 or right < 0 or left > right:
        raise ValueError
    return left, right""",
    "Python-direct_rule": """def parse_slots(payload):
    if type(payload) is not dict or set(payload) != {'used_slots', 'total_slots'}:
        raise ValueError
    left, right = payload['used_slots'], payload['total_slots']
    if type(left) is not int or type(right) is not int or left < 0 or right < 0 or left > right:
        raise ValueError
    return left, right""",
}
SQL_SOURCES = {
    "C-S1": "SELECT hostname FROM endpoints WHERE online = 1 ORDER BY hostname;",
    "C-S2": "SELECT sensor, SUM(value) FROM readings GROUP BY sensor ORDER BY sensor;",
    "SQLite-cold": "SELECT title FROM volumes WHERE id NOT IN (SELECT volume_id FROM loans) ORDER BY title;",
    "SQLite-direct_rule": "SELECT d.code FROM depots d WHERE NOT EXISTS (SELECT 1 FROM shipments s WHERE s.depot_id = d.id) ORDER BY d.code;",
}


class FakeInvoker:
    def __init__(self, fail_first_anchor=False):
        self.calls = []
        self.fail_first_anchor = fail_first_anchor

    def __call__(self, model, spec):
        self.calls.append(spec)
        if self.fail_first_anchor and spec.logical_index == 1:
            output = "bad"
        else:
            output = PYTHON_SOURCES.get(spec.call_id) or SQL_SOURCES.get(spec.call_id)
            output = output or PYTHON_SOURCES.get(f"{spec.family}-{spec.condition}")
            output = output or SQL_SOURCES[f"{spec.family}-{spec.condition}"]
        return Attempt(
            spec.logical_index,
            1,
            spec.call_id,
            spec.family,
            spec.condition,
            spec.seed,
            spec.prompt,
            output,
            {"model": model.model_key, "seed": spec.seed},
            {"choices": [{"message": {"content": output}}]},
            "2026-08-15T00:00:00+00:00",
            "2026-08-15T00:00:01+00:00",
            1.0,
            None,
            None,
        )


class NemotronAdmissionRunnerTests(unittest.TestCase):
    def test_frozen_schedule_and_disclosed_prompts(self):
        calls = schedule()
        self.assertEqual(len(calls), 16)
        self.assertEqual([call.logical_index for call in calls], list(range(1, 17)))
        self.assertEqual([call.seed for call in calls[:4]], [2001, 2002, 2003, 2004])
        self.assertEqual(tuple(dict.fromkeys(call.family for call in calls[4:])), MODEL.family_order)
        self.assertEqual([call.seed for call in calls[4:]], [2101, 2102, 2103] * 4)
        self.assertIn("all, any", ANCHOR_P1_PROMPT)
        self.assertIn("yield from", ANCHOR_P1_PROMPT)
        self.assertIn("positional-only", ANCHOR_P1_PROMPT)

    def test_every_prompt_is_byte_equal_to_normative_appendix(self):
        appendix = (Path(__file__).parents[1] / "docs" / "NEMOTRON_ADMISSION_SUCCESSOR_VECTORS.md").read_text()
        prompts = {
            "Anchor C-P1": ANCHOR_P1_PROMPT,
            "Anchor C-P2": ANCHOR_P2_PROMPT,
            "Anchor C-S1": ANCHOR_S1_PROMPT,
            "Anchor C-S2": ANCHOR_S2_PROMPT,
            "Python cold target": PYTHON_COLD_PROMPT,
            "Python direct-rule target": PYTHON_DIRECT_PROMPT,
            "SQLite cold target": SQLITE_COLD_PROMPT,
            "SQLite direct-rule target": SQLITE_DIRECT_PROMPT,
        }
        for heading, prompt in prompts.items():
            section = appendix.split("## " + heading, 1)[1]
            documented = section.split("```text\n", 1)[1].split("\n```", 1)[0]
            self.assertEqual(prompt, documented, heading)

    def test_all_vector_fields_match_frozen_snapshots(self):
        vectors = {
            "C-P1": (ANCHOR_P1_VECTORS, "ed9eb43b256fbe2bc403fdfcf7977c63bb82e02c7b6d57f54192159ae0e9ca44"),
            "C-P2": (ANCHOR_P2_VECTORS, "516b80a5933a4b491cb33d7282465cda0bd5d4924f7c33ac6649b91fe37aef32"),
            "Python-cold": (PYTHON_COLD_VECTORS, "6304faf8afdf2910c3bb5376d5e50e68545666260a6883f610609b046d0017cc"),
            "Python-direct": (PYTHON_DIRECT_VECTORS, "737e6ad88f19703e9635d241b184cc364e2354880d1395de0c6b8713c372bfe9"),
            "C-S1": (ANCHOR_S1_VECTORS, "1844f60b24ba02674f8534d779584dddf7f69e3121ea24a4e541d63960695176"),
            "C-S2": (ANCHOR_S2_VECTORS, "befc242bfdb5d14f559501c0b3da5a536b90d51901537008cce3c279ab3088b1"),
            "SQLite-cold": (SQLITE_COLD_VECTORS, "e9cfe02c878ea3322a601c335bc23453ab24ace1f5f5e66870dbe7047594fc16"),
            "SQLite-direct": (SQLITE_DIRECT_VECTORS, "03d670a5029c969092adf1399957cf8ef1da203f4925a9b9a6b4f04f1df43305"),
        }
        for name, (items, expected) in vectors.items():
            encoded = json.dumps([asdict(item) for item in items], sort_keys=True, separators=(",", ":")).encode()
            self.assertEqual(hashlib.sha256(encoded).hexdigest(), expected, name)

    def test_disclosed_all_builtin_executes_in_fresh_child(self):
        report = _python_report(PYTHON_SOURCES["C-P1"], "combine_labels", ANCHOR_P1_VECTORS)
        self.assertIsNone(report["gate_refusal"])
        self.assertTrue(all(item["passed"] for item in report["tests"]))

    def test_exact_source_gate_signature_and_tree(self):
        self.assertEqual(validate_source("def combine_labels(payload=None):\n    return ''", "combine_labels"), "exact_payload_signature_required")
        self.assertEqual(validate_source("def combine_labels(payload, /):\n    return ''", "combine_labels"), "exact_payload_signature_required")
        self.assertEqual(validate_source("def combine_labels(payload):\n    yield from payload", "combine_labels"), "disallowed_syntax")
        mixed = "def combine_labels(payload):\n    def helper():\n        import os\n    return ''"
        self.assertEqual(validate_source(mixed, "combine_labels"), "disallowed_syntax")
        self.assertEqual(validate_source("```python\ndef combine_labels(payload):\n    return ''\n```", "combine_labels"), "markdown_fence")

    def test_python_class_labels_drive_boundary_result(self):
        report = _python_report(PYTHON_SOURCES["Python-cold"], "parse_versions", PYTHON_COLD_VECTORS)
        self.assertEqual(sum(bool(item["held"]) for item in report["tests"]), 3)
        spec = next(call for call in schedule() if call.call_id == "Python-cold-1")
        self.assertEqual(_score(spec, PYTHON_SOURCES["Python-cold"])[1], "boundary_miss")
        direct = next(call for call in schedule() if call.call_id == "Python-direct_rule-1")
        self.assertEqual(_score(direct, PYTHON_SOURCES["Python-direct_rule"])[1], "full_pass")

    def test_sqlite_gate_boundary_and_direct_constraint(self):
        self.assertIsNone(_query_gate(" SELECT*FROM volumes"))
        self.assertEqual(_query_gate("WITH rows AS (SELECT 1) SELECT * FROM rows"), "select_required")
        report = _sqlite_report(SQL_SOURCES["SQLite-cold"], SQLITE_COLD_VECTORS)
        self.assertEqual([item["passed"] for item in report["tests"]], [True, True, False, False])
        cold = next(call for call in schedule() if call.call_id == "SQLite-cold-1")
        self.assertEqual(_score(cold, SQL_SOURCES["SQLite-cold"])[1], "boundary_miss")
        direct = next(call for call in schedule() if call.call_id == "SQLite-direct_rule-1")
        left_join = "SELECT d.code FROM depots d LEFT JOIN shipments s ON s.depot_id = d.id WHERE s.id IS NULL ORDER BY d.code;"
        self.assertEqual(_score(direct, left_join)[1], "ordinary_fail")
        split_keyword = SQL_SOURCES["SQLite-direct_rule"].replace("NOT EXISTS", "NOT\nEXISTS")
        self.assertEqual(_score(direct, split_keyword)[1], "full_pass")

    def test_full_fake_packet_admits_both_families(self):
        invoker = FakeInvoker()
        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "nemotron"
            summary = run_model(invoker, directory)
            self.assertEqual(len(list(directory.glob("*.prompt.txt"))), 16)
        self.assertEqual(summary["terminal_result"], "admitted:Python,SQLite")
        self.assertEqual(summary["family_cells"], {"Python": "in_band", "SQLite": "in_band"})
        self.assertEqual(len(invoker.calls), 16)

    def test_empty_output_gets_one_linked_retry(self):
        class RetryingInvoker(FakeInvoker):
            def __call__(self, model, spec):
                attempt = super().__call__(model, spec)
                if len(self.calls) == 1:
                    return Attempt(
                        attempt.logical_index, attempt.attempt_index, attempt.call_id,
                        attempt.family, attempt.condition, attempt.seed, attempt.prompt,
                        "", attempt.request_envelope, {"choices": [{"message": {"content": ""}}]},
                        attempt.started_at, attempt.ended_at, attempt.elapsed_seconds,
                        None, None,
                    )
                return attempt

        invoker = RetryingInvoker()
        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "nemotron"
            run_model(invoker, directory)
            first = json.loads((directory / "01-C-P1-a1.json").read_text())
            second = json.loads((directory / "01-C-P1-a2.json").read_text())
        self.assertEqual(len(invoker.calls), 17)
        self.assertEqual(first["call_label"], "retry_pending")
        self.assertEqual(first["retry_reason"], "no_model_output")
        self.assertEqual(second["retry_of_attempt"], 1)

    def test_model_load_identity_is_exact(self):
        self.assertEqual(MODEL.model_key, "nvidia/nemotron-3-nano-4b")
        self.assertEqual(MODEL.selected_variant, "nvidia/nemotron-3-nano-4b@q4_k_m")
        self.assertEqual(
            load_command(),
            (
                "lms", "load", MODEL.model_key, "--gpu", "max",
                "--context-length", "8192", "--parallel", "1",
                "--no-speculative-draft-mtp", "--identifier", LIVE_IDENTIFIER, "-y",
            ),
        )
        instance = {
            "identifier": LIVE_IDENTIFIER,
            "selectedVariant": MODEL.selected_variant,
            "contextLength": 8192,
            "parallel": 1,
            "vision": False,
        }
        self.assertIs(validate_loaded_instance([instance]), instance)
        with self.assertRaisesRegex(ValueError, "exact_text_only_model_load_required"):
            validate_loaded_instance([{**instance, "vision": True}])

    def test_live_request_has_only_frozen_inference_fields(self):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self):
                return json.dumps({"choices": [{"message": {"content": "answer"}}]}).encode()

        spec = schedule()[0]
        with patch("contact.nemotron_admission.urlopen", return_value=Response()) as opened:
            attempt = LiveInvoker()(MODEL, spec)
        request = opened.call_args.args[0]
        envelope = json.loads(request.data)
        self.assertEqual(
            set(envelope),
            {"model", "messages", "seed", *SAMPLING.keys()},
        )
        self.assertEqual(envelope["model"], LIVE_IDENTIFIER)
        self.assertEqual(envelope["messages"], [{"role": "user", "content": spec.prompt}])
        self.assertEqual(envelope["seed"], 2001)
        self.assertEqual({key: envelope[key] for key in SAMPLING}, SAMPLING)
        self.assertEqual(attempt.output, "answer")

    def test_anchor_failure_stops_before_targets(self):
        invoker = FakeInvoker(fail_first_anchor=True)
        with tempfile.TemporaryDirectory() as parent:
            summary = run_model(invoker, Path(parent) / "nemotron")
        self.assertEqual(summary["terminal_result"], "contract_unreliable")
        self.assertEqual(summary["family_cells"], {})
        self.assertEqual(len(invoker.calls), 1)


if __name__ == "__main__":
    unittest.main()
