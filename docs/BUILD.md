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
- No candidate affects practice before admission.
- Every activation cites the admitted change and current situation.
- Non-activation is observable without exposing hidden harness labels.
- Suspension and revocation prevent later activation.
- Every ablation names its target, public condition, runtime receipt, and frozen
  boundary without changing unrelated state.
- A replay exclusion makes dependent effects unavailable or produces an
  explicit unresolved dependency.
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

The following proposal and direct-admission boundary remains Markdown-only.
Cold reconstruction exposed missing distinctions between candidate author and
recorder, governor and runtime host, candidate applicability and admitted
scope, and equivalent text and the exact proposal version. The repaired record
and fixture contracts now fix those meanings, baseline silence,
treatment-branch equality, and the one-shot causal order. Both model-family
rechecks and an additional independent review return `PASS`. No deterministic
identity, validation, or exchange operation has yet been named for these
receipts, so this semantic convergence does not license their materialization.

The semantic [deterministic fixture v0](FIXTURE.md) and its governing packet have
been cold-reviewed and simplified so a pre-admission trial is not a schema
requirement. The shared-prefix and first condition-append boundaries now have
licensed fixture-local implementations; the later proposal, governance,
practice, replay, ablation, and scoring paths remain wire-only. The [instrument
map](INSTRUMENTS.md) keeps each later design layer in Markdown until another
named replay, separation, identity, or refusal ambiguity requires machine
syntax.

The fixture's semantic schedule and compatibility boundary are explicit. The
prefix draft selects SHA-256 only for same-producer fork comparison; it does not
license byte exchange, per-event digests, hash chains, clocks, or a universal
lifecycle. The independently reconstructed literal bytes and refusal ownership
license only the prefix slice above; the full walking skeleton remains gated.
