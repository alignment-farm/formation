# Canonical mapping authorship evidence

This directory contains the completed 98-call developmental contact. One
acquisition action received an environment-issued result. The model then
authored one retained mapping in a required first-then-second sentence form.
The exact returned text was either delivered or ablated and was compared with
raw occurrence persistence and the exact static mapping across three fresh
later cases with eight repeats each. The contact completed on 2026-08-19.

## Outcome

The acquisition call chose the first displayed control for an upward target.
The environment applied it, moved the position down, and reported that the
first slot decreased position. From that record, the model authored:

> For controller family e7a28519096c260d5a73, the first displayed control
> decreases position and the second displayed control increases position.

That sentence was byte-identical to the frozen static mapping. The runner did
not repair or rewrite it.

Delivered authorship and the static mapping produced identical later actions.
Authored ablation and raw persistence also produced identical actions.

| Case | Ablation | Raw occurrence | Authored delivery | Static mapping |
| --- | ---: | ---: | ---: | ---: |
| Same family, target above | 0/8 | 0/8 | 8/8 | 8/8 |
| Same family, target below | 0/8 | 0/8 | 8/8 | 8/8 |
| Other family, target above | 8/8 | 8/8 | 0/8 | 0/8 |

Every authored-delivery comparison with ablation had total variation distance
`1.0`. All 96 later requests returned a valid action, and every branch-case
distribution was stable across eight repeats.

## What this says

The contact produced a candidate experience-to-authorship-to-action path. The
model used the acquisition consequence to fill a canonical family mapping, and
the exact authored sentence changed action on new devices from that family in
both target directions. Raw occurrence alone did not reproduce the effect.
Authored ablation supplies the same cold-model and lineage history without
delivering the candidate, so the later difference is attributable to candidate
delivery within this packet.

The candidate was not selective. When delivered to a different controller
family with the opposite mapping, it overrode the correct baseline action and
made all eight calls wrong. This complete negative transfer prevents a
Formation claim. The contact also has only one acquisition and one authorship
draw, so it does not validate consequence-dependent authorship.

The next test should continue this exact candidate onto prospective new devices
and compare three delivery policies: ablate it everywhere, deliver it
everywhere, or deliver it only when the public controller family exactly
matches the family of the acquisition occurrence. That gate uses a public
structural key and does not inspect or rewrite the model-authored mapping.

## Integrity and cost

- Model: `ai/qwen3:14B-Q6_K`
- Artifact digest:
  `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Protocol: `canonical-mapping-authorship-contact-v1`
- Logical calls: 98/98
- Physical attempts: 98/102
- HTTP 200 responses: 98
- Retries: 0
- Valid later actions: 96/96
- Prompt tokens reported by the provider: 35,410
- Completion tokens reported by the provider: 2,703
- Elapsed packet time: about 117 seconds

The directory contains the provider receipt, canonical specimen and packet,
and the exact request, response, and metadata files for every attempt. The
runner replayed the packet from raw evidence before exiting successfully. The
terminal verdicts remain:

```json
{"formation_verdict":null,"validation_verdict":null}
```
