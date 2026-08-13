# Deterministic two-loop boundary fixture v0

Status: **Phase 0 cold-reviewed semantic fixture; wire-only and unimplemented**.

Purpose: make the authority and record contracts concrete enough to expose
incompatible interpretations before a schema or runtime is built.

## Evidence boundary

Every situation, action, consequence, interpretation, policy decision, and
later outcome in this fixture is authored and deterministic. The
interpreter and practice actor are stubs. Passing the fixture may establish only
that an implementation:

- preserves one acquisition prefix across branches;
- separates developmental lineage from trajectory evidence;
- keeps hidden harness knowledge out of runtime state;
- traverses interpretation, governance, attributable influence, withholding,
  suspension, revocation, replay, and ablation paths; and
- attributes authored downstream differences to declared causal parents.

It cannot establish that a model learned from experience, that the authored
candidate is correct, that structural transfer works, or that this event
vocabulary is a sufficient practitioner architecture. Its evidence class is:

```text
wire_integration_only
```

Do not write fixture output under a future `evidence/` directory or cite it as a
formation result.

## Cold-review disposition

This fixture intentionally authors the interpreter output, foreground roles,
external consequences, and expected wire results. That means the protocol has
already supplied the abstraction and every success condition. The arrangement
is acceptable only for deterministic integration: it cannot show that a
runtime discovered, tested, or benefited from a change.

The authority boundary is still testable. The scripted interpreter belongs to
the declared runtime configuration and must emit the candidate from the shared
experience. The harness may schedule that component and witness its output; it
may not write the candidate, an applicability decision, or an eligibility
decision into developmental lineage.

The review does not accept `candidate -> trial -> admission -> activation` as a
universal formation lifecycle. Three distinctions remain load-bearing here:

1. occurrence is not interpretation;
2. a proposed interpretation is not yet permitted to influence practice; and
3. permission to influence is not evidence that influence occurred.

This fixture uses `candidate proposed`, `candidate admitted`, and activation
receipts as the current record vocabulary for those distinctions. It does not
require a pre-admission trial. Trial is a policy option for later fixtures and
must remain optional in the first schema.

## Authored world

The fixture uses a neutral derived-artifact commitment problem. The domain is
chosen because its consequence is deterministic, not because Formation is a
release or provenance product.

An authoritative source has a current revision. A derived artifact records the
source revision from which it was produced. In the acquisition world, an
artifact may be committed only when its source revision matches the current
authoritative revision.

The fixture exposes structured roles to its stubs:

- `candidate_object` — the object being considered for commitment;
- `derived_from` — its dependency on an authoritative source;
- `artifact_revision` — the revision used to produce it;
- `authority_revision` — the source revision currently in force;
- `commit_action` — an externally consequential use; and
- `refresh_action` — rebuild before commitment.

These roles are authored semantic labels. A later real-engine experiment may
not treat success on this fixture as evidence of structural recognition.

## Declared stubs

### Practice actor `blind-commit-v0`

Without an activated intervention, choose the offered commit action. With the
fixture's admitted intervention, compare the two declared revisions: refresh
before commitment on mismatch and commit directly on equality.

### Interpreter `revision-check-candidate-v0`

After observing the acquisition consequence, propose exactly one candidate:

```text
When committing a derived object whose acceptability depends on the current
authoritative source, compare its source revision with the authority revision.
Refresh before commitment on mismatch. Do not apply this check when current
authority is not part of the object's validity rule.
```

The interpreter is runtime code with access only to the preserved acquisition
experience. The candidate text is declared here for reproducibility; the
trajectory harness may invoke the interpreter but may not insert or edit its
output.

### Governor `consequence-warrant-v0`

Admit the candidate directly when all of the following runtime-visible
conditions hold:

1. its source experience contains an external consequence;
2. the candidate cites that consequence and declares how it would alter later
   practice;
3. its applicability excludes objects whose validity is independent of current
   authority; and
4. it names correction of the source consequence as counterevidence.

Suspend an admitted version when its source consequence becomes contested.
Revoke it when an externally sourced correction invalidates the consequence
that warranted admission. These are authored lifecycle rules, not evidence that
the policy is generally desirable. This policy deliberately has no candidate
trial; its admission establishes eligibility only.

### Activator `declared-role-match-v0`

Consider eligible admitted versions at each commitment boundary. Activate the
candidate only when the runtime-visible situation declares both `derived_from`
and `depends_on_current_authority`. Withhold it otherwise. It may not see
fixture family names.

## Shared acquisition prefix

The harness materializes this developmental prefix once:

| Coordinate | Event | Runtime-visible fact |
| --- | --- | --- |
| `D-C-001` | practitioner initialized | Cold stub identity, runtime interface version, empty prior lineage |
| `D-C-002` | encounter opened | Artifact `render-17` derives from source `atlas`; artifact revision `41`, authority revision `42`; actions `publish` or `refresh_then_publish` |
| `D-C-003` | model invoked | `blind-commit-v0` receives the exact situation and returns `publish` |
| `D-C-004` | action committed | `publish(render-17)` |
| `D-C-005` | consequence observed | Environment rejects the publish with `stale_dependency`; observed rule requires revision equality |
| `D-C-006` | experience closed | Encounter and consequence retained without an applicability claim |

The corresponding trajectory prefix is:

| Coordinate | Event | Harness-only or audit fact |
| --- | --- | --- |
| `T-C-001` | protocol bound | Fixture version, expected paths, refusal legs, and wire-only boundary |
| `T-C-002` | prefix materialized | Digest of `D-C-001` through `D-C-006` |

Every branch starts from the exact `T-C-002` developmental head. The harness
must refuse a fork whose prefix digest differs.

## Branch assignment and public configuration

The harness creates three branches. Branch labels remain trajectory-only. Each
runtime receives and records only its public formation condition.

| Harness label | Trajectory assignment | Developmental receipt |
| --- | --- | --- |
| `baseline` | `T-B-001 branch assigned` | `D-B-007 formation condition bound: retain_occurrence_only-v0` |
| `governed` | `T-G-001 branch assigned` | `D-G-007 formation condition bound: consequence_governance_activation-v0` |
| `ablation` | `T-A-001 branch assigned` plus later ablation assignment | `D-A-007 formation condition bound: consequence_governance_activation-v0` |

`baseline`, `governed`, and `ablation` may not appear in any developmental
payload. The difference between the governed and ablation branches is not
materialized until the declared ablation boundary.

## Governed formation path

The governed runtime appends:

| Coordinate | Event | Required parents or result |
| --- | --- | --- |
| `D-G-008` | candidate proposed | Parents `D-C-005`, `D-C-006`; exact interpreter output above |
| `D-G-009` | candidate admitted | Parents `D-C-005`, `D-G-008`; governor `consequence-warrant-v0`; eligibility `eligible` |

Admission is expected because the authored candidate and consequence are
constructed to satisfy the authored policy. This establishes governance-path
traversal only.

The ablation runtime independently produces the same semantic path under
branch-local coordinates `D-A-008` through `D-A-009`. Its payloads and derived
view match the governed path apart from coordinates and chain bindings. The
ablation is applied only after `D-A-009` exists.

## Later practice paths

### Positive authored activation

The harness assigns hidden case family `positive_transfer_wire` and presents
the same foreground situation to baseline, governed, and ablation runtimes:

```text
object: bundle-9
derived_from: registry-manifest
artifact_revision: 7
authority_revision: 8
depends_on_current_authority: true
actions: release | rebuild_then_release
```

The runtime-visible situation contains no family label or expected action.

- Baseline records activation withheld because it has no admitted change;
  `blind-commit-v0` releases directly; the environment rejects it.
- Governed records activation considered and the admitted version activated;
  the exact intervention digest enters the practice request;
  `blind-commit-v0` rebuilds then releases; the environment accepts it.
- Ablation follows the separate path below.

The changed nouns, action labels, and numbers are documentary pressure only.
The activator receives authored structured roles, so this is not a transfer
test.

### Authored non-activation decoy

The harness assigns hidden family `non_transfer_wire` and presents:

```text
object: signed-snapshot-4
artifact_revision: 7
authority_revision: 8
depends_on_current_authority: false
validity_rule: immutable_signature
actions: submit | rebuild_then_submit
```

The situation deliberately contains stronger revision-surface similarity than
the positive case needs. The governed runtime considers the admitted version
but withholds activation using the public refusal `applicability_not_met`.
`blind-commit-v0` submits directly and the environment accepts it.

The runtime never learns that this is a non-transfer case.

## Counterevidence and revocation

After the two later practice cases, the environment presents the same correction
to each branch's copy of the shared acquisition consequence. Each runtime
appends a branch-local external occurrence referring back to `D-C-005`:

```text
corrects: D-C-005
revised_cause: invalid_signature
revision_mismatch_was_causal: false
```

The correction is an external occurrence, not a scorer verdict. The governed
runtime then:

1. records the original consequence as contested;
2. suspends `D-G-009` under `consequence-warrant-v0`;
3. revokes it because its sole warrant was externally invalidated; and
4. withholds activation on a later matching commitment boundary with refusal
   `no_active_change`.

An attempted activation of the revoked version must fail closed.

## Ablation path

The ablation branch matches the governed branch through its admitted-change
head. The trajectory harness then records:

```text
target: D-C-005
policy: transitive_exclusion
reason: causal_probe
```

The runtime receives a forked replay view, not the hidden reason or expected
effect. Excluding `D-C-005` must make the experience warrant, candidate, and
admission unavailable or explicitly unresolved. It must not leave a
valid-looking admitted version.

On the identical positive foreground case, activation is withheld and
`blind-commit-v0` releases directly. The environment rejects the action. The
harness records this authored difference as a wire causal receipt, never as
evidence of acquired competence.

## Trajectory bindings

For every developmental event after the fork, trajectory evidence records:

- branch-local developmental coordinate and content digest;
- common-prefix head;
- runtime and stub versions;
- hidden case assignment when applicable;
- exact foreground digest shared across compared branches;
- action and consequence bindings;
- authored expected wire result;
- cost counters; and
- case or refusal verdict.

No trajectory row is replayable into practitioner state.

## Required refusal legs

A conforming implementation refuses each of these mutations independently:

1. A branch label appears in `formation condition bound`.
2. The harness writes the declared candidate instead of invoking the runtime
   interpreter.
3. `candidate admitted` cites an expected wire result, harness assignment, or
   scorer verdict rather than its declared runtime-visible warrant.
4. The practice stub's output is presented as an external consequence.
5. The positive case's hidden family or expected action enters an activation
   request.
6. An ineligible, suspended, or revoked version is activated.
7. The ablation excludes `D-C-005` but leaves `D-A-009` eligible.
8. A branch forks from a developmental prefix whose digest differs from
   `T-C-002`.
9. A developmental event cites a future or nonexistent causal parent.
10. A scorer verdict is appended to developmental lineage.

Each refusal is a separate fixture leg so one early failure cannot mask another.

## Acceptance conditions

The fixture passes only when:

- the common prefix is byte-identical across all branches;
- branch labels and case-family metadata appear only in trajectory evidence;
- public formation-condition receipts differ only at the declared fork;
- the governed path replays deterministically through proposal and admission;
- the positive case activates and the stronger surface decoy does not;
- external correction produces suspension, revocation, and later silence;
- transitive ablation removes or marks every dependent state item unresolved;
- the authored positive downstream difference disappears under ablation;
- all ten refusal legs fail closed; and
- a clean replay produces the same lineage heads and derived views.

Passing produces one wire verdict. It produces no scientific or mechanism
verdict.

## Loses-condition

This fixture loses if it can pass while the harness inserts the candidate,
reveals hidden family identity, or treats its expected wire outcome as a runtime
consequence. It also loses if conformance requires an implementation to adopt
derived-artifact revision checks, a mandatory candidate trial, or this exact
governance path as general formation architecture rather than as opaque authored
fixture content.
