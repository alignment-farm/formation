from __future__ import annotations

from dataclasses import replace
import unittest

from formation.foreground import (
    ForegroundConsumptionRefusal,
    ForegroundSourceRefusal,
    PositiveForeground,
    RuntimeForegroundConsumer,
    adapt_positive_foreground_source,
    fixture_positive_foreground_protocol,
    foreground_values,
)
from trajectory.foreground import (
    ForegroundDeliveryController,
    ForegroundDeliveryRefusal,
    ForegroundRecipientRefusal,
    ForegroundValidationRefusal,
    validate_fixture_positive_foreground,
)
from test_admitted_root import clean_admitted
from test_replay_constraint import clean_constraint


def complete_foreground():
    values = clean_constraint()
    conditions, formations, admitted, constraints, ablation = (
        values[0],
        values[1],
        values[2],
        values[5],
        values[12],
    )
    baseline = next(
        root
        for root, condition in conditions._root_conditions
        if condition == "audit_lineage_only-v0"
    )
    governed = admitted[0][6]
    controller = constraints.open_foreground_controller(
        baseline,
        governed,
        ablation,
    )
    freeze = controller.freeze()
    bound = controller.bind(freeze)
    results = []
    for root in freeze.authorized_roots:
        assignment = controller.assign_case(bound, root)
        delivery, consumer = controller.issue_delivery(assignment)
        handoff = consumer.consume(delivery)
        witness = controller.witness(assignment, consumer, handoff)
        results.append((assignment, delivery, consumer, handoff, witness))
    return values, controller, freeze, bound, results


class ForegroundTests(unittest.TestCase):
    def test_clean_one_freeze_three_exact_deliveries_and_direct_witnesses(self):
        values, controller, freeze, bound, results = complete_foreground()
        self.assertIsNotNone(bound)
        self.assertEqual(len(freeze.authorized_roots), 3)
        self.assertEqual(
            freeze.authorized_roots[0].prefix_root.artifact,
            values[2][0][6].condition_root.prefix_root.artifact,
        )
        self.assertIs(freeze.authorized_roots[1], values[2][0][6])
        self.assertIs(freeze.authorized_roots[2], values[12])
        self.assertEqual(foreground_values(freeze.foreground), (
            "bundle-9", "registry-manifest", 7, 8, True,
            "release", "rebuild_then_release",
        ))
        for assignment, delivery, consumer, handoff, witness in results:
            self.assertIs(delivery.recipient, assignment.recipient)
            self.assertIs(handoff.consumed_root, assignment.recipient)
            self.assertIs(handoff.foreground, freeze.foreground)
            self.assertIs(witness.handoff, handoff)
            self.assertIs(consumer.require_current(handoff), handoff)
        self.assertEqual(len(controller._witnesses), 3)

    def test_public_value_semantic_mutations_refuse(self):
        clean = fixture_positive_foreground_protocol().foreground
        mutations = (
            replace(clean, candidate_object="bundle-10"),
            replace(clean, artifact_revision="7"),
            replace(clean, authority_revision=7),
            replace(clean, depends_on_current_authority=1),
            replace(clean, commit_action="rebuild_then_release"),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaisesRegex(
                ForegroundValidationRefusal, "invalid_fixture_positive_foreground"
            ):
                validate_fixture_positive_foreground(mutation)

    def test_source_requires_exact_protocol_and_is_source_derived(self):
        protocol = fixture_positive_foreground_protocol()
        source = adapt_positive_foreground_source("run-001", protocol)
        self.assertIs(source.foreground, protocol.foreground)
        with self.assertRaisesRegex(
            ForegroundSourceRefusal, "exact_fixture_foreground_protocol_required"
        ):
            adapt_positive_foreground_source("run-001", replace(protocol))

    def test_wrong_root_types_and_meanings_refuse(self):
        values = clean_constraint()
        conditions, formations, admitted, constraints, ablation = (
            values[0], values[1], values[2], values[5], values[12]
        )
        baseline = next(
            root for root, condition in conditions._root_conditions
            if condition == "audit_lineage_only-v0"
        )
        with self.assertRaises((ForegroundRecipientRefusal, ValueError)):
            constraints.open_foreground_controller(
                admitted[0][6].condition_root, admitted[0][6], ablation,
            )
        with self.assertRaises((ForegroundRecipientRefusal, ValueError)):
            constraints.open_foreground_controller(
                baseline, admitted[1][6], ablation,
            )
        with self.assertRaises((ForegroundRecipientRefusal, ValueError)):
            constraints.open_foreground_controller(
                baseline, admitted[0][6], ablation.admitted_root,
            )

    def test_freeze_bound_assignment_delivery_and_consumption_are_one_shot(self):
        values = clean_constraint()
        conditions, formations, admitted, constraints, ablation = (
            values[0], values[1], values[2], values[5], values[12]
        )
        baseline = next(
            root for root, condition in conditions._root_conditions
            if condition == "audit_lineage_only-v0"
        )
        controller = constraints.open_foreground_controller(
            baseline, admitted[0][6], ablation,
        )
        freeze = controller.freeze()
        with self.assertRaisesRegex(
            ForegroundDeliveryRefusal, "positive_foreground_already_frozen"
        ):
            controller.freeze()
        bound = controller.bind(freeze)
        with self.assertRaisesRegex(
            ForegroundDeliveryRefusal, "foreground_already_bound"
        ):
            controller.bind(freeze)
        assignment = controller.assign_case(bound, baseline)
        with self.assertRaisesRegex(
            ForegroundDeliveryRefusal, "positive_case_already_assigned"
        ):
            controller.assign_case(bound, baseline)
        delivery, consumer = controller.issue_delivery(assignment)
        with self.assertRaisesRegex(
            ForegroundDeliveryRefusal, "foreground_delivery_already_issued"
        ):
            controller.issue_delivery(assignment)
        handoff = consumer.consume(delivery)
        with self.assertRaisesRegex(
            ForegroundConsumptionRefusal, "positive_delivery_already_consumed"
        ):
            consumer.consume(delivery)
        controller.witness(assignment, consumer, handoff)
        with self.assertRaisesRegex(
            ForegroundDeliveryRefusal, "received_foreground_mismatch"
        ):
            controller.witness(assignment, consumer, handoff)

    def test_equal_reconstructions_and_wrong_delivery_refuse(self):
        _, controller, freeze, bound, _ = complete_foreground()
        with self.assertRaisesRegex(
            ForegroundDeliveryRefusal, "exact_frozen_positive_foreground_required"
        ):
            controller.bind(replace(freeze))
        # New clean controller for delivery reconstruction before consumption.
        values = clean_constraint()
        conditions, formations, admitted, constraints, ablation = (
            values[0], values[1], values[2], values[5], values[12]
        )
        baseline = next(
            root for root, condition in conditions._root_conditions
            if condition == "audit_lineage_only-v0"
        )
        fresh = constraints.open_foreground_controller(
            baseline, admitted[0][6], ablation,
        )
        current = fresh.freeze()
        current_bound = fresh.bind(current)
        assignment = fresh.assign_case(current_bound, baseline)
        delivery, consumer = fresh.issue_delivery(assignment)
        with self.assertRaisesRegex(
            ForegroundConsumptionRefusal, "exact_positive_delivery_required"
        ):
            consumer.consume(replace(delivery))
        wrong_assignment = fresh.assign_case(current_bound, admitted[0][6])
        wrong_delivery, _ = fresh.issue_delivery(wrong_assignment)
        with self.assertRaisesRegex(
            ForegroundConsumptionRefusal, "exact_positive_delivery_required"
        ):
            consumer.consume(wrong_delivery)

    def test_runtime_visible_objects_expose_only_public_foreground(self):
        _, _, _, _, results = complete_foreground()
        for _, delivery, _, handoff, _ in results:
            for value in (delivery, handoff):
                for forbidden in (
                    "label", "comparison_group", "authorized_roots",
                    "expected_result", "case_family", "scorer",
                    "ablation_target", "reason", "intervention",
                ):
                    self.assertFalse(hasattr(value, forbidden))

    def test_post_capture_mutation_refuses(self):
        _, controller, freeze, _, results = complete_foreground()
        object.__setattr__(freeze.foreground, "artifact_revision", 9)
        try:
            with self.assertRaisesRegex(
                ForegroundDeliveryRefusal, "frozen_positive_foreground_changed"
            ):
                controller._require_freeze(freeze)
        finally:
            object.__setattr__(freeze.foreground, "artifact_revision", 7)

        _, _, _, _, results_2 = complete_foreground()
        _, delivery, consumer, handoff, _ = results_2[0]
        object.__setattr__(delivery, "recipient", object())
        with self.assertRaisesRegex(
            ForegroundConsumptionRefusal, "positive_delivery_changed"
        ):
            consumer.require_current(handoff)

    def test_no_bytes_digest_or_encounter_claim(self):
        _, _, freeze, _, results = complete_foreground()
        for value in (freeze, results[0][1], results[0][3], results[0][4]):
            self.assertFalse(hasattr(value, "artifact"))
            self.assertFalse(hasattr(value, "digest"))
            self.assertFalse(hasattr(value, "encounter"))

    def test_only_one_foreground_controller_can_own_the_recipient_set(self):
        values = clean_constraint()
        conditions, formations, admitted, constraints, ablation = (
            values[0], values[1], values[2], values[5], values[12]
        )
        baseline = next(
            root for root, condition in conditions._root_conditions
            if condition == "audit_lineage_only-v0"
        )
        controller = constraints.open_foreground_controller(
            baseline, admitted[0][6], ablation
        )
        self.assertIsNotNone(controller.freeze())
        with self.assertRaisesRegex(
            ValueError, "foreground_controller_already_registered"
        ):
            constraints.open_foreground_controller(
                baseline, admitted[0][6], ablation
            )
        with self.assertRaisesRegex(
            ForegroundRecipientRefusal, "constraint_foreground_factory_required"
        ):
            ForegroundDeliveryController(
                constraints, baseline, admitted[0][6], ablation
            )
        with self.assertRaisesRegex(
            ForegroundRecipientRefusal, "constraint_foreground_factory_required"
        ):
            ForegroundDeliveryController._from_constraint_controller(
                constraints, baseline, admitted[0][6], ablation, object()
            )

    def test_case_assignment_cannot_change_after_authorization(self):
        values = clean_constraint()
        conditions, admitted, constraints, ablation = (
            values[0], values[2], values[5], values[12]
        )
        baseline = next(
            root for root, condition in conditions._root_conditions
            if condition == "audit_lineage_only-v0"
        )
        controller = constraints.open_foreground_controller(
            baseline, admitted[0][6], ablation
        )
        freeze = controller.freeze()
        bound = controller.bind(freeze)
        assignment = controller.assign_case(bound, baseline)
        object.__setattr__(assignment, "recipient", object())
        with self.assertRaisesRegex(
            ForegroundDeliveryRefusal, "exact_positive_case_assignment_required"
        ):
            controller.issue_delivery(assignment)

    def test_runtime_rechecks_recipient_currentness(self):
        _, controller, _, _, results = complete_foreground()
        assignment, _, consumer, handoff, witness = results[0]
        original = assignment.recipient.head
        object.__setattr__(assignment.recipient, "head", "D-X-999999")
        try:
            with self.assertRaises(ValueError):
                consumer.require_current(handoff)
            with self.assertRaises(ValueError):
                controller.require_witness(witness)
        finally:
            object.__setattr__(assignment.recipient, "head", original)

    def test_runtime_consumer_cannot_be_caller_issued_or_duplicated(self):
        _, _, _, _, results = complete_foreground()
        _, delivery, _, _, _ = results[0]
        self.assertFalse(hasattr(RuntimeForegroundConsumer, "issue"))
        with self.assertRaisesRegex(
            ForegroundConsumptionRefusal, "foreground_consumer_factory_required"
        ):
            RuntimeForegroundConsumer(delivery, object())

    def test_source_and_protocol_currentness_are_exact(self):
        protocol = fixture_positive_foreground_protocol()
        original = protocol.foreground
        object.__setattr__(protocol, "foreground", replace(original))
        try:
            with self.assertRaisesRegex(
                ForegroundSourceRefusal,
                "exact_fixture_foreground_protocol_required",
            ):
                adapt_positive_foreground_source("run-001", protocol)
        finally:
            object.__setattr__(protocol, "foreground", original)

        _, controller, freeze, _, _ = complete_foreground()
        object.__setattr__(freeze.source, "run_id", "other-run")
        with self.assertRaisesRegex(
            ForegroundDeliveryRefusal, "frozen_positive_foreground_changed"
        ):
            controller._require_freeze(freeze)

        _, controller_2, freeze_2, _, _ = complete_foreground()
        object.__setattr__(freeze_2.source, "foreground", replace(freeze_2.foreground))
        with self.assertRaisesRegex(
            ForegroundDeliveryRefusal, "frozen_positive_foreground_changed"
        ):
            controller_2._require_freeze(freeze_2)

    def test_witnesses_remain_current_and_complete(self):
        _, controller, _, _, results = complete_foreground()
        witnesses = controller.require_complete_witnesses()
        self.assertEqual(len(witnesses), 3)
        witness = results[0][4]
        object.__setattr__(witness, "handoff", results[1][3])
        with self.assertRaisesRegex(
            ForegroundDeliveryRefusal, "exact_received_foreground_witness_required"
        ):
            controller.require_witness(witness)

    def test_delivery_retains_exact_freeze_and_group_provenance(self):
        _, _, freeze, _, results = complete_foreground()
        _, delivery, consumer, handoff, _ = results[0]
        self.assertIs(delivery._freeze, freeze)
        self.assertIs(delivery._comparison_group, freeze.comparison_group)
        object.__setattr__(delivery, "_freeze", replace(freeze))
        with self.assertRaisesRegex(
            ForegroundConsumptionRefusal, "positive_delivery_changed"
        ):
            consumer.require_current(handoff)

        _, _, freeze_2, _, results_2 = complete_foreground()
        _, delivery_2, consumer_2, handoff_2, _ = results_2[0]
        object.__setattr__(
            delivery_2,
            "_comparison_group",
            replace(freeze_2.comparison_group),
        )
        with self.assertRaisesRegex(
            ForegroundConsumptionRefusal, "positive_delivery_changed"
        ):
            consumer_2.require_current(handoff_2)


if __name__ == "__main__":
    unittest.main()
