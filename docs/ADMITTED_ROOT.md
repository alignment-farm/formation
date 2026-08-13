# Proposal and direct-admission root contract

Status: **fixture-local typed materialization contract implemented and
post-build reviewed; receipt bytes remain unselected**.

Cold construction first separated semantic closure from machine form. One
reader correctly rejected proposal and admission bytes as unearned; another
identified the narrower need for exact in-memory admitted-root capabilities.
The repaired contract was independently reconstructed as
`CONTRACT_STABLE_CODE_LICENSED` and passed a separate code-facing review.

Purpose: define the smallest machine boundary that turns each exact treatment
condition root into one exact eligible admitted-version root. The foreground
delivery contract needs those roots as capabilities. This contract does not
define a general interpretation or governance schema.

## Named computational need

The earlier proposal and admission review stopped in Markdown because no
machine operation needed their identity. That changed when shared-foreground
delivery required the current governed admitted root and the later ablation
constraint required the current ablation admitted root.

The required computation is:

```text
two exact treatment condition roots
  -> one label-blind runtime formation slot per root
  -> one proposal authored from that root's preserved experience
  -> one governor decision over that exact proposal
  -> one immutable admitted root per treatment root
```

Semantic equality cannot prove this path. Constant fixture text can imitate the
candidate without consuming experience. Equivalent text can imitate the
candidate while changing its version. An eligible-looking admission can cite
the wrong proposal or condition root. Those cases require typed provenance,
exact object identity, and one-shot root transitions.

This need earns in-memory fixture capabilities and validators only. It does not
earn proposal or admission bytes, digests, coordinate strings, canonical field
order, storage, or cross-implementation exchange.

## Existing input boundary

The operation accepts only exact immutable `BranchLocalRoot` capabilities
returned by the condition-append controller. Each accepted root retains:

```text
prefix_root: exact immutable six-receipt prefix root
condition_segment: exact validated condition receipt bytes
head: opaque condition coordinate
condition_binding: exact binding over the condition segment
```

Before formation begins, the condition-append controller has returned and
witnessed all three roots. It issues one private, one-use
`TreatmentRootBatch` containing exactly the two roots whose validated public
condition is `consequence_governance_activation-v0`, in their original
label-blind root-issuance order. The set contains no branch label, assignment
coordinate, expected result, scorer field, ablation target, or hidden reason.

The runtime accepts only that exact retained set. It rejects a raw sequence,
caller-selected pair, reversed pair, duplicated root, condition-only copy,
baseline root, missing treatment root, stale root, other-run root, or equal
reconstruction. The harness cannot add, remove, reorder, or replace a root
after the set is issued.

The two roots have the same public formation condition. Nothing at this
boundary identifies which will later receive an ablation constraint.

## Source derived from retained lineage

For each treatment root, a runtime-owned adapter validates the exact prefix
artifact and exact condition segment through their existing fixture contracts.
It then captures one immutable `FixtureFormationSource` containing:

```text
run: current fixture-run capability
consumed_root: exact treatment BranchLocalRoot
source_consequence: exact retained D-C-005 receipt
source_experience: exact retained D-C-006 receipt
public_condition: exact validated treatment condition
```

The adapter reads `D-C-005` and `D-C-006` from the actual immutable prefix
retained by the consumed root. The harness may not supply parsed receipts,
candidate text, a precomputed projection, or an authored practitioner view.
The adapter may inspect the public condition only to establish that the named
interpreter and governor are authorized. The condition is a causal parent, not
candidate evidence.

Each source belongs to one exact root and is consumed once. Reopening mutable
storage, accepting a caller mapping, substituting another root's receipts, or
returning the fixture candidate as a constant without reading the retained
receipts refuses.

## Runtime formation run and opaque coordinates

Only a runtime-owned `RuntimeFormationRun` consumes the exact
`TreatmentRootBatch`. It creates one formation materializer for each retained
root in the set's label-blind order. The harness receives no coordinate
issuance or reservation method.

For each root, the runtime reserves two distinct opaque coordinate capabilities:

```text
proposal_coordinate
admission_coordinate
```

They identify events within the current run but have no selected string
encoding. They expose no branch label, condition name, assignment coordinate,
expected result, scorer value, ablation value, or documentary `D-G-*` /
`D-A-*` alias. They are unique across the formation run. Proposal is branch
order `8`; admission is branch order `9`. The runtime retains the original
root and coordinate reservations and refuses later mutation or substitution.

## Exact proposal

The declared interpreter `revision-check-candidate-v0` is the proposal author.
The formation runtime invokes it, hosts the recorder, and preserves the
authorship; the runtime host is not a second candidate author. The harness and
governor are not candidate authors.

The interpreter consumes the exact `FixtureFormationSource` once and produces
the exact retained representation:

```text
When committing a derived object whose acceptability depends on the current
authoritative source, compare its source revision with the authority revision.
Refresh before commitment on mismatch. Do not apply this check when current
authority is not part of the object's validity rule. Treat an externally sourced
correction showing that revision mismatch was not causal as counterevidence.
```

Its one deterministic semantic projection is:

| Meaning | Exact fixture value |
| --- | --- |
| Source experience | exact retained `D-C-006` |
| Source consequence | exact retained `D-C-005` |
| Author | `revision-check-candidate-v0` |
| Claimed applicability | A commitment of a derived object whose acceptability depends on its current authoritative source |
| Explicit non-applicability | An object whose validity is independent of current authority |
| Expected practice effect | Compare artifact and authority revisions; refresh before commitment when they differ |
| Counterevidence | An externally sourced correction to `D-C-005` showing revision mismatch was not causal |
| Expiry | none |

The exact text is the retained representation. The projection is derived by the
fixture validator; it is not a second caller-authored input.

Only the runtime proposal materializer may construct `ProposedCandidate`. It is
an immutable semantic capability containing:

```text
run: current fixture-run capability
consumed_root: exact treatment BranchLocalRoot
coordinate: reserved opaque proposal coordinate
order: 8
event: candidate proposed
author: revision-check-candidate-v0
recorder: formation_runtime
parents: exact D-C-005, exact D-C-006, exact condition head
representation: exact retained candidate text
projection: exact validator-derived semantic projection
```

The proposal also retains the exact private `InterpreterAuthorship` capability
returned by a distinct interpreter invocation. That invocation consumes and
parses the captured `D-C-005` and `D-C-006` receipts before originating the
representation and projection. An author name written by the runtime host is
not a substitute for this capability.

The materializer retains private issuer identity and the exact object. The
proposal object is the candidate version. Equal text, an equal reconstructed
object, a coordinate alias, or a candidate copied from the other treatment
branch is not that proposal version.

The runtime returns one immutable `ProposalHandoff` containing the exact source
and proposal. The harness validates and witnesses that handoff without
authoring, normalizing, repairing, replacing, or reconstructing either object.
A proposal failure yields no current proposal handoff and no governor call.

## Exact direct admission

After the proposal exists, the runtime invokes
`consequence-warrant-v0` over that exact retained proposal. The governor is the
decision authority. The formation runtime hosts invocation and recording; the
harness does neither.

The governor admits only when the proposal and retained consequence satisfy the
four fixture checks:

1. the source experience contains an external consequence;
2. the proposal cites that consequence and declares how later practice changes;
3. applicability excludes authority-independent validity; and
4. correction of the source consequence is named as counterevidence.

The exact direct-admission result is:

| Meaning | Exact fixture value |
| --- | --- |
| Candidate version | exact current `ProposedCandidate` object |
| Policy and decision authority | `consequence-warrant-v0` |
| Warrant | exact retained `D-C-005` plus satisfaction of the four checks |
| Admitted scope | Commitments of derived objects whose acceptability depends on the current authoritative source; authority-independent validity is excluded |
| Initial status | `eligible` |
| Trial | none |

Candidate applicability remains the interpreter's claim. Admitted scope is the
governor's permission. They remain separate meanings even where this fixture
makes them extensionally equal.

Only the runtime governor materializer may construct `AdmittedCandidate`. It is
an immutable semantic capability containing:

```text
run: current fixture-run capability
consumed_root: exact treatment BranchLocalRoot
proposal: exact current ProposedCandidate
coordinate: reserved opaque admission coordinate
order: 9
event: candidate admitted
decision_authority: consequence-warrant-v0
recorder: formation_runtime
parents: exact D-C-005, exact condition head, exact proposal coordinate
warrant: exact retained consequence plus four satisfied checks
scope: exact admitted scope
status: eligible
trial: none
```

The admission also retains the exact private `GovernorDecision` capability
returned by a distinct governor invocation. The governor evaluates the exact
current proposal and the four warrant checks before originating scope, status,
and trial absence. A decision-authority name written by the runtime host is not
a substitute for this capability.

The governor consumes the exact proposal once. Another branch's proposal,
equivalent text, a caller reconstruction, a noncurrent or changed proposal,
or a proposal not rooted in the same condition root refuses. Admission cannot
precede proposal and cannot be repeated at the same head.

The runtime returns one immutable `AdmissionHandoff` containing the exact
proposal handoff and admitted candidate. The harness validates and witnesses it
without producing or repairing the decision.

## Returned admitted root

After both runtime handoffs have been independently validated and witnessed,
the append controller returns one immutable `AdmittedBranchRoot`:

```text
run: current fixture-run capability
condition_root: exact consumed BranchLocalRoot
proposal: exact ProposedCandidate
admission: exact AdmittedCandidate
head: exact opaque admission coordinate
```

The append controller retains private issuer identity, the exact root, and a
snapshot of every capability above. It also retains the exact originating
runtime verifier and admission handoff. Every later root-consumption check asks
that runtime to revalidate the complete current chain from retained source,
through interpreter authorship and governor decision, to admission. This avoids
creating a weaker second provenance implementation in the harness.

This root is distinct from the condition root. It is returned once and later
work must consume it directly. A raw
mapping, documentary alias, caller-created root, equal reconstruction, changed
object, stale root, other-run root, condition-only root, or root from the other
treatment branch refuses.

The governed and ablation operations produce two distinct admitted roots. The
complete public semantic projections of their proposals and admissions must
match. Their opaque coordinates, exact root and proposal identities, issuer
capabilities, handoffs, witnesses, and future downstream histories must differ.

This returned root satisfies the governed prerequisite in
[FOREGROUND_DELIVERY.md](FOREGROUND_DELIVERY.md). It is only an ancestor of the
ablation prerequisite. The ablation branch still requires a separate
replay-constraint append containing `D-A-010` before foreground freeze.

## Baseline silence

The baseline condition root is not a formation input. It names no interpreter
or governor. The treatment-root set excludes it, and every proposal,
admission, or admitted-root operation presented with it refuses.

Baseline emits no placeholder proposal, rejection, admission, empty admitted
root, or synthetic governance event. Its later `no_admitted_change` result
belongs to the influence boundary.

## Validation, provenance, identity, and exchange

These checks remain separate:

| Check | Owner | Question |
| --- | --- | --- |
| Semantic validation | Protocol fixture validator | Do proposal and admission have the exact permitted meanings, parents, order, authorities, and public values? |
| Proposal provenance | Runtime interpreter materializer | Was this proposal authored from this exact retained source and treatment root? |
| Admission provenance | Runtime governor materializer | Did this governor decide over this exact proposal version and warrant? |
| Root and one-shot identity | Formation append controller | Do the two current handoffs extend this exact root once and yield this exact admitted head? |
| Witness identity | Trajectory witness | Are the runtime-returned semantic objects complete and unchanged, with no harness repair? |
| Exchange | Unselected | No byte format or cross-implementation exchange is claimed. |

Direct comparison of the closed semantic projections is authoritative for
governed/ablation equality. Capability identity is authoritative for source,
proposal-version, and admitted-root provenance. Neither substitutes for the
other. No digest is selected.

## Refusal vectors and ownership

Each refusal starts independently from a clean treatment-root set, formation
source, proposal boundary, admission boundary, handoff, witness, or returned
root:

1. Supply fewer or more than the exact two treatment roots, duplicate or
   reorder them, select them by hidden label, or include baseline.
2. Supply a raw sequence, path, mapping, caller-selected pair, stale set,
   other-run set, or equal reconstruction instead of the issued
   `TreatmentRootBatch`.
3. Supply a raw, forged, copied, stale, other-run, wrong-head, condition-only,
   or reconstructed-equal `BranchLocalRoot`.
4. Change the retained prefix bytes, condition bytes, binding, head, or public
   condition after the root was returned.
5. Let the harness supply parsed source receipts, candidate text, projection,
   warrant checks, eligibility, or a practitioner view.
6. Read candidate evidence from the condition receipt, branch assignment,
   expected result, scorer, ablation target, or hidden reason.
7. Ignore the retained `D-C-005` or `D-C-006`, use another root's receipt, reopen
   mutable storage, or emit the fixture candidate as a source-independent
   constant.
8. Change, omit, add, normalize, paraphrase, or mistype the candidate
   representation or any projected meaning.
9. Name the runtime host, harness, governor, or cold model as proposal author.
10. Change, omit, or add to the proposal parent set; cite a documentary
    alias or another branch's condition head.
11. Reuse a source, issue no proposal or two proposals, mutate a reserved
    coordinate or root, or reconstruct the proposal handoff.
12. Admit before proposal, admit a noncurrent or changed proposal, or admit a
    proposal rooted in another condition branch.
13. Cite equivalent candidate text, an equal reconstruction, another branch's
    proposal, or a documentary alias instead of the exact proposal object.
14. Change, omit, or add to the admission parent set; omit the exact
    proposal coordinate or use a future/nonexistent parent.
15. Let the runtime host, harness, interpreter, or scorer become admission
    decision authority.
16. Change the policy, warrant, admitted scope, initial status, or explicit
    absence of trial; import an expected wire result into the decision.
17. Reuse a proposal, issue no admission or two admissions, mutate the reserved
    coordinate, or reconstruct the admission handoff.
18. Emit any branch label, assignment coordinate, expected result, scorer
    field, ablation target, `causal_probe`, or hidden reason in a runtime-visible
    source, proposal, admission, handoff, coordinate, or root.
19. Copy the governed proposal, admission, handoff, coordinate, or root object
    into ablation, or allow their public semantic projections to differ.
20. Let the harness author, insert, normalize, repair, replace, or reconstruct a
    runtime object or caller-created witness.
21. Return the condition root, proposal object, raw mapping, alias, stale root,
    other-run root, or equal reconstruction as the admitted root.
22. Treat the admitted ablation root as if it already contained `D-A-010`, or
    let foreground delivery consume it before replay-constraint append.

The fixture validator owns semantic content, parent-set, order, and hidden-field
refusals. The condition-append controller owns treatment-set and input-root
provenance. The runtime source adapter and interpreter materializer own retained
input and proposal-authorship refusals. The governor materializer owns exact
proposal-version and decision-authority refusals. The formation append
controller owns one-shot handoffs and returned-root identity. The trajectory
witness owns unchanged-object and no-repair refusals.

## Implementation gate

Code may begin only after cold readers independently reconstruct:

- the exact two-root, label-blind input set;
- source derivation from the real retained prefix and condition;
- separate interpreter authorship, runtime recording, and governor authority;
- the exact proposal object as candidate version;
- direct admission over that exact proposal;
- one-shot handoffs and the distinct returned admitted root;
- governed/ablation semantic equality with branch-local identity; and
- baseline silence and the refusal ownership above.

The first implementation, if licensed, is fixture-local and in-memory. It must
extend the existing condition-root capabilities rather than reopen paths or
introduce a second lineage representation.

That gate is complete. The implementation produces two distinct admitted roots
from one label-blind treatment batch and passes 45 deterministic tests. The
first 39-test green run was not accepted as closure: post-build review found
shallow nested snapshots, mutable upstream bindings, and a runtime host that
could stamp interpreter and governor authority without invoking distinct
authorities. Repairs added source-reading interpreter authorship, an exact
proposal-evaluating governor decision, full current-chain verification, and
independent mutation regressions. Final mechanical recheck returned `PASS`.

## Unselected

This contract does not select:

- JSON, JSON Lines, proposal or admission receipt bytes;
- string encodings for opaque coordinates or documentary aliases;
- a digest, content binding, canonical field or parent order, or storage form;
- a general interpretation, governance, lifecycle, developmental, or
  trajectory schema;
- a generic candidate language, projection system, or governor service;
- trial, rejection, revision, withdrawal, supersession, or retry paths;
- replay-constraint, activation, encounter, foreground, correction, or scoring
  syntax;
- cross-implementation exchange, authentication, or distributed writers; or
- any formation, transfer, or causal finding.

## Acceptance and loses-conditions

This contract is sufficient only if independent readers reconstruct one exact
source-derived proposal per treatment root, one direct governor admission over
that exact proposal, two distinct admitted roots with matching public semantic
projections, baseline silence, and the same implementation and non-license
boundary.

It loses if fixture text can replace source consumption, equivalent text can
replace the proposal version, the harness authors or repairs either event, the
runtime host becomes governor, a condition root can masquerade as admitted, a
branch label can influence coordinates or content, governed and ablation share
an identity, or the admitted ablation root is treated as if `D-A-010` already
exists.
