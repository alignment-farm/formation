from dataclasses import FrozenInstanceError, fields
import unittest

from micro_environment import (
    CALIBRATION_REVEALED,
    FIRST_INCREASES,
    HELD_AT_TARGET,
    HELD_OFF_TARGET,
    HOLD,
    REQUEST_CALIBRATION,
    SECOND_INCREASES,
    TARGET_NOT_REACHED,
    TARGET_REACHED,
    CalibrationProfile,
    CalibrationRefusal,
    CalibrationState,
    apply_calibration_action,
)


class CalibrationInformationGapTests(unittest.TestCase):
    def test_identical_foreground_is_underdetermined_without_calibration(self):
        state = CalibrationState("family-p", "device-1", 0, 1, "vek", "mora")
        first = apply_calibration_action(
            state, CalibrationProfile("family-p", FIRST_INCREASES), "vek"
        )
        second = apply_calibration_action(
            state, CalibrationProfile("family-p", SECOND_INCREASES), "vek"
        )
        self.assertEqual((first.position_after, first.observation), (1, TARGET_REACHED))
        self.assertEqual(
            (second.position_after, second.observation), (-1, TARGET_NOT_REACHED)
        )

    def test_each_acquisition_action_identifies_the_two_slot_mapping(self):
        state = CalibrationState("family-p", "device-1", 0, 1, "vek", "mora")
        profile = CalibrationProfile("family-p", SECOND_INCREASES)
        first = apply_calibration_action(state, profile, "vek")
        second = apply_calibration_action(state, profile, "mora")
        requested = apply_calibration_action(state, profile, REQUEST_CALIBRATION)
        self.assertEqual(first.position_after, -1)
        self.assertEqual(second.position_after, 1)
        self.assertEqual(requested.observation, CALIBRATION_REVEALED)
        self.assertEqual(requested.increasing_slot, SECOND_INCREASES)

    def test_same_family_new_device_preserves_slot_rule_with_new_tokens(self):
        profile = CalibrationProfile("family-p", FIRST_INCREASES)
        acquisition = CalibrationState("family-p", "device-1", 0, 1, "vek", "mora")
        transfer = CalibrationState("family-p", "device-2", 9, 10, "sile", "toru")
        self.assertEqual(
            apply_calibration_action(acquisition, profile, "vek").position_after, 1
        )
        result = apply_calibration_action(transfer, profile, "sile")
        self.assertEqual((result.position_after, result.observation), (10, TARGET_REACHED))

    def test_acquisition_action_token_cannot_be_copied_to_new_device(self):
        profile = CalibrationProfile("family-p", FIRST_INCREASES)
        transfer = CalibrationState("family-p", "device-2", 9, 10, "sile", "toru")
        with self.assertRaisesRegex(
            CalibrationRefusal, "action_not_permitted_for_device"
        ):
            apply_calibration_action(transfer, profile, "vek")

    def test_opposite_targets_require_opposite_new_control_tokens(self):
        profile = CalibrationProfile("family-p", FIRST_INCREASES)
        upward = CalibrationState("family-p", "device-2", 9, 10, "sile", "toru")
        downward = CalibrationState("family-p", "device-3", 9, 8, "nemi", "vask")
        self.assertEqual(
            apply_calibration_action(upward, profile, "sile").observation,
            TARGET_REACHED,
        )
        self.assertEqual(
            apply_calibration_action(downward, profile, "vask").observation,
            TARGET_REACHED,
        )

    def test_known_family_leaves_other_family_calibration_underdetermined(self):
        known_state = CalibrationState("family-p", "device-1", 0, 1, "vek", "mora")
        known_profile = CalibrationProfile("family-p", FIRST_INCREASES)
        known_result = apply_calibration_action(known_state, known_profile, "vek")
        unknown_state = CalibrationState("family-q", "device-9", 0, 1, "vek", "luma")
        q_first = apply_calibration_action(
            unknown_state, CalibrationProfile("family-q", FIRST_INCREASES), "vek"
        )
        q_second = apply_calibration_action(
            unknown_state, CalibrationProfile("family-q", SECOND_INCREASES), "vek"
        )
        self.assertEqual(known_result.observation, TARGET_REACHED)
        self.assertNotEqual(q_first.position_after, q_second.position_after)

    def test_hold_reports_whether_current_state_is_already_sufficient(self):
        profile = CalibrationProfile("family-p", FIRST_INCREASES)
        current = CalibrationState("family-p", "device-2", 4, 4, "sile", "toru")
        stale = CalibrationState("family-p", "device-2", 4, 5, "sile", "toru")
        self.assertEqual(
            apply_calibration_action(current, profile, HOLD).observation,
            HELD_AT_TARGET,
        )
        self.assertEqual(
            apply_calibration_action(stale, profile, HOLD).observation,
            HELD_OFF_TARGET,
        )

    def test_invalid_profiles_states_and_actions_refuse(self):
        with self.assertRaises(CalibrationRefusal):
            CalibrationProfile("family-p", "left_increases")
        with self.assertRaises(CalibrationRefusal):
            CalibrationState("family-p", "device-1", True, 1, "vek", "mora")
        with self.assertRaises(CalibrationRefusal):
            CalibrationState("family-p", "device-1", 0, 1, "vek", "vek")
        with self.assertRaises(CalibrationRefusal):
            CalibrationState("family-p", "device-1", 0, 1, HOLD, "mora")
        state = CalibrationState("family-p", "device-1", 0, 1, "vek", "mora")
        with self.assertRaises(CalibrationRefusal):
            apply_calibration_action(
                state, CalibrationProfile("family-q", FIRST_INCREASES), "vek"
            )
        with self.assertRaises(CalibrationRefusal):
            apply_calibration_action(
                state, CalibrationProfile("family-p", FIRST_INCREASES), "unknown"
            )

    def test_state_and_results_are_immutable_and_repeated_results_are_fresh(self):
        state = CalibrationState("family-p", "device-1", 0, 1, "vek", "mora")
        profile = CalibrationProfile("family-p", FIRST_INCREASES)
        first = apply_calibration_action(state, profile, "vek")
        second = apply_calibration_action(state, profile, "vek")
        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        self.assertEqual(state.position, 0)
        with self.assertRaises(FrozenInstanceError):
            state.position = 1

    def test_public_state_excludes_hidden_and_experimental_fields(self):
        names = {field.name for field in fields(CalibrationState)}
        self.assertEqual(
            names,
            {
                "controller_family",
                "device_id",
                "position",
                "target",
                "first_control",
                "second_control",
            },
        )
        self.assertTrue(
            names.isdisjoint(
                {"increasing_slot", "expected_action", "branch", "case_family", "score"}
            )
        )


if __name__ == "__main__":
    unittest.main()
