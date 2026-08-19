# Exact-draft challenge exploratory contact evidence

This directory is the complete record of the one contact licensed by the
[exact-draft challenge charter](../../docs/DRAFT_CHALLENGE_EXPLORATORY_CHARTER.md).
The run completed on 2026-08-18. It establishes no Formation or validation
verdict.

## Outcome

The contact completed all 39 logical calls in 39 physical attempts. There was
no retry, HTTP error, prompt repair, resampling, or conditional omission. The
disposable interface and both acquisition calls returned valid actions. Both
fresh worlds therefore completed every scheduled candidate call.

Neither world earned `draft-challenge-associated exact candidate revision` or
`draft-challenge-associated exact candidate withdrawal`.

- In World G, the two exact-draft challenge replies differed. The required
  stable challenge anchor was absent. One static-review reply and one
  prompt-mass reply were also malformed.
- In World H, both exact-draft challenge replies exactly repeated the source
  draft. An exact source match is not a revision. Static review,
  same-response drafting, and deterministic restatement also varied between
  their two samples.

The terminal verdicts remain exactly:

```json
{"formation_verdict":null,"validation_verdict":null}
```

## What happened

The disposable interface returned `hold`. In both acquisition worlds, the
model selected the two listed controls in their displayed order. The
environment applied each complete pair without intermediate model feedback and
issued the two-step occurrence used by every candidate condition.

The first direct candidate in each world remained the source draft. Neither was
selected for quality:

| World | Exact retained source content |
| --- | --- |
| G | `{"change":"7e81cf4ce9afe7ad","counterevidence":null}` |
| H | `{"change":"a3dd902b2fe11658","counterevidence":"movement_direction"}` |

Both direct conditions were internally stable. The byte-identical withheld
requests reproduced the direct candidate exactly in both worlds. This passes
the packet’s observable cold-call audit; it does not prove that the provider
had no hidden state.

The challenge conditions then separated:

| Frozen observation | World G | World H |
| --- | --- | --- |
| Direct and withheld | stable exact match | stable exact match |
| Exact draft replay | stable exact source candidate | stable exact source candidate |
| Exact draft challenge | two parseable but different candidates | stable exact source candidate |
| Static review | one malformed, one parseable | two parseable but different candidates |
| Same-response draft and review | two parseable but different candidates | two parseable but different candidates |
| Repeated occurrence | two parseable but different candidates | stable exact source candidate |
| Deterministic restatement | stable | two parseable but different candidates |
| Prompt-mass control | one malformed, one parseable | stable copy of the control string |
| Mechanism label | unavailable | unavailable |

World G’s two exact challenges kept the same action token as `change` but wrote
different counterevidence. Because the identical requests did not reproduce
one exact candidate, the packet cannot call either output a stable revision.

World H’s exact challenges reproduced the complete source candidate, byte for
byte for byte. Exact replay reproduced it after receiving the source draft.
Repeated occurrence also reproduced it, but that request contained no draft;
the same candidate could therefore arise from the occurrence and default
authorship responsibility alone. Separately, the prompt-mass condition stably
copied its deterministic uppercase control string into `change`. The record
keeps both default authorship and visible-material copying as live explanations.
It does not show that the model retained or revised an experience-derived
belief.

## Parsing and governance

Thirty-four of the 36 candidate replies were parseable. Two World G replies
were malformed JSON and were retained without retry. The frozen lexical
governor admitted none of the 34 parseable candidates:

- 32 copied an acquisition control token in `change`;
- 11 also copied an acquisition control in `counterevidence`; and
- 9 used null or another nonempty-string failure for `counterevidence`.

These refusal counts overlap. The governor did not judge whether a candidate’s
prose was true or useful. It checked only the declared text-form requirements,
including the rule against reusing one device’s opaque action name as a
reusable family relation. Governance ran only after all authorship calls had
completed and therefore could not affect the source draft, challenge, or later
requests.

## Prompt-mass instrument

The local renderer applied the 4,100-byte chat template from the verified model
inspect receipt with tools and thinking controls omitted as chartered. It used
the pinned `Qwen/Qwen3-14B` tokenizer through `tokenizers-0.23.1` and rendered
the template through `jinja2-3.1.6`.

The source-blind constructor found one deterministic uppercase control string
for each world before downstream calls. Local and provider token counts matched
exactly:

| World | Exact challenge prompt tokens | Mass-control prompt tokens | Prefix length |
| --- | ---: | ---: | ---: |
| G | 609 | 609 | 38 |
| H | 633 | 633 | 44 |

This repairs the earlier token-measurement instrument. It does not make either
candidate comparison positive. World G’s mass replies were not both parseable;
World H’s stable mass reply copied the control string.

## Integrity and cost

- Model: `ai/qwen3:14B-Q6_K`
- Artifact digest:
  `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Provider: Docker Model Runner v1.2.6 with the frozen llama.cpp backend
- HTTP results: 39 responses with status 200
- Logical calls: 39 of 39
- Physical attempts: 39 of 42
- Prompt tokens: 24,081
- Completion tokens: 2,704
- Candidate calls: 36
- Parseable candidates: 34
- Governor admissions among parseable candidates: 0 of 34
- Malformed candidate replies: 2

The generated record contains 164 machine files: provider and protocol
receipts, two canonical occurrences, two mass-control records, the terminal
summary, the integrity report, and four retained artifacts for every call. The
[integrity report](integrity.json) recomputed all 39 request and response hashes;
every value matched. Logical indices are complete from 1 through 39. Every
candidate record retains its public condition, fork point, source receipt,
request-parent status, parse, canonical comparison value, and post-authorship
governor receipt.

Before the packet began, an attempted file-form Python launch failed while
importing the project package. It created no evidence directory, executed no
runner preflight, and sent no provider or participant request. The unchanged
runner was then launched as a package module, which began and completed the
single chartered contact recorded here.

## Interpretation boundary

This contact does not show that exact-draft challenge improves a candidate,
that Qwen cannot revise, or that a different responsibility would succeed. It
shows that this exact two-world, two-sample packet produced neither a stable
control-qualified revision nor a withdrawal.

The result narrows the authorship problem. In one world the challenged answer
varied between identical requests. In the other it copied the source exactly.
Across the packet, most parseable candidates copied opaque action names, and a
prompt-mass control could itself become the copied `change`. A later mechanism
therefore cannot treat changed text, challenge wording, or stable copying as
evidence that experience produced a reusable proposition.

The next work must first state this exposed problem without choosing a new
prompt, model, schema, source draft, or contact. A separate
[post-contact boundary](../../docs/POST_CHALLENGE_AUTHORSHIP_BOUNDARY.md) owns
that analysis.

The charter is consumed. This record licenses no rerun, prompt repair, model
search, successor contact, later-action packet, validation protocol, or
Formation claim.

## Interpretation review

Composer 2.5 and Grok 4.6 independently checked this account and the post-
contact problem definition against the charter, terminal summary, integrity
report, and retained logical records. Grok’s first pass rejected two causal
shortcuts: copying had been grouped with the formal label gates, and the
repeated-occurrence source match had been described as draft copying even
though that request contained no draft. The repaired account separates those
facts and leaves default authorship and visible-material copying open.

Both reviewers then returned `POST_CONTACT_ACCOUNT_SOUND` on the same repaired
text. Neither review contacted the participant model.
