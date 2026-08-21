# Diagnostic of accumulated-table containers

Status: **frozen before contact under the session-wide human authorization**.

## Question

Did joint table use fail because the first list entry dominated, and can a
container keyed by controller family make both retained lessons usable?

The preceding accumulation exploration authored eight exact tables. Gated
delivery used both families well, but an ordered two-table list produced 24 of
24 actions for family A and only 12 of 24 for family B. The supplied list had
the same split. This diagnostic keeps those exact tables fixed and changes only
their container.

## Comparison

The source is
`evidence/staged-table-accumulation-20260820T140646Z/packet.json` with SHA-256
`c9c12ca3ef2db355bc6832d76db390657179579ca305f945f9949456c11381ab`.
Its specimen SHA-256 is
`9368cbd51181ee400d8da9e6218ee4d2745b8099203e959a460be82b1d673945`.
The runner must verify both files and require all eight retained tables to be
exact before contact.

Each of the four retained lineages receives four fresh matching devices: A
above, A below, B above, and B below. Every case receives four identical calls
under five conditions:

- no retained material;
- the two exact model-written tables in A-then-B list order;
- the same tables in B-then-A list order;
- the two tables in an object keyed by their exact controller-family IDs; and
- the existing family gate delivering only the matching table.

The table bytes do not change between conditions. The harness may arrange the
container and perform the declared gated lookup. It may not rewrite a table,
infer a relation, choose an action, or resample a valid output.

## Model, budget, and retention

The participant is `ai/qwen3:14B-Q6_K` with digest
`sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
through the unchanged Docker Model Runner chat-completions interface.

The schedule contains 320 logical calls and permits at most eight transport
retries, giving a physical ceiling of 328 attempts. Model output never changes
the schedule. Evidence is written under
`evidence/accumulated-table-container-<run-id>/` and replayed from exact raw
request and response bytes before successful exit.

## Frozen interpretation

The diagnostic is `not_engaged` unless gated delivery makes at least 58 of 64
actions, at least 29 of 32 for each family position, and every four-call cell
contains at least three valid action objects.

An order effect is found only if A-then-B delivery favors A over B by at least
12 actions and B-then-A delivery favors B over A by at least 12 actions.

The keyed container is usable only if it makes at least 58 of 64 actions, at
least 29 of 32 for each family position, trails gated delivery by no more than
four actions, and every keyed cell contains at least three valid actions.

The verdict is `keyed_repairs_order_bias` if both observations hold,
`order_bias_found` or `keyed_container_found` if only one holds, and null
otherwise. The result selects an interface only. It cannot support acquisition,
accumulation, or Formation because no new lesson is authored in this contact.
