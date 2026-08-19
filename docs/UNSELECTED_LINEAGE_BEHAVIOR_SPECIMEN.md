# Unselected lineage behavior deterministic specimen

Status: **complete; 14 focused tests and the 411-test repository suite pass,
and two independent implementation reviews return `SPECIMEN_CONFORMS`; only a
separate strict-budget charter decision is licensed, not a runner, model call,
validation packet, or Formation claim**.

## Decision

Implement the minimum deterministic machine needed to test the reviewed
[unselected lineage behavior mechanism](UNSELECTED_LINEAGE_BEHAVIOR_MECHANISM.md)
before any participant contact is chartered.

The specimen must prove that the environment can score committed opaque actions
without choosing them, that every case role is frozen from oracle geometry,
that all six information paths have exact non-collapsing semantics, and that
unavailable or invalid proposals remain in complete denominators.

It must not simulate model reasoning, author a useful intermediate, choose a
live prompt, or tune a case after observing output.

## Implementation boundary

Add two separate modules:

- `micro_environment/unselected_lineage_behavior.py` owns only hidden profile
  physics, public device state, total proposal availability, and factual action
  results after commitment.
- `unselected_lineage_specimen.py` owns deterministic opaque fixture
  construction, pre-result occurrence and result projections, branch
  foregrounds, public action-request surfaces, leakage checks, and the
  harness-only complete scorer.

Add `tests/test_unselected_lineage_behavior.py` for prospective deterministic
witnesses. Update only the nearest READMEs, package exports, project routing,
and test count after conformance.

The environment module may import only standard-library value types. It may not
import branch names, fixture roles, scorers, runtime objects, model clients, or
contact code.

## Frozen specimen fixture

The deterministic witness uses four synthetic blocks. They are specimen data,
not future contact cases.

- Both family profiles occur twice.
- Acquisition target direction is up in two blocks and down in two blocks.
- Profile and acquisition direction are fully crossed.
- Every block has one acquisition-use case, one opposite-direction transfer
  case, one already-current non-transfer case, and one copy-control case.
- Every device uses fresh opaque action strings.
- All six later branches receive all four roles.

The generator uses one versioned seed and domain-separated identifiers. The
tests must prove uniqueness and counterbalance rather than treating a saved
example as sufficient.

## Environment obligations

The environment must:

1. accept only exact immutable profile, state, and proposal-receipt types;
2. distinguish provider-unavailable content from available empty content;
3. return `not_applied` for unavailable content;
4. return a factual refusal for available but unlisted or malformed action
   text;
5. apply `hold`, first control, or second control only after proposal
   commitment;
6. use the hidden profile to compute movement only, never to produce an action;
7. return selected slot, pre-state, post-state, movement direction, and target
   status only for valid applications;
8. preserve the input state without mutation; and
9. expose no branch, case role, expected action, intermediate, lesson, or scorer
   field.

Tests must exhaust both profiles, up/down target directions, all permitted
actions, available empty, unavailable, foreign, and malformed proposals.

## Surface obligations

The specimen layer must produce one canonical UTF-8 JSON representation for
each surface.

The shared authorship occurrence contains only family, device, pre-state,
target, ordered controls, `hold`, proposal availability, and exact proposal
string. Tests must prove that it excludes application status, selected slot,
post-state, movement, refusal, inferred profile, and correctness.

The exposed result contains the exact environment application facts. The
withheld result is one versioned sentinel and contains no environment fact.
The raw foreground is the canonical pair of shared occurrence and exposed
result. The static foreground is the frozen true family lesson and contains no
device or action string.

All later requests use one generic `retained_material` string and one common
public device/action responsibility. Branch names and hidden roles never enter
the request.

## Six-path obligations

For one supplied result-exposed intermediate and one supplied result-withheld
intermediate, the specimen must construct:

| Branch | Delivered foreground | Hidden retained intermediate |
| --- | --- | --- |
| No persistence | empty | none |
| Raw persistence | exact raw occurrence and result | none |
| Result-withheld authorship | exact withheld intermediate or empty | same if available |
| Result-exposed authorship | exact exposed intermediate or empty | same if available |
| Ablation | empty | exact same exposed intermediate if available |
| Static instruction | exact static lesson | none |

Tests must show that result-exposed delivery and ablation cite one identical
intermediate receipt, not two draws. No-persistence and ablation later requests
must be byte-identical for the same case. Unavailable intermediates produce
empty foregrounds without losing hidden availability records or assignments.

## Prospective-role obligations

The generator and oracle must prove before any simulated proposal:

- acquisition-use direction equals the frozen oracle-correct acquisition
  direction;
- transfer requires the opposite oracle slot;
- already-current requires `hold` under both profiles;
- copy-control correct action bytes are absent from every frozen pre-contact
  acquisition, request, result-schema, sentinel, raw-field-name, and static-
  lesson byte surface; and
- later roles do not change after wrong, invalid, empty, or unavailable
  acquisition proposals.

Live proposal or intermediate collisions are diagnostic facts only. They may
not relabel a case.

## Scorer obligations

The scorer receives an exact expected assignment set and one retained later-
action record per assignment. It must:

- refuse duplicates, omissions, extra coordinates, unknown branches, and
  unknown roles;
- report every branch by every primary role;
- retain provider availability, action-interface validity, environment
  application validity, correctness, invalid/unavailable counts, and exact
  action distributions;
- report the full unstratified denominator and acquisition-status strata;
- keep invalid, unavailable, wrong, and empty actions assigned; and
- compute no Formation, validation, durability, revision, or compound success
  verdict.

The scorer may call the deterministic oracle after commitment. It cannot write
a request, foreground, intermediate, or action.

## Required tests

Focused tests must cover at least:

1. environment immutability, total proposal states, and exact refusals;
2. both profiles and target directions;
3. fresh identifiers and counterbalance;
4. pre-contact role freeze and role invariance after every acquisition status;
5. closed occurrence/result field separation;
6. raw and static foreground authorship boundaries;
7. all six delivered and hidden-material paths;
8. exact exposed/ablation identity and no-persistence/ablation request identity;
9. common later action surface and exclusion of branch and role labels;
10. copy-control leakage witnesses and report-only live collisions;
11. complete scorer reports over the 4-block × 6-branch × 4-role matrix; and
12. scorer refusal of missing, duplicate, extra, or malformed assignments.

Run the focused tests and full repository suite. Then obtain read-only
implementation reviews from exact model identifiers `composer-2.5` and
`cursor-grok-4.6-high-fast` on the same final code and tests.

## Boundary after implementation

Two `SPECIMEN_CONFORMS` verdicts would establish only deterministic environment,
surface, fork, leakage, and scorer readiness. They would license a separate
decision about whether to draft a strict-budget exploratory charter.

They would not license a participant model, exact live prompts or cases, a
numeric contact budget, runner, model call, validation packet, or Formation
claim. A specimen defect returns to this implementation boundary; it does not
license a mechanism change or easier case.

## Implementation and review record

The environment physics are implemented in
[`unselected_lineage_behavior.py`](../micro_environment/unselected_lineage_behavior.py).
Deterministic surfaces, fixture construction, six-path foregrounds, and the
complete scorer are implemented in
[`unselected_lineage_specimen.py`](../unselected_lineage_specimen.py). Fourteen
focused tests cover the required obligations in
[`test_unselected_lineage_behavior.py`](../tests/test_unselected_lineage_behavior.py).

Verification before review:

```text
python3 -m unittest tests.test_unselected_lineage_behavior
Ran 14 tests ... OK

python3 -m unittest discover -s tests
Ran 411 tests ... OK (skipped=1)
```

Independent code review is pending.

The first read-only review round used exact model identifiers `composer-2.5`
and `cursor-grok-4.6-high-fast`. Both returned `REVISE_SPECIMEN`. Composer found
that the correct-action oracle lived inside the environment module and was
re-exported from the environment package, which let hidden profile knowledge
produce an action on the wrong side of the authority boundary. Grok found that
the six-path tests did not bind raw and static delivered bytes to their
canonical constructors or exclude every later device and control token. Both
also identified malformed-record hardening opportunities.

The repair moves the oracle entirely into the specimen/scorer module, removes
its environment export, and adds a source witness that no oracle entry point
remains. The tests now bind all six delivered and hidden-material cells, retain
unavailable intermediate receipts, and exclude every later token from raw and
static foregrounds. The scorer also recomputes environment physics and refuses
a well-typed but impossible result. The focused 14 tests and full 411-test suite
still pass.

Final read-only verdicts on that repaired snapshot:

- `composer-2.5`: `SPECIMEN_CONFORMS`
- `cursor-grok-4.6-high-fast`: `SPECIMEN_CONFORMS`

These verdicts establish deterministic specimen readiness only. Neither review
contacted the participant model.
