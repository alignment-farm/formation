# Positive action-commitment contract

Status: **fixture-local semantic contract; typed implementation complete**.

Purpose: define the next practice-boundary append for the exact baseline and
governed positive invocation roots. The runtime commits one external action from
each actor-issued proposal. Commitment preserves the proposal as a causal input
without treating the proposal itself as an action or predicting a consequence.

## Named computational need

The deterministic actor has proposed `release` for baseline and
`rebuild_then_release` for governed. The environment cannot receive an
`ActorProposal` object. It needs a runtime-issued action capability that states
what the runtime actually chose to send and which exact invocation warranted
that choice.

```text
withheld invocation root + actor proposal release
  -> runtime commits release
  -> exact baseline action root

activated invocation root + actor proposal rebuild_then_release
  -> runtime commits rebuild_then_release
  -> exact governed action root
```

This fixture uses the identity commitment policy `commit-model-proposal-v0`:
commit the exact public action value proposed by the cold actor. The policy is
runtime-public configuration, not a universal rule that runtimes must obey
models.

## Closed input pair

One action authority accepts an unordered closed pair containing the exact
current `WithheldInvocationRoot` and `ActivatedInvocationRoot` issued by the
positive invocation authority. It classifies them only from runtime-visible
root and request lineage. Order, branch assignment, expected result, case
family, scorer key, comparison group, and ablation reason have no meaning.

Both roots must retain the same exact actor capability and an actor-issued
proposal for their exact request. The action authority receives the public
commitment policy `commit-model-proposal-v0` as its own configuration and records
it on each commitment. The ablation path remains excluded until constrained
replay produces its own decision, request, and invocation.

## Action commitment

For each root, the runtime constructs one immutable `ActionCommitted` object:

```text
run: current fixture run
policy: commit-model-proposal-v0
invocation: exact ModelInvocation from the predecessor
proposal: exact ActorProposal retained by that invocation
action_value: exact proposal.value
```

The proposal remains a cold-actor output. `ActionCommitted` is a new
runtime-authored capability. Equal action text, a request role, fixture prose,
or a caller-created action cannot replace it.

The baseline action value is `release`. The governed action value is
`rebuild_then_release`. These values follow from the actor proposals, not from
hidden expected outcomes. The runtime does not reopen the situation or
intervention to recompute either value during commitment.

`ActionCommitted` is the fixture-local developmental `action committed` event.
The returned `WithheldActionRoot` or `ActivatedActionRoot` retains the exact
invocation predecessor and exact committed-action object. It is the new current
developmental head. It contains no environment result or consequence verdict.

## External handoff

Commitment originates one private `EnvironmentActionHandoff` per action. It
contains the exact `ActionCommitted` object and its exact action value. The
runtime registers that handoff and returns one sealed `EnvironmentActionBinding`
that identifies it without exposing the registry or trajectory state. A later
environment boundary must resolve and consume the exact handoff once when
applying the action. This contract does not apply the action or manufacture the
environment response.

The full environment handoff remains in a private runtime registry until that
boundary. The returned action root retains its public `ActionCommitted` event
and carries only the sealed binding for the separate private handoff. A
snapshot-only action-root verifier cannot reach the registry.

## Atomicity and one-shot use

Each invocation root has one commitment right. Success atomically records one
commitment, originates one environment binding, returns one current action root,
and retires the invocation root at this layer. Failure returns none of those and
does not consume the right.

Resetting flags cannot restore a spent right. One invocation cannot produce two
commitments. One commitment cannot originate two environment bindings. Witnessing
consumes neither the future environment-use right nor any new action.

## Authority and information flow

1. The invocation authority supplies the exact closed pair through
   issuer-registered snapshot-only verifiers.
2. One runtime action authority claims that pair and the public commitment
   policy.
3. The runtime revalidates the actor-issued proposal and commits its exact value.
4. The runtime records the new action capability on the developmental root,
   registers the private environment handoff, and returns only a sealed binding
   for that handoff.
5. The harness witnesses the exact chain. It does not select, author, alter, or
   apply the action.

The cold actor does not commit. The harness does not commit. The environment
does not retroactively choose what was committed. The formation runtime is the
sole commitment authority under the declared policy.

## Trajectory witness

The harness records one witness per commitment. It checks the exact invocation
witness and predecessor, actor-issued proposal identity, declared policy,
proposal-to-action equality, sealed environment binding identity, and the
complete unordered set of one withheld and one activated action root.

The witness proves what the runtime committed and its causal inputs. It does not
prove the environment received or accepted the action, that a consequence
occurred, or that formation helped.

## Refusal vectors

Each refusal starts from clean invocation roots and unused commitment rights:

1. Raw, caller-created, reconstructed, stale, wrong-head, other-run, or
   wrong-authority invocation, proposal, commitment, binding, root, verifier, or
   witness.
2. Missing, duplicate, third, ablation, or order-classified pair input.
3. Different actor capabilities, non-actor-issued proposals, mismatched proposal
   requests, or changed invocation lineage.
4. A policy other than `commit-model-proposal-v0`, a hidden policy, or a policy
   selected from trajectory expectation.
5. An action value copied from the situation, fixture, candidate, expected
   result, or scorer instead of the exact proposal.
6. An action value unequal to `proposal.value`, including coercion,
   normalization, aliasing, or fallback.
7. Recomputing the proposal from request or intervention during commitment.
8. Reusing one proposal or committed-action identity across invocation roots.
9. Producing commitment without an invocation, two commitments from one root,
   or two bindings from one commitment.
10. Mutating or replacing any retained proposal, invocation, commitment,
    binding, root, or witness after validation.
11. Resetting a flag, registering a second authority, or reusing a retired
    predecessor.
12. Letting the harness author, choose, repair, normalize, apply, or precompute
    an action.
13. Treating a commitment or witness as an environment receipt, consequence,
    score, causal benefit, transfer result, or formation finding.

The invocation authority owns predecessor identity and pair issuance. The
runtime action authority owns policy application, commitment authorship,
linearity, private environment handoffs, and returned roots. The harness owns
witness joins and completeness. A later environment boundary owns action
application and external result issuance. A still-later runtime intake boundary
owns the developmental `consequence observed` append.

## Implementation gate

Two independent cold readers reconstructed one compatible action pair, exact
proposal-to-action lineage, the runtime's distinct commitment authority, sealed
environment bindings, one-shot rights, witness scope, refusals, and
loses-conditions. Their first review found and repaired a nonexistent
predecessor policy field and an ambiguous public-root/private-handoff shape.

Code-facing review then confirmed that the existing invocation roots can issue
detached verifiers and that the established owner-bound factory, issuer token,
private registry, and sealed-binding patterns can enforce this slice. The
license covers only the two positive action commitments and their witnesses. It
does not license environment application, external result issuance, or
consequence intake.

The typed implementation now passes the combined 162-test suite. Its first
independent post-build review found no blocker, then identified a harder reset
attack: clearing several per-use aliases together could mint a second
commitment while leaving the first environment binding resolvable. The repaired
runtime also anchors spentness in its issued-root registry and makes binding
resolution depend on the one live commitment lineage. It names policy,
invocation, proposal, action-value, and binding checks directly in the witness.
A final cold recheck attacked those repairs and returned `PASS` with no
blockers.

## Unselected

This contract does not select an action wire format, environment adapter,
tool protocol, transport, retry policy, action application, consequence,
experience closure, scoring, constrained replay, or any behavioral or formation
finding.

## Acceptance and loses-conditions

This contract is sufficient only if independent readers reconstruct the exact
baseline `release` commitment and governed `rebuild_then_release` commitment,
each from its actor-issued proposal, with one current root and sealed environment
binding each, no ablation action, and the same refusals.

It loses if proposal and commitment collapse into one object; if equal text can
replace exact proposal lineage; if the harness selects an action; if one
invocation commits twice; if an action root exposes the private environment
registry; or if commitment is treated as proof of application, consequence, or
formation.
