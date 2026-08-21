# Candidate non-transfer sweep evidence

This directory contains the completed 96-call sweep of the two result-exposed
model-authored candidates from the null validation. Empty delivery and each
ungated candidate ran four times on eight fresh nonmatching controller
families. Four cases had upward targets and four had downward targets. The
contact completed on 2026-08-20.

## Outcome

Empty delivery was correct on all 32 calls. Both candidates were harmless on
all upward cases and harmful on every downward case.

| Condition | Upward non-transfer | Downward non-transfer |
| --- | ---: | ---: |
| Empty | 16/16 | 16/16 |
| Candidate A | 16/16 | 0/16 |
| Candidate B | 16/16 | 1/16 |

Candidate B varied once on one downward request; every other request produced
one action across all four repeats. All 96 calls returned valid actions.

## What this says

The model-authored family scope did not reliably prevent negative transfer.
Across these fresh cases, scope adherence depended on target direction. The
candidate stayed silent for upward targets but overrode the correct baseline
for downward targets, even though every current controller family differed
from the family named in the candidate.

This explains why the frozen validation could not credit governance: its two
non-transfer cases both used upward targets, where ungated authorship happened
to be selective. The validation verdict remains null because its cases and
scorer were frozen. The sweep is new exploratory evidence, not a retroactive
repair.

A fresh successor may now test the named governance edge prospectively. It
must include both non-transfer directions, preserve matching-family benefit,
and compare exact candidate ablation, ungated delivery, and exact-family-scoped
delivery in both source lineages.

## Integrity and cost

- Model: `ai/qwen3:14B-Q6_K`
- Artifact digest:
  `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Protocol: `candidate-nontransfer-sweep-v1`
- Logical calls: 96/96
- Physical attempts: 96/100
- HTTP 200 responses: 96
- Retries: 0
- Valid actions: 96/96
- Prompt tokens reported by the provider: 30,968
- Completion tokens reported by the provider: 2,686
- Elapsed packet time: about 109 seconds

The runner replayed the packet from retained raw requests and responses before
exiting. Formation and validation verdicts remain null.
