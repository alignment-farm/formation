# Occurrence-accounting exploratory contact evidence

This directory is the complete record of the one contact licensed by the
[occurrence-accounting charter](../../docs/OCCURRENCE_ACCOUNTING_EXPLORATORY_CHARTER.md).
The run completed on 2026-08-18. It establishes no Formation or validation
verdict.

## Outcome

The contact completed all 37 logical calls in 37 physical attempts. There was
no retry, HTTP error, prompt repair, resampling, or conditional omission. Both
acquisition pairs and both model-authored accounts were observable.

Neither world earned `account-delivery-conditioned exact candidate difference`.
The delivered candidates varied between their two identical requests, at least
one same-response sample was malformed in each world, and the exact-byte-length
content controls differed from delivered accounts by 58 and 52 provider prompt
tokens. Both deltas exceeded the frozen 24-token ceiling. The required eight-
condition comparison was therefore unavailable in both worlds.

The terminal verdicts remain exactly:

```json
{"formation_verdict":null,"validation_verdict":null}
```

## What happened

The disposable interface returned `hold`. World E selected its two listed
controls in order; both actions increased position and the second reached the
target. World F also selected its controls in order; both actions decreased
position and the target was not reached. These are observed acquisition
choices, not competence scores.

Each account was a parseable, nonempty recount of its occurrence. Each copied
both acquisition control tokens. Because no semantic account scorer was
selected, both accounts remain `indeterminate`; the possibility that an
account already states a reusable relation remains live.

| Frozen observation | World E | World F |
| --- | --- | --- |
| Direct candidate | internally stable | internally stable |
| Withheld candidate | internally stable and exact direct match | internally stable and exact direct match |
| Delivered candidate | parseable twice, but unstable | parseable twice, but unstable |
| Same-response candidate | both samples malformed by truncation | one parseable, one malformed by truncation |
| Other unstable conditions | repeated occurrence, restatement, content control | restatement, content control |
| Delivered/content-control prompt-token delta | 58 in both rounds | 52 in both rounds |
| Frozen collapse label | none available | none available |
| Weak delivery-conditioned label | unavailable | unavailable |

Twenty-nine candidate outputs were parseable, and the frozen governor refused
all 29. Most copied an exact acquisition control token; many also left
`counterevidence` null. The governor did not score whether their prose was
correct. Three same-response outputs were malformed truncations and produced no
candidate for the governor to assess.

In both worlds, direct, withheld, and static-expanded requests produced the
same stable token-shaped candidate. Some delivered and restatement draws
contained longer relational prose, but neither condition was stable. World F's
repeated-occurrence condition was internally stable and differed from direct,
but delivered remained unstable. These are separate condition observations,
not a licensed delivery contrast. Restatement and ordinary prompt-content
explanations remain live; no exact collapse label was available.

Any relation visible in an account or candidate may already be present in the
request's occurrence or model-authored text. Nothing here shows that retention
or delivery created an abstraction.

The three malformed same-response samples exhausted their 256-token completion
while writing the account or change and ended before a complete JSON object.
They were retained without retry. The one parseable same-response sample was
also refused by the governor.

## Integrity and cost

- Model: `ai/qwen3:14B-Q6_K`
- Artifact digest:
  `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Provider: Docker Model Runner v1.2.6, running llama.cpp backend
- HTTP results: 37 responses with status 200
- Logical calls: 37 of 37
- Physical attempts: 37 of 40
- Prompt tokens: 24,412
- Completion tokens: 2,901
- Candidate calls: 32
- Parseable candidates: 29
- Governor admissions among parseable candidates: 0 of 29
- Malformed candidate outputs: 3

The directory contains 154 files: the provider and protocol receipts, two
canonical occurrences, the terminal summary, and request, response, metadata,
and logical records for every call, plus the post-contact integrity audit. The
[integrity audit](integrity-audit.json) recomputed all 37 request hashes and all
37 response hashes from retained bytes; every value matched its metadata.
Logical indices are complete from 1 through 37. Every candidate record retains
its public formation condition, fork point, and account-parent status.

## Interpretation boundary

This contact does not show that occurrence accounting works, that it cannot
work, or that persistence created an abstraction. It shows only that this exact
model, occurrence responsibility, candidate responsibility, and bounded
sampling packet did not produce a stable, control-qualified candidate
difference.

It exposes two separate next problems.

First, token-shaped authorship was already present before account delivery:
direct, withheld, and static-expanded requests returned the same stable token
object. The faithful accounts also repeated the episode's opaque action names,
while delivered and restatement candidates varied. This packet therefore
cannot attribute token attraction to occurrence accounting. The research
question remains whether a model-authored process can yield a stable, scope-
bearing, token-independent relation without the runtime writing that relation
for it. This contact does not select that process.

Second, byte-length parity did not create prompt-token parity, and the combined
same-response responsibility frequently exceeded the completion budget. These
are instrument failures or limitations, not evidence about formation. Any next
proposal must decide explicitly whether it studies token-independent
abstraction or repairs those instruments. It may not silently treat instrument
repair as developmental progress.

The charter is consumed. This record licenses no prompt change, rerun, model
search, successor contact, later-action packet, or validation protocol.

## Interpretation review

Composer 2.5 and Grok 4.6 independently reviewed this public account against
the charter, terminal summary, and raw logical records. The first pass rejected
language that grouped three malformed outputs with governor refusals and
implied a delivery contrast despite unstable delivered and restatement cells.
After the repair above, both returned `INTERPRETATION_SOUND`. Neither review
contacted the participant model.
