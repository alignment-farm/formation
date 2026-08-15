import tempfile
from pathlib import Path
import unittest

from contact.model_admission import (
    ANCHOR_S1_VECTORS,
    MODELS,
    SQLITE_COLD_VECTORS,
    Attempt,
    _score,
    _sqlite_report,
    family_label,
    run_model,
    schedule,
    terminal_label,
)


PYTHON_SOURCES = {
    "A-P1": """def join_pair(payload):
    if type(payload) is not list or len(payload) != 2 or type(payload[0]) is not str or type(payload[1]) is not str:
        raise ValueError
    return payload[0] + ':' + payload[1]""",
    "A-P2": """def require_ready(payload):
    if type(payload) is not str or payload != 'ready':
        raise ValueError
    return 'ready'""",
    "Python-cold": """def parse_limits(payload):
    if type(payload) is not dict or set(payload) != {'soft', 'hard'}:
        raise ValueError
    soft, hard = payload['soft'], payload['hard']
    if not isinstance(soft, int) or not isinstance(hard, int) or soft < 0 or hard < 0 or soft > hard:
        raise ValueError
    return soft, hard""",
    "Python-direct_rule": """def parse_revisions(payload):
    if type(payload) is not dict or set(payload) != {'artifact_revision', 'authority_revision'}:
        raise ValueError
    left, right = payload['artifact_revision'], payload['authority_revision']
    if type(left) is not int or type(right) is not int or left < 0 or right < 0:
        raise ValueError
    return left, right""",
}
SQL_SOURCES = {
    "A-S1": "SELECT label FROM devices WHERE enabled = 1 ORDER BY label;",
    "A-S2": "SELECT category, SUM(amount) FROM entries GROUP BY category ORDER BY category;",
    "SQLite-cold": "SELECT name FROM vessels WHERE id NOT IN (SELECT vessel_id FROM inspections) ORDER BY name;",
    "SQLite-direct_rule": "SELECT p.label FROM packages p WHERE NOT EXISTS (SELECT 1 FROM scans s WHERE s.package_id = p.id) ORDER BY p.label;",
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
            output = PYTHON_SOURCES.get(spec.call_id)
            if output is None:
                output = SQL_SOURCES.get(spec.call_id)
            if output is None:
                output = PYTHON_SOURCES.get(f"{spec.family}-{spec.condition}")
            if output is None:
                output = SQL_SOURCES[f"{spec.family}-{spec.condition}"]
        envelope = {"model": model.model_key, "seed": spec.seed}
        return Attempt(
            spec.logical_index, 1, spec.call_id, spec.family, spec.condition,
            spec.seed, spec.prompt, output, envelope,
            {"choices": [{"message": {"content": output}}]},
            "2026-08-15T00:00:00+00:00", "2026-08-15T00:00:01+00:00",
            1.0, None, None,
        )


class ModelAdmissionRunnerTests(unittest.TestCase):
    def test_frozen_model_specific_schedules(self):
        for model in MODELS:
            calls = schedule(model)
            self.assertEqual(len(calls), 16)
            self.assertEqual([item.logical_index for item in calls], list(range(1, 17)))
            self.assertEqual(tuple(dict.fromkeys(item.family for item in calls[4:])), model.family_order)
            self.assertEqual([item.seed for item in calls[:4]], [1001, 1002, 1003, 1004])

    def test_sqlite_null_boundary_is_distinct_from_ordinary(self):
        query = SQL_SOURCES["SQLite-cold"]
        report = _sqlite_report(query, SQLITE_COLD_VECTORS)
        self.assertEqual([item["passed"] for item in report["tests"]], [True, True, False, False])
        spec = next(item for item in schedule(MODELS[0]) if item.call_id == "SQLite-cold-1")
        self.assertEqual(_score(spec, query)[1], "boundary_miss")

    def test_sqlite_anchor_oracle(self):
        report = _sqlite_report(SQL_SOURCES["A-S1"], ANCHOR_S1_VECTORS)
        self.assertTrue(all(item["passed"] for item in report["tests"]))

    def test_family_and_terminal_classifiers(self):
        self.assertEqual(family_label(("boundary_miss",) * 3, ("full_pass",) * 3), "in_band")
        self.assertEqual(family_label(("full_pass",) * 3, ("ordinary_fail",) + ("full_pass",) * 2), "ordinary_fragile")
        self.assertEqual(family_label(("full_pass",) * 2 + ("boundary_miss",), ("full_pass",) * 3), "cold_ceiling")
        self.assertEqual(family_label(("boundary_miss",) * 3, ("boundary_miss",) * 3), "not_teachable")
        self.assertEqual(terminal_label({"Python": "in_band", "SQLite": "in_band"}), "admitted:Python,SQLite")
        self.assertEqual(terminal_label({"Python": "cold_ceiling", "SQLite": "cold_ceiling"}), "cold_ceiling")

    def test_full_fake_packet_admits_both_families(self):
        invoker = FakeInvoker()
        with tempfile.TemporaryDirectory() as parent:
            directory = Path(parent) / "model"
            summary = run_model(invoker, MODELS[0], directory)
            self.assertEqual(len(list(directory.glob("*.prompt.txt"))), 16)
        self.assertEqual(summary["terminal_result"], "admitted:Python,SQLite")
        self.assertEqual(summary["family_cells"], {"Python": "in_band", "SQLite": "in_band"})
        self.assertEqual(len(invoker.calls), 16)

    def test_anchor_failure_stops_without_family_cells(self):
        invoker = FakeInvoker(fail_first_anchor=True)
        with tempfile.TemporaryDirectory() as parent:
            summary = run_model(invoker, MODELS[1], Path(parent) / "model")
        self.assertEqual(summary["terminal_result"], "contract_unreliable")
        self.assertEqual(summary["family_cells"], {})
        self.assertEqual(len(invoker.calls), 1)


if __name__ == "__main__":
    unittest.main()
