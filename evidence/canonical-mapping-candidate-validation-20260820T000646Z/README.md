# Canonical mapping candidate validation evidence

This directory contains the completed two-world candidate validation governed
by [the frozen specification](../../docs/CANONICAL_MAPPING_CANDIDATE_VALIDATION.md).
The packet completed on 2026-08-20 with a computed `null` verdict for the
acquisition-transfer-selectivity mechanism. The Formation verdict remains null.

## Outcome

Both acquisition actions were wrong and received informative environment
results. World A observed that its first slot decreased position. World B
observed that its second slot increased position.

In both worlds, result-exposed authorship produced the exact correct canonical
mapping. Result-withheld authorship produced the exact opposite mapping. The
later distributions were fully separated:

- Governed, ungated authored, and oracle-static delivery scored 24/24 across
  the four same-family transfer cells.
- Cold, raw occurrence, consequence-withheld governed, and delivery ablation
  scored 0/24 on those cells.
- Every branch scored 12/12 on the two non-transfer cells.

All 252 later calls returned valid actions. Every branch-case distribution was
stable across its six repeated calls.

## Why the frozen verdict is null

The validation required the governed branch to outperform ungated authored
delivery by at least four actions on each non-transfer case. That criterion did
not pass. Ungated authorship and governed delivery were both 6/6 correct in
both worlds, so the exact-family gate had no behavioral effect.

The verdict is not `not_engaged`: exposed authorship, the static diagnostic,
and the action interface all performed their assigned responsibilities. It is
not `harmful`: governed delivery caused no non-transfer loss. The mechanism
engaged and produced benefit, but it did not beat the simpler authored lesson
on the frozen selectivity comparison. Under the prospective scorer, that is
`null`.

## What remains supported as a bounded observation

The packet gives strong evidence for consequence-dependent authored content in
these two worlds. With the external result exposed, both model-authored
mappings were correct and their delivery changed all 24 transfer actions. With
the same occurrence but result withheld, both mappings reversed and changed no
transfer action beyond the cold baseline. Raw occurrence also had no effect.

That observation does not rescue the governed candidate validation. Formation
requires the governed system to add value beyond the simpler authored lesson.
The exact-family gate cannot receive causal credit when ungated delivery is
already selective.

The remaining empirical problem is inconsistent self-scoping. Ungated delivery
caused 8/8 negative-transfer errors in the preceding canonical-authorship
contact, but it caused no error in the continuation or either validation world.
A fresh multi-case non-transfer sweep is needed before another governance
validation is justified.

## Integrity and cost

- Model: `ai/qwen3:14B-Q6_K`
- Artifact digest:
  `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Protocol: `canonical-mapping-candidate-validation-v1`
- Logical calls: 258/258
- Physical attempts: 258/266
- HTTP 200 responses: 258
- Retries: 0
- Valid later actions: 252/252
- Prompt tokens reported by the provider: 87,542
- Completion tokens reported by the provider: 7,213
- Elapsed packet time: about 303 seconds
- Candidate-validation verdict: `null`
- Formation verdict: null

The directory contains the provider receipt, frozen specimen and packet, and
the exact request, response, and metadata files for every attempt. The runner
regenerated the packet and verdict from raw evidence before exiting.
