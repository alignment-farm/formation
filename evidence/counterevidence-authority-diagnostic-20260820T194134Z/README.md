# Counterevidence authority diagnostic

## Main result

The deterministic diagnostic conforms. The completed longer-lineage evidence
contains four complete action-and-consequence occurrences that contradict the
current record's claim for the selected control. Three of those actions also
follow the current record's target policy. One does not.

An observation-grounded governor would admit all four already composed-
admitted proposals. An action-attributed governor would admit three and
quarantine one.

This makes the policy boundary computable from runtime-visible facts. It does
not change the longer-lineage experiment's frozen null verdict.

## What the diagnostic reconstructed

For each third occurrence, the diagnostic read the exact retained version-2
record, source position and target, allowed actions, committed action, and
environment movement. It then reconstructed the selected slot and the action
that version 2 recommended for the target.

| Check | Result |
| --- | ---: |
| Complete selected-control and movement sources | 4/4 |
| Movements contradicting the selected-effect claim | 4/4 |
| Reconstructed action-attribution labels | 4/4 |
| Observation-grounded admissions | 4/4 |
| Action-attributed admissions | 3/4 |

In the differing lineage, version 2 recommended the first control to decrease
position. The participant selected the second control instead. The environment
reported that the second control decreased position, contradicting version 2's
claim that it would increase position.

The occurrence therefore supports an observational correction of the selected-
effect claim. It does not support the claim that version 2 caused the control
choice.

## Why the distinction matters

The two governors preserve different causal meanings:

- Observation-grounded revision can learn from deliberate exploration or an
  action chosen for reasons other than the current target policy.
- Action-attributed revision changes state only when the current retained
  record can also be credited with guiding the source action.

Neither policy uses a hidden answer or later score. The difference is whether
action attribution is part of the admission warrant.

A later experiment can now make the action origin prospective: one ordinary
target-directed source and one explicitly exploratory source. It can compare
both governors without relying on accidental model noncompliance.

## Limits

This diagnostic made no model calls and introduced no new experience. It shows
only that the two policies are distinct and exactly computable on the retained
packet. It does not show which policy improves later action, which should be the
default governor, or whether either produces Formation.

## Audit details

- Source packet SHA-256: `1ce32ea264ff0631c6c45a4a73d6b5fee423b68540acb6367d53b6a5158933c2`
- Source specimen SHA-256: `b795ab2468b5c4cb5fb9f1429fa0eb14841b1bb3b1267ffc08c1cf5eb46fb10d`
- Frozen diagnostic specification SHA-256: `24bb4b0e2c25d9747cf26205f6db0099488d46a1a8ec703581d30de5638070ea`
- Packet SHA-256: `7edaf10540d53d643c332a36b960fc995366d7949f3cbf38008397bc10caa407`
- Model calls: 0
- Diagnostic verdict: `conforms`
- Formation verdict: `null`
- Replay: exact deterministic reconstruction

The four reconstructed receipts and both policy decisions are in
[packet.json](packet.json).
