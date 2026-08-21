# Four-world staged-chain validation

## Main result

The model used the real environment result to write the correct lesson in all
four worlds. With that lesson, later calls made 29 of 32 correct actions on new
devices from the same controller families. The cold comparison made 3, raw
experience made none, direct lesson writing made none, and removing the staged
lesson left 3.

The family check also did its job. It preserved 31 of 32 actions on unrelated
controllers. Giving the same lesson without that check preserved only 8. The
check therefore prevented 23 errors in this run.

The frozen verdict is null, not supported. Two thresholds missed. Upward
transfer was 13 of 16, one below the required 14. One author that could not see
the consequence guessed the correct lesson for one world. That comparison then
made 8 matching actions, so the staged lesson beat it by 21 rather than the
required 24.

## What the model did

Each world used a new controller family with two new action strings. The target
was below the starting position. The first model call chose the second action
in every world. The environment then reported that the choice moved the
position up, away from the target.

A second cold call received that result and wrote a small observation: the
second displayed action increased position. A third call turned the observation
into a complete two-row effect table. Both steps were exact in all four worlds.

The later test used new devices and action strings. It asked for movement both
up and down. It also used unrelated controller families where the action rule
was reversed. The retained table was delivered only when the controller family
matched, except in the deliberate no-check comparison.

## Comparisons

| Later information | Matching actions | Unrelated actions |
| --- | ---: | ---: |
| No retained information | 3/32 | 31/32 |
| Raw experience | 0/32 | 32/32 |
| Directly written table | 0/32 | 32/32 |
| Staged table with family check | 29/32 | 31/32 |
| Staged table written without the consequence | 8/32 | 32/32 |
| Staged table removed | 3/32 | 32/32 |
| Staged table without the family check | 28/32 | 8/32 |
| Supplied correct table with family check | 30/32 | 32/32 |

The staged table made all 16 downward actions and 13 of 16 upward actions. The
supplied correct table made 16 downward and 14 upward actions. Every group of
four later calls contained at least three valid action objects.

## What this supports

This run supports three bounded observations. First, splitting observation from
table writing remained reliable on four new experiences. Second, the resulting
model-written table strongly changed later matching action. Third, an external
family check prevented most of the table's harm on unrelated controllers.

The result does not satisfy its prospective validation rule. It therefore does
not establish a validated Formation effect. It also does not test revision,
several accumulated lessons, long delays, or another task domain.

The withheld comparison exposed a design issue for a successor. A model that
cannot see the consequence can still guess one of the two possible relations.
With four source worlds, one correct guess creates eight correct later actions
and makes the frozen 24-action gap difficult to meet. A fresh test should
balance both possible true relations across source worlds so that a fixed guess
cannot look like consequence-grounded authorship.

## Audit details

- Model: `ai/qwen3:14B-Q6_K`
- Model digest: `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Logical calls: 536
- Physical attempts: 536
- Retries: 0
- Frozen specification SHA-256: `47ce3313bc2c6af2dbdec26d492d98514311f5b091fca64ddbf3bb11d847f24f`
- Specimen SHA-256: `2612b511fac5af26d9d43fc38e0e6f3bfbeec91b965e942ac43db2be796c2c2f`
- Packet SHA-256: `4714ec057e7cfce733ebd1127c10d18da5fc4ba7461f3a887ed840f8e813b238`
- Frozen validation verdict: `null`
- Formation verdict: `null`
- Replay: exact from retained request and response bytes

The primary computed record is [packet.json](packet.json). The frozen cases are
in [specimen.json](specimen.json), the exact provider identity is in
[provider.json](provider.json), and every raw request and response is retained
under `attempts/`.
