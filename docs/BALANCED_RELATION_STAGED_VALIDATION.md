# Balanced-relation validation of the staged chain

Status: **frozen before contact under the session-wide human authorization**.

## Question

Does staged lesson writing follow the environment result when both possible
controller relations are equally common, and does the resulting lesson improve
later matching action without harming unrelated action?

The preceding validation used four source worlds with the same true relation.
An author that could not see the consequence guessed that relation once. That
single guess supplied eight correct later actions and caused the frozen
comparison to miss its required gap. This successor does not lower that old
threshold or rescore that run. It uses a fresh design in which a fixed guess
cannot be right across the whole packet.

## Comparison

Six fresh source families are fixed before contact. Three have a first action
that increases position. Three have a second action that increases position.
Every acquisition target is one step below its start. The environment applies
the model's chosen action and issues the selected slot and actual movement.

For each source, one observation author sees the environment result. Another
sees the same occurrence with the result withheld. Separate cold calls turn
each observation into a complete effect table. A direct author receives the raw
occurrence and result without the observation step.

Each source then receives four new cases. Two use the same controller family,
with one target above and one below. Two use a new family with the opposite
relation, again with one target above and one below. Every later branch and case
receives three identical calls.

The eight later branches are:

- no retained information;
- raw experience;
- the directly written table, delivered only to the matching family;
- the consequence-exposed staged table, delivered only to the matching family;
- the consequence-withheld staged table, delivered only to the matching family;
- removal of the consequence-exposed table;
- the consequence-exposed table without the family check; and
- a supplied correct table with the family check.

The harness may apply the external action result, preserve exact model text,
check exact family identity, and score action correctness. It may not write or
repair an observation or table.

## Model, budget, and retention

The participant is `ai/qwen3:14B-Q6_K` with digest
`sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
through the unchanged Docker Model Runner chat-completions interface.

The fixed schedule contains 612 logical calls: 36 acquisition and authorship
calls, followed by 576 later actions. Every logical call may receive one
transport retry. At most eight retries are allowed, giving a physical ceiling
of 620 attempts. Model output never changes the schedule. The run stops only at
completion, provider-identity mismatch, the physical ceiling, or an apparatus
failure that prevents evidence retention.

Evidence is written under
`evidence/balanced-relation-staged-validation-<run-id>/`. The runner must replay
the computed packet from exact retained request and response bytes before it
exits successfully.

## Frozen verdict

The validation is `not_engaged` unless all six consequence-exposed observations
and staged tables are exact and the supplied table makes at least 16 of 18
matching actions in each movement direction.

It is `harmful` if the family-checked staged table loses at least four unrelated
actions compared with no retained information.

It is `supported` only if all of these conditions hold:

- the family-checked staged table makes at least 32 of 36 matching actions;
- it makes at least 16 of 18 matching actions in each movement direction;
- it makes at least 16 of 18 matching actions in each of the two true-relation
  groups;
- it beats no retained information, raw experience, direct authorship,
  consequence-withheld staged authorship, and table removal by at least 12
  matching actions each;
- it loses no more than two unrelated actions compared with no retained
  information;
- the family check prevents at least 12 errors caused by unchecked delivery;
  and
- every three-call branch and case contains at least two valid action objects.

Otherwise the verdict is null. A supported result would validate this bounded
staged mechanism against balanced relation priors. Formation would remain null
because the packet does not test revision, longer accumulation, or another
domain.
