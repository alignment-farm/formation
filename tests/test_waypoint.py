import contextlib
from dataclasses import replace
import io
from pathlib import Path
import unittest

from tools.waypoint import Proposal, inspect_proposal, load_route_state, main


ROOT = Path(__file__).parents[1]
STATE = ROOT / "tools" / "waypoint_route.json"


def proposal(**changes):
    values = {
        "summary": "Implement exact environment action application",
        "kind": "lifecycle_step",
        "target": "environment_application",
        "success": "consequence_intake",
        "failure": "environment_application",
        "claim": "wire",
    }
    values.update(changes)
    return Proposal(**values)


class WaypointTests(unittest.TestCase):
    def setUp(self):
        self.state = load_route_state(STATE)

    def test_reviewed_route_is_current(self):
        self.assertEqual(self.state.current_boundary, "environment_application")
        self.assertEqual(self.state.next_boundary, "consequence_intake")
        self.assertFalse(self.state.model_contact_allowed)
        self.assertEqual(len(self.state.historical_pressure), 2)

    def test_current_lifecycle_step_is_on_route(self):
        result = inspect_proposal(self.state, proposal())
        self.assertEqual(result.verdict, "ON_ROUTE")
        self.assertEqual(result.exit_code, 0)

    def test_success_cannot_be_another_gate(self):
        result = inspect_proposal(self.state, proposal(success="another_gate"))
        self.assertEqual(result.verdict, "ROUTE_DRIFT")
        self.assertTrue(any("another gate" in item for item in result.findings))

    def test_failure_cannot_route_to_another_model(self):
        result = inspect_proposal(self.state, proposal(failure="another_model"))
        self.assertEqual(result.verdict, "ROUTE_DRIFT")

    def test_future_boundary_cannot_skip_current_boundary(self):
        result = inspect_proposal(self.state, proposal(target="consequence_intake"))
        self.assertEqual(result.verdict, "ROUTE_DRIFT")

    def test_model_catalog_and_generic_gate_are_route_drift(self):
        for kind in ("model_catalog_search", "generic_competence_gate", "model_admission"):
            with self.subTest(kind=kind):
                result = inspect_proposal(self.state, proposal(kind=kind))
                self.assertEqual(result.verdict, "ROUTE_DRIFT")

    def test_model_contact_stays_closed_even_when_agent_names_a_responsibility(self):
        result = inspect_proposal(
            self.state,
            proposal(kind="model_contact", responsibility="interpret_consequence"),
        )
        self.assertEqual(result.verdict, "ROUTE_DRIFT")
        self.assertTrue(any("model contact is closed" in item for item in result.findings))

    def test_future_named_model_contact_remains_support_only(self):
        future = replace(
            self.state,
            model_contact_allowed=True,
            named_responsibilities=("interpret_consequence",),
            prohibited_work_kinds=tuple(
                kind for kind in self.state.prohibited_work_kinds if kind != "model_contact"
            ),
        )
        result = inspect_proposal(
            future,
            proposal(
                kind="model_contact",
                success="environment_application",
                unblocks="environment_application",
                responsibility="interpret_consequence",
            ),
        )
        self.assertEqual(result.verdict, "SUPPORT_ONLY")

    def test_support_is_visible_but_not_progress(self):
        result = inspect_proposal(
            self.state,
            proposal(
                kind="support",
                target="environment_application",
                success="environment_application",
                failure="environment_application",
                unblocks="environment_application",
            ),
        )
        self.assertEqual(result.verdict, "SUPPORT_ONLY")
        self.assertEqual(result.exit_code, 1)

    def test_support_without_exact_unblock_is_route_drift(self):
        result = inspect_proposal(
            self.state,
            proposal(kind="support", success="environment_application"),
        )
        self.assertEqual(result.verdict, "ROUTE_DRIFT")

    def test_claim_cannot_outrun_current_maturity(self):
        result = inspect_proposal(self.state, proposal(claim="formation"))
        self.assertEqual(result.verdict, "ROUTE_DRIFT")

    def test_lifecycle_repair_must_stay_at_current_boundary(self):
        result = inspect_proposal(
            self.state,
            proposal(
                kind="lifecycle_repair",
                success="environment_application",
                unblocks="environment_application",
            ),
        )
        self.assertEqual(result.verdict, "ON_ROUTE")
        drift = inspect_proposal(
            self.state,
            proposal(kind="lifecycle_repair", unblocks="other_boundary"),
        )
        self.assertEqual(drift.verdict, "ROUTE_DRIFT")

    def test_cli_prints_pressure_and_uses_verdict_exit(self):
        output = io.StringIO()
        args = [
            "inspect",
            "--summary", "Screen another model",
            "--kind", "generic_competence_gate",
            "--target", "model_selection",
            "--success", "another_gate",
            "--failure", "another_model",
            "--claim", "wire",
        ]
        with contextlib.redirect_stdout(output):
            exit_code = main(args)
        rendered = output.getvalue()
        self.assertEqual(exit_code, 2)
        self.assertIn("WAYPOINT: ROUTE_DRIFT", rendered)
        self.assertIn("Historical pressure:", rendered)
        self.assertIn("does it only authorize another gate?", rendered)


if __name__ == "__main__":
    unittest.main()
