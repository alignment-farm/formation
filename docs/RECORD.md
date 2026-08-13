# Minimal developmental record and lifecycle

Status: **Phase 0 draft specification; schema syntax remains unselected**.

Purpose: define the semantic records needed to replay a practitioner and audit a
trajectory without presuming how skills, dispositions, checks, or working
knowledge are represented.

## Two bound records

Formation uses two records with different readers and authorities.

### Developmental lineage

The formation runtime's append-only history. It contains only runtime-visible
occurrence, interpretation, governance, and activation events. Replay of this
lineage reconstructs practitioner state.

### Trajectory evidence

The harness's append-only experimental record. It contains assignments, hidden
case metadata, fork coordinates, execution receipts, costs, ablations, and
scorer verdicts. It is never replayed into the practitioner.

The records share opaque encounter, invocation, action, consequence, and event
coordinates plus content digests where needed. A join is possible for audit; a
merge is forbidden because it would make harness-only knowledge available to
the runtime.

## Common event envelope

Every event requires:

- a schema version;
- a unique event coordinate;
- a record kind: `developmental` or `trajectory`;
- an event kind and originating authority;
- an append order and prior-event binding within its record;
- a recorded-at time or deterministic logical clock;
- causal-parent coordinates;
- encounter and invocation coordinates when applicable;
- a retention form: inline, referenced, or explicitly redacted; and
- a content digest over the semantically relevant payload.

Wall-clock time is not causal order. Hash linkage can expose mutation relative
to a trusted head but does not authenticate a privileged writer.

## Developmental occurrence events

These record what happened without stating what should be learned:

- **practitioner initialized** — fixed model identity/configuration, base runtime
  interface/configuration, initial lineage head, and supported mechanism
  interfaces, without a branch-specific formation condition;
- **encounter opened** — the runtime-visible situation and observation boundary;
- **model invoked** — exact request or retained reference, cold-invocation
  receipt, and returned output;
- **action committed** — the chosen external action and its causal inputs;
- **consequence observed** — environment or oracle source, observation, and its
  relation to the action; and
- **experience closed** — the encounter coordinates included in the preserved
  experience, without an applicability claim.

A consequence may be missing, delayed, partial, or contested. The record must
represent those states rather than invent closure.

## Interpretation events

An interpretation is versioned and cannot mutate occurrence:

- **candidate proposed** — opaque candidate representation, source-experience
  references, author, claimed applicability, expected effect, and stated
  counterevidence or expiry conditions;
- **candidate trial opened** — when the governing policy requires one, the
  declared policy, evidence available to the trial, and the boundary preventing
  undeclared ordinary influence;
- **candidate trial observed** — runtime-visible trial outcome receipt and
  declared runtime evaluator authority, without harness-only case metadata;
  and
- **candidate withdrawn** — author withdrawal without a claim that the proposal
  was false.

The candidate representation may be natural language, structured policy, code,
an executable check, or another future form. The envelope treats it as retained
content plus declared interfaces.

## Runtime-configuration events

Before a formation condition may affect practice, the runtime records:

- **formation condition bound** — the public mechanism and governance
  configuration assigned to that runtime, excluding branch labels, expected
  results, and other harness-only metadata.

In an experiment, the harness owns the hidden assignment while the runtime owns
the receipt for the public configuration it actually applies. This event is
expected to differ across branches at the declared fork boundary. Outside an
experiment, the same receipt records an operator- or runtime-selected condition
without implying a harness exists.

## Governance events

Governance changes eligibility, not scientific truth:

- **candidate admitted** — candidate version, admission policy, warranting
  runtime-visible evidence, any policy-required trial receipts, scope, and
  initial status;
- **candidate rejected** — candidate version and policy basis;
- **change suspended** — admitted-change version and unresolved or adverse
  evidence preventing activation;
- **change reinstated** — suspension resolution and new warrant;
- **change superseded** — new candidate or admitted version replacing an old
  one while preserving both;
- **change revoked** — terminal ineligibility under the current policy; and
- **change expired** — ineligibility caused by a declared temporal, revision, or
  usage boundary.

Revision creates a new version and supersedes the old one. History is never
edited in place. Rejection and revocation differ: rejection precedes admission;
revocation ends a previously admitted version.

## Activation events

At each governed decision boundary the runtime records:

- **activation considered** — current situation coordinate, eligible admitted
  versions considered by the runtime, and the public activation-policy version;
- **change activated** — selected admitted version, exact materialization or
  intervention digest, and reason expressed only in runtime-visible terms; or
- **activation withheld** — that no change was selected, with a runtime-visible
  refusal class.

The subsequent model invocation and action cite the activation decision.
Presence in a search result or prompt is not enough to claim influence; causal
contribution still requires a harness-side branch or ablation.

Recording non-activation must not require revealing that an encounter belongs
to a hidden negative-transfer family.

## Trajectory-only events

The harness record includes:

- **protocol bound** — exact spec, scorer, budget, stopping rule, and artifact
  versions;
- **prefix materialized** — the common runtime-visible history from which forks
  begin;
- **branch assigned** — baseline or mechanism assignment, hidden from runtime;
- **case assigned** — held-out family and expected-result references;
- **runtime event witnessed** — binding to developmental event coordinates and
  digests;
- **ablation assigned** — exact state element or causal edge removed;
- **cost observed** — tokens, time, tool use, checks, and storage;
- **case scored** — computed case verdict; and
- **trajectory closed** — completion, refusal, invalidation, or stopping-rule
  receipt.

Scientific verdicts exist only here or in derived scorer output. They never
become developmental events automatically.

## Lifecycle

```text
experience closed
  -> candidate proposed
     -> candidate withdrawn
     -> candidate rejected
     -> candidate admitted
     -> trial opened -> trial observed -> candidate rejected or admitted

candidate admitted
  -> activation considered -> activated or withheld
  -> suspended -> reinstated
  -> superseded by a new version
  -> revoked
  -> expired
```

Permitted transitions are policy-versioned. Trial is optional unless the
selected policy requires it; the record vocabulary must not silently make one
governance strategy universal. Unknown states, missing causal parents,
unresolved retained references, and activation of a non-admitted version fail
closed.

## Replay views

Full developmental replay must be sufficient to derive:

- open and closed encounters;
- the formation condition in force after each declared fork;
- unresolved, contested, and delayed consequences;
- candidate versions and source experiences;
- admitted, suspended, superseded, revoked, and expired versions;
- current eligibility at a specified lineage head;
- activation and withholding history; and
- unresolved dependencies caused by redaction or ablation.

The first build may cache these views, but caches have no independent authority.
Trajectory replay separately derives assignments and verdicts and may join to,
but never alter, developmental views.

## Causal ablation

An ablation is a trajectory assignment, not a mutation of retained history. It
creates a fork whose runtime view excludes a declared experience, candidate,
admitted version, activation, or causal edge.

Dependent state must either disappear transitively or become explicitly
unresolved. An ablation must not silently repair the branch, alter its
foreground situation, or expose why the element was removed.

## Conformance requirements

A deterministic implementation must refuse:

- interpretation payloads presented as occurrence;
- a formation-condition receipt containing a branch label, expected result, or
  hidden case-family field;
- a model output presented as an external consequence;
- admission without a candidate version, source lineage, policy, warrant, or a
  trial receipt required by that policy;
- activation before admission or while suspended, superseded, revoked, or
  expired;
- in-place candidate revision;
- harness-only fields in developmental payloads;
- scorer verdicts used as governance events;
- causal references to future or nonexistent events;
- replay from a broken record binding; and
- an ablation that leaves silently valid-looking dependent state.

## Loses-condition

This contract loses if it forces an unearned ontology of skill, cannot represent
ambiguous or absent consequences, or cannot keep scientific verdicts outside
practitioner state. It also loses if two conforming implementations cannot
exchange a deterministic fixture because the semantic event requirements are
too vague.
