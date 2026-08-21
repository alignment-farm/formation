# Counterevidence authority diagnostic

Status: **frozen deterministic diagnostic**.

## Question

Can the runtime distinguish two counterevidence policies using only the exact
retained record, committed action, target, and environment result from the
completed longer-lineage packet?

The source packet is
`evidence/selective-longer-lineage-revision-20260820T192314Z/packet.json` with
SHA-256
`1ce32ea264ff0631c6c45a4a73d6b5fee423b68540acb6367d53b6a5158933c2`.
Its specimen has SHA-256
`b795ab2468b5c4cb5fb9f1429fa0eb14841b1bb3b1267ffc08c1cf5eb46fb10d`.

## Two policies

The observation-grounded policy accepts an already composed-admitted proposal
when the source contains a selected control and movement, and the movement
contradicts the current record's claim for that selected control.

The action-attributed policy requires the same facts and also requires the
committed action to equal the action recommended by the current record for the
source target.

Both policies use runtime-visible lineage facts. Neither receives a later
answer, score, branch label, or counterfactual outcome.

## Deterministic checks

For each of the four third occurrences, the diagnostic must reconstruct:

- the selected slot from the committed action and allowed actions;
- the selected-effect claim from the exact parent version-2 record;
- the observed movement from the environment result;
- whether the result contradicts the selected-effect claim;
- the target-directed action recommended by version 2; and
- each policy's admission decision.

The diagnostic conforms only if all four sources are complete, all four
selected-effect claims are contradicted, the observation-grounded policy admits
four, the action-attributed policy admits three, and the reconstructed action-
attribution labels match the retained scorer labels.

This result can prove that the two policies are computable and different on the
retained occurrences. It cannot show which policy produces better development
or change the completed experiment's null verdict.

## Evidence

The diagnostic makes no model calls. It writes its packet under
`evidence/counterevidence-authority-diagnostic-<run-id>/` and verifies exact
deterministic replay before successful exit. Formation remains null.
