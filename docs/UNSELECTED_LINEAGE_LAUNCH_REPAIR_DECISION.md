# Unselected-lineage launch repair decision

Status: **completed engineering repair; retained as history, not as a required
research gate**.

## Current methodological status

The module-form entrypoint and no-contact smoke check were useful repairs. The
separate decision and review ceremony around them is not the current template.
Future pre-contact engineering failures should be diagnosed, tested in
proportion to risk, and repaired directly. Human authorization still governs
participant contact.

## Decision

After this decision passes independent review, repair only the launch surface
of the conformant unselected-lineage runner and prove that surface without
executing a live argument vector.

The consumed contact decision remains consumed. This repair cannot revive it.
The 109-call packet, participant model, prompts, manifest, witness, parser,
environment, branches, schedule, budgets, scorer, and evidence semantics are
out of scope.

## Candidate launch surface

The candidate repository-root entrypoint is module-form execution:

```text
python3 -m contact.unselected_lineage_behavior_contact
```

This form places the repository root on Python's module search path. It avoids
the file-path behavior that made `contact/` the import root and prevented the
runner from importing `micro_environment`.

Implementation must extract one pure CLI configuration function and add one
dedicated `--smoke-no-contact` mode. Invocation with neither `--live` nor
`--smoke-no-contact` must preserve the existing `parser.error` stop. The two
modes must be mutually exclusive. Implementation may not add a path mutation,
`PYTHONPATH` repair, working-directory change, automatic fallback, alternate
participant model, or second live adapter.

## Two separate proofs

### Operating-system launch proof

From the repository root, a test may run exactly:

```text
python3 -m contact.unselected_lineage_behavior_contact --smoke-no-contact
```

That subprocess must exercise the module's real top-level imports and
entrypoint, return 0, and emit one frozen no-contact receipt. The smoke branch
must return immediately after pure argument parsing. It must run before and
without evidence reservation, provider preflight, endpoint access, Docker
commands, tokenizer loading, prompt rendering, live-transport construction, or
participant contact.

Standard output is exactly this canonical JSON plus one newline; standard error
is empty:

```json
{"mode":"smoke_no_contact","protocol_version":"unselected-lineage-behavior-contact-v1","side_effects_entered":false}
```

The subprocess test must bind the interpreter path and version, repository-root
working directory, exact argv, source length and hash, stdout, stderr, and exit
status. It must fail if its argv contains `--live`.

### Live-argument construction proof

A pure function may parse the proposed future live argument vector and return a
configuration value. The test must use the exact candidate evidence and
tokenizer arguments but may not call the module entrypoint or any side-effecting
function.

The parser must reject missing values, an unknown option, simultaneous live and
smoke modes, and a live vector without both required paths. Parsing must not
read or create either path.

This proves only argument construction. It is not execution of the live command
and cannot be cited as provider or participant readiness.

## Side-effect barrier

Focused tests must replace every contact-adjacent callable with a fail-on-use
canary when exercising smoke mode or pure parsing. The canaries must cover
`EvidenceWriter`, `EvidenceWriter.write`, `collect_provider_receipt`,
`shell_command`, `endpoint_receipt`, `PinnedTokenCounter`, `render_chat`,
`DockerInvoker`, `run_packet`, `replay_evidence`, and `urlopen`.

The real subprocess proof may execute only the dedicated smoke argv. It may not
contain `--live`, name the consumed evidence destination, or depend on that
destination already existing. Its frozen receipt must state that no contact-
adjacent surface was entered; that statement is an instrument receipt, not a
model-contact finding.

## Implementation scope

After review stability, implementation may change only:

- `contact/unselected_lineage_behavior_contact.py`, limited to pure extraction
  of the existing argument rules, the mutually exclusive smoke option, its
  immediate frozen receipt, and the preserved bare-argv refusal;
- `tests/test_unselected_lineage_behavior_contact.py`, limited to the two
  proofs, parser failures, exact receipt, and side-effect canaries;
- `README.md`, `contact/README.md`, `tests/README.md`, `docs/README.md`, and
  `docs/PLAN.md`, limited to short launch-repair status and routing text; and
- this decision's implementation and review record.

The existing live branch after argument parsing must remain byte-for-byte
unchanged. In particular, evidence reservation, provider receipt retention,
preflight refusal, tokenizer construction, Docker invoker construction, packet
execution, evidence writing, and replay must keep their present order and code.
No charter, consumed contact decision, evidence account, authority document,
mechanism, specimen, manifest, witness, or unrelated test may change.

Run the focused tests and full repository suite. Then obtain read-only
conformance reviews from Composer 2.5 and Grok 4.6 on the same final source and
tests. Reviewers may inspect retained subprocess output but may not execute
`--live`, run provider preflight, or contact Qwen.

## Boundary after repair

Two `LAUNCH_REPAIR_STABLE` verdicts would establish only that the candidate
module entrypoint reaches a no-contact stop and that its proposed live arguments
can be constructed purely. They would not prove a provider request can succeed,
revive the consumed contact decision, or license a new attempt.

Under the rule then in force, any later participant attempt required explicit
user authorization and a new independently reviewed one-use contact decision
bound to the repaired source. The current method retains the human-
authorization requirement and retires the one-use review sequence.

## Review question

Return `LAUNCH_REPAIR_DECISION_STABLE` only if this decision licenses the
minimum no-contact launch repair, keeps operating-system smoke separate from
pure live-argument construction, makes all contact-adjacent side effects fail
closed, and leaves every participant path behind new user and review authority.

Otherwise return `REVISE_LAUNCH_REPAIR_DECISION` with each scope expansion,
unsafe test path, or hidden route to a corrected execution.

## Review record

Grok 4.6 first returned `LAUNCH_REPAIR_DECISION_STABLE`. Composer 2.5 returned
`REVISE_LAUNCH_REPAIR_DECISION` because the first draft left file scope and
canaries open-ended, made the pure parser optional, did not preserve the bare-
argument refusal explicitly, and allowed CLI edits broad enough to reorder the
live branch.

The repair names every editable file, freezes the smoke receipt, requires pure
and mutually exclusive modes, enumerates all contact-adjacent canaries,
preserves the bare-argument error, and requires the live branch after parsing to
remain byte-for-byte unchanged. Final independent reviews returned:

- `composer-2.5`: `LAUNCH_REPAIR_DECISION_STABLE`
- `grok-4.6`: `LAUNCH_REPAIR_DECISION_STABLE`

Neither review executed a runner command, edited repository files, or contacted
the participant model.

## Implementation and conformance record

The repaired runner is 56,940 bytes with SHA-256
`353dbaf59355a67ca762958c7c760e2ae961af58ccb137bd719a71b33b116c91`.
Its test module is 27,213 bytes with SHA-256
`46a14fbefac92e65117ebe6b8ea33aa21ce0f8c94e33a078d87a22a44e39c9ee`.

The implementation adds only `CliConfig`, pure `parse_cli`, the mutually
exclusive smoke flag, and the frozen early-return receipt. The live branch
after parsing is unchanged. Three added tests cover pure live-argument
construction, in-process fail-on-use canaries, and the real module-form smoke
subprocess.

Final verification:

```text
python3 -m unittest tests.test_unselected_lineage_behavior_contact -q
Ran 26 tests ... OK

python3 -m unittest discover -s tests -q
Ran 437 tests ... OK
```

Composer 2.5 and Grok 4.6 independently returned `LAUNCH_REPAIR_STABLE` on the
same source and tests. Neither reviewer executed a runner command. This record
did not itself authorize provider preflight or participant contact.
