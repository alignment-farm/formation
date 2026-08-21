# Exploratory staged-table revision

## Main result

The model revised all four old effect tables correctly after the environment
relation changed. The revised tables then made 21 of 24 correct post-change
matching actions. Cold action made 12, the stale table made none, old table plus
raw counterexperience made 6, a revision without the consequence made 3, and
removing the exposed revision made none.

The frozen verdict is null. Upward post-change action scored 9 of 12, one below
the required 10. The supplied exact new table failed the same three-call world
and also scored 9 of 12 upward. Every other candidate threshold passed.

## What changed

Each of four controller families first had a stable relation. The model acted,
received the environment result, wrote an exact observation, and wrote an exact
effect table. Before the environment changed, those tables made 21 of 24
correct actions on new devices, versus 12 cold.

The environment then reversed the hidden relation for the same family. A new
device received the old table. All four model actions followed that stale
policy. Under the changed environment, each action moved in the newly opposite
way and produced a direct counterexample to the old table.

One cold author saw the new selected slot and movement. Another saw the same
occurrence with that result hidden. Separate revision authors received the old
table plus one of those observations and returned a complete current table.

All four exposed observations and revisions were exact. Only one hidden
observation and revision happened to be exact.

## Post-change results

| Later information | Matching actions | Unrelated actions |
| --- | ---: | ---: |
| No retained information | 12/24 | 12/24 |
| Stale old table | 0/24 | 12/24 |
| Old table plus raw counterexperience | 6/24 | 12/24 |
| Exposed revised table with family check | 21/24 | 12/24 |
| Hidden-consequence revised table | 3/24 | 12/24 |
| Exposed revision removed, leaving old table | 0/24 | 12/24 |
| Supplied exact new table | 21/24 | 12/24 |
| Exposed revised table without family check | 21/24 | 9/24 |

The revised table made all 12 downward actions and 9 of 12 upward actions. The
only failed cell was one upward device, where both the model-written revision
and supplied exact table scored 0 of 3. Every post-change cell contained at
least two valid action objects.

## What this supports

This run found a bounded revision candidate. A previously useful table became
stale after a real environment change. A new consequence caused the model to
write the opposite current table, and later action changed accordingly. Raw
counterexperience, stale persistence, hidden consequence, and revision removal
did not produce the same effect.

The prospective verdict remains null, so this run does not validate revision.
The one failed threshold follows the later action interface rather than a wrong
revision: the supplied exact table failed the same cell. A fresh aggregate
revision validation can test more balanced worlds while tolerating one isolated
three-call interface failure.

Formation remains null. The run covers one artificial relation reversal in one
small domain and does not test accumulated lessons, delayed revision, net cost,
or performance beyond a supplied exact update.

## Audit details

- Model: `ai/qwen3:14B-Q6_K`
- Model digest: `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Logical calls: 464
- Physical attempts: 464
- Retries: 0
- Frozen specification SHA-256: `1d06ab80d8805cc350273e1a8a2bae8496400da90a6c68ddca284a0c1b3553d6`
- Specimen SHA-256: `2a104a911056cca5c4ccdfebf79c2b1bad93656bec4c6bc6e412c2823c4e58ab`
- Packet SHA-256: `026739b99835aa96c722de46ec707d25bc60f6ba684e48961a596c194c472058`
- Frozen revision verdict: `null`
- Formation verdict: `null`
- Replay: exact from retained request and response bytes

The computed record is [packet.json](packet.json). The frozen two-phase worlds
are in [specimen.json](specimen.json). The exact provider identity is in
[provider.json](provider.json). Every raw request and response is retained under
`attempts/`.
