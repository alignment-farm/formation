# Practice-request construction contract

Status: **fixture-local semantic contract implemented; independent post-build
review passes**.

Purpose: define the next practice-boundary append for the baseline-withheld and
governed-activated positive decisions. Both branches prepare one request from
the exact situation already retained by their decision root. Governed must
consume its exact activation handoff once. Baseline must reach the same boundary
without any intervention.

This is request construction, not model invocation. It selects no prompt bytes,
provider format, response, action, consequence, or formation finding.

## Named computational need

The activation boundary deliberately left one governed handoff in a private
registry with an unused request-consumption right. Prose cannot consume that
right or prove that the object entering practice is the exact handoff selected
from governed lineage. The baseline also needs a positive absence claim: its
request must contain no intervention fields, not merely a null-looking copy.

The fixture therefore needs this exchange:

```text
withheld decision root
  -> prepare request from exact retained situation
  -> request with no intervention
  -> exact current withheld-request root

activated decision root + sealed handoff binding
  -> resolve and consume exact private handoff once
  -> request with exact intervention identity and admitted lineage
  -> exact current activated-request root
```

The same candidate text, procedure name, or admission value cannot prove that
the selected encounter-local handoff entered the request. A typed identity
boundary is therefore earned. Request serialization is not.

## Closed input pair

One practice-request authority accepts the exact two current decision roots
issued by the positive activation authority:

- one `WithheldDecisionRoot` for the baseline public condition; and
- one `ActivatedDecisionRoot` for the governed public condition.

Input is one unordered pair. Classification uses only the runtime-visible
decision type, public condition, retained lineage, and presence or absence of
the activation binding. Input order has no meaning. No branch label, assignment,
comparison group, expected result, scorer key, or ablation reason enters the
authority.

The ablation encounter or any replay-constrained state is outside this boundary.
This contract neither constructs its request nor predicts its later decision.

## Shared request semantics

Each accepted decision produces one immutable `PracticeRequest` containing:

```text
run: current fixture run
actor: blind-commit-v0
situation: exact seven-role situation retained by the decision
decision: exact current activation or withholding result
intervention: absent on withholding; exact consumed ActivationHandoff on activation
```

The situation is not rebuilt from the fixture, foreground source, freeze, or
trajectory record. It is the exact object retained by the considered decision
and encounter root. The actor name is public fixture configuration. It does not
choose a branch result.

The request is a semantic object suitable for a later model-invocation boundary.
It is not a prompt, message list, digest, provider request, model response, or
claim that any content affected behavior.

## Withheld request

The baseline predecessor must be the exact current `WithheldDecisionRoot`. Its
considered object carries `declared-role-match-v0`, the exact baseline public
condition, an empty eligible tuple, and the exact situation. Its result is
`no_admitted_change`.

The practice authority prepares one request whose `intervention` is structurally
absent. The request and returned `WithheldRequestRoot` contain no handoff
binding, admitted version, proposal, intervention procedure, intervention
content, selection reason, candidate copy, or placeholder token.

Absence is caused by the runtime-visible withholding result. The authority does
not infer that this is baseline from trajectory assignment.

## Activated request

The governed predecessor must be the exact current `ActivatedDecisionRoot`. The
practice authority presents that root and its exact sealed
`ActivationHandoffBinding` to the activation authority's narrow consumption
operation.

That operation must:

1. revalidate the complete activated decision root;
2. resolve the binding to the exact issuer-owned private handoff;
3. revalidate the handoff's encounter, considered decision, selected admission,
   proposal, procedure, content, and selection reason;
4. verify that the handoff has not entered another request;
5. mark its request-consumption right used; and
6. return the exact handoff object to the practice boundary once.

The resulting request retains that exact handoff as its intervention identity.
Its admitted version, proposal, procedure, content, and reason are reachable
only through the handoff. They are not copied into parallel request fields.
This makes a mismatch impossible to hide behind equal text.

The returned `ActivatedRequestRoot` retains the predecessor, exact request, and
exact consumed handoff. Once request construction succeeds, the decision root
is retired at this layer.

## Atomicity and one-shot rights

Request preparation is one atomic operation per decision root. Success returns
one exact current request root and consumes that decision's request-preparation
right. Governed success also consumes the separate activation-handoff right.

Failure returns no request or root and consumes neither right. In particular,
the practice authority validates every input it can before asking the activation
registry to consume the handoff. After handoff consumption begins, request and
root construction must not contain another fallible caller-controlled step.

Witnessing does not consume or restore either right. Resetting a visible or
private boolean cannot restore a spent decision or handoff. One decision cannot
prepare two requests, and one handoff cannot enter two requests.

## Authority and information flow

1. The activation authority owns decision currentness and the private handoff
   registry.
2. One runtime practice-request authority owns request authorship and returned
   request-root currentness for the exact pair.
3. The practice-request authority owns the handoff-consumption transition as
   part of request construction. It invokes a narrow activation-registry
   operation; the activation authority resolves the full handoff and enforces
   that registry-held right without becoming a second transition owner.
4. The practice authority receives the exact handoff only at consumption. It
   does not receive the registry or reopen admission lineage.
5. The harness may schedule and witness completed request roots. It may not
   construct, enrich, normalize, repair, or choose either request.

The activation decision-root verifiers used at pair intake are snapshot-only.
They expose no activation registry, full handoff, trajectory controller,
assignment, freeze, comparison group, or expected result. The practice request
and returned roots expose no harness provenance.

## Trajectory witness

The harness records one witness per completed request. It checks:

1. the request root's predecessor is the exact decision root retained by the
   activation-decision witness;
2. the request was runtime-authored once from that exact current root;
3. the request situation is the exact seven-role object retained by the
   considered decision and encounter;
4. the withheld request has structural intervention absence;
5. the activated request contains the exact consumed handoff associated with
   its predecessor binding;
6. the closed witness set contains exactly one withheld and one activated
   request for the authorized roots; and
7. no extra public or harness-only field appears.

The witness proves request construction and identity only. It does not prove a
model was invoked, an action was chosen, a consequence occurred, or formation
improved behavior.

## Refusal vectors and ownership

Each refusal begins from clean activation decisions and unused request rights:

1. Supply a raw mapping, alias, caller-created request, root, verifier, handoff,
   binding, or witness.
2. Use an equal reconstructed, stale, other-run, wrong-head, wrong-authority, or
   already-consumed decision root.
3. Omit either required root, add a third, duplicate a root, reverse semantic
   meaning by order, or submit an ablation object.
4. Let a branch label, case family, expected result, scorer key, comparison
   group, or ablation reason select request content.
5. Reopen the foreground source, freeze, assignment, admitted-root controller,
   fixture text, or mutable storage instead of reading the decision root.
6. Omit, add, replace, coerce, or change a situation role between decision and
   request.
7. Put any handoff, binding, admission, proposal, procedure, candidate content,
   selection reason, or placeholder into the withheld request.
8. Build the governed request from its binding token, procedure name, copied
   candidate text, equal admission, equal proposal, or reconstructed handoff.
9. Resolve a binding against the wrong decision root or return a different
   handoff from the private registry.
10. Mutate or replace the decision, binding, handoff, request, or returned root
    before or after validation.
11. Prepare two requests from one decision, consume one handoff twice, reuse a
    handoff across encounters, or restore either right by resetting a flag.
12. Consume the handoff and then fail request construction because of an input
    that could have been checked before consumption.
13. Let the harness author, enrich, normalize, repair, replace, or precompute a
    request or intervention.
14. Witness a partial or duplicate pair, ignore extra fields, compare only
    copied values, or treat witness order as branch meaning.
15. Treat a request or witness as proof of model invocation, action,
    consequence, transfer, or formation.

The activation authority owns decision and binding identity, private handoff
resolution, and enforcement of the registry-held use right. The
practice-request authority owns the request-construction transition, including
handoff consumption, pair intake, situation binding, request authorship,
request linearity, and returned-root currentness. The harness owns assignment
joins and witness completeness only. A later model-invocation boundary owns
cold-model contact and response identity.

## Implementation gate

Two independent cold readers reconstructed one compatible two-request object
with the same authorities, causal order, one-shot rights, structural absence,
exact handoff consumption, witness scope, and refusal ownership. Code-facing
review then confirmed that the existing activation registry could expose one
narrow consumption operation without making its private registry reachable.

The implemented fixture-local slice prepares one baseline request with no
intervention-shaped field and one governed request containing the exact consumed
handoff. The combined suite passes 136 deterministic tests. Post-build review
rejected green states with a counterfeit verifier, restorable boolean guards, a
counterfeit factory owner, and handoff consumption outside request preparation.
The repaired boundary pins verifier identity, keeps append-only spend evidence,
binds the factory permit to the exact controller, revalidates through the
activation authority, and requires a live preparation context for registry
consumption. Two independent final rechecks return `PASS`.

## Unselected

This contract does not select:

- prompt text, messages, serialization, canonicalization, digest, or provider
  request format;
- a universal practice request or intervention schema;
- constrained replay or an ablation request;
- model invocation, response capture, action selection, commitment,
  consequence, or experience closure;
- tools, agent framework, session continuity, or model configuration; or
- any behavioral, transfer, causal, learning, or formation finding.

## Acceptance and loses-conditions

This contract is sufficient only if independent readers reconstruct one exact
withheld request with structural intervention absence, one exact activated
request containing the consumed encounter-local handoff, one current root for
each, no ablation request, and the same refusal outcomes.

It loses if equal text or names can replace the handoff; if the governed handoff
can enter two requests; if withholding is represented by an intervention-shaped
placeholder; if the harness supplies request content; if request construction
reopens mutable lineage; if failure spends only one of two rights; if a decision
remains reusable after success; or if a request is treated as evidence that a
model acted or formation occurred.
