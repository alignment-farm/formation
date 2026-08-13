from __future__ import annotations

from dataclasses import replace
import unittest

from formation.replay_constraint import (
    CONSTRAINT_ORDER,
    POLICY,
    RECORDER,
    TARGET_ROLE,
    ConstraintHandoffRefusal,
    ReplayConstraintReservationRefusal,
    ReplayConstraintSourceRefusal,
    RuntimeReplayConstraintRun,
)
from trajectory.admitted_root import (
    AdmittedTreatmentBatchRefusal,
    FormationAppendController,
)
from trajectory.replay_constraint import (
    PublicReplayConstraintDelivery,
    ReplayConstraintBranchRoot,
    ReplayConstraintAppendController,
    ReplayConstraintAppendRefusal,
    ReplayConstraintAssignmentRefusal,
    ReplayConstraintValidationRefusal,
    validate_fixture_replay_constraint,
)
from test_admitted_root import clean_admitted


def clean_constraint():
    conditions, _, _, _, formations, admitted = clean_admitted()
    batch = formations.issue_admitted_treatment_batch()
    runtime_run = RuntimeReplayConstraintRun(batch.run_id, batch)
    controller = formations.open_constraint_controller(batch)
    assignment, delivery = controller.assign(runtime_run.reservation())
    runtime = runtime_run.materializer(delivery.recipient, delivery)
    source = runtime.adapt_source(delivery)
    handoff = runtime.materialize(source)
    witness = controller.witness(
        runtime, handoff, assignment, delivery
    )
    root = controller.append(runtime, handoff, witness)
    return (
        conditions,
        formations,
        admitted,
        batch,
        runtime_run,
        controller,
        assignment,
        delivery,
        runtime,
        source,
        handoff,
        witness,
        root,
    )


class ReplayConstraintTests(unittest.TestCase):
    def test_clean_append_selects_exact_ablation_and_returns_distinct_root(self):
        values = clean_constraint()
        admitted, assignment, delivery, source, handoff, root = (
            values[2],
            values[6],
            values[7],
            values[9],
            values[10],
            values[12],
        )
        self.assertIs(assignment.recipient.condition_root, admitted[1][6].condition_root)
        self.assertIs(delivery.recipient, assignment.recipient)
        self.assertEqual(delivery.target_role, TARGET_ROLE)
        self.assertEqual(delivery.policy, POLICY)
        self.assertIs(source.target, assignment.recipient.proposal._authorship.source.source_consequence)
        self.assertEqual(handoff.event.order, CONSTRAINT_ORDER)
        self.assertEqual(handoff.event.authority, RECORDER)
        self.assertIs(handoff.event.target, source.target)
        self.assertTrue(any(parent is source.target for parent in handoff.event.parents))
        self.assertTrue(any(parent is assignment.recipient.head for parent in handoff.event.parents))
        self.assertIs(root.admitted_root, assignment.recipient)
        self.assertIs(root.constraint, handoff.event)
        self.assertIsNot(root, root.admitted_root)
        self.assertIs(values[5].require_returned_root(root), root)

    def test_runtime_visible_objects_exclude_hidden_assignment_and_replay_view(self):
        values = clean_constraint()
        delivery, source, event, root = values[7], values[9], values[10].event, values[12]
        for value in (delivery, source, event, root):
            for forbidden in (
                "label",
                "reason",
                "expected_effect",
                "scorer",
                "case_family",
                "constrained_view",
                "artifact",
                "binding",
                "digest",
            ):
                self.assertFalse(hasattr(value, forbidden))

    def test_admitted_batch_is_canonical_exact_and_one_shot(self):
        _, _, _, _, formations, admitted = clean_admitted()
        batch = formations.issue_admitted_treatment_batch()
        self.assertEqual(
            batch.roots,
            (admitted[0][6], admitted[1][6]),
        )
        forged = replace(batch, roots=tuple(reversed(batch.roots)))
        with self.assertRaisesRegex(
            (ReplayConstraintReservationRefusal, AdmittedTreatmentBatchRefusal),
            "exact_admitted_treatment_batch_required",
        ):
            RuntimeReplayConstraintRun(batch.run_id, forged)
        RuntimeReplayConstraintRun(batch.run_id, batch)
        with self.assertRaisesRegex(
            AdmittedTreatmentBatchRefusal,
            "admitted_treatment_batch_already_consumed",
        ):
            RuntimeReplayConstraintRun(batch.run_id, batch)
        with self.assertRaisesRegex(
            AdmittedTreatmentBatchRefusal,
            "admitted_treatment_batch_already_issued",
        ):
            formations.issue_admitted_treatment_batch()

    def test_assignment_requires_preassignment_reservation_and_single_controller(self):
        _, _, _, _, formations, _ = clean_admitted()
        batch = formations.issue_admitted_treatment_batch()
        controller = formations.open_constraint_controller(batch)
        with self.assertRaisesRegex(
            ReplayConstraintAssignmentRefusal,
            "exact_runtime_reservation_required",
        ):
            controller.assign(object())
        runtime_run = RuntimeReplayConstraintRun(batch.run_id, batch)
        controller.assign(runtime_run.reservation())
        with self.assertRaisesRegex(
            ReplayConstraintAssignmentRefusal, "ablation_already_assigned"
        ):
            controller.assign(runtime_run.reservation())
        with self.assertRaisesRegex(
            AdmittedTreatmentBatchRefusal, "constraint_controller_already_registered"
        ):
            formations.open_constraint_controller(batch)

    def test_wrong_root_and_reconstructed_delivery_refuse(self):
        _, _, _, _, formations, admitted = clean_admitted()
        batch = formations.issue_admitted_treatment_batch()
        runtime_run = RuntimeReplayConstraintRun(batch.run_id, batch)
        controller = formations.open_constraint_controller(batch)
        assignment, delivery = controller.assign(runtime_run.reservation())
        governed = admitted[0][6]
        self.assertIsNot(governed, assignment.recipient)
        # The clean helper has already opened the ablation slot; the governed
        # reservation remains unopened and must reject its root-bound delivery.
        with self.assertRaisesRegex(
            ReplayConstraintReservationRefusal,
            "root_bound_constraint_delivery_required",
        ):
            runtime_run.materializer(governed, delivery)
        with self.assertRaisesRegex(
            ReplayConstraintAssignmentRefusal,
            "exact_public_constraint_delivery_required",
        ):
            controller.require_delivery(replace(delivery))
        self.assertEqual(len(batch.roots), 2)

    def test_target_role_policy_and_hidden_assignment_mutations_refuse(self):
        values = clean_constraint()
        controller, assignment, delivery = values[5], values[6], values[7]
        for mutation in (
            replace(delivery, target_role="D-C-005"),
            replace(delivery, policy="direct_exclusion"),
        ):
            with self.subTest(mutation=mutation), self.assertRaisesRegex(
                ReplayConstraintAssignmentRefusal,
                "exact_public_constraint_delivery_required|public_constraint_delivery_changed",
            ):
                controller.require_delivery(mutation)
        object.__setattr__(assignment, "reason", "expected_failure")
        with self.assertRaisesRegex(
            ReplayConstraintAssignmentRefusal, "ablation_assignment_changed"
        ):
            controller.require_assignment(assignment)

    def test_source_delivery_and_materialization_are_one_shot(self):
        _, _, _, _, formations, _ = clean_admitted()
        batch = formations.issue_admitted_treatment_batch()
        runtime_run = RuntimeReplayConstraintRun(batch.run_id, batch)
        controller = formations.open_constraint_controller(batch)
        assignment, delivery = controller.assign(runtime_run.reservation())
        runtime = runtime_run.materializer(delivery.recipient, delivery)
        source = runtime.adapt_source(delivery)
        with self.assertRaisesRegex(
            ReplayConstraintSourceRefusal, "constraint_source_already_issued"
        ):
            runtime.adapt_source(delivery)
        handoff = runtime.materialize(source)
        with self.assertRaisesRegex(
            ConstraintHandoffRefusal, "constraint_already_materialized"
        ):
            runtime.materialize(source)
        witness = controller.witness(runtime, handoff, assignment, delivery)
        with self.assertRaisesRegex(
            ReplayConstraintAppendRefusal, "constraint_already_witnessed"
        ):
            controller.witness(runtime, handoff, assignment, delivery)
        controller.append(runtime, handoff, witness)
        with self.assertRaisesRegex(
            ReplayConstraintAppendRefusal, "constraint_root_already_returned"
        ):
            controller.append(runtime, handoff, witness)

    def test_semantic_mutations_refuse_independently(self):
        event = clean_constraint()[10].event
        mutations = (
            replace(event, order=11),
            replace(event, event="candidate_revoked"),
            replace(event, authority="trajectory_harness"),
            replace(event, policy="direct_exclusion"),
            replace(event, parents=frozenset()),
            replace(event, target=object()),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaisesRegex(
                ReplayConstraintValidationRefusal,
                "invalid_fixture_replay_constraint",
            ):
                validate_fixture_replay_constraint(mutation)

    def test_reservation_coordinate_and_root_mutations_refuse(self):
        _, _, _, _, formations, _ = clean_admitted()
        batch = formations.issue_admitted_treatment_batch()
        runtime_run = RuntimeReplayConstraintRun(batch.run_id, batch)
        runtime_run._slots[0][1]._sequence = 999
        with self.assertRaisesRegex(
            ReplayConstraintReservationRefusal,
            "constraint_reservation_changed",
        ):
            runtime_run.reservation()

        _, _, _, _, formations_2, _ = clean_admitted()
        batch_2 = formations_2.issue_admitted_treatment_batch()
        runtime_run_2 = RuntimeReplayConstraintRun(batch_2.run_id, batch_2)
        object.__setattr__(batch_2.roots[0], "head", object())
        with self.assertRaisesRegex(
            ValueError, "admitted_(treatment_)?root_changed"
        ):
            runtime_run_2.reservation()

    def test_handoff_witness_and_returned_root_reconstructions_refuse(self):
        values = clean_constraint()
        controller, runtime, handoff, witness, root = (
            values[5],
            values[8],
            values[10],
            values[11],
            values[12],
        )
        with self.assertRaisesRegex(
            ConstraintHandoffRefusal, "exact_current_constraint_handoff_required"
        ):
            runtime.require_current(replace(handoff))
        with self.assertRaisesRegex(
            ReplayConstraintAppendRefusal, "exact_constraint_witness_required"
        ):
            controller._require_witness(replace(witness))
        with self.assertRaisesRegex(
            ReplayConstraintAppendRefusal, "exact_replay_constraint_root_required"
        ):
            controller.require_returned_root(replace(root))
        with self.assertRaisesRegex(
            ReplayConstraintAppendRefusal, "exact_replay_constraint_root_required"
        ):
            controller.require_returned_root(root.admitted_root)

    def test_post_return_constraint_and_upstream_mutations_refuse(self):
        values = clean_constraint()
        controller, root = values[5], values[12]
        object.__setattr__(root.constraint, "policy", "direct_exclusion")
        with self.assertRaisesRegex(
            ReplayConstraintAppendRefusal, "replay_constraint_root_changed"
        ):
            controller.require_returned_root(root)

        values_2 = clean_constraint()
        controller_2, root_2 = values_2[5], values_2[12]
        object.__setattr__(root_2.admitted_root.admission.warrant, "satisfied_checks", ())
        with self.assertRaisesRegex(
            ReplayConstraintAppendRefusal, "replay_constraint_root_changed"
        ):
            controller_2.require_returned_root(root_2)

    def test_parent_reconstruction_and_target_substitution_refuse_after_handoff(self):
        values = clean_constraint()
        runtime, handoff = values[8], values[10]
        object.__setattr__(
            handoff.event,
            "parents",
            frozenset(tuple(handoff.event.parents)),
        )
        with self.assertRaisesRegex(
            ConstraintHandoffRefusal, "constraint_handoff_changed"
        ):
            runtime.require_current(handoff)

        values_2 = clean_constraint()
        runtime_2, handoff_2 = values_2[8], values_2[10]
        object.__setattr__(handoff_2.event, "target", replace(handoff_2.event.target))
        with self.assertRaisesRegex(
            ConstraintHandoffRefusal, "constraint_handoff_changed"
        ):
            runtime_2.require_current(handoff_2)

    def test_runtime_objects_have_no_harness_assignment_backpointer(self):
        values = clean_constraint()
        batch, delivery, source = values[3], values[7], values[9]
        self.assertFalse(hasattr(batch._use, "_controller"))
        self.assertFalse(hasattr(delivery._use, "_controller"))
        self.assertFalse(hasattr(source._use, "_controller"))

    def test_forged_delivery_use_and_unregistered_materializer_refuse(self):
        _, _, _, _, formations, admitted = clean_admitted()
        batch = formations.issue_admitted_treatment_batch()
        runtime_run = RuntimeReplayConstraintRun(batch.run_id, batch)
        controller = formations.open_constraint_controller(batch)
        _, delivery = controller.assign(runtime_run.reservation())
        governed = admitted[0][6]
        use_type = type(delivery._use)
        with self.assertRaisesRegex(
            ReplayConstraintAssignmentRefusal, "delivery_factory_required"
        ):
            use_type(object())
        cloned_use = use_type(delivery._use._issuer)
        cloned_delivery = PublicReplayConstraintDelivery(
            delivery.run_id,
            governed,
            delivery.target_role,
            delivery.policy,
            cloned_use,
            delivery._registry,
            delivery._issuer,
        )
        cloned_use.bind(cloned_delivery)
        with self.assertRaisesRegex(
            ReplayConstraintReservationRefusal,
            "exact_issued_delivery_required",
        ):
            runtime_run.materializer(governed, cloned_delivery)

        from formation.replay_constraint import (
            OpaqueReplayConstraintCoordinate,
            RuntimeReplayConstraintMaterializer,
            _RUN_ISSUER,
        )

        forged = RuntimeReplayConstraintMaterializer(
            runtime_run,
            delivery.recipient,
            OpaqueReplayConstraintCoordinate(batch.run_id, 999),
            delivery,
            _RUN_ISSUER,
        )
        with self.assertRaisesRegex(
            ReplayConstraintReservationRefusal,
            "exact_registered_constraint_materializer_required",
        ):
            forged.adapt_source(delivery)
        self.assertIsNot(governed, delivery.recipient)

    def test_hidden_extra_fields_and_use_flag_resets_refuse(self):
        values = clean_constraint()
        controller, delivery, source, root = values[5], values[7], values[9], values[12]
        with self.assertRaises(AttributeError):
            object.__setattr__(delivery, "label", "ablation")
        with self.assertRaises(AttributeError):
            object.__setattr__(root.constraint, "constrained_view", object())

        delivery._use.used = False
        with self.assertRaisesRegex(
            ReplayConstraintAppendRefusal, "replay_constraint_root_changed"
        ):
            controller.require_returned_root(root)

        values_2 = clean_constraint()
        controller_2, source_2, root_2 = values_2[5], values_2[9], values_2[12]
        source_2._use.used = False
        with self.assertRaisesRegex(
            ReplayConstraintAppendRefusal, "replay_constraint_root_changed"
        ):
            controller_2.require_returned_root(root_2)

        values_3 = clean_constraint()
        controller_3, batch_3, root_3 = values_3[5], values_3[3], values_3[12]
        batch_3._use.used = False
        with self.assertRaisesRegex(
            ReplayConstraintAppendRefusal, "replay_constraint_root_changed"
        ):
            controller_3.require_returned_root(root_3)

    def test_forged_reservation_fake_runtime_and_controller_registration_refuse(self):
        _, _, _, _, formations, _ = clean_admitted()
        batch = formations.issue_admitted_treatment_batch()
        with self.assertRaisesRegex(
            AdmittedTreatmentBatchRefusal, "formation_constraint_factory_required"
        ):
            ReplayConstraintAppendController(formations, batch)
        uninitialized = object.__new__(ReplayConstraintAppendController)
        with self.assertRaisesRegex(
            AdmittedTreatmentBatchRefusal, "exact_constraint_controller_required"
        ):
            formations.resolve_ablation_root(batch, uninitialized)
        formations._constraint_controller = uninitialized
        with self.assertRaisesRegex(
            AdmittedTreatmentBatchRefusal, "exact_constraint_controller_required"
        ):
            formations.resolve_ablation_root(batch, uninitialized)

        # Use a fresh formation boundary because the failed registration above
        # intentionally contacts and validates the original batch.
        _, _, _, _, formations_2, _ = clean_admitted()
        batch_2 = formations_2.issue_admitted_treatment_batch()
        runtime_run = RuntimeReplayConstraintRun(batch_2.run_id, batch_2)
        controller = formations_2.open_constraint_controller(batch_2)

        class FakeUse:
            def require(self, reservation, candidate_batch):
                return reservation

        from formation.replay_constraint import ReplayConstraintReservation

        forged_reservation = ReplayConstraintReservation(
            batch_2.run_id, batch_2.roots, FakeUse(), object()
        )
        with self.assertRaisesRegex(
            ReplayConstraintAssignmentRefusal, "exact_runtime_reservation_required"
        ):
            controller.assign(forged_reservation)

        assignment, delivery = controller.assign(runtime_run.reservation())
        runtime = runtime_run.materializer(delivery.recipient, delivery)
        source = runtime.adapt_source(delivery)
        handoff = runtime.materialize(source)

        class FakeRuntime:
            def require_current(self, candidate):
                return candidate

        with self.assertRaisesRegex(
            ReplayConstraintAppendRefusal, "exact_constraint_runtime_required"
        ):
            controller.witness(
                FakeRuntime(), handoff, assignment, delivery
            )
        self.assertIs(type(delivery), PublicReplayConstraintDelivery)
        self.assertIsNot(type(delivery), ReplayConstraintBranchRoot)

    def test_caller_created_delivery_use_cannot_open_governed_slot(self):
        _, _, _, _, formations, admitted = clean_admitted()
        batch = formations.issue_admitted_treatment_batch()
        runtime_run = RuntimeReplayConstraintRun(batch.run_id, batch)
        controller = formations.open_constraint_controller(batch)
        _, clean_delivery = controller.assign(runtime_run.reservation())
        governed = admitted[0][6]

        class FakeDeliveryUse:
            def require(self, delivery, root, **_):
                return delivery

            def consume(self, delivery, root):
                return delivery

        forged = PublicReplayConstraintDelivery(
            clean_delivery.run_id,
            governed,
            clean_delivery.target_role,
            clean_delivery.policy,
            FakeDeliveryUse(),
            clean_delivery._registry,
            clean_delivery._issuer,
        )
        with self.assertRaisesRegex(
            ReplayConstraintReservationRefusal,
            "root_bound_constraint_delivery_required",
        ):
            runtime_run.materializer(governed, forged)

    def test_registered_delivery_cannot_be_rebound_to_governed(self):
        _, _, _, _, formations, admitted = clean_admitted()
        batch = formations.issue_admitted_treatment_batch()
        runtime_run = RuntimeReplayConstraintRun(batch.run_id, batch)
        controller = formations.open_constraint_controller(batch)
        _, delivery = controller.assign(runtime_run.reservation())
        governed = admitted[0][6]
        use = type(delivery._use)(delivery._use._issuer)
        forged = PublicReplayConstraintDelivery(
            delivery.run_id,
            governed,
            delivery.target_role,
            delivery.policy,
            use,
            delivery._registry,
            delivery._issuer,
        )
        use.bind(forged)
        delivery._registry._delivery = forged
        with self.assertRaisesRegex(
            ReplayConstraintReservationRefusal, "exact_issued_delivery_required"
        ):
            runtime_run.materializer(governed, forged)

    def test_registered_delivery_rebinding_refuses_after_root_return(self):
        values = clean_constraint()
        controller, delivery, root = values[5], values[7], values[12]
        delivery._registry._delivery = object()
        with self.assertRaisesRegex(
            ReplayConstraintAppendRefusal, "replay_constraint_root_changed"
        ):
            controller.require_returned_root(root)


if __name__ == "__main__":
    unittest.main()
