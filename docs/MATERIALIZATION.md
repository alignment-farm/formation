# First materialization contract

Status: **fixture-local contract implemented; two-family cold reconstruction
and post-build authority review complete**.

Purpose: define the smallest machine object needed to prove that every branch
of the first fixture starts from the same materialized developmental prefix.
This contract does not define a general event format.

## Named computational need

The fixture creates `D-C-001` through `D-C-006` once. Before branch assignment,
the harness must compute whether each branch root contains the exact same
materialized prefix.

The required operation is:

```text
runtime's frozen six-receipt source -> one frozen prefix handoff
frozen prefix handoff -> one compact content binding
current handoff + T-C-002 + claimed binding -> immutable branch root | refuse
```

Semantic compatibility is not enough. Re-encoding an equivalent receipt graph
produces another materialization and must not pass this check.

## Four separate checks

The first implementation must not ask one digest to establish four different
facts:

| Check | Question | First owner |
| --- | --- | --- |
| Semantic validation | Does the artifact contain exactly the six permitted developmental receipts? | Protocol-owned fixture validator, which the harness may host |
| Provenance | Did this trusted implementation receive the artifact through the current runtime handoff? | Runtime handoff boundary witnessed by the harness |
| Content identity | Are these the same artifact bytes? | Harness prefix and fork controller using direct byte comparison |
| Exchange | Can another implementation produce or consume the same bytes? | Unselected |

A digest is a compact content witness, not proof of byte equality, authorship,
or validity. Byte-identical content does not reveal who produced it. Identically
copied invalid content remains invalid. A canonical semantic projection answers
a different question and may erase an extra forbidden field.

## Fixture-local prefix artifact

The producer contract is `fixture-v0-prefix-jsonl-v0`. It emits one byte string
containing six JSON lines in developmental record order. The artifact:

- is UTF-8 without a byte-order mark;
- contains printable ASCII only;
- uses the exact bytes below, including key order and compact punctuation;
- ends every record, including the last, with one line feed byte `0a`;
- contains no carriage return, leading or trailing space, blank line, or extra
  record; and
- contains no trajectory receipt or harness-only field.

The complete clean artifact is:

```jsonl
{"contract":"fixture-v0","coordinate":"D-C-001","record":"developmental","order":1,"event":"practitioner_initialized","authority":"formation_runtime","parents":[],"retention":"inline","payload":{"model_identity":"cold-model-stub-v0","model_configuration":"deterministic-v0","runtime_interface":"formation-runtime-v0","initial_lineage_head":null,"supported_interfaces":["practice-v0","formation-procedure-v0","governance-v0","influence-v0","replay-v0"]}}
{"contract":"fixture-v0","coordinate":"D-C-002","record":"developmental","order":2,"event":"encounter_opened","authority":"formation_runtime","parents":["D-C-001"],"retention":"inline","payload":{"encounter":"E-C-001","candidate_object":"render-17","derived_from":"atlas","artifact_revision":41,"authority_revision":42,"depends_on_current_authority":true,"commit_action":"publish","refresh_action":"refresh_then_publish"}}
{"contract":"fixture-v0","coordinate":"D-C-003","record":"developmental","order":3,"event":"model_invoked","authority":"formation_runtime","parents":["D-C-002"],"retention":"inline","payload":{"encounter":"E-C-001","invocation":"I-C-001","stub":"blind-commit-v0","cold_invocation":true,"request_binding":"D-C-002","output_authority":"cold_model","output":"publish"}}
{"contract":"fixture-v0","coordinate":"D-C-004","record":"developmental","order":4,"event":"action_committed","authority":"formation_runtime","parents":["D-C-003"],"retention":"inline","payload":{"encounter":"E-C-001","invocation":"I-C-001","action":"A-C-001","action_name":"publish","target":"render-17"}}
{"contract":"fixture-v0","coordinate":"D-C-005","record":"developmental","order":5,"event":"consequence_observed","authority":"environment","parents":["D-C-004"],"retention":"inline","payload":{"encounter":"E-C-001","action":"A-C-001","consequence":"K-C-001","source":"fixture-environment-v0","outcome":"rejected","reason":"stale_dependency","observed_rule":"artifact_revision_must_equal_authority_revision"}}
{"contract":"fixture-v0","coordinate":"D-C-006","record":"developmental","order":6,"event":"experience_closed","authority":"formation_runtime","parents":["D-C-002","D-C-005"],"retention":"inline","payload":{"encounter":"E-C-001","included_events":["D-C-002","D-C-003","D-C-004","D-C-005"],"consequence":"K-C-001","applicability_claim":null}}
```

This literal artifact selects only fixture-local spellings that byte production
requires. It does not require later receipts to use these coordinates, payload
shapes, or JSON Lines.

## Producer and validator

The formation runtime records the six developmental events through its normal
fixture operations. At head `D-C-006`, a fixture-local source adapter reads the
runtime recorder's actual ordered receipts and creates a frozen
`FixturePrefixSource`. This source contains the six receipt envelopes and
payload values represented by the literal artifact. It is not an exchange
format and has no producer outside the runtime fixture path.

The `fixture-v0-prefix-jsonl-v0` materializer consumes that frozen source. Every
emitted value must come from the source; only the JSON field names, punctuation,
and framing are fixed encoder constants. A source mutation must cause the
materializer to refuse or change its output so the fixture validator refuses.
A producer that returns the published literal without reading its source is
nonconforming.

On a clean source, the materializer emits the artifact above once and creates a
`FrozenPrefixHandoff` with:

```text
handoff_id: opaque identity issued by the runtime
run_id: opaque identity of the current runtime fixture run
source_head: D-C-006
materializer: fixture-v0-prefix-jsonl-v0
artifact: immutable byte string
```

Only the runtime materializer may construct this handoff. The harness may
request and witness it. The prefix and fork boundary accepts the typed handoff;
it does not accept raw bytes, a path, or a mapping in its place. A handoff from
another run, a stale or forged handoff, or a handoff with another source head
refuses. This is a trusted local conformance boundary, not cryptographic proof
against malicious implementation code.

The fixture validator checks the artifact before `T-C-002` is recorded. For the
clean fixture, validity means exact equality with the literal artifact above.
This exact check fixes the envelope, payload, order, authority, retention, and
developmental-only boundary without creating a general parser contract.

The validator emits only `valid_fixture_prefix_bytes` or
`invalid_fixture_prefix_bytes`. Mutation names belong to the conformance case,
not to a parser. The validator may not produce, normalize, or repair runtime
bytes.

Validation failure produces no content binding and no fork. The trajectory
closes `invalid` and names the failed fixture clause. The invalid artifact never
enters developmental lineage as a repair or correction.

## Content binding

After semantic validation and the runtime handoff, the harness computes a
`fixture-v0-prefix-identity-v0` binding over the entire artifact byte string as
received. It does not parse, project, sort, normalize, or re-encode the
artifact.

The binding has exactly these fields:

```text
materializer: fixture-v0-prefix-jsonl-v0
identity_contract: fixture-v0-prefix-identity-v0
algorithm: sha-256
digest: 64 lowercase hexadecimal characters
byte_length: exact artifact byte length
```

For the clean artifact above, the binding values are:

```text
materializer: fixture-v0-prefix-jsonl-v0
identity_contract: fixture-v0-prefix-identity-v0
algorithm: sha-256
digest: 1a219122dec8b02544ef5502194da8e9920ebc2aaa7168a8dabb38eae71e4a0d
byte_length: 2303
```

`T-C-002 prefix materialized` retains this binding and witnesses the handoff ID,
run ID, and source head `D-C-006`. Head, event count, coordinate span,
authorities, and causal parents are validator findings. They are not facts
established by the digest.

The algorithm name and contract versions are closed values. Unknown versions,
an absent field, a non-lowercase or non-hexadecimal digest, or a negative or
incorrect byte length refuse before comparison.

## Fork check

The fork operation consumes the current `FrozenPrefixHandoff`, the exact
`T-C-002` receipt that witnessed it, and a claimed binding. It does not accept a
caller-supplied branch artifact. Before recording `T-B-001`, `T-G-001`, or
`T-A-001`, the harness:

1. verifies the typed handoff, current run ID, handoff ID, materializer, and
   source head;
2. verifies that `T-C-002` cites that handoff and source head;
3. requires the complete claimed binding, with no extra or defaulted field, to
   equal the binding retained by `T-C-002`;
4. creates the branch artifact only from the immutable handoff bytes;
5. directly compares the branch bytes with the handoff bytes;
6. verifies the byte length and recomputed SHA-256 value against `T-C-002`; and
7. returns the immutable branch root that later branch execution must use.

The operation checks one captured byte value and passes that same immutable
value forward. It must not check a path and reopen it later. Direct comparison
is the authoritative equality result. SHA-256 is the compact binding retained
in trajectory evidence.

Only then may the harness record the branch assignment, citing `T-C-002`, the
handoff ID, source head, and complete binding. The branch label remains in
trajectory evidence and is not part of the artifact.

## Provenance limit

A byte-identical unauthorized rebuild has the same content identity. Neither a
digest nor direct comparison can detect its author. Provenance therefore
depends on the typed, current-run runtime handoff and a fork interface that does
not accept replacement bytes.

The first conformance tests must exercise both boundaries:

- changed bytes fail the content check; and
- raw clean bytes without a handoff refuse;
- a forged, stale, other-run, or wrong-head handoff refuses;
- a harness-supplied byte-identical replacement refuses at the fork input; and
- branch execution receives the immutable value that the fork operation
  checked, rather than reopening mutable storage.

Passing the second test is an authority result, not a property of SHA-256.

## Refusal vectors

Each mutation starts independently from the clean source, artifact, handoff, or
binding:

- change or omit each identity-bearing source value and require refusal or a
  changed artifact that the validator refuses;
- replace the materializer with a constant producer that ignores its source;
- change one retained value;
- omit, reorder, or duplicate a line;
- use the wrong head, event count, coordinate, authority, parent, or retention
  value;
- add a seventh developmental line;
- add a trajectory receipt, branch label, expected result, or scorer field;
- change whitespace, key order, line endings, or final-line termination;
- use an unknown materializer or identity-contract version;
- omit, default, add, or use the wrong type for a binding field;
- alter the digest or byte length;
- submit a semantically equivalent re-encoding; or
- cite another `T-C-002`, run, handoff, or source head;
- ask the fork boundary to accept raw or harness-supplied replacement bytes;
  or
- mutate or reopen storage after a successful check instead of using the
  returned immutable branch root.

The source adapter and materializer own source-side refusals. Before binding,
the validator owns every artifact difference and reports only
`invalid_fixture_prefix_bytes`. After binding, the identity checker owns direct
byte, binding, and version refusals. The handoff and fork input own provenance
and replacement-source refusals.

## What remains unselected

- a general developmental or trajectory event schema;
- serialization of any event after `D-C-006`;
- replay storage and derived-view syntax;
- per-event digests, hash chains, clocks, timestamps, or authentication;
- cross-implementation byte exchange or migration;
- distributed writers, snapshots, compaction, or a storage engine; and
- any formation mechanism or developmental claim.

## Acceptance and loses-conditions

This contract is sufficient only if two independent readers can reconstruct the
same literal artifact, binding, authority handoff, and refusal ownership.

Grok 4.6 and Composer 2.5 independently reconstructed all seven required
surfaces, recomputed the 2,303-byte artifact and SHA-256 value, found no
remaining authority contradiction, and returned `code_slice_licensed`.

The licensed slice is implemented in [`formation/fixture_prefix.py`](../formation/fixture_prefix.py)
and [`trajectory/fixture_fork.py`](../trajectory/fixture_fork.py). Eleven
deterministic tests cover source changes and omissions, literal-byte mutations,
handoff and witness forgery, post-binding tampering, complete binding checks,
and immutable root use. Post-build review found and closed two caller-created
capability bypasses before both reviewers returned `PASS`.

It loses if a constant producer can pass without consuming runtime receipts, if
a clean fork can pass with different artifact bytes, if validation ignores a
forbidden field, if the harness can replace the runtime artifact, or if a digest
match is reported as proof of byte equality, semantic validity, or provenance.
It also loses if the checked value can change before branch use or if
implementing this fixture forces later records to use JSON Lines or this payload
vocabulary.
