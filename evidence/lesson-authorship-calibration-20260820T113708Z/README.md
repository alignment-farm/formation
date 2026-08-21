# Neither usable lesson form was written reliably

## Main point

We tested whether one action and its external result could make the model write
a lesson that later calls already know how to use. Eight fresh experiences
covered the first displayed slot four times and the second slot four times.

Neither the relation sentence nor the effect table passed. The result was
stable enough to expose two specific failures rather than sampling noise.

The effect table was correct after all four first-slot experiences and wrong
after all four second-slot experiences. The relation sentence handled more
cases, but it failed three of eight families. In two of those families, an
author who did not see the consequence wrote the same correct lesson, so the
lesson could not be attributed to the result.

Formation remains null.

## What happened

Each controller used the same hidden rule: the first displayed control moved
down and the second moved up. Acquisition targets alternated above and below.
The cold model consequently selected each displayed slot four times. Every
selected slot moved in the direction needed to infer the full rule.

For each experience, one author saw the environment's result and another saw
the action with the result withheld. Both wrote a sentence and an effect table.
Every exact request was repeated three times.

| Lesson form | Families that passed | Families that failed |
| --- | ---: | ---: |
| Relation sentence | 5/8 | 3/8 |
| Effect table | 4/8 | 4/8 |

All 96 authorship calls returned text. Most identical requests produced the
same output all three times. The effect-table split followed the selected slot
exactly: first-slot results always produced the correct table; second-slot
results always produced the opposite table.

## What this changes

The delivery interface is not the current obstacle. Correct sentences and
tables already guided every matching action in the preceding diagnostic. The
remaining problem is how the model turns an environment result into either
lesson.

The next experiment will split that reasoning into two model calls. The first
will record only the directly observed slot and movement. The second will infer
the complete table from that model-authored observation. A direct raw-result
branch and removal of the observation will show whether the extra stage helps.
The harness will pass the authored observation forward but will not compute the
controller rule.

## Audit details

The exact comparison was frozen in
[the specification](../../docs/LESSON_AUTHORSHIP_CALIBRATION.md).

- Model: `ai/qwen3:14B-Q6_K`
- Artifact digest:
  `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Protocol: `lesson-authorship-calibration-v1`
- Logical calls: 104/104
- Physical attempts: 104/112
- Retries: 0
- Selected slots: first 4, second 4
- Prompt tokens: 32,102
- Completion tokens: 4,459
- Packet SHA-256:
  `91a3b18ec98aad6f10cb2fe774e83c78c14fcbe6445880050b93a519b9eecc2a`
- Authorship verdict: null
- Formation verdict: null

The runner rebuilt the packet from all retained requests and responses before
exiting.
