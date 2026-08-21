# Same-request variation evidence

This directory contains a 32-call repeatability contact with the exact Qwen
requests retained by the completed
[unselected-lineage contact](../unselected-lineage-behavior-contact-20260819-contact/README.md).
The contact completed on 2026-08-19. One of the four requests produced two
different actions. The other three produced one action each across all eight
repeats.

## Outcome

All 32 logical calls completed in 32 physical attempts. Every response had
HTTP status 200, valid JSON, and one allowed action. No call was retried.

The runner repeated four byte-identical requests eight times each. It
interleaved them so that the same request did not run eight times in a row.

| Source request | Why it was selected | Eight repeated actions |
| --- | --- | --- |
| `iv077` | The request behind the earlier byte-identical disagreement | 7 originally wrong, 1 originally correct |
| `iv087` | An originally incorrect request | 8 originally incorrect |
| `iv088` | An originally correct non-hold request | 8 originally correct |
| `iv089` | An originally correct hold request | 8 correct holds |

For `iv077`, the first seven repeats returned
`c49684e2926eb307e30d`. The eighth returned
`fbffc30e5a9d59b94e52`. These are the same two actions returned by the
byte-identical no-persistence and ablation calls in the earlier packet. The
request bytes and their SHA-256 hash were unchanged across every repeat:

```text
69839aa5bc63a2aed55a358e862dec8f0f6139fd7b9e6dd38b783c0216ec98ba
```

The other three requests had one observed action each. That does not prove
that they are deterministic. Eight draws can miss a less common alternative.

## What this resolves

The earlier unselected-lineage contact had only one apparent branch difference.
Its exact-request control also disagreed once, so the contact could not tell a
condition effect from ordinary call variation. This repeatability contact
reproduced both actions from that control request without changing its input.

The earlier one-cell difference therefore remains non-attributable. It does
not show that raw experience, authored material, governance, ablation, or a
static instruction caused the changed action. The result also does not show
that every request varies at the same rate. Variation was observed for one of
four selected requests under eight repeats each.

The next developmental comparison should compare repeated action distributions
within each branch and case. A single draw per branch cannot support a causal
interpretation when a relevant request can return both actions on its own.

## Integrity and cost

- Model: `ai/qwen3:14B-Q6_K`
- Artifact digest:
  `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Protocol: `same-request-variation-v1`
- Logical calls: 32/32
- Physical attempts: 32/36
- HTTP 200 responses: 32
- Retries: 0
- Available valid actions: 32
- Prompt tokens reported by the provider: 11,424
- Completion tokens reported by the provider: 712
- Elapsed packet time: about 31 seconds

The directory contains the canonical packet plus the exact request, response,
and metadata files for every attempt. The terminal verdicts remain:

```json
{"formation_verdict":null,"validation_verdict":null}
```

This was a repeatability measurement, not a developmental comparison or a
Formation validation.
