# Distributional developmental comparison evidence

This directory contains the completed 98-call comparison of authored delivery,
authored ablation, raw occurrence persistence, and a static family rule. The
contact used three fresh later cases and repeated every branch-case request
eight times. It completed on 2026-08-19.

## Outcome

All four conditions returned the same action on every later case. There was no
condition-level variation across 96 later calls.

| Later case | Correct action counts in each condition | Observed behavior |
| --- | ---: | --- |
| Same family, target above | 0/8 | First displayed control on every call |
| Same family, target below | 0/8 | Second displayed control on every call |
| Opposite-profile family, target above | 8/8 | First displayed control on every call |

Every comparison with authored ablation had total variation distance `0.0`.
Authored delivery, raw persistence, and the static instruction each had a
correct-action delta of zero on all three cases.

The acquisition call chose the first displayed control while the target was
above the current position. The environment applied it, moved the position
down, and reported that the selected first slot decreased position. The
authored guidance was:

> When the device position is near the target but has not yet reached it,
> prioritize the action that aligns with the movement direction indicated by
> the position change, while considering the available actions on the device.

This guidance did not state the controller-family mapping. The static condition
did state it exactly: for the experienced family, the second displayed control
increases position and the first decreases it. Even that condition produced
the same actions as empty delivery.

## What this resolves

Repeating each request removed the sampling ambiguity that affected the prior
single-draw comparison. Under this packet, there is no observed distributional
effect to attribute. The model followed target direction and displayed order:
it chose the first control for upward targets and the second for downward
targets. Delivered material did not change that pattern.

This does not show that persisted experience or authored guidance is generally
inert. The action prompt exposed `retained_material` as a JSON field but did not
explicitly tell the model how to consume that field. The static positive
control's failure therefore leaves an interface-engagement problem before
another developmental mechanism comparison.

The next bounded test should vary only a generic retained-material consumption
instruction and the presence of the static family rule. It should check both
same-family directions and an opposite-profile non-transfer family. That test
would measure whether the interface can make rule content influential without
embedding later action tokens or answers.

## Integrity and cost

- Model: `ai/qwen3:14B-Q6_K`
- Artifact digest:
  `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Protocol: `distributional-developmental-comparison-v1`
- Logical calls: 98/98
- Physical attempts: 98/102
- HTTP 200 responses: 98
- Retries: 0
- Valid later actions: 96/96
- Prompt tokens reported by the provider: 35,426
- Completion tokens reported by the provider: 2,658
- Elapsed packet time: about 120 seconds

The directory contains the provider receipt, canonical specimen and packet,
and the exact request, response, and metadata files for every attempt. The
runner replayed the packet from those raw files before exiting successfully.
The terminal verdicts remain:

```json
{"formation_verdict":null,"validation_verdict":null}
```

This was an exploratory interface and behavior comparison, not a Formation
validation.
