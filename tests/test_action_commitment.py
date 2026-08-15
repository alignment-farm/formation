from dataclasses import replace
import unittest
from formation.action_commitment import (
    ActivatedActionRoot, ActionCommitmentRefusal, COMMIT_POLICY,
    RuntimePositiveActionCommitmentAuthority, WithheldActionRoot,
)
from formation.model_invocation import fixture_blind_commit_actor
from trajectory.action_commitment import ActionCommitmentWitnessRefusal
from trajectory.model_invocation import ModelInvocationWitnessRefusal
from test_model_invocation import complete_invocations

def complete_actions():
    *prefix, invocations, invocation_results=complete_invocations()
    controller=invocations.open_positive_action_commitment_controller(); results=[]
    for use in controller.runtime._uses:
        root=controller.runtime.commit(use.root)
        iw=next(x[3] for x in invocation_results if x[1] is use.root)
        witness=controller.witness(iw,root); results.append((use,root,iw,witness))
    return (*prefix,invocations,invocation_results,controller,results)

class ActionCommitmentTests(unittest.TestCase):
    def test_clean_pair(self):
        *_,controller,results=complete_actions()
        self.assertEqual(len(controller.require_complete_witnesses()),2)
        values={type(r):r.commitment.action_value for _,r,_,_ in results}
        self.assertEqual(values[WithheldActionRoot],"release"); self.assertEqual(values[ActivatedActionRoot],"rebuild_then_release")
        for _,r,_,_ in results:
            self.assertEqual(r.commitment.policy,COMMIT_POLICY); self.assertIs(r.commitment.proposal,r.predecessor.proposal); self.assertIs(r.commitment.invocation,r.predecessor.invocation)
    def test_root_has_binding_not_private_handoff(self):
        *_,controller,results=complete_actions()
        for _,r,_,_ in results:
            self.assertFalse(hasattr(r,"environment_handoff")); self.assertFalse(hasattr(r.environment_binding,"handoff")); self.assertFalse(hasattr(r.environment_binding,"registry"))
            self.assertIs(controller.runtime.require_binding(r.environment_binding,r),r.environment_binding)
    def test_one_shot_and_flag_reset(self):
        *_,invocations,_=complete_invocations(); c=invocations.open_positive_action_commitment_controller(); u=c.runtime._uses[0]; r=c.runtime.commit(u.root)
        with self.assertRaises(ActionCommitmentRefusal): c.runtime.commit(u.root)
        self.assertIs(c.runtime.require_root(r),r)
        u.used=False; u.action_root=None
        with self.assertRaises(ActionCommitmentRefusal): c.runtime.commit(u.root)
        u._commitments.clear()
        with self.assertRaises(ActionCommitmentRefusal): c.runtime.commit(u.root)
        with self.assertRaises(ActionCommitmentRefusal): c.runtime.require_binding(r.environment_binding,r)
    def test_detached_verifier_has_snapshot_only(self):
        *_,c,results=complete_actions(); r=results[0][1]; verifier=c.runtime.root_verifier(r)
        self.assertIs(verifier.require(r),r)
        for name in ("authority","runtime","registry","environment_uses","handoff"):
            self.assertFalse(hasattr(verifier,name))
        with self.assertRaises(ActionCommitmentRefusal): verifier.require(replace(r))
    def test_predecessor_currentness_is_explicit(self):
        *_,c,results=complete_actions(); r=results[0][1]
        self.assertIs(c.runtime.require_predecessor_current(r),r)
        predecessor_use=c.runtime._invocations._use_for(r.predecessor.predecessor)
        predecessor_use.used=False
        self.assertIs(c.runtime.require_root(r),r)
        with self.assertRaises(ValueError): c.runtime.require_predecessor_current(r)
    def test_verifier_swap_before_and_after_refuses(self):
        for after in (False,True):
            with self.subTest(after=after):
                *_,invocations,_=complete_invocations(); c=invocations.open_positive_action_commitment_controller(); u=c.runtime._uses[0]; r=c.runtime.commit(u.root) if after else None
                class Fake:
                    def require(self,x): return x
                u.verifier=Fake()
                with self.assertRaises(ActionCommitmentRefusal): c.runtime.require_root(r) if after else c.runtime.commit(u.root)
    def test_reconstruction_and_mutation_refuse(self):
        *_,c,results=complete_actions(); r=results[0][1]
        with self.assertRaises(ActionCommitmentRefusal): c.runtime.require_root(replace(r))
        original=r.commitment.action_value; object.__setattr__(r.commitment,"action_value","other")
        try:
            with self.assertRaises(ActionCommitmentRefusal): c.runtime.require_root(r)
        finally: object.__setattr__(r.commitment,"action_value",original)
    def test_pair_policy_actor_and_owner_refuse(self):
        *_,invocations,_=complete_invocations(); vs=tuple(invocations.runtime.root_verifier(w.invocation_root) for w in invocations.require_complete_witnesses())
        with self.assertRaises(ActionCommitmentRefusal): RuntimePositiveActionCommitmentAuthority((vs[0],vs[0]),COMMIT_POLICY,invocations.runtime,invocations,invocations._action_permit)
        with self.assertRaises(ActionCommitmentRefusal): RuntimePositiveActionCommitmentAuthority(vs,"hidden",invocations.runtime,invocations,invocations._action_permit)
        class FakeOwner:
            def _preflight_action_runtime(self,p,v): pass
            def _claim_action_runtime(self,r,p,v): pass
        with self.assertRaises(ValueError): RuntimePositiveActionCommitmentAuthority(vs,COMMIT_POLICY,invocations.runtime,FakeOwner(),invocations._action_permit)
    def test_second_controller_refuses(self):
        *_,invocations,_=complete_invocations(); invocations.open_positive_action_commitment_controller()
        with self.assertRaises(ModelInvocationWitnessRefusal): invocations.open_positive_action_commitment_controller()
    def test_witness_refusals(self):
        *_,invocations,irs=complete_invocations(); c=invocations.open_positive_action_commitment_controller(); u=c.runtime._uses[0]; r=c.runtime.commit(u.root); iw=next(x[3] for x in irs if x[1] is u.root); w=c.witness(iw,r)
        with self.assertRaises(ActionCommitmentWitnessRefusal): c.require_complete_witnesses()
        with self.assertRaises(ActionCommitmentWitnessRefusal): c.witness(iw,r)
        with self.assertRaises(ActionCommitmentWitnessRefusal): c.require_witness(replace(w))
    def test_raw_values_fail_closed(self):
        *_,invocations,_=complete_invocations(); c=invocations.open_positive_action_commitment_controller()
        for x in (None,{},object(),"release"):
            with self.assertRaises(ActionCommitmentRefusal): c.runtime.commit(x)
            with self.assertRaises(ActionCommitmentRefusal): c.runtime.require_root(x)
    def test_no_environment_or_formation_claim(self):
        *_,c,results=complete_actions()
        for _,r,_,w in results:
            for v in (r,r.commitment,r.environment_binding,w):
                for forbidden in ("environment_result","consequence","accepted","score","formation_effect","expected_result"):
                    self.assertFalse(hasattr(v,forbidden))

if __name__=="__main__": unittest.main()
