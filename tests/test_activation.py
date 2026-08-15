from __future__ import annotations

from dataclasses import replace
import unittest

from formation.activation import (
    ActivatedDecisionRoot,
    ActivationConsidered,
    ActivationDecisionRefusal,
    ActivationHandoffBinding,
    RuntimePositiveActivationAuthority,
    WithheldDecisionRoot,
)
from formation.condition_append import INFLUENCE_POLICY, baseline_condition, treatment_condition
from trajectory.activation import ActivationWitnessRefusal, PositiveActivationController
from trajectory.encounter import EncounterWitnessRefusal
from test_encounter import complete_encounters


def complete_activation():
    values, foreground, freeze, bound, encounters, encounter_results = complete_encounters()
    controller = encounters.open_positive_activation_controller()
    results = []
    for use in controller.runtime._uses:
        root = controller.runtime.decide(use.root)
        encounter_witness = next(
            item[7] for item in encounter_results if item[6] is use.root
        )
        witness = controller.witness(encounter_witness, root)
        results.append((use, root, encounter_witness, witness))
    return (
        values,
        foreground,
        freeze,
        bound,
        encounters,
        encounter_results,
        controller,
        results,
    )


class PositiveActivationDecisionTests(unittest.TestCase):
    def test_clean_baseline_withholding_and_governed_activation(self):
        *_, controller, results = complete_activation()
        self.assertEqual(len(controller.require_complete_witnesses()), 2)
        withheld = next(root for _, root, _, _ in results if type(root) is WithheldDecisionRoot)
        activated = next(root for _, root, _, _ in results if type(root) is ActivatedDecisionRoot)
        self.assertEqual(withheld.considered.formation_condition, baseline_condition())
        self.assertEqual(withheld.considered.activation_policy, INFLUENCE_POLICY)
        self.assertEqual(withheld.considered.eligible_versions, ())
        self.assertEqual(withheld.result.refusal, "no_admitted_change")
        self.assertFalse(hasattr(withheld, "handoff_binding"))
        self.assertEqual(activated.considered.formation_condition, treatment_condition())
        self.assertEqual(
            activated.considered.eligible_versions,
            (activated.selected_admission,),
        )
        self.assertIs(activated.selected_admission.proposal, activated.proposal)
        self.assertIs(
            controller.runtime.require_handoff_binding(
                activated.handoff_binding, activated
            ),
            activated.handoff_binding,
        )

    def test_ablation_encounter_is_excluded_without_replay_answer(self):
        *_, encounters, encounter_results = complete_encounters()
        controller = encounters.open_positive_activation_controller()
        accepted = {id(use.root) for use in controller.runtime._uses}
        ablation = next(
            item[6]
            for item in encounter_results
            if encounters.runtime.activation_input_verifier(item[6]).replay_constrained
        )
        self.assertNotIn(id(ablation), accepted)
        with self.assertRaisesRegex(
            ActivationDecisionRefusal, "exact_activation_encounter_required"
        ):
            controller.runtime.decide(ablation)

    def test_pair_classification_is_independent_of_input_order(self):
        *_, encounters, encounter_results = complete_encounters()
        witnesses = encounters.require_complete_witnesses()
        accepted = tuple(
            verifier
            for verifier in (
                encounters.runtime.activation_input_verifier(item.encounter_root)
                for item in witnesses
            )
            if not verifier.replay_constrained
        )
        runtime = RuntimePositiveActivationAuthority(
            tuple(reversed(accepted)), encounters, encounters._activation_permit
        )
        controller = PositiveActivationController(
            encounters, runtime, encounters._activation_permit
        )
        roots = tuple(runtime.decide(use.root) for use in runtime._uses)
        self.assertEqual({type(root) for root in roots}, {WithheldDecisionRoot, ActivatedDecisionRoot})

    def test_decision_is_one_shot_and_retires_encounter_predecessor(self):
        *_, encounters, _ = complete_encounters()
        controller = encounters.open_positive_activation_controller()
        use = controller.runtime._uses[0]
        root = controller.runtime.decide(use.root)
        with self.assertRaisesRegex(
            ActivationDecisionRefusal, "activation_decision_already_consumed"
        ):
            controller.runtime.decide(use.root)
        with self.assertRaisesRegex(
            ActivationDecisionRefusal, "activation_predecessor_not_current"
        ):
            controller.runtime.require_predecessor_current(use.root)
        verifier = controller.runtime.root_verifier(root)
        self.assertIs(verifier.require(root), root)
        self.assertFalse(hasattr(verifier, "_authority"))

    def test_private_flag_reset_does_not_restore_decision_right(self):
        *_, encounters, _ = complete_encounters()
        controller = encounters.open_positive_activation_controller()
        use = controller.runtime._uses[0]
        controller.runtime.decide(use.root)
        use.used = False
        with self.assertRaisesRegex(
            ActivationDecisionRefusal, "activation_decision_already_consumed"
        ):
            controller.runtime.decide(use.root)

    def test_failed_applicability_is_atomic_and_does_not_spend_right(self):
        *_, encounters, _ = complete_encounters()
        controller = encounters.open_positive_activation_controller()
        use = next(item for item in controller.runtime._uses if item.admission is not None)
        original = use.root.situation.depends_on_current_authority
        object.__setattr__(use.root.situation, "depends_on_current_authority", False)
        try:
            with self.assertRaises(ValueError):
                controller.runtime.decide(use.root)
            self.assertFalse(use.used)
            self.assertIsNone(use.decision_root)
            self.assertEqual(len(controller.runtime._decision_roots), 0)
        finally:
            object.__setattr__(use.root.situation, "depends_on_current_authority", original)
        self.assertIsInstance(controller.runtime.decide(use.root), ActivatedDecisionRoot)

    def test_absent_derived_from_refuses_atomically(self):
        *_, encounters, _ = complete_encounters()
        controller = encounters.open_positive_activation_controller()
        use = next(item for item in controller.runtime._uses if item.admission is not None)
        original = use.root.situation.derived_from
        object.__setattr__(use.root.situation, "derived_from", "")
        try:
            with self.assertRaises(ValueError):
                controller.runtime.decide(use.root)
            self.assertFalse(use.used)
            self.assertIsNone(use.decision_root)
            self.assertEqual(controller.runtime._decision_roots, [])
        finally:
            object.__setattr__(use.root.situation, "derived_from", original)

    def test_non_boolean_authority_dependency_refuses(self):
        *_, encounters, _ = complete_encounters()
        controller = encounters.open_positive_activation_controller()
        use = next(item for item in controller.runtime._uses if item.admission is not None)
        original = use.root.situation.depends_on_current_authority
        object.__setattr__(use.root.situation, "depends_on_current_authority", 1)
        try:
            with self.assertRaisesRegex(
                ActivationDecisionRefusal, "positive_applicability_not_met"
            ):
                controller.runtime.decide(use.root)
            self.assertFalse(use.used)
        finally:
            object.__setattr__(
                use.root.situation, "depends_on_current_authority", original
            )

    def test_activation_root_cannot_reach_full_handoff_or_trajectory_state(self):
        *_, controller, results = complete_activation()
        activated = next(root for _, root, _, _ in results if type(root) is ActivatedDecisionRoot)
        verifier = controller.runtime.root_verifier(activated)
        for value in (activated, activated.handoff_binding, verifier):
            for forbidden in (
                "handoff", "registry", "assignment", "freeze",
                "comparison_group", "case_family", "expected_result",
            ):
                self.assertFalse(hasattr(value, forbidden), (type(value), forbidden))
        self.assertFalse(hasattr(verifier, "_runtime"))

    def test_equal_reconstructed_binding_and_root_refuse(self):
        *_, controller, results = complete_activation()
        activated = next(root for _, root, _, _ in results if type(root) is ActivatedDecisionRoot)
        with self.assertRaisesRegex(
            ActivationDecisionRefusal, "exact_activation_handoff_binding_required"
        ):
            controller.runtime.require_handoff_binding(
                replace(activated.handoff_binding), activated
            )
        with self.assertRaisesRegex(
            ActivationDecisionRefusal, "exact_activation_decision_root_required"
        ):
            controller.runtime.require_root(replace(activated))

    def test_admission_and_proposal_mutation_refuse_after_decision(self):
        *_, controller, results = complete_activation()
        activated = next(root for _, root, _, _ in results if type(root) is ActivatedDecisionRoot)
        original = activated.proposal.representation
        object.__setattr__(activated.proposal, "representation", "copied lesson")
        try:
            with self.assertRaises(ValueError):
                controller.runtime.require_root(activated)
        finally:
            object.__setattr__(activated.proposal, "representation", original)

    def test_decision_use_cannot_substitute_equal_ablation_lineage(self):
        *_, encounters, encounter_results = complete_encounters()
        controller = encounters.open_positive_activation_controller()
        governed = next(
            item for item in controller.runtime._uses if item.admission is not None
        )
        ablation_root = next(
            item[6]
            for item in encounter_results
            if encounters.runtime.activation_input_verifier(item[6]).replay_constrained
        )
        ablation_admission = ablation_root.predecessor.admitted_root.admission
        ablation_proposal = ablation_root.predecessor.admitted_root.proposal
        self.assertEqual(governed.proposal.representation, ablation_proposal.representation)
        self.assertIsNot(governed.admission, ablation_admission)
        governed.admission = ablation_admission
        governed.proposal = ablation_proposal
        with self.assertRaisesRegex(
            ActivationDecisionRefusal, "exact_activation_encounter_required"
        ):
            controller.runtime.decide(governed.root)
        self.assertFalse(governed.used)
        self.assertIsNone(governed.decision_root)

    def test_admitted_scope_and_status_refuse_before_decision(self):
        for field, replacement in (("scope", "all objects"), ("status", "revoked")):
            with self.subTest(field=field):
                *_, encounters, _ = complete_encounters()
                controller = encounters.open_positive_activation_controller()
                use = next(
                    item for item in controller.runtime._uses if item.admission is not None
                )
                original = getattr(use.admission, field)
                object.__setattr__(use.admission, field, replacement)
                try:
                    with self.assertRaises(ValueError):
                        controller.runtime.decide(use.root)
                    self.assertFalse(use.used)
                    self.assertIsNone(use.decision_root)
                finally:
                    object.__setattr__(use.admission, field, original)

    def test_pair_intake_refuses_missing_duplicate_and_wrong_condition(self):
        *_, encounters, _ = complete_encounters()
        verifiers = tuple(
            encounters.runtime.activation_input_verifier(witness.encounter_root)
            for witness in encounters.require_complete_witnesses()
            if not encounters.runtime.activation_input_verifier(
                witness.encounter_root
            ).replay_constrained
        )
        with self.assertRaisesRegex(
            ActivationDecisionRefusal, "exact_positive_activation_pair_required"
        ):
            RuntimePositiveActivationAuthority(
                (verifiers[0],), encounters, encounters._activation_permit
            )
        with self.assertRaisesRegex(
            ActivationDecisionRefusal, "exact_positive_activation_pair_required"
        ):
            RuntimePositiveActivationAuthority(
                (verifiers[0], verifiers[0]), encounters, encounters._activation_permit
            )
        governed = next(item for item in verifiers if item.admission is not None)
        original = governed.condition
        governed.condition = baseline_condition()
        try:
            with self.assertRaisesRegex(
                ActivationDecisionRefusal, "exact_positive_activation_pair_required"
            ):
                RuntimePositiveActivationAuthority(
                    verifiers, encounters, encounters._activation_permit
                )
            self.assertIsNone(encounters._activation_runtime)
        finally:
            governed.condition = original

    def test_pair_intake_refuses_baseline_admission_and_governed_absence(self):
        for change, message in (
            ("baseline_admission", "baseline_eligible_state_not_empty"),
            ("governed_absence", "governed_admission_required"),
        ):
            with self.subTest(change=change):
                *_, encounters, _ = complete_encounters()
                verifiers = tuple(
                    encounters.runtime.activation_input_verifier(witness.encounter_root)
                    for witness in encounters.require_complete_witnesses()
                    if not encounters.runtime.activation_input_verifier(
                        witness.encounter_root
                    ).replay_constrained
                )
                baseline = next(item for item in verifiers if item.admission is None)
                governed = next(item for item in verifiers if item.admission is not None)
                if change == "baseline_admission":
                    baseline.admission = governed.admission
                    baseline.proposal = governed.proposal
                else:
                    governed.admission = None
                    governed.proposal = None
                with self.assertRaises(ValueError):
                    RuntimePositiveActivationAuthority(
                        verifiers, encounters, encounters._activation_permit
                    )
                self.assertIsNone(encounters._activation_runtime)

    def test_second_activation_controller_refuses(self):
        *_, encounters, _ = complete_encounters()
        encounters.open_positive_activation_controller()
        with self.assertRaisesRegex(
            EncounterWitnessRefusal, "activation_controller_already_opened"
        ):
            encounters.open_positive_activation_controller()

    def test_incomplete_duplicate_and_forged_witnesses_refuse(self):
        *_, encounters, encounter_results = complete_encounters()
        controller = encounters.open_positive_activation_controller()
        use = controller.runtime._uses[0]
        root = controller.runtime.decide(use.root)
        encounter_witness = next(item[7] for item in encounter_results if item[6] is use.root)
        witness = controller.witness(encounter_witness, root)
        with self.assertRaisesRegex(
            ActivationWitnessRefusal, "two_activation_witnesses_required"
        ):
            controller.require_complete_witnesses()
        with self.assertRaises(ActivationWitnessRefusal):
            controller.witness(encounter_witness, root)
        with self.assertRaisesRegex(
            ActivationWitnessRefusal, "exact_activation_witness_required"
        ):
            controller.require_witness(replace(witness))

    def test_wrong_encounter_witness_refuses(self):
        *_, encounters, encounter_results = complete_encounters()
        controller = encounters.open_positive_activation_controller()
        use = controller.runtime._uses[0]
        root = controller.runtime.decide(use.root)
        wrong_witness = next(item[7] for item in encounter_results if item[6] is not use.root)
        with self.assertRaisesRegex(
            ActivationWitnessRefusal, "activation_witness_chain_mismatch"
        ):
            controller.witness(wrong_witness, root)

    def test_no_bytes_request_action_or_formation_claim(self):
        *_, controller, results = complete_activation()
        for _, root, _, witness in results:
            values = [root, root.considered, root.result, witness]
            if type(root) is ActivatedDecisionRoot:
                values.append(root.handoff_binding)
            for value in values:
                for forbidden in (
                    "artifact", "digest", "model_request", "action",
                    "consequence", "formation_effect", "case_family",
                ):
                    self.assertFalse(hasattr(value, forbidden))

    def test_raw_malformed_values_fail_closed(self):
        *_, encounters, _ = complete_encounters()
        controller = encounters.open_positive_activation_controller()
        for raw in (None, {}, object(), "governed"):
            with self.subTest(raw=type(raw).__name__):
                with self.assertRaises(ActivationDecisionRefusal):
                    controller.runtime.decide(raw)
                with self.assertRaises(ActivationDecisionRefusal):
                    controller.runtime.require_root(raw)
                with self.assertRaises((ActivationWitnessRefusal, EncounterWitnessRefusal)):
                    controller.witness(raw, raw)

    def test_caller_created_considered_binding_and_controller_refuse(self):
        *_, encounters, _ = complete_encounters()
        controller = encounters.open_positive_activation_controller()
        use = controller.runtime._uses[0]
        fake_considered = ActivationConsidered(
            use.root.run_id,
            use.root,
            use.root.encounter,
            use.condition,
            INFLUENCE_POLICY,
            (),
            use.root.situation,
            object(),
        )
        self.assertNotIn(fake_considered, [item.considered for item in controller.runtime._decision_roots])
        with self.assertRaises(ValueError):
            ActivationHandoffBinding(use.root.run_id, object(), object())
            controller.runtime.require_handoff_binding(object(), object())


if __name__ == "__main__":
    unittest.main()
