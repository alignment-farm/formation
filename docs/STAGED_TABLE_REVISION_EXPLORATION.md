# Exploratory revision of a staged effect table

Status: **frozen before contact under the session-wide human authorization**.

## Question

After a model-written effect table has correctly guided action, can a later
environment consequence cause the model to replace that now-stale table and act
correctly under the changed relation?

The preceding aggregate validation supports acquisition and selective transfer
in this bounded domain. It did not test revision. This experiment introduces
one controlled relation change and measures whether the developmental lineage
can move from an old correct table to a new correct table without the harness
writing either relation.

## Two phases

Four fresh controller families are fixed before contact. Two begin with a first
action that increases position. Two begin with a second action that increases
position. Each family first produces one action, one environment-issued result,
one model-written observation, and one model-written effect table.

Before any change, the old table and a cold comparison act three times on new
targets above and below. This checks that the initial lesson is actually usable.

The environment then reverses the hidden relation for the same controller
family. A new device is presented with the old table. The model acts once, and
the changed environment issues the selected slot and actual movement. One
observation author sees that result. Another sees the same occurrence with the
result withheld.

Two revision authors receive the exact old table and one of those model-written
observations. Each must return one complete current effect table. The prompt
states that a new direct observation may supersede the old table, but it does
not state the new relation or choose an action. The runtime preserves both
versions in lineage and delivers only the selected current table on the
revision branch.

## Post-change comparison

Each world then receives four new cases. Two use the changed source family with
targets above and below. Two use an unrelated family with the opposite of the
changed relation, again above and below. Every branch and case receives three
identical calls.

The eight post-change branches are:

- no retained information;
- the stale old table;
- the old table plus raw counterexperience;
- the consequence-exposed revised table;
- the consequence-hidden revised table;
- removal of the exposed revision, leaving the old table;
- a supplied exact new table; and
- the exposed revised table without the family check.

The stale-table and revision-removal requests are byte-identical within each
world and case. They are separate samples of the same ablated state.

## Model, budget, and retention

The participant is `ai/qwen3:14B-Q6_K` with digest
`sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
through the unchanged Docker Model Runner chat-completions interface.

The schedule contains 464 logical calls: 32 acquisition, counterexperience,
observation, and table calls; 48 pre-change actions; and 384 post-change
actions. At most eight transport retries are allowed, giving a physical ceiling
of 472 attempts. Model output never changes the schedule. The run stops only at
completion, provider-identity mismatch, the physical ceiling, or an apparatus
failure that prevents evidence retention.

Evidence is written under `evidence/staged-table-revision-<run-id>/`. The runner
must replay the computed packet from retained request and response bytes before
successful exit.

## Frozen interpretation

The exploration is `not_engaged` unless all four initial observations and
tables are exact, the old tables make at least 21 of 24 pre-change actions, at
least three of four counterexperience actions follow the old table, all four
exposed counter-observations and revised tables are exact, and the supplied new
tables make at least 21 of 24 post-change matching actions.

It is `harmful` if the family-checked exposed revision loses at least four
unrelated post-change actions compared with no retained information.

It is `candidate_found` only if:

- the exposed revised table makes at least 21 of 24 post-change matching
  actions and at least 10 of 12 in each movement direction;
- it beats no retained information, the stale old table, and revision removal
  by at least eight matching actions each;
- it beats old table plus raw counterexperience and the consequence-hidden
  revision by at least six matching actions each;
- it trails the supplied exact new table by no more than three matching
  actions;
- it loses no more than two unrelated actions compared with no retained
  information; and
- every three-call post-change branch and case contains at least two valid
  action objects.

Otherwise the result is null. Gate benefit is reported but cannot help the
verdict. A candidate would justify a fresh revision validation. It would not
establish general revision or a Formation effect.
