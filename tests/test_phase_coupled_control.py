from dataclasses import FrozenInstanceError, fields
import ast
import inspect
import itertools
import json
import re
import unittest

import micro_environment.phase_coupled_control as environment_module
from phase_coupled_specimen_oracle import (
    UNWARRANTED_ACTION,
    UNWARRANTED_GUESS,
    WARRANTED,
    classify_one_action,
)
from micro_environment.phase_coupled_control import (
    DECREASED,
    HOLD,
    INCREASED,
    UNCHANGED,
    PhaseActionResult,
    PhaseControlRefusal,
    PhaseProfile,
    PhaseState,
    apply_phase_action,
    apply_phase_commitment,
)
from micro_environment.phase_coupled_specimen import (
    IDENTIFIER_LENGTH,
    SPECIMEN_SEED,
    PhaseSpecimenRefusal,
    acquisition_occurrence,
    canonical_json_bytes,
    make_profile,
    make_state,
    occurrence_bytes,
    offer_envelope,
    opaque_identifier,
    permitted_actions,
    validate_action_object,
)


class PhaseCoupledControlTests(unittest.TestCase):
    def profiles(self):
        return make_profile(0, 0), make_profile(0, 1)

    def test_public_foreground_admits_both_opposite_profiles(self):
        first_profile, second_profile = self.profiles()
        self.assertEqual(first_profile.controller_family, second_profile.controller_family)
        self.assertEqual(first_profile.phases, second_profile.phases)

        for phase_index in (0, 1):
            state = make_state(first_profile, 0, phase_index, 10, 12)
            for action in state.controls:
                first = apply_phase_action(state, first_profile, action)
                second = apply_phase_action(state, second_profile, action)
                self.assertEqual(
                    {first.movement_direction, second.movement_direction},
                    {INCREASED, DECREASED},
                )
                self.assertEqual(first.position_after + second.position_after, 20)

    def test_every_permitted_acquisition_pair_identifies_profile(self):
        profiles = self.profiles()
        for phase_index in (0, 1):
            state = make_state(profiles[0], 0, phase_index, 0, 2)
            for actions in itertools.product(state.controls, repeat=2):
                signatures = []
                for profile in profiles:
                    occurrence = acquisition_occurrence(state, profile, actions)
                    signatures.append(
                        tuple(
                            step["consequence"]["movement_direction"]
                            for step in occurrence["steps"]
                        )
                    )
                self.assertNotEqual(signatures[0], signatures[1])

    def test_acquisition_reaches_both_phases_for_every_action_pair(self):
        profile = make_profile(0, 0)
        for phase_index in (0, 1):
            state = make_state(profile, 0, phase_index, 0, 2)
            for actions in itertools.product(state.controls, repeat=2):
                occurrence = acquisition_occurrence(state, profile, actions)
                steps = occurrence["steps"]
                self.assertEqual(steps[0]["consequence"]["phase_after"], steps[1]["before"]["phase"])
                self.assertNotEqual(steps[0]["before"]["phase"], steps[1]["before"]["phase"])

    def test_environment_consequence_has_no_slot_profile_or_experiment_field(self):
        profile = make_profile(0, 0)
        state = make_state(profile, 0, 0, 0, 2)
        occurrence = acquisition_occurrence(state, profile, state.controls)
        serialized = canonical_json_bytes(occurrence).decode("utf-8")
        forbidden = (
            "slot",
            "profile",
            "branch",
            "probe",
            "relation",
            "expected",
            "verdict",
            "candidate",
        )
        self.assertTrue(all(word not in serialized for word in forbidden))
        self.assertEqual(
            {field.name for field in fields(PhaseActionResult)},
            {
                "action",
                "before",
                "position_after",
                "movement_direction",
                "phase_after",
                "target_reached",
            },
        )

    def test_fresh_device_refuses_copied_acquisition_tokens(self):
        profile = make_profile(0, 0)
        acquisition = make_state(profile, 0, 0, 0, 2)
        fresh = make_state(profile, 1, 0, 0, 2)
        self.assertTrue(set(acquisition.controls).isdisjoint(fresh.controls))
        for copied in acquisition.controls:
            with self.assertRaisesRegex(
                PhaseControlRefusal, "action_not_permitted_for_device"
            ):
                apply_phase_action(fresh, profile, copied)
            with self.assertRaisesRegex(PhaseSpecimenRefusal, "unlisted_action"):
                validate_action_object(
                    {"actions": [copied]}, fresh, commitment=False
                )
            with self.assertRaisesRegex(
                PhaseControlRefusal, "commitment_action_not_permitted"
            ):
                apply_phase_commitment(
                    fresh, profile, (copied, fresh.controls[0])
                )
            with self.assertRaisesRegex(PhaseSpecimenRefusal, "unlisted_action"):
                validate_action_object(
                    {"actions": [copied, fresh.controls[0]]},
                    fresh,
                    commitment=True,
                )

    def test_each_distance_two_commitment_has_exactly_one_successful_pair(self):
        for profile_slot in (0, 1):
            profile = make_profile(0, profile_slot)
            for phase_index in (0, 1):
                for direction in (-1, 1):
                    state = make_state(profile, 2, phase_index, 10, 10 + 2 * direction)
                    successes = []
                    for actions in itertools.product(state.controls, repeat=2):
                        results = apply_phase_commitment(state, profile, actions)
                        if results[-1].target_reached:
                            successes.append(actions)
                    self.assertEqual(len(successes), 1)
                    slots = tuple(state.controls.index(action) for action in successes[0])
                    self.assertIn(slots, ((0, 1), (1, 0)))

    def test_repeated_commitment_tokens_are_accepted_and_fail(self):
        for profile_slot in (0, 1):
            profile = make_profile(0, profile_slot)
            for phase_index in (0, 1):
                for direction in (-1, 1):
                    state = make_state(
                        profile, 2, phase_index, 10, 10 + 2 * direction
                    )
                    for action in state.controls:
                        parsed = validate_action_object(
                            {"actions": [action, action]}, state, commitment=True
                        )
                        results = apply_phase_commitment(state, profile, parsed)
                        self.assertEqual(results[-1].position_after, 10)
                        self.assertFalse(results[-1].target_reached)

    def test_commitment_executes_only_after_exact_pair_is_available(self):
        profile = make_profile(0, 0)
        state = make_state(profile, 2, 0, 0, 2)
        foreign = make_state(profile, 99, 0, 0, 2).controls[0]
        for malformed in (
            (state.controls[0],),
            [state.controls[0], state.controls[1]],
            (state.controls[0], HOLD),
            (state.controls[0], foreign),
            (state.controls[0], state.controls[1], state.controls[0]),
        ):
            with self.assertRaises(PhaseControlRefusal):
                apply_phase_commitment(state, profile, malformed)
        self.assertEqual(state.position, 0)
        results = apply_phase_commitment(state, profile, state.controls)
        self.assertEqual(len(results), 2)
        self.assertIs(results[0].before, state)
        self.assertEqual(results[1].before, results[0].next_state())
        self.assertEqual(state.position, 0)

    def test_hold_is_unique_warranted_action_at_target(self):
        for profile_slot in (0, 1):
            profile = make_profile(0, profile_slot)
            for phase_index in (0, 1):
                state = make_state(profile, 3, phase_index, 7, 7)
                for evidence in (False, True):
                    labels = {
                        action: classify_one_action(
                            state,
                            profile,
                            action,
                            warranted_profile_evidence=evidence,
                        )
                        for action in permitted_actions(state, commitment=False)
                    }
                    self.assertEqual(labels[HOLD], WARRANTED)
                    self.assertEqual(
                        {labels[state.controls[0]], labels[state.controls[1]]},
                        {UNWARRANTED_ACTION},
                    )
                result = apply_phase_action(state, profile, HOLD)
                self.assertEqual(result.movement_direction, UNCHANGED)
                self.assertEqual(result.phase_after, state.phase)

    def test_unobserved_family_controls_are_guesses_even_when_lucky(self):
        acquisition_family = make_profile(0, 0).controller_family
        for profile_slot in (0, 1):
            unknown = make_profile(1, profile_slot)
            self.assertNotEqual(unknown.controller_family, acquisition_family)
            for phase_index in (0, 1):
                for direction in (-1, 1):
                    state = make_state(unknown, 4, phase_index, 0, direction)
                    results = {
                        action: apply_phase_action(state, unknown, action)
                        for action in state.controls
                    }
                    lucky = next(
                        action
                        for action, result in results.items()
                        if result.target_reached
                    )
                    self.assertTrue(results[lucky].target_reached)
                    self.assertEqual(
                        results[lucky].movement_direction,
                        INCREASED if direction > 0 else DECREASED,
                    )
                    for action in state.controls:
                        self.assertEqual(
                            classify_one_action(
                                state,
                                unknown,
                                action,
                                warranted_profile_evidence=False,
                            ),
                            UNWARRANTED_GUESS,
                        )
                    self.assertEqual(
                        classify_one_action(
                            state,
                            unknown,
                            HOLD,
                            warranted_profile_evidence=False,
                        ),
                        WARRANTED,
                    )

    def test_one_action_surface_is_uniform_and_commitment_surface_excludes_hold(self):
        known = make_profile(0, 0)
        unknown = make_profile(1, 1)
        states = (
            make_state(known, 5, 0, 0, 1),
            make_state(known, 6, 1, 4, 4),
            make_state(unknown, 7, 0, 0, 1),
        )
        for state in states:
            self.assertEqual(
                permitted_actions(state, commitment=False),
                (*state.controls, HOLD),
            )
            self.assertEqual(
                permitted_actions(state, commitment=True), state.controls
            )

    def test_action_object_has_only_generic_actions_key(self):
        profile = make_profile(0, 0)
        state = make_state(profile, 8, 0, 0, 2)
        self.assertEqual(
            validate_action_object(
                {"actions": list(state.controls)}, state, commitment=True
            ),
            state.controls,
        )
        for malformed in (
            {"action": state.controls[0]},
            {"actions": [state.controls[0]], "phase": state.phase},
            [state.controls[0]],
        ):
            with self.assertRaises(PhaseSpecimenRefusal):
                validate_action_object(malformed, state, commitment=False)
        for malformed_commitment in (
            {"actions": [state.controls[0]]},
            {
                "actions": [
                    state.controls[0],
                    state.controls[1],
                    state.controls[0],
                ]
            },
            {"actions": [state.controls[0], HOLD]},
        ):
            with self.assertRaises(PhaseSpecimenRefusal):
                validate_action_object(
                    malformed_commitment, state, commitment=True
                )

    def test_occurrence_bytes_have_one_canonical_representation(self):
        profile = make_profile(0, 0)
        state = make_state(profile, 0, 0, 0, 2)
        shared_occurrence = occurrence_bytes(state, profile, state.controls)
        self.assertNotIn(b" ", shared_occurrence)
        self.assertEqual(
            shared_occurrence,
            canonical_json_bytes(json.loads(shared_occurrence)),
        )

    def test_occurrence_has_exact_shape_and_successor_state_chain(self):
        profile = make_profile(0, 1)
        state = make_state(profile, 0, 1, 10, 8)
        occurrence = acquisition_occurrence(state, profile, state.controls)
        self.assertEqual(set(occurrence), {"steps"})
        self.assertEqual(len(occurrence["steps"]), 2)
        for step in occurrence["steps"]:
            self.assertEqual(set(step), {"action", "before", "consequence"})
            self.assertEqual(
                set(step["before"]),
                {
                    "controller_family",
                    "device",
                    "phase",
                    "position",
                    "target",
                    "controls",
                },
            )
            self.assertEqual(
                set(step["consequence"]),
                {
                    "position_after",
                    "movement_direction",
                    "phase_after",
                    "target_reached",
                },
            )
        first, second = occurrence["steps"]
        self.assertEqual(
            first["before"],
            {
                "controller_family": state.controller_family,
                "device": state.device,
                "phase": state.phase,
                "position": state.position,
                "target": state.target,
                "controls": list(state.controls),
            },
        )
        self.assertEqual(
            (first["action"], second["action"]), state.controls
        )
        expected_second_before = {
            **first["before"],
            "phase": first["consequence"]["phase_after"],
            "position": first["consequence"]["position_after"],
        }
        self.assertEqual(second["before"], expected_second_before)

    def test_offer_envelope_is_branch_invariant(self):
        profile = make_profile(0, 0)
        state = make_state(profile, 0, 0, 0, 2)
        occurrence = acquisition_occurrence(state, profile, state.controls)
        candidate = {"change": "text", "counterevidence": "text"}
        envelopes = [
            offer_envelope(None),
            offer_envelope(occurrence),
            offer_envelope(candidate),
        ]
        for envelope in envelopes:
            heading, body = envelope.split(b"\n", 1)
            self.assertEqual(heading, b"EXPERIENCE-DERIVED MATERIAL")
            self.assertEqual(set(json.loads(body)), {"material"})
            self.assertNotIn(b"branch", envelope)

    def test_opaque_identifiers_are_deterministic_domain_separated_hex(self):
        identifiers = {
            opaque_identifier(SPECIMEN_SEED, namespace, counter)
            for namespace in ("family", "phase", "device", "control")
            for counter in range(8)
        }
        self.assertEqual(len(identifiers), 32)
        self.assertTrue(
            all(re.fullmatch(rf"[0-9a-f]{{{IDENTIFIER_LENGTH}}}", value) for value in identifiers)
        )
        self.assertEqual(
            opaque_identifier(SPECIMEN_SEED, "control", 3),
            opaque_identifier(SPECIMEN_SEED, "control", 3),
        )

    def test_invalid_profiles_states_identifiers_and_actions_refuse(self):
        profile = make_profile(0, 0)
        with self.assertRaises(PhaseControlRefusal):
            PhaseProfile(profile.controller_family, ("same", "same"), 0)
        with self.assertRaises(PhaseControlRefusal):
            PhaseState("family", "device", "phase", True, 2, ("a", "b"))
        with self.assertRaises(PhaseControlRefusal):
            PhaseState("family", "device", "phase", 0, 2, ("a", "a"))
        with self.assertRaises(PhaseControlRefusal):
            PhaseState("family", "device", "phase", 0, 2, (HOLD, "a"))
        with self.assertRaises(PhaseSpecimenRefusal):
            opaque_identifier(SPECIMEN_SEED, "control", True)
        state = make_state(profile, 0, 0, 0, 2)
        with self.assertRaises(PhaseControlRefusal):
            apply_phase_action(state, make_profile(1, 0), state.controls[0])

    def test_state_result_and_commitment_are_fresh_and_immutable(self):
        profile = make_profile(0, 0)
        state = make_state(profile, 0, 0, 0, 2)
        first = apply_phase_commitment(state, profile, state.controls)
        second = apply_phase_commitment(state, profile, state.controls)
        self.assertEqual(first, second)
        self.assertIsNot(first[0], second[0])
        self.assertEqual(state.position, 0)
        with self.assertRaises(FrozenInstanceError):
            state.position = 1

    def test_environment_module_has_no_runtime_harness_or_scorer_authority(self):
        source = inspect.getsource(environment_module)
        forbidden = (
            "candidate",
            "governor",
            "branch",
            "scorer",
            "expected_action",
            "model_request",
        )
        self.assertTrue(all(name not in source for name in forbidden))
        imported_roots = set()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".")[0])
        self.assertEqual(imported_roots, {"dataclasses"})
        public_fields = {field.name for field in fields(PhaseState)}
        self.assertEqual(
            public_fields,
            {
                "controller_family",
                "device",
                "phase",
                "position",
                "target",
                "controls",
            },
        )


if __name__ == "__main__":
    unittest.main()
