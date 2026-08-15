from __future__ import annotations

from dataclasses import replace
import unittest

from formation.activation import ActivationDecisionRefusal
from formation.practice_request import (
    ActivatedPracticeRequest,
    ActivatedRequestRoot,
    PracticeRequestRefusal,
    RuntimePositivePracticeRequestAuthority,
    WithheldPracticeRequest,
    WithheldRequestRoot,
)
from trajectory.activation import ActivationWitnessRefusal
from trajectory.practice_request import PracticeRequestWitnessRefusal
from test_activation import complete_activation


def complete_requests():
    *prefix, decisions, decision_results = complete_activation()
    controller = decisions.open_positive_practice_request_controller()
    results = []
    for use in controller.runtime._uses:
        root = controller.runtime.prepare(use.root)
        decision_witness = next(
            item[3] for item in decision_results if item[1] is use.root
        )
        witness = controller.witness(decision_witness, root)
        results.append((use, root, decision_witness, witness))
    return (*prefix, decisions, decision_results, controller, results)


class PracticeRequestTests(unittest.TestCase):
    def test_clean_withheld_and_activated_requests(self):
        *_, controller, results = complete_requests()
        self.assertEqual(len(controller.require_complete_witnesses()), 2)
        withheld = next(root for _, root, _, _ in results if type(root) is WithheldRequestRoot)
        activated = next(root for _, root, _, _ in results if type(root) is ActivatedRequestRoot)
        self.assertIsInstance(withheld.request, WithheldPracticeRequest)
        self.assertIsInstance(activated.request, ActivatedPracticeRequest)
        self.assertIs(withheld.request.situation, withheld.predecessor.considered.situation)
        self.assertIs(activated.request.situation, activated.predecessor.considered.situation)
        self.assertIs(activated.request.intervention, activated.intervention)
        self.assertIs(
            activated.intervention.selected_admission,
            activated.predecessor.selected_admission,
        )

    def test_withheld_intervention_absence_is_structural(self):
        *_, controller, results = complete_requests()
        withheld = next(root for _, root, _, _ in results if type(root) is WithheldRequestRoot)
        for value in (withheld, withheld.request):
            for forbidden in (
                "intervention",
                "handoff_binding",
                "selected_admission",
                "proposal",
                "intervention_procedure",
                "intervention_content",
                "selection_reason",
            ):
                self.assertFalse(hasattr(value, forbidden), forbidden)

    def test_activation_witnessing_does_not_consume_handoff(self):
        *_, decisions, decision_results = complete_activation()
        activated = next(item[1] for item in decision_results if hasattr(item[1], "handoff_binding"))
        handoff_use = next(
            item
            for item in decisions.runtime._handoff_uses
            if item.binding is activated.handoff_binding
        )
        self.assertFalse(handoff_use.request_consumed)
        self.assertIsNone(handoff_use.request_consumer)
        requests = decisions.open_positive_practice_request_controller()
        root = requests.runtime.prepare(activated)
        self.assertIsInstance(root, ActivatedRequestRoot)
        self.assertTrue(handoff_use.request_consumed)
        self.assertIs(handoff_use.request_consumer, requests.runtime)

    def test_prepare_is_one_shot_and_retires_decision_predecessor(self):
        *_, decisions, _ = complete_activation()
        controller = decisions.open_positive_practice_request_controller()
        use = controller.runtime._uses[0]
        root = controller.runtime.prepare(use.root)
        with self.assertRaisesRegex(PracticeRequestRefusal, "practice_request_already_prepared"):
            controller.runtime.prepare(use.root)
        with self.assertRaisesRegex(
            PracticeRequestRefusal, "practice_decision_predecessor_not_current"
        ):
            controller.runtime.require_predecessor_current(use.root)
        self.assertIs(controller.runtime.require_root(root), root)

    def test_flag_resets_restore_neither_right(self):
        *_, decisions, _ = complete_activation()
        controller = decisions.open_positive_practice_request_controller()
        use = next(item for item in controller.runtime._uses if hasattr(item.root, "handoff_binding"))
        root = controller.runtime.prepare(use.root)
        handoff_use = next(
            item
            for item in decisions.runtime._handoff_uses
            if item.binding is root.predecessor.handoff_binding
        )
        use.used = False
        use.request_root = None
        handoff_use.request_consumed = False
        handoff_use.request_consumer = None
        with self.assertRaises(PracticeRequestRefusal):
            controller.runtime.prepare(use.root)
        with self.assertRaises(ValueError):
            decisions.runtime._consume_request_handoff(
                controller.runtime,
                root.predecessor.handoff_binding,
                root.predecessor,
                object(),
            )

    def test_live_verifier_substitution_refuses(self):
        *_, decisions, _ = complete_activation()
        controller = decisions.open_positive_practice_request_controller()
        use = controller.runtime._uses[0]

        class PermissiveVerifier:
            def require(self, root):
                return root

        use.verifier = PermissiveVerifier()
        with self.assertRaisesRegex(
            PracticeRequestRefusal, "exact_practice_decision_root_required"
        ):
            controller.runtime.prepare(use.root)
        self.assertFalse(use.used)
        self.assertEqual(use._preparations, [])

    def test_failed_preflight_consumes_neither_right(self):
        *_, decisions, _ = complete_activation()
        controller = decisions.open_positive_practice_request_controller()
        use = next(item for item in controller.runtime._uses if hasattr(item.root, "handoff_binding"))
        handoff_use = next(
            item
            for item in decisions.runtime._handoff_uses
            if item.binding is use.root.handoff_binding
        )
        original = use.root.considered.situation.derived_from
        object.__setattr__(use.root.considered.situation, "derived_from", "changed")
        try:
            with self.assertRaises(ValueError):
                controller.runtime.prepare(use.root)
            self.assertFalse(use.used)
            self.assertIsNone(use.request_root)
            self.assertFalse(handoff_use.request_consumed)
            self.assertIsNone(handoff_use.request_consumer)
            self.assertEqual(controller.runtime._roots, [])
        finally:
            object.__setattr__(use.root.considered.situation, "derived_from", original)

    def test_private_registry_cannot_be_reached_from_request_inputs(self):
        *_, controller, results = complete_requests()
        activated = next(root for _, root, _, _ in results if type(root) is ActivatedRequestRoot)
        verifier = controller._decisions.runtime.root_verifier(activated.predecessor)
        for value in (
            activated.predecessor,
            activated.predecessor.handoff_binding,
            verifier,
        ):
            for forbidden in ("registry", "handoff", "_handoff_uses", "assignment", "case_family"):
                self.assertFalse(hasattr(value, forbidden), (type(value), forbidden))

    def test_equal_reconstructed_request_and_root_refuse(self):
        *_, controller, results = complete_requests()
        for _, root, _, _ in results:
            with self.assertRaisesRegex(
                PracticeRequestRefusal, "exact_practice_request_root_required"
            ):
                controller.runtime.require_root(replace(root))
            rebuilt_request = replace(root.request)
            object.__setattr__(root, "request", rebuilt_request)
            with self.assertRaisesRegex(PracticeRequestRefusal, "practice_request_root_changed"):
                controller.runtime.require_root(root)

    def test_request_mutations_refuse_after_return(self):
        *_, controller, results = complete_requests()
        root = results[0][1]
        original = root.request.actor
        object.__setattr__(root.request, "actor", "fixture-coach-v0")
        try:
            with self.assertRaisesRegex(PracticeRequestRefusal, "practice_request_root_changed"):
                controller.runtime.require_root(root)
        finally:
            object.__setattr__(root.request, "actor", original)

    def test_pair_classification_is_order_independent(self):
        *_, decisions, _ = complete_activation()
        witnesses = decisions.require_complete_witnesses()
        verifiers = tuple(
            decisions.runtime.root_verifier(item.decision_root) for item in witnesses
        )
        runtime = RuntimePositivePracticeRequestAuthority(
            tuple(reversed(verifiers)),
            decisions.runtime,
            decisions,
            decisions._practice_permit,
        )
        roots = tuple(runtime.prepare(use.root) for use in runtime._uses)
        self.assertEqual({type(root) for root in roots}, {WithheldRequestRoot, ActivatedRequestRoot})

    def test_pair_intake_refuses_missing_duplicate_and_caller_verifier(self):
        *_, decisions, _ = complete_activation()
        verifiers = tuple(
            decisions.runtime.root_verifier(item.decision_root)
            for item in decisions.require_complete_witnesses()
        )
        with self.assertRaises(PracticeRequestRefusal):
            RuntimePositivePracticeRequestAuthority(
                (verifiers[0],), decisions.runtime, decisions, decisions._practice_permit
            )
        with self.assertRaises(PracticeRequestRefusal):
            RuntimePositivePracticeRequestAuthority(
                (verifiers[0], verifiers[0]),
                decisions.runtime,
                decisions,
                decisions._practice_permit,
            )

        class FakeVerifier:
            root = verifiers[0].root
            def require(self, root):
                return root

        with self.assertRaises(ValueError):
            RuntimePositivePracticeRequestAuthority(
                (FakeVerifier(), verifiers[1]),
                decisions.runtime,
                decisions,
                decisions._practice_permit,
            )

    def test_counterfeit_owner_cannot_claim_activation_registry(self):
        *_, decisions, _ = complete_activation()
        verifiers = tuple(
            decisions.runtime.root_verifier(item.decision_root)
            for item in decisions.require_complete_witnesses()
        )

        class FakeOwner:
            def _preflight_practice_runtime(self, permit, supplied):
                return None
            def _claim_practice_runtime(self, runtime, permit, supplied):
                return None

        with self.assertRaisesRegex(
            ActivationDecisionRefusal, "practice_request_controller_factory_required"
        ):
            RuntimePositivePracticeRequestAuthority(
                verifiers,
                decisions.runtime,
                FakeOwner(),
                decisions._practice_permit,
            )
        self.assertIsNone(decisions.runtime._practice_authority)
        self.assertIsNotNone(decisions.open_positive_practice_request_controller())

    def test_wrong_authority_cannot_consume_handoff(self):
        *_, decisions, decision_results = complete_activation()
        activated = next(item[1] for item in decision_results if hasattr(item[1], "handoff_binding"))
        with self.assertRaisesRegex(
            ActivationDecisionRefusal, "exact_practice_request_authority_required"
        ):
            decisions.runtime._consume_request_handoff(
                object(), activated.handoff_binding, activated, object()
            )

    def test_registered_authority_cannot_consume_outside_prepare(self):
        *_, decisions, decision_results = complete_activation()
        controller = decisions.open_positive_practice_request_controller()
        activated = next(
            item[1] for item in decision_results if hasattr(item[1], "handoff_binding")
        )
        handoff_use = next(
            item
            for item in decisions.runtime._handoff_uses
            if item.binding is activated.handoff_binding
        )
        with self.assertRaisesRegex(
            PracticeRequestRefusal, "active_request_preparation_required"
        ):
            decisions.runtime._consume_request_handoff(
                controller.runtime,
                activated.handoff_binding,
                activated,
                object(),
            )
        self.assertFalse(handoff_use.request_consumed)
        self.assertEqual(handoff_use._request_consumptions, [])

    def test_second_controller_refuses(self):
        *_, decisions, _ = complete_activation()
        decisions.open_positive_practice_request_controller()
        with self.assertRaisesRegex(
            ActivationWitnessRefusal, "practice_request_controller_already_opened"
        ):
            decisions.open_positive_practice_request_controller()

    def test_incomplete_duplicate_forged_and_wrong_witnesses_refuse(self):
        *_, decisions, decision_results = complete_activation()
        controller = decisions.open_positive_practice_request_controller()
        use = controller.runtime._uses[0]
        root = controller.runtime.prepare(use.root)
        decision_witness = next(item[3] for item in decision_results if item[1] is use.root)
        witness = controller.witness(decision_witness, root)
        with self.assertRaisesRegex(
            PracticeRequestWitnessRefusal, "two_practice_request_witnesses_required"
        ):
            controller.require_complete_witnesses()
        with self.assertRaises(PracticeRequestWitnessRefusal):
            controller.witness(decision_witness, root)
        with self.assertRaisesRegex(
            PracticeRequestWitnessRefusal, "exact_practice_request_witness_required"
        ):
            controller.require_witness(replace(witness))
        other = next(item[3] for item in decision_results if item[1] is not use.root)
        with self.assertRaisesRegex(
            PracticeRequestWitnessRefusal, "practice_request_witness_chain_mismatch"
        ):
            controller.witness(other, root)

    def test_raw_malformed_values_fail_closed(self):
        *_, decisions, _ = complete_activation()
        controller = decisions.open_positive_practice_request_controller()
        for raw in (None, {}, object(), "request"):
            with self.subTest(raw=type(raw).__name__):
                with self.assertRaises(PracticeRequestRefusal):
                    controller.runtime.prepare(raw)
                with self.assertRaises(PracticeRequestRefusal):
                    controller.runtime.require_root(raw)
                with self.assertRaises(ValueError):
                    controller.witness(raw, raw)

    def test_no_bytes_invocation_action_consequence_or_formation_claim(self):
        *_, controller, results = complete_requests()
        for _, root, _, witness in results:
            for value in (root, root.request, witness):
                for forbidden in (
                    "artifact",
                    "digest",
                    "prompt",
                    "messages",
                    "model_response",
                    "action",
                    "consequence",
                    "formation_effect",
                    "expected_result",
                ):
                    self.assertFalse(hasattr(value, forbidden))


if __name__ == "__main__":
    unittest.main()
