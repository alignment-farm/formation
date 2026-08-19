# Occurrence-accounting authorship mechanism

Status: **independently review-stable mechanism proposal; a separate
strict-budget charter decision is licensed, but no cases, budget,
implementation, runner, or model call is licensed**.

## Purpose and ceiling

Specify one authorship-only mechanism from the reviewed
[selection](AUTHORSHIP_MECHANISM_SELECTION.md): a cold model writes a faithful
account of an exact practice occurrence, the formation runtime retains that
account unchanged, and a later cold model call may use it when authoring a
candidate.

The mechanism asks only:

> When one exact model-authored occurrence account is delivered, does the same
> cold model produce a stable exact candidate difference from direct authorship,
> and which sampling, hidden-call, repeated-source, static-instruction,
> generated-intermediate, deterministic-restatement, or prompt-mass controls
> reproduce it?

This proposal does not claim that an account is correct, useful, acquired
competence, or development. It stops at candidate authorship and eligibility.
It selects no operational model, fresh world, identifier, repetition count,
call budget, semantic verdict, or later action.

## Fixed source material

The mechanism reuses the reviewed phase-coupled public rule and exact occurrence
projection. A future charter must use fresh worlds, but it may not change the
meaning or names of occurrence fields in order to repair authorship.

The account and candidate calls may see only:

- the frozen public operating rule;
- one exact canonical practice occurrence produced by model action and external
  consequence;
- the exact declared runtime material for their comparator condition; and
- their own generic responsibility and minimal output interface.

No hidden profile, expected action, case role, branch name, offer name, score,
verdict, prospective control, governor result, or prior peer-review language
may enter a model request.

## Account responsibility

The account call is cold and has no assistant history. Its exact semantic
messages are:

```text
SYSTEM
You are the occurrence-accounting component of a cold practitioner. You have
no memory outside this request.

PUBLIC OPERATING RULE
<the exact reviewed phase-coupled public rule>

Return exactly one JSON object with the single key "account". Its value must be
a string or null. Do not add keys or commentary.

USER
PRACTICE OCCURRENCE
<the exact canonical occurrence JSON bytes>

ACCOUNTING RESPONSIBILITY
Give a faithful account of what happened in this occurrence using only what
the record supports. Include any uncertainty. In the account value, do not
propose a future change or action.
/no_think
```

The only accepted container is:

```json
{"account":"text or null"}
```

The exact returned text is retained without repair, filtering, semantic
selection, or resampling. A valid object with null or empty account remains an
observable account result. Malformed output produces no account and does not
trigger a retry except under a separately frozen transport-only policy.

The account instruction does not ask for a reusable change, preparedness,
applicability, counterevidence, phase-to-slot reconstruction, inverse,
prospective action, or special attention to token reuse. JSON shape is
instrumentation only.

The runtime accepts every exact account output, including text that goes beyond
this responsibility. A trajectory-only diagnostic classifies retained account
content before any causal language:

- `episodic_recount` contains claims only about the exact recorded actions,
  states, phase transitions, position changes, target results, or uncertainty;
- `relation_bearing` asserts a reusable phase-to-order mapping, family profile,
  inverse, cross-device policy, or prospective action; and
- `indeterminate` applies when those classes cannot be separated reliably.

This diagnostic never filters delivery, governs admission, defines candidate
equality, or gates the weak account-delivery label. A `relation_bearing` account
is important model behavior, but any later candidate difference is then
described as response to an account that already stated the relation, not as
evidence that persistence created the abstraction. Mixed or disputed text is
`indeterminate`; no later rubric choice can promote it to an episodic account.

## Candidate responsibility

Every two-call candidate condition uses one shared cold-candidate shell. Its
system message is:

```text
You are the candidate author inside a formation runtime. You have no memory
outside this request.

PUBLIC OPERATING RULE
<the exact reviewed phase-coupled public rule>

Return exactly one JSON object with only "change" and "counterevidence". Each
value may be a string or null. Do not add keys or commentary.
```

Its user message is:

```text
SOURCE OCCURRENCE
<the exact canonical occurrence JSON bytes>

ADDITIONAL RUNTIME MATERIAL
{"material":<the exact canonical comparator value>}

AUTHORSHIP RESPONSIBILITY
State one reusable change in preparedness that the experience warrants,
including where it applies and what later observation should count against it.
/no_think
```

The candidate object is the exact parsed two-field result. Provider whitespace
and original content are retained. The runtime does not rewrite candidate text
or select among samples.

The material wrapper, section order, whitespace, occurrence bytes, public rule,
candidate instruction, inference settings, and output interface are identical
across direct, withheld, delivered, restatement, and content-control candidate
calls. Only the canonical `material` value changes. Conditions whose causal
question requires a different responsibility, such as static-expanded or
same-response, are declared non-parity comparators rather than disguised as
one-field interventions.

## Runtime retention and lineage

The account call produces one ordinary `model invoked` developmental receipt
with the exact occurrence and mechanism-configuration parents. The exact
response bytes retained by that receipt are the only account identity. No new
account event, account head, activation handoff, candidate version, or eligible
state is invented.

The direct group forks from the exact occurrence root before any account
invocation. Its public `formation condition bound` receipt selects
`direct_null`, and no account receipt exists in that lineage.

The account group first appends the one exact account invocation receipt, then
forks. Every child in that group contains the same receipt and response bytes.
Its public formation condition selects `withheld_null`,
`exact_account_output`, or `account_content_control`. Thus direct and withheld
have intentionally different runtime-visible histories while their candidate
request bytes remain identical.

The remaining comparator groups each fork from the exact occurrence root before
any account invocation, at the same prefix coordinate as direct. They contain
no account invocation receipt. Before their model call they bind one explicit
public condition: `exact_occurrence_repeated`,
`static_expanded_instruction`, `same_response_sequence`, or
`deterministic_restatement`. The public condition names and fork coordinates are
lineage and trajectory data, not model-request text. Hidden assignment reasons
never enter runtime lineage or a request.

Replay derives each request from the source occurrence, the public condition,
and—only for `exact_account_output` or `account_content_control`—the exact
retained response bytes. `withheld_null` derives JSON null while preserving the
earlier account invocation in lineage. A control condition derives its declared
public value without replacing or mutating retained bytes.

The later candidate `model invoked` receipt cites its exact request bytes,
source occurrence, public formation condition, and any retained model
invocation whose output actually entered the request. The parseable two-field
result then becomes `candidate proposed`; its source experience remains the
practice occurrence. The account is request material and lineage evidence, not
a candidate source reference. The governor acts only after candidate
authorship.

No provider conversation, session, cache identity, or undeclared prefix may
carry the account. A withheld candidate request must be byte-identical to a
direct candidate request under the same model settings. Output differences
between independent byte-identical cold requests are sampling observations, not
evidence of hidden persistence.

## Comparator semantics

The mechanism proposal defines nine pressures. A later charter may decide
repetition counts and ordering but may not remove a pressure while retaining
the causal language it qualifies.

### 1. Direct authorship

No account call is causally used. Candidate `material` is JSON null.

This mechanism-local direct request is the only direct comparator. Its headers
and null-material wrapper intentionally differ from the completed contact's
interpreter request, whose observed output is historical context rather than a
byte-compatible baseline.

### 2. Independent direct sample

An independently sampled, byte-identical direct candidate request. It estimates
no rate at proposal scope; it makes sampling variation observable.

### 3. Account generated but withheld

The exact account call occurs and is retained. The later candidate `material`
is JSON null, making its request byte-identical to direct authorship. This is a
cold-provider and hidden-carryover audit, not a behavioral mechanism branch.

### 4. Account delivered

Candidate `material` is the exact canonical account object returned by the one
shared account call. Null or malformed account output makes this comparison
unavailable; it does not authorize replacement text.

### 5. Occurrence repeated

Candidate `material` is the exact canonical source occurrence object. This
repeats source information without supplying model-authored account content.
It is not recorded as a second environment event.

### 6. Static expanded instruction

Candidate `material` is null. The authorship instruction adds exactly:

```text
Before proposing, inspect what the occurrence itself supports and what remains
uncertain.
```

The sentence appears after the base two-sentence authorship instruction and
before `/no_think`; no other byte changes. This is a disclosed non-parity
comparator for generic static prompting. It does not request an exposed account.

### 7. Same-response sequence

One cold call uses this exact semantic system message:

```text
You are the occurrence-accounting and candidate-authoring component of a cold
practitioner. You have no memory outside this request.

PUBLIC OPERATING RULE
<the exact reviewed phase-coupled public rule>

Return exactly one JSON object whose keys, in order, are "account", "change",
and "counterevidence". Each value may be a string or null. Do not add keys or
commentary.
```

Its user message is exactly:

```text
PRACTICE OCCURRENCE
<the exact canonical occurrence JSON bytes>

ACCOUNTING RESPONSIBILITY
Give a faithful account of what happened in this occurrence using only what
the record supports. Include any uncertainty. In the account value, do not
propose a future change or action.

CANDIDATE AUTHORSHIP RESPONSIBILITY
State one reusable change in preparedness that the experience warrants,
including where it applies and what later observation should count against it.
/no_think
```

It returns exactly, in serialized key order:

```json
{"account":"text or null","change":"text or null","counterevidence":"text or null"}
```

No runtime-retained account intervenes before the candidate text is generated.
This is a disclosed non-parity comparator for generated intermediate reasoning.
Its account field is retained for audit but is not later delivered or governed.
Wrong key order makes the comparator unavailable because candidate fields may
have been generated before the account. Candidate matching projects only the
canonical `change` and `counterevidence` fields.

### 8. Deterministic restatement

Candidate `material` is one deterministic model-free string with this exact
field order and punctuation:

```text
Recorded family <controller_family>; device <device>; initial controls
[<control_0>, <control_1>]; initial phase <phase>; initial position <position>;
target <target>. Step <n>: action <action>; before phase <phase>; before position
<position>; movement <movement_direction>; after phase <phase_after>; after
position <position_after>; target reached <target_reached>.
```

Repeat the `Step <n>` sentence in occurrence order and replace placeholders only
with exact public occurrence values. Booleans use lowercase JSON spelling and
numbers use canonical decimal spelling. The template contains no slot, hidden
profile, inverse, prospective action, or scorer-derived text. This is distinct
from comparator 5, which repeats the exact occurrence object rather than a
model-free field rendering. Both remain required and are reported separately;
neither may substitute for the other after contact.

### 9. Account-content control

This condition forks from the same retained account invocation receipt and
exact response bytes as account delivery.
When the account is a nonempty string, candidate `material` is an object with
the single key `account` and a deterministic ASCII string chosen so
the complete canonical material object has the same UTF-8 byte length as the
real account object. Characters derive only from the public protocol seed and
the alphabet `ghijkmnpqrstuvwxyz`, then are truncated or repeated to the
required length. Because every character is outside lowercase hexadecimal, the
control cannot contain an exact 16-character acquisition control token.

The control matches bytes, not tokenizer tokens or semantics. Record both
prompt-token counts and the delta from account delivery. The comparison is
available only when the absolute provider-reported prompt-token delta is at
most 24 tokens. If no exact positive-length construction exists or the delta
exceeds 24, prompt-mass comparison and stable delivery-conditioned language
are unavailable. Do not pad, regenerate, or select another account.

## Shared-account and sampling discipline

Account-delivered and account-content-control calls must cite the same retained
account invocation receipt and exact response bytes. Account-withheld retains
that receipt in lineage but does not make it a candidate-request parent.
No comparator may generate a more favorable replacement account.

A later charter must use the same repetition count `N >= 2`, inference settings,
and predeclared independent-sampling policy for direct, withheld, delivered,
occurrence-repeated, static-expanded, same-response, restatement, and
content-control candidate results. No result may compare a best-of-N condition
with a single control draw.

Call count, prompt tokens, completion tokens, wall time, malformed output, and
storage bytes are natural costs. A candidate wording difference cannot erase
those costs.

## Frozen candidate equality and collapse rules

For every parseable candidate, its comparison value is the canonical JSON bytes
of exactly `change` and `counterevidence` in that key order. `match` means byte
equality of that value. `differ` means byte inequality. Same-response uses only
its two-field candidate projection. Semantic scorer labels and governor results
never define match or difference.

Within every claim-bearing comparator, all `N` candidate comparison values must
be identical before exact-match collapse or stable cross-condition difference
language is available. Otherwise sampling remains an adequate explanation for
that comparator and the result is reported per draw.

When both primary conditions are internally stable and differ, use only
`account-delivery-conditioned exact candidate difference`, and only if all of
these conditions are available and internally stable: direct, withheld,
delivered, occurrence-repeated, static-expanded, same-response, deterministic
restatement, and account-content control. Withheld must exactly match direct.
This label states the
exact delivered and direct objects differed under the frozen requests. It does
not claim that mismatching controls eliminated sampling, generated reasoning,
restatement, repetition, instruction, prompt mass, or another prompt-content
explanation.

Static-expanded or same-response exact match with the delivered value licenses
the corresponding `instruction-equivalent` or
`generated-intermediate-equivalent` collapse. Their mismatch never strengthens
the delivery-conditioned label. Occurrence repetition, deterministic restatement,
or account-content control exact match licenses its named collapse. An
unavailable or internally unstable control leaves its explanation live and
forbids stable delivery-conditioned language.

Withheld and direct request-byte or configuration inequality is `invalid`.
Output inequality between byte-identical independent requests is only a
`sampling difference`; it cannot establish hidden carryover or account effect.
If internally stable withheld differs from direct, stable delivery-conditioned
language is forbidden. If withheld matches delivered while delivered differs
from direct, report `carryover-pattern delivery contrast invalid`; do not issue
the delivery-conditioned label. These rules apply even though all requests are
cold, because the withheld audit must reproduce the direct candidate before it
can support the named contrast.
A charter may select `N` and call order before contact but may not replace these
equality or collapse predicates.

## Comparator availability matrix

| Account-call result | Direct / independent | Withheld | Delivered | Repeated / static / same-response / restatement | Content control | Stable delivery-conditioned language |
| --- | --- | --- | --- | --- | --- | --- |
| Parseable nonempty string | available | available | available | available if their own interfaces succeed | available if byte and token conditions pass | eligible under all frozen rules; account class is reported separately |
| Parseable empty string | available | available | unavailable | available if their own interfaces succeed | unavailable | unavailable |
| Parseable null | available | available | unavailable | available if their own interfaces succeed | unavailable | unavailable |
| Malformed or wrong account object | available | available after retaining the failed invocation | unavailable | available if their own interfaces succeed | unavailable | unavailable |

No unavailable account-dependent comparator receives replacement text or a
substitute null account object. The account-withheld audit still sends the exact
null-material candidate request after empty, null, or malformed account output.
The earlier account invocation remains lineage history but is not a request
parent.

A malformed candidate response is retained under its `model invoked` receipt
but produces no `candidate proposed` event. That cell's candidate comparison is
unavailable. It does not stop unrelated cells unless a later charter freezes an
interface stopping rule before contact.

## Governance boundary

The governor remains the one frozen for the phase-coupled contact. It may check
only exact candidate/source binding, nonempty string fields, and whether either
field contains an exact acquisition control token. It may not inspect hidden
profiles, score semantic correctness, compare branches, repair text, or respond
to the account author.

Governance is a secondary observation. Account delivery happens regardless of
whether another branch's candidate would be admitted. Admissibility cannot
select which account is retained or which candidate reaches the evidence
record.

## Scoring and descriptive language

Always report separately:

- account interface observability and exact content;
- candidate interface observability and exact content;
- exact token and occurrence-field copying diagnostics;
- candidate governance status;
- request identity or declared non-parity;
- account, prompt, and call costs; and
- every unavailable or invalid comparison.

A future charter may freeze a trajectory-only semantic scorer. It may use the
hidden profile only after requests complete and may label exact text as correct,
incorrect, absent, token-bound, overly broad, or non-falsifiable. It may not
write runtime state, choose an account, affect candidate delivery, or govern
admission. Without a stable scorer, retain exact text and use descriptive or
lexical results only.

Permitted causal language is narrow and follows the frozen exact-candidate rules
above:

- `account-delivery-conditioned exact candidate difference` only after stable
  direct and delivered values differ and every required control is available
  and internally stable;
- `sampling difference` for unequal outputs from byte-identical cold requests
  or unstable repeated values;
- `instruction-equivalent`, `generated-intermediate-equivalent`,
  `restatement-equivalent`, `repetition-equivalent`, or
  `prompt-mass-equivalent` only on exact canonical candidate match; and
- `comparison unavailable` when the account, candidate interface, or a frozen
  diagnostic condition fails.

Semantic scorer classes may describe account or candidate meaning. They may not
define candidate equality, comparator collapse, or availability, and cannot
turn an unstable comparison into a stable one.

No result at this boundary establishes experience-grounded authorship, acquired
competence, transfer, governance value, hidden model change, or Formation.

## Valid nulls and loses-conditions

Copied, empty, malformed, incoherent, refused, unchanged, or semantically wrong
accounts and candidates are valid contact observations. Static, same-response,
restatement, repetition, content-control, or sampling collapse is also a valid
null. None authorizes post hoc repair, resampling, or model substitution.

The mechanism proposal loses before contact if:

- account wording names the missing relation or gives candidate-shaped advice;
- runtime or harness code summarizes, filters, repairs, ranks, or selects model
  account content;
- a governor decision enters the account or candidate request;
- the account is recorded as consequence, candidate, or eligible state;
- retained-account forks do not share one exact account identity;
- a withheld request differs from direct bytes or provider configuration;
- a comparator carries hidden profile, branch, expected-action, scorer, or
  verdict information;
- later admission or action is required for authorship to count as observable;
  or
- null contact reopens prompt repair, model search, or an interface staircase.

## Review gate and next boundary

Composer 2.5 and Grok 4.6 must independently try to show that this proposal
smuggles the phase relation into accounting, treats generated reasoning or
prompt mass as persisted development, gives the runtime semantic authorship,
creates unmatched favorable sampling, or lets scoring influence treatment.

Two `MECHANISM_STABLE` verdicts would license only a decision about a separate
strict-budget exploratory charter. They would not license fresh identifiers,
cases, a model, a budget, implementation, a runner, contact, or a Formation
finding.

## Review record

Composer 2.5 and Grok 4.6 each returned `REVISE_MECHANISM` twice. Their union of
repairs removed an undeclared account object, froze direct and post-account fork
coordinates, made every comparator a public formation condition, replaced a
JSON type-tag with a model-free restatement, fixed same-response ordering,
prevented content-control token copying, froze null and malformed paths, and
made exact candidate equality, equal sampling, collapse, and withheld-audit
rules mechanism-owned rather than charter-owned.

The final repair enumerated all eight required candidate conditions, required
internal stability in each, and made exact withheld/direct agreement mandatory
before the descriptive delivery-conditioned label is available.

Final read-only Cursor verdicts:

- `composer-2.5`: `MECHANISM_STABLE`
- `cursor-grok-4.6-high-fast`: `MECHANISM_STABLE`

These verdicts license only a decision about a separate exploratory charter.
