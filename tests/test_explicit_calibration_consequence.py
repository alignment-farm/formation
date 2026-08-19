from dataclasses import fields
import unittest

from micro_environment import (
    DECREASED,
    FIRST_INCREASES,
    FIRST_SLOT,
    HOLD,
    INCREASED,
    REQUEST_CALIBRATION,
    SECOND_INCREASES,
    SECOND_SLOT,
    UNCHANGED,
    CalibrationProfile,
    CalibrationState,
    apply_explicit_calibration_action,
)


class ExplicitCalibrationConsequenceTests(unittest.TestCase):
    def test_first_control_increase_is_rendered_as_two_environment_facts(self):
        state = CalibrationState("family-a", "device-a", 0, 1, "vek", "mora")
        result = apply_explicit_calibration_action(
            state, CalibrationProfile("family-a", FIRST_INCREASES), "vek"
        )
        self.assertEqual(result.selected_slot, FIRST_SLOT)
        self.assertEqual(result.movement_direction, INCREASED)
        self.assertIsNone(result.increasing_slot)

    def test_first_control_decrease_does_not_state_the_inferred_opposite_rule(self):
        state = CalibrationState("family-b", "device-b", 0, 1, "brin", "sova")
        result = apply_explicit_calibration_action(
            state, CalibrationProfile("family-b", SECOND_INCREASES), "brin"
        )
        self.assertEqual(result.selected_slot, FIRST_SLOT)
        self.assertEqual(result.movement_direction, DECREASED)
        self.assertEqual(result.position_after, -1)
        self.assertIsNone(result.increasing_slot)

    def test_second_control_reports_second_slot_and_factual_direction(self):
        state = CalibrationState("family-b", "device-b", 0, 1, "brin", "sova")
        result = apply_explicit_calibration_action(
            state, CalibrationProfile("family-b", SECOND_INCREASES), "sova"
        )
        self.assertEqual(result.selected_slot, SECOND_SLOT)
        self.assertEqual(result.movement_direction, INCREASED)

    def test_calibration_request_preserves_direct_environment_revelation(self):
        state = CalibrationState("family-b", "device-b", 0, 1, "brin", "sova")
        result = apply_explicit_calibration_action(
            state,
            CalibrationProfile("family-b", SECOND_INCREASES),
            REQUEST_CALIBRATION,
        )
        self.assertIsNone(result.selected_slot)
        self.assertEqual(result.movement_direction, UNCHANGED)
        self.assertEqual(result.increasing_slot, SECOND_INCREASES)

    def test_hold_reports_unchanged_without_a_control_slot(self):
        state = CalibrationState("family-a", "device-a", 2, 2, "vek", "mora")
        result = apply_explicit_calibration_action(
            state, CalibrationProfile("family-a", FIRST_INCREASES), HOLD
        )
        self.assertIsNone(result.selected_slot)
        self.assertEqual(result.movement_direction, UNCHANGED)

    def test_explicit_result_contains_no_candidate_or_experimental_fields(self):
        names = {field.name for field in fields(type(apply_explicit_calibration_action(
            CalibrationState("family-a", "device-a", 0, 1, "vek", "mora"),
            CalibrationProfile("family-a", FIRST_INCREASES),
            "vek",
        )))}
        self.assertTrue(
            names.isdisjoint(
                {
                    "candidate",
                    "claimed_scope",
                    "expected_action",
                    "case_family",
                    "branch",
                    "formation_verdict",
                }
            )
        )


if __name__ == "__main__":
    unittest.main()
