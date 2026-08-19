# Unselected lineage behavior contact decision

Status: **historical decision; its one-use interpretation is retired; the
repaired contact later completed under explicit user authorization**.

## Current methodological status

This document records the exact rule used for the first launch attempt. That
attempt failed during import before provider preflight or participant contact.
The project no longer treats such a mechanical failure as a consumed scientific
experiment. It is engineering history, not evidence about Formation and not a
template for future exploratory contact.

The repaired runner later completed the intended 109 calls. See the
[evidence account](../evidence/unselected-lineage-behavior-contact-20260819-contact/README.md).
The original decision and execution record below remain unchanged in meaning so
the route can be audited.

## Decision

After this decision passes independent review, execute the independently
reviewed [charter](UNSELECTED_LINEAGE_EXPLORATORY_CHARTER.md) once with the
independently conformant runner.

This is an operational authorization, not a prediction. Literal, malformed,
empty, unavailable, awkward, variable, wrong, or apparently useful model
behavior all complete their assigned observations. None is an admission
failure, and none licenses repair or another sample.

## Exact execution

The authorized runner is
[`unselected_lineage_behavior_contact.py`](../contact/unselected_lineage_behavior_contact.py):

```text
UTF-8 length: 55951 bytes
SHA-256: 8c8b9f69a5913810a4850fee65d750968287c2d4057d95edb2085efc5f5ca679
```

The tokenizer is the existing local Qwen tokenizer:

```text
/Users/macos-user/Library/Caches/formation/Qwen3-14B/7d3da9c56f02b22d31dc1ca97c7ee628d1e2e237/tokenizer.json
UTF-8 length: 11422654 bytes
SHA-256: aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4
```

The evidence destination is exactly:

```text
evidence/unselected-lineage-behavior-contact-20260818
```

It must not exist before execution. From the repository root, the only
authorized participant command is:

```text
python3 contact/unselected_lineage_behavior_contact.py --live --evidence-dir evidence/unselected-lineage-behavior-contact-20260818 --tokenizer-json /Users/macos-user/Library/Caches/formation/Qwen3-14B/7d3da9c56f02b22d31dc1ca97c7ee628d1e2e237/tokenizer.json
```

No prompt, manifest, witness, model, endpoint, setting, parser, proposal rule,
environment physics, branch material, call order, retry rule, scorer, report,
or budget may change between review and execution.

## Preconditions

The runner must atomically reserve the unused evidence destination before
collecting provider preflight or constructing live transport. If the directory
already exists, the attempt stops without querying the provider or contacting
the participant model.

Immediately before the disposable call, the runner must reproduce and retain
the charter's provider bindings: exact Qwen artifact and digest, Docker Model
Runner client and server, Docker Desktop and Engine, llama.cpp backend and
digest, model inspection, endpoint reachability, 4,100-byte chat template,
Jinja2 3.1.6 renderer, and tokenizer. Any mismatch stops before a participant
request. No substitute model, provider, renderer, tokenizer, or evidence path
is allowed.

The runner must validate each rendered request before transport. The published
manifest and independently reconstructed leakage witness must match before the
disposable call. The focused 23-test suite and full 434-test suite must remain
clean on the authorized source.

A read-only preflight on 2026-08-18 matched all current provider bindings. That
observation does not replace the fresh preflight inside the authorized command.

## Execution and closure

If the disposable JSON action interface fails, retain exactly that call and
stop. If it passes, continue every preassigned history through the 109-logical-
call schedule unless the 112-physical-attempt or 6,048-completion-token
contingency ceiling prevents transport. Unavailable calls remain assigned and
counted. Do not repair, resample, reorder, extend, or select an alternate model.

After execution, the runner must regenerate the packet from retained raw
request and response bytes and compare every deterministic projection. A replay
mismatch invalidates interpretation and authorizes no repair or rerun. If
integrity passes, write a plain-language evidence account with complete
denominators, atomic comparisons, instrument differences, and the exact null
terminal verdicts:

```json
{"formation_verdict":null,"validation_verdict":null}
```

This decision is consumed by the first authorized execution attempt, including
a pre-contact refusal or disposable stop. No outcome licenses a rerun,
successor model, validation packet, or Formation claim. The next boundary is
interpretation of this one closed attempt.

## Review question

Return `CONTACT_DECISION_STABLE` only if this decision authorizes exactly one
execution of the reviewed packet, reproduces all provider and artifact bindings
before transport, preserves every total continuation and stopping rule, and
cannot silently repair, substitute, expand, or rerun after participant output.

Otherwise return `REVISE_CONTACT_DECISION` with each concrete ambiguity,
missing precondition, or path to unreviewed contact.

## Review record

The first identical read-only reviews used `composer-2.5` and `grok-4.6`.
Grok returned `CONTACT_DECISION_STABLE`. Composer returned
`REVISE_CONTACT_DECISION` because the pinned runner reserved the evidence
destination only after participant transport. A pre-existing directory could
therefore consume the packet before evidence was written.

The repair moved atomic evidence reservation before provider preflight or live
transport, retained the provider receipt immediately, added a focused
no-preflight/no-transport test, and rebound this decision to the repaired runner
hash. Both reviewers then rechecked the runner and returned `RUNNER_STABLE`.

Final independent reviews of this repaired decision returned:

- `composer-2.5`: `CONTACT_DECISION_STABLE`
- `grok-4.6`: `CONTACT_DECISION_STABLE`

Neither review edited repository files or contacted the participant model.

## Execution record

The exact authorized command was invoked once. Python failed while importing
the runner, before `main()` began:

```text
ModuleNotFoundError: No module named 'micro_environment'
```

Running the file by path placed `contact/`, not the repository root, at the
front of Python's module search path. The runner therefore could not import its
root-level `micro_environment` package. Exit status was 1. The evidence
destination had not yet been created, provider preflight did not run, live
transport was not constructed, and Qwen received no request.

The tests exercised the runner as an imported module, and the reviews inspected
the bound command without executing its non-contact launch path. They therefore
missed the difference between module import and file-path execution.

Under the then-current one-use closure rule, this pre-contact refusal was
recorded as consuming the decision. The post-attempt
[evidence account](../evidence/unselected-lineage-behavior-contact-20260818/README.md)
records the shell-level result. At the time, that document authorized no
corrected command or rerun. The current methodological status at the top of
this document supersedes that procedural interpretation.
