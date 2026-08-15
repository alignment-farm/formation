import unittest
from pathlib import Path
import tempfile

from contact.python_boundary_contact import (
    CASE_ORDER,
    CONDITION_ORDER,
    EXPLORATION_PROMPT,
    EXPLORATION_VECTORS,
    PROMPTS,
    VECTORS,
    assemble_prompt,
    classify_exploration,
    encode_report,
    first_acquisition_index,
    report_source,
    run_vector,
    run_protocol,
    validate_source,
)
from contact.sqlite_contact import Attempt


ISINSTANCE_LIMITS = """def parse_limits(payload):
    if not isinstance(payload, dict) or set(payload) != {"soft", "hard"}:
        raise ValueError
    soft, hard = payload["soft"], payload["hard"]
    if not isinstance(soft, int) or not isinstance(hard, int):
        raise ValueError
    if soft < 0 or hard < 0 or soft > hard:
        raise ValueError
    return soft, hard"""
EXACT_LIMITS = ISINSTANCE_LIMITS.replace(
    "not isinstance(soft, int) or not isinstance(hard, int)",
    "type(soft) is not int or type(hard) is not int",
)
EXACT_SOURCES = {
    "V1": """def parse_revisions(payload):
    if type(payload) is not dict or set(payload) != {'artifact_revision', 'authority_revision'}:
        raise ValueError
    left, right = payload['artifact_revision'], payload['authority_revision']
    if type(left) is not int or type(right) is not int or left < 0 or right < 0:
        raise ValueError
    return left, right""",
    "V2": """def parse_window(payload):
    if type(payload) is not list or len(payload) != 2:
        raise ValueError
    low, high = payload
    if type(low) is not int or type(high) is not int or low > high:
        raise ValueError
    return low, high""",
    "V3": """def total_counts(payload):
    if type(payload) is not dict or set(payload) != {'primary', 'secondary'}:
        raise ValueError
    left, right = payload['primary'], payload['secondary']
    if type(left) is not int or type(right) is not int or left < 0 or right < 0:
        raise ValueError
    return left + right""",
    "N1": """def parse_feature_flags(payload):
    if type(payload) is not dict or set(payload) != {'audit', 'cache'}:
        raise ValueError
    audit, cache = payload['audit'], payload['cache']
    if type(audit) is not bool or type(cache) is not bool:
        raise ValueError
    return audit, cache""",
    "N2": """def parse_gate(payload):
    if type(payload) is not tuple or len(payload) != 2:
        raise ValueError
    enabled, attempts = payload
    if type(enabled) is not bool or type(attempts) is not int or attempts < 0:
        raise ValueError
    return enabled, attempts""",
}


class FakeInvoker:
    def __init__(self, engaged=True):
        self.engaged = engaged
        self.calls = []

    def __call__(self, prompt, logical_index, condition, case_id):
        self.calls.append((logical_index, condition, case_id, prompt))
        if condition == "exploration":
            output = ISINSTANCE_LIMITS if self.engaged else EXACT_LIMITS
        elif condition == "lesson_authorship":
            output = "Require exact int values because bool is an int subclass."
        else:
            output = EXACT_SOURCES[case_id]
        return Attempt(
            logical_index, 1, condition, case_id, prompt, output,
            ("agent", "<exact-prompt>"), "/empty", True,
            "2026-08-15T00:00:00+00:00", "2026-08-15T00:00:01+00:00",
            1.0, 0, "fake", True, None, None,
        )


class PythonBoundaryContactRunnerTests(unittest.TestCase):
    def test_frozen_schedule_and_vector_counts(self):
        self.assertEqual(CASE_ORDER, ("V2", "N1", "V1", "N2", "V3"))
        self.assertEqual(CONDITION_ORDER, ("cold", "raw", "lesson"))
        self.assertEqual(len(EXPLORATION_VECTORS), 24)
        self.assertEqual(
            {case_id: len(vectors) for case_id, vectors in VECTORS.items()},
            {"V1": 18, "V2": 19, "V3": 18, "N1": 16, "N2": 17},
        )

    def test_vector_ids_are_in_normative_order(self):
        self.assertEqual(
            [vector.test_id for vector in EXPLORATION_VECTORS],
            [f"E-O{index:02d}" for index in range(1, 22)]
            + [f"E-H{index:02d}" for index in range(1, 4)],
        )
        for case_id, vectors in VECTORS.items():
            self.assertEqual(
                [vector.test_id for vector in vectors],
                [f"{case_id}-{index:02d}" for index in range(1, len(vectors) + 1)],
            )

    def test_isinstance_behavior_engages_and_exact_type_passes(self):
        ambiguous = report_source(ISINSTANCE_LIMITS, "E1")
        exact = report_source(EXACT_LIMITS, "E1")
        self.assertEqual(classify_exploration((ambiguous, exact, ambiguous)), "engaged")
        self.assertEqual(classify_exploration((exact, ambiguous, exact)), "not_engaged")
        self.assertEqual(first_acquisition_index((ambiguous, exact, ambiguous)), 1)

    def test_report_schema_and_compact_encoding(self):
        report = report_source(ISINSTANCE_LIMITS, "E1")
        self.assertEqual(
            set(report), {"function_name", "python_version", "source_sha256", "tests"}
        )
        self.assertEqual(
            set(report["tests"][0]),
            {
                "exception_type", "expected", "input_repr", "mutated", "passed",
                "process_status", "returned_repr", "stderr", "stdout", "test_id",
            },
        )
        encoded = encode_report(report)
        self.assertNotIn("\n", encoded)
        self.assertNotIn('"function_name": ', encoded)

    def test_source_gate_refuses_unsafe_or_wrong_shape(self):
        cases = (
            "```python\ndef parse_limits(payload): return (0, 0)\n```",
            "import os\ndef parse_limits(payload): return (0, 0)",
            "def other(payload): return (0, 0)",
            "def parse_limits(x): return (0, 0)",
            "def parse_limits(payload):\n def nested(): pass\n return (0, 0)",
            "def parse_limits(payload): return payload.__class__",
            "async def parse_limits(payload): return (0, 0)",
        )
        for source in cases:
            with self.subTest(source=source):
                self.assertIsNotNone(validate_source(source, "parse_limits"))

    def test_refused_source_cannot_engage(self):
        report = report_source("bad", "E1")
        self.assertTrue(all(item["process_status"] == "refused" for item in report["tests"]))
        self.assertEqual(classify_exploration((report, report, report)), "unstable")

    def test_cpu_limit_is_reported_as_timeout(self):
        source = "def parse_limits(payload):\n    while True:\n        pass"
        result = run_vector(source, "parse_limits", EXPLORATION_VECTORS[0])
        self.assertEqual(result["process_status"], "timeout")

    def test_raw_and_lesson_offers_separate_sources(self):
        report = encode_report(report_source(ISINSTANCE_LIMITS, "E1"))
        raw = assemble_prompt("raw", "V1", ISINSTANCE_LIMITS, report, "")
        self.assertIn(ISINSTANCE_LIMITS, raw)
        self.assertIn('"E-H01"', raw)
        lesson = assemble_prompt("lesson", "V1", ISINSTANCE_LIMITS, report, "lesson")
        self.assertIn("lesson", lesson)
        self.assertNotIn(ISINSTANCE_LIMITS, lesson)
        self.assertNotIn('"E-H01"', lesson)
        self.assertEqual(assemble_prompt("cold", "V1", "", "", ""), PROMPTS["V1"])

    def test_not_engaged_stops_after_three_calls(self):
        invoker = FakeInvoker(engaged=False)
        with tempfile.TemporaryDirectory() as parent:
            evidence = Path(parent) / "evidence"
            summary = run_protocol(invoker, evidence)
        self.assertEqual(summary["exploration_status"], "not_engaged")
        self.assertEqual(summary["contact_status"], "stopped")
        self.assertEqual(len(invoker.calls), 3)

    def test_engaged_protocol_runs_frozen_nineteen_call_schedule(self):
        invoker = FakeInvoker(engaged=True)
        with tempfile.TemporaryDirectory() as parent:
            evidence = Path(parent) / "evidence"
            summary = run_protocol(invoker, evidence)
            self.assertTrue((evidence / "summary.json").is_file())
            self.assertEqual(len(list(evidence.glob("*.prompt.txt"))), 19)
        self.assertEqual(summary["contact_status"], "complete")
        self.assertEqual(summary["success_counts"], {"cold": 5, "raw": 5, "lesson": 5})
        self.assertEqual(
            [(condition, case) for _, condition, case, _ in invoker.calls[4:]],
            [(condition, case) for condition in CONDITION_ORDER for case in CASE_ORDER],
        )


if __name__ == "__main__":
    unittest.main()
