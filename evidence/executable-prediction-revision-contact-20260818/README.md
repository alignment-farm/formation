# Executable-prediction revision contact evidence

This directory is the complete record of the one contact licensed by the
[executable-prediction revision charter](../../docs/EXECUTABLE_PREDICTION_REVISION_CHARTER.md).
The run completed on 2026-08-18. It establishes no Formation or validation
verdict.

## Outcome

The contact completed all 35 logical calls in 35 physical attempts. There was
no retry, HTTP error, prompt repair, resampling, or conditional omission. The
disposable interface returned a valid scalar, both acquisition calls returned
content, and every scheduled rule call completed.

World K produced the packet's narrowest positive observation. Its first
successor rule changed a wrong primary-test prediction into the correct one.
The byte-identical repeat returned the exact same rule, and none of the frozen
first-cycle alternative-explanation controls reproduced its complete nine-case
prediction vector.

That observation is not a Formation result. The rule was correct on only the
one primary test. It was correct on neither transfer case, neither copy-control
case, neither non-transfer case, nor the later revision case. World J did not
produce the same pattern. Repeated calls elsewhere in the packet often changed
their rules. One instance in one world cannot separate consequence-associated
revision from sampling variation.

The terminal verdicts remain exactly:

```json
{"formation_verdict":null,"validation_verdict":null}
```

## What the contact tested

Each fresh world first asked the cold model to write one rule that predicted an
opaque result from three public input fields. The runtime kept the exact model
string. An independent environment then tested the rule on a hidden input and
issued the actual result. A later cold call received the parent rule, the test,
the parent's prediction, and the external result, then wrote a successor rule.

The frozen interpreter accepted two kinds of rule:

- A string beginning with the exact `RULE_AST_V1` marker could become a
  conditional rule if its following JSON matched the small rule language.
- Every other returned scalar remained executable as a literal prediction on
  all cases. JSON-looking text without the exact marker was not repaired or
  silently promoted into a conditional rule.

This total rule language kept awkward and malformed attempts in the experiment
instead of rejecting the model before contact. Across the 36 authored rule
slots, including the parent and successor fields in same-response calls, 11
were recognized conditional rules and 25 were literal rules. No model content
was unavailable.

## World J

The acquisition action was wrong: the model returned `zafren`, while the
environment returned `ulmec`.

The first parent looked like JSON but omitted the exact rule marker. It was
therefore a literal prediction and was wrong on all nine fixed cases. The
selected successor also omitted the marker, remained a literal prediction, and
was wrong on all nine cases.

The byte-identical repeat of that successor request did not reproduce the
selected successor. It added the marker and became a conditional rule that was
correct on the primary test only. The result-withheld control returned that
same primary-correct rule. This means the corrected repeat cannot be attributed
to receiving the external result.

In the later cycle, the parent predicted the new test in scope and disagreed
with the new external result. The selected successor, its repeat, and the
result-withheld control all reproduced the first selected successor exactly.
The rule did not change and was wrong on the later test. World J therefore
showed no later revision after eligible counterevidence.

## World K

The acquisition action was correct: the model returned `vesan`, and the
environment returned `vesan`.

The first parent was a recognized conditional rule. It was wrong on the
primary test. The selected successor changed the rule and was correct on that
test. Its byte-identical repeat returned the exact same string and the exact
same prediction vector.

The selected successor's complete vector was not reproduced by the
result-withheld, parent-withheld, same-response, repeated-occurrence,
deterministic-restatement, visible-material, or static-instruction conditions.
This is a consequence-associated and repeatable difference within World K's
first cycle. It remains an atomic observation because the mirrored world did
not reproduce it and none of the prospective transfer cases became correct.

The later World K parent did not predict the later test in scope. The new
external result was therefore not counterevidence to that parent. The selected
later successor changed, but its byte-identical repeat changed again. The
result-withheld control instead reproduced the parent rule exactly. These facts
do not support a later revision claim.

## Controls and sampling

The controls rule out several simple equal-output descriptions of World K's
first selected successor. They do not turn one draw into causal proof.

- Repeating the original parent request changed the rule in both worlds.
- Repeating the selected successor request reproduced it in World K but not in
  World J.
- Withholding the external result failed to reproduce either selected
  successor.
- The same-response conditions never made their complete parent and successor
  vectors collapse into the selected two-call sequence.
- Repeated occurrence, deterministic restatement, visible material, and static
  instruction never reproduced either selected successor's complete vector.
- No selected successor was correct on a transfer or copy-control case.

The static model calls began with the exact marker, but the text after it was
not a valid single rule in the frozen language. The total parser therefore kept
each complete string as a literal rule. Both were wrong on all nine cases. This
is the observed same-model static condition, not the deterministic instrument
ceiling. The separate protocol-authored static rules correctly represented all
nine oracle results in each world; they show that the frozen rule language
could express the target function, not that the model learned it.

## Integrity and cost

- Model: `ai/qwen3:14B-Q6_K`
- Artifact digest:
  `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Provider: Docker Model Runner v1.2.6 with the frozen llama.cpp backend
- Docker Desktop: 4.87.0; Docker Engine: 29.7.2
- HTTP results: 35 responses with status 200
- Logical calls: 35 of 35
- Physical attempts: 35 of 38
- Prompt tokens: 14,842
- Completion tokens: 2,599
- Authored rule slots: 36
- Recognized conditional rules: 11
- Literal rules: 25
- Unavailable model contents: 0

Apart from this README, the directory contains 148 machine files: provider and
protocol receipts, the frozen case manifest and leakage witness,
protocol-authored static rules, the terminal summary, integrity bindings, and
four retained artifacts for every call. The
[integrity report](integrity.json) checked all 35 attempts, regenerated the
deterministic request and logical records from the retained raw responses, and
reproduced the protocol proposals and summary. The case manifest and witness
also matched their frozen hashes.

## Interpretation boundary

This contact does not show that Qwen acquired a reusable rule, that the
external result caused World K's corrected successor, or that the mechanism
can transfer or revise knowledge. It also does not show that the mechanism
cannot work. The packet contains two kinds of evidence that must remain
separate:

1. World K's first selected successor was a stable, control-distinct correction
   on one primary case.
2. The correction did not transfer, did not recur in World J, and occurred in a
   packet where many identical requests returned different functions.

The next problem is therefore not how to admit a better model or tighten the
output parser. It is how to distinguish a consequence-associated function
change from ordinary sampling variation, then ask whether any stable change
extends to cases that require the same relation without copying the tested
answer. That problem must be stated and reviewed before any new mechanism,
runner, or model call is licensed.

The charter and contact decision are consumed. This record licenses no rerun,
prompt repair, model search, successor contact, later influence test,
validation packet, or Formation claim.

## Interpretation review

Composer 2.5 and Grok 4.6 independently checked this account against the
charter, terminal summary, integrity report, and retained logical records. The
first pass found one factual error: both static calls carried the marker, but
their following text was not a valid single rule. The account had incorrectly
said they omitted the marker. The same pass also asked that World K's
control-distinct observation be bounded to its first-cycle
alternative-explanation controls because later calls could reproduce the
earlier rule.

The repaired account now separates literal JSON-looking outputs from
recognized conditional rules, selected draws from their repeats, eligible
later counterevidence from out-of-scope results, and atomic observations from a
Formation claim. On the same repaired account, exact model identifiers
`composer-2.5` and `cursor-grok-4.6-high-fast` both returned
`INTERPRETATION_STABLE`. Neither review contacted the participant model.
