from pathlib import Path
import tempfile
import unittest

from contact.sqlite_contact import (
    CASE_ORDER,
    CONDITION_ORDER,
    EXPLORATION,
    Attempt,
    TASKS,
    assemble_validation_prompt,
    classify_exploration,
    encode_rows,
    first_acquisition_index,
    mechanically_engaged,
    invoke_with_retry,
    score_query,
    run_protocol,
)


CORRECT = """SELECT c.name
FROM customers AS c
WHERE NOT EXISTS (
  SELECT 1 FROM orders AS o WHERE o.customer_id = c.id
)
ORDER BY c.name;"""
WRONG = """SELECT name FROM customers
WHERE id NOT IN (SELECT customer_id FROM orders)
ORDER BY name;"""


class SQLiteContactRunnerTests(unittest.TestCase):
    def test_frozen_schedule(self):
        self.assertEqual(CASE_ORDER, ("V2", "N1", "V1", "N2", "V3"))
        self.assertEqual(CONDITION_ORDER, ("cold", "raw", "lesson"))
        self.assertEqual(set(TASKS), {"V1", "V2", "V3", "N1", "N2"})

    def test_exploration_oracle(self):
        score = score_query(EXPLORATION, CORRECT)
        self.assertTrue(score.passed)
        self.assertEqual(encode_rows(score.rows), '[["Bex"],["Cy"]]')

    def test_mechanical_engagement(self):
        score = score_query(EXPLORATION, WRONG)
        self.assertTrue(mechanically_engaged(WRONG, score))
        self.assertEqual(score.rows, ())

    def test_exploration_classifications_and_acquisition(self):
        status, scores = classify_exploration((WRONG, CORRECT, WRONG))
        self.assertEqual(status, "engaged")
        self.assertEqual(first_acquisition_index((WRONG, CORRECT, WRONG), scores), 1)
        self.assertEqual(classify_exploration((CORRECT, WRONG, CORRECT))[0], "not_engaged")
        self.assertEqual(classify_exploration(("bad", WRONG, CORRECT))[0], "unstable")

    def test_all_oracles_with_known_queries(self):
        queries = {
            "V1": "SELECT p.label FROM packages p WHERE NOT EXISTS (SELECT 1 FROM scans s WHERE s.package_ref=p.id) ORDER BY p.label;",
            "V2": "SELECT a.handle FROM authors a WHERE NOT EXISTS (SELECT 1 FROM reviews r WHERE r.author_id=a.id) ORDER BY a.handle;",
            "V3": "SELECT p.number FROM ports p WHERE NOT EXISTS (SELECT 1 FROM reservations r WHERE r.port_number=p.number) ORDER BY p.number;",
            "N1": "SELECT id FROM jobs WHERE state NOT IN ('held','done') ORDER BY id;",
            "N2": "SELECT label FROM devices WHERE id NOT IN (SELECT device_id FROM leases WHERE device_id IS NOT NULL) ORDER BY label;",
        }
        for case_id, query in queries.items():
            with self.subTest(case_id=case_id):
                self.assertTrue(score_query(TASKS[case_id], query).passed)

    def test_extraction_refuses_non_select_and_multiple_statements(self):
        for output in ("", "```sql\nSELECT 1;\n```", "WITH x AS (SELECT 1) SELECT * FROM x", "PRAGMA table_info(x)", "SELECT 1; SELECT 2;"):
            with self.subTest(output=output):
                self.assertFalse(score_query(EXPLORATION, output).accepted_query)

    def test_n2_requires_exact_normalized_constraint(self):
        wrong_shape = "SELECT d.label FROM devices d WHERE NOT EXISTS (SELECT 1 FROM leases l WHERE l.device_id=d.id) ORDER BY d.label;"
        score = score_query(TASKS["N2"], wrong_shape)
        self.assertTrue(score.correct_rows)
        self.assertFalse(score.constraint_met)

    def test_native_integer_rows_do_not_equal_digit_strings(self):
        score = score_query(TASKS["V3"], "SELECT CAST(number AS TEXT) FROM ports WHERE number IN (8000,8002) ORDER BY number;")
        self.assertFalse(score.correct_rows)

    def test_offer_assembly_excludes_oracle_rows(self):
        prompt = assemble_validation_prompt(
            "raw", TASKS["V1"], EXPLORATION.prompt(), WRONG, "[]", ""
        )
        self.assertIn("SQLite rows:\n[]", prompt)
        self.assertNotIn('[["Bex"],["Cy"]]', prompt)
        lesson = assemble_validation_prompt(
            "lesson", TASKS["V1"], EXPLORATION.prompt(), WRONG, "[]", "model text"
        )
        self.assertIn("model text", lesson)
        self.assertNotIn(WRONG, lesson)

    def test_not_engaged_stops_after_three_calls(self):
        calls = []

        def invoke(prompt, logical_index, condition, case_id):
            calls.append((logical_index, condition, case_id))
            return fake_attempt(prompt, logical_index, condition, case_id, CORRECT)

        with tempfile.TemporaryDirectory() as parent:
            summary = run_protocol(invoke, Path(parent) / "run")
        self.assertEqual(summary["exploration_status"], "not_engaged")
        self.assertEqual(len(calls), 3)
        self.assertEqual(summary["validation"], [])

    def test_engaged_executes_exact_nineteen_call_schedule(self):
        calls = []
        known = {
            "V1": "SELECT p.label FROM packages p WHERE NOT EXISTS (SELECT 1 FROM scans s WHERE s.package_ref=p.id) ORDER BY p.label;",
            "V2": "SELECT a.handle FROM authors a WHERE NOT EXISTS (SELECT 1 FROM reviews r WHERE r.author_id=a.id) ORDER BY a.handle;",
            "V3": "SELECT p.number FROM ports p WHERE NOT EXISTS (SELECT 1 FROM reservations r WHERE r.port_number=p.number) ORDER BY p.number;",
            "N1": "SELECT id FROM jobs WHERE state NOT IN ('held','done') ORDER BY id;",
            "N2": "SELECT label FROM devices WHERE id NOT IN (SELECT device_id FROM leases WHERE device_id IS NOT NULL) ORDER BY label;",
        }

        def invoke(prompt, logical_index, condition, case_id):
            calls.append((logical_index, condition, case_id))
            if logical_index <= 3:
                output = WRONG
            elif logical_index == 4:
                output = "NULL in a NOT IN subquery makes the predicate unknown."
            else:
                output = known[case_id]
            return fake_attempt(prompt, logical_index, condition, case_id, output)

        with tempfile.TemporaryDirectory() as parent:
            run_dir = Path(parent) / "run"
            summary = run_protocol(invoke, run_dir)
            receipt_count = len(tuple(run_dir.glob("*.json")))
        self.assertEqual(len(calls), 19)
        self.assertEqual(calls[4:], [
            (index, condition, case_id)
            for index, (condition, case_id) in enumerate(
                ((condition, case_id) for condition in CONDITION_ORDER for case_id in CASE_ORDER),
                5,
            )
        ])
        self.assertEqual(summary["success_counts"], {"cold": 5, "raw": 5, "lesson": 5})
        self.assertEqual(receipt_count, 20)

    def test_empty_output_retry_retains_reason_link_and_no_resume(self):
        calls = 0

        def invoke(prompt, logical_index, condition, case_id):
            nonlocal calls
            calls += 1
            output = "" if calls == 1 else CORRECT
            return fake_attempt(prompt, logical_index, condition, case_id, output)

        attempts = invoke_with_retry(invoke, EXPLORATION.prompt(), 1, "exploration", "E1")
        self.assertEqual(len(attempts), 2)
        self.assertTrue(all(attempt.no_resume for attempt in attempts))
        self.assertEqual(attempts[0].retry_reason, "no_model_output")
        self.assertIsNone(attempts[0].retry_of_attempt)
        self.assertEqual(attempts[1].retry_reason, "no_model_output")
        self.assertEqual(attempts[1].retry_of_attempt, 1)


def fake_attempt(prompt, logical_index, condition, case_id, output):
    return Attempt(
        logical_index,
        1,
        condition,
        case_id,
        prompt,
        output,
        ("agent", "<exact-prompt>"),
        "/tmp/empty",
        True,
        "start",
        "end",
        0.1,
        0,
        "test-agent",
        True,
        None,
        None,
    )


if __name__ == "__main__":
    unittest.main()
