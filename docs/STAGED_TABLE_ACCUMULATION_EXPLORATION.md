# Exploratory accumulation of two staged tables

Status: **frozen before contact under the session-wide human authorization**.

## Question

After two controller lessons are earned in sequence, do both remain useful on
new devices, and can the model select the applicable lesson when both are
delivered together?

The staged mechanism has now passed bounded acquisition and revision
validations. It has not shown that more than one retained change can coexist.
Simply storing two tables is not enough: later behavior must show that the
second did not erase the first and that joint delivery does not create
uncontrolled interference.

## Comparison

Four fresh lineages each contain two controller families, A and B. The families
have opposite hidden relations. Their acquisition order and relation assignment
are balanced across lineages. Each family independently produces one action,
one environment-issued result, one model-written observation, and one
model-written effect table. Family B is always acquired after family A.

After both tables exist, each lineage receives targets above and below on new A
devices, new B devices, and an unrelated third family. Every branch and case
receives three identical calls.

The eight later branches are:

- no retained information;
- both raw experiences;
- both model-written tables stored, with the exact-family gate delivering only
  the matching table;
- both model-written tables delivered together, requiring the model to select
  the matching family;
- only the first table retained;
- only the second table retained;
- two supplied exact tables delivered together; and
- two supplied exact tables stored behind the family gate.

The gated branch delivers no lesson to the unrelated family. The joint branch
delivers both tables unchanged to every case. The harness may preserve text,
apply exact family identity for the gated branches, and score actions. It may
not merge tables, choose a table for a joint branch, infer a relation, or
resample a valid output.

## Model, budget, and retention

The participant is `ai/qwen3:14B-Q6_K` with digest
`sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
through the unchanged Docker Model Runner chat-completions interface.

The schedule contains 600 logical calls: 24 acquisition and authorship calls
and 576 later actions. At most eight transport retries are allowed, giving a
physical ceiling of 608 attempts. Model output never changes the schedule. The
run stops only at completion, provider-identity mismatch, the physical ceiling,
or an apparatus failure that prevents evidence retention.

Evidence is written under `evidence/staged-table-accumulation-<run-id>/`. The
runner must replay the packet from exact retained request and response bytes
before successful exit.

## Frozen interpretation

The exploration is `not_engaged` unless all eight observations and tables are
exact and the supplied gated tables make at least 43 of 48 matching actions,
at least 21 of 24 for each family position, and at least 21 of 24 in each
movement direction.

It is `harmful` if the gated authored tables lose at least six unrelated actions
compared with cold action.

It is `candidate_found` only if:

- gated authored delivery makes at least 43 of 48 matching actions, at least 21
  of 24 for each family position, and at least 21 of 24 in each direction;
- joint authored delivery makes at least 40 of 48 matching actions, at least 19
  of 24 for each family position, and at least 19 of 24 in each direction;
- gated authored delivery beats cold and raw experience by at least 16 matching
  actions each;
- gated authored A action trails the first-only A branch by no more than three,
  and gated authored B action trails the second-only B branch by no more than
  three;
- joint authored delivery trails joint supplied delivery by no more than four,
  and gated authored delivery trails gated supplied delivery by no more than
  three;
- gated authored delivery loses no more than three unrelated actions compared
  with cold action; and
- every three-call branch and case contains at least two valid action objects.

Otherwise the result is null. Joint unrelated behavior and the difference
between joint and gated delivery are reported but cannot rescue a failed
verdict. A candidate would show bounded coexistence and selection of two
retained lessons. It would not distinguish a general developmental capacity
from scoped retrieval, establish net value, or establish Formation.
