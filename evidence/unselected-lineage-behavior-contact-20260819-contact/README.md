# Unselected-lineage behavior contact evidence

This directory contains the completed Qwen3 14B contact under the
[unselected-lineage charter](../../docs/UNSELECTED_LINEAGE_EXPLORATORY_CHARTER.md).
The packet completed on 2026-08-19. It found one later-action difference, but
the packet's byte-identical control reproduced a difference of the same size.
The result therefore does not attribute behavioral change to experience,
authorship, or Formation.

## Outcome

The disposable interface passed. All 109 logical calls completed in 109
physical attempts, with no retry or HTTP error. Every model response supplied
available content. All 100 scored acquisition and later actions used valid JSON
and an allowed action, and the environment applied every proposal.

The four acquisition actions were correct in two blocks and wrong in two. The
model generally chose the first displayed control when the target was above the
current position and the second when it was below. That public-state heuristic
ignored which displayed slot actually increased or decreased position for each
opaque controller family.

Across the 16 later cases per branch, correct actions were:

| Branch | Correct |
| --- | ---: |
| No persistence | 11/16 |
| Raw persistence | 10/16 |
| Result-withheld authorship | 10/16 |
| Result-exposed authorship | 11/16 |
| Ablation | 10/16 |
| Static instruction | 11/16 |

Those totals come from only one differing cell. In the other 15 cases, all six
branches proposed the same action.

## The one differing cell

The difference occurred in the block 3 transfer case. Raw persistence,
result-withheld authorship, and ablation chose the wrong first displayed
control. Result-exposed authorship, static instruction, and no persistence
chose the correct second displayed control.

This is not an attributable authored-intermediate effect. No persistence and
ablation had exactly the same request bytes and request hash:

```text
69839aa5bc63a2aed55a358e862dec8f0f6139fd7b9e6dd38b783c0216ec98ba
```

Despite that identity, ablation returned the wrong action at `iv077` and no
persistence returned the correct action at `iv085`. Across all 16 matched
cases, the two byte-identical conditions agreed 15 times and differed once.
The packet therefore directly observed cold-call variation large enough to
explain its only apparent branch effect.

The result-exposed authored text for that block was:

> If the device position is one greater than the target and the selected slot
> is second, consider increasing movement in the same direction to approach the
> target.

It mentioned the observed second slot and increasing movement, but its advice
to increase when position was already above the target was not a sound reusable
action rule. The frozen static instruction stated the controller mapping
directly. Both conditions nevertheless returned the same action as no
persistence in every later case.

## What this says about the research question

The contact does not show that an experience, its consequence, and a runtime-
authored interpretation caused a later behavioral difference beyond raw
persistence or a static lesson.

It also does not show that the mechanism is inert. The packet had only one draw
per branch and case, while an exact-request control demonstrated output
variation. The immediate empirical problem is now clearer: before a one-cell
condition difference can carry causal weight, the experiment must measure or
control same-request variation at the comparison level.

The authored intermediates also varied in quality. Several were generic or
situation-bound, and none produced a behavioral pattern distinct from both no
persistence and static instruction. That is an observed property of these
eight outputs, not an admission failure.

## Integrity and cost

- Model: `ai/qwen3:14B-Q6_K`
- Artifact digest:
  `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Logical calls: 109/109
- Physical attempts: 109/112
- HTTP 200 responses: 109
- Retries: 0
- Prompt tokens reported by the provider: 36,460
- Completion tokens reported by the provider: 2,615
- Elapsed packet time: about 128 seconds
- Later assignments: 96/96

The directory contains 331 machine files in addition to this account: the
provider receipt, canonical manifest and witness, packet projection, and exact
request, response, and metadata files for every attempt. The runner regenerated
the packet from retained raw responses and exited successfully, which means its
section-by-section integrity replay passed.

The terminal verdicts remain:

```json
{"formation_verdict":null,"validation_verdict":null}
```

No rerun or stronger claim follows from this account.
