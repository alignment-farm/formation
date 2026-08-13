from __future__ import annotations

from dataclasses import replace
import unittest

from formation.admitted_root import (
    ADMISSION_ORDER,
    CANDIDATE_REPRESENTATION,
    PROPOSAL_ORDER,
    AdmissionRefusal,
    FormationCoordinateRefusal,
    FormationSourceRefusal,
    ProposalRefusal,
    RuntimeFormationRun,
    admission_public_semantics,
    proposal_public_semantics,
)
from trajectory.admitted_root import (
    FormationAppendController,
    FormationAppendRefusal,
    FormationValidationRefusal,
    validate_fixture_admission,
    validate_fixture_proposal,
)
from trajectory.fixture_condition import (
    TreatmentRootBatchRefusal,
)
from test_fixture_condition import materialize_all


def clean_admitted():
    _, _, _, _, conditions, condition_results = materialize_all()
    batch = conditions.issue_treatment_root_batch()
    runtime_run = RuntimeFormationRun(batch.run_id, batch)
    controller = FormationAppendController(conditions, batch)
    results = []
    for root in batch.roots:
        runtime = runtime_run.materializer(root)
        source = runtime.adapt_source()
        proposal_handoff = runtime.propose(source)
        proposal_witness = controller.witness_proposal(runtime, proposal_handoff)
        admission_handoff = runtime.admit(proposal_handoff)
        admission_witness = controller.witness_admission(
            runtime, admission_handoff, proposal_witness
        )
        admitted_root = controller.append(
            runtime,
            admission_handoff,
            proposal_witness,
            admission_witness,
        )
        results.append(
            (
                runtime,
                source,
                proposal_handoff,
                proposal_witness,
                admission_handoff,
                admission_witness,
                admitted_root,
            )
        )
    return conditions, condition_results, batch, runtime_run, controller, results


class AdmittedRootTests(unittest.TestCase):
    def test_clean_two_treatment_roots_are_semantically_equal_and_distinct(self):
        _, condition_results, batch, _, controller, results = clean_admitted()
        self.assertEqual(batch.roots, (condition_results[1][5], condition_results[2][5]))
        first, second = results
        self.assertEqual(first[2].proposal.order, PROPOSAL_ORDER)
        self.assertEqual(first[4].admission.order, ADMISSION_ORDER)
        self.assertEqual(first[2].proposal.representation, CANDIDATE_REPRESENTATION)
        self.assertEqual(
            proposal_public_semantics(first[2].proposal),
            proposal_public_semantics(second[2].proposal),
        )
        self.assertEqual(
            admission_public_semantics(first[4].admission),
            admission_public_semantics(second[4].admission),
        )
        self.assertIsNot(first[2].proposal, second[2].proposal)
        self.assertIsNot(first[4].admission, second[4].admission)
        self.assertIsNot(first[6].head, second[6].head)
        self.assertIs(controller.require_returned_root(first[6]), first[6])
        self.assertFalse(hasattr(first[2], "artifact"))
        self.assertFalse(hasattr(first[4], "artifact"))
        self.assertFalse(hasattr(first[6], "binding"))
        self.assertIs(first[2].proposal._authorship.source, first[1])
        self.assertIs(first[4].admission._decision.proposal, first[2].proposal)
        self.assertIsNot(first[2].proposal._authorship._issuer, first[2].proposal._issuer)
        self.assertIsNot(first[4].admission._decision._issuer, first[4].admission._issuer)

    def test_batch_is_exact_label_blind_canonical_and_one_shot(self):
        _, _, _, _, conditions, results = materialize_all(
            ("governed", "baseline", "ablation")
        )
        batch = conditions.issue_treatment_root_batch()
        self.assertEqual(batch.roots, (results[0][5], results[2][5]))
        forged = replace(batch, roots=tuple(reversed(batch.roots)))
        with self.assertRaisesRegex(
            TreatmentRootBatchRefusal, "exact_treatment_root_batch_required"
        ):
            RuntimeFormationRun(batch.run_id, forged)
        RuntimeFormationRun(batch.run_id, batch)
        with self.assertRaisesRegex(
            TreatmentRootBatchRefusal, "treatment_root_batch_already_consumed"
        ):
            RuntimeFormationRun(batch.run_id, batch)
        with self.assertRaisesRegex(
            TreatmentRootBatchRefusal, "treatment_root_batch_already_issued"
        ):
            conditions.issue_treatment_root_batch()

    def test_baseline_and_label_bearing_run_refuse(self):
        _, condition_results, batch, _, _, _ = clean_admitted()
        # The clean helper consumed its batch, so create another run for input attacks.
        _, _, _, _, conditions, fresh_results = materialize_all()
        fresh_batch = conditions.issue_treatment_root_batch()
        with self.assertRaisesRegex(FormationSourceRefusal, "label_bearing_run_id"):
            RuntimeFormationRun("run-governed-hidden", fresh_batch)

        _, _, _, _, conditions_2, roots_2 = materialize_all()
        batch_2 = conditions_2.issue_treatment_root_batch()
        runtime_run = RuntimeFormationRun(batch_2.run_id, batch_2)
        with self.assertRaisesRegex(FormationSourceRefusal, "exact_treatment_root_required"):
            runtime_run.materializer(roots_2[0][5])
        self.assertNotIn(condition_results[0][5], batch.roots)

    def test_source_is_derived_from_exact_retained_root_and_consumed_once(self):
        _, _, _, _, conditions, _ = materialize_all()
        batch = conditions.issue_treatment_root_batch()
        runtime_run = RuntimeFormationRun(batch.run_id, batch)
        runtime = runtime_run.materializer(batch.roots[0])
        source = runtime.adapt_source()
        self.assertEqual(source.source_consequence.coordinate, "D-C-005")
        self.assertEqual(source.source_experience.coordinate, "D-C-006")
        self.assertIs(source.source_consequence.root, batch.roots[0])
        with self.assertRaisesRegex(FormationSourceRefusal, "formation_source_already_issued"):
            runtime.adapt_source()
        proposal = runtime.propose(source)
        with self.assertRaisesRegex(ProposalRefusal, "proposal_already_issued"):
            runtime.propose(source)
        self.assertIs(proposal.source, source)

    def test_equal_reconstructed_source_and_proposal_refuse(self):
        _, _, _, _, conditions, _ = materialize_all()
        batch = conditions.issue_treatment_root_batch()
        runtime_run = RuntimeFormationRun(batch.run_id, batch)
        runtime = runtime_run.materializer(batch.roots[0])
        source = runtime.adapt_source()
        with self.assertRaisesRegex(FormationSourceRefusal, "exact_formation_source_required"):
            runtime.propose(replace(source))
        proposal_handoff = runtime.propose(source)
        forged = replace(
            proposal_handoff,
            proposal=replace(proposal_handoff.proposal),
        )
        with self.assertRaisesRegex(ProposalRefusal, "exact_current_proposal_handoff_required"):
            runtime.admit(forged)

    def test_source_nested_mutation_and_coordinate_mutation_refuse(self):
        _, _, _, _, conditions, _ = materialize_all()
        batch = conditions.issue_treatment_root_batch()
        runtime_run = RuntimeFormationRun(batch.run_id, batch)
        runtime = runtime_run.materializer(batch.roots[0])
        source = runtime.adapt_source()
        object.__setattr__(
            source.source_consequence,
            "artifact",
            bytes(bytearray(source.source_consequence.artifact)),
        )
        with self.assertRaisesRegex(FormationSourceRefusal, "formation_source_changed"):
            runtime.propose(source)

        _, _, _, _, conditions_2, _ = materialize_all()
        batch_2 = conditions_2.issue_treatment_root_batch()
        runtime_2 = RuntimeFormationRun(batch_2.run_id, batch_2).materializer(
            batch_2.roots[0]
        )
        source_2 = runtime_2.adapt_source()
        runtime_2._proposal_coordinate._sequence = 999
        with self.assertRaisesRegex(
            FormationCoordinateRefusal, "formation_reservation_changed"
        ):
            runtime_2.propose(source_2)

    def test_post_batch_prefix_and_condition_binding_mutations_refuse_before_source(self):
        for binding_name in ("prefix", "condition"):
            with self.subTest(binding=binding_name):
                _, _, _, _, conditions, _ = materialize_all()
                batch = conditions.issue_treatment_root_batch()
                runtime = RuntimeFormationRun(batch.run_id, batch).materializer(
                    batch.roots[0]
                )
                binding = (
                    batch.roots[0].prefix_root.binding
                    if binding_name == "prefix"
                    else batch.roots[0].condition_binding
                )
                object.__setattr__(binding, "digest", "0" * 64)
                with self.assertRaisesRegex(
                    FormationCoordinateRefusal, "formation_reservation_changed"
                ):
                    runtime.adapt_source()

    def test_proposal_semantic_mutations_refuse_independently(self):
        _, _, _, _, _, results = clean_admitted()
        clean = results[0][2].proposal
        mutations = (
            replace(clean, representation=clean.representation + " extra"),
            replace(clean, author="formation_runtime"),
            replace(clean, recorder="trajectory_harness"),
            replace(clean, order=9),
            replace(clean, parents=frozenset()),
            replace(clean, projection=replace(clean.projection, expiry="later")),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaisesRegex(
                FormationValidationRefusal, "invalid_fixture_proposal"
            ):
                validate_fixture_proposal(mutation)

    def test_admission_semantic_mutations_refuse_independently(self):
        _, _, _, _, _, results = clean_admitted()
        clean = results[0][4].admission
        mutations = (
            replace(clean, decision_authority="formation_runtime"),
            replace(clean, recorder="trajectory_harness"),
            replace(clean, status="rejected"),
            replace(clean, scope=clean.scope + " broader"),
            replace(clean, trial="synthetic"),
            replace(clean, warrant=replace(clean.warrant, satisfied_checks=tuple())),
            replace(clean, parents=frozenset()),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaisesRegex(
                FormationValidationRefusal, "invalid_fixture_admission"
            ):
                validate_fixture_admission(mutation)

    def test_admission_requires_exact_current_proposal_and_is_one_shot(self):
        _, _, _, _, conditions, _ = materialize_all()
        batch = conditions.issue_treatment_root_batch()
        runtime_run = RuntimeFormationRun(batch.run_id, batch)
        first = runtime_run.materializer(batch.roots[0])
        second = runtime_run.materializer(batch.roots[1])
        first_source = first.adapt_source()
        second_source = second.adapt_source()
        first_proposal = first.propose(first_source)
        second_proposal = second.propose(second_source)
        with self.assertRaisesRegex(ProposalRefusal, "exact_current_proposal_handoff_required"):
            first.admit(second_proposal)
        admission = first.admit(first_proposal)
        with self.assertRaisesRegex(
            AdmissionRefusal, "proposal_already_admitted_or_admission_issued"
        ):
            first.admit(first_proposal)
        self.assertIs(admission.admission.proposal, first_proposal.proposal)

    def test_harness_witnesses_cannot_be_forged_reused_or_crossed(self):
        _, _, _, _, conditions, _ = materialize_all()
        batch = conditions.issue_treatment_root_batch()
        runtime_run = RuntimeFormationRun(batch.run_id, batch)
        controller = FormationAppendController(conditions, batch)
        first = runtime_run.materializer(batch.roots[0])
        second = runtime_run.materializer(batch.roots[1])
        first_source = first.adapt_source()
        second_source = second.adapt_source()
        first_proposal = first.propose(first_source)
        second_proposal = second.propose(second_source)
        first_witness = controller.witness_proposal(first, first_proposal)
        second_witness = controller.witness_proposal(second, second_proposal)
        first_admission = first.admit(first_proposal)
        with self.assertRaisesRegex(
            FormationAppendRefusal, "admission_proposal_witness_mismatch"
        ):
            controller.witness_admission(first, first_admission, second_witness)
        first_admission_witness = controller.witness_admission(
            first, first_admission, first_witness
        )
        with self.assertRaisesRegex(FormationAppendRefusal, "admission_already_witnessed"):
            controller.witness_admission(first, first_admission, first_witness)
        with self.assertRaisesRegex(FormationAppendRefusal, "exact_proposal_witness_required"):
            controller.append(
                first,
                first_admission,
                replace(first_witness),
                first_admission_witness,
            )

    def test_only_one_formation_controller_can_own_the_batch(self):
        _, _, _, _, conditions, _ = materialize_all()
        batch = conditions.issue_treatment_root_batch()
        FormationAppendController(conditions, batch)
        with self.assertRaisesRegex(
            TreatmentRootBatchRefusal, "formation_controller_already_registered"
        ):
            FormationAppendController(conditions, batch)

    def test_returned_root_is_exact_distinct_and_does_not_claim_d_a_010(self):
        _, _, _, _, controller, results = clean_admitted()
        root = results[0][6]
        self.assertIsNot(root, root.condition_root)
        self.assertIs(root.head, root.admission.coordinate)
        self.assertFalse(hasattr(root, "replay_constraint"))
        self.assertFalse(hasattr(root, "D_A_010"))
        with self.assertRaisesRegex(FormationAppendRefusal, "exact_admitted_root_required"):
            controller.require_returned_root(root.condition_root)
        with self.assertRaisesRegex(FormationAppendRefusal, "exact_admitted_root_required"):
            controller.require_returned_root(replace(root))

    def test_post_handoff_equal_reconstruction_and_mutation_refuse(self):
        _, _, _, _, conditions, _ = materialize_all()
        batch = conditions.issue_treatment_root_batch()
        runtime = RuntimeFormationRun(batch.run_id, batch).materializer(batch.roots[0])
        source = runtime.adapt_source()
        proposal = runtime.propose(source)
        object.__setattr__(
            proposal.proposal,
            "projection",
            replace(proposal.proposal.projection),
        )
        with self.assertRaisesRegex(ProposalRefusal, "proposal_handoff_changed"):
            runtime.require_current_proposal(proposal)

        _, _, _, _, conditions_2, _ = materialize_all()
        batch_2 = conditions_2.issue_treatment_root_batch()
        runtime_2 = RuntimeFormationRun(batch_2.run_id, batch_2).materializer(
            batch_2.roots[0]
        )
        source_2 = runtime_2.adapt_source()
        proposal_2 = runtime_2.propose(source_2)
        admission = runtime_2.admit(proposal_2)
        object.__setattr__(
            admission.admission,
            "warrant",
            replace(admission.admission.warrant),
        )
        with self.assertRaisesRegex(AdmissionRefusal, "admission_handoff_changed"):
            runtime_2.require_current_admission(admission)

    def test_nested_mutation_after_witness_and_after_root_return_refuses(self):
        _, _, _, _, conditions, _ = materialize_all()
        batch = conditions.issue_treatment_root_batch()
        runtime = RuntimeFormationRun(batch.run_id, batch).materializer(batch.roots[0])
        controller = FormationAppendController(conditions, batch)
        source = runtime.adapt_source()
        proposal = runtime.propose(source)
        proposal_witness = controller.witness_proposal(runtime, proposal)
        admission = runtime.admit(proposal)
        admission_witness = controller.witness_admission(
            runtime, admission, proposal_witness
        )
        object.__setattr__(admission.admission.warrant, "satisfied_checks", tuple())
        with self.assertRaisesRegex(
            (AdmissionRefusal, FormationAppendRefusal),
            "changed_or_forged|admission_handoff_changed",
        ):
            controller.append(
                runtime, admission, proposal_witness, admission_witness
            )

        _, _, _, _, clean_controller, clean_results = clean_admitted()
        admitted_root = clean_results[0][6]
        object.__setattr__(admitted_root.proposal.projection, "expiry", "later")
        with self.assertRaisesRegex(
            FormationAppendRefusal, "admitted_root_changed"
        ):
            clean_controller.require_returned_root(admitted_root)

    def test_reconstructed_authority_results_refuse(self):
        _, _, _, _, conditions, _ = materialize_all()
        batch = conditions.issue_treatment_root_batch()
        runtime = RuntimeFormationRun(batch.run_id, batch).materializer(batch.roots[0])
        source = runtime.adapt_source()
        proposal = runtime.propose(source)
        object.__setattr__(
            proposal.proposal,
            "_authorship",
            replace(proposal.proposal._authorship),
        )
        with self.assertRaisesRegex(
            ProposalRefusal, "interpreter_authorship_changed_or_forged"
        ):
            runtime.require_current_proposal(proposal)

    def test_reconstructed_authority_results_refuse_after_root_return(self):
        for authority in ("interpreter", "governor"):
            with self.subTest(authority=authority):
                _, _, _, _, controller, results = clean_admitted()
                root = results[0][6]
                if authority == "interpreter":
                    object.__setattr__(
                        root.proposal,
                        "_authorship",
                        replace(root.proposal._authorship),
                    )
                else:
                    object.__setattr__(
                        root.admission,
                        "_decision",
                        replace(root.admission._decision),
                    )
                with self.assertRaisesRegex(
                    FormationAppendRefusal, "admitted_root_changed"
                ):
                    controller.require_returned_root(root)

    def test_retained_source_mutation_refuses_after_root_return(self):
        mutations = ("receipt_copy", "receipt_bytes", "condition_copy")
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                _, _, _, _, controller, results = clean_admitted()
                root = results[0][6]
                source = root.proposal._authorship.source
                if mutation == "receipt_copy":
                    object.__setattr__(
                        source,
                        "source_consequence",
                        replace(source.source_consequence),
                    )
                elif mutation == "receipt_bytes":
                    object.__setattr__(
                        source.source_consequence,
                        "artifact",
                        b"not-a-receipt\n",
                    )
                else:
                    object.__setattr__(
                        source,
                        "public_condition",
                        replace(source.public_condition),
                    )
                with self.assertRaisesRegex(
                    FormationAppendRefusal, "admitted_root_changed"
                ):
                    controller.require_returned_root(root)

    def test_parent_reconstruction_and_coordinate_mutation_refuse_after_return(self):
        mutations = (
            "proposal_parents",
            "admission_parents",
            "proposal_coordinate",
            "admission_coordinate",
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                _, _, _, _, controller, results = clean_admitted()
                root = results[0][6]
                if mutation == "proposal_parents":
                    object.__setattr__(
                        root.proposal,
                        "parents",
                        frozenset(tuple(root.proposal.parents)),
                    )
                elif mutation == "admission_parents":
                    object.__setattr__(
                        root.admission,
                        "parents",
                        frozenset(tuple(root.admission.parents)),
                    )
                elif mutation == "proposal_coordinate":
                    root.proposal.coordinate._sequence = 999
                else:
                    root.admission.coordinate._run_id = "other"
                with self.assertRaisesRegex(
                    FormationAppendRefusal, "admitted_root_changed"
                ):
                    controller.require_returned_root(root)


if __name__ == "__main__":
    unittest.main()
