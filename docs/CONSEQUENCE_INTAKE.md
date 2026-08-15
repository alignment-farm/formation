# Positive consequence-intake contract

Status: **fixture-local semantic contract; reconstruction stable, code slice
blocked by predecessor**.

Purpose: define how the runtime records the two exact positive environment
results as developmental `consequence observed` events. Intake preserves an
external occurrence and its action relation. It does not explain the occurrence,
propose a lesson, close an experience, or score a branch.

## Named semantic need

Environment application leaves each branch with a transport root carrying a
sealed binding to an environment-owned private result. Developmental lineage
still ends at `action committed`. An ordinary practitioner must be able to
retain the external result before any interpretation can cite it.

```text
environment result binding
  -> runtime resolves exact result through environment authority
  -> runtime appends consequence observed
  -> exact consequence root
```

This is intake, not environment application. It changes no artifact state and
does not ask the environment to issue a second result.

## Closed input pair

One runtime intake authority accepts the unordered exact current pair of
`WithheldEnvironmentRoot` and `ActivatedEnvironmentRoot`. Each root must come
from the same positive environment authority and retain the exact action
predecessor plus its sealed result binding. The environment authority resolves
that binding to the exact private `EnvironmentActionResult` once for intake.

The runtime receives the result capability, its exact action predecessor, and
public intake policy `record-direct-result-v0`. It receives no branch label,
case family, expected result, scorer verdict, counterfactual outcome, candidate
content, applicability claim, or explanation of why the result occurred.

Result resolution for intake is distinct from action application. Application
has already consumed the action handoff. Intake consumes one separate result-
delivery right; it cannot reapply the action or change the environment result.

## Consequence-observed event

For each exact result, the runtime authors one immutable
`ConsequenceObserved` event:

```text
run: current fixture run
policy: record-direct-result-v0
action: exact ActionCommitted object retained by the result
environment_result: exact EnvironmentActionResult resolved from the binding
status: observed
```

The retained result capability supplies both the observation and an opaque
issuer-identity binding to the environment authority that originated it. That
binding is evidence of source identity, not a live environment capability,
verifier, or registry handle. Baseline therefore exposes observation
`stale_dependency` through its exact rejected result; governed exposes
`released` through its exact accepted result. The runtime copies neither
observation, disposition, nor revision fields into independent parallel
consequence fields. They remain available only through the exact retained
environment-result capability, so no copied field can disagree with its source.

`status: observed` means that a direct result was available and retained. It
does not mean accepted, beneficial, correct, complete for every future purpose,
or uncontested forever. Missing, delayed, partial, contested, and corrected
consequences remain required general semantics, but this slice selects only the
two directly observed positive results.

The returned `WithheldConsequenceRoot` or `ActivatedConsequenceRoot` retains the
exact action root and exact `ConsequenceObserved` event. The semantic
developmental parent is the `ActionCommitted` occurrence on that action root.
The retired action root and environment transport root are intake-join evidence,
not additional developmental events or parents. The consequence event retains
its exact result to make the external join auditable. Each returned consequence
root is the new current developmental head for its branch.

## Causal order and authority

1. The environment has already applied the exact action and privately issued
   the exact result.
2. The environment authority resolves one sealed result binding for the runtime
   under a one-shot intake right.
3. The runtime checks that result, binding, transport root, commitment, action
   root, and run form one exact chain.
4. The environment remains the originating authority for the external
   occurrence. The runtime records and appends `ConsequenceObserved` under
   `record-direct-result-v0` and appends it after the exact `action committed`
   predecessor.
5. The harness witnesses the join and complete pair afterward.

The environment owns result truth and originates the external occurrence. The
runtime owns recording and appending the developmental occurrence event and may
only preserve what the result says. The harness
owns scheduling and evidence joins, not occurrence content. The scorer owns no
runtime input. A consequence oracle does not participate because these results
are directly inspectable.

## Atomicity and one-shot use

Each result binding has one intake right. Success atomically resolves the exact
result, records one event, and returns one current consequence root. Failure
does none and leaves the right unused. Resetting flags cannot restore a consumed
right. One result cannot create two consequence events, one event cannot cite
two results, and one binding cannot serve another action or branch.

The consumed right is specifically the runtime's developmental delivery right.
The environment retains the immutable result for non-intake witness and audit
joins, but successful intake leaves no second path to append it again. A later
correction cites the retained consequence occurrence and does not re-consume
the original result binding.

Historical validation of a consequence root remains distinct from checking
whether its environment transport input and action predecessor are still
current at their respective layers.

## Trajectory witness

The harness records one witness per intake. It checks the exact environment
root and application witness, exact binding resolution, exact result identity,
exact action and action-root relation, declared intake policy, result
observation, current consequence root, and the complete unordered pair of one
withheld and one activated consequence.

The witness proves that the runtime preserved the exact environment-issued
results in developmental lineage. It does not prove the results were good, that
the governed mechanism caused the difference, that an experience was closed,
that a lesson was acquired, or that behavior transfers.

## Refusal vectors

Each refusal starts from clean environment roots and unused intake rights:

1. Raw, caller-created, reconstructed, stale, wrong-head, other-run, or
   wrong-authority environment root, result, binding, action, event, consequence
   root, verifier, or witness.
2. Missing, duplicate, third, ablation, or order-classified pair input.
3. A result-binding join whose environment authority, result, commitment,
   action value, action root, or run loses exact identity.
4. An intake policy other than `record-direct-result-v0`, or a policy selected
   from hidden assignment or expected outcome.
5. Caller-supplied observation, disposition, revisions, result reconstruction,
   model self-evaluation, oracle replacement, or scorer verdict.
6. Recording `stale_dependency` or `released` from fixture prose without
   resolving the exact environment-issued result.
7. Copying disposition or revision fields into parallel consequence fields that
   can disagree with the retained result.
8. Reapplying the action, asking the environment to recompute the result, or
   changing result content during intake.
9. Reusing one result binding, recording one result twice, restoring a right by
   resetting guards, or leaving an orphaned binding resolvable after lineage
   rejection.
10. Mutating or replacing any retained input, event, root, or witness after
    validation.
11. Letting the environment append runtime lineage or letting the runtime,
    harness, oracle, or scorer author the external result.
12. Treating intake as experience closure, interpretation, admission, score,
    causal attribution, transfer evidence, or a formation finding.

The environment authority owns result identity, external-occurrence
origination, and developmental-delivery consumption. The runtime intake
authority owns validation, occurrence recording, append linearity, and current
developmental roots. The harness owns witness joins and completeness.

## Implementation gate

Two independent final cold readers reconstructed the same result resolution,
developmental parentage, recorder/originator split, one-shot delivery right,
audit retention, current roots, witness boundary, refusals, and loses-
conditions. An earlier reconstruction exposed and repaired ambiguous transport
parentage, live source-authority leakage, copied observation fields, unclear
audit rights, and collapsed environment/runtime authorship. The semantic gate
is closed.

Code remains blocked by the predecessor environment-application slice, so no
live environment-issued result capability exists to consume. Semantic
convergence does not override that missing computation. Intake implementation
must wait until an independently warranted environment case distinguishes real
rule execution from action-keyed lookup and licenses its result boundary.

## Unselected

This contract does not select result serialization, consequence receipt bytes,
missing or delayed intake, oracle substitution, correction, experience closure,
candidate interpretation, governance, scoring, constrained replay, or any
formation finding.

## Acceptance and loses-conditions

This contract is sufficient only if independent readers reconstruct two exact
runtime-authored occurrence events: baseline retains its environment-issued
`stale_dependency` result and governed retains its environment-issued `released`
result, each after its exact action predecessor, with no ablation event and no
interpretation or score.

It loses if fixture prose or scorer expectations can substitute for result
resolution; if result and consequence event collapse into one authority; if the
environment writes developmental lineage; if the runtime edits the external
result; if one delivery records twice; if equal-looking values replace exact
identity; or if occurrence retention is treated as experience closure,
learning, causal benefit, or transfer.
