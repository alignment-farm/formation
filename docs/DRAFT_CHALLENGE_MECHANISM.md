# Exact-draft challenge and revision mechanism

Status: **independently review-stable mechanism; a separate strict-budget
charter decision is licensed, but no operational model, tokenizer, cases,
settings, identifiers, implementation, runner, participant-model call, or
Formation claim is licensed**.

## Purpose and ceiling

Specify the independently selected authorship-only route: a cold model authors
one first-draft candidate from an exact occurrence, the formation runtime
retains its complete output string, and later cold calls may replay or challenge
that exact string before governance.

The mechanism asks only:

> Conditional on one predeclared first draft, is there a stable exact candidate
> byte change under draft delivery plus a generic epistemic challenge that is
> not exactly reproduced by the frozen direct, hidden-call, replay, static,
> same-response, repeated-source, restatement, or prompt-mass conditions?

This is a request-conditioned authorship question. It does not ask whether a
revision is correct, non-copying, admissible, useful, acquired competence, or
Formation. A first draft or later output may be awkward, malformed, unchanged,
withdrawn, or worse.

## Fixed source and first-draft responsibility

Reuse the reviewed phase-coupled public operating rule and canonical occurrence
projection. A future charter must use fresh worlds. No hidden profile, expected
action, condition name, score, governor result, or peer-review language may
enter a model request.

The first-draft calls reuse the exact candidate system message from the
[occurrence-accounting mechanism](OCCURRENCE_ACCOUNTING_MECHANISM.md#candidate-responsibility):

```text
You are the candidate author inside a formation runtime. You have no memory
outside this request.

PUBLIC OPERATING RULE
<the exact reviewed phase-coupled public rule>

Return exactly one JSON object with only "change" and "counterevidence". Each
value may be a string or null. Do not add keys or commentary.
```

The exact user message is:

```text
SOURCE OCCURRENCE
<the exact canonical occurrence JSON bytes>

ADDITIONAL RUNTIME MATERIAL
{"material":null}

AUTHORSHIP RESPONSIBILITY
State one reusable change in preparedness that the experience warrants,
including where it applies and what later observation should count against it.
/no_think
```

The mechanism does not repair that responsibility after seeing the completed
contact. Its observed ambiguity remains part of the phenomenon.

## Predeclared source draft

A later charter selects one common sample count `N >= 2` and freezes an ordered
list of the `N` direct-candidate invocation identifiers before contact. The
source-draft identifier is the first entry in that direct-candidate list. It is
not a packet-global serial index, the first response to complete, or an actor,
interface, or acquisition call. All `N` direct invocations complete and their
raw responses are retained before any other claim-bearing invocation begins.
Completion order cannot select the source. The source identifier is never
replaced by a more parseable, interesting, admissible, or stable sample.

Every invocation records its predeclared index, actual send and completion
order, and any provider session, prefix-cache, or cache-use metadata the
provider exposes. Undeclared conversation or session reuse is an invalid cold-
call packet. Direct stability and the later byte-identical withheld audit are
the observable checks on order or provider carryover; passing them does not
prove that every unexposed provider effect was absent.

The complete `choices[0].message.content` value from direct invocation index 1
is the draft content:

- every UTF-8-encodable Unicode-scalar string, including empty or malformed
  candidate JSON, is retained exactly and is eligible for raw draft replay and
  challenge;
- an unencodable string is retained in the provider receipt but makes draft-
  dependent request construction unavailable;
- a non-string or absent content value is retained as an interface result but
  makes draft-dependent conditions unavailable; and
- parsing a string as a candidate is a separate observation. Parse failure does
  not alter the retained string.

The retained draft identity is the exact decoded content string bound to the
source invocation and raw provider-response receipt. Provider reasoning or
thinking fields are audit evidence only and can never replace content. Missing
`choices[0]`, missing `message`, missing content, or non-string content follows
the unavailable-content rule even if another provider field contains text.

This mechanism uses the repository byte function `canonical_json_bytes` for
every material envelope and candidate comparison:

```python
json.dumps(
    value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
).encode("utf-8")
```

A content string is draft-eligible only if every decoded code point is a
Unicode scalar value and the encoder succeeds on
`{"material":{"draft_content":source_string}}`. Scalar legality is tested on
the decoded provider string before envelope construction. JSON `\uD800`-style
escaping does not make a non-scalar eligible. A failing string remains in the
raw provider receipt but makes draft-dependent conditions unavailable. It is
not replaced, escaped under another rule, or read from a different provider
field. Candidate parsing separately excludes non-finite values, so every value
passed to the comparison encoder is in the encoder's declared JSON domain.

When an encodable string is delivered, the exact material-envelope bytes are
`canonical_json_bytes({"material":{"draft_content":source_string}})`, which
has the compact shape:

```json
{"material":{"draft_content":"<exact string value>"}}
```

JSON quoting and escaping under this one shared encoder are representation, not
repair. The model receives prompt text containing that JSON representation; no
model-side decoding event is assumed. Replay, exact challenge, and prompt-mass
control use the same envelope function. The raw response, decoded content
string, canonical material bytes, byte length, tokenizer length, and hashes are
all retained separately.

A named candidate-revision comparison requires all `N` direct results to be
parseable candidates with identical canonical candidate bytes. This makes the
predeclared source candidate a member of the stable direct set. If the source
string is malformed, empty, unencodable, non-string, or differs canonically
from another direct sample, raw challenge remains observable when constructible
but stable revision language is unavailable.

## Challenge responsibility

Every two-call challenge condition uses the same candidate system message. Its
user message is:

```text
SOURCE OCCURRENCE
<the exact canonical occurrence JSON bytes>

ADDITIONAL RUNTIME MATERIAL
{"material":{"draft_content":"<exact first-draft string>"}}

CHALLENGE RESPONSIBILITY
Review the exact prior model output supplied as `draft_content` using only the
public rule and source occurrence. Return the candidate you can support now.
Keep only claims supported by those sources, state where they apply, and state
what later observation would count against them. Use null for both fields if
you withdraw the prior attempt or cannot support a candidate.
/no_think
```

The output interface remains exactly `change` and `counterevidence`. Exact
retention of the first candidate, exact revision, null withdrawal, partial null,
malformed output, and non-string content are all observable. The runtime does
not complete, summarize, or explain the first draft.

The challenge wording does not mention action-token reuse, episode identifiers,
ordered slots, increasing or decreasing roles, inverse profiles, the realized
family relation, eligibility, or the governor. It supplies an epistemic
responsibility, not a phase-coupled answer.

## Runtime lineage

All `N` direct samples fork from the exact occurrence root under public
condition `direct_candidate`. Direct invocation index 1 produces the retained
source-draft receipt. Its model invocation cites the exact occurrence and
mechanism configuration. A parseable result may also produce candidate version
1, but the exact model-output string exists whether parsing succeeds or not.

After all direct invocations complete, one draft group forks with the exact
source invocation receipt and response bytes in lineage. Its children bind
public conditions:

- `draft_withheld`;
- `exact_draft_replay`;
- `static_challenge_withheld_draft`;
- `exact_draft_challenge`; and
- `draft_prompt_mass_control`.

Only replay and exact challenge cite the source draft receipt as a request
parent: in those branches, the retained content actually contributes bytes to
the request. Prompt-mass control shares the retained head for schedule parity
but does not cite draft content as a request parent. Withheld and static
challenge preserve the earlier invocation in lineage while deriving null
material.

Same-response, occurrence-repeated, and deterministic-restatement groups fork
from the occurrence root before the source draft receipt. They contain no
retained draft. Condition names and fork coordinates are public lineage data,
never request text.

A later parseable challenge result becomes candidate version 2 with the source
occurrence, exact challenge request, public condition, and any delivered draft
receipt as parents. Version 1 is not overwritten. An absent, non-string, or
malformed result is retained without inventing a candidate version. Governance
follows authorship and cannot become a challenge parent.

A parseable double-null object is candidate version 2 and a withdrawal
observation. Missing-path, JSON-null, or non-string content is an interface
result without a candidate version.

No provider conversation, session, cache identity, or undeclared prefix may
connect calls. Every call is cold.

## Comparator semantics

The nine conditions below are mandatory before a later mechanism-specific
revision label can issue. A charter may select `N`, the remaining condition
order, and budget while preserving the source-first lifecycle above, but may
not remove a condition while retaining the language it qualifies.

### 1. Direct sampling and source draft

Run the exact first-draft request `N` times. Invocation index 1 is the
predeclared source draft. The condition estimates exact output stability
without challenge.

### 2. Draft generated but withheld

The exact source-draft invocation exists in lineage. Send the byte-identical
direct candidate request with null material and the base authorship
responsibility `N` times. The request bytes and model settings must exactly
match direct. This is a hidden-call carryover and sampling audit.

### 3. Exact draft replay

Deliver the canonical exact-draft object under `ADDITIONAL RUNTIME MATERIAL`,
but retain the unchanged base authorship responsibility. This isolates visible
draft presence and extra draft content without challenge language.

### 4. Static challenge

The source-draft invocation exists in lineage but no draft content enters the
request. Material is null. Replace the base responsibility with this exact
non-indexical, non-parity near-clone of the challenge responsibility:

```text
STATIC REVIEW RESPONSIBILITY
Review using only the public rule and source occurrence. Return the candidate
you can support now. Keep only claims supported by those sources, state where
they apply, and state what later observation would count against them. Use null
for both fields if you cannot support a candidate.
/no_think
```

It never says that a prior draft exists. This condition isolates generic static
review guidance under matched hidden-call history.

### 5. Exact draft plus challenge

Deliver the one exact draft object and use the frozen challenge responsibility.
This is the selected interaction.

### 6. Same-response draft and challenge

One cold call authors a draft and then reviews it without runtime retention. Its
system message is:

```text
You are the candidate drafting and review component of a cold practitioner. You
have no memory outside this request.

PUBLIC OPERATING RULE
<the exact reviewed phase-coupled public rule>

Return exactly one JSON object whose keys, in order, are "draft" and "final".
Each value must be an object with only "change" and "counterevidence". Each
field value may be a string or null. Do not add keys or commentary.
```

Its user message is:

```text
SOURCE OCCURRENCE
<the exact canonical occurrence JSON bytes>

FIRST DRAFT RESPONSIBILITY
State one reusable change in preparedness that the experience warrants,
including where it applies and what later observation should count against it.

REVIEW RESPONSIBILITY
Review the draft you just wrote using only the public rule and source
occurrence. Return the candidate you can support now. Keep only claims supported
by those sources, state where they apply, and state what later observation would
count against them. Use null for both fields if you withdraw the draft or cannot
support a candidate.
/no_think
```

Key order is part of the observable output interface, but it does not prove the
model's internal planning order. Wrong order, malformed nested objects,
truncation, or extra keys makes the comparator unavailable. Exact draft and
final objects are retained. Only canonical `final` candidate bytes enter cross-
condition equality; the nested draft is audit material and never substitutes
for the predeclared source string.

This is a disclosed non-parity comparator for whether the same final candidate
can appear when an intermediate is generated in one response. It does not
reproduce runtime retention, the exact source draft, or raw malformed-draft
handling. A match is a conservative collapse. A mismatch never establishes
that separate runtime retention mattered.

### 7. Occurrence repeated

Use the base candidate responsibility and deliver the exact canonical source
occurrence as material. This repeats source bytes without creating another
environment event, draft, or challenge.

### 8. Deterministic restatement

Use the base candidate responsibility and the exact public-field restatement
owned by the occurrence-accounting mechanism. It performs no semantic
translation and contains no hidden slot, expected relation, scorer result, or
model-authored draft.

### 9. Draft prompt-mass control

Use the exact challenge responsibility and the same material shape as draft
delivery, but substitute a deterministic non-draft string:

```json
{"draft_content":"<public-seed control string>"}
```

The source draft determines only one integer: the target tokenizer length of
the complete exact-challenge request. A future charter must name the exact
tokenizer artifact, public seed, alphabet, deterministic prefix-search
algorithm, exact public request template, and maximum search bound before
contact. The constructor receives only that integer and those frozen public
inputs. It may not receive or inspect draft bytes, the draft-shaped request,
hashes, semantics, candidate parsing, governor results, hidden truth, or
favorable outputs. Its alphabet must exclude lowercase hexadecimal so it
cannot contain an acquisition control token.

The public request template may contain a hole for the `draft_content` string
but must not contain the live source string or any other draft-derived bytes.

The comparison is available only if the preflight tokenizer and provider both
report exact prompt-token equality between draft challenge and mass control in
every paired sample. Failure to construct within the frozen bound, or later
failure to verify equality, leaves prompt mass live and forbids the mechanism-
specific label. There is no second seed, widened alphabet, enlarged bound, or
post-contact constructor repair in the packet. This cell matches both prompt
tokens and the draft-shaped field and responsibility; it is not a pure token-
count intervention. Token-aware parity is instrument repair, not research
progress.

## Shared-draft and sampling discipline

Replay, exact challenge, and prompt-mass conditions share the one predeclared
source invocation and exact response bytes. No condition may request or select
a replacement draft. Withheld and static conditions preserve that same receipt
without placing its output in the request.

Every candidate condition uses the same `N >= 2`, stochastic inference
settings, cold-call policy, and predeclared independent-sampling rule. A later
charter freezes one single-call completion allowance `B` before contact. Every
ordinary invocation receives `B`; the same-response invocation receives
exactly `2B`, equal to the two visible model-call allowances on the selected
draft-then-challenge path. No observed response length may determine `B`.
Wrong-order, truncated, or malformed same-response output remains unavailable;
there is no budget retry. The disclosed two-call allowance is instrumentation
and establishes no authorship result.

Call count, prompt tokens, completion tokens, latency, malformed output, and
storage bytes are costs. No textual improvement can erase them.

## Candidate parsing, equality, and stability

Parse candidate JSON with a duplicate-key-refusing object decoder and reject
`NaN`, positive or negative `Infinity`, and any other non-finite constant.
Last-wins `json.loads` is not a successful parse. The base and challenge
interfaces accept exactly one object with only `change` and `counterevidence`,
each string or null. Duplicate keys, extra keys, wrong types, non-finite JSON
values, or malformed JSON are retained and unavailable for candidate equality.
Same-response additionally enforces its outer key order and two exact nested
objects using the same decoder.

The comparison value is `canonical_json_bytes` of the two-field candidate
object. Because that encoder sorts keys, its compact shape is exactly:

```json
{"change":<exact value>,"counterevidence":<exact value>}
```

Provider whitespace and raw content remain evidence but do not define equality.
`match` means exact byte equality. No semantic rescue or normalization enters
candidate equality.

Delivery identity and equality identity remain distinct. The delivered value is
the raw decoded content string from source invocation index 1. If it parses,
its equality value is the canonical candidate bytes above. Other direct raw
strings may differ in whitespace while parsing to the same equality value;
that does not rewrite the source string that later requests receive.

All `N` values in every claim-bearing condition must be available and identical
before stable match, collapse, or revision language is permitted. Otherwise
report each draw and keep sampling live. Direct stability includes the
predeclared source candidate. Raw equality between the later provider content
string and the source string is retained only as `exact challenge-source raw-
output match`; it is not evidence that runtime retention caused the match.

## Collapse and invalidation rules

First compare direct and withheld request bytes and settings. Any mismatch is
`withheld-audit invalid`; do not treat those outputs as a withheld audit. That
terminal result forbids every mechanism-specific label, named equivalence
collapse, and challenge-associated retention, revision, or withdrawal phrase.

If request bytes and settings match, compare the `N` outputs. If either
condition is internally unstable, report direct or withheld instability, keep
sampling live, and apply the same forbid. If both are internally stable and the
outputs differ, report `withheld-audit failed` and apply the same forbid. If
stable withheld matches exact challenge while exact challenge differs from
direct, report `carryover-pattern challenge contrast invalid` and stop
mechanism-specific interpretation.

If the selected exact-challenge condition is unavailable or unstable, no
challenge-anchored equivalence, retention, revision, or withdrawal label can
issue. Report only per-draw and per-cell instrumentation.

When stable exact challenge equals the source candidate, report `exact
challenge-source candidate match`, not retention or revision. When it differs,
the mechanism-specific label remains unavailable unless all nine conditions
are available, internally stable, the source candidate belongs to the stable
direct set, direct matches withheld, prompt-token parity is exact, and none of
these exact collapses applies:

- exact replay matches challenge: `draft-priming-equivalent`;
- static challenge matches challenge: `static-review-equivalent`;
- same-response final matches challenge: `generated-intermediate-equivalent`;
- occurrence repeated matches challenge: `repetition-equivalent`;
- deterministic restatement matches challenge: `restatement-equivalent`; or
- prompt-mass control matches challenge: `prompt-mass-equivalent`.

Report every equivalence label whose exact match applies, and only when
withheld request bytes and settings match direct and both conditions are
internally stable. Any one match forbids the complete label. Independent
sampling remains mandatory through direct stability and the withheld audit;
after a challenge-source difference it cannot also provide a distinct stable-
direct match. Per-draw instrumentation may still be reported without named
equivalence or revision language. Mismatches never eliminate the corresponding
prompt-content explanation. An unavailable or unstable condition forbids the
complete label and leaves its explanation live.

Only when every rule above holds and the stable exact-challenge candidate is not
double-null may a record use:

```text
draft-challenge-associated exact candidate revision
```

If every rule holds but the stable exact-challenge candidate is exactly
`{"change":null,"counterevidence":null}` and differs from the source, the only
parallel label is:

```text
draft-challenge-associated exact candidate withdrawal
```

Both labels state only that stable exact candidate bytes under the selected
request differed from the stable source candidate and were not exactly
reproduced by the frozen controls. `Associated` names a frozen request
condition, not a causal effect. Neither label claims improvement, semantic
correctness, experience grounding, separate-runtime necessity, development, or
Formation.

## Governance and semantic scoring

No governor runs until every predeclared model invocation in the authorship
packet has completed or hit a frozen infrastructure stop and every raw response
has been retained. The frozen phase-coupled governor then observes each
parseable candidate that enters cross-condition equality. It checks exact
source binding, nonempty fields, and acquisition-control-token copying. The
same-response inner draft is audit-only and is not substituted as a governed
source candidate.

No governor result may exist in request lineage before the exact-challenge
receipt. Governance cannot decide whether challenge runs, alter a request,
select a draft, define equality, or become a request parent. A policy refusal
is not environment counterevidence.

A future charter may freeze a post-contact semantic scorer that classifies
exact candidates as correct, wrong, token-bound, overbroad, non-falsifiable, or
indeterminate. The scorer may use hidden truth only after requests complete. It
cannot enter runtime lineage, select a sample, govern admission, or feed back a
result. Without stable semantic review, exact text and descriptive diagnostics
remain the evidence.

## Availability matrix

| Source draft result | Direct / withheld / static / repeated / restatement / same-response | Replay / exact challenge / mass control | Complete revision label |
| --- | --- | --- | --- |
| Parseable stable candidate string | available if own interfaces succeed | available from exact encodable string; mass also requires token parity | eligible under every rule |
| Parseable but direct-unstable candidate string | available per draw | raw draft conditions available | unavailable |
| Malformed or empty string | available per interface | raw string replay and challenge available without repair | unavailable because source candidate equality is absent |
| Unencodable string | unaffected conditions still run; raw receipt retained | unavailable | unavailable |
| Missing path, null, or non-string content | unaffected conditions still run; reasoning/thinking fields remain audit-only | unavailable | unavailable |

No unavailable condition receives replacement text, another draft, or repaired
JSON. Truncated JSON is never completed. A parseable double-null object is a
candidate withdrawal, not malformed. A nested same-response draft never
substitutes for unavailable source content. If the source candidate is
unavailable, no revision or challenge-anchored collapse label issues even when
other cells happen to match. Malformed downstream outputs make only their cells
unavailable. A charter may freeze infrastructure stops but may not convert
awkward model behavior into an admission stop.

## Claim and stopping boundary

Unchanged, copied, wrong, withdrawn, null, malformed, unstable,
draft-priming-equivalent, static-review-equivalent,
generated-intermediate-equivalent, repetition-equivalent,
restatement-equivalent, prompt-mass-equivalent, withheld-audit failure, or
comparison-unavailable results all complete a bounded exploration.

No result licenses prompt repair, another challenge wording, a replacement
draft, more experience, model substitution, later-action cases, validation, or
another contact. Instrument repair may be necessary to make a later charter
well-formed, but completing that repair does not count as mechanism success or
lifecycle progress.

## Review gate

Independent reviewers must try to show that raw malformed-draft delivery is a
repair, source-draft designation selects convenience, lineage hides a first-call
effect, static review is not a fair ceiling, same-response order supplies a
different task, token-aware mass construction leaks draft content, or the
collapse rules can manufacture revision or hide a null.

Two `MECHANISM_STABLE` verdicts would license only a separate strict-budget
charter decision. They would not license an operational model, tokenizer,
instrument implementation, fresh worlds, cases, settings, budget, runner,
participant-model request, or Formation claim.

## Review record

Composer 2.5 and Grok 4.6 first returned `REVISE_MECHANISM`. Their shared
objections froze the direct-candidate source identifier, exact Unicode and JSON
byte contract, near-clone static review, disclosed same-response non-parity,
token-mass constructor information flow, raw-versus-canonical identities,
terminal audit rules, withdrawal language, and post-packet governor timing.

The confirmation pass exposed three further implementation traps: an invalid
withheld request did not yet block every label, ordinary JSON parsing could
silently accept duplicate keys, and a mistaken illustrated key order could
classify double-null withdrawal as revision. Those defects were repaired in the
mechanism rather than deferred to a runner.

Final read-only Cursor verdicts on the exact current byte predicates and claim
rules:

- `composer-2.5`: `MECHANISM_STABLE`
- `cursor-grok-4.6-high-fast`: `MECHANISM_STABLE`

The reviews license only a separate strict-budget charter decision. No
participant-model call occurred during mechanism review.
