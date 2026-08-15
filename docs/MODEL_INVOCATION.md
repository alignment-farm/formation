# Deterministic model-invocation contract

Status: **fixture-local semantic contract implemented; independent post-build
review passes**.

Purpose: define the next practice-boundary append for the exact baseline and
governed positive request roots. One stateless deterministic actor receives each
exact semantic request and returns a model proposal. The runtime records that
invocation without treating the proposal as a committed action or consequence.

This contract makes no language-model call. The fixture actor is a deterministic
port used to test authority, identity, and lifecycle order before model contact.

## Named computational need

The two current request roots now differ only where the mechanism permits:
baseline has no intervention, while governed retains the exact consumed
activation handoff. The next computation must show that one declared actor sees
those exact requests and produces its response from runtime-visible content.

```text
withheld request root
  -> invoke blind-commit-v0 with exact request
  -> model proposal: release
  -> exact withheld-invocation root

activated request root
  -> invoke the same blind-commit-v0 with exact request
  -> compare artifact revision 7 with authority revision 8
  -> model proposal: rebuild_then_release
  -> exact activated-invocation root
```

The returned proposal is not an action. A later runtime boundary must decide
what to commit and bind that commitment to the model output.

## Closed input pair and actor

One invocation authority accepts an unordered closed pair containing the exact
current `WithheldRequestRoot` and `ActivatedRequestRoot` issued by one positive
practice-request authority. Pair order has no meaning. Classification uses the
request types and their runtime-visible content only.

Both invocations use one exact `blind-commit-v0` actor configuration. The actor
is stateless across calls: it retains no prior request, output, branch meaning,
provider conversation, cache, or mutable memory. Delivery order cannot affect
either result.

The actor is a distinct logical authority from the runtime recorder. It authors
the proposal. The runtime owns scheduling, exact request delivery, invocation
recording, and returned-root currentness. The harness owns neither request nor
proposal content.

Each request already names `blind-commit-v0`. Pair intake requires that exact
public name to match the version of the actor capability used for both calls.
A request name alone does not prove execution.

The ablation path remains excluded until constrained replay produces its
decision and request. This contract returns no ablation invocation.

## Deterministic actor semantics

`blind-commit-v0` reads only the exact request it receives.

For a withheld request, it verifies structural intervention absence and returns
the exact public `commit_action` value from the request situation. In the
positive fixture that value is `release`.

For an activated request, it verifies that the request contains the exact
encounter-local handoff selected by its predecessor. It applies the public
procedure `revision-check-intervention-v0`:

1. read `artifact_revision` and `authority_revision` from the exact request
   situation;
2. if they are equal, return the public `commit_action`;
3. if they differ, return the public `refresh_action`.

The positive fixture has revisions 7 and 8, so the activated proposal is
`rebuild_then_release`. The actor does not read documentary aliases, candidate
text as a hidden instruction, branch names, case families, expected actions,
or scorer keys.

The actor returns one immutable `ActorProposal` capability containing the exact
actor capability, exact request, public authority `cold_model`, and proposal
value. Only the actor can issue it. The runtime must retain that exact object;
writing the expected string without an actor-issued proposal is not an
invocation. This follows the acquisition prefix's existing distinction between
runtime recording and `output_authority: cold_model` without selecting a general
model-response schema.

The proposal value remains typed semantic content. No prompt text, message
sequence, tokenization, provider response bytes, or general action language is
selected.

## Model-invoked append

Each successful call produces one immutable `ModelInvocation` containing:

```text
run: current fixture run
actor: exact blind-commit-v0 actor capability
request: exact semantic request object from the predecessor root
proposal: exact actor-issued ActorProposal capability
```

`ModelInvocation` is the fixture-local developmental `model invoked` event, not
a preliminary event before it. The request root is its predecessor, and the
typed invocation root is the new current developmental head.

The invocation has the exact request root and actor capability as causal inputs.
The returned `WithheldInvocationRoot` or `ActivatedInvocationRoot` retains the
predecessor, invocation, and proposal. It does not contain an action,
environment result, consequence, score, or formation verdict.

The activated invocation must retain the exact request whose intervention is
the consumed activation handoff. Reconstructing an equal request, copying the
candidate representation, or passing only the procedure name refuses. The
withheld invocation must retain a request with structural intervention absence.

## Atomicity, currentness, and statelessness

One invocation right exists per request root. Success atomically records one
invocation and returns one exact current invocation root, retiring that request
root at this layer. Failure records nothing and leaves the right unused.

The actor call and invocation append form one fixture-local operation. Because
the deterministic actor has no external side effect, a validation or actor
failure can leave no durable invocation. A later real-model boundary will need
an explicit policy for ambiguous provider outcomes; this contract does not
pretend that problem is solved.

Resetting flags cannot restore a spent request. One request cannot produce two
invocations. The actor capability may serve both authorized requests, but it
cannot carry state from one call into the other. Reversing invocation order
must return the same request-to-proposal mapping.

## Authority and information flow

1. The practice-request authority supplies two exact current request roots
   through issuer-registered snapshot-only verifiers.
2. One runtime invocation authority claims that exact pair and one exact actor
   capability.
3. The runtime delivers each exact semantic request to the actor once.
4. The actor authors a proposal using only request-visible fields.
5. The runtime records the exact request, actor, and proposal and returns a new
   current root.
6. The harness witnesses the completed chain and joins it to request evidence.

The request-root verifiers expose no request authority backpointer, activation
registry, trajectory controller, assignment, freeze, comparison group,
expected result, or scorer state. The actor capability exposes no harness
configuration and no cross-call state.

## Trajectory witness

The harness records one witness per invocation. It checks:

1. the request witness is exact and current;
2. the invocation root predecessor is the exact witnessed request root;
3. the invocation retains the exact request object from that predecessor;
4. both invocations used the same exact actor capability, whose version matches
   each request's `actor`, and each proposal was issued by that capability;
5. withheld retained structural intervention absence;
6. activated retained the exact handoff-bearing request;
7. the closed set contains one withheld and one activated invocation for the
   authorized roots, independent of order; and
8. no action, consequence, score, or hidden field appears.

The harness may compare proposals later, but it may not author, replace,
normalize, repair, or precompute them. The witness proves invocation identity
and fixture-actor output only. It does not prove that the runtime committed the
proposal, that the environment accepted it, or that formation caused a benefit.

## Refusal vectors and ownership

Each refusal starts from clean request roots and unused invocation rights:

1. Supply a raw mapping, alias, caller-created actor, request, invocation, root,
   verifier, proposal, or witness.
2. Use an equal reconstructed, stale, wrong-head, wrong-authority,
   other-run, or already-consumed request root.
3. Omit a required root, add a third, duplicate one, give order semantic
   meaning, or submit an ablation object.
4. Use different actor capabilities or actor versions across the pair.
5. Let actor state, delivery order, provider session state, prompt cache, branch
   label, case family, expected result, scorer key, or ablation reason affect a
   proposal.
6. Rebuild or enrich a request before actor delivery.
7. Add an intervention-shaped field to the withheld request or ignore such a
   field when validating it.
8. Replace the governed handoff with its binding token, name, equal admission,
   copied candidate text, or reconstructed semantic object.
9. Omit, add, replace, coerce, or mutate a situation role before or during the
   actor call.
10. Return an undeclared proposal, construct a proposal in the runtime, mismatch
    its actor or request, or derive the positive answer from trajectory
    expectation rather than the request semantics.
11. Record an invocation without an actor call, call without recording, retain
    a different request or proposal, or append twice from one request.
12. Mutate or replace the actor, request, proposal, invocation, root, or witness
    after validation.
13. Let the harness author, repair, normalize, or replace model input or output.
14. Reset a flag, register a second authority, or reuse a retired request root.
15. Treat a proposal as a committed action, external consequence, score,
    behavioral benefit, transfer result, or formation finding.

The practice-request authority owns predecessor identity, currentness, closed
pair issuance, and request-shape checks. The cold actor owns proposal
authorship. The runtime invocation authority owns delivery, invocation
recording, linearity, and returned roots. The harness owns witness joins and
completeness only. A later action-commitment boundary owns whether and what the
runtime commits.

## Implementation gate

Two independent cold readers reconstructed one compatible pair of invocations,
the same exact actor capability, the request-to-proposal computation, the
distinction between proposal and action, stateless order independence,
authorities, refusals, and loses-conditions. Code-facing review licensed an
actor-issued proposal capability and detached request-root verifiers.

The implemented fixture-local slice uses one frozen stateless actor capability
that alone issues proposal objects. The runtime delivers and records but cannot
forge the proposal issuer. The combined suite passes 150 deterministic tests.
Post-build review found one revalidation path that failed to pin a replaced
verifier after invocation; the repaired runtime uses the same pinned path before
and after spend, and independent recheck returns `PASS`.

## Unselected

This contract does not select:

- an LM, provider, prompt, messages, tokenization, response bytes, or model
  configuration format;
- tools, streaming, retries, timeout semantics, or ambiguous-call recovery;
- a universal model port, request schema, response schema, or action language;
- constrained replay or an ablation invocation;
- action commitment, environment transition, consequence, experience closure,
  scoring, or costs; or
- any behavioral, causal, transfer, learning, or formation finding.

## Acceptance and loses-conditions

This contract is sufficient only if independent readers reconstruct one exact
withheld invocation proposing `release`, one exact activated invocation
proposing `rebuild_then_release`, the same stateless actor capability on both,
one current root per request, no ablation invocation, and the same refusals.

It loses if the runtime writes a proposal without an actor call; if the harness
supplies the proposal; if invocation order changes output; if a reconstructed
request or handoff is accepted; if one request invokes twice; if an invocation
is treated as an action or consequence; or if the deterministic stub is
presented as evidence that a model learned or improved.
