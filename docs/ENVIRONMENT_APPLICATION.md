# Positive environment-application contract

Status: **fixture-local semantic contract; reconstruction stable, code slice
blocked**.

Purpose: define the boundary at which the two exact positive commitments become
externally consequential. The environment consumes each private action handoff
once, applies one public deterministic rule, and issues an external result. The
runtime preserves that result without interpreting what should be learned from
it.

## Named computational need

The action authority holds two private `EnvironmentActionHandoff` objects. A
sealed binding on each action root identifies its handoff without exposing that
registry. The next machine need is to resolve each binding exactly once across
the runtime-to-environment boundary and distinguish the resulting occurrence
from both the earlier commitment and any later consequence interpretation.

```text
baseline commitment release
  -> environment applies release to revisions 7 and 8
  -> rejected: stale_dependency

governed commitment rebuild_then_release
  -> environment rebuilds artifact revision to 8, then applies release
  -> accepted
```

These are authored fixture mechanics. They are not a claim that environments
in general should use revision checks or that an accepted result proves
formation.

## Closed input pair

One environment authority accepts an unordered closed pair containing the exact
current `WithheldActionRoot` and `ActivatedActionRoot` issued by the positive
action authority. It receives issuer-registered snapshot-only root verifiers,
then resolves each root's exact sealed binding through the action authority.

Both roots must descend from the same frozen positive foreground and the same
environment rule. The environment receives
`revision-gated-release-v0` as public configuration of its own authority. It
may read the two revision integers only from the exact seven-role positive-
foreground projection retained as `situation` on the practice request, reached
through the resolved handoff's path
`commitment.invocation.request.situation`. Here `situation` is that same frozen
foreground projection, not a second source. The environment may not reopen the
encounter or developmental storage, or accept reconstructed situation roles
from the caller. It receives no branch label, case family, expected result,
scorer key, intervention interpretation, comparison result, or formation
verdict.

Order is not semantic. The environment classifies the two actions by exact
action value and applies the same rule to both; it does not receive a baseline
or governed role.

## Environment rule

The fixture-local rule is `revision-gated-release-v0`.

Each application starts from the artifact revision in its own exact encounter
situation. Its before/after state is local to that application. The two
branch-local applications do not share mutable artifact state, so either
execution order produces the same pair.

- `release` attempts release without changing `artifact_revision`. When
  `artifact_revision` differs from `authority_revision`, the environment rejects
  the action with observation `stale_dependency`.
- `rebuild_then_release` first sets the environment's artifact revision to the
  supplied authority revision, then attempts release. The environment accepts
  the action.

The environment follows the retained request only to read the exact situation
roles that caused the committed action. It does not inspect intervention
presence or use request shape to discover which branch it is on. No other
action value, coercion, fallback, retry, or partial application belongs to this
closed pair.

## External result

For each consumed handoff, the environment issues one immutable
`EnvironmentActionResult`:

```text
run: current fixture run
rule: revision-gated-release-v0
commitment: exact ActionCommitted object from the private handoff
action_value: exact handoff action value
disposition: rejected | accepted
observation: stale_dependency | released
artifact_revision_before: exact integer from the action's situation
artifact_revision_after: unchanged for release; authority revision after rebuild
authority_revision: exact integer from the action's situation
```

For baseline the exact result is `rejected`, `stale_dependency`, revision 7
before and after, authority revision 8. For governed it is `accepted`,
`released`, revision 7 before, revision 8 after, authority revision 8.
These tokens are the exact projection owned by the fixture's positive
environment rule; they make its earlier “rejects” and “accepts” prose
inspectable rather than importing a hidden scorer expectation.

The result is an environment-issued occurrence capability. Equal field values,
the authored fixture table, a model statement, a runtime prediction, or a
scorer expectation cannot replace it.

The environment stores each full result in one environment-owned private result
registry and issues one sealed result binding. The returned
`WithheldEnvironmentRoot` or `ActivatedEnvironmentRoot` retains the exact action
predecessor and that binding, while the full result remains in a private result
registry. The runtime carries only that opaque binding; it neither holds nor
authors result content. This keeps environment authority distinct from runtime
authorship. A later consequence-intake boundary may ask the environment
authority to resolve the exact result through the binding and record
`consequence observed`; this contract does not write that developmental event.

## Atomicity and one-shot use

Each environment action handoff has one application right. Success atomically:

1. resolves and consumes the exact handoff;
2. applies the declared environment rule once;
3. issues one exact external result;
4. registers one sealed result binding; and
5. returns one environment root for the exact action predecessor.

Failure performs none of those operations and does not consume the right.
Resetting flags cannot restore a consumed handoff. One commitment cannot be
applied twice, one application cannot issue two results, and a result binding
cannot resolve for another action root.

Application returns the environment root as current at the environment-
application layer and retires the action root at that layer. The environment
root is a transport head, not a developmental occurrence. This slice appends no
developmental event. Historical validation of an environment root remains
distinct from asking whether its action predecessor is still the live current
head at the action layer.

## Authority and information flow

1. The action authority supplies the closed action pair through registered
   snapshot-only verifiers and privately resolves each sealed handoff. The
   action root supplies predecessor identity; the resolved handoff supplies its
   exact commitment and action value, and the environment checks their join.
2. The environment authority alone applies `revision-gated-release-v0` and
   issues the result capability.
3. The environment owns the private result registry and later resolution. The
   runtime carries the opaque result binding forward. It does not hold, author,
   repair, normalize, or reinterpret the result.
4. The harness witnesses the exact predecessor, handoff consumption, declared
   rule, result identity, and complete unordered result pair.

The actor does not apply its proposal. The commitment runtime does not invent a
result. The harness does not return the expected outcome as if it came from the
environment. A later consequence oracle is unnecessary for these two directly
inspectable fixture results and must not overwrite them.

## Trajectory witness

The harness records one witness per environment result. It checks the exact
action witness and predecessor, exact consumed handoff identity, declared rule,
commitment and action-value identity, exact before/after revision transition,
sealed result binding identity, and the complete unordered pair of one rejected
withheld result and one accepted activated result.

The witness proves what this deterministic environment issued and which action
caused it. It does not prove that the runtime has recorded `consequence
observed`, that an experience is closed, that the admitted change caused a
scientific improvement, or that the mechanism transfers.

## Refusal vectors

Each refusal starts from clean action roots and unused application rights:

1. Raw, caller-created, reconstructed, stale, wrong-head, other-run, or
   wrong-authority action, commitment, handoff, binding, verifier, result, root,
   or witness.
2. Missing, duplicate, third, ablation, or order-classified pair input.
3. An action-root and resolved-handoff join whose commitment, action value, run,
   binding, or predecessor does not retain exact identity.
4. A rule other than `revision-gated-release-v0`, a hidden rule, or a rule
   selected from expected outcome or branch assignment.
5. Missing, extra, coerced, or non-integer revision roles; a revision value read
   from a caller reconstruction instead of exact action lineage.
6. Any action other than exact `release` or `rebuild_then_release`, including an
   equal-looking caller value that is not carried by the exact handoff.
7. Returning the authored expected result without consuming the handoff and
   applying the transition.
8. Rebuilding on `release`, failing to rebuild on `rebuild_then_release`, or
   accepting a release while revisions differ.
9. Reusing one result or result binding across actions, applying one commitment
   twice, or restoring use by resetting guards.
10. Mutating or replacing any retained input, result, binding, root, or witness
    after validation.
11. Letting the runtime, actor, harness, scorer, or consequence oracle author or
    repair the directly inspectable environment result.
12. Treating the result or witness as a `consequence observed` receipt, an
    interpretation, a score, a causal effect, or a formation finding.

The action authority owns handoff identity and consumption. The environment
owns rule application, state transition, and result authorship. The runtime
owns later developmental recording. The harness owns assignment joins and
witness completeness. The scorer owns only later conformance or scientific
verdicts.

## Implementation gate

Two independent final cold readers reconstructed the same closed pair,
environment rule, exact result values, environment-owned private registry,
transport-root shape, one-shot boundary, authority flow, refusals, and
loses-conditions. Earlier reads exposed and repaired an unnamed revision
carrier, order-dependent shared state, unowned result tokens, ambiguous registry
authority, and confusion between transport currentness and developmental
append. The semantic gate is closed.

Code remains blocked. In this one frozen foreground, both actions always see
artifact revision 7 and authority revision 8. A lookup keyed only by action
value can therefore imitate every clean result of the declared revision rule.
Tampering and refusal tests can prove identity and fail-closed behavior, but
they cannot distinguish actual revision comparison from that authored lookup.
The missing pressure is a retained encounter where the same action value must
produce a different disposition under different valid revisions. Adding such a
case solely to force code would expand the fixture rather than answer a need the
fixture already presents. This is the same observational boundary that keeps
fixed-graph constrained replay unmaterialized.

## Unselected

This contract does not select a general action protocol, tool adapter,
transport, retry policy, asynchronous result model, environment persistence,
consequence-observed append, experience closure, candidate interpretation,
governance response, scoring, constrained replay, or formation finding.

## Acceptance and loses-conditions

This contract is sufficient only if independent readers reconstruct one
baseline rejection with `stale_dependency` and unchanged revision 7, and one
governed acceptance with revision 8 after rebuild, both issued by the same
environment rule from exact consumed action handoffs. The environment roots
must expose neither private action-handoff nor private result registries.

It loses if expected results can substitute for environment execution; if the
harness or runtime authors the result; if one handoff applies twice; if direct
release silently repairs stale state; if equal-looking values replace exact
lineage; if private registries become reachable from returned roots or detached
verifiers; or if an external result is treated as a consequence receipt,
interpretation, score, or evidence that formation helped.
