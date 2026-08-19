# Executable prediction revision implementation decision

Status: **implemented, independently review-conformant, and consumed by the one
completed live contact; retained as the runner decision and licenses no further
participant-model request**.

## Decision

Implement the independently reviewed
[executable prediction revision charter](EXECUTABLE_PREDICTION_REVISION_CHARTER.md)
as one deterministic contact runner.

The charter is now exact enough for code to reveal mistakes instead of choosing
research semantics. Both independent reviewers reproduced its case and witness
bindings, request classes, identities, denominators, and budget. The remaining
work is mechanical materialization and conformance testing.

## Implementation scope

Add:

- `contact/executable_prediction_revision_contact.py` for deterministic packet
  construction, fake or live provider transport, lineage, evaluation, atomic
  reporting, and integrity verification;
- `tests/test_executable_prediction_revision_contact.py` for fake-provider and
  pure-function tests; and
- short routing updates in the nearest READMEs.

The runner must reproduce, rather than reinterpret:

- the 2,473-byte case manifest and its frozen hash;
- the 45,357-byte witness artifact, both static-rule hashes, and every witness
  evaluation;
- all 35 invocation and derived output coordinates;
- every exact system message, user message, runtime material variant, and
  byte-identical repeat;
- literal and AST recognition, three-valued evaluation, trial and consequence
  separation, unavailable continuations, and comparison slots;
- the 35-logical, 38-physical, 18,816-planned-token, and 21,888-contingency
  ceilings; and
- the fixed two-world denominators and null terminal verdicts.

## Required tests

Before any live request, tests must show that:

1. malformed, fenced, empty, copied, long, and partial-JSON strings remain
   executable literal rules unless they exactly satisfy the AST marker and
   grammar;
2. AST parsing and three-valued missing-field evaluation match the mechanism;
3. manifest, witness, static-rule, prompt, material, and schedule bytes are
   deterministic;
4. unavailable acquisition, parent, successor, trial, and same-response values
   continue through their preassigned events and denominators;
5. result-withheld calls differ from selected calls only at the frozen result
   field, and all declared repeats are byte-identical while retaining distinct
   identities;
6. the fake transport exercises success, malformed envelopes, HTTP failure,
   retryable pre-response failure, physical-ceiling stop, and partial schedule;
7. integrity recomputation detects changed requests, responses, manifests,
   witnesses, identities, trials, consequences, vectors, facts, or summary; and
8. no report field computes a compound revision, success, validation, or
   Formation verdict.

Run the focused tests and the full repository suite. Then obtain read-only
runner-conformance reviews from `composer-2.5` and
`cursor-grok-4.6-high-fast` on the same final code and tests.

## Boundary after implementation

Two `RUNNER_CONFORMS` verdicts would license only a separate decision to execute
the charter's disposable interface and single participant packet. They would
not execute Qwen, establish revision, license influence testing, or support a
Formation claim.

Any runner defect returns to implementation under the same charter. It does not
license prompt, case, oracle, model, schedule, language, or report changes.

## Implementation and review record

The runner is [executable_prediction_revision_contact.py](../contact/executable_prediction_revision_contact.py).
Sixteen focused fake-contact tests cover the frozen artifacts, total rule
interpreter, exact requests and repeats, unavailable continuations, malformed
same-response envelopes, fixed denominators, retry and stopping behavior,
protocol authorship, token accounting, and integrity tampering. The full
repository suite passes 397 tests with one existing optional renderer test
skipped.

The first read-only review round used exact model identifiers `composer-2.5`
and `cursor-grok-4.6-high-fast`. Both returned `REVISE_RUNNER`. They required a
chat-template render audit and Engine pin, exact artifact bytes on disk,
protocol-authored visible and static proposal records, explicit atomic `/2`
facts, observed token accounting, stronger pre-response retry semantics, and
integrity bindings over every evidence surface.

The repaired runner added those controls. The second round found that the
integrity audit still trusted stored trial and consequence receipts, and that
malformed same-response slots did not enter the unavailable partition. The
final repair replays the deterministic packet from retained raw responses,
compares regenerated requests, logical records, protocol proposals, and
summary, and makes each same-response slot partition total.

Final read-only verdicts on the same code and tests:

- `composer-2.5`: `RUNNER_CONFORMS`
- `cursor-grok-4.6-high-fast`: `RUNNER_CONFORMS`
