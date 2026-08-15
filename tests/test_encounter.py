from __future__ import annotations

from dataclasses import replace
import unittest

from formation.encounter import (
    EncounterBranchRoot,
    EncounterOpenedAppend,
    EncounterOpeningBinding,
    EncounterOpeningRefusal,
    PositiveEncounter,
    RuntimeEncounterOpener,
)
from trajectory.encounter import (
    EncounterOpeningController,
    EncounterOpeningWitness,
    EncounterWitnessRefusal,
)
from trajectory.foreground import ForegroundDeliveryRefusal
from test_foreground import complete_foreground


def complete_encounters():
    values, foreground, freeze, bound, deliveries = complete_foreground()
    controller = foreground.open_encounter_controller()
    results = []
    for assignment, delivery, consumer, handoff, foreground_witness in deliveries:
        binding = controller.runtime.bind(consumer, handoff)
        root = controller.runtime.open(assignment.recipient, binding)
        witness = controller.witness(
            assignment,
            foreground_witness,
            consumer,
            handoff,
            binding,
            root,
        )
        results.append(
            (
                assignment,
                delivery,
                consumer,
                handoff,
                foreground_witness,
                binding,
                root,
                witness,
            )
        )
    return values, foreground, freeze, bound, controller, results


class EncounterOpeningTests(unittest.TestCase):
    def test_clean_three_runtime_authored_encounters_and_closed_witness_set(self):
        _, _, freeze, _, controller, results = complete_encounters()
        self.assertEqual(len(controller.require_complete_witnesses()), 3)
        encounter_ids = set()
        for assignment, _, consumer, handoff, _, binding, root, witness in results:
            self.assertIs(root.predecessor, assignment.recipient)
            self.assertIs(root.opening_binding, binding)
            self.assertIs(root.situation, handoff.foreground)
            self.assertIs(root.situation, freeze.foreground)
            self.assertIs(root.append.predecessor, root.predecessor)
            self.assertIs(root.append.opening_binding, binding)
            self.assertIs(root.append.encounter, root.encounter)
            self.assertIs(witness.encounter_root, root)
            self.assertIs(controller.runtime.require_root(root), root)
            self.assertIs(
                controller.runtime.require_binding(
                    binding, consumer, handoff, root.predecessor, opened=True
                ),
                binding,
            )
            encounter_ids.add(id(root.encounter))
        self.assertEqual(len(encounter_ids), 3)

    def test_opening_binding_and_runtime_are_one_shot(self):
        _, foreground, _, _, deliveries = complete_foreground()
        controller = foreground.open_encounter_controller()
        assignment, _, consumer, handoff, _ = deliveries[0]
        binding = controller.runtime.bind(consumer, handoff)
        with self.assertRaisesRegex(
            EncounterOpeningRefusal, "encounter_opening_already_bound"
        ):
            controller.runtime.bind(consumer, handoff)
        root = controller.runtime.open(assignment.recipient, binding)
        self.assertIs(controller.runtime.require_root(root), root)
        with self.assertRaisesRegex(
            EncounterOpeningRefusal, "encounter_predecessor_not_current"
        ):
            controller.runtime.require_predecessor_current(assignment.recipient)
        verifier = controller.runtime.root_verifier(root)
        self.assertIs(verifier.require(root), root)
        with self.assertRaisesRegex(
            EncounterOpeningRefusal, "encounter_opening_already_consumed"
        ):
            controller.runtime.open(assignment.recipient, binding)
        with self.assertRaisesRegex(
            ForegroundDeliveryRefusal, "encounter_controller_already_opened"
        ):
            foreground.open_encounter_controller()

    def test_wrong_predecessor_refuses_without_spending_opening_right(self):
        _, foreground, _, _, deliveries = complete_foreground()
        controller = foreground.open_encounter_controller()
        assignment, _, consumer, handoff, _ = deliveries[0]
        binding = controller.runtime.bind(consumer, handoff)
        wrong = deliveries[1][0].recipient
        with self.assertRaises(EncounterOpeningRefusal):
            controller.runtime.open(wrong, binding)
        root = controller.runtime.open(assignment.recipient, binding)
        self.assertIs(root.predecessor, assignment.recipient)

    def test_caller_created_and_equal_reconstructed_bindings_refuse(self):
        _, foreground, _, _, deliveries = complete_foreground()
        controller = foreground.open_encounter_controller()
        assignment, _, consumer, handoff, _ = deliveries[0]
        binding = controller.runtime.bind(consumer, handoff)
        with self.assertRaisesRegex(
            EncounterOpeningRefusal, "exact_encounter_opening_binding_required"
        ):
            controller.runtime.open(assignment.recipient, replace(binding))
        forged = EncounterOpeningBinding(binding.run_id, binding.token, binding._issuer)
        with self.assertRaisesRegex(
            EncounterOpeningRefusal, "exact_encounter_opening_binding_required"
        ):
            controller.runtime.open(assignment.recipient, forged)
        root = controller.runtime.open(assignment.recipient, binding)
        with self.assertRaisesRegex(
            EncounterOpeningRefusal, "exact_encounter_root_required"
        ):
            controller.runtime.require_root(replace(root))

    def test_lineage_objects_cannot_reach_harness_provenance(self):
        _, _, _, _, _, results = complete_encounters()
        forbidden = (
            "handoff",
            "delivery",
            "freeze",
            "comparison_group",
            "authorized_roots",
            "case_assignment",
            "label",
            "case_family",
            "expected_result",
            "scorer",
        )
        for *_, binding, root, _ in results:
            for value in (binding, root, root.append, root.encounter):
                for name in forbidden:
                    self.assertFalse(hasattr(value, name), (type(value), name))
            self.assertFalse(hasattr(binding, "_handoff"))
            self.assertFalse(hasattr(binding, "_registry"))

    def test_no_bytes_digest_or_later_practice_claim(self):
        _, _, _, _, _, results = complete_encounters()
        root = results[0][6]
        for value in (root.opening_binding, root.encounter, root.append, root):
            for name in (
                "artifact", "digest", "activation", "model_request",
                "action", "consequence", "formation_effect",
            ):
                self.assertFalse(hasattr(value, name))

    def test_binding_append_encounter_and_root_mutation_refuse(self):
        _, _, _, _, controller, results = complete_encounters()
        binding = results[0][5]
        root = results[0][6]
        original = binding.token
        object.__setattr__(binding, "token", object())
        try:
            with self.assertRaises(EncounterOpeningRefusal):
                controller.runtime.require_root(root)
        finally:
            object.__setattr__(binding, "token", original)

        object.__setattr__(root.append, "predecessor", object())
        with self.assertRaisesRegex(EncounterOpeningRefusal, "encounter_root_changed"):
            controller.runtime.require_root(root)

    def test_private_boolean_resets_do_not_reopen_the_encounter(self):
        _, foreground, _, _, deliveries = complete_foreground()
        controller = foreground.open_encounter_controller()
        assignment, _, consumer, handoff, _ = deliveries[0]
        binding = controller.runtime.bind(consumer, handoff)
        controller.runtime.open(assignment.recipient, binding)
        use = controller.runtime._find_use(binding)
        use.opened = False
        consumer._encounter_opened = False
        with self.assertRaisesRegex(
            EncounterOpeningRefusal, "encounter_opening_already_consumed"
        ):
            controller.runtime.open(assignment.recipient, binding)

    def test_witness_refuses_wrong_chain_forgery_and_incomplete_set(self):
        _, foreground, _, _, deliveries = complete_foreground()
        controller = foreground.open_encounter_controller()
        first = deliveries[0]
        second = deliveries[1]
        binding = controller.runtime.bind(first[2], first[3])
        root = controller.runtime.open(first[0].recipient, binding)
        with self.assertRaises(EncounterWitnessRefusal):
            controller.witness(
                second[0], second[4], first[2], first[3], binding, root
            )
        witness = controller.witness(
            first[0], first[4], first[2], first[3], binding, root
        )
        with self.assertRaisesRegex(
            EncounterWitnessRefusal, "three_encounter_witnesses_required"
        ):
            controller.require_complete_witnesses()
        forged = replace(witness)
        with self.assertRaisesRegex(
            EncounterWitnessRefusal, "exact_encounter_witness_required"
        ):
            controller.require_witness(forged)

    def test_runtime_and_harness_factories_refuse_caller_construction(self):
        _, foreground, _, _, deliveries = complete_foreground()
        consumers = tuple(item[2] for item in deliveries)
        with self.assertRaisesRegex(
            ForegroundDeliveryRefusal, "encounter_controller_factory_required"
        ):
            RuntimeEncounterOpener(
                consumers, foreground._verifiers, foreground, object()
            )
        controller = foreground.open_encounter_controller()
        with self.assertRaisesRegex(
            ForegroundDeliveryRefusal, "exact_encounter_runtime_required"
        ):
            EncounterOpeningController(foreground, controller.runtime, object())

    def test_same_consumers_cannot_register_a_second_opening_authority(self):
        _, foreground, _, _, deliveries = complete_foreground()
        foreground.open_encounter_controller()
        consumers = tuple(item[2] for item in deliveries)
        with self.assertRaisesRegex(
            ValueError, "encounter_authority_already_registered"
        ):
            RuntimeEncounterOpener(
                consumers,
                foreground._verifiers,
                foreground,
                foreground._encounter_open_permit,
            )

    def test_failed_factory_validation_does_not_claim_controller_or_consumers(self):
        _, foreground, _, _, deliveries = complete_foreground()
        consumers = tuple(item[2] for item in deliveries)
        wrong_verifiers = (
            foreground._verifiers[1],
            foreground._verifiers[0],
            foreground._verifiers[2],
        )
        with self.assertRaisesRegex(
            EncounterOpeningRefusal, "exact_three_encounter_recipients_required"
        ):
            RuntimeEncounterOpener(
                consumers,
                wrong_verifiers,
                foreground,
                foreground._encounter_open_permit,
            )
        controller = foreground.open_encounter_controller()
        self.assertIsNotNone(controller)

    def test_delivery_order_does_not_change_consumer_verifier_pairing(self):
        values, foreground, freeze, bound, deliveries = complete_foreground()
        # Rebuild a clean controller because complete_foreground uses root order.
        conditions, formations, admitted, constraints, ablation = (
            values[0], values[1], values[2], values[5], values[12]
        )
        baseline = next(
            root for root, condition in conditions._root_conditions
            if condition == "audit_lineage_only-v0"
        )
        # The fixture chain permits only one foreground controller, so obtain a
        # fresh chain and issue in ablation, baseline, governed order.
        from test_replay_constraint import clean_constraint

        fresh_values = clean_constraint()
        fresh_conditions, fresh_admitted, fresh_constraints, fresh_ablation = (
            fresh_values[0], fresh_values[2], fresh_values[5], fresh_values[12]
        )
        fresh_baseline = next(
            root for root, condition in fresh_conditions._root_conditions
            if condition == "audit_lineage_only-v0"
        )
        fresh_foreground = fresh_constraints.open_foreground_controller(
            fresh_baseline, fresh_admitted[0][6], fresh_ablation
        )
        fresh_freeze = fresh_foreground.freeze()
        fresh_bound = fresh_foreground.bind(fresh_freeze)
        issued = []
        for root in (
            fresh_freeze.authorized_roots[2],
            fresh_freeze.authorized_roots[0],
            fresh_freeze.authorized_roots[1],
        ):
            assignment = fresh_foreground.assign_case(fresh_bound, root)
            delivery, consumer = fresh_foreground.issue_delivery(assignment)
            handoff = consumer.consume(delivery)
            witness = fresh_foreground.witness(assignment, consumer, handoff)
            issued.append((assignment, consumer, handoff, witness))
        encounters = fresh_foreground.open_encounter_controller()
        for assignment, consumer, handoff, _ in issued:
            binding = encounters.runtime.bind(consumer, handoff)
            root = encounters.runtime.open(assignment.recipient, binding)
            self.assertIs(root.predecessor, assignment.recipient)

    def test_raw_witness_root_refuses_instead_of_attribute_error(self):
        _, foreground, _, _, deliveries = complete_foreground()
        controller = foreground.open_encounter_controller()
        assignment, _, consumer, handoff, foreground_witness = deliveries[0]
        binding = controller.runtime.bind(consumer, handoff)
        with self.assertRaises(EncounterWitnessRefusal):
            controller.witness(
                assignment,
                foreground_witness,
                consumer,
                handoff,
                binding,
                object(),
            )

    def test_caller_created_runtime_objects_cannot_be_witnessed(self):
        _, foreground, _, _, deliveries = complete_foreground()
        controller = foreground.open_encounter_controller()
        assignment, _, consumer, handoff, foreground_witness = deliveries[0]
        binding = controller.runtime.bind(consumer, handoff)
        root = controller.runtime.open(assignment.recipient, binding)
        fake_encounter = PositiveEncounter(
            root.encounter.run_id, root.encounter.token, root.encounter._issuer
        )
        fake_append = EncounterOpenedAppend(
            root.run_id,
            root.predecessor,
            binding,
            fake_encounter,
            root.situation,
            root.append._issuer,
        )
        fake_root = EncounterBranchRoot(
            root.run_id,
            root.predecessor,
            binding,
            fake_encounter,
            fake_append,
            root.situation,
            root._issuer,
        )
        with self.assertRaises(EncounterOpeningRefusal):
            controller.runtime.require_root(fake_root)
        with self.assertRaises(EncounterOpeningRefusal):
            controller.witness(
                assignment,
                foreground_witness,
                consumer,
                handoff,
                binding,
                fake_root,
            )

    def test_witness_mutation_refuses_after_recording(self):
        _, _, _, _, controller, results = complete_encounters()
        witness = results[0][7]
        object.__setattr__(witness, "encounter_root", results[1][6])
        with self.assertRaisesRegex(
            EncounterWitnessRefusal, "exact_encounter_witness_required"
        ):
            controller.require_witness(witness)


if __name__ == "__main__":
    unittest.main()
