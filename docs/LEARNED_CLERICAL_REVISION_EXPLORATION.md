# Learned clerical revision exploration

Status: **frozen before contact under the session-wide human authorization**.

## Question

Can the validated clerical substrate revise guidance after the same visible
structure produces a contradictory consequence, while preserving the old
record and preventing it from acting as the current version?

This is an exploratory revision test. It uses the same restricted clerk,
explicit prose parser, deterministic sentence renderer, later feature
normalizer, and exact two-field matcher that passed the learned-instrument
validation.

## Experience sequence

Two fresh lineages each contain two visible designs with opposite control
relations. The old experience produces one complete record for each design.
That record is used on fresh pre-change devices before the environment relation
changes.

A counterexperience then presents a new device with the same visible design.
The participant acts using the old sentence. The environment has reversed the
true control relation, so an old-policy action produces the contradictory
movement. The exposed clerk receives that movement and writes a new record.

The old and new records remain separate lineage objects with version numbers
and links to their source occurrences. The runtime may select the newest
complete version after an exact structural match. An incomplete hidden-
consequence attempt does not displace the old complete version. The runtime may
not delete the old record, infer the new effect, or rewrite either version.

## Information separation

The 4B clerk sees the same restricted inputs as the validated instrument. It
never receives a later action's controls, target, expected answer, or score.
The consequence-hidden revision chain receives the selected actuator but not
its movement.

The 14B participant alone receives controls, position, target, and the exact
sentence allowed by its branch. The harness applies every action in the
environment and preserves both record versions in evidence.

## Comparisons

Before the relation changes, each old record is tested three times above and
below the source position on fresh devices.

After the change, each lineage has A above, A below, B above, B below, a novel
device, and a recombined device. Every case receives three calls under nine
conditions:

- cold;
- raw counterexperience;
- newest exposed revision selected by normalized scope;
- stale old record selected by the same scope;
- consequence-hidden revision, which leaves the old complete version current;
- exposed revision removed before action, which also leaves the old version
  current;
- old and new rendered sentences delivered together;
- a supplied correct new sentence selected by normalized scope; and
- the exposed revision selected by the environment-owned structural match.

## Prospective interpretation

The apparatus is not engaged unless supplied new guidance makes at least 21 of
24 post-change matching actions, at least 10 of 12 in each design and
direction, and every three-call participant cell contains at least two valid
actions.

A revision candidate requires:

- at least three of four old records exact;
- at least 21 of 24 pre-change old-record actions correct;
- all four counter actions consistent with the old policy;
- at least three of four exposed revision records exact and rendered exactly;
- at least 10 of 12 later normalizations and structural selections exact, with
  no more than one false novel or recombined selection;
- revised guidance making at least 21 of 24 post-change matching actions;
- at least eight more matching actions than cold, raw counterexperience,
  consequence-hidden revision, and removal;
- at least 16 more matching actions than the stale old record;
- no more than three fewer matching actions than supplied new guidance;
- oracle-selected exposed revisions making at least 21 matching actions; and
- no more than two fewer unrelated actions than cold.

If the apparatus is engaged but the revised branch loses at least four
unrelated actions, the verdict is `harmful`. Otherwise it is
`revision_candidate` or `null`.

This result cannot validate revision on its own. A candidate would justify a
larger fresh validation with more lineages and balanced changed relations.
Formation remains outside the claim ceiling.

## Models, budget, and evidence

The clerk remains
`huggingface.co/qwen/qwen3-4b-gguf:Q4_K_M` with digest
`sha256:618c80458ca4012b132ef1847bcd49ec5f923c3d9df35fdc534715085108e9f3`.
The participant remains `ai/qwen3:14B-Q6_K` with digest
`sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`.

The schedule contains 404 logical calls and permits at most eight transport
retries, for a physical ceiling of 412 attempts. Model output never changes the
schedule. Valid outputs are never resampled.

Evidence is written under
`evidence/learned-clerical-revision-<run-id>/` and replayed from retained raw
requests and responses before successful exit.
