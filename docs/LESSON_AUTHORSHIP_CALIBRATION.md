# Can experience make the model write a usable lesson?

Status: **frozen before contact under the session-wide human authorization**.

## Question

After one action and its environment-issued consequence, can the model
reliably write either of the two lesson forms that later calls can use?

## Test

Eight fresh controller families use the rule that the first displayed control
moves down and the second moves up. Acquisition targets alternate above and
below. The model acts without a lesson, and the environment reports the
selected slot and movement direction.

The model then writes either a relation sentence or an effect table. One author
sees the consequence. A comparison author sees the same action with the
consequence withheld. Each exact authorship request is repeated three times.

The harness supplies the empty form and output grammar. It does not supply the
family relation. Every output continues into the evidence, including malformed
or unavailable text. This packet tests lesson writing only; it makes no later
action calls.

The schedule contains 104 logical calls: eight acquisition actions and 96
authorship calls. The physical ceiling is 112 attempts with at most eight
transport retries. The exact model is `ai/qwen3:14B-Q6_K`, artifact digest
`sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`,
through the unchanged Docker Model Runner interface.

Evidence is retained under `evidence/lesson-authorship-calibration-<run-id>/`
and replayed from raw requests and responses before exit.

## Prospective result rule

The packet is `not_engaged` unless at least two informative experiences select
the first slot and at least two select the second.

A lesson form is an authorship candidate only when every informative family
satisfies all of these rules:

- the consequence-exposed author writes the exact correct lesson at least two
  times out of three;
- the exposed author produces at least two more exact correct lessons than the
  comparison author; and
- neither exposed nor comparison authorship has more than one malformed or
  unavailable output.

If either form passes, the diagnostic verdict is `candidate_found`. Otherwise
it is null. A candidate selects a lesson-writing interface for a later combined
experiment. It does not establish transfer, selective use, revision, or
Formation.
