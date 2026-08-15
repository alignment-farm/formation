from dataclasses import replace
import unittest

from formation.model_invocation import (
    ActivatedInvocationRoot,
    ActorProposal,
    BlindCommitActor,
    ModelInvocationRefusal,
    RuntimePositiveModelInvocationAuthority,
    WithheldInvocationRoot,
    fixture_blind_commit_actor,
)
from trajectory.model_invocation import ModelInvocationWitnessRefusal
from trajectory.practice_request import PracticeRequestWitnessRefusal
from test_practice_request import complete_requests


def complete_invocations():
    *prefix, requests, request_results = complete_requests()
    controller = requests.open_positive_model_invocation_controller()
    results = []
    for use in controller.runtime._uses:
        root = controller.runtime.invoke(use.root)
        request_witness = next(item[3] for item in request_results if item[1] is use.root)
        witness = controller.witness(request_witness, root)
        results.append((use, root, request_witness, witness))
    return (*prefix, requests, request_results, controller, results)


class ModelInvocationTests(unittest.TestCase):
    def test_clean_pair_uses_same_actor_and_expected_proposals(self):
        *_, controller, results = complete_invocations()
        witnesses = controller.require_complete_witnesses()
        self.assertEqual(len(witnesses), 2)
        values = {type(root): root.proposal.value for _, root, _, _ in results}
        self.assertEqual(values[WithheldInvocationRoot], "release")
        self.assertEqual(values[ActivatedInvocationRoot], "rebuild_then_release")
        self.assertEqual(len({id(root.invocation.actor) for _, root, _, _ in results}), 1)
        for _, root, _, _ in results:
            self.assertIs(root.invocation.request, root.predecessor.request)
            self.assertIs(root.invocation.proposal, root.proposal)
            self.assertIs(root.proposal.request, root.predecessor.request)

    def test_order_independence(self):
        *_, requests, _ = complete_requests()
        controller = requests.open_positive_model_invocation_controller()
        roots = tuple(controller.runtime.invoke(use.root) for use in reversed(controller.runtime._uses))
        mapping = {type(root): root.proposal.value for root in roots}
        self.assertEqual(mapping[WithheldInvocationRoot], "release")
        self.assertEqual(mapping[ActivatedInvocationRoot], "rebuild_then_release")

    def test_actor_is_stateless_capability(self):
        actor = fixture_blind_commit_actor()
        self.assertFalse(hasattr(actor, "history"))
        self.assertFalse(hasattr(actor, "last_request"))
        self.assertFalse(hasattr(actor, "branch"))

    def test_runtime_cannot_substitute_caller_proposal(self):
        *_, requests, request_results = complete_requests()
        request = request_results[0][1].request
        fake = ActorProposal(fixture_blind_commit_actor(), request, "cold_model", "release", object())
        self.assertIsNot(fake._issuer, fixture_blind_commit_actor().invoke(request)._issuer)

    def test_one_shot_and_flag_reset(self):
        *_, requests, _ = complete_requests()
        controller = requests.open_positive_model_invocation_controller()
        use = controller.runtime._uses[0]
        root = controller.runtime.invoke(use.root)
        with self.assertRaisesRegex(ModelInvocationRefusal, "request_already_invoked"):
            controller.runtime.invoke(use.root)
        self.assertIs(controller.runtime.require_root(root), root)
        use.used = False
        use.invocation_root = None
        with self.assertRaisesRegex(ModelInvocationRefusal, "request_already_invoked"):
            controller.runtime.invoke(use.root)

    def test_live_verifier_replacement_refuses_without_spend(self):
        *_, requests, _ = complete_requests()
        controller = requests.open_positive_model_invocation_controller()
        use = controller.runtime._uses[0]
        class Fake:
            def require(self, root): return root
        use.verifier = Fake()
        with self.assertRaises(ModelInvocationRefusal):
            controller.runtime.invoke(use.root)
        self.assertEqual(use._invocations, [])

    def test_live_verifier_replacement_refuses_after_spend(self):
        *_, requests, request_results = complete_requests()
        controller = requests.open_positive_model_invocation_controller()
        use = controller.runtime._uses[0]
        root = controller.runtime.invoke(use.root)
        request_witness = next(
            item[3] for item in request_results if item[1] is use.root
        )
        witness = controller.witness(request_witness, root)
        class Fake:
            def require(self, candidate): return candidate
        use.verifier = Fake()
        with self.assertRaises(ModelInvocationRefusal):
            controller.runtime.require_root(root)
        with self.assertRaises(ModelInvocationRefusal):
            controller.require_witness(witness)

    def test_reconstructed_and_mutated_roots_refuse(self):
        *_, controller, results = complete_invocations()
        root = results[0][1]
        with self.assertRaisesRegex(ModelInvocationRefusal, "exact_model_invocation_root_required"):
            controller.runtime.require_root(replace(root))
        original = root.proposal.value
        object.__setattr__(root.proposal, "value", "rebuild_then_release")
        try:
            with self.assertRaisesRegex(ModelInvocationRefusal, "model_invocation_root_changed"):
                controller.runtime.require_root(root)
        finally:
            object.__setattr__(root.proposal, "value", original)

    def test_counterfeit_actor_and_pair_refuse(self):
        *_, requests, _ = complete_requests()
        verifiers = tuple(requests.runtime.root_verifier(item.request_root) for item in requests.require_complete_witnesses())
        fake_actor = BlindCommitActor("blind-commit-v0", "cold_model", object())
        with self.assertRaises(ModelInvocationRefusal):
            RuntimePositiveModelInvocationAuthority(verifiers, fake_actor, requests.runtime, requests, requests._invocation_permit)
        with self.assertRaises(ModelInvocationRefusal):
            RuntimePositiveModelInvocationAuthority((verifiers[0], verifiers[0]), fixture_blind_commit_actor(), requests.runtime, requests, requests._invocation_permit)

    def test_counterfeit_owner_with_stolen_permit_refuses(self):
        *_, requests, _ = complete_requests()
        verifiers = tuple(
            requests.runtime.root_verifier(item.request_root)
            for item in requests.require_complete_witnesses()
        )
        class FakeOwner:
            def _preflight_invocation_runtime(self, permit, supplied): return None
            def _claim_invocation_runtime(self, runtime, permit, supplied): return None
        with self.assertRaises(ValueError):
            RuntimePositiveModelInvocationAuthority(
                verifiers,
                fixture_blind_commit_actor(),
                requests.runtime,
                FakeOwner(),
                requests._invocation_permit,
            )
        self.assertIsNone(requests.runtime._invocation_authority)
        self.assertIsNotNone(requests.open_positive_model_invocation_controller())

    def test_second_controller_refuses(self):
        *_, requests, _ = complete_requests()
        requests.open_positive_model_invocation_controller()
        with self.assertRaises(PracticeRequestWitnessRefusal):
            requests.open_positive_model_invocation_controller()

    def test_witness_refusals_and_completeness(self):
        *_, requests, request_results = complete_requests()
        controller = requests.open_positive_model_invocation_controller()
        use = controller.runtime._uses[0]
        root = controller.runtime.invoke(use.root)
        request_witness = next(item[3] for item in request_results if item[1] is use.root)
        witness = controller.witness(request_witness, root)
        with self.assertRaises(ModelInvocationWitnessRefusal):
            controller.require_complete_witnesses()
        with self.assertRaises(ModelInvocationWitnessRefusal):
            controller.witness(request_witness, root)
        with self.assertRaises(ModelInvocationWitnessRefusal):
            controller.require_witness(replace(witness))

    def test_raw_values_fail_closed(self):
        *_, requests, _ = complete_requests()
        controller = requests.open_positive_model_invocation_controller()
        for raw in (None, {}, object(), "release"):
            with self.assertRaises(ModelInvocationRefusal): controller.runtime.invoke(raw)
            with self.assertRaises(ModelInvocationRefusal): controller.runtime.require_root(raw)

    def test_no_action_consequence_or_formation_claim(self):
        *_, controller, results = complete_invocations()
        for _, root, _, witness in results:
            for value in (root, root.invocation, root.proposal, witness):
                for forbidden in ("committed_action", "action", "consequence", "score", "formation_effect", "expected_result"):
                    self.assertFalse(hasattr(value, forbidden))


if __name__ == "__main__":
    unittest.main()
