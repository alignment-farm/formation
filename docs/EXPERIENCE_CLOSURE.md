# Positive experience-closure contract

Status: **fixture-local semantic contract; reconstruction stable, code slice
blocked by predecessors**.

Purpose: define the final occurrence append for the two exact positive practice
encounters. Closure retains which encounter and consequence belong to one
experience. It adds no interpretation of what the experience means or where it
should influence later action.

## Named semantic need

After consequence intake, each positive branch has an encounter occurrence and
a consequence occurrence joined through invocation, commitment, and external
result lineage. The practitioner needs one explicit boundary saying that this
encounter is complete enough to retain as an experience.

```text
exact encounter opened + exact consequence observed
  -> runtime closes their occurrence interval
  -> exact retained experience root
```

Closure is containment, not compression. It does not replace either occurrence
with a summary.

## Closed input pair

One runtime closure authority accepts the unordered exact current pair of
`WithheldConsequenceRoot` and `ActivatedConsequenceRoot` issued by positive
consequence intake. For each root it follows exact retained lineage back to one
`EncounterOpenedAppend` occurrence. It reaches that append only through the
historical predecessor and causal links retained from the consequence root. It
may not reopen encounter authority or live storage, require the retired
encounter root to remain current, or substitute a reconstructed encounter
capability. That append must be the same encounter whose considered decision,
activation or withholding, request, invocation, action, environment result, and
consequence form the current chain.

The closure authority receives public policy `close-complete-occurrence-v0`.
It receives no branch label, case family, expected result, scorer verdict,
candidate lesson, applicability scope, success category, comparison, or claim
about whether an intervention helped.

The ablation branch remains excluded until constrained replay can produce its
later practice path.

## Experience-closed event

For each exact consequence root, the runtime records one immutable
`ExperienceClosed` event:

```text
run: current fixture run
policy: close-complete-occurrence-v0
encounter: exact EncounterOpenedAppend occurrence from the retained chain
consequence: exact ConsequenceObserved occurrence at the current head
status: closed
```

`status: closed` means only that the selected occurrence interval contains its
required encounter and directly observed consequence. It does not mean that the
result was accepted, desirable, correctly interpreted, uncontested forever, or
useful beyond this encounter.

The event retains exact occurrences rather than copied situation, action,
observation, disposition, revision, intervention, or candidate fields. Those
facts remain available through their originating lineage objects. Closure does
not author a synopsis.

The exact `EncounterOpenedAppend` and `ConsequenceObserved` are the event's two
causal parents, matching the fixture's acquisition closure pattern. The returned
`WithheldExperienceRoot` or `ActivatedExperienceRoot` retains the exact
consequence head as its linear predecessor and the exact `ExperienceClosed`
event. It becomes the current developmental head for its branch. Baseline and
governed roots are different identities even though they use the same closure
policy.

## Completeness rule

Fixture-local closure requires exactly one causally connected instance of each
occurrence in this order:

```text
encounter opened
  -> activation considered
  -> activation withheld | change activated
  -> model invoked
  -> action committed
  -> consequence observed
  -> experience closed
```

The closure authority validates actual retained causal-parent links. The
withheld or activated decision must cite the exact preceding considered event;
every later occurrence must descend from that exact decision. It does not infer
completeness from event names, counts, authored fixture coordinates, or an
expected branch path. The baseline chain must contain exact intervention
absence; the governed chain must contain its exact activated handoff lineage.
Those differences are preserved, not normalized. A validator that recognizes
the authored kind sequence without walking these retained identities refuses.

This positive slice selects only directly observed consequences. General
Formation still requires missing, delayed, partial, and contested states; those
may remain open or use a separately declared closure policy. This contract does
not silently classify them as complete.

## Atomicity and one-shot use

Each consequence root has one closure right. Success atomically records one
event and returns one current experience root. Failure returns neither and does
not consume the right. Resetting guards cannot restore a spent right. One
consequence cannot close twice, two consequences cannot be merged into one
event, and one encounter cannot be closed under both positive roots.

Historical validation of an experience root remains distinct from checking
whether its consequence predecessor is still current at the intake layer.

## Authority and witness

The runtime alone records closure from runtime-visible occurrence lineage. The
environment does not decide that the experience is complete. The model does not
summarize or interpret it. The harness may witness exact joins after closure but
cannot insert missing occurrences, select a lesson, or mark a result successful.

One trajectory witness checks the exact consequence witness and predecessor,
the exact encounter-to-consequence chain, declared closure policy, event and
root identity, and the complete unordered pair of one withheld and one activated
experience root.

The witness proves only that the runtime retained two complete positive
occurrence intervals. It does not prove memory use, acquisition, transfer,
selectivity, revision, causal contribution, or net value.

## Refusal vectors

Each refusal starts from clean consequence roots and unused closure rights:

1. Raw, caller-created, reconstructed, stale, wrong-head, other-run, or
   wrong-authority consequence, encounter, event, root, verifier, or witness.
2. Missing, duplicate, third, ablation, or order-classified pair input.
3. A consequence joined to the wrong encounter, considered decision,
   activation or withholding, invocation, action, result, run, or branch-local
   lineage.
4. Missing, duplicate, reordered, disconnected, or independently reconstructed
   occurrence in the required causal chain.
5. A closure policy other than `close-complete-occurrence-v0`, or one selected
   from hidden assignment or expected outcome.
6. A copied summary, situation, intervention, action, result, observation,
   disposition, or revision field in place of exact occurrence identity.
7. Normalizing away baseline intervention absence or governed activation
   identity to make the two experiences equal-looking.
8. Calling a missing, delayed, partial, or contested consequence complete under
   this positive directly-observed policy.
9. Closing one consequence twice, merging branches, restoring a right by
   resetting guards, or registering a second closure authority.
10. Mutating or replacing any retained occurrence, event, root, or witness
    after validation.
11. Letting the environment, model, harness, oracle, or scorer record closure
    or repair its lineage.
12. Treating closure as a lesson, applicability claim, admission, activation,
    score, causal attribution, behavioral change, or formation finding.

The consequence-intake authority owns predecessor identity and pair issuance.
The runtime closure authority owns chain validation, event recording, linearity,
and current experience roots. The harness owns witness joins and completeness.

## Implementation gate

Two independent final cold readers reconstructed the same retained encounter,
considered-decision sequence, dual causal parents, linear predecessor, closure
meaning, one-shot authority, witnesses, refusals, and loses-conditions. An
earlier reconstruction exposed and repaired a missing `activation considered`
event, ambiguous encounter reachability, and failure to name the acquisition-
matching dual-parent shape. The semantic gate is closed.

No code is licensed. Environment application and consequence intake are code-
blocked, so no live consequence roots exist to close. Convergence establishes
only the meaning of closure; it does not override either missing predecessor
computation.

## Unselected

This contract does not select experience serialization, summary generation,
retrieval, candidate interpretation, applicability inference, missing-result
closure, correction, governance, scoring, constrained replay, or any formation
finding.

## Acceptance and loses-conditions

This contract is sufficient only if independent readers reconstruct one
baseline and one governed retained experience, each containing its exact
encounter and exact consequence chain, with branch-local differences preserved,
no ablation closure, and no added interpretation or verdict.

It loses if closure can be inferred from fixture coordinates instead of actual
lineage; if a summary replaces occurrence identity; if disconnected events can
be joined; if the harness repairs or closes runtime history; if one consequence
closes twice; or if a retained experience is treated as evidence that anything
was learned, transferred, or improved.
