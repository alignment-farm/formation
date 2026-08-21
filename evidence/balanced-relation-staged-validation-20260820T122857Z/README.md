# Balanced-relation staged validation

## Main result

The model used the environment result to write the correct observation and
effect table in all six source worlds. Those tables then produced 33 correct
actions out of 36 on new devices from the same controller families.

The frozen verdict is null. One upward test in a family where the second action
increased position failed all three times. The supplied correct table also
failed that same test twice out of three. This left upward performance at 15 of
18 and performance for that relation group at 15 of 18. Both were one below
their required floors.

The balanced comparison did remove the earlier guessing problem. With the
consequence hidden, staged lessons made 12 of 36 matching actions. With the
consequence exposed, they made 33. A fixed prior no longer looked like success
across the whole packet.

## What changed from the preceding test

The preceding four-world validation used only families where the second action
increased position. A lesson author that could not see the consequence guessed
that relation once and gained eight later actions.

This test used six fresh families. In three, the first action increased
position. In three, the second action increased position. An author had to
follow the actual environment result to write correct lessons across both
groups.

Every source produced two new matching devices and two unrelated devices. The
matching devices required movement in opposite directions. The unrelated
devices used the opposite hidden relation. Every later comparison received
three identical calls.

## What happened

The first action call chose the second displayed action in all six source
worlds. The environment reported downward movement in the three first-increases
families and upward movement in the three second-increases families.

The consequence-exposed author recorded all six results exactly. A separate
cold call converted each observation into the correct complete effect table.
The author with no consequence did not write an exact observation in any world.
Its later tables followed guesses that were useful only in some families.

| Later information | Matching actions | Unrelated actions |
| --- | ---: | ---: |
| No retained information | 18/36 | 18/36 |
| Raw experience | 18/36 | 21/36 |
| Directly written table | 2/36 | 18/36 |
| Exposed staged table with family check | 33/36 | 18/36 |
| Withheld staged table with family check | 12/36 | 18/36 |
| Exposed staged table removed | 18/36 | 18/36 |
| Exposed staged table without family check | 33/36 | 1/36 |
| Supplied correct table with family check | 34/36 | 18/36 |

The family check preserved exactly as many unrelated actions as the cold
comparison. Without the check, the table lost 17 of them.

## What this supports

The result supports a bounded causal account of lesson writing. Across both
possible relations, seeing the environment result produced exact observations
and tables. Hiding the result did not. Delivering the exposed table changed
later matching action far more than raw experience, direct writing, or removal.

The result does not meet its prospective validation rule and does not establish
a validated Formation effect. Its only failed performance thresholds trace to
one later-action cell. The supplied correct table also struggled there, so the
failure does not point to a wrong model-written lesson. It points to unreliable
use of an exact lesson by a later cold call.

The next experiment should compare staged sentence and table forms from the
same observations. It should ask whether one form reduces this consumption
failure while the same family check controls unrelated action. That is an
interface question, not a new claim about model development.

## Audit details

- Model: `ai/qwen3:14B-Q6_K`
- Model digest: `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Logical calls: 612
- Physical attempts: 612
- Retries: 0
- Frozen specification SHA-256: `3cb5705985790e8870ad37fc6a698fed3c278a2394c44c607446c9960c2bc7d2`
- Specimen SHA-256: `882bfb7c062b991e7223e19c9a99df2032dc619450b6c7a7e7fc390f6df25b90`
- Packet SHA-256: `720edb1fa8363483b5e885f9b9650fa8db26a6f8b1ec3dd03eeae735e7c1b9d4`
- Frozen validation verdict: `null`
- Formation verdict: `null`
- Replay: exact from retained request and response bytes

The computed record is [packet.json](packet.json). The frozen worlds and
relation groups are in [specimen.json](specimen.json). The exact provider
identity is in [provider.json](provider.json). Every raw request and response is
under `attempts/`.
