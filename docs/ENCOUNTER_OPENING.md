# Positive encounter-opening contract

Status: **fixture-local typed boundary implemented; independent post-build
conformance review passes**.

Purpose: define the smallest developmental append after shared positive-
foreground delivery. This contract fixes what it means for each runtime to open
the positive encounter from the exact foreground it received. It does not
select receipt bytes, implement activation, or claim that a model was invoked.

## Named computational need

The foreground boundary ends with three exact `ReceivedForegroundHandoff`
objects. The fixture next needs three new current developmental heads:

```text
exact current branch root + exact received foreground handoff
  -> one runtime-authored encounter opened append
  -> one exact branch-local encounter root
  -> one trajectory witness of the append and received projection
```

Later activation must cite an exact current encounter and branch lineage.
Equal-looking foregrounds cannot show which predecessor was extended, whether
the retained handoff was used, or whether one handoff opened two encounters.
Those are separate refusal cases, so a fixture-local typed append and linear-
use boundary may be earned after cold review.

No byte identity is required. The operation stays within one runtime, and no
cross-implementation exchange, serialization, digest, clock, or general
lineage schema is selected.

## Semantic object

The positive `encounter opened` append retains:

```text
run: current fixture-run capability
predecessor: exact current branch root that received the foreground
opening_binding: sealed capability issued for the exact received handoff
encounter: one fresh opaque branch-local encounter capability
situation: the exact immutable seven-role foreground carried by the handoff
```

Its developmental causal parent is the exact predecessor root. The handoff is
the append input and content source; it is not a second lineage parent and is
not retained as a traversable object in developmental lineage. Before append,
the runtime foreground-consumption authority issues one sealed
`EncounterOpeningBinding` for the exact handoff. The returned encounter root
retains the predecessor, that binding, encounter capability, append, and
complete situation projection. The binding exposes no delivery, freeze,
comparison group, recipient set, or assignment state.

For this fixture, the seven-role situation is the complete observation
boundary at encounter opening. There is no separate observation payload,
default, hidden state, or eighth public role. Later model output and environment
observation belong to later receipts.

The encounter coordinate is opaque and branch-local. Documentary aliases,
branch names, case-family names, issue order, and equal reconstructed objects
cannot identify it.

## Required predecessors

The append accepts the three deliberately different predecessor types already
authorized by foreground delivery:

| Trajectory meaning | Exact predecessor |
| --- | --- |
| Baseline | Current `audit_lineage_only-v0` condition-bound root |
| Governed | Current eligible admitted-version root |
| Ablation | Current replay-constrained root containing `D-A-010` |

Each handoff names the exact root whose delivery was consumed. The runtime
requires object identity between that `consumed_root` and the predecessor it
extends. A condition-only substitute for governed or ablation, the ablation
admitted ancestor before `D-A-010`, a stale root, an equal rebuild, or a root
from another run refuses.

The root types need not share a public interface. A materialization may use one
narrow currentness verifier per root authority, but no verifier may issue or
validate a root owned by another authority.

## Authority and causal order

1. The protocol owner authors the seven-role positive foreground.
2. The foreground controller freezes it for one comparison group and exact
   recipient set.
3. The harness records `foreground bound` and a branch-local positive
   `case assigned` that cites the freeze.
4. The runtime consumes its exact root-bound delivery and produces one
   `ReceivedForegroundHandoff`.
5. The runtime foreground-consumption authority binds that exact handoff once
   to one sealed encounter-opening capability.
6. The runtime encounter opener consumes that exact binding once, revalidates
   its privately retained handoff, and appends `encounter opened` to the exact
   predecessor.
7. The runtime returns the exact new encounter root.
8. The harness witnesses the returned append and compares its complete
   situation projection with the one foreground freeze.

The harness owns hidden scheduling and the evidence that assignment preceded
presentation. It may reject or witness a runtime append. It may not construct
the encounter receipt, choose its coordinate, supply its situation, repair its
parents, or return a replacement root.

The runtime-visible append contains no branch label, comparison-group identity,
case family, expected action, scorer key, coaching field, intervention field,
ablation reason, or expected effect.

## Runtime append boundary

The encounter opener accepts one exact current predecessor, the exact sealed
opening binding issued for its retained handoff, and the narrow currentness
authority for that predecessor type. The opener's issuer-owned registry, not
the binding's public surface, retains the handoff, its foreground consumer, and
the one-use state. Before appending, the opener revalidates:

1. the run and predecessor are current;
2. the binding is the exact registered binding, not a caller-created
   equivalent;
3. the privately registered handoff is the exact handoff retained by its
   foreground consumer;
4. the handoff's `consumed_root` is the predecessor by object identity;
5. its delivery, freeze, comparison group, foreground, and recipient provenance
   remain unchanged;
6. the binding has not already opened an encounter; and
7. the situation is exactly the handoff's immutable seven-role foreground.

On success, the opener atomically marks the binding used for encounter opening,
creates one opaque encounter capability, records the semantic append, and
returns one immutable encounter root. Failure returns no encounter or root and
does not consume the opening right.

The opener may not reopen protocol storage, read a trajectory assignment,
derive the situation again from the freeze, or accept a raw foreground mapping.
The privately retained handoff is the sole situation source at this boundary.

Only the runtime opener constructs the returned root. Making it current turns
the predecessor into an ancestor without erasing its historical identity or
permitting a second positive append from it.

The root retains only the sealed opening binding needed to prove which runtime
handoff was consumed. The binding has no backpointer to the handoff or its
harness-owned provenance. The issuer-owned opener registry retains those
objects outside developmental lineage and exposes only narrow validation
operations. Later runtime operations cannot reach comparison-group,
assignment, freeze, delivery, or recipient-set state through the root or
binding.

Later `activation considered` must consume this exact encounter root and cite
its exact encounter capability. This contract does not materialize that
decision, an activation handoff, a constrained replay view, or a model request.

## Trajectory witness

The harness accepts only the exact encounter root retained by the runtime
opener. Before recording `runtime event witnessed`, it checks:

1. the positive `case assigned` exists and cites the exact freeze;
2. assignment preceded delivery consumption and encounter opening;
3. the predecessor is the exact recipient authorized by that assignment;
4. the sealed binding resolves through the opener's private registry to the
   retained handoff from that recipient's one delivery;
5. the runtime-authored append extended that predecessor exactly once;
6. the returned root retains the exact append, sealed binding, and fresh
   encounter, without a traversable handoff backpointer;
7. the complete seven-role situation directly equals the frozen foreground;
8. no hidden or extra field appears in the public seven-role encounter
   projection.

Each branch-local witness may be recorded as its runtime executes. After all
three executions, the harness separately closes the witness set only if one
exact witnessed encounter root exists for each authorized recipient. Branches
need not execute or be witnessed in lockstep.

The witness stores the join between hidden assignment and public developmental
identity in trajectory evidence only. It does not add assignment, freeze,
comparison group, or branch meaning to developmental lineage.

The witness does not compare eligible state, activation decisions, model
requests, actions, or consequences. It cannot claim that activation was
considered or that the model saw the situation.

## Refusal vectors and ownership

Each refusal begins independently from clean roots, handoffs, assignments, and
foreground provenance:

1. Supply a raw mapping, foreground, coordinate, alias, caller-created handoff,
   append, encounter, root, binding, or witness.
2. Use an equal reconstructed, stale, other-run, other-group, wrong-head, or
   wrong-authority predecessor.
3. Pair a valid binding or its privately retained handoff with a predecessor
   other than the handoff's exact `consumed_root`.
4. Open from the governed condition root before admission or the ablation
   admitted root before `D-A-010`.
5. Open before `foreground bound`, before `case assigned`, or from an assignment
   that does not cite the exact freeze.
6. Reopen protocol storage, the freeze, or another source instead of taking the
   situation from the handoff.
7. Change, omit, add, default, coerce, or replace a foreground role between
   handoff and append.
8. Add hidden branch, comparison, family, expected-result, scorer, coaching,
   intervention, ablation-reason, or expected-effect data to the append.
9. Use one binding or retained handoff to open zero encounters, two encounters,
   or encounters on two roots.
10. Append twice from the same predecessor for this positive presentation.
11. Reuse or accept a caller-selected encounter coordinate.
12. Mutate or replace the predecessor, delivery, handoff, binding, append,
   encounter, or returned root after validation.
13. Let the harness author, normalize, repair, append, or replace runtime
   objects.
14. Witness a partial situation, ignore extras, or compare complete branch
   requests instead of the seven-role projection.
15. Treat the encounter witness as proof of activation, invocation, action,
   consequence, transfer, or formation.

The runtime foreground-consumption boundary owns exact-handoff, opening-binding
issuance, and retained-provenance refusals.
The runtime opener owns predecessor identity, currentness, append authority,
fresh encounter identity, linear opening, projection, and returned-root
refusals. The harness owns assignment order, freeze citation, closed three-
recipient witness coverage, and comparison-scope refusals.

## Implementation gate

Two independent cold readers reconstructed one compatible object covering the
exact predecessor and handoff, runtime authorship, harness-only scheduling,
one-shot append, fresh encounter, complete projection, returned root, witness
scope, refusals, and the boundary before activation. Both returned
`CONTRACT_STABLE_CODE_REVIEW_NEEDED`.

Materialization requires one issuer-owned linear-use authority created by the
runtime foreground-consumption boundary. It must retain the exact handoff and
consumer privately, issue one sealed opening binding with no provenance
backpointer, and allow one registered opener to consume it atomically. A
caller-visible boolean or a binding that makes the handoff, freeze, comparison
group, or assignment reachable is nonconforming.

The first code-facing review rejected retaining the full foreground handoff in
developmental lineage because that object could reach the harness-owned freeze
and comparison group. The repaired contract introduced the sealed binding and
private runtime registry above. Fresh cold reconstruction converged on that
object, and focused review licensed a fixture-local typed slice.

Post-build review rejected two green implementations. The first returned roots
without making them the encounter layer's current heads and kept one-shot state
inside a replaceable opener, so a second opener could reuse the same handoff.
The second exposed the opener and its retained provenance through a supposedly
narrow root verifier and allowed module-level issuer constants to bypass the
registered controller path. The repaired implementation uses consumer-owned
one-shot registration, an encounter-layer current-head verifier with snapshots
only, one ephemeral permit owned by the existing foreground controller, and
recipient-keyed verifier pairing so branch execution order remains free.

The combined suite now passes 96 tests. The final independent mechanical
recheck returns `PASS`. The implementation selects typed in-memory capabilities
only; it does not select encounter bytes or any later practice event.

## Unselected

This contract does not select receipt bytes, digests, storage, a general event
or lineage schema, constrained replay, activation or withholding, intervention
or request formats, invocation, action, consequence, experience closure,
correction, governance revision, scoring, costs, or any formation finding.

## Acceptance and loses-conditions

This contract is sufficient only if independent readers reconstruct one
runtime-authored append from each exact predecessor and handoff-bound opening
capability, one fresh
encounter, one exact returned root, a complete foreground projection, a
harness-only assignment witness, and the same refusal outcomes.

It loses if a conformer can pass by copying the seven values without consuming
the binding for the retained handoff, extending the wrong or stale root,
opening twice, letting the harness create or repair the encounter, or leaking
hidden case information into developmental lineage. Reachability of the full
handoff, delivery, freeze, comparison group, recipient set, or assignment from
the returned root is leakage even when its fields are called private. The
contract also loses if it requires equality of complete branch requests,
claims a later practice event from encounter opening alone, or returns a new
root while leaving the predecessor usable as a current head for another
append.
