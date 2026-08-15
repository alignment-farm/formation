# SQLite nullable anti-join exploration

Status: **valid contact; stopped as not engaged**.

## What we tested

We asked the same cold Cursor model, Composer 2.5, to write a SQLite query three
times. The query needed to find customers with no orders. The orders table also
contained a row whose customer id was `NULL`.

A careless `NOT IN` query can return no customers when its subquery contains
`NULL`. We wanted to learn whether the cold model made that error often enough
to support a persistence comparison.

Each call started in a new empty directory with no resumed chat. All three calls
received the same prompt bytes.

## What happened

All three queries returned the correct names: `Bex` and `Cy`.

- Call 1 used a correlated `NOT EXISTS` query.
- Call 2 used a correlated `NOT EXISTS` query.
- Call 3 used `NOT IN`, but removed `NULL` values inside the subquery.

The runner therefore classified the exploration as `not_engaged` and stopped
after the third call. It did not ask the model to write a lesson. It did not
send raw persistence, authored-lesson, or validation prompts.

## What this means

For this exact prompt and model, the proposed error was not repeatable. There
was no wrong acquisition experience for persistence to correct. The SQLite task
is therefore unsuitable as the first comparison between cold behavior and
simple persistence.

This does not show that Composer always handles nullable anti-joins. Three calls
on one task cannot support that claim. It also says nothing about Formation,
learning, transfer, or whether raw persistence would have helped.

The useful result is the stop itself: we rejected an unproductive contact task
without changing it after seeing the model's answers or shopping within the run
for an easier failure.

## Audit trail

[`summary.json`](summary.json) contains the mechanical classification. The
numbered files retain each exact prompt, raw output, and process receipt. An
independent evidence audit re-executed the queries, verified the receipts, and
returned `EVIDENCE_VALID` with no discrepancies.
