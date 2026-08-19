# Occurrence-accounting exploratory contact charter

Status: **completed and consumed strict-budget authorship-only charter; no
repair, replication, successor contact, later-action packet, or validation is
licensed**.

## Question and ceiling

Run one bounded contact under the reviewed
[occurrence-accounting mechanism](OCCURRENCE_ACCOUNTING_MECHANISM.md).

Ask only:

> When one exact model-authored account of a phase-coupled occurrence is
> retained and delivered, does the same cold model produce a stable exact
> candidate difference from mechanism-local direct authorship, and which frozen
> authorship controls reproduce it?

The contact ends at candidate authorship and lexical eligibility. It has no
later-action, transfer, non-transfer, revision, or validation cases. Exact text
differences are request-conditioned observations. The contact cannot establish
experience-grounded authorship, acquired competence, governance value, hidden
model change, or Formation.

## Operational model and provider

Use the already participating artifact rather than opening model selection:

```text
model request identifier: ai/qwen3:14B-Q6_K
Docker inspect tag: docker.io/ai/qwen3:14B-Q6_K
artifact digest: sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219
endpoint: http://localhost:12434/engines/llama.cpp/v1/chat/completions
```

Retain fresh `docker model list`, `inspect`, `status`, and `version` receipts
before contact. Stop before the first request if the digest, endpoint, runner
status, or version receipt is unavailable. Do not use `gpt-oss:20B`, download a
successor, compare models, or reopen admission.

Every call is cold: one system/user pair, no assistant history, no provider
session, and no undeclared prefix. All authoring requests use:

```json
{
  "max_tokens": 256,
  "temperature": 0.6,
  "top_p": 0.95,
  "stream": false,
  "response_format": {"type": "json_object"}
}
```

Actor calls change only `max_tokens` to `128`. Every user instruction ends in
`/no_think`. Only `choices[0].message.content` supplies actions, accounts, or
candidates. Provider reasoning fields are retained but never scored.

## Public rule and action interface

Use the exact public rule frozen in
[the prior charter](PHASE_COUPLED_EXPLORATORY_CHARTER.md#frozen-public-rule).
Use its exact actor system/user templates with `material` JSON null for the
disposable interface call and both acquisitions. Their material section is
byte-identical to `offer_envelope(None)`.

The interface call requests one action from the two listed controls and `hold`.
Each acquisition requests exactly two actions, each one of the current controls;
repetition is valid. No action is repaired, replaced, or semantically scored.
Any valid pair is applied without intermediate model feedback and produces the
exact canonical occurrence owned by `phase_coupled_specimen.py`.

Any valid listed one-action object passes the disposable interface check.
Choosing `hold` is not required, action correctness is not scored, and this
call is not a competence or admission test.

The interface call must be observable before contact continues. An invalid or
unobservable acquisition pair makes that world unavailable but does not screen
the model or cancel the other world. Retain it and skip only calls that require
its missing occurrence.

## Account and candidate interfaces

Use the exact account, shared candidate, static-expanded, and same-response
messages frozen in the mechanism proposal. The runner may substitute only the
exact public rule, canonical occurrence bytes, and canonical comparator
material at their declared placeholders.

The account object must have exactly one key, `account`, whose value is a string
or null. Empty and null are observable but make delivered and content-control
comparisons unavailable. Malformed account output is retained, never repaired,
and also makes those comparisons unavailable.

The shared candidate object must have exactly `change` and `counterevidence`,
each string or null. Same-response must serialize `account`, `change`, and
`counterevidence` in that order. Malformed candidate output is retained and
makes only its cell unavailable.

No semantic account scorer is selected. A lexical rule cannot establish that
an account claims only about one episode or that it asserts a reusable
relation. Therefore every parseable nonempty account receives the conservative
trajectory class `indeterminate`. Null, empty, or malformed account output
receives `not_classified` with its exact interface reason. This is frozen before
contact; neither exact words nor later candidates may promote an account to
`episodic_recount` or `relation_bearing`.

For descriptive audit only, normalize account text with Unicode NFKC and case
folding, then report exact acquisition-control-token and occurrence-field-name
matches. These observations are not semantic classes. The diagnostic uses no
hidden slot or expected relation, never filters delivery, and never changes
exact candidate equality or availability.

The governor applies only the mechanism's frozen source binding, nonempty-field,
and exact acquisition-control-token checks after each parseable candidate. Its
receipt is descriptive eligibility evidence and never enters another request.

## Fresh deterministic worlds

All identifiers use the reviewed specimen seed
`formation.phase-coupled-control.specimen.v1`. Profile slots below are
harness-only.

### Disposable interface

```text
family counter: 7
controller family: c5feb6f0d132c08e
phases: [50679bf78e69e0d6, 2627e75d1beda451]
hidden phase-zero increasing slot: 0
device counter: 22
device: 0ac23ba43c882959
start phase: 50679bf78e69e0d6
position: 3
target: 3
controls: [3185f44dddd55df2, 9f66ade0f8ea381a]
```

### World E

```text
family counter: 5
controller family: c378816a8c4ed06f
phases: [72b4369223095ae5, 96e6b778c4c3439e]
hidden phase-zero increasing slot: 0
device counter: 20
device: adfc8f4a1b01d510
start phase: 72b4369223095ae5
position: 0
target: 2
controls: [91dd8389d9c3730a, c07e743cb43592c8]
```

### World F

```text
family counter: 6
controller family: 95d703a257e5a8fb
phases: [41dd49a87033606b, 9782ecf0f92e8157]
hidden phase-zero increasing slot: 1
device counter: 21
device: a4c67fdac36e0ef5
start phase: 41dd49a87033606b
position: 0
target: 2
controls: [20de6d24dbe28705, 9c3e211ff8cc41c2]
```

World E and F material never crosses. World names, counters, hidden slots, and
expected profiles never enter a model request.

## Comparator values

For each observable world occurrence, build the eight required candidate
conditions exactly as the mechanism defines:

| Condition | Fork point | Candidate material or responsibility |
| --- | --- | --- |
| `direct` | occurrence root | shared candidate shell, material null |
| `withheld` | post-account invocation | byte-identical direct request, material null |
| `delivered` | post-account invocation | exact nonempty account object |
| `occurrence_repeated` | occurrence root | exact occurrence object as material |
| `static_expanded` | occurrence root | material null plus exact frozen static sentence |
| `same_response` | occurrence root | exact frozen combined responsibility and three-field output |
| `restatement` | occurrence root | exact mechanism-owned deterministic field rendering |
| `content_control` | post-account invocation | exact-byte-length non-hex account object |

Direct, withheld, repeated, static, same-response, and restatement always run
after an observable occurrence. Delivered and content control run only after a
parseable nonempty account. Content-control characters derive only from public
seed `formation.occurrence-accounting.content-control.v1` and alphabet
`ghijkmnpqrstuvwxyz`; account bytes determine only the target UTF-8 length of
the canonical `{"account":...}` object. Truncate or repeat the seeded stream
once to that length, then freeze the object. Do not hash account content into
the stream, pad, regenerate, or choose another account. If no exact positive-
length construction exists, content control and stable delivery-conditioned
language are unavailable.

Use `N = 2` independent candidate samples for every condition that runs. Do not
resample an unstable condition. The provider-reported prompt-token delta between
delivered and content control must be at most 24 or the prompt-mass comparison
and stable delivery-conditioned language are unavailable.

The two `direct` rounds are mechanism comparators 1 and 2: direct authorship and
its independent direct sample. Both use the same `direct_null` fork semantics.

## Exact schedule and budget

The maximum logical schedule is 37 calls:

1. disposable actor interface;
2. World E acquisition;
3. World F acquisition;
4. World E account, if its occurrence exists;
5. World F account, if its occurrence exists; and
6. up to 32 candidate calls: eight conditions times two samples in each
   observable world.

Candidate calls use two rounds. Within each listed world/round, omit only
account-dependent conditions made unavailable before scheduling.

| Round | World | Frozen condition order |
| --- | --- | --- |
| 1 | E | direct, withheld, delivered, occurrence repeated, static expanded, same response, restatement, content control |
| 1 | F | static expanded, same response, restatement, content control, direct, withheld, delivered, occurrence repeated |
| 2 | E | delivered, occurrence repeated, static expanded, same response, restatement, content control, direct, withheld |
| 2 | F | restatement, content control, direct, withheld, delivered, occurrence repeated, static expanded, same response |

Finish all scheduled round-1 calls before round 2. There is no resume or
conversation reuse.

The hard physical-attempt ceiling is 40. Retry once only after a local transport
failure with no HTTP response, and never beyond the ceiling. Every attempt
spends the ceiling. Do not retry HTTP errors, malformed or empty model content,
invalid actions, null accounts, unstable candidates, governor refusal, token
disparity, or awkward behavior.

Stop the full contact on provider/digest drift, exhausted physical ceiling, an
unobservable disposable interface, an HTTP error, or evidence-write failure.
Do not change prompts, identifiers, worlds, condition order, settings, parser,
device control tokens, content-control construction rule, threshold, `N`, or
budget after contact begins. The content-control object is necessarily
materialized once after the live account determines only its target length.

## Frozen comparisons and reporting

Use the mechanism-owned canonical two-field candidate bytes, internal stability,
exact match, collapse, availability, and withheld-audit rules without change.
All eight conditions must be available and internally stable, and withheld must
exactly match direct, before reporting
`account-delivery-conditioned exact candidate difference` for a world.

If stable withheld differs from direct, stable delivery-conditioned language is
forbidden. If withheld matches delivered while delivered differs from direct,
report `carryover-pattern delivery contrast invalid`. Matches by other controls
receive only their frozen equivalence labels. Mismatches do not eliminate the
corresponding prompt-content explanation.

For every account result, state explicitly that the unscored account may
already state the relevant relation and that relation-already-present remains a
live explanation. The conservative diagnostic never licenses stronger causal
language or evidence that persistence created an abstraction.

Report each world separately and do not pool text equality across worlds. No
best-of, majority, semantic rescue, or cross-world favorable selection is
permitted.

The terminal summary must contain:

```json
{"formation_verdict":null,"validation_verdict":null}
```

Retain exact provider receipts, requests, responses, usage, attempt order,
occurrences, account invocation receipts, public formation conditions,
candidate objects, malformed content, governor receipts, canonical comparison
bytes, availability decisions, token diagnostics, costs, and all nulls.

## Claim and stopping boundary

Copied, empty, malformed, incoherent, refused, unstable, instruction-equivalent,
generated-intermediate-equivalent, repetition-equivalent,
restatement-equivalent, prompt-mass-equivalent, or unchanged results are valid
contact outcomes. Partial completion after a frozen stop is infrastructure or
interface evidence only.

No outcome licenses prompt repair, model search, another account schema, a
second contact, later-action cases, or validation. The charter is consumed by
one live start even if conditional paths are unavailable.

## Observed result

The contact completed on 2026-08-18 in 37 logical calls and 37 physical
attempts. Both acquisition occurrences and both accounts were observable. The
direct and withheld candidates were internally stable and exactly matched in
both worlds. Delivered candidates were unstable, at least one same-response
sample was malformed in each world, and delivered/content-control prompt-token
deltas were 58 and 52, above the frozen 24-token ceiling. Neither world had an
available eight-condition comparison or weak delivery-conditioned label.

Twenty-nine candidates were parseable and all were refused by the frozen
eligibility checks; three same-response outputs were truncated before valid
JSON. This is not a competence verdict. The
[evidence record](../evidence/occurrence-accounting-exploratory-contact-20260818/README.md)
retains exact requests, responses, accounts, comparisons, integrity audit, and
null Formation and validation verdicts. Composer 2.5 and Grok 4.6 both returned
`INTERPRETATION_SOUND`. The charter licenses no repair or successor.

## Review gate

Before implementation, Composer 2.5 and Grok 4.6 must independently try to show
that the schedule, conditional omissions, fresh worlds, account content, static
or same-response prompts, content-control construction, exact equality rule,
withheld audit, stopping policy, or 40-attempt ceiling can manufacture a
delivery-conditioned result or hide a null.

Only two `CHARTER_STABLE` verdicts license a fake-tested runner. Runner
conformance review is still required before the first participant-model request.
No peer-review call may contact the participant model.

## Review record

Composer 2.5 and Grok 4.6 reviewed successive drafts through Cursor `agent` in
read-only `ask` mode. The first round rejected an interface rule that treated
one particular valid action as required, an unfrozen actor material value, a
blanket-indeterminate account diagnostic, and a content control whose bytes
could depend on account content rather than only its length. Those surfaces
were frozen and repaired.

A second round found that the proposed lexical classifier could label text
`episodic_recount` even when it expressed the reusable relation without one of
the listed marker words. Adding a reporting caveat did not repair the stored
semantic claim. The final charter therefore makes no lexical semantic
classification: every parseable nonempty account is conservatively
`indeterminate`, exact copying diagnostics remain descriptive, and
relation-already-present stays live for every result.

The final identical review prompt asked both required reviewers whether that
repair obeyed the mechanism and whether any schedule, omission, world,
content-control, exact-comparison, withheld, stopping, or budget rule could
manufacture a delivery-conditioned result or hide a null. Terminal results:

- `composer-2.5`: `CHARTER_STABLE`
- `cursor-grok-4.6-high-fast`: `CHARTER_STABLE`

Kimi K3 (`kimi-k3-max`) supplied one additional independent read of the prior
repaired draft and returned `CHARTER_STABLE`. Its residual caution remains in
force: exact prose collapse matches may be rare, so an unmatched exact
difference remains a weak request-conditioned observation with prompt-content
explanations live. No peer-review call contacted the participant model.

The first implementation review returned `REVISE_RUNNER` from Composer, Grok,
and Kimi. Their union found an unfrozen newline in the static-expanded prompt,
a path that could emit the weak delivery label alongside a control collapse,
and missing public formation-condition names in candidate evidence. The runner
restored the exact prompt bytes, made every frozen collapse suppress the weak
label, retained the eight mechanism condition names, strengthened account
lineage, and added a collapse regression. It then passed 15 focused tests and
the combined 362-test suite.

The same three reviewers examined that repaired snapshot in read-only mode.
Terminal results:

- `composer-2.5`: `RUNNER_CONFORMS`
- `cursor-grok-4.6-high-fast`: `RUNNER_CONFORMS`
- `kimi-k3-max`: `RUNNER_CONFORMS`

These verdicts license only the charter's one live start. They do not license
prompt repair, replication, a successor model, later-action cases, or
validation.
