# Does a model-written observation repair lesson authorship?

Status: **frozen before contact under the session-wide human authorization**.

## Question

Can the model infer the complete controller table more reliably when one cold
call first records the directly observed slot and movement, and a second cold
call completes the rule?

## Comparison

Eight fresh controller families use the same hidden rule. Acquisition targets
alternate above and below so the model is expected to select both displayed
slots. After the environment returns the selected slot and movement direction,
one cold call writes only this observation:

`controller family`, `observed slot`, and `observed movement`.

The harness supplies the empty JSON form but not its values. It preserves the
exact model output.

Three final-table conditions then receive identical fresh responsibilities:

1. `direct_raw`: infer the effect table from the raw occurrence and result;
2. `staged_observation`: infer it from the exact model-written observation and
   the public device; and
3. `observation_removed`: receive the public device without the raw result or
   model-written observation.

Each final request is repeated three times. Every output continues, including
malformed or unavailable text. The harness never parses an observation into a
controller rule and never fills the final table.

The fixed schedule contains 88 calls: eight acquisitions, eight observation
authors, and 72 final-table authors. The physical ceiling is 96 attempts with
at most eight transport retries. The exact model and Docker interface remain
unchanged. Evidence is retained under
`evidence/staged-observation-authorship-<run-id>/` and replayed before exit.

## Prospective result rule

The experiment is `not_engaged` unless at least two informative acquisitions
select each displayed slot and at least seven of eight observation authors
write the exact observed fact.

The staged mechanism is a candidate only if every family satisfies all of
these conditions:

- staged authorship produces the exact correct table at least two times out of
  three;
- staged authorship beats observation removal by at least two exact tables;
- staged authorship is no worse than direct raw authorship in any family; and
- staged authorship beats direct raw authorship by at least two exact tables in
  at least three of the second-slot families.

Otherwise the verdict is null. A candidate would license a later combined
lesson-writing and action experiment. It would not establish Formation.
