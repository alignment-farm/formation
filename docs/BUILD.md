# Initial build boundary

Status: **planning contract; the walking skeleton is incomplete, with two
fixture-local materialization slices implemented**.

## First build objective

Build a deterministic walking skeleton that proves the practice loop and
formation loop can be separated, replayed, forked, and causally inspected. It
must not claim to learn, generalize, or improve a model.

## Required build surfaces

The first build must expose the formation-runtime, trajectory-harness,
environment-or-oracle, and scorer authorities described in the instrument map.
It also needs deterministic conformance checks for lineage, replay, separation,
forking, governance, influence, and refusal paths.

No package, module, class, or file layout is selected yet. Fixture-authored
practice, interpreter, governor, and influence stubs retain their declared
logical authorities even if one test process eventually hosts them. Placement
under test or fixture support cannot give the harness role permission to author
their developmental receipts.

## Minimal governance path

The skeleton needs only enough state to expose the distinctions under test:

```text
observed -> candidate proposed -> admitted
admitted -> revoked
admitted -> suspended -> revoked
admitted -> activation considered -> activated or withheld
```

Transitions require declared runtime-governor receipts and source lineage. The
model may propose a candidate but cannot declare its own proposal admitted. The
[authority boundary](AUTHORITY.md) defines why the trajectory harness cannot
stand in for that governor.

A selected policy may insert a bounded trial before admission or use
probationary influence, but the first materialization contract must not require
either. Those are formation-mechanism choices, not structural properties of
developmental lineage.

The shared record vocabulary can describe rejection, reinstatement,
supersession, expiry, and revision, but the first build does not implement them
unless the fixture is revised to exercise them. A vocabulary entry is not a
licensed runtime transition.

## Required separations

### Occurrence, interpretation, and policy

- Occurrence records what situation, action, and consequence happened.
- Interpretation proposes what might be learned from it.
- Policy decides whether that proposal may influence later practice.

These should be separately attributable even if an early implementation stores
them in one event stream.

### Runtime and trajectory harness

The runtime owns experience processing and change activation. The harness owns
experimental assignment, hidden evaluation structure, branching, and scoring.
The runtime must not see branch labels, expected answers, counterfactual
outcomes, or held-out family identities.

### Model output and external consequence

The model's assessment of its action can be retained, but it cannot overwrite
the environment's result or oracle verdict.

## First deterministic scenario

The walking skeleton should enact this sequence without an LM:

1. One cold practitioner takes the authored bad action in the acquisition
   encounter and receives its external consequence.
2. The retained acquisition prefix is materialized once and forked into
   baseline, governed, and ablation branches.
3. Governed and ablation independently propose a candidate and apply the same
   declared governance policy; this fixture's policy admits directly from the
   authored consequence warrant. Baseline does neither.
4. After ablation admission and before later practice, the ablation runtime
   binds the public replay constraint and derives its own constrained view.
5. The same structurally matching later encounter reaches all three branches:
   governed activates, baseline has no admitted change, and ablation withholds
   for an unresolved dependency.
6. A superficially similar but structurally mismatched encounter reaches
   governed and does not activate the admitted change.
7. The same counterevidence reaches every branch. Governed suspends and revokes
   under the fixture policy; baseline and ablation emit no governance change.
8. A later matching governed encounter withholds after revocation.
9. Replay reproduces every state. In the ablation branch, excluding the source
   consequence makes its warrant, candidate, admission, and later influence
   unavailable or explicitly unresolved in the derived view.

Passing this scenario establishes plumbing and separation only.

## Invariants to test

- Event order and causal references are valid and deterministic.
- Replay is authoritative; caches cannot change semantic state.
- Forks share an exact prefix and diverge only at declared public conditions or
  their downstream effects.
- Each paired comparison uses one frozen, closed foreground delivered once to
  every declared branch; later request differences do not alter that identity.
- No candidate affects practice before admission.
- Every activation cites the admitted change and current situation.
- The exact admitted lineage object considered is the one selected, bound into
  the encounter-local intervention, and consumed by request construction.
- A model invocation retains an exact request or binding to the immutable
  activation handoff; repeated names or copied candidate text do not establish
  identity.
- Non-activation is observable without exposing hidden harness labels.
- Suspension and revocation prevent later activation.
- Every ablation names its target, public condition, runtime receipt, and frozen
  boundary without changing unrelated state.
- A replay exclusion makes dependent effects unavailable or produces an
  explicit unresolved dependency.
- Replay consumes the actual retained dependency projection; a target-keyed
  fixture lookup cannot stand in for lineage derivation.
- Replay preserves non-dependent state and the active constraint while making
  each unresolved result traceable to a retained dependency path.
- Harness-only fields cannot enter the runtime offer.
- Model self-report cannot manufacture an external consequence or admission.

## Explicit non-goals for the first build

- selecting a universal representation of skill or disposition;
- implementing a universal lifecycle state machine;
- optimizing retrieval;
- integrating a production agent framework;
- supporting distributed writers, compaction, or schema migration;
- contacting an LM;
- demonstrating transfer or practitioner improvement;
- importing Construct's Body Core wholesale; or
- choosing the first application domain.

## Implementation gate

Before code begins, Phase 0 should produce two small specifications:

1. the [authority and information-flow boundary](AUTHORITY.md); and
2. the [minimal developmental record and lifecycle contract](RECORD.md).

Those specifications should contain their own loses-conditions. If the same
tests can be passed by the trajectory harness directly inserting a correct
lesson, the boundary is insufficient.

Both specifications and the deterministic fixture have completed their current
Markdown boundary review. Two independent semantic constructions now agree on
the receipt graph and refusal outcomes. That convergence closes semantic
prototyping; it did not by itself select syntax or license code. The first named
need is now content identity across the fixture fork. Its [fixture-local
materialization contract](MATERIALIZATION.md) selects a producer artifact,
validator, runtime handoff, and byte binding. Grok and Composer independently
reconstructed the repaired contract, found no remaining authority contradiction,
and returned `code_slice_licensed`.

That confirmation licenses only the fixture-local source adapter,
six-line producer, exact-literal validator, frozen runtime handoff, direct byte
comparison, compact digest binding, and their refusal tests. It does not license
the full walking skeleton, a general recorder, replay schema, storage layer, or
trajectory harness.

That licensed slice is implemented. Eleven deterministic tests pass. Two
post-build authority reviews found caller-created witness and binding bypasses;
both were reproduced, repaired, and added to the refusal suite before the final
reviews returned `PASS`.

The next named computation is the first post-fork condition append. Its
[fixture-local contract](CONDITION_APPEND.md) closes the hidden-label boundary:
the runtime reserves opaque coordinates over the sealed unlabeled roots before
the harness assigns branches, records one public condition in a separate
segment, and returns an exact immutable branch-local root. The implementation
passes the combined twenty-six-test suite. Independent post-build semantic and
authority reviews return `PASS` after concrete duplicate-assignment,
duplicate-witness, forged-root-order, coordinate-channel, and reservation
mutation attempts were reproduced and closed.

The proposal and direct-admission boundary is now implemented as typed
in-memory capabilities. Its earlier Markdown review fixed candidate author
versus recorder, governor versus runtime host, candidate applicability versus
admitted scope, and equivalent text versus the exact proposal version. Shared
foreground then named the missing computation: later work needs exact current
admitted-root identities. [ADMITTED_ROOT.md](ADMITTED_ROOT.md) therefore
licenses one label-blind two-root batch, source-reading interpreter authorship,
direct governor admission over the exact proposal, and returned admitted roots,
while leaving receipt bytes and a general lifecycle schema unselected.

The implementation passes 45 tests. Post-build review rejected the first
39-test green state: it reproduced shallow nested mutation, upstream-binding
mutation, and authority strings that did not prove distinct interpreter or
governor calls. The repaired slice retains and revalidates the complete runtime
chain from condition root through source, authorship, proposal, decision, and
admission. Final independent mechanical recheck returns `PASS`.

The next named computation is the fixture-local public replay-constraint
append. Its [typed contract](REPLAY_CONSTRAINT_APPEND.md) separates exact
constraint binding from unearned constrained replay. The implementation
selects the exact ablation admitted root through retained trajectory assignment,
delivers only a public target role and `transitive_exclusion`, lets the runtime
resolve that role inside its own retained lineage, and returns one exact
post-constraint root. No receipt bytes, digest, replay view, or traversal is
selected.

The combined 64-test suite passes. Post-build review rejected the first green
57-test version because broad verifier backpointers exposed harness state and
caller-created coordinates, deliveries, or runtime facades could counterfeit
provenance. The repaired boundary factory-issues the sole controller, reserves
both treatment slots before later ablation assignment, registers one narrow
exact public delivery, and revalidates the complete one-use chain whenever the
returned root is consumed. Final independent mechanical recheck returns
`PASS`.

The next cold gate contacted fixture-local transitive replay exclusion. It
exposed a lineage-insensitive shortcut: returning the documented closure from
the target token could satisfy the earlier fixture. The repaired contracts make
the actual retained dependency projection authoritative, distinguish
state-bearing dependencies from control references, preserve non-dependents,
and add refusal legs 17 through 20. Both model-family rechecks reconstruct one
compatible object. They do not license code: with one fixed graph, exact graph
validation followed by the authored result remains observationally equivalent
to a general traversal. Adding graph variants solely to force that distinction
would select unearned replay architecture.

The activation-identity gate remains Markdown-only as well. Cold reconstruction
found that repeated version names and copied candidate text could imitate an
attributable activation. The repaired fixture fixes the exact admitted and
proposal lineage objects, causal parents, encounter-local intervention handoff,
one-shot request consumption, withheld-path absence, and refusal legs 21
through 24. Independent rechecks agree on one semantic object. No byte identity
or cross-boundary exchange is required to enforce those same-runtime
references, so an activation or request materialization contract is not earned.

The shared positive-foreground semantic gate is closed. Cold review exposed an
ambiguous freeze point, inconsistent role count, and possible confusion between
the common situation and the intentionally different model requests. The
repaired fixture freezes one closed seven-role value, derives one delivery per
branch root, compares each received projection directly, and adds refusal legs
25 through 31. A focused license review then found that rebuilt-equal,
wrong-root, and twice-consumed deliveries cannot be refused by value inspection
alone. The [foreground-delivery contract](FOREGROUND_DELIVERY.md) therefore
earns a narrow typed freeze, root-bound delivery, consumption, and witness
boundary without selecting bytes. The contract originally waited for real
governed-admission and ablation-constraint root capabilities. Both now exist.
Two independent cold reconstructions agreed on the full contract and originally
returned `CONTRACT_STABLE_CODE_BLOCKED`; its exact type and issuer boundary now
needs a final code-facing review before implementation.

The semantic [deterministic fixture v0](FIXTURE.md) and its governing packet have
been cold-reviewed and simplified so a pre-admission trial is not a schema
requirement. The shared-prefix, first condition-append, direct-admission, and
replay-constraint append boundaries now have licensed fixture-local
implementations; later governance, practice, replay derivation, and scoring
paths remain wire-only. The [instrument
map](INSTRUMENTS.md) keeps each later design layer in Markdown until another
named replay, separation, identity, or refusal ambiguity requires machine
syntax. The later foreground-delivery contract is semantically earned, and all
three prerequisite root capabilities now exist.

The fixture's semantic schedule and compatibility boundary are explicit. The
prefix draft selects SHA-256 only for same-producer fork comparison; it does not
license byte exchange, per-event digests, hash chains, clocks, or a universal
lifecycle. The independently reconstructed literal bytes and refusal ownership
license only the prefix slice above; the full walking skeleton remains gated.
