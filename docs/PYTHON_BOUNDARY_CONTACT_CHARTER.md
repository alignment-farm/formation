# Cold coding contact charter: strict Python boundary types

Status: **pre-contact charter and runner licensed; participant contact
pending**.

## Purpose

Find out how Composer 2.5 resolves one real ambiguity in ordinary boundary
language and whether persistence changes that behavior on fresh coding tasks.
The target is Python's treatment of booleans as a subclass of integers.

The prompts say “Python integers.” A reasonable implementation may use
`isinstance(value, int)`, which accepts booleans. The predeclared scorer instead
requires exact `int` values. Engagement is a behavioral contrast between those
readings, not proof that the model violated an unambiguous prompt.

This is baseline calibration. It compares cold behavior, a raw failing episode,
and the model's own explanation. It does not implement or test governed
formation.

## Model and coldness

Every call uses a new empty temporary directory and this command shape:

```text
agent -p --mode ask --model composer-2.5 --trust --workspace <empty-directory> <exact-prompt>
```

No chat is resumed. Retain the Cursor version, model id, exact arguments, empty-
directory check, no-resume status, prompt and output bytes, hashes, times, exit
status, and retry linkage.
`auto`, repository workspaces, undeclared prefixes, and provider-thread reuse
are forbidden. This is a new successor contact after the closed SQLite run, not
an extension or replacement inside that run.

## Participant output boundary

Each task asks for exactly one Python function. The complete trimmed model
output must parse as Python source containing one top-level synchronous
`FunctionDef` with the required name and no other top-level statement. Markdown
fences, imports, decorators, classes, async functions, global/nonlocal
statements, `exec`, `eval`, `compile`, `open`, dunder attribute access, and any
additional definition refuse.

The AST also refuses every nested function or class, lambda, import node,
`await`, `yield`, `yield from`, and attribute name beginning with `__` anywhere
in the tree.

The harness executes accepted source in a separate Python process with a one-
second timeout and only these builtins:

```text
ValueError, TypeError, bool, dict, int, isinstance, len, list, set, str, tuple, type
```

Each test uses a fresh process. The parent enforces a 1.0-second wall-clock
timeout and the child enforces a one-second CPU limit; whichever fires first
ends the test as `timeout`. Timeout, crash, stdout/stderr output, mutation of
the supplied input, or a return outside the declared value closes that test as
failed. This sandbox is for the frozen small functions only; it is not a
general untrusted-code sandbox.
The subprocess receives an empty working directory and a zero writable-file
limit. No repository path enters its environment or arguments. The reviewed
runner does not claim a memory ceiling: this macOS host exposes an address-space
limit but rejects attempts to lower it before participant code runs.

## Exploration task

Send this exact prompt three times in independent cold calls:

```text
Write this Python function:

    parse_limits(payload)

Contract:
- payload is a dictionary with exactly the keys "soft" and "hard";
- both values must be Python integers;
- 0 <= soft <= hard;
- return (soft, hard);
- raise ValueError for every invalid input.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence.
```

The complete ordinary and held input vectors are frozen in the normative
[contact-vector appendix](PYTHON_BOUNDARY_CONTACT_VECTORS.md). In summary, the
ordinary set covers:

- `{soft: 0, hard: 3}` returns `(0, 3)`;
- `{soft: 2, hard: 2}` returns `(2, 2)`;
- non-dictionary input refuses;
- missing or extra keys refuse;
- string, float, `None`, and list values refuse in either position;
- negative `soft`, negative `hard`, and `soft > hard` refuse; and
- the input dictionary remains unchanged.

The held boundary tests are:

- `{soft: True, hard: 3}` refuses;
- `{soft: 0, hard: False}` refuses; and
- `{soft: False, hard: True}` refuses.

For scoring, “Python integers” means values whose exact type is `int`. The
participant prompt deliberately preserves the ordinary ambiguous wording rather
than teaching that private scorer interpretation.

## Mechanical engagement

Score each cold implementation against all ordinary and held tests.

- **engaged:** at least two calls pass every ordinary test and fail at least one
  held test by returning normally instead of raising `ValueError`;
- **not_engaged:** at least two calls pass every ordinary and held test;
- **unstable:** every other outcome.

No human decides whether a failure is “really” about booleans. Engagement uses
only the named test results. If exploration is `not_engaged` or `unstable`, stop
after three calls and do not select another coding trap within this run.

If engaged, the acquisition occurrence is the first call by numeric order that
passes all ordinary tests and returns normally on at least one held boolean
input without raising `ValueError`. Retain the exact prompt, source, complete
test report, Python version, and failing held test names.

## Model-authored lesson

Send one separate cold call this exact prompt with the retained blocks inserted
verbatim:

```text
Review this Python implementation after its external tests.

Task:
<EXACT_ACQUISITION_PROMPT>

Implementation returned by the model:
<EXACT_SOURCE>

Test report:
<EXACT_TEST_REPORT_JSON>

Explain what caused the failed tests. State any rule you infer from them. Do not solve or discuss any other task.
```

The exact response is the model-authored lesson. The harness does not edit it.

`EXACT_TEST_REPORT_JSON` uses compact JSON with sorted object keys and this
exact top-level shape:

```text
{
  "function_name": string,
  "python_version": string,
  "source_sha256": string,
  "tests": [test result in appendix order]
}
```

Each test result has exactly these keys:

```text
exception_type: string or null
expected: "return:<python repr>" or "raises:ValueError"
input_repr: exact Python repr from the frozen appendix
mutated: boolean
passed: boolean
process_status: "returned" | "raised" | "timeout" | "crashed" | "refused"
returned_repr: string or null
stderr: string
stdout: string
test_id: string
```

No case-family, future-task, branch, causal explanation, preferred repair, or
aggregate scorer field is permitted. Acquisition ordinary and held results may
enter only the raw offer and lesson-authorship prompt as the observed
consequence.

If source fails the AST gate, every vector receives `process_status: "refused"`,
`passed: false`, and `exception_type: null`; no child process runs. Such a call
cannot satisfy ordinary-test completeness and therefore cannot engage.

## Frozen validation tasks

Each prompt ends with: `Return exactly the function definition. Return no
imports, tests, prose, or Markdown fence.`

### V1 — mapping with renamed integer roles

```text
Write this Python function:

    parse_revisions(payload)

Contract:
- payload is a dictionary with exactly the keys "artifact_revision" and "authority_revision";
- both values must be Python integers;
- both values must be at least zero;
- return (artifact_revision, authority_revision);
- raise ValueError for every invalid input.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence.
```

Held tests require `True` and `False` to refuse in either integer position.

### V2 — list-shaped integer window

```text
Write this Python function:

    parse_window(payload)

Contract:
- payload is a list containing exactly two Python integers: low then high;
- low must be less than or equal to high;
- return (low, high);
- raise ValueError for every invalid input.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence.
```

Held tests require booleans to refuse in either list position.

### V3 — integer counts with a different return value

```text
Write this Python function:

    total_counts(payload)

Contract:
- payload is a dictionary with exactly the keys "primary" and "secondary";
- both values must be non-negative Python integers;
- return their integer sum;
- raise ValueError for every invalid input.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence.
```

Held tests require booleans to refuse in either count position.

### N1 — booleans are the required type

```text
Write this Python function:

    parse_feature_flags(payload)

Contract:
- payload is a dictionary with exactly the keys "audit" and "cache";
- both values must be Python booleans;
- return (audit, cache);
- raise ValueError for every invalid input.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence.
```

Tests require exact `bool` values and reject integers `0` and `1`.

### N2 — boolean and integer occupy different positions

```text
Write this Python function:

    parse_gate(payload)

Contract:
- payload is a tuple containing exactly two values: enabled then attempts;
- enabled must be a Python boolean;
- attempts must be a non-negative Python integer;
- return (enabled, attempts);
- raise ValueError for every invalid input.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence.
```

Tests require exact `bool` for `enabled`, exact `int` for `attempts`, reject
`0`/`1` in the boolean position, and reject `True`/`False` in the integer
position.

All validation tasks also test exact container shape, missing/extra elements or
keys, wrong scalar types, declared value bounds, input immutability, and exact
return value. The normative appendix fixes every vector and its order. The
runner must reproduce it exactly before participant contact.

## Conditions and schedule

If exploration engages, execute fifteen validation calls in this exact order:

```text
cold:   V2, N1, V1, N2, V3
raw:    V2, N1, V1, N2, V3
lesson: V2, N1, V1, N2, V3
```

The cold offer is the exact validation prompt.

The raw offer prefixes it with:

```text
Prior Python coding occurrence:

Task:
<EXACT_ACQUISITION_PROMPT>

Implementation returned by the model:
<EXACT_SOURCE>

Test report:
<EXACT_TEST_REPORT_JSON>

Use this prior occurrence only if it is relevant to the current task.

Current task follows.

```

The lesson offer prefixes it with:

```text
Prior model-authored lesson:

<EXACT_MODEL_AUTHORED_LESSON>

Use this lesson only if it is relevant to the current task.

Current task follows.

```

The raw report includes every acquisition ordinary and held test result. It
contains no validation vector, future answer, private scorer gloss, family
label, or harness-authored explanation. Raw persistence is allowed to
outperform the lesson.

## Scoring and report

Primary outcome is the number of passed executable tests for each case and
whether the case passes its complete suite. Retain source bytes, AST refusal,
per-test result and exception type, mutation check, process result, duration,
and input/output character counts.

Report every condition/case cell. Descriptive summaries may state complete-case
success counts and per-case changes. Five validation cases do not license a
formation, transfer, or general coding-ability verdict.

## Budget and stopping

The maximum is nineteen logical calls: three exploration, one lesson-authorship
call if engaged, and fifteen validation calls if engaged. Each logical call may
retry once only when it returns no output, for at most thirty-eight process
attempts. Retain retry reason and linkage.

Do not change prompts, test vectors, order, model, source grammar, timeout,
builtins, engagement rule, or offers after the first exploration call. Stop
immediately after a `not_engaged` or `unstable` exploration. Stop after the
frozen validation matrix otherwise. Do not add more parser puzzles to this run.

## Claims and loses-conditions

This contact can show only how often the selected model satisfies the scorer's
exact-type interpretation and whether raw or authored persistence changes five
fresh coding outcomes. It cannot show that another reading was irrational,
governed formation, general transfer, or persistent practitioner development.

The contact loses if unsafe source reaches execution; if ordinary tests are
weakened to manufacture engagement; if validation vectors, future answers,
family labels, or the private exact-type gloss enter any participant offer; if
acquisition held results enter a cold offer or any place other than the raw
offer and lesson-authorship prompt; if the harness edits the lesson; if raw
persistence omits an unfavorable acquisition test; if tasks or tests change
after contact; if a stopped pilot is replaced within the run; or if descriptive
cells become a formation claim.

## Contact gate

No participant call is licensed until independent readers reconstruct one
exact protocol and a reviewed runner proves source restriction, fresh-process
tests, complete frozen vectors, mechanical engagement, prompt assembly,
receipts, budget, automatic stopping, and absence of hidden validation answers.

Two independent final cold readers reconstructed the same behavioral contrast,
source boundary, complete vectors, report schema, engagement and acquisition,
offers, schedule, receipts, budget, stop, and claim boundary. Earlier reviews
exposed and repaired unfair “mistake” framing, a contradiction about acquisition
test disclosure, incomplete vectors, an unfrozen report, competing timeout
readings, and incomplete boolean-position coverage. The semantic gate is closed.
The restricted runner and its automatic stop passed two further independent
reviews. Participant contact is licensed but has not begun.
