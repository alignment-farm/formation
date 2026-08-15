# Deterministic two-loop boundary fixture v0

Status: **Phase 0 cold-reviewed semantic fixture; fixture-local prefix and
condition-append boundaries implemented and independently reviewed; remaining
paths wire-only**.

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

The public formation condition selects and authorizes this interpreter, so the
condition receipt is a causal parent of the proposal. The interpreter does not
receive the condition receipt as candidate evidence and may not copy procedure
names or other configuration into the candidate claim.

For this fixture, the exact text above is the retained candidate
representation. Its deterministic semantic projection is:

| Meaning | Fixture value |
| --- | --- |
| Source experience | `D-C-006 experience closed` |
| Source consequence | `D-C-005 consequence observed` |
| Author | `revision-check-candidate-v0`, invoked and recorded by the formation runtime |
| Claimed applicability | A commitment of a derived object whose acceptability depends on its current authoritative source |
| Explicit non-applicability | An object whose validity is independent of current authority |
| Expected practice effect | Compare the artifact and authority revisions; refresh before commitment when they differ |
| Counterevidence | An externally sourced correction to `D-C-005` showing that revision mismatch was not causal |
| Expiry | None declared |

These meanings are candidate claims, not environment facts or scorer findings.
The equality path—commit directly when the revisions already match—belongs to
the later practice actor under an activated intervention. It is not added to the
candidate's expected-effect claim.

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

The governor is the decision authority for `candidate admitted`; the formation
runtime invokes it and records its decision. For the first admission, its exact
semantic output is:

| Meaning | Fixture value |
| --- | --- |
| Candidate version | The exact branch-local `candidate proposed` receipt |
| Policy | `consequence-warrant-v0` |
| Warrant | `D-C-005` plus satisfaction of the four declared checks above |
| Admitted scope | Commitments of derived objects whose acceptability depends on the current authoritative source; authority-independent validity is excluded |
| Initial status | `eligible` |
| Trial | None |

The proposal receipt is the candidate version. The admission receipt is the
governed, eligible version later influence decisions must cite. Equivalent text
without the exact proposal lineage is not the same candidate version.

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
- refusal execution: thirty-one independent legs, each starting from its named
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

The `D-B-*`, `D-G-*`, and `D-A-*` coordinates in this document are prose
aliases. They let the fixture state branch-specific parents and refusal cases
without making the hidden assignment part of practitioner state. Materialized
developmental receipts use runtime-visible opaque coordinates instead. The
trajectory witness joins each opaque coordinate to its prose alias for audit;
that join is never replayed into the runtime.

`baseline`, `governed`, and `ablation`, their one-letter aliases, and the prose
coordinates above may not appear in any runtime-visible field. The public
condition itself may distinguish the baseline mechanism from the treatment
mechanism. Governed and ablation receive the same public condition and must
have identical validated public-condition payloads until the declared ablation
boundary. Their opaque event coordinates, runtime handoffs, root capabilities,
and content bindings remain distinct identity facts rather than condition
differences.

`T-A-001` contains the branch assignment only. The later `ablation assigned`
receipt is a distinct trajectory event created at schedule step 4; its public
target and policy do not appear early in `T-A-001`.

Each branch-local formation-condition receipt cites `D-C-006` as its causal
parent.

The [condition-append contract](CONDITION_APPEND.md) fixes the first machine
representation after the fork. It gives every fork an exact retained capability
before the harness assigns a branch, then keeps the six-line prefix unchanged
while the runtime authors a separate condition segment with an opaque event
coordinate.

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
5. The harness freezes the exact closed positive foreground from the
   protocol-authored value below and records one trajectory `foreground bound`
   receipt naming the three branch roots authorized to receive it. This occurs
   after `D-A-010` and before branch-local case assignment or presentation.
6. Each positive `case assigned` receipt cites that foreground binding. The
   harness delivers the same frozen public value once to baseline, governed,
   and ablation; each runtime consumes its delivery in `encounter opened`.
   Their executions may occur in any order.
7. The non-activation decoy is presented to governed only. It tests the
   fixture's authored applicability path, not a cross-branch contrast.
8. After the positive comparison and governed decoy are complete, the same
   environment-authored correction is presented to all three branches.
9. Governed applies its declared suspension and revocation policy, then receives
   one later matching commitment boundary to demonstrate post-revocation
   silence. Baseline and ablation emit no governance transition from the
   correction.
10. The scorer operates only after all required developmental histories and
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
| Later practice | Freeze one closed foreground and deliver it once to each compared root under one environment rule | Exactly the seven public foreground roles | Record the received projection, decide influence, construct the branch-specific practice request, commit the action, and record consequence | Case family, expected action, cross-branch result, and foreground binding | `foreground bound`, activation or withholding, invocation, action, consequence, and direct foreground witnesses |
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

The runtime appends the proposal before invoking the governor. After each
runtime append, the harness may validate and witness the developmental receipt;
it may not supply or repair it. A second proposal or admission at the same
fixture head refuses: revision, rejection, supersession, and retry paths are not
selected here.

The ablation runtime independently produces the same semantic path under
branch-local coordinates `D-A-008` through `D-A-009`. Its payloads and derived
view match the governed path apart from coordinates and any implementation-level
integrity bindings. `D-A-008` has parents `D-C-005`, `D-C-006`, and `D-A-007`;
`D-A-009` has parents `D-C-005`, `D-A-007`, and `D-A-008`. The ablation is
applied only after `D-A-009` exists.

Through admission, governed and ablation match on the exact retained candidate
text, semantic projection, interpreter authorship, admission policy, warrant,
scope, initial status, and absence of a trial. They remain independently
authored histories. Their opaque coordinates, exact proposal and admission
versions, root capabilities, handoffs, and content bindings differ without
constituting a mechanism difference.

Baseline performs neither proposal nor admission. Its later
`no_admitted_change` result is an influence-boundary outcome, not a formation
event inserted during this phase.

## Shared positive foreground

The positive comparison uses one frozen semantic foreground, called `F+` here
only for exposition. It is a closed value with exactly seven public roles:

| Role | Exact value |
| --- | --- |
| `candidate_object` | `bundle-9` |
| `derived_from` | `registry-manifest` |
| `artifact_revision` | integer `7` |
| `authority_revision` | integer `8` |
| `depends_on_current_authority` | boolean `true` |
| `commit_action` | `release` |
| `refresh_action` | `rebuild_then_release` |

Role order is not semantic. A changed value, missing role, extra role, changed
value type, branch label, case family, expected result, scorer key, coaching
text, intervention field, or ablation reason is not `F+`.

The human protocol owner authors this value. After `D-A-010` exists and before
any positive branch-local case assignment, the harness freezes it once and
records one trajectory `foreground bound` receipt. That receipt binds the exact
closed value, comparison group, and three existing branch roots authorized to
receive it. Hidden recipient mapping stays in trajectory evidence.

The harness derives exactly one public delivery for each authorized root from
that immutable freeze. Each delivery contains only the seven public roles. It
does not identify its branch or comparison group to the runtime. Branch
execution order is free, but a missing, duplicate, reused, late, or wrong-root
delivery refuses. Reopening or rebuilding from a mutable or independent source
after the freeze is nonconforming even if the rebuilt role values match.

Each runtime consumes its delivery exactly once when it records the positive
`encounter opened` receipt, whose situation projection is the exact seven-role
value received. A trajectory witness then compares that complete projection
directly with the single foreground binding. No defaulting, ignored extras, or
semantic paraphrase is permitted.

Foreground identity ends at that projection. It does not require equality of
the complete encounter receipts, eligible state, activation decisions, model
requests, actions, or consequences. In particular, the governed model request
adds its encounter-local activation handoff; baseline and ablation requests do
not. Comparing complete requests would erase the mechanism difference the
fixture is meant to exercise.

## Later practice paths

Every commitment-boundary presentation below is a complete practice encounter.
The runtime records `encounter opened`, `activation considered`, exactly one of
`change activated` or `activation withheld`, `model invoked`, `action committed`,
`consequence observed`, and `experience closed` in that causal order. The prose
below names the branch-specific activation, action, and consequence rather than
repeating that common receipt sequence. The later external correction is not a
practice encounter; its smaller receipt path is specified separately.

Each `activation considered` has the public formation condition in force, the
current encounter, and every exact admitted version actually considered as
causal inputs. In the governed positive and decoy encounters that set contains
the branch-local admitted version aliased here as `D-G-009`; in the ablation
branch the decision also cites `D-A-010`. A `change activated` receipt has the
considered receipt and exact selected admitted version as parents. The model
invocation cites the exact activation or withholding receipt for that encounter,
so an intervention cannot enter a practice request without an attributable
influence decision.

The eligible set in `activation considered` contains `D-G-009` only for the
clean governed positive and decoy encounters. It is empty for baseline, for the
constrained ablation view, and after governed revocation. The shared acquisition
precedes any formation condition and therefore has no activation receipt.

For the governed positive path, the runtime resolves the selected admitted
version from its current lineage and originates one immutable activation
handoff. Its exact semantic content is:

| Meaning | Fixture value |
| --- | --- |
| Encounter | The current governed positive encounter |
| Considered decision | The exact `activation considered` receipt for that encounter |
| Selected admitted version | The exact branch-local `candidate admitted` receipt aliased `D-G-009` |
| Proposal version | The exact `D-G-008` receipt cited by that admission |
| Intervention procedure | `revision-check-intervention-v0` |
| Intervention content | The retained candidate representation read through `D-G-009` to `D-G-008` |
| Selection reason | Both runtime-visible roles `derived_from` and `depends_on_current_authority` are present and the latter is true |

`revision-check-intervention-v0` is a procedure name, not the encounter-local
intervention identity. That identity is the exact activation handoff above.
Documentary aliases never enter it; materialized lineage uses the opaque
branch-local identities. Equivalent candidate text, the ablation branch's
semantically matching admission, or independently reconstructed fields are not
the selected object.

The practice boundary consumes this same immutable handoff exactly once when it
constructs the model request. It may not reopen lineage or mutable storage to
recreate matching values. The request contains the current foreground and the
exact handoff. The intervention identity, admitted-version binding, and exact
candidate content are available through that handoff, not copied into parallel
request fields that could disagree with it. The `model invoked` receipt cites
the exact encounter-local
`change activated` receipt and retains the exact request or a content-identity
binding to it. The harness may witness that result afterward; it may not supply,
replace, or repair the handoff or request.

On every withheld path, `activation withheld` has the considered receipt as its
parent and no activation handoff exists. The model request must contain no
intervention procedure, admitted-version binding, or copied candidate content.

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

#### Positive environment rule

The two positive actions use the public fixture rule
`revision-gated-release-v0`. Each branch-local application begins from its own
encounter situation; applications do not share mutable artifact state with one
another.

- `release` leaves `artifact_revision` unchanged. When it differs from
  `authority_revision`, the environment returns disposition `rejected` and
  observation `stale_dependency`.
- `rebuild_then_release` first makes the application-local artifact revision
  equal the supplied authority revision, then releases. The environment returns
  disposition `accepted` and observation `released`.

The resulting positive projections are therefore baseline revision 7 to 7
against authority revision 8, and governed revision 7 to 8 against authority
revision 8. These exact tokens make the already-authored “rejects” and “accepts”
outcomes inspectable. They are environment results, not scorer expectations or
developmental `consequence observed` receipts.

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

After the positive comparison and governed decoy, the environment originates
and presents the same correction to each branch's copy of the shared acquisition
consequence. Each runtime records and appends a branch-local external occurrence
referring back to `D-C-005`:

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

For derivation, the input is the ablation branch's actual retained semantic
lineage at the head containing `D-A-010`. The runtime reads the target and policy
from that bound constraint and follows the declared meanings of the retained
references below. The documentary aliases and this table are inspection
oracles, not runtime inputs.

| Retained item or view element | Reference role contacted by exclusion | Required constrained result |
| --- | --- | --- |
| `D-C-005` | Exclusion target | Receipt retained; unavailable as a usable consequence or warrant |
| `D-C-006` | State-bearing containment of consequence `D-C-005` | Receipt retained; consequence dependency and experience completeness explicitly unresolved |
| `D-A-008` | Source consequence `D-C-005` and source experience `D-C-006` | Candidate unavailable or explicitly unresolved |
| `D-A-009` | Warrant `D-C-005` and candidate version `D-A-008` | Admission unavailable or explicitly unresolved; never eligible-looking |
| Later eligibility and influence | Derived through `D-A-009` | Empty eligible set and `unresolved_dependency` at the affected decision |
| Later correction | Correction binding to `D-C-005` | Occurrence retained; binding unresolved; no governance transition |
| `D-C-001` through `D-C-004` and `D-A-007` | No contacted state dependency | Preserved and available |
| `D-A-010` | Control reference naming the exclusion target | Preserved as the active constraint; not propagated into its own closure |

Each unavailable or unresolved result must be traceable through the actual
branch-local references above. Missing, altered, future, or nonexistent required
references refuse before a view is returned. The same input head and constraint
produce the same view. A target-keyed lookup that returns this table without
consuming the retained dependency projection is nonconforming.

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

The positive comparison has one `foreground bound` receipt before its three
branch-local `case assigned` receipts. Each case assignment cites it. Each later
positive `encounter opened` witness records both the foreground binding and the
complete seven-role situation projection received by that runtime. The witness
compares that projection directly to the freeze; it does not compare the full
model request.

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
| Developmental replay | Clean branch replay and runtime-derived constrained replay from actual retained dependencies | Hash chain, cache, snapshot, or general exclusion algorithm |
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
- the thirty-one independent refusal mutations; and
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
formation path, ablation boundary, four refusal classes, the then-current
sixteen refusal legs, and wire verdict. Their disagreements exposed prose-level
omissions rather than
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

A later cold replay review exposed a different defect: the enumerated ablation
answer could stand in for source-sensitive replay. The actual-lineage rule and
refusal legs 17 through 20 close that counterfeit-oracle path. They add
fixture-local dependency pressure without selecting a general replay graph.

A later activation-identity review exposed the analogous repeated-name defect
at the influence boundary. The immutable semantic handoff and refusal legs 21
through 24 make the actual admitted lineage object, rather than its alias or
copied text, the source of the intervention and request.

A later shared-foreground review exposed ambiguity between a common public
situation and the branch-specific request built from it. The closed seven-role
freeze and refusal legs 25 through 31 make the foreground provenance and
comparison exact without requiring the governed request to equal the two
withheld requests. Two model-family rechecks reconstructed that object. A
focused license review then distinguished public-value equality from freeze
provenance, root binding, and one-time consumption. The resulting
[foreground-delivery contract](FOREGROUND_DELIVERY.md) earns typed local
capabilities and validators while leaving foreground bytes unselected. Two
independent cold contract reconstructions agreed on that boundary and returned
`CONTRACT_STABLE_CODE_BLOCKED` because the governed admitted root and ablation
constraint root were not yet materialized. The governed admitted root is now
implemented under [ADMITTED_ROOT.md](ADMITTED_ROOT.md); the ablation constraint
root remains open.

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
17. From the clean ablation head, a required retained parent or dependency role
    of `D-C-006`, `D-A-008`, or `D-A-009` is missing or altered, but replay
    returns the authored closure instead of refusing the broken lineage.
18. From the clean ablation head, replay marks `D-A-007` or any of `D-C-001`
    through `D-C-004` unavailable even though no contacted state dependency
    reaches it.
19. From the clean ablation head, replay deletes `D-C-006` instead of retaining
    it with unresolved consequence dependency and completeness.
20. From the clean ablation head, replay makes `D-A-010` unavailable merely
    because its control reference names `D-C-005`, instead of preserving the
    active constraint.
21. From the opened governed positive encounter, `activation considered` names
    equivalent candidate text, `D-A-009`, or a documentary alias rather than
    the exact eligible branch-local admitted lineage object.
22. From the clean governed considered decision, `change activated` selects an
    admitted version different from the exact version considered, or omits the
    considered decision or selected version as a causal parent.
23. From the clean governed activation, the intervention is constructed from
    fixture text, an equivalent proposal, or mutable state rather than the exact
    proposal reached through the selected admission.
24. From the clean governed activation, request construction or model invocation
    replaces, reconstructs, tampers with, reuses, or cites a same-named handoff
    instead of consuming the exact encounter-local handoff once.
25. Before positive case assignment, the `foreground bound` value changes,
    omits, adds, or changes the type of one of the exact seven public roles.
26. At the positive freeze or delivery boundary, a branch label, case family,
    expected result, scorer key, coaching field, intervention field, or ablation
    reason enters the public foreground.
27. From the clean positive freeze, one branch delivery changes, omits, adds,
    substitutes, or defaults a role instead of deriving the complete value from
    that freeze.
28. From the clean positive freeze, the controller reopens mutable source state,
    independently rebuilds the value, or accepts caller replacement rather than
    deriving every delivery from the one frozen value, even when role values
    happen to match.
29. From the clean three-recipient delivery set, one delivery is missing,
    duplicated, reused, assigned to the wrong root or comparison group, or
    consumed more than once.
30. The positive foreground is bound, assigned, or presented before `D-A-010`,
    or a runtime opens its positive encounter before its case assignment cites
    the foreground binding.
31. A positive witness ignores extra received fields, compares only a partial
    projection, or uses equality of the complete branch-specific model requests
    instead of direct equality of the closed foreground projection.

Each refusal is a separate fixture leg so one early failure cannot mask another.

## Authored wire rubric

A clean case passes only when its receipts, action, and consequence match the
authored path for its branch and no harness-only field crosses the boundary. A
refusal case passes only when its one named mutation is rejected at the named
boundary. The scorer emits `wire_integration_only` only when every clean case
and all thirty-one refusal legs pass; otherwise it closes `invalid` and names the
failed clause. These are conformance classes, not scientific verdicts, and have
no partial-credit interpretation.

## Acceptance conditions

The fixture passes only when:

- the common retained prefix satisfies the fixture-local semantic identity rule
  and, when selected, the materialization identity rule across all branches;
- branch labels and case-family metadata appear only in trajectory evidence;
- any difference among public formation-condition receipts occurs only at the
  declared fork, and governed and ablation have identical validated condition
  payloads there apart from their opaque coordinates, runtime handoffs, root
  capabilities, and content bindings;
- governed and ablation independently produce the same proposal projection and
  admission decision through their branch-local admitted versions, apart from
  identity and integrity facts;
- the positive foreground is frozen once as the exact closed seven-role value,
  delivered once to each declared branch root, and directly matches every
  received `encounter opened` situation projection without requiring full
  request equality;
- the governed path replays deterministically through proposal and admission;
- the positive case activates and the stronger surface decoy does not;
- external correction produces suspension, revocation, and later silence;
- the ablation runtime records the public constraint and derives its own view;
- the fixture's transitive replay exclusion makes every dependent state item
  unavailable or explicitly unresolved;
- the authored positive downstream difference disappears under ablation;
- all thirty-one refusal legs fail closed; and
- a clean replay produces the same lineage heads and derived views.

Passing produces one wire verdict. It produces no scientific or mechanism
verdict.

## Loses-condition

This fixture loses if it can pass while the harness inserts the candidate,
reveals hidden family identity, supplies a derived practitioner view, or treats
its expected wire outcome as a runtime consequence. It also loses if conformance
requires an implementation to adopt derived-artifact revision checks, a
mandatory candidate trial, or this exact governance path as general formation
architecture rather than as opaque authored fixture content. It further loses
if compared branches can receive unequal or differently enriched foregrounds,
or if foreground identity is confused with equality of their intentionally
different model requests.
