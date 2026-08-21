# Two lesson forms worked across every matching device

## Main point

We supplied the model with a correct lesson and tested whether later cold calls
could use it. The lesson was written as a sentence, a table, or a simple policy.

The sentence and table each produced the correct action on all 32 matching
calls. With no lesson, the same model was correct on none of those calls. The
policy produced only 6 correct actions out of 32.

The sentence and table also changed some actions in unrelated controller
families. They are usable delivery forms, but they still need the family gate
to keep the lesson from acting in the wrong place.

This was an interface test. The harness supplied the correct lesson, so the
result is not evidence that the model learned from experience. Formation
remains null.

## The task

Each device showed two controls with meaningless names. The first moved a
number down by one. The second moved it up by one. The model had to choose the
control that moved the number toward a target.

Four controller families used fresh device names and fresh action strings.
Each family had one target above the current number and one below it. Every
request was repeated four times.

We supplied the correct lesson in three forms:

1. a sentence saying what the first and second controls do;
2. a JSON table assigning an effect to each displayed slot; and
3. a JSON policy saying which slot to choose for targets above and below.

Empty retention showed what the same model did without a lesson. The harness
did not parse the lesson or choose the action.

## Results on matching families

| Supplied material | Correct actions | Result |
| --- | ---: | --- |
| Nothing | 0/32 | Baseline |
| Relation sentence | 32/32 | Usable |
| Effect table | 32/32 | Usable |
| Target policy | 6/32 | Not usable |

All 128 matching calls returned valid action strings. The sentence and table
worked in both directions for all four families. The policy failed at least
one direction in every family.

## Results on unrelated families

We also delivered each source lesson to a family with the opposite control
rule. This tested whether the model would ignore a lesson whose family name did
not match the current device.

The relation sentence caused clear harm in three of eight unrelated cases. The
effect table caused clear harm in four. The policy caused clear harm in one.
The exact-family gate can remove all of this source material before a
nonmatching action request, but that gate was not applied in these diagnostic
calls.

## What this changes

The policy form is no longer a candidate interface. The sentence and effect
table are both reliable enough for a separate authorship test.

The next experiment will stop supplying the answer. The model will act, see an
environment-issued consequence, and try to write the sentence or table itself.
A comparison author will see the action without its consequence. This will test
lesson writing without mixing it with a delivery interface that may be broken.

## Audit details

The exact comparison was frozen in the
[experiment specification](../../docs/REPRESENTATION_CONSUMPTION_CALIBRATION.md).

- Model: `ai/qwen3:14B-Q6_K`
- Artifact digest:
  `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Protocol: `representation-consumption-calibration-v1`
- Logical calls: 256/256
- Physical attempts: 256/264
- Retries: 0
- Valid actions: 256/256
- Prompt tokens reported by the provider: 84,400
- Completion tokens reported by the provider: 7,149
- Packet SHA-256:
  `38f8953a7114e753964af91b1f9fbbba50dbaa24e1a53aa2c9b0a16b61c500fc`
- Diagnostic verdict: `candidate_found`
- Formation verdict: null

The runner rebuilt this result from every retained request and response before
exiting.
