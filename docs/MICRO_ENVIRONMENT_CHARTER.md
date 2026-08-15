# Revision-gated release micro-environment charter

Status: **pre-contact charter; computational code slice licensed**.

## Purpose

Build the smallest state-transition engine needed to distinguish an action
lookup from state-dependent execution. This micro-environment is a computation
specimen. It is not a formation fixture, a simulated world, or evidence that a
practitioner learned anything.

The existing deterministic fixture asks the environment to evaluate one stale
revision state. In that single state, a program can map `release` to rejection
and `rebuild_then_release` to acceptance without reading revisions. This charter
introduces independently useful state variation so that shortcut no longer
passes.

## Question

Can one deterministic environment apply the same declared transition rule to a
bounded family of states, such that the same action produces different results
when the state changes?

The answer is computational. No language model, developmental history,
retrieval system, lesson, governor, activation mechanism, or scorer judgment is
needed.

## Frozen state and action language

An input state has exactly two integers:

```text
artifact_revision
authority_revision
```

The environment accepts exactly two actions:

- `release`
- `rebuild_then_release`

There are no branch labels, expected outcomes, case-family labels, candidate
objects, provenance graphs, hidden interventions, retry instructions, or
natural-language aliases.

## Transition rule

The public rule is `revision-gated-release-v0`:

1. `release` leaves the artifact revision unchanged.
2. `rebuild_then_release` first sets the artifact revision to the authority
   revision.
3. Release is accepted exactly when the resulting artifact revision equals the
   authority revision.

The result contains only:

```text
action
artifact_revision_before
artifact_revision_after
authority_revision
disposition: accepted | rejected
observation: released | stale_dependency
```

`released` accompanies `accepted`. `stale_dependency` accompanies `rejected`.
The input state is immutable; the after-state is a new value returned by the
transition.

## Prospective case family

Before implementation, freeze the revision domain as every ordered pair drawn
from:

```text
0, 1, 2, 7, 8, 41, 42
```

Apply both actions to every pair. This yields 98 cases: 49 states times two
actions. Each engine case contains exactly
`(artifact_revision, authority_revision, action)`. Expected disposition,
observation, and after-state exist only in an external conformance oracle that
applies the public rule after receiving the engine result. They are never fields
on the case object or inputs to the engine.

The domain deliberately contains equal and unequal revisions, adjacent and
non-adjacent values, zero, and the revision values used by the deterministic
fixture. It is bounded to keep exhaustive execution cheap. It is not claimed to
represent all integers or real deployment revisions.

The cases are generated from the Cartesian product of the frozen domain and
action set. They are not written as an action-to-answer table.

Canonical enumeration uses the listed artifact revisions as the outer loop,
the listed authority revisions as the middle loop, and actions in the listed
order as the inner loop. Number those cases 0 through 97. Two execution orders
are frozen now:

- order A takes source index `(37 * position + 11) mod 98` for positions 0
  through 97;
- order B takes source index `(55 * position + 23) mod 98` for positions 0
  through 97.

Both multipliers are coprime to 98, so each order visits every case exactly
once. Neither order reads or groups by oracle output.

## Decisive contrasts

The implementation gate depends on these prospective contrasts:

- `release` must accept for every equal pair.
- The same `release` action must reject for every unequal pair.
- `rebuild_then_release` must accept for both equal and unequal pairs.
- For equal pairs, rebuilding must leave the revision value unchanged.
- For unequal pairs, rebuilding must change the artifact revision to the exact
  authority revision.

An implementation that returns one result per action cannot pass. The
`release` outcome must depend on state, and the rebuild after-state must depend
on the supplied authority revision.

A finite program could still memorize all 98 cases. This charter does not claim
to prove otherwise. Its narrower claim is that conformance cannot be achieved
by the action-only shortcut that blocks the deterministic fixture.

## Prospective refusal cases

Refusals are frozen before implementation:

1. Unknown, missing, empty, or non-string action.
2. Missing or extra state fields.
3. Boolean, string, float, null, container, or other non-integer revision.
   Booleans refuse even where the host language treats them as integers.
4. Caller-supplied disposition, observation, or after-state.
5. Mutation of input state during execution.
6. A result whose before-state differs from the supplied state.
7. Rejection after the transition reaches equal revisions.
8. Acceptance while the resulting revisions differ.
9. `release` changing the artifact revision.
10. `rebuild_then_release` producing an after-revision other than the exact
    authority revision.
11. Execution that depends on case order, prior cases, fixture branch, or hidden
    expected result.
12. Reusing one mutable result object across cases.

Refusal tests establish input closure and transition invariants. They do not
introduce runtime capabilities, developmental lineage, or harness authority
machinery.

The concrete witnesses are frozen before implementation:

| Clause | Frozen witness |
| --- | --- |
| 1 | Valid state `(7, 8)` with action `Release`; separately omit the action and use integer action `1` |
| 2 | Omit `authority_revision`; separately add field `expected_disposition` |
| 3 | Substitute `True`, `"7"`, `7.0`, `null`, and `[7]` for each revision position |
| 4 | Add caller fields `disposition: accepted`, `observation: released`, or `artifact_revision_after: 8` |
| 5 | Snapshot input `(7, 8)` before `rebuild_then_release` and compare it after return |
| 6 | Counterfeit result for input `(7, 8, release)` with before-revision `8` |
| 7 | Counterfeit result for `(8, 8, release)` with disposition `rejected` and observation `stale_dependency` |
| 8 | Counterfeit result for `(7, 8, release)` with disposition `accepted` and observation `released` |
| 9 | Counterfeit result for `(7, 8, release)` with after-revision `8` |
| 10 | Counterfeit result for `(7, 8, rebuild_then_release)` with after-revision `7` |
| 11 | A diagnostic engine whose answer alternates by call count, run under canonical order and orders A and B |
| 12 | Execute `(7, 8, release)` and `(7, 8, rebuild_then_release)` and require distinct result identities |

The conformance oracle must also reject either mismatched pair
`accepted`/`stale_dependency` or `rejected`/`released`, even when the remaining
fields look valid. Counterfeit results test the oracle and contract invariants;
they are never fed to the engine as expected answers.

## Independence and reset

Every case starts from its supplied immutable state. The engine carries no
state from one case to the next. Running the same case twice yields equal result
values in distinct result objects. Reordering the 98 cases leaves the mapping
from input state and action to result unchanged.

This is deliberate. Stateful trajectories belong to later contact. Here,
cross-case memory would make the transition harder to inspect without answering
the charter's question.

## Comparator

The explicit losing comparator is an action-only implementation:

```text
release -> rejected, stale_dependency
rebuild_then_release -> accepted, released
```

It matches the existing positive fixture but fails this charter because
`release` must also succeed when revisions are equal and rebuild output must
track different authority revisions.

A second diagnostic comparator may read whether revisions are equal but return
fixed after-state values. It must fail the prospective after-state checks. These
comparators are demonstrations of the computational pressure, not experimental
branches or scientific baselines.

## Pass condition

The micro-environment passes only if:

- all 98 prospective cases satisfy the transition rule;
- all refusal cases fail closed;
- input states remain unchanged;
- repeated runs produce equal values in distinct result objects;
- at least two fixed case permutations produce the same input-to-result map;
  and
- the action-only and fixed-after-state comparators fail their named contrasts.

One failed clause closes the run as nonconforming. There is no partial credit.

## Claim boundary

Passing would establish one bounded engineering fact: the tested engine's
outputs depend on both the declared action and supplied revision state across
this frozen domain. It would clear only the action-only observational blocker
for this transition function. It would not license the environment-
application handoff, identity, registry, or lifecycle code.

Passing would not establish:

- formation, acquisition, transfer, selectivity, or revision;
- a useful persistence mechanism;
- correctness for all integers, concurrency, storage, retries, or distributed
  execution;
- realism of the release scenario;
- environment-result provenance or developmental-lineage correctness; or
- superiority over a simpler persistence baseline.

Those claims require different contact.

## Stopping rule and handoff to contact

Stop this micro-environment after one reviewed implementation passes the frozen
case family and refusals. Do not add more fake-world state, entities, tools,
histories, or policy language. Do not tune it into a benchmark.

The next experiment must move toward model contact in a task where ordinary
persistence is a serious comparator and is allowed to win. Before that contact,
a separate charter must freeze the cold model, static instructions, raw episode
or transcript persistence, authored-lesson branch, governed branch, prospective
transfer and non-transfer cases, costs, and stopping rule.

## Implementation gate

Implementation is licensed only if independent cold readers agree that:

1. the 98 cases are prospective and fully generated from the frozen domain;
2. the same `release` action must produce both accepted and rejected results;
3. rebuild after-state must vary with the supplied authority revision;
4. no expected-result or fixture-branch input is needed;
5. the claim remains bounded to state-dependent computation; and
6. the stopping rule prevents this specimen from growing into another synthetic
   world.

The code-facing review must show that these contrasts fail an action-only
implementation before code is written.

Two independent final cold readers reconstructed the same input-only cases,
offline oracle, permutations, refusals, comparators, bounded claim, and stopping
rule. An earlier review exposed and repaired expected-output ambiguity, unnamed
permutations, unfrozen refusal witnesses, and an overbroad lifecycle handoff.

Code-facing review then demonstrated that the action-only comparator fails all
seven equal-revision `release` cases and that an equality-aware fixed-after-state
comparator fails whenever rebuild must track another authority revision. It
returned `CODE_SLICE_LICENSED` for only the isolated transition engine,
external conformance oracle, and frozen tests. Environment-application handoff,
registry, lineage, and formation code remain unlicensed by this charter.

## Loses-conditions

The charter loses if cases are chosen or changed after seeing implementation
output; if expected results enter the engine; if the engine can pass without
reading state; if mutable cross-case state affects results; if passing is called
formation or transfer; or if additional fictional complexity is added instead
of proceeding toward contact with simpler persistence baselines.
