# Positive activation-decision contract

Status: **fixture-local semantic contract implemented; independent post-build
review passes**.

Purpose: define the next formation-lifecycle append for the baseline and
governed positive encounters. Each runtime must record `activation considered`
and exactly one result. Baseline withholds because it has no admitted change.
Governed activates the exact admitted change whose applicability matches the
current situation. The ablation result remains excluded until constrained
replay can derive its eligible set from retained lineage.

## Why this is a two-root boundary

The positive encounter-opening slice returns three exact current roots. Two can
make their activation decision from already materialized runtime-visible state:

| Root | Runtime-visible eligibility source | Required result |
| --- | --- | --- |
| Baseline encounter root | `audit_lineage_only-v0`; no admitted change | Withhold: `no_admitted_change` |
| Governed encounter root | Exact eligible admission and positive situation | Activate exact admitted version |

The ablation encounter root contains `D-A-010`, but no runtime-derived
constrained view exists. Returning `unresolved_dependency` from its target name
or documentary alias would reproduce the fixture's expected answer without
performing replay. This contract therefore accepts no ablation root and makes
no three-branch causal claim.

That exclusion is a stopping condition, not an optional implementation choice.
The later ablation decision must receive a separately licensed runtime-derived
view or another exact capability that proves the eligible set was derived from
the retained dependency projection.

## Named computational need

Later request construction must distinguish these two exact results:

```text
baseline encounter root
  -> activation considered with empty eligible set
  -> activation withheld: no_admitted_change
  -> exact current withheld-decision root

governed encounter root
  -> activation considered with exact admitted version
  -> change activated with one encounter-local intervention
  -> exact current activated-decision root + one-shot activation handoff
```

Equal result strings cannot prove which encounter was considered, which exact
admitted version was selected, whether the selected proposal supplied the
intervention content, or whether a handoff entered two requests. Later request
construction needs exact current roots and a linear activation handoff, so a
fixture-local typed identity boundary may be earned after cold review.

No bytes, digest, request format, or universal activation schema is selected.

## Shared activation-considered append

For each accepted encounter root, the runtime appends one immutable
`ActivationConsidered` object containing:

```text
run: current fixture run
predecessor: exact current encounter root
encounter: exact encounter capability retained by that root
formation_condition: exact public condition in the predecessor lineage
activation_policy: exact public influence policy in force
eligible_versions: exact closed tuple of admitted lineage objects considered
situation: exact seven-role situation retained by the encounter root
```

Its causal inputs are the current encounter, the public formation condition,
and every admitted version actually considered. Documentary aliases, copied
candidate text, semantically equal admissions, and hidden branch or case labels
cannot enter the object.

The runtime reads the situation from the exact encounter root. It may not
reopen the foreground handoff, freeze, protocol source, or trajectory
assignment. The seven-role situation remains the complete public observation
boundary for this fixture.

Exactly one result must extend the considered append. Failure returns no
considered object, result, handoff, or new root and does not consume the
decision right.

## Baseline withholding

The baseline predecessor must be the exact current encounter root whose
ancestor is the `audit_lineage_only-v0` condition-bound root. Its public
condition has no interpreter, governor, admitted version, or activation
procedure. It does carry the public influence policy
`declared-role-match-v0`, which operates over the empty eligible set and
returns `no_admitted_change`. Baseline absence is absence of admitted state,
not absence of an activation policy.

The runtime records:

```text
eligible_versions: empty tuple
result: activation withheld
refusal: no_admitted_change
```

`ActivationWithheld` has the exact considered object as its only new causal
parent. The returned `WithheldDecisionRoot` retains the predecessor,
considered object, withholding result, empty eligible set, and refusal. It
contains no activation handoff, intervention procedure, admitted-version
binding, proposal content, copied candidate text, or ablation reason.

The result is warranted by the public condition and retained lineage, not by
the hidden fact that the harness calls this branch baseline.

## Governed activation

The governed predecessor must be the exact current encounter root whose
predecessor is the eligible admitted root produced by the governed runtime. The
runtime resolves that exact `AdmittedCandidate` capability and its proposal
through the encounter predecessor chain and revalidates the complete admitted-
root snapshot. Semantic projection equality is insufficient.

The considered object contains a one-element `eligible_versions` tuple holding
that exact admitted object. It refuses the ablation branch's semantically equal
admission, copied candidate text, documentary alias `D-G-009`, or an independently
rebuilt admission.

The fixture activator applies only runtime-visible rules:

1. the situation contains `derived_from`;
2. `depends_on_current_authority` is exactly boolean `true`;
3. the admitted scope is exactly “Commitments of derived objects whose
   acceptability depends on the current authoritative source;
   authority-independent validity is excluded,” and the current situation
   declares the included side of that boundary; and
4. the exact admitted version remains eligible at the encounter head.

On success, the runtime records one `ChangeActivated` whose causal parents are
the exact considered object and exact admitted version. It originates one
sealed `ActivationHandoff` with this semantic content:

```text
encounter: exact current positive encounter
considered: exact ActivationConsidered object
selected_admission: exact governed admitted version
proposal: exact proposal reached through that admission
intervention_procedure: revision-check-intervention-v0
intervention_content: exact retained candidate representation from the proposal
selection_reason: derived_from is present and depends_on_current_authority is true
```

The handoff is encounter-local. A procedure name, admitted alias, equal
candidate representation, or caller reconstruction is not the handoff.

Before returning the root, the activation authority places the complete
handoff in an issuer-owned private registry and issues one sealed
`ActivationHandoffBinding`. The binding has no backpointer to the registry,
encounter authority, admitted-root controller, or trajectory state. The
returned `ActivatedDecisionRoot` retains the predecessor, considered object,
activation result, exact admitted and proposal objects, and only that sealed
binding. Later request construction must resolve and consume the exact handoff
through a narrow registry operation once; this contract does not construct the
request.

The full handoff is runtime-visible when the future practice boundary resolves
it. It is not traversable from developmental lineage before that operation.

## Authority and order

1. The exact baseline and governed encounter roots exist and are current.
2. The encounter authority supplies them as one unordered, closed pair with
   snapshot-only verifiers. The activation authority classifies them only from
   runtime-visible condition and retained lineage: one
   `audit_lineage_only-v0` root and one
   `consequence_governance_activation-v0` root with an exact eligible admission.
3. One runtime activation authority is registered for that exact pair.
4. Each runtime resolves its public condition and eligible state from its own
   lineage.
5. In one atomic operation, the runtime constructs `activation considered` and
   its one required result. No durable considered-only head exists.
6. Baseline appends `activation withheld`; governed appends `change activated`
   and originates one activation handoff.
7. Each result returns one exact current decision root and retires its encounter
   predecessor at this layer.
8. The harness witnesses the exact runtime result and joins it to the existing
   positive case assignment in trajectory evidence only.

The harness may schedule and witness. It may not supply the eligible set,
select the admission, choose the refusal, construct the intervention, author a
result, repair a root, or derive the ablation answer.

## Runtime authority and one-shot use

Only one activation authority may claim the unordered pair of exact encounter
roots. Pair intake refuses a third root, duplicate root, ablation root,
caller-selected ordering with semantic meaning, missing public condition,
condition-only governed substitute, or root not issued by the encounter
authority. It uses narrow snapshot-only currentness verifiers and exposes no
trajectory controller, assignment, freeze, comparison group, expected result,
or branch label.

Each encounter root has one decision right. Considered plus result is one
atomic append operation: a successful result consumes the right and makes the
returned decision root current; a failed attempt leaves no considered object
and does not consume it. A second activation authority, second considered
append, second result, result without consideration, considered object without
a result, or result of both kinds for one encounter refuses.

The governed activation handoff has a separate request-consumption right owned
by the private activation registry. It is not consumed by activation
witnessing. The activated root retains only its sealed binding. A snapshot-only
decision-root verifier cannot reach the registry or full handoff. Resetting
caller-visible flags cannot restore either right.

## Trajectory witness

The harness records one witness per result. It checks:

1. the positive case assignment and encounter witness are exact and current;
2. the decision predecessor is the exact witnessed encounter root;
3. the considered append was runtime-authored once from that root;
4. the public formation condition matches retained lineage;
5. baseline has an empty eligible tuple, `no_admitted_change`, and no handoff;
6. governed contains the exact governed admission, proposal, activation result,
   and sealed handoff identity;
7. the complete situation equals the encounter's seven-role projection;
8. no harness-only or extra public field appears; and
9. the two-root witness set contains exactly baseline withholding and governed
   activation for their authorized encounter roots.

The harness may know which trajectory meaning each root has. That mapping stays
in trajectory evidence. The developmental result must be reconstructable from
public condition, retained lineage, and current situation alone.

The witness proves neither request construction nor behavioral influence. It
does not compare actions, consequences, or complete model requests.

## Refusal vectors and ownership

Each refusal begins independently from clean encounter roots and runtime state:

1. Supply a raw mapping, coordinate, alias, caller-created considered object,
   result, handoff, root, binding, verifier, or witness.
2. Use an equal reconstructed, stale, other-run, wrong-head, wrong-authority, or
   already-consumed encounter root.
3. Submit the ablation encounter root or any root containing a replay constraint
   to this two-root boundary.
4. Omit either required root, add a third, duplicate a root, use the wrong
   public conditions, or let hidden trajectory meaning select pair order or
   runtime classification.
5. Use hidden branch, case-family, expected-result, scorer, or ablation-reason
   data to choose eligibility or result.
6. Reopen the foreground delivery, freeze, protocol source, mutable storage, or
   trajectory assignment instead of reading the encounter root.
7. Omit, add, replace, coerce, or change a situation role between encounter and
   consideration.
8. Give baseline an admitted version, activation handoff, intervention,
   proposal content, or any refusal other than `no_admitted_change`.
9. Give governed an empty eligible set, another branch's admission, copied
   candidate text, an ineligible version, or more than one eligible version.
10. Activate when `derived_from` is absent, when
   `depends_on_current_authority` is not exactly true, or outside admitted
   scope.
11. Construct intervention content independently instead of reading it through
    the exact admission-to-proposal chain.
12. Emit a result without consideration, retain consideration without a result,
    emit both activation and withholding, emit neither result, or create more
    than one considered append for an encounter.
13. Reuse a considered object, result identity, decision root, or activation
    handoff across encounters.
14. Reset a flag, register a second authority, or reuse an encounter predecessor
    after a successful decision.
15. Mutate or replace any predecessor, admitted object, proposal, considered
    object, result, binding, handoff, or returned root after validation.
16. Let the harness author, normalize, repair, replace, or precompute runtime
    objects or decisions.
17. Witness partial eligible state, ignore extra fields, compare full requests,
    or accept an incomplete or duplicate two-root witness set.
18. Treat either witness as proof that a model request was constructed, an
    intervention affected action, or formation occurred.

The encounter-opening authority owns predecessor identity, currentness, closed
pair issuance, and ablation-root exclusion. The
runtime activation authority owns condition resolution, eligible-set
construction, considered and result authorship, exact admitted/proposal
selection, decision linearity, handoff issuance, and returned-root refusals.
The future practice boundary owns activation-handoff request consumption. The
harness owns assignment joins, witness completeness, comparison scope, and
hidden-information refusals.

## Implementation gate

Two independent cold readers reconstructed one compatible two-root object,
including the reason ablation is excluded, exact condition and eligible inputs,
baseline absence, governed lineage identity, applicability decision, activation
handoff, authority split, two separate one-shot rights, witness scope, and
refusal ownership. Code-facing review then confirmed that the existing
encounter and admitted-root capabilities could enforce the boundary without
exposing harness state.

The implemented fixture-local slice preserves the sealed handoff binding,
private registry, snapshot-only decision-root verifier, label-blind pair
intake, and atomic considered-plus-result operation above. The combined suite
passes 117 deterministic tests. Post-build review found one equal-lineage
substitution through mutable cached decision inputs; the repaired decision use
now revalidates its exact condition, admission, and proposal against both its
intake snapshot and encounter verifier before every append. Independent recheck
reproduced that attack and returned `PASS`.

## Unselected

This contract does not select:

- activation, withholding, or decision receipt bytes;
- a general activation service, lifecycle state machine, or lineage schema;
- constrained replay traversal or an ablation eligible-set result;
- model-request or intervention serialization;
- model invocation, action, consequence, experience closure, correction,
  suspension, revocation, scoring, or costs; or
- any transfer, causal, learning, or formation finding.

## Acceptance and loses-conditions

This contract is sufficient only if independent readers reconstruct one
baseline withheld decision, one governed activated decision, one exact current
root for each, one encounter-local activation handoff, no ablation result, and
the same refusal outcomes.

It loses if equal candidate text can replace the exact admitted lineage, if
baseline receives an intervention, if hidden assignment chooses a runtime
result, if one encounter produces two decisions, if one activation handoff can
enter two requests, or if an ablation answer is returned without runtime-derived
constrained eligibility. It also loses if a decision witness is treated as
evidence of behavioral influence or formation; if the harness authors or
repairs a decision; if a result skips consideration; if a durable
considered-only head exists, the encounter predecessor remains usable for
another decision, or a second authority or flag reset restores either one-shot
right.
