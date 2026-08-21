# Canonical mapping scope-gate validation evidence

This directory contains the completed successor validation governed by
[the frozen scope-gate specification](../../docs/CANONICAL_MAPPING_SCOPE_GATE_VALIDATION.md).
The packet completed on 2026-08-20 with a computed `not_engaged` verdict. The
Formation verdict remains null.

## Outcome

The exact-family gate behaved as intended on the prospective non-transfer
cases:

- Scoped and ablated delivery scored 8/8 on downward non-transfer.
- Ungated delivery scored 0/8 on downward non-transfer.
- All three conditions scored 8/8 on upward non-transfer.

The candidate effect did not reliably reproduce on matching-family upward
cases:

| World | Ablation | Ungated | Scoped |
| --- | ---: | ---: | ---: |
| A, target above | 0/4 | 0/4 | 0/4 |
| A, target below | 0/4 | 4/4 | 4/4 |
| B, target above | 0/4 | 2/4 | 2/4 |
| B, target below | 0/4 | 4/4 | 4/4 |

All 96 calls returned valid actions. Only the World B upward candidate request
varied, returning each control twice. Every other condition-case request had
one action across four repeats.

## Why the verdict is not engaged

The frozen scorer required ungated candidate delivery to score at least 3/4 on
both matching-family directions in both source lineages before the scope gate
could be validated. The two upward cells failed that prerequisite. The packet
therefore cannot claim that the gate preserved a reliable candidate benefit,
even though it prevented the predeclared downward non-transfer harm.

This result does not revise the earlier null validation. It shows a narrower
fact: exact-family gating can remove a known negative-transfer path, while the
natural-language candidate representation remains too case-dependent for the
whole later-action mechanism to engage reliably.

The next empirical problem is representation robustness. Before another
governance validation, a model-authored mapping must influence both target
directions across prospective devices without depending strongly on action
tokens or case surface. Any new representation still has to be authored from
consequence rather than supplied by the harness.

## Integrity and cost

- Model: `ai/qwen3:14B-Q6_K`
- Artifact digest:
  `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Protocol: `canonical-mapping-scope-gate-validation-v1`
- Logical calls: 96/96
- Physical attempts: 96/100
- HTTP 200 responses: 96
- Retries: 0
- Valid actions: 96/96
- Prompt tokens reported by the provider: 30,324
- Completion tokens reported by the provider: 2,589
- Elapsed packet time: about 101 seconds
- Scope-gate validation verdict: `not_engaged`
- Formation verdict: null

The runner replayed the packet and verdict from retained raw requests and
responses before exiting.
