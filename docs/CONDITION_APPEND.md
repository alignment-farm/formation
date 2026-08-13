# First post-fork condition append

Status: **fixture-local materialization contract**.

This contract covers one operation: bind the public formation condition after
the shared prefix has been forked. It does not define a general event schema,
storage layer, or formation mechanism.

The named computational need is information separation across a branch-local
append. A machine must decide whether one runtime-authored receipt extends the
exact fork root once, cites the correct parent, and contains only the public
condition. Prose cannot perform those identity, provenance, and refusal checks
at runtime.

## Result

The operation produces a new immutable branch-local root or refuses:

```text
verified prefix fork
  -> exact root capability returned before assignment
  -> runtime reserves coordinates for the sealed unlabeled root set
  -> hidden assignment recorded by harness
  -> public condition delivered to runtime
  -> runtime authors one condition segment
  -> harness validates and witnesses without repair
  -> immutable branch-local root | refuse
```

The existing six-line prefix remains unchanged. The new receipt is a separate
one-line segment. Later runtime work consumes the returned two-segment root, not
a reopened path and not a caller's reconstruction.

## Authority and order

The order is part of this contract.

1. The fork controller verifies the runtime-issued prefix handoff and
   `T-C-002`, then returns a distinct immutable root capability. The controller
   retains that exact object before it is given a branch label. Its fork
   operation has no label parameter.
2. The formation runtime claims the sealed roots in their label-blind issuance
   order and reserves one event coordinate for each. The harness receives no
   coordinate-issuance method.
3. The harness assigns `baseline`, `governed`, or `ablation` to that exact root
   and records `T-B-001`, `T-G-001`, or `T-A-001`. The label remains in
   trajectory evidence.
4. From the protocol-frozen map, the harness delivers one complete public
   formation condition. The delivery is bound to the exact root capability and
   contains the public condition, but no label, assignment coordinate, expected
   result, scorer field, or ablation field.
5. The formation runtime records the condition it actually received and emits
   the one-line developmental segment. The harness may not author, insert,
   normalize, or repair these bytes.
6. The fixture validator checks the segment. The harness records one `runtime
   event witnessed` trajectory receipt from the accepted runtime handoff.
7. The append checker returns the immutable branch-local root. A second append
   to the same fork root refuses.

Assignment therefore precedes the developmental append, while the trajectory
witness follows it. The witness observes runtime output; it does not cause that
output.

The harness is allowed to choose public configuration under the frozen
protocol. That is not permission to interpret the acquisition consequence,
propose a candidate change, govern eligibility, or derive replay state.

## Public conditions

The protocol owns two closed condition values.

| Condition | Interpreter | Governor | Influence policy |
| --- | --- | --- | --- |
| `audit_lineage_only-v0` | absent | absent | `declared-role-match-v0` |
| `consequence_governance_activation-v0` | `revision-check-candidate-v0` | `consequence-warrant-v0` | `declared-role-match-v0` |

The frozen assignment map is:

| Hidden harness label | Delivered public condition |
| --- | --- |
| baseline | `audit_lineage_only-v0` |
| governed | `consequence_governance_activation-v0` |
| ablation | `consequence_governance_activation-v0` |

The runtime receives the complete value, not a label or a name that authorizes
it to invent additional procedures. Baseline records explicit `null` values for
its absent interpreter and governor. Governed and ablation have identical
condition payloads at this boundary.

## Root capability and opaque event coordinate

Every successful fork returns a distinct frozen object bearing a private issuer
capability and the current run. The controller retains each exact object and
accepts it once at this append boundary. An equal dataclass copy is not the same
root. This is enough to bind delivery and prove once-only consumption while
exchange remains unselected; no durable branch-root identifier is added to the
record format.

One fixture-local allocator owned by the formation runtime reserves all three
condition-receipt coordinates from the sealed root set before assignment:

```text
D-X-000001
D-X-000002
D-X-000003
```

The runtime receives the roots only in the fork controller's issuance order.
The allocator accepts no branch label, assignment coordinate, condition,
expected result, scorer value, ablation value, or label-bearing harness run
identifier. The harness cannot call or advance it. Its six-digit suffix is only
runtime issuance order within the fixture run. The coordinate is opaque in the
semantic sense: it identifies one event but does not name a branch, condition,
expected outcome, or policy verdict. It is not a secret. The harness may join
it to a branch label in trajectory evidence after the runtime emits the event.

`D-B-007`, `D-G-007`, and `D-A-007` remain readable aliases in
[the fixture](FIXTURE.md). They are not legal materialized coordinates. The same
rule applies to later `D-B-*`, `D-G-*`, and `D-A-*` aliases when those events
eventually earn machine syntax.

The coordinate must be unique among runtime events witnessed in one fixture
run. Unknown forms, collisions, the reserved `D-B-*`, `D-G-*`, or `D-A-*`
grammar, and coordinates containing an explicit branch word refuse. Ordinary
opaque encodings are not rejected merely because they contain a single letter
such as `a`, `b`, or `g`.

## Segment bytes

The fixture-local materializer is `fixture-v0-condition-jsonl-v0`. It emits one
compact JSON object encoded as printable ASCII and terminated by one line-feed
byte. There is no byte-order mark, carriage return, leading or trailing space,
blank line, or extra key. Envelope and payload key order are fixed by the two
templates below.

Baseline, with the issued coordinate substituted for `<opaque>`:

```jsonl
{"contract":"fixture-v0","coordinate":"<opaque>","record":"developmental","order":7,"event":"formation_condition_bound","authority":"formation_runtime","parents":["D-C-006"],"retention":"inline","payload":{"condition":"audit_lineage_only-v0","interpreter":null,"governor":null,"influence_policy":"declared-role-match-v0"}}
```

Governed and ablation, again with only the issued coordinate substituted:

```jsonl
{"contract":"fixture-v0","coordinate":"<opaque>","record":"developmental","order":7,"event":"formation_condition_bound","authority":"formation_runtime","parents":["D-C-006"],"retention":"inline","payload":{"condition":"consequence_governance_activation-v0","interpreter":"revision-check-candidate-v0","governor":"consequence-warrant-v0","influence_policy":"declared-role-match-v0"}}
```

The materializer consumes the exact immutable fork root and the complete public
condition delivery. Payload values come from that delivered value. Envelope
constants belong to the fixture encoder. A producer that ignores the root or
condition and returns a constant literal is nonconforming.

## Runtime handoff

Only the runtime condition materializer issues the typed handoff. It contains:

```text
handoff_id: runtime-issued identifier
run_id: current run
consumed_root: exact in-memory fork capability
source_head: D-C-006
head_after: issued D-X coordinate
materializer: fixture-v0-condition-jsonl-v0
condition: delivered public condition identifier
artifact: immutable one-line segment bytes
```

The harness accepts only the exact current handoff retained by that runtime
materializer. Raw bytes, a path, a mapping, an equal reconstructed object, an
other-run handoff, a handoff for another root, or a stale handoff refuses.

## Validation, provenance, identity, and exchange

These remain different checks.

| Check | Owner | Question |
| --- | --- | --- |
| Semantic validation | Protocol fixture validator | Are these exactly the permitted bytes for this coordinate and delivered condition? |
| Provenance | Runtime handoff and append checker | Did this runtime author the segment from this issued root and delivery? |
| Content identity | Harness witness and append checker | Are the received bytes unchanged from the validated segment? |
| Exchange | Unselected | No cross-implementation format is claimed. |

The content binding covers the complete one-line segment as received:

```text
materializer: fixture-v0-condition-jsonl-v0
identity_contract: fixture-v0-condition-identity-v0
algorithm: sha-256
digest: 64 lowercase hexadecimal characters
byte_length: exact segment byte length
```

There is no one published digest because each clean branch has a different
opaque coordinate. Direct byte comparison is authoritative within the append
operation; SHA-256 is the compact witness retained by trajectory evidence.

The witness cites the assignment receipt, prefix binding, runtime handoff,
condition binding, coordinate, and runtime versions. Before writing it, the
harness checks that the handoff consumed the exact root capability bound to the
delivery. A caller-created witness refuses even if every public field is equal.

## Returned root

The successful result contains:

```text
prefix_root: exact immutable root returned by the fork controller
condition_segment: exact immutable bytes accepted above
head: issued D-X coordinate
condition_binding: complete binding over condition_segment
```

The prefix artifact still contains six lines and retains its original
`T-C-002` binding. The condition segment is not appended to or reclassified as
part of that artifact. Later work must consume this returned value directly.

## Clean checks

A clean fixture demonstrates all of the following:

- three distinct root capabilities fork from the same prefix bytes before
  assignment;
- an equal reconstruction of a root is refused, and permuting assignments
  cannot affect root issuance;
- the runtime reserves three unique developmental coordinates before assignment
  without receiving a label or condition, and the harness cannot advance the
  allocator;
- baseline receives and records `audit_lineage_only-v0`;
- governed and ablation receive the same treatment condition and emit identical
  payload bytes;
- their complete segment bytes differ only because their opaque coordinates
  differ;
- every receipt has order `7` and parent `D-C-006` only;
- each fork root accepts exactly one condition segment; and
- the prefix bytes and binding remain unchanged.

## Refusal checks

Each case starts from an otherwise clean fixture and changes one boundary.

1. Raw bytes, a path, or a mapping replaces the typed fork root, delivery,
   runtime handoff, witness, or returned root.
2. A root, delivery, handoff, witness, or binding is forged, stale, equal but
   reconstructed, from another run, or tied to another root.
3. The prefix binding differs from `T-C-002`, or the prefix bytes change after
   the fork.
4. The root capability is missing, copied, reused, from another run, or not the
   exact object retained before assignment.
5. The condition append is missing, duplicated, has order other than `7`, or
   cites a parent other than exactly `D-C-006`.
6. The harness or caller supplies, inserts, edits, normalizes, or replaces the
   developmental bytes, including with an equal reconstruction.
7. The delivered condition is unknown or does not match the frozen assignment
   map.
8. A condition payload omits, adds, or changes a procedure identity. This
   includes treatment procedures on baseline and absent treatment procedures on
   governed or ablation.
9. Governed and ablation payloads differ at this boundary.
10. A branch label, reserved mnemonic fixture coordinate, expected result,
    scorer field, case family, or verdict appears in any runtime-visible field.
11. An ablation target, `transitive_exclusion`, `causal_probe`, hidden reason,
    or expected effect appears before the declared ablation boundary.
12. The coordinate is malformed, collides with another runtime event, or comes
    from an allocator that can read a label, assignment coordinate, condition,
    or other harness-only input.
13. Semantically equivalent re-encoding changes whitespace, key order, line
    ending, null representation, field names, or framing.
14. The condition line is added as a seventh line of the frozen prefix.
15. A caller-created content binding or trajectory witness bypasses validation.
16. Storage changes after validation, or later work reopens storage instead of
    consuming the returned immutable root.
17. The producer ignores the delivered condition or consumed root.

Artifact validation reports `invalid_fixture_condition_bytes` without exposing
parser detail. Provenance and assignment failures remain attributed to their
own boundary rather than being mislabeled as byte failures.

## Unselected

This contract does not select proposal, admission, activation, correction,
ablation, replay, or scoring syntax. It does not choose a general developmental
or trajectory schema, a storage engine, concatenation of later segments,
per-event hash chains, timestamps, authentication, or cross-implementation
exchange. It establishes no formation effect.

The next record should remain in Markdown until its own computation or refusal
boundary requires materialization.
