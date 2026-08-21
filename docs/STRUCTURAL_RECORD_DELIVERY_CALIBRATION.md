# Structural record delivery calibration

Status: **frozen before contact under the session-wide human authorization**.

## Why this calibration is needed

The first learned clerical instrument experiment could not test its full
pipeline. Even a correct supplied record produced only 15 of 32 matching
actions. The participant had not previously been shown to use that record's
new field names and string container.

This calibration changes only how a known-correct, already selected effect is
presented to the participant. It contains no clerk calls and cannot show that
experience was encoded, classified, or learned.

## Question

Which small record form lets the existing 14B participant reliably turn an
already selected control-effect relation into action on devices with fresh
identities and control strings?

## World and comparison

Two lineages provide opposite control relations in each of two visible design
positions. Each lineage has four fresh later devices: A above, A below, B
above, and B below. Their controller-family IDs, device IDs, and action strings
did not appear in the first learned-instrument contact.

Every case receives four identical calls under six conditions:

- no retained material;
- the prior scoped record kept as a JSON string inside a list;
- a scoped record containing a nested control-effect object;
- the control-effect object alone;
- the same effect written as one short sentence; and
- the previously successful table form keyed to the current controller-family
  ID.

The harness supplies the correct relation in every non-cold condition. It does
not use model output to change the schedule, rewrite a form, or resample a
valid answer. The environment still applies and scores the participant's
action.

## Model, budget, and evidence

The participant is `ai/qwen3:14B-Q6_K` with digest
`sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
through the local Docker Model Runner chat-completions interface.

The frozen schedule contains 192 logical calls: two lineages by four cases by
six forms by four repeats. At most eight transport failures may be retried, so
the physical ceiling is 200 attempts. A valid output is never resampled. The
runner stops after the fixed schedule or either ceiling.

Evidence is written under
`evidence/structural-record-delivery-<run-id>/` and replayed from retained raw
requests and responses before successful exit.

## Prospective interpretation

The calibration is not engaged unless the current-family table makes at least
29 of 32 actions, at least 14 of 16 in each design position, at least 14 of 16
in each target direction, and every four-call cell contains at least three
valid action objects.

Another form is usable if it also makes at least 29 of 32 actions, meets the
same design and direction floors, trails the current-family table by no more
than two actions, and every one of its cells contains at least three valid
actions.

The verdict is `not_engaged` if the current-family table fails, `usable_form_found`
if at least one other form passes, and `null` otherwise. The result selects a
delivery interface only. It cannot support a learned instrument or Formation.
