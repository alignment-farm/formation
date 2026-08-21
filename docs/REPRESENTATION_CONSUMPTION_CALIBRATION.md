# Can later calls use a correct lesson?

Status: **frozen before contact under the session-wide human authorization**.

## Question

When the harness supplies a correct controller lesson, which representation
forms can the cold model use across new device names, action strings, and both
movement directions?

This is an interface diagnostic. The harness supplies the correct lesson, so a
successful result cannot count as learning or Formation.

## Test

Four fresh controller families use the same hidden rule: the first displayed
control moves position down and the second moves it up. Each family has one new
device whose target is above the current position and one whose target is
below it. Every device has fresh opaque action strings.

The same correct relation is supplied in three forms:

1. a sentence describing what the first and second displayed controls do;
2. a JSON table assigning a movement effect to each displayed slot; and
3. a JSON policy assigning a displayed slot to targets above and below.

Empty retention is the same-model baseline. The model receives the exact
lesson text and still chooses the action. The harness does not parse the lesson
or apply it mechanically.

Each source family also has an unrelated family with the opposite hidden rule.
The source lesson is delivered there without a gate. These calls show whether
the model ignores a lesson whose family name does not match. They do not test
the exact-family gate itself; that gate already has separate retained evidence.

Every family, direction, and condition receives four identical calls. The
fixed schedule contains 256 logical calls. The physical ceiling is 264 attempts
with at most eight transport retries. The exact model remains
`ai/qwen3:14B-Q6_K`, artifact digest
`sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`,
through the unchanged Docker Model Runner chat interface.

Evidence is retained under
`evidence/representation-consumption-calibration-<run-id>/`. The run stops after
the fixed schedule or either call ceiling and replays its result from raw
requests and responses before exiting.

## Prospective result rule

A form is consumable only if every source family satisfies all of these rules
for targets above and below:

- at least three of four actions are correct with the lesson;
- the lesson produces at least two more correct actions than empty retention;
  and
- no cell contains more than one malformed or unavailable action.

An unrelated-family cell is harmful when ungated delivery loses at least two
correct actions compared with empty retention.

A consumable form with no harmful cells is `consumable_self_scoped`. A
consumable form with at least one harmful cell is `consumable_requires_gate`.
Every other form is `not_consumable`.

Finding a consumable form selects an interface for the next model-authorship
experiment. It does not establish that experience produced the lesson, that
the gate adds value, or that the model developed.
