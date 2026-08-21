# Retained-material consumption trial evidence

This directory contains the completed 96-call interface trial. It crossed an
implicit or explicit retained-material consumption instruction with empty or
static retained content. Each of four conditions ran eight times on two fresh
same-family cases and one opposite-profile non-transfer case. The contact
completed on 2026-08-19.

## Outcome

The generic consumption instruction changed no action distribution. Empty
requests were identical across the implicit and explicit interfaces. Static
requests were also identical across those interfaces.

The static family rule did change one case:

| Case | Empty | Static | Static minus empty |
| --- | ---: | ---: | ---: |
| Same family, target above | 0/8 correct | 8/8 correct | +8 |
| Same family, target below | 0/8 correct | 0/8 correct | 0 |
| Other family, target above | 8/8 correct | 8/8 correct | 0 |

The upward same-family action distributions were disjoint, with total
variation distance `1.0`. Every other content comparison had distance `0.0`.
All 96 calls returned one valid allowed action.

The static rule said that the second displayed control increases position and
the first decreases it. With empty material, the model chose the first control
for an upward target and the second for a downward target. With the static
rule, it chose the second control in both cases. That repaired the upward case
but left the downward case wrong.

## What this says

Retained content can change a repeated action distribution under this interface.
The effect was family-selective in this packet: a rule scoped to one controller
family did not change the other-family case.

The result does not yet show that the model applied the complete mapping. The
rule mentioned the second slot first, and the static conditions chose that slot
in both target directions. A simpler account is that the model copied the
first-mentioned slot from the retained sentence. The added generic instruction
does not explain the effect because the implicit and explicit static conditions
were identical.

The next experiment should reverse the order of the two equivalent mapping
clauses. If the chosen slot follows mention order, the surface form controls the
action. If both wordings support the same direction-sensitive mapping, the
model is using the relation rather than a slot-copy shortcut.

This is an interface-level candidate phenomenon. It is not acquisition,
transfer, or Formation: the rule was authored by the harness and supplied in
the same request as the action.

## Integrity and cost

- Model: `ai/qwen3:14B-Q6_K`
- Artifact digest:
  `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Protocol: `retained-material-consumption-trial-v1`
- Logical calls: 96/96
- Physical attempts: 96/100
- HTTP 200 responses: 96
- Retries: 0
- Valid actions: 96/96
- Prompt tokens reported by the provider: 33,056
- Completion tokens reported by the provider: 2,524
- Elapsed packet time: about 109 seconds

The directory contains the provider receipt, canonical specimen and packet,
and the exact request, response, and metadata files for every attempt. The
runner replayed the packet from raw evidence before exiting successfully. The
terminal verdicts remain:

```json
{"formation_verdict":null,"validation_verdict":null}
```
