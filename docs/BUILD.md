# Initial build boundary

Status: **planning contract; implementation has not begun**.

## First build objective

Build a deterministic walking skeleton that proves the practice loop and
formation loop can be separated, replayed, forked, and causally inspected. It
must not claim to learn, generalize, or improve a model.

## Proposed initial layout

```text
formation/
  lineage.py       append, validate, and replay developmental events
  practice.py      ports and orchestration for situation, inference, action,
                   and external consequence
  development.py   candidate-change lifecycle and activation boundary
  runtime.py       explicit composition of practice and formation loops
trajectory/
  harness.py       fork starting states and execute controlled histories
  fixtures.py      deterministic environments, consequences, and cases
  scoring.py       computed wire and later behavioral verdicts
tests/
  test_lineage.py
  test_separation.py
  test_lifecycle.py
  test_replay.py
  test_forking.py
```

Names are provisional until Phase 0 fixes the contracts. In particular,
`development.py` must not become a miscellaneous policy container.

## Minimal governance path

The skeleton needs only enough state to expose the distinctions under test:

```text
observed -> candidate -> admitted or rejected
admitted -> suspended -> reinstated
admitted -> revised
admitted -> revoked
admitted -> activation considered -> activated or withheld
```

Transitions require declared runtime-governor receipts and source lineage. The
model may propose a candidate but cannot declare its own proposal admitted. The
[authority boundary](AUTHORITY.md) defines why the trajectory harness cannot
stand in for that governor.

A selected policy may insert a bounded trial before admission or use
probationary influence, but the first schema must not require either. Those are
formation-mechanism choices, not structural properties of developmental
lineage.

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

1. An identical practitioner state is forked into baseline and treatment.
2. Both take the same authored bad action in a training encounter.
3. Both receive the same external consequence.
4. Only treatment proposes a candidate and applies its declared governance
   policy; this fixture's policy admits directly from the authored consequence
   warrant.
5. A structurally matching later encounter activates the admitted change.
6. A superficially similar but structurally mismatched encounter does not.
7. Counterevidence suspends or revokes the change.
8. Replay reproduces every state, and ablation removes only the attributed
   downstream influence.

Passing this scenario establishes plumbing and separation only.

## Invariants to test

- Event order and causal references are valid and deterministic.
- Replay is authoritative; caches cannot change semantic state.
- Forks share an exact prefix and diverge only at declared assignments.
- No candidate affects practice before admission.
- Every activation cites the admitted change and current situation.
- Non-activation is observable without exposing hidden harness labels.
- Suspension and revocation prevent later activation.
- Removing one experience or change removes its dependent effects or produces an
  explicit unresolved dependency.
- Harness-only fields cannot enter the runtime offer.
- Model self-report cannot manufacture an external consequence or admission.

## Explicit non-goals for the first build

- selecting a universal representation of skill or disposition;
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

Both specifications now have initial drafts. Code remains gated on review plus
one deterministic fixture that demonstrates their shared coordinates and
refusal paths.

The semantic [deterministic fixture v0](FIXTURE.md) has been cold-reviewed and
simplified so a pre-admission trial is not a schema requirement. It remains
wire-only and unimplemented; schema selection and encoding are still gated on
the fixture's explicit separation and refusal conditions.
