# Shared positive-foreground delivery contract

Status: **fixture-local materialization contract; semantic boundary closed;
implementation prerequisites not yet materialized**.

Two independent model families reconstructed this contract from the same
sealed Markdown packet. Both returned `CONTRACT_STABLE_CODE_BLOCKED`: the
contract is internally sufficient, while the governed admitted root and the
ablation root containing `D-A-010` did not yet exist as typed capabilities.
The governed admitted root now exists; the ablation constraint remains open.

Purpose: define the smallest machine boundary needed to prove that baseline,
governed, and ablation receive the same positive foreground from one frozen
source. This contract does not define a general situation schema or model
request format.

## Named computational need

The fixture requires more than three equal-looking mappings. It requires:

```text
one protocol-authored foreground
  -> one immutable comparison-group freeze
  -> one root-bound delivery for each of three exact branch heads
  -> one runtime consumption per delivery
  -> three complete received projections compared with the freeze
```

Value equality cannot establish that a delivery came from the freeze, belonged
to the receiving root, or was consumed only once. A rebuilt equal value, a
correct value sent to the wrong root, and a delivery consumed twice all retain
the same seven public roles. Those are separate refusal cases, so a typed
provenance and linear-consumption boundary is earned.

No byte identity is required. Role order is not semantic, no cross-implementation
exchange is claimed, and no digest is selected.

## Four separate checks

| Check | Question | Owner |
| --- | --- | --- |
| Semantic validation | Is this exactly the closed seven-role `F+` value? | Protocol-owned fixture validator hosted by the harness |
| Provenance | Did this delivery derive from the current comparison group's one freeze? | Foreground freeze and delivery controller |
| Recipient and consumption identity | Was this exact delivery issued for this exact current branch root and consumed once? | Delivery controller and runtime consumption boundary |
| Received-value identity | Does the runtime's complete received projection equal the freeze? | Trajectory witness using direct role-and-value comparison |

None of these checks proves the others. Equal values do not prove provenance;
valid provenance does not make a changed projection valid; and full model
request equality answers the wrong question.

## Exact public foreground

The protocol-authored value has exactly seven roles:

| Role | Exact value and type |
| --- | --- |
| `candidate_object` | string `bundle-9` |
| `derived_from` | string `registry-manifest` |
| `artifact_revision` | integer `7` |
| `authority_revision` | integer `8` |
| `depends_on_current_authority` | boolean `true` |
| `commit_action` | string `release` |
| `refresh_action` | string `rebuild_then_release` |

Role order is not semantic. There is no defaulting, projection from a larger
mapping, ignored extra, string-to-number conversion, or semantic paraphrase.
Any missing, extra, changed, or mistyped role refuses.

The public value contains no branch label, comparison-group identity, case
family, expected result, scorer key, coaching field, intervention field,
ablation target, hidden reason, or expected effect.

## Required recipient capabilities

The controller accepts exactly three current, immutable branch-root
capabilities from the same fixture run:

| Trajectory meaning | Required developmental head |
| --- | --- |
| Baseline recipient | Its `audit_lineage_only-v0` condition-bound head |
| Governed recipient | Its exact eligible admitted-version head after proposal and admission |
| Ablation recipient | Its replay-constrained head containing `D-A-010` |

The trajectory meanings remain harness-only. The runtime-visible delivery does
not contain them. The controller validates the meanings against trajectory
assignment and witnessed lineage; it does not infer them from a root's issue
order, public condition, or documentary alias.

The baseline condition-bound and governed admitted capabilities now exist. The
ablation replay-constrained root containing `D-A-010` does not. Raw coordinates,
prose aliases, mappings, condition-only substitutes for governed or ablation,
reconstructed equal roots, stale roots, other-run roots, and roots from another
comparison group refuse.

This prerequisite is load-bearing. Implementing against placeholder or
condition-only roots would permit presentation before admission or replay
constraint and would answer a different causal question.

## Authority and order

1. The human protocol owner authors the exact seven-role value before contact.
2. The required three current root capabilities exist and have been witnessed.
   In particular, the ablation root contains `D-A-010`.
3. The harness binds one comparison group and its exact recipient set. Hidden
   case assignments and expected results are not inputs to the public value.
4. A protocol-owned source adapter reads the frozen protocol value and produces
   one immutable `FixturePositiveForegroundSource`.
5. The foreground controller consumes that source once and creates one
   `FrozenPositiveForeground` for the current run, comparison group, and exact
   recipient set.
6. Before any positive branch-local `case assigned`, the trajectory recorder
   records `foreground bound` from that exact freeze.
7. Each positive `case assigned` cites the freeze. The controller derives one
   `PositiveForegroundDelivery` for each exact authorized root.
8. Branch execution order is free. Each runtime consumes its exact delivery
   once when opening the positive encounter and returns a typed
   `ReceivedForegroundHandoff`.
9. The harness validates and witnesses the returned handoff without producing,
   normalizing, replacing, or repairing its public value.

The controller may know the recipient mapping in its harness role. The public
delivery exposes only the seven roles to the runtime's practice input.

## Freeze capability

Only the foreground controller may construct `FrozenPositiveForeground`. It
contains:

```text
run: current fixture-run capability
comparison_group: exact harness-only group capability
source: exact immutable FixturePositiveForegroundSource
foreground: exact immutable seven-role value
authorized_roots: exact closed set of three current root capabilities
```

The freeze has a private issuer identity retained by the controller. An equal
reconstructed object is not the freeze. The source and foreground are captured
once; the controller may not reopen protocol storage later.

The fixture validator checks the complete source value before any delivery is
issued. It returns only `valid_fixture_positive_foreground` or
`invalid_fixture_positive_foreground`. It may not repair, normalize, sort, add,
or remove roles.

## Root-bound deliveries

For each authorized root, the controller derives exactly one
`PositiveForegroundDelivery` containing:

```text
freeze: exact FrozenPositiveForeground capability
recipient: exact authorized current root capability
foreground: the exact immutable value captured by the freeze
```

The delivery carries private provenance and recipient binding for enforcement.
Its runtime-visible projection contains only the seven public roles. It exposes
no branch label, comparison group, recipient list, expected result, or hidden
case fact.

The controller retains each exact delivery object. Raw mappings, caller-created
deliveries, equal reconstructions, caller replacements, other-run deliveries,
wrong-root deliveries, fourth-recipient deliveries, and deliveries derived from
another freeze refuse.

Issuing a delivery is not consumption. Each authorized root has exactly one
issued delivery and one permitted consumption. A missing, duplicated, reused,
or multiply consumed delivery refuses.

## Runtime consumption and returned handoff

The runtime consumption boundary accepts the exact current root and exact
delivery retained for it. It checks the private issuer, run, freeze, comparison
group, recipient object, and unused state before exposing the public foreground
to encounter construction.

On success it atomically marks the delivery consumed and returns one immutable
`ReceivedForegroundHandoff`:

```text
run: current fixture-run capability
consumed_root: exact current recipient root
consumed_delivery: exact PositiveForegroundDelivery
foreground: exact immutable seven-role value received
```

Only the runtime consumption boundary may construct this handoff. It accepts no
raw mapping, path, alias, caller-created binding, or equal reconstructed object.
Failure returns no handoff and does not partially open an encounter.

The future positive `encounter opened` materializer must consume this exact
handoff and retain its complete seven-role situation projection. It may not
reopen storage or reconstruct the foreground. That encounter materializer and
its developmental receipt syntax remain unselected here.

## Witness

The harness accepts only the exact current `ReceivedForegroundHandoff` retained
by the runtime consumption boundary. Before recording the trajectory witness it
checks:

1. the freeze belongs to the current run and comparison group;
2. the exact consumed root is in the freeze's closed authorized set;
3. the delivery is the one retained for that root and freeze;
4. the delivery was issued and consumed exactly once;
5. the complete received seven-role value directly equals the frozen value;
6. the branch-local `case assigned` receipt cites that freeze; and
7. no hidden or extra field appears in the received projection.

Direct role-and-value comparison is authoritative. There is no digest. The
witness does not compare the complete model request, activation state, action,
or consequence. Governed may add its activation handoff after foreground
receipt; baseline and ablation must not.

The witness may later cite the positive `encounter opened` receipt when that
receipt earns materialization. Until then it witnesses only the foreground
handoff and cannot claim that a developmental encounter was appended.

## Refusal vectors and ownership

Each refusal starts independently from the clean source, freeze, recipient set,
delivery, consumption boundary, or witness:

1. Change, omit, add, default, or change the type of any public role.
2. Add a branch label, case family, expected result, scorer key, coaching field,
   intervention field, ablation target, hidden reason, or expected effect.
3. Use a constant producer that ignores the protocol source.
4. Reopen mutable protocol storage or independently rebuild the foreground
   after freeze, including a value-equal rebuild.
5. Supply a raw mapping, path, caller replacement, or caller-created freeze,
   delivery, received handoff, binding, or witness.
6. Use an equal reconstructed, stale, other-run, other-group, wrong-head,
   condition-only, or documentary-alias root.
7. Omit one of the three required roots, add a fourth root, duplicate a root, or
   bind the wrong developmental head to a trajectory meaning.
8. Issue no delivery, more than one delivery, or a delivery for a root outside
   the freeze's exact recipient set.
9. Deliver before the freeze, before the ablation constraint, before the
   branch-local case assignment cites the freeze, or after the permitted
   positive boundary.
10. Consume a delivery with another root, another freeze, another run, or
    another comparison group.
11. Consume a delivery zero times, twice, after reuse, or after replacement.
12. Mutate, replace, or reopen the foreground between validation, delivery,
    runtime consumption, and witness.
13. Let the harness author, normalize, repair, or replace the runtime's received
    handoff or projection.
14. Ignore extra received fields, compare only a partial projection, default a
    missing role, or compare complete branch-specific requests.
15. Treat a foreground witness as proof that `encounter opened` or any later
    developmental event was appended before those materializers exist.

The fixture validator owns public-value refusals. The controller owns source,
freeze, recipient-set, issuance, provenance, and replacement refusals. The
runtime consumption boundary owns wrong-root and linear-consumption refusals.
The witness owns received-projection and comparison-scope refusals.

## Implementation gate

The semantic object and named computation are closed, but this slice is not yet
buildable. Code begins only after the project materializes typed current root
capabilities for:

- the baseline condition-bound head;
- the governed admitted head; and
- the ablation replay-constrained head containing `D-A-010`.

The existing baseline condition root and governed admitted root satisfy their
two prerequisites. The ablation admitted root is only an ancestor of its
required replay-constrained root. Using it before `D-A-010` would bypass the
fixture's causal order.

When all three prerequisites exist, a new cold review must confirm that their
exact types and issuer boundaries satisfy this contract. Only then may the
foreground freeze, delivery, consumption, witness, and refusal-test slice be
implemented.

## Unselected

This contract does not select:

- JSON, JSON Lines, a digest, canonical role order, or a storage format;
- a general situation, foreground, developmental, or trajectory schema;
- proposal, admission, replay-constraint, or encounter receipt syntax;
- how later root artifacts concatenate or bind their retained lineage;
- model-request bytes or cross-branch request equality;
- decoy, correction, post-revocation, action, consequence, or scoring syntax;
- cross-implementation exchange, distributed writers, or authentication; or
- any formation, transfer, or causal finding.

## Acceptance and loses-conditions

This contract is sufficient only if independent readers reconstruct one closed
value, freeze authority, exact prerequisite recipient set, delivery provenance,
linear consumption boundary, direct witness, refusal ownership, and
implementation gate.

The first cold contract review met that condition. Both readers independently
reconstructed the exact seven roles, four separate checks, three required
recipient heads, one-shot delivery and handoff, witness scope, refusal
ownership, and non-license boundary. Both also found the existing
condition-append output sufficient only for the baseline recipient and returned
`CONTRACT_STABLE_CODE_BLOCKED`.

It loses if equal public values can substitute for provenance, if a delivery can
reach the wrong root or be consumed twice, if hidden assignment enters the
runtime-visible foreground, if the witness ignores an extra role, if full
request equality erases the governed intervention, or if placeholder roots
allow positive presentation before admission and replay constraint.
