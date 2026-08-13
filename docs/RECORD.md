# Minimal developmental record and lifecycle

Status: **Phase 0 draft specification; schema syntax remains unselected**.

Purpose: define the semantic records needed to replay a practitioner and audit a
trajectory without presuming how skills, dispositions, checks, or working
knowledge are represented.

The event names below are shared semantic vocabulary, not a requirement that
every runtime implement one universal lifecycle. A mechanism emits only the
events its declared policy can produce. A fixture or mechanism specification
must name the subset it requires before an implementation is judged against
those transitions.

## Two bound records

Formation uses two records with different readers and authorities.

### Developmental lineage

The formation runtime's append-only history. It contains only runtime-visible
occurrence, interpretation, configuration, governance, and activation events.
Replay of this lineage reconstructs practitioner state.

### Trajectory evidence

The harness's append-only experimental record. It contains assignments, hidden
case metadata, fork coordinates, execution receipts, costs, ablations, and
scorer verdicts. It is never replayed into the practitioner.

The records share opaque encounter, invocation, action, consequence, and event
coordinates plus content-identity bindings where an audit comparison requires
them. A join is possible for audit; a merge is forbidden because it would make
harness-only knowledge available to the runtime.

## Common semantic receipt

Every event requires:

- a contract version identifying the event semantics;
- a unique event coordinate;
- a record kind: `developmental` or `trajectory`;
- an event kind and originating authority;
- deterministic order within its record;
- causal-parent coordinates;
- encounter and invocation coordinates when applicable;
- a retention form: inline, referenced, or explicitly redacted; and
- retained content or an explicit reason it is unavailable.

When a claim depends on equality across records or branches, the receipt also
needs a content-identity binding sufficient for that claim. The binding may be
exact retained bytes or a digest once serialization and digest scope are
selected. Timestamps, logical clocks, prior-event integrity bindings, and hash
linkage may support audit or storage, but are not semantic requirements of every
event. Wall-clock time is not causal order, and hash linkage would expose
mutation only relative to a trusted head; it would not authenticate a
privileged writer.

### Packet-review disposition

The load-bearing envelope requirements are semantic identity, authority,
deterministic record order, causal references, and explicit retention. They let
an audit distinguish what happened, who supplied it, and what later state may
depend on it.

Schema syntax, timestamps, clocks, hash chains, per-event digests, and
prior-event integrity bindings are possible instruments rather than properties
of development. They remain unselected until a materializer or storage threat
requires them. An integrity mechanism may expose mutation; it cannot establish
that an originating authority was entitled or truthful.

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
- **replay constraint bound** — a public exclusion or redaction constraint that
  the runtime will apply during its own replay, naming the target and policy but
  excluding a hidden assignment reason or expected effect.

These are the runtime-configuration receipts required by the first fixture,
not an exhaustive configuration vocabulary. A later ablation mechanism must
name its public receipt semantics before its records can claim conformance.

In an experiment, the harness owns the hidden assignment while the runtime owns
the receipt for the public configuration it actually applies. A `formation
condition bound` event is expected to differ across branches at the declared
fork boundary. A replay constraint is bound at the lineage point where its
policy applies; in an ablation of an admitted change, that point follows the
dependent admission. Outside an experiment, the same receipt categories record
operator- or runtime-selected configuration without implying a harness exists.

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
  intervention identity, and reason expressed only in runtime-visible terms; or
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
  content identity;
- **ablation assigned** — target state element or causal edge, public exclusion
  or prevention condition, and harness-only assignment reason and
  expected-effect reference;
- **cost observed** — tokens, time, tool use, checks, and storage;
- **case scored** — computed case verdict; and
- **trajectory closed** — completion, refusal, invalidation, or stopping-rule
  receipt.

Scientific verdicts exist only here or in derived scorer output. They never
become developmental events automatically.

## Policy-transition vocabulary

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

The first deterministic fixture requires occurrence and configuration receipts,
proposal, direct admission, activation or withholding, suspension, revocation,
and replay constraint. It does not require trial, withdrawal, rejection,
reinstatement, supersession, or expiry support. Listing those transitions here
fixes their meanings if selected later; it does not put them in the first build.

## Replay views

Full developmental replay must be sufficient to derive:

- open and closed encounters;
- the formation condition in force after each declared fork;
- replay constraints in force at the selected lineage head;
- unresolved, contested, and delayed consequences;
- candidate versions and source experiences;
- admitted, suspended, superseded, revoked, and expired versions;
- current eligibility at a specified lineage head;
- activation and withholding history; and
- unresolved dependencies caused by redaction or replay exclusion.

The first build may cache these views, but caches have no independent authority.
Trajectory replay separately derives assignments and verdicts and may join to,
but never alter, developmental views.

## Causal ablation

An ablation is a trajectory assignment, not a scientific verdict or a mutation
of retained history. It prevents a named contributor from affecting the branch
at a frozen boundary through a declared runtime-visible condition. The harness
records the assignment and gives the runtime only the public target and
condition; the runtime records and applies that condition using the mechanism's
declared semantics.

The first fixture uses a replay constraint to exclude lineage-derived state.
For that subtype, the runtime derives its own constrained view and dependent
state must either disappear transitively or become explicitly unresolved. A
different ablation mechanism, such as preventing one activation at a decision
boundary, must specify its runtime-configuration receipt and dependency
semantics before use. No ablation may silently repair the branch, alter its
foreground situation, expose why the element was targeted, or arrive as an
already-derived practitioner view.

Unavailable or unresolved state under a replay constraint is a property of the
derived view, not a governance transition. Applying the constraint emits no
`change suspended`, `change revoked`, or `change expired` receipt.

## Conformance requirements

A deterministic implementation must refuse:

- interpretation payloads presented as occurrence;
- a formation-condition receipt containing a branch label, expected result, or
  hidden case-family field;
- a replay-constraint receipt containing a branch label, hidden ablation reason,
  or expected effect;
- a model output presented as an external consequence;
- admission without a candidate version, source lineage, policy, warrant, or a
  trial receipt required by that policy;
- activation before admission or while in any policy-declared ineligible state,
  including suspended, superseded, revoked, or expired;
- in-place candidate revision;
- harness-only fields in developmental payloads;
- scorer verdicts used as governance events;
- causal references to future or nonexistent events;
- replay from broken declared ordering, causal, or retention bindings, or from
  a broken integrity binding when one is declared; and
- a replay exclusion that leaves silently valid-looking dependent state.

## Loses-condition

This contract loses if it forces an unearned ontology of skill, cannot represent
ambiguous or absent consequences, or cannot keep scientific verdicts outside
practitioner state. It also loses if two conforming implementations cannot
exchange a deterministic fixture because the semantic event requirements are
too vague.
