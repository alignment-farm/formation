# Deterministic two-loop boundary fixture v0

Status: **Phase 0 cold-reviewed semantic fixture; fixture-local prefix byte
boundary implemented and independently reviewed; remaining paths wire-only**.

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
experience. The harness may schedule a runtime formation opportunity and
witness its output; it may not write the candidate, an applicability decision,
or an eligibility decision into developmental lineage.

The review does not accept `candidate -> trial -> admission -> activation` as a
universal formation lifecycle. Three distinctions remain load-bearing here:

1. occurrence is not interpretation;
2. a proposed interpretation is not yet permitted to influence practice; and
3. permission to influence is not evidence that influence occurred.

This fixture uses `candidate proposed`, `candidate admitted`, and activation
receipts as the current record vocabulary for those distinctions. It does not
require a pre-admission trial. Trial is a policy option for later fixtures and
must remain optional in the first materialization contract.

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

In each authored foreground below, `commit_action` names the direct external
use and `refresh_action` names the corrective action followed by that use. The
stubs receive those bindings explicitly; list position or action spelling is not
an implicit classifier.

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
authority is not part of the object's validity rule. Treat an externally sourced
correction showing that revision mismatch was not causal as counterevidence.
```

The interpreter is runtime code with access only to the preserved acquisition
experience. The candidate text is declared here for reproducibility; the
trajectory harness may schedule formation processing only through the runtime
boundary. The runtime invokes the interpreter and originates its output. Shared
process hosting does not permit the harness role to author, insert, or edit that
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

When it activates the admitted candidate, the runtime materializes intervention
`revision-check-intervention-v0`, bound to that admitted version and containing
the exact candidate text above. The intervention identity and admitted-version
binding enter the model request; the harness does not construct either.

## Protocol bounds

The human protocol owner freezes these bounds before materialization:

- model contact budget: zero; every inference seat is a declared deterministic
  stub;
- semantic contract version: `fixture-v0`; all authored fixture content needed
  for a clean or refusal decision is retained inline, with no redacted or
  unresolved source reference before ablation;
- clean execution: one shared acquisition, three branch schedules, the positive
  comparison, one governed decoy, one correction per branch, and one governed
  post-revocation boundary;
- refusal execution: sixteen independent legs, each starting from its named
  clean precondition and applying only its named mutation;
- retries: none for a semantic mismatch; an infrastructure interruption does
  not resume, and a new run starts from the shared acquisition prefix;
- stopping: close successfully after the clean execution and all refusal legs
  produce their required receipts, or close invalid on the first boundary leak,
  prefix mismatch, broken causal reference, or non-deterministic replay; and
- output: one trajectory-only conformance verdict, `wire_integration_only` or
  `invalid`, plus counts of practitioner-model contacts, deterministic stub
  invocations by role, developmental and trajectory receipts, and refusal
  checks. Wall time and storage may be retained but do not affect fixture
  conformance.

These bounds make fixture completion deterministic. They do not license a
scientific verdict or prescribe budgets for later model-contact experiments.

## Shared acquisition prefix

The harness materializes this developmental prefix once:

| Coordinate | Event | Runtime-visible fact |
| --- | --- | --- |
| `D-C-001` | practitioner initialized | No developmental parent; cold stub identity, runtime interface version, empty prior lineage |
| `D-C-002` | encounter opened | Parent `D-C-001`; artifact `render-17` derives from source `atlas`; artifact revision `41`, authority revision `42`; `depends_on_current_authority: true`; `commit_action: publish`; `refresh_action: refresh_then_publish` |
| `D-C-003` | model invoked | Parent `D-C-002`; `blind-commit-v0` receives the exact situation and returns `publish` |
| `D-C-004` | action committed | Parent `D-C-003`; `publish(render-17)` |
| `D-C-005` | consequence observed | Parent `D-C-004`; environment rejects the publish with `stale_dependency`; observed rule requires revision equality |
| `D-C-006` | experience closed | Parents `D-C-002`, `D-C-005`; encounter and consequence retained without an applicability claim |

The corresponding trajectory prefix is:

| Coordinate | Event | Harness-only or audit fact |
| --- | --- | --- |
| `T-C-001` | protocol bound | First fixture receipt; protocol bounds above, fixture and stub versions, expected paths, refusal legs, scorer rubric, and wire-only boundary |
| `T-C-002` | prefix materialized | After `D-C-006`; trajectory parent `T-C-001`; content-identity binding over `D-C-001` through `D-C-006` |

Every branch starts from developmental head `D-C-006`, whose retained prefix is
bound by `T-C-002`. The harness must refuse a fork whose prefix identity
differs. The exact draft artifact and check are defined by the [first
materialization contract](MATERIALIZATION.md); they do not apply to later
receipts.

## Branch assignment and public configuration

The harness creates three branches. Branch labels remain trajectory-only. Each
runtime receives and records only its public formation condition.

| Harness label | Trajectory assignment | Developmental receipt |
| --- | --- | --- |
| `baseline` | `T-B-001 branch assigned` | `D-B-007 formation condition bound: audit_lineage_only-v0` |
| `governed` | `T-G-001 branch assigned` | `D-G-007 formation condition bound: consequence_governance_activation-v0` |
| `ablation` | `T-A-001 branch assigned` plus later ablation assignment | `D-A-007 formation condition bound: consequence_governance_activation-v0` |

`baseline`, `governed`, and `ablation` may not appear in any developmental
payload. The difference between the governed and ablation branches is not
materialized until the declared ablation boundary.

`T-A-001` contains the branch assignment only. The later `ablation assigned`
receipt is a distinct trajectory event created at schedule step 4; its public
target and policy do not appear early in `T-A-001`.

Each branch-local formation-condition receipt cites `D-C-006` as its causal
parent.

`audit_lineage_only-v0` preserves the shared occurrence for audit but makes no
experience-derived material available to later practice. Each public formation
condition names its interpreter, governor, and influence-policy identities when
it has them; those branch-specific procedure identities do not appear in the
shared `D-C-001` receipt.

The baseline condition has no interpreter or governor. It does name
`declared-role-match-v0` as its influence policy; that policy operates over an
empty eligible set and therefore emits `no_admitted_change`. This does not make
the retained acquisition available to baseline practice.

## Required semantic schedule

This order is part of the fixture. It fixes causal precedence and comparison
membership without fixing serialization, process order between independent
branches, or coordinates for every later receipt.

1. The protocol is bound and the acquisition prefix `D-C-001` through
   `D-C-006` is materialized once.
2. All three branches fork from developmental head `D-C-006` as bound by
   `T-C-002`, then record their public formation condition.
3. Governed and ablation independently produce their branch-local proposal and
   admission paths. Baseline performs no interpretation or governance step.
4. After `D-A-009` exists and before any later ablation-branch practice, the
   harness assigns the ablation. The ablation runtime records `D-A-010` and
   derives its constrained view.
5. The positive foreground is materialized once and presented to baseline,
   governed, and ablation. Their executions may occur in any order; all three
   bind the same foreground content.
6. The non-activation decoy is presented to governed only. It tests the
   fixture's authored applicability path, not a cross-branch contrast.
7. After the positive comparison and governed decoy are complete, the same
   environment-authored correction is presented to all three branches.
8. Governed applies its declared suspension and revocation policy, then receives
   one later matching commitment boundary to demonstrate post-revocation
   silence. Baseline and ablation emit no governance transition from the
   correction.
9. The scorer operates only after all required developmental histories and
   trajectory receipts are complete.

The branches need not advance in lockstep outside the shared positive
comparison. The numbered phases are nevertheless global semantic precedence:
every receipt in an earlier phase that a later phase requires exists first.
Within each developmental or trajectory record, deterministic order preserves
that precedence; cross-record bindings and causal references make the handoffs
auditable. In particular, `D-A-010` exists before any branch receives the shared
positive presentation. Applying the ablation before `D-A-009` or after the
positive case constructs a different causal question.

The public refusal classes used by this fixture are authored tokens, not a
universal enumeration:

| Situation | Refusal class |
| --- | --- |
| Baseline positive case, with no admitted change | `no_admitted_change` |
| Governed decoy, where applicability is false | `applicability_not_met` |
| Ablation positive case, where the warrant path is unresolved | `unresolved_dependency` |
| Governed post-revocation case, with no active change | `no_active_change` |

## Instrument handoff audit

The fixture uses the instrument surfaces in [INSTRUMENTS.md](INSTRUMENTS.md).
This table describes logical handoffs, not required processes or APIs.

| Phase | External arrangement | Runtime receives | Runtime must do | Must remain outside runtime | Required receipt |
| --- | --- | --- | --- | --- | --- |
| Protocol binding | Human owner freezes the fixture; harness binds it | Public runtime interface and supported mechanism identifiers | Record its base configuration | Expected paths, scorer keys, budget, and wire verdict | `T-C-001 protocol bound` and `D-C-001 practitioner initialized` |
| Acquisition | Harness presents one authored situation and schedules the environment | Foreground situation, model output, committed action, external consequence | Conduct practice and preserve the experience without an applicability claim | Future branches, cases, and expected effects | `D-C-002` through `D-C-006`, witnessed by trajectory bindings |
| Fork and condition | Fork the one retained prefix and assign a condition | Public formation condition only | Record the condition it will apply | Branch label and cross-branch comparison | `T-*-001 branch assigned` plus branch-local `D-*-007 formation condition bound` |
| Formation opportunity | Schedule runtime processing at `D-C-006` | Preserved experience and public mechanism configuration | Invoke its interpreter and governor; author proposal and eligibility receipts | Expected candidate and whether the authored path should pass | `D-G-008` and `D-G-009`, with trajectory content-identity witnesses |
| Later practice | Present content-identical foregrounds under one environment rule | Foreground fields only | Decide influence, construct the practice request, commit the action, and record consequence | Case family, expected action, and cross-branch result | Activation or withholding, invocation, action, and consequence receipts |
| Correction | Harness schedules the same environment-authored correction for every branch | Correction and its source binding | Contest the warrant and apply declared governance | Expected suspension and revocation path | Correction, suspension, revocation, and later withholding receipts |
| Ablation | Assign a target and public ablation condition, here an exclusion policy | Target `D-C-005` and `transitive_exclusion` only | Record the replay constraint and derive the constrained view itself | Branch label, `causal_probe` reason, and expected downstream effect | Trajectory assignment plus `D-A-010 replay constraint bound` |
| Scoring | Harness joins witnessed receipts; scorer applies the authored wire rubric | Nothing | Nothing | Costs, case verdicts, aggregate comparison, and wire verdict | Trajectory-only score and close receipts |

The handoff loses if scheduling a runtime operation gives the harness authority
to author its result. Knowing the scripted expected output permits the harness
to score the wire; it does not permit the harness to append that output or a
derived practitioner view.

### Handoff-audit result

The first Markdown pass exposed two authority collapses in the prose:

1. the ablation path let the harness supply a derived practitioner view; and
2. the initial handoff table described protocol freezing, environment action,
   and scoring as undifferentiated harness work.

Both are resolved above by preserving logical authority and making the runtime
apply its own public replay constraint. The review result is:

```text
markdown_sufficient
```

No remaining disagreement in this handoff pass required machine syntax. A later
contact with the fork operation did: prose cannot compute whether three branch
roots contain the same materialized prefix. The resulting fixture-local
contract is isolated in [MATERIALIZATION.md](MATERIALIZATION.md); two independent
model families reconstructed it and licensed only its narrow implementation
slice.

## Governed formation path

The governed runtime appends:

| Coordinate | Event | Required parents or result |
| --- | --- | --- |
| `D-G-008` | candidate proposed | Parents `D-C-005`, `D-C-006`, `D-G-007`; exact interpreter output above |
| `D-G-009` | candidate admitted | Parents `D-C-005`, `D-G-007`, `D-G-008`; governor `consequence-warrant-v0`; initial status `eligible` |

Admission is expected because the authored candidate and consequence are
constructed to satisfy the authored policy. This establishes governance-path
traversal only.

The ablation runtime independently produces the same semantic path under
branch-local coordinates `D-A-008` through `D-A-009`. Its payloads and derived
view match the governed path apart from coordinates and any implementation-level
integrity bindings. `D-A-008` has parents `D-C-005`, `D-C-006`, and `D-A-007`;
`D-A-009` has parents `D-C-005`, `D-A-007`, and `D-A-008`. The ablation is
applied only after `D-A-009` exists.

## Later practice paths

Every commitment-boundary presentation below is a complete practice encounter.
The runtime records `encounter opened`, `activation considered`, exactly one of
`change activated` or `activation withheld`, `model invoked`, `action committed`,
`consequence observed`, and `experience closed` in that causal order. The prose
below names the branch-specific activation, action, and consequence rather than
repeating that common receipt sequence. The later external correction is not a
practice encounter; its smaller receipt path is specified separately.

Each `activation considered` cites the public formation condition in force and
the current encounter. In the ablation branch it also cites `D-A-010`. The model
invocation cites the selected activation or withholding receipt, so an
intervention cannot enter a practice request without an attributable influence
decision.

The eligible set in `activation considered` contains `D-G-009` only for the
clean governed positive and decoy encounters. It is empty for baseline, for the
constrained ablation view, and after governed revocation. The shared acquisition
precedes any formation condition and therefore has no activation receipt.

For every hidden practice case or correction presentation, trajectory evidence
records `case assigned` before presentation. Runtime and environment receipts
may be witnessed as they occur, but the scorer emits every `case scored` receipt
only after all clean and refusal executions are complete. Cost receipts and
final `trajectory closed` remain trajectory-only and follow the case scores.

### Positive authored activation

The harness assigns hidden case family `positive_transfer_wire` and presents
the same foreground situation to baseline, governed, and ablation runtimes:

```text
candidate_object: bundle-9
derived_from: registry-manifest
artifact_revision: 7
authority_revision: 8
depends_on_current_authority: true
commit_action: release
refresh_action: rebuild_then_release
```

The runtime-visible situation contains no family label or expected action.

- Baseline records activation withheld because it has no admitted change;
  its refusal is `no_admitted_change`; `blind-commit-v0` releases directly; the
  environment rejects it.
- Governed records activation considered and the admitted version activated;
  `revision-check-intervention-v0` and its `D-G-009` binding enter the practice
  request;
  `blind-commit-v0` rebuilds then releases; the environment accepts it.
- Ablation follows the separate path below.

The changed nouns, action labels, and numbers are documentary pressure only.
The activator receives authored structured roles, so this is not a transfer
test.

### Authored non-activation decoy

The harness assigns hidden family `non_transfer_wire` and presents:

```text
candidate_object: signed-snapshot-4
derived_from: signing-key
artifact_revision: 7
authority_revision: 8
depends_on_current_authority: false
validity_rule: immutable_signature
commit_action: submit
refresh_action: rebuild_then_submit
```

The situation deliberately contains stronger revision-surface similarity than
the positive case needs. It supplies `derived_from`, so the declared false
`depends_on_current_authority` value is the operative applicability failure.
The governed runtime considers the admitted version but withholds activation
using the public refusal `applicability_not_met`.
`blind-commit-v0` submits directly and the environment accepts it.

The runtime never learns that this is a non-transfer case.

## Counterevidence and revocation

After the positive comparison and governed decoy, the environment presents the
same correction to each branch's copy of the shared acquisition consequence.
Each runtime appends a branch-local external occurrence referring back to
`D-C-005`:

```text
corrects: D-C-005
revised_cause: invalid_signature
revision_mismatch_was_causal: false
```

The correction presentation is not a practice encounter and does not invoke the
model or commit a new action. After its trajectory `case assigned` receipt, the
environment originates one new branch-local `consequence observed` receipt.
That receipt cites `D-C-004` and `D-C-005`, and is neither a scorer verdict nor
an edit to `D-C-005`. Replay leaves `D-C-005` immutable and derives its contested
status from the correction. The harness-only correction family is
`correction_wire`. Contested status is a replay view, not another developmental
event. The governed runtime then:

1. derives the original consequence as contested;
2. suspends `D-G-009` under `consequence-warrant-v0`;
3. revokes it because its sole warrant was externally invalidated; and
4. withholds activation on a later matching commitment boundary with refusal
   `no_active_change`.

The suspension receipt has parents `D-G-009` and the governed correction
receipt. The revocation receipt has parents `D-G-009`, the suspension receipt,
and the governed correction receipt.

An attempted activation of the revoked version must fail closed.

The clean post-revocation encounter demonstrates withholding. Refusal leg 9 is
a separate mutation from the same clean head that attempts activation and must
be rejected; the clean withholding does not substitute for that refusal test.

The governed post-revocation boundary presents this authored foreground:

```text
candidate_object: package-12
derived_from: release-index
artifact_revision: 18
authority_revision: 19
depends_on_current_authority: true
commit_action: publish
refresh_action: regenerate_then_publish
```

The runtime considers the matching situation but withholds activation using
`no_active_change`; `blind-commit-v0` publishes directly and the environment
rejects it. The harness-only case family is `post_revocation_wire`; its expected
action remains harness-only.

Baseline records the correction and derives the original consequence as
contested, but has no candidate or admitted change to govern. Ablation also
retains the correction occurrence. Under its replay constraint, the correction's
binding to excluded `D-C-005` is unavailable or explicitly unresolved; this
produces no suspension, revocation, or expiry receipt.

## Ablation path

The ablation branch matches the governed branch through its admitted-change
head. The trajectory harness then records:

```text
target: D-C-005
policy: transitive_exclusion
reason: causal_probe
```

The harness delivers only the public target and policy. The runtime appends:

```text
D-A-010 replay constraint bound
parents: D-C-005, D-A-009
target: D-C-005
policy: transitive_exclusion
```

The runtime then derives the constrained view from retained lineage using its
own replay semantics. It does not receive the hidden reason, expected effect, or
a harness-produced view. Excluding `D-C-005` must make the retained experience's
consequence dependency, candidate, and admission unavailable or explicitly
unresolved. It must not leave a valid-looking admitted version.

For this fixture, the transitive dependents are `D-C-006`'s completeness as a
retained experience containing the consequence, `D-A-008`, `D-A-009`, and later
eligibility or influence derived through them. `D-C-006` remains retained but
its consequence dependency is unresolved. No separate warrant is inserted into
that occurrence receipt: admission cites `D-C-005` directly. The correction
receipt also remains retained, but its binding to excluded `D-C-005` is
unresolved and produces no governance transition.

On the identical positive foreground case, activation is withheld with refusal
`unresolved_dependency` and `blind-commit-v0` releases directly. The environment
rejects the action. The harness records this authored difference as a wire
causal comparison in the later `case scored` output, not as a new developmental
event kind or evidence of acquired competence.

## Trajectory bindings

For every developmental event after the fork, one `runtime event witnessed`
trajectory receipt records:

- branch-local developmental coordinate and content identity;
- common-prefix head;
- runtime and stub versions;
- hidden case assignment when applicable;
- exact foreground identity shared across compared branches;
- action and consequence bindings;
- authored expected wire result;
- cost counters; and
- case or refusal verdict.

No trajectory row is replayable into practitioner state.

## Cross-contract coverage

| Contract surface | Exercised here | Deliberately not required |
| --- | --- | --- |
| Occurrence and consequence | Shared acquisition, later complete encounters, external correction | A learned interpretation or complete causal explanation |
| Runtime configuration | Formation condition at fork; replay constraint at ablation boundary | One universal configuration or storage format |
| Interpretation and governance | Runtime proposal, direct admission, suspension, revocation | Trial, rejection, reinstatement, supersession, expiry |
| Influence | Considered, activated, and four authored withholding reasons | A universal activator service or proof of behavioral causality |
| Developmental replay | Clean branch replay and runtime-derived constrained replay | Hash chain, cache, snapshot, or general exclusion algorithm |
| Trajectory evidence | Protocol, prefix, branch, case, witness, ablation, cost, score, and closure receipts | Any trajectory row entering practitioner state |

Coverage means that the semantic boundary is traversed or refused. It does not
mean the fixture has earned the policy, representation, or instrument it uses.

## Fixture compatibility before schema

At this stage, two fixture declarations are compatible when they agree on:

- the authored world, stubs, public policies, and exact authored inputs;
- the semantic schedule and comparison membership above;
- which information is runtime-visible, harness-only, or protocol-public but
  withheld from runtime input;
- the required receipt meanings, originating authorities, and causal
  precedence;
- the four fixture-local refusal classes;
- the sixteen independent refusal mutations; and
- the acceptance and loses-conditions.

The semantic identity rule remains: `D-C-001` through `D-C-006` must have the
fixed coordinates, event kinds, originating authorities, causal relations,
runtime and stub identities, and authored retained content declared above. The
fixture validator checks that rule. The draft [materialization
identity](MATERIALIZATION.md) then binds the validated artifact bytes verbatim;
it does not canonicalize the graph or replace semantic validation.

Compatibility does not yet mean that one implementation can replay another's
materialized event bytes. The prefix draft selects fixture-local serialization
and digest scope only for one producer and its forks. Coordinate allocation and
serialization after `D-C-006`, integrity binding, clocks, storage, and ancillary
implementation receipts remain unselected. Machine syntax must preserve the
semantic contract; it may not decide a disagreement about authority or schedule
by making one interpretation parse.

Cross-implementation byte exchange remains a separate materialization question.
The contacted operation is same-producer fork comparison.

### Independent-construction comparison

Two independent model-family readings constructed the receipt graph from this
packet without a schema. They agreed on the authorities, three branches,
formation path, ablation boundary, four refusal classes, sixteen refusal legs,
and wire verdict. Their disagreements exposed prose-level omissions rather than
a need for typed syntax. This revision resolves those omissions by fixing:

- acquisition parents, action-role bindings, and current-authority relevance;
- the baseline's empty-set influence policy;
- mirrored ablation-branch parents and the fixture-local dependency closure;
- correction as a new non-practice occurrence with replay-derived contestation;
- scoring order, post-revocation case identity, and the distinct revoked-state
  refusal mutation; and
- the exact activated intervention identity and its admitted-version binding.

Coordinate allocation for unnamed receipts, serialization after the shared
prefix, timestamps, storage, and the choice between unavailable and explicitly
unresolved derived state remain deliberately open. The prefix contract fixes
`E-C-001`, `I-C-001`, `A-C-001`, and `K-C-001` only where its six literal
receipts require them. The two allowed derived-state results are equivalent for
this fixture only where the acceptance conditions explicitly permit either.
These open choices do not change the semantic graph or information boundary.

## Required refusal legs

A conforming implementation refuses each mutation independently from the clean
coordinate or named semantic precondition in that line:

1. At a branch's condition-binding step, the `formation condition bound`
   receipt contains a branch label.
2. From `D-G-007`, the harness role authors, inserts, or edits the candidate,
   applicability, or eligibility instead of the runtime and declared governor
   originating their receipts from runtime-visible inputs.
3. From `D-G-008`, the candidate interpretation is appended as an occurrence or
   external consequence instead of `candidate proposed`.
4. From `D-G-008`, `candidate admitted` cites an expected wire result, harness
   assignment, or scorer verdict rather than its runtime-visible warrant.
5. From `D-C-004`, the practice stub's output is presented as an external
   consequence.
6. From the opened governed positive encounter, its hidden family or expected
   action enters an activation request.
7. From `D-G-008` before admission, the proposed version is activated.
8. From the clean governed correction history after suspension and before
   revocation, the suspended version is activated.
9. From the clean governed post-revocation head, the revoked version is
   activated.
10. From `D-A-009`, the replay exclusion of `D-C-005` leaves `D-A-009`
    eligible.
11. From `D-A-009`, the harness supplies a precomputed practitioner view instead
    of the runtime recording and applying `D-A-010`.
12. From `D-A-009`, `D-A-010` contains the hidden `causal_probe` reason or
    expected downstream effect.
13. Before branch assignment, a branch prefix differs from the semantic identity
    bound by `T-C-002`.
14. From any clean developmental head, a new event cites a future or nonexistent
    causal parent.
15. After a clean case score, its scorer verdict is appended to developmental
    lineage.
16. From the opened governed positive encounter with `D-G-009` eligible, the
    intervention enters the model request without a matching `change activated`
    receipt for that encounter.

Each refusal is a separate fixture leg so one early failure cannot mask another.

## Authored wire rubric

A clean case passes only when its receipts, action, and consequence match the
authored path for its branch and no harness-only field crosses the boundary. A
refusal case passes only when its one named mutation is rejected at the named
boundary. The scorer emits `wire_integration_only` only when every clean case
and all sixteen refusal legs pass; otherwise it closes `invalid` and names the
failed clause. These are conformance classes, not scientific verdicts, and have
no partial-credit interpretation.

## Acceptance conditions

The fixture passes only when:

- the common retained prefix satisfies the fixture-local semantic identity rule
  and, when selected, the materialization identity rule across all branches;
- branch labels and case-family metadata appear only in trajectory evidence;
- any difference among public formation-condition receipts occurs only at the
  declared fork, and governed and ablation receipts match there;
- the governed path replays deterministically through proposal and admission;
- the positive case activates and the stronger surface decoy does not;
- external correction produces suspension, revocation, and later silence;
- the ablation runtime records the public constraint and derives its own view;
- the fixture's transitive replay exclusion makes every dependent state item
  unavailable or explicitly unresolved;
- the authored positive downstream difference disappears under ablation;
- all sixteen refusal legs fail closed; and
- a clean replay produces the same lineage heads and derived views.

Passing produces one wire verdict. It produces no scientific or mechanism
verdict.

## Loses-condition

This fixture loses if it can pass while the harness inserts the candidate,
reveals hidden family identity, supplies a derived practitioner view, or treats
its expected wire outcome as a runtime consequence. It also loses if conformance
requires an implementation to adopt derived-artifact revision checks, a
mandatory candidate trial, or this exact governance path as general formation
architecture rather than as opaque authored fixture content.
