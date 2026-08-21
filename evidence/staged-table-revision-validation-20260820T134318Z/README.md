# Aggregate validation of staged-table revision

## Main result

The bounded revision mechanism passed its frozen validation. Eight old
model-written tables first made 45 of 48 correct actions. The environment then
reversed each relation. All eight counterexperience actions followed the old
policy and produced contradictory environment results. The model recorded each
new result exactly and wrote all eight revised tables correctly.

Those revised tables made all 48 post-change matching actions. Cold action made
24. The stale old table made 3. Old table plus raw counterexperience made 17. A
revision without the consequence made 27. Removing the exposed revision and
leaving the old table made 4. A supplied exact new table also made all 48.

The family check preserved unrelated action. The checked revision made 24 of 48
unrelated actions, compared with 23 cold. Unchecked delivery made only 4. The
gate prevented 20 observed errors, but that number could not help the verdict.

## Two-phase task

Eight fresh controller families were balanced across both possible starting
relations. The first environment phase produced one action, one external result,
one model-written observation, and one model-written table per family.

Before the change, the tables acted on new devices above and below the current
position. They made all 24 downward actions and 21 of 24 upward actions. Cold
action made 21 of 48 overall.

The environment then reversed the relation for the same family. Each new
counterexperience device received the old table. Every model action followed
that table, so the changed environment moved in the opposite way from the old
prediction.

One author saw the new selected slot and movement. Another saw the same action
with the result hidden. Revision authors received the exact old table plus one
of those observations and returned a complete current table. All exposed
observations and revisions were exact. Four of eight hidden revisions happened
to be exact.

## Post-change results

| Later information | Matching actions | Unrelated actions |
| --- | ---: | ---: |
| No retained information | 24/48 | 23/48 |
| Stale old table | 3/48 | 24/48 |
| Old table plus raw counterexperience | 17/48 | 24/48 |
| Exposed revised table with family check | 48/48 | 24/48 |
| Hidden-consequence revised table | 27/48 | 24/48 |
| Exposed revision removed, leaving old table | 4/48 | 24/48 |
| Supplied exact new table | 48/48 | 23/48 |
| Exposed revised table without family check | 48/48 | 4/48 |

The revised table made all 24 upward and all 24 downward actions. It made all
24 matching actions in each changed-relation group and all 12 in each
relation-by-direction quadrant. Every post-change cell contained at least two
valid action objects.

## What this supports

This run validates one bounded form of revision. A table that had been useful
became stale after an external change. A new environment result caused the
model to write the opposite current table. That revision, and not raw history,
the stale table, a hidden result, or simple removal, caused the later behavioral
change. The exact-family check kept the revision from changing unrelated
families.

This is still not a general Formation effect. The mechanism matched a supplied
exact update rather than outperforming it. It covers one immediate reversal in
one artificial domain. It does not show that several lessons can coexist,
survive long delays, compose across tasks, or justify their operating cost.

The next experiment can test accumulation. Two independently earned tables
should remain available at the same time, and the family check should deliver
the right one without the later lesson erasing or contaminating the earlier
one.

## Audit details

- Model: `ai/qwen3:14B-Q6_K`
- Model digest: `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Logical calls: 928
- Physical attempts: 928
- Retries: 0
- Frozen specification SHA-256: `e6890bd81510735fa2b5131057ff4c40fc564793d02fdfd07dbd0178d83ac71f`
- Specimen SHA-256: `15562d39419c58948afed4f99455c8e316b2879aa6f3ac9916fd739d27d103ff`
- Packet SHA-256: `af03d1feb4aa32656ac272e93b7bdf980d210663b6e9a2d284006046f4ae4374`
- Frozen revision verdict: `supported`
- Formation verdict: `null`
- Replay: exact from retained request and response bytes

The computed record is [packet.json](packet.json). The frozen two-phase worlds
are in [specimen.json](specimen.json). The exact provider identity is in
[provider.json](provider.json). Every raw request and response is retained under
`attempts/`.
