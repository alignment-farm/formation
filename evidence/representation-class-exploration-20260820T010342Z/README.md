# The model could not reliably write and use the same lesson

## Main point

We tested three ways for a model to record what it learned from one action: a
sentence, a table, and a simple policy. None worked across both test worlds.

The failure happened in two different places. Sometimes the model wrote the
wrong lesson after seeing a clear consequence. In another case it wrote the
right lesson, but later calls did not use it. The experiment therefore found no
representation ready for the next developmental comparison. Formation remains
null.

## The task in plain language

Each device displayed two controls with meaningless names. One control moved a
number up by one. The other moved it down by one. The model had to move the
number toward a target.

The model first chose a control without knowing which one moved up. The
environment then reported which displayed slot it had selected and whether the
number moved up or down. From that single result, the model could infer what
both slots did.

We asked the model to record that relation in three forms:

1. a sentence saying what the first and second controls do;
2. a JSON table assigning an effect to each displayed slot; and
3. a JSON policy saying which slot to use when the target is above or below.

Later calls received the exact text written by the model. The harness did not
parse the text or choose an action from it.

## What we compared

There were two independent test worlds. Both used the same hidden rule: the
first displayed control moved down and the second moved up. The first
experience revealed that the first slot moved down. The second experience
revealed that the second slot moved up.

For each form, one author saw the environment's result. A comparison author saw
the same action but not its consequence. New devices then tested movement both
up and down. Empty retention showed what the same cold model did without a
lesson.

## What happened

The three representation classes separated two failures:

| Form | World A authorship | World A matching action | World B authorship | World B matching action |
| --- | --- | ---: | --- | ---: |
| Relation sentence | Exact correct mapping | 8/8 | Exact opposite mapping | 0/8 |
| Effect table | Exact correct mapping | 8/8 | Exact opposite mapping | 0/8 |
| Target policy | Exact opposite policy | 0/8 | Exact correct policy | 0/8 |

The sentence and table worked completely in the first world: the model wrote
the correct relation, and later calls made all eight correct actions. In the
second world, the model wrote both forms backward and later calls made none of
the eight correct actions.

The policy failed differently. It was backward in the first world. It was
correct in the second world, but later calls still made none of the eight
correct actions.

Without a lesson, the model made none of the matching actions correctly. The
same was true when the author did not see the consequence. All 176 later calls
returned valid action strings, so unavailable output does not explain the
result.

The nonmatching diagnostic found one smaller harm. World A's ungated effect
table changed two of four upward actions from correct to wrong. The other
eleven form, world, and direction cells matched the empty baseline. This does
not revise the earlier evidence that exact-family gating can block known harm.

## What the result means

The prospective rule required one form to be authored exactly and to improve
both matching directions in both worlds. No form did so.

The result is more specific than “the prompts failed.” The substrate has two
independent jobs:

1. help the model write a correct account from what happened; and
2. make that account usable when the model acts later.

This experiment shows that either job can fail while the other succeeds. A
single end-to-end score would hide that distinction.

The next instrument will measure those jobs separately. First, known-correct
lessons will test which delivery form later calls can use across varied device
names and action strings. That is an interface test, not evidence of learning.
After the delivery interface is stable, a separate comparison will ask whether
experience causes the model to write the correct lesson itself.

## What this does not show

The experiment does not show that the model developed, learned a durable skill,
or would behave the same way in another task. It tested one model artifact in a
small artificial control problem. A correct lesson supplied by the harness can
diagnose the interface, but it cannot count as acquired competence.

## Audit details

The exact comparison was frozen in the
[experiment specification](../../docs/REPRESENTATION_CLASS_EXPLORATION.md).
That file is an audit contract, so it uses more exact language than this
account.

- Model: `ai/qwen3:14B-Q6_K`
- Artifact digest:
  `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Protocol: `representation-class-exploration-v1`
- Logical calls: 190/190
- Physical attempts: 190/198
- Retries: 0
- Valid later actions: 176/176
- Prompt tokens reported by the provider: 62,880
- Completion tokens reported by the provider: 5,447
- Packet SHA-256:
  `f9f6f3bb34904650d03834c23e433685fdfbf54d3880c7060d930473372faa76`
- Representation trial verdict: null
- Formation verdict: null

The runner regenerated the packet and verdict from the retained raw requests
and responses before exiting.
