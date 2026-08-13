# Fixture-local replay-constraint append

Status: **fixture-local typed materialization contract implemented and
post-build reviewed; constrained replay remains unselected**.

Purpose: define the smallest boundary that can turn the exact admitted ablation
root into an exact post-constraint root containing the fixture's public
`replay constraint bound` event. This contract does not implement or certify a
constrained replay view.

## Named computational need

The shared-foreground contract requires one exact ablation recipient after the
public replay constraint exists. The admitted-root boundary returns two
label-blind treatment roots with matching public semantics, so value equality
cannot identify which one the harness later assigned to ablation. Prose also
cannot enforce that one public constraint was delivered to that exact root,
recorded once by its runtime, witnessed unchanged, and returned as a new root.

The required computation is:

```text
exact two-root admitted set plus hidden trajectory assignments
  -> exact harness-only ablation selection
  -> one root-bound public constraint delivery
  -> one runtime-authored constraint event
  -> one witnessed immutable replay-constraint root | refuse
```

This need earns fixture-local typed capabilities, exact object checks, and
one-shot transitions. It does not earn receipt bytes, a digest, a general event
schema, or replay traversal code.

## Boundary with constrained replay

This contract proves only that the exact public constraint is bound at the
correct causal location. Its returned root is a valid input to the separately
specified replay semantics in [FIXTURE.md](FIXTURE.md) and
[INSTRUMENTS.md](INSTRUMENTS.md).

It does not claim that replay was performed and does not carry a cached or
precomputed practitioner view. The fixture still has only one fixed dependency
graph. On that graph, exact validation followed by the authored closure cannot
be distinguished from a general traversal. Replay materialization therefore
remains unlicensed.

## Existing input boundary

The operation accepts only exact immutable `AdmittedBranchRoot` capabilities
returned by the admitted-root append controller. Before assignment of the later
ablation, both treatment roots exist, are independently witnessed, and retain
their complete current source-to-admission chains.

The admitted-root controller issues one private, immutable, one-use
`AdmittedTreatmentBatch` containing exactly those two roots in their original
label-blind formation order. The batch contains no branch label, trajectory
assignment, ablation target, hidden reason, expected effect, scorer field, or
documentary `D-G-*` / `D-A-*` alias.

The constraint-append controller accepts only that exact batch. A raw sequence,
caller-selected pair, reversed pair, duplicate, missing root, governed-only or
ablation-only root, stale batch, other-run batch, or equal reconstruction
refuses.

## Harness-only ablation assignment

After both admitted roots exist, the trajectory harness records one exact
`ablation assigned` capability. It binds:

```text
recipient: exact one of the two admitted roots
public target role: retained acquisition consequence
public policy: transitive_exclusion
hidden reason: causal_probe
expected-effect reference: harness-only fixture expectation
```

The recipient selection comes from the already retained trajectory assignment
chain for the condition root beneath that admitted root. The controller must
resolve that chain directly. It may not infer ablation from treatment-root
order, opaque event coordinates, proposal or admission values, or a caller's
label-to-root mapping.

Exactly one admitted root resolves to the hidden `ablation` assignment and the
other resolves to `governed`. Missing, duplicate, changed, cross-run, or
ambiguous assignment lineage refuses before public delivery.

The `ablation assigned` capability remains trajectory-only. The runtime never
receives that object, its assignment coordinate, the branch label,
`causal_probe`, or the expected-effect reference.

## Exact public target

`D-C-005` is the materialized coordinate of the consequence in the frozen
six-receipt prefix. The public delivery nevertheless names only the closed
semantic role `retained acquisition consequence`; it does not carry that
coordinate, a receipt object, or receipt bytes. For this fixture that role has
exactly one valid resolution in the selected admitted root: the exact
consequence capability already preserved in its formation source.

The harness may name that public role in its trajectory assignment, but it may
not construct, parse, replace, or resolve the runtime target. The runtime
adapter resolves the role from its own retained admitted lineage and retains
the resulting exact capability as the event target.

A raw string `D-C-005`, a coordinate lookup result, equal receipt bytes, a
parsed mapping, another root's consequence, or an equal reconstructed
capability is not the target. This preserves public inspectability without
turning a documentary alias into runtime identity.

## Public delivery

From the frozen fixture policy, the harness derives one immutable
`PublicReplayConstraintDelivery` containing only:

```text
run: current fixture run
recipient: exact admitted ablation root
target role: retained acquisition consequence
policy: transitive_exclusion
```

The delivery has a private issuer and is bound to the exact trajectory
assignment, but exposes none of its hidden fields. It is delivered once to the
runtime responsible for that root. Raw values, caller-created deliveries,
equal copies, wrong-root or wrong-run deliveries, unknown targets or policies,
and reused deliveries refuse.

The public policy is the exact authored token `transitive_exclusion`. This
contract does not generalize an exclusion-policy language or permit additional
configuration fields.

## Runtime source and coordinate

Only a runtime-owned constraint run consumes the exact admitted treatment
batch. It creates one unopened slot for each exact admitted root in the batch's
label-blind order and reserves one distinct opaque constraint coordinate per
slot before the harness assigns the later ablation.

The harness receives no coordinate issuance or reservation method. A runtime
materializer is opened only for the root named by the public delivery; the
unused governed slot emits no placeholder constraint.

The coordinate identifies one event within the current run but has no selected
wire encoding. It exposes no branch label, condition name, hidden assignment,
target alias, policy result, expected effect, or documentary `D-A-010` alias.
The runtime retains the exact root and reservation and refuses later mutation
or substitution.

The runtime adapter consumes the public delivery once and captures one
immutable `FixtureReplayConstraintSource`:

```text
run: current fixture run
consumed_root: exact admitted ablation root
source_head: exact admission coordinate of that root
target: exact retained D-C-005 consequence capability
policy: transitive_exclusion
```

It revalidates the complete current admitted-root chain before accepting the
source. It does not receive or derive a constrained view at this boundary.

## Runtime-authored constraint

Only the runtime materializer may construct the immutable
`ReplayConstraintBound` capability:

```text
run: current fixture run
consumed_root: exact admitted ablation root
coordinate: reserved opaque constraint coordinate
order: 10
event: replay constraint bound
authority: formation_runtime
parents:
  - exact retained D-C-005 consequence capability
  - exact admission coordinate from the consumed root
target: exact retained D-C-005 consequence capability
policy: transitive_exclusion
```

The parent set is exactly those two capabilities. Order in a set has no
semantic meaning. The target and the consequence parent are the same exact
object. The admission parent is the consumed root's exact current head. No
condition head, proposal coordinate, assignment coordinate, hidden reason,
expected effect, branch label, or documentary alias is added.

The runtime returns one immutable `ReplayConstraintHandoff` containing the
exact source and event. It retains private issuer identity, the exact handoff,
and detached snapshots of the complete input and output chain. A caller cannot
author, normalize, repair, replace, or reconstruct the event or handoff.

## Harness witness and returned root

The constraint-append controller validates the exact current runtime handoff
against the retained assignment and public delivery. It records one immutable
trajectory witness without copying hidden fields into runtime lineage.

After that exact handoff is witnessed, the controller returns one immutable
`ReplayConstraintBranchRoot`:

```text
run: current fixture run
admitted_root: exact consumed AdmittedBranchRoot
constraint: exact ReplayConstraintBound
head: exact opaque constraint coordinate
```

The returned root has a private issuer and is returned once. Every later
consumer asks the originating runtime to revalidate the complete current chain
from retained prefix through condition, proposal, admission, public constraint
source, and bound constraint. The harness additionally rechecks the exact
assignment, delivery, handoff, witness, and returned-root identities.

This is the ablation prerequisite required by
[FOREGROUND_DELIVERY.md](FOREGROUND_DELIVERY.md). Foreground delivery consumes
this exact root, not the admitted ancestor, constraint object alone, opaque
coordinate, documentary alias, raw mapping, or equal reconstruction.

## Baseline and governed silence

Baseline is not in the admitted treatment batch and cannot receive this
constraint. Governed is in the batch but is not the hidden ablation recipient.
It emits no placeholder constraint, empty constraint root, rejection event, or
synthetic assignment.

Presenting either root as the ablation recipient refuses before runtime
materialization. The runtime itself does not learn that the other treatment
root is governed or that its own selected root is called ablation.

## Validation, provenance, identity, and exchange

These checks remain separate:

| Check | Owner | Question |
| --- | --- | --- |
| Assignment validity | Trajectory constraint controller | Is this the exact admitted root selected by the retained hidden ablation assignment? |
| Semantic validation | Protocol fixture validator | Does the event have the exact permitted meaning, parents, order, authority, target, and policy? |
| Target provenance | Runtime source adapter | Does the public role resolve to the exact retained consequence in this admitted lineage? |
| Event provenance | Runtime materializer | Did this runtime author the event from this exact root and delivery? |
| Witness and root identity | Trajectory controller | Is the unchanged current handoff witnessed once and returned as this exact root? |
| Replay derivation | Unselected | No constrained-view computation is implemented or certified here. |
| Exchange | Unselected | No byte format, digest, or cross-implementation exchange is claimed. |

Direct capability identity is authoritative for the admitted root, retained
target, handoff, witness, and returned root. Semantic validation is
authoritative for the closed fixture meaning. Neither substitutes for the
other.

## Refusal vectors and ownership

Each refusal starts independently from a clean admitted treatment batch,
assignment, delivery, runtime source, handoff, witness, or returned root:

1. Supply a raw sequence, caller-selected pair, reversed pair, duplicate,
   missing root, stale batch, other-run batch, or equal reconstruction instead
   of the exact admitted treatment batch.
2. Select the recipient by treatment issue order, opaque coordinate, public
   proposal or admission values, caller mapping, or supplied label instead of
   the retained trajectory assignment chain.
3. Resolve zero, two, changed, cross-run, or ambiguous ablation assignments.
4. Deliver to baseline, governed, the admitted ancestor of another root, or an
   equal reconstructed root.
5. Include the branch label, assignment coordinate, `causal_probe`, expected
   effect, case family, expected action, scorer field, or verdict in any
   runtime-visible source, event, handoff, coordinate, or root.
6. Supply `D-C-005` as a raw string, parsed mapping, coordinate lookup result,
   copied bytes, other-root receipt, or equal reconstruction instead of the
   exact retained consequence capability.
7. Change the target or policy, add another field, use an unknown policy, or
   bind a target not retained by the selected admitted lineage.
8. Supply a raw mapping or caller-created, copied, stale, other-run, wrong-root,
   mutated, or reused public delivery.
9. Open a runtime slot before reservation, let hidden assignment affect slot or
   coordinate order, expose coordinate issuance to the harness, or mutate the
   reserved coordinate or root.
10. Change, omit, or add to the event parent set; use a condition or proposal
    head; cite a future, nonexistent, documentary, or other-branch parent.
11. Change order `10`, event meaning, runtime authority, target, or policy; or
    let target and consequence parent differ.
12. Let the harness author, insert, parse into a replacement, normalize, repair,
    or reconstruct the runtime event, source, handoff, witness, or root.
13. Emit no constraint or two constraints for the selected root; emit a
    placeholder constraint for baseline or governed; or reuse a source,
    delivery, handoff, witness, or returned root.
14. Change the admitted root or any retained source, interpreter, proposal,
    governor, admission, delivery, constraint, coordinate, handoff, or witness
    after capture.
15. Return the admitted ancestor, constraint object, raw mapping, opaque
    coordinate, alias, stale root, other-run root, wrong-root result, or equal
    reconstruction as the replay-constraint root.
16. Allow foreground freeze, assignment, delivery, or encounter opening to use
    the admitted ancestor or occur before this exact returned root exists.
17. Attach a constrained practitioner view, dependency closure, eligibility
    result, or expected later refusal to the event or returned root.
18. Claim that successful append validates replay traversal, constrained state,
    causal effect, transfer, or formation.

The trajectory constraint controller owns admitted-batch, hidden-assignment,
recipient-selection, delivery, witness, and returned-root refusals. The runtime
source adapter owns exact retained target, admitted-chain, and delivery-use
refusals. The runtime materializer owns coordinate reservation, runtime
authorship, exact event construction, and handoff refusals. The fixture
validator owns public semantics, parent-set, order, and hidden-field refusals.
The future replay boundary owns dependency traversal and constrained-view
refusals; this append cannot convert those into its own claims.

## Implementation gate

Code may begin only after independent cold readers reconstruct:

- the exact admitted two-root input set and retained hidden assignment chain;
- harness-only selection of one exact ablation root without runtime label flow;
- the public target role and its runtime resolution to the exact retained consequence capability;
- one root-bound public delivery containing only target and policy;
- label-blind runtime coordinate reservation and one runtime-authored event;
- the exact two-parent causal set and distinct returned root;
- baseline and governed silence;
- one-shot and unchanged-object refusals through later root consumption; and
- the strict non-license for constrained replay.

The licensed implementation is fixture-local and in-memory. It must
extend the existing admitted-root capabilities and validators rather than
reopen storage or introduce a second lineage representation.

That implementation now passes the combined 64-test suite. The first green
57-test version was not accepted as closure: independent mechanical review
found broad verifier backpointers into harness assignments, unregistered
runtime coordinates and facades, self-authenticating deliveries, mutable
one-use state, and a delivery registry without a detached currentness snapshot.
The repaired boundary factory-issues the only constraint controller, removes
harness backpointers from runtime-facing verifier capabilities, registers
materializers against exact runtime reservations, registers one exact public
delivery without retaining hidden assignment state, and revalidates assignment,
delivery, source, handoff, witness, and returned-root currentness on later use.

## Unselected

This contract does not select:

- replay-constraint receipt bytes, JSON, JSON Lines, or canonical field order;
- a digest, content binding, string coordinate, or documentary alias encoding;
- a general event, constraint, dependency-edge, replay, or trajectory schema;
- constrained-view representation, caching, traversal, redaction, or closure;
- generic exclusion policies or ablation mechanisms;
- activation, foreground, encounter, correction, scoring, or evidence syntax;
- cross-implementation exchange, authentication, storage, or distributed
  writers; or
- any formation, transfer, ablation-effect, or causal finding.

## Acceptance and loses-conditions

This contract is sufficient only if independent readers reconstruct one exact
harness-selected admitted root, one public target resolved to its retained
consequence, one runtime-authored constraint with the exact causal parents, one
immutable post-constraint root, silence elsewhere, and the same boundary around
unimplemented replay.

It loses if the runtime learns the hidden assignment, if a documentary alias or
equal value can replace exact lineage identity, if the harness can author or
repair the constraint, if the wrong treatment root can receive it, if an
admitted ancestor can masquerade as post-constraint, or if successful append is
presented as evidence that constrained replay was correctly derived.
