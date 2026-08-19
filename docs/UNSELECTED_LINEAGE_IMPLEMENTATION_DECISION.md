# Unselected lineage behavior implementation decision

Status: **independently review-stable implementation decision; one fake-tested
runner and read-only conformance reviews are licensed, but no disposable
request, participant-model contact, validation packet, or Formation claim is
licensed**.

## Decision

Implement the independently reviewed
[unselected lineage behavior charter](UNSELECTED_LINEAGE_EXPLORATORY_CHARTER.md)
as one deterministic contact runner after this decision passes independent
review.

The charter now owns the research choices. It publishes the exact manifest and
leakage witness, freezes both prompt families, separates provider content from
parsing and action commitment, fixes all 109 logical calls, and defines total
continuation and null verdicts. Implementation may materialize those choices;
it may not improve them.

## Implementation scope

After review stability, add:

- `contact/unselected_lineage_behavior_contact.py` for exact packet
  construction, fake and live Docker Model Runner transport, lineage,
  environment application, scoring, evidence writing, and integrity replay;
- `tests/test_unselected_lineage_behavior_contact.py` for deterministic,
  fake-provider, transport, evidence, and tamper tests; and
- short routing updates in the nearest READMEs and test index.

Reuse the pure physics in
`micro_environment/unselected_lineage_behavior.py` and the specimen's public
surface and oracle behavior where they match the charter. Do not alter the
reviewed mechanism, specimen, charter, manifest, or witness to make the runner
easier. Do not import admission classifications, old LM Studio lifecycle code,
old rule languages, or answer-producing actor stubs.

The live adapter must use the charter's Docker endpoint and standard-library
HTTP transport. The default and test paths spend no model calls. A live path
may exist behind an explicit command option, but this decision does not
authorize invoking it. The adapter must expose charter-exact read-only
collection of model list, inspect, Model Runner status and version, Docker
version, backend, endpoint, and chat-template receipts for a later contact
decision. Tests inject fixed command and HTTP results; they do not query the
live provider.

## Exact implementation obligations

The runner must reproduce, not reinterpret:

- the published 7,720-byte canonical manifest and 3,954-byte canonical leakage
  witness with their frozen hashes;
- the charter's seven-step leakage-witness construction from the manifest,
  including identifier uniqueness, fixed-surface construction, oracle-derived
  roles, copy and later-token scans, model-visible label checks, canonical
  reconstruction, and comparison with the published witness;
- the four prompt/responsibility hashes, withheld sentinel, four static-lesson
  hashes, and four fixed-surface hashes;
- the 4,100-byte chat-template binding, its frozen hash, Jinja2 3.1.6, exactly
  one system/user pair, `tools` omitted, `add_generation_prompt=True`,
  `enable_thinking` undefined, and per-call rendered bytes and tokenizer counts;
- both exact HTTP setting objects, including JSON mode and 32 tokens only for
  action calls and no response grammar with 256 tokens for authorship;
- the disposable device and its interface-only stop;
- all provider-content, parse, proposal, commitment, environment, authorship,
  foreground, hidden-lineage, assignment, and score receipts;
- the rule that the environment sees only the committed proposal and applies
  unchanged specimen physics, even when JSON parsing is invalid;
- the two authorship calls per block and one shared exposed intermediate for
  delivery and ablation;
- the six later foreground paths and all no-persistence/ablation byte-equality
  witnesses;
- invocation coordinates `iv001` through `iv109` and the charter's nested
  later-call schedule;
- the 109-logical, 112-physical, 5,280-planned-token, and 6,048-contingency
  ceilings;
- one pre-response transport retry per logical call, at most three retries for
  the packet, and no quality retry;
- total continuation after the disposable call, including unmade calls after
  physical exhaustion; and
- complete branch-by-role and acquisition-status denominators with exact null
  terminal verdicts.

The runner may define public value types needed to keep provider, parse, and
proposal receipts separate. It may add a live scorer adapter that preserves the
specimen's assignment, oracle, physics, and completeness rules while deriving
JSON-interface validity from the parse receipt.

The parser-to-proposal mapping is exact. Unavailable content commits
`available=false, content=""`. A valid one-key `action` object commits the
extracted string, including an empty or unlisted string. Every other available
content commits the exact raw content string. Parsing therefore determines
which already-authored string enters the proposal before commitment. After
commitment, neither parser nor scorer may suppress, replace, repair, or alter
the proposal or environment result. The environment and physics scorer never
read the parse receipt. `action_interface_valid` requires a valid parse and
allowed-action membership; it cannot be inferred from proposal membership or
environment success.

Integrity replay must regenerate the deterministic packet from retained raw
HTTP request and response bytes plus the published manifest and witness. Stored
derived receipts are comparison targets, never trusted replay inputs. Replay
must regenerate logical records, provider and parse projections, proposals,
commitments, environment transitions, authorship receipts, foregrounds,
requests, rendered-chat audits, request-equality predicates, assignments,
scores, acquisition strata, paired facts, denominators, budget totals, and the
terminal summary.

## Required tests

Before any live request, focused tests must prove at least:

1. published manifest and witness objects reserialize to their exact lengths
   and hashes, and an independent constructor derives the exact witness from
   the manifest without using the published witness as its source of truth;
2. all fresh identifiers, states, targets, roles, profiles, oracle actions,
   presentation orders, and copy-control checks reproduce the charter;
3. both exact setting objects and request bodies contain only one system/user
   pair and the declared fields, with no branch, role, oracle, score, tool,
   session, or hidden-profile leakage and no JSON grammar on authorship;
4. fixture inspect bytes reproduce the 4,100-byte chat-template hash; the
   pinned renderer uses the exact bindings; every rendered chat and tokenizer
   count is retained; and the audit render adds no HTTP field;
5. action parsing rejects duplicate keys, extra or missing keys, non-string
   actions, non-finite constants, fences, trailing text, and malformed JSON
   without trimming or repair;
6. provider-unavailable, available-empty, parse-invalid, valid-unlisted, valid-
   listed, `hold`, and both control proposals remain distinct;
7. a valid listed envelope commits the extracted action, applies under
   unchanged specimen physics, and scores interface-valid, while a parse-
   invalid raw string equal to an allowed action is still committed and
   applied by unchanged environment physics while its interface-validity score
   remains false;
8. authorship output is a total raw string with no parser, and exposed versus
   withheld requests differ only at `external_result`;
9. all six foreground paths preserve exact delivered and hidden material,
   exposed and ablation share one receipt, and no-persistence and ablation
   action requests are byte-identical for every matched case;
10. the 109-call fake schedule is exact, all acquisition results commit before
    authorship, all authored outputs retain before later action, every branch-
    role denominator is four, and invalid or unavailable upstream output
    changes no assignment;
11. fake transport covers success, empty content, malformed envelopes,
    reasoning-only content, 4xx, 429, 5xx, retryable pre-response failure,
    exhausted retry, the global retry limit, and physical-ceiling exhaustion;
12. invalid, unavailable, or unlisted disposable output retains exactly
    `iv001` and sends no acquisition, authorship, or later request, while a
    valid disposable continues into the frozen schedule;
13. completion allowance is reserved before every attempt and cannot be
    repurposed into another call, block, repair, or rerun;
14. every focused test uses injected fake transport and fails if code attempts
    to connect to or invoke the live endpoint;
15. full fake evidence retains exact request and response bytes, usage,
    ordering, retries, lineage, scores, residual byte/token deltas, and null
    verdicts; and
16. integrity replay regenerates the full deterministic packet from retained
    raw evidence without trusting stored derived receipts, compares every
    charter surface, equality predicate, denominator, budget, and summary, and
    fails on any mismatch.

Run the focused tests and full repository suite. Then obtain independent
read-only runner-conformance reviews from exact model identifiers
`composer-2.5` and `cursor-grok-4.6-high-fast` on the same final code and tests.

## Boundary after implementation

Two `RUNNER_CONFORMS` verdicts would license only a separate live-contact
decision. That later decision must perform fresh read-only provider preflight
and either authorize the charter's one disposable call and participant packet
or stop.

Runner conformance would not execute Qwen, establish a behavioral difference,
validate Formation, or license any rerun or successor. A runner defect returns
to implementation under the same charter. It cannot change the model, prompts,
manifest, witness, interface, schedule, budget, scorer meaning, or stop rule.

## Review question

Return `IMPLEMENTATION_DECISION_STABLE` only if this decision licenses exactly
the minimum fake-tested runner needed to materialize the reviewed charter while
keeping participant contact behind a later decision.

Otherwise return `REVISE_IMPLEMENTATION_DECISION` with each missing test,
authority leak, scope expansion, or path that could contact the model before
runner conformance.

## Review record

The first identical read-only review used exact model identifiers
`composer-2.5` and `cursor-grok-4.6-high-fast`. Both returned
`REVISE_IMPLEMENTATION_DECISION`. They found four shared gaps: the parser-to-
proposal mapping was compressed into an ambiguous sentence; integrity replay
could stop at tamper detection instead of regeneration; witness construction
and chat-template rendering were not fully licensed; and the disposable stop
was not tested. Grok also required an explicit fake-transport barrier.

The repair freezes the three-way parser-to-proposal mapping, manifest-derived
witness construction, template and render audit, raw-evidence packet
regeneration, disposable stop, injected transport, and ordering witnesses.

Final independent read-only reviews on the same repaired text returned:

- `composer-2.5`: `IMPLEMENTATION_DECISION_STABLE`
- `cursor-grok-4.6-high-fast`: `IMPLEMENTATION_DECISION_STABLE`

Neither review edited repository files or contacted the participant model.

## Implementation and review record

The first runner snapshot is implemented in
[`unselected_lineage_behavior_contact.py`](../contact/unselected_lineage_behavior_contact.py).
Twenty-three focused tests in
[`test_unselected_lineage_behavior_contact.py`](../tests/test_unselected_lineage_behavior_contact.py)
cover the published artifacts, strict action adapter, authority split, full
fake schedule, retries and exhaustion, render audit, preflight injection,
evidence replay, tamper rejection, and inert live CLI.

Final verification after runner review and repair:

```text
python3 -m unittest tests.test_unselected_lineage_behavior_contact
Ran 23 tests ... OK

python3 -m unittest discover -s tests -q
Ran 434 tests ... OK
```

The first identical runner reviews by `composer-2.5` and `grok-4.6` both
returned `REVISE_RUNNER`. They required explicit paired facts, request and
foreground audits, richer intermediate and action receipts, section-by-section
replay, exact provider preflight checks, safe retry exhaustion, and broader
contract tests.

After that repair, Composer returned `RUNNER_STABLE`. Grok found two remaining
gaps: render reproduction could still fail after transport began, and the tests
did not independently reconstruct the six exact delivered and hidden paths.
The final repair moved render validation before transport and added exact-path
checks across all 96 later calls.

Final independent read-only reviews on the same repaired runner returned:

- `composer-2.5`: `RUNNER_STABLE`
- `grok-4.6`: `RUNNER_STABLE`

No review edited repository files or contacted the participant model. Runner
conformance licenses only a separate live-contact decision.

The first review of that later decision exposed one operational defect: the
runner checked whether the evidence destination was unused only after contact.
The runner now reserves that directory before provider preflight, retains the
provider receipt immediately, and refuses an existing destination before any
provider query or live transport. One additional focused test proves the stop.
Composer 2.5 and Grok 4.6 both returned `RUNNER_STABLE` on this final
23-test, 434-suite snapshot.
