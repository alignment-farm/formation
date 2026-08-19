# Exact-draft challenge exploratory contact charter

Status: **consumed independently reviewed strict-budget charter; its one
participant-model contact is complete with no mechanism label and null
Formation and validation verdicts, and no rerun, successor, replication, or
validation is licensed**.

## Charter decision

Charter one bounded authorship-only contact under the independently reviewed
[exact-draft challenge mechanism](DRAFT_CHALLENGE_MECHANISM.md).

The contact asks:

> For one predeclared first-draft output from each fresh occurrence, what stable
> exact candidate bytes appear when the same cold model receives the exact
> draft plus a generic challenge, and which frozen request conditions reproduce
> them?

The contact does not ask whether a later candidate is better, correct,
admissible, experience-grounded, transferable, or evidence of Formation. A
malformed first draft still enters raw challenge when its exact string can be
represented. Unchanged, awkward, wrong, withdrawn, unstable, malformed, or
unavailable results all complete the exploration.

This charter changes authorship process while keeping the participating model,
public rule, action interface, occurrence representation, JSON interface,
sampling settings, and lexical governor fixed. It does not reopen admission or
model search.

## Operational model and provider

Use the same artifact that participated in the phase-coupled and occurrence-
accounting contacts:

```text
model request identifier: ai/qwen3:14B-Q6_K
Docker inspect tag: docker.io/ai/qwen3:14B-Q6_K
artifact digest: sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219
format: GGUF
architecture: qwen3
quantization: IQ1_S/Q6_K
parameters: 14.77 B
endpoint: http://localhost:12434/engines/llama.cpp/v1/chat/completions
```

Freeze the serving stack for this packet as:

```text
Docker Model Runner client/server: v1.2.6
Docker Desktop: 4.87.0 (236836)
llama.cpp backend build: b9879-metal
llama.cpp backend digest: sha256:b70706f473b4043ca3e0c32704a7fda3412b83bceef0564684187b8011230de8
```

Before contact, retain fresh `docker model list`, `inspect`, `status`,
`version`, Docker version, and endpoint reachability receipts. Stop before the
first request if the model digest, runner version, Docker Desktop version,
backend name or digest, endpoint, or required receipt differs or is
unavailable. Do not silently treat a provider upgrade as the chartered setup.

Do not use `gpt-oss:20B`, download or substitute another model, compare model
families, alter the model artifact, or reopen admission. The machine has ample
memory for the already installed artifact; that operational fact is not a
competence claim.

Every call is cold: one system/user pair, no assistant history, provider
conversation, session identifier, undeclared prefix, or response reuse. Retain
any provider cache or prefix metadata that exists. Passive unreported backend
effects remain a limitation; the byte-identical withheld condition is the
observable audit.

## Fixed request settings and completion budget

Every ordinary candidate invocation uses:

```json
{
  "model": "ai/qwen3:14B-Q6_K",
  "max_tokens": 256,
  "temperature": 0.6,
  "top_p": 0.95,
  "stream": false,
  "response_format": {"type": "json_object"}
}
```

Thus the mechanism's single-call allowance is `B = 256`. Same-response alone
uses `max_tokens = 512`, exactly `2B`. Actor calls use `max_tokens = 128` with
the same temperature, `top_p`, streaming, and JSON-mode settings. Do not send
`seed`, `top_k`, `repeat_penalty`, an authorization header, a schema-shaped
`response_format`, or any other unlisted inference option.

Every user instruction ends in `/no_think`. Only
`choices[0].message.content` supplies actions or candidates. Retain reasoning,
thinking, refusal, finish-reason, usage, and complete response-envelope fields
as audit evidence, but never substitute them for content.

The maximum completion-token allowance is 10,624: three actor calls at 128,
thirty-two ordinary candidate calls at 256, and four same-response calls at
512. This is an allowance ceiling, not an expected spend. Record actual prompt
and completion tokens for every response.

## Public rule, action interface, and occurrence construction

Use the exact public rule, actor system message, actor user template, action
parser, action commitment, and canonical occurrence projection owned by the
[phase-coupled charter](PHASE_COUPLED_EXPLORATORY_CHARTER.md) and implemented by
`micro_environment/phase_coupled_specimen.py`. No prompt may expose a hidden
profile, increasing slot, expected relation, expected action, condition name,
governor result, or peer-review language.

The disposable interface call and both World G and World H acquisition calls
use the exact actor user message with experience-derived `material` JSON null,
byte-identical to `offer_envelope(None)`. Do not omit the material section,
preload an occurrence or candidate, or add another actor offer.

One disposable interface call requests one action from the two displayed
controls and `hold`. Any exact listed one-action object satisfies this minimal
interface check. Correctness and a particular action are not scored. An
invalid or unobservable disposable result stops the packet before acquisition
because the environment cannot apply an undeclared action. Record this only as
an interface stop, never model inadmission.

Each fresh world then requests exactly two listed control actions. Repetition
is valid. Every valid pair is committed and applied without intermediate model
feedback. The environment issues the canonical two-step occurrence. An invalid
or unobservable pair makes only that world unavailable; retain it and continue
the other world. Do not repair, replace, or resample an action.

## Fresh deterministic worlds

All identifiers derive prospectively from specimen seed
`formation.phase-coupled-control.specimen.v1`. Profile slots and counters below
are harness-only. World names, counters, slots, and expected profiles never
enter a model request.

### Disposable interface

```text
family counter: 10
controller family: 89572ec331e3be44
phases: [5d8e06e178f2e72d, 42f63674573a11a3]
hidden phase-zero increasing slot: 0
device counter: 25
device: 764226e12f57f878
start phase: 5d8e06e178f2e72d
position: 3
target: 3
controls: [de8a1aa2d11135b5, 0bb7b5ead4ac392b]
```

### World G

```text
family counter: 8
controller family: cd32522fbc89d0cc
phases: [ccdabc1e1f6ca491, de7c867e5bd687b5]
hidden phase-zero increasing slot: 0
device counter: 23
device: fde26f170afcc3ae
start phase: ccdabc1e1f6ca491
position: 0
target: 2
controls: [7e81cf4ce9afe7ad, 183609a9f5e6b701]
```

### World H

```text
family counter: 9
controller family: 04a6549a17c2f498
phases: [b1a356711b7c0edf, 0a4aa47fe9bf67f7]
hidden phase-zero increasing slot: 1
device counter: 24
device: e52fe06ac648cd96
start phase: b1a356711b7c0edf
position: 0
target: 2
controls: [aa94f3ae24c6630b, a3dd902b2fe11658]
```

World G and H material never crosses. Each world is reported separately. The
mirrored hidden profiles create complementary opportunities for later semantic
inspection, but no expected candidate or semantic scorer is selected by this
charter.

## Exact source-draft identity

Use `N = 2` independent samples for every candidate condition that runs. Do not
resample instability.

Before contact, freeze these ordered direct-candidate identifier lists:

```text
World G: [candidate-g-direct-1, candidate-g-direct-2]
World H: [candidate-h-direct-1, candidate-h-direct-2]
```

The first identifier in each list is that world's source-draft identifier. It
is not the first response to complete or a packet-global index. No actor,
interface, other world, or later direct result may become the source. The exact
decoded `choices[0].message.content` string from that invocation remains the
source even if it is empty, malformed, uninteresting, refused, or unlike the
second direct result.

Run and retain all four direct invocations before constructing either prompt-
mass control and before any other candidate condition begins. The physical
direct order is frozen below. Parsing, stability, and governance cannot replace
the source string.

Use the mechanism's Unicode-scalar check and
`canonical_json_bytes({"material":{"draft_content":source_string}})` without
change. An unencodable, missing, JSON-null, or non-string source makes only
draft-dependent requests unavailable. A malformed but encodable string still
enters exact replay and challenge. Never read provider reasoning text as the
draft.

## Candidate prompts and nine conditions

Use the exact candidate system message, base authorship responsibility,
challenge responsibility, near-clone static responsibility, same-response
messages, repeated occurrence, and deterministic restatement frozen in the
[mechanism](DRAFT_CHALLENGE_MECHANISM.md). The runner may substitute only the
exact public rule, canonical occurrence bytes, canonical material envelope,
and declared source or mass-control string at their placeholders.

For every observable world construct these nine conditions:

| Condition | Lineage and request material | Responsibility |
| --- | --- | --- |
| `direct_candidate` | occurrence root; material null | base authorship |
| `draft_withheld` | source receipt retained; byte-identical direct request | base authorship |
| `exact_draft_replay` | source receipt is request parent; exact draft material | base authorship |
| `static_challenge_withheld_draft` | source receipt retained; material null | exact static review |
| `exact_draft_challenge` | source receipt is request parent; exact draft material | exact challenge |
| `same_response_draft_challenge` | occurrence root; no retained draft | exact nested same-response responsibility |
| `occurrence_repeated` | occurrence root; exact occurrence as material | base authorship |
| `deterministic_restatement` | occurrence root; mechanism-owned restatement | base authorship |
| `draft_prompt_mass_control` | source group; deterministic non-draft string | exact challenge |

Direct sample 1 and sample 2 are the two `direct_candidate` members. Withheld
request bodies and inference settings must be byte-identical to their same-
world direct requests. Logical identifiers, evidence paths, and lineage fields
must not enter provider request bytes.

The output parsers, canonical candidate bytes, double-null withdrawal object,
same-response key order, internal stability, withheld invalidation, exact
matches, equivalence labels, and complete-label rules are mechanism-owned and
may not change in the charter or runner.

## Tokenizer-bound prompt-mass control

The preflight tokenizer vocabulary and merges are pinned to the official
`Qwen/Qwen3-14B` tokenizer artifact:

```text
repository: Qwen/Qwen3-14B
revision: 7d3da9c56f02b22d31dc1ca97c7ee628d1e2e237
file: tokenizer.json
UTF-8 length: 11,422,654 bytes
SHA-256: aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4
tokenizer model reported by GGUF: gpt2
tokenizer pre-tokenizer reported by GGUF: qwen2
BOS token id: 151643
EOS token id: 151645
add BOS: false
```

The provider chat template is not taken from the remote tokenizer config. It
is the exact `tokenizer.chat_template` string in the installed Docker model
inspect receipt. For the chartered artifact its draft-time values were:

```text
UTF-8 length: 4,100 bytes
SHA-256: 57f1fd00f0013a2be96aa79b857391f27e23df5b5f847072b524c897e24d0361
```

Before runner review, materialize the pinned tokenizer file outside evidence,
verify its hash and special identifiers against model inspect, retain the exact
inspect chat-template bytes, and freeze the tokenizer implementation and
version. Render the two-message request with `tools` omitted,
`add_generation_prompt=True`, and `enable_thinking` omitted and therefore
undefined. Tokenize that exact rendered system/user chat with
`add_special_tokens=False`. Unit tests must show the renderer follows the
inspect template under exactly those bindings. A tokenizer or template mismatch
makes the mass instrument unavailable; it never licenses a different tokenizer,
binding, seed, or model request.

Use:

```text
public seed: formation.draft-challenge.prompt-mass.v1
alphabet: GHIJKLMNOPQRSTUVWXYZ
maximum prefix length: 8192 Unicode code points
```

The constructor is exactly:

1. Outside the constructor, render and tokenize the complete exact-draft-
   challenge request. Pass only its integer token count to the constructor.
2. Create an infinite deterministic character stream. For counter `k` starting
   at zero, compute
   `SHA256(canonical_json_bytes([public_seed,k]))`; for each digest byte in
   order, append `alphabet[byte % len(alphabet)]`.
3. For prefix lengths from 0 through 8192 inclusive, place that prefix in the
   public `draft_content` hole, build the exact canonical material envelope and
   challenge request, render the exact chat template, and tokenize it.
4. Select the first prefix whose complete rendered prompt-token count equals
   the target. Freeze its string, bytes, length, request hash, and token count
   before any downstream candidate call. If none matches, mark mass unavailable
   without another seed, alphabet, bound, tokenizer, or search.

The constructor receives only the target integer, public seed, alphabet,
bound, tokenizer artifact, exact public request template, occurrence, public
rule, and canonical encoder. It cannot receive the source string, source bytes,
source hash, parsed source candidate, governor result, hidden profile, or any
model output except the permitted integer target. The public template contains
only a hole and no draft-derived bytes. The uppercase alphabet cannot contain
the lowercase hexadecimal acquisition controls.

Preflight equality requires exact local tokenizer equality between challenge
and mass-control prompts. Contact-time availability additionally requires the
provider to report the same `prompt_tokens` value for all `N` challenge calls
and all `N` mass-control calls in that world. Missing usage or any mismatch
makes prompt mass and both complete mechanism labels unavailable. The calls and
costs remain evidence. No token discrepancy is retried or repaired.

## Exact schedule

The maximum logical schedule is 39 calls:

1. disposable actor interface;
2. World G acquisition;
3. World H acquisition;
4. `candidate-g-direct-1` — World G source draft;
5. `candidate-h-direct-1` — World H source draft;
6. `candidate-g-direct-2`;
7. `candidate-h-direct-2`;
8. freeze both constructible prompt-mass controls without a model call; and
9. up to 32 downstream candidate calls: eight remaining conditions times two
   samples in each observable world.

If a world occurrence is unavailable, omit every candidate call for that
world. If a source content value cannot construct draft material, omit only
`exact_draft_replay`, `exact_draft_challenge`, and
`draft_prompt_mass_control`; run its unaffected conditions. If mass search
alone fails, omit only mass. Every omission is explicit evidence and forbids
the complete label.

After all scheduled direct calls finish, use this downstream order:

| Round | World | Frozen condition order |
| --- | --- | --- |
| 1 | G | withheld, replay, static, challenge, same response, repeated, restatement, mass |
| 1 | H | mass, restatement, repeated, same response, challenge, static, replay, withheld |
| 2 | G | challenge, same response, repeated, restatement, mass, withheld, replay, static |
| 2 | H | static, replay, withheld, mass, restatement, repeated, same response, challenge |

Finish all scheduled round-1 calls before round 2. Condition aliases in this
table map exactly to the public names above. No concurrent request or response-
completion ordering may alter the schedule.

## Attempts, stops, and consumption

The hard physical-attempt ceiling is 42. Retry a logical call once only after a
local transport failure that produced no HTTP response, and never beyond the
physical ceiling. Every attempt spends the ceiling. Do not retry HTTP errors,
empty or malformed content, invalid actions, non-string content, instability,
governor refusal, tokenizer disparity, truncation, or awkward behavior.

Stop the full packet on model or backend drift, exhausted physical ceiling, an
unobservable disposable interface, an HTTP error, evidence-write failure, or
request-integrity failure. An invalid acquisition or missing source affects
only its declared world or dependent cells as above.

Do not change prompts, worlds, identifiers, source designation, condition
order, settings, tokenizer artifacts, constructor inputs, parser, `N`, `B`,
retry rule, or attempt ceiling after contact begins. The charter is consumed by
one live start even if a stop or unavailable cell prevents interpretation.

## Governance, comparisons, and reporting

No governor or semantic scorer runs until every scheduled authorship invocation
has completed or hit a frozen stop and every response has been retained. Then
apply the unchanged phase-coupled lexical governor to each parseable candidate
that enters cross-condition equality. Governor results never enter request
lineage, define equality, select a draft, or determine whether challenge runs.

No semantic scorer is selected. Report exact text, parsing, canonical bytes,
lexical governor observations, and costs. Descriptive discussion may note
apparent correctness or awkwardness only as unscored interpretation and may not
promote a label.

Apply the mechanism's rules in order:

1. validate direct/withheld request and settings identity;
2. require internal stability for both audit conditions;
3. apply terminal withheld invalidity, instability, failure, or carryover
   contrast rules;
4. require an available and stable exact-challenge anchor;
5. report exact challenge-source candidate or raw-output matches;
6. report every available exact equivalence collapse;
7. require all nine conditions, internal stability, direct/withheld match, and
   local plus provider prompt-token parity before either complete label; and
8. distinguish non-double-null revision from exact double-null withdrawal.

Worlds never pool. No best-of, majority vote, semantic rescue, cross-world
selection, or favorable sample choice is permitted. Mismatches never eliminate
the corresponding prompt-content explanation.

The terminal summary must contain:

```json
{"formation_verdict":null,"validation_verdict":null}
```

Retain exact request and response bytes, HTTP status, usage, attempt and logical
order, Docker receipts, model and tokenizer hashes, renderer and constructor
records, action and occurrence records, source-draft receipt, raw and canonical
identities, request parents, public formation conditions, candidates,
withdrawals, malformed content, availability decisions, every comparison,
governor receipts, stops, and natural costs. An integrity audit must recompute
all retained request and response hashes before interpretation review.

## Claim and stopping boundary

The strongest possible result is only the mechanism-owned
`draft-challenge-associated exact candidate revision` or
`draft-challenge-associated exact candidate withdrawal` for one world. It says
that stable exact bytes under one frozen request were not exactly reproduced by
the frozen controls. It does not claim causation, improvement, grounding,
retention necessity, acquired competence, development, or Formation.

Any exact match, control collapse, audit failure, instability, malformed
source, missing usage, mass mismatch, same-response failure, wrong candidate,
governor refusal, withdrawal, or unavailable comparison is a valid terminal
outcome. One bounded result closes this route.

No outcome licenses prompt repair, another source draft, added experience,
model substitution, another tokenizer, another charter, replication, later-
action testing, validation, or Formation claims. A separate post-contact
problem document would be required to interpret what hard problem the contact
actually exposed.

## Two-review gate

Two independent adversarial Cursor reviews must try to show that source
identity, fresh worlds, request bytes, schedule, tokenizer construction,
conditional omissions, completion allowances, retry policy, governor timing,
comparison order, or 42-attempt ceiling can select a convenient draft, repair
malformed behavior, manufacture a revision, or hide a null.

One `CHARTER_STABLE` verdict each from Composer 2.5 and Grok 4.6 licenses only a
separate fake-tested runner implementation. Runner conformance review remains
required before the first participant-model request and must use both reviewers.
Peer review may not call the participant model.

## Review record

Grok 4.6 reviewed the complete charter through Cursor `agent` in read-only
`ask` mode and first returned `REVISE_CHARTER`. It found three undeclared
implementation choices: actor material was not explicitly bound to null, the
text both disclaimed and required backend identity, and the tokenizer section
did not freeze all chat-template render arguments.

The repair binds all three actor calls to exact null material, freezes Docker
Model Runner `v1.2.6`, Docker Desktop `4.87.0 (236836)`, llama.cpp
`b9879-metal` and its digest, and fixes `tools`, generation-prompt, thinking,
and added-special-token bindings. The same reviewer then checked the exact
repaired text and returned:

- `cursor-grok-4.6-high-fast`: `CHARTER_STABLE`

The review used no participant-model request. After the reviewer policy was
restored to two independent passes, Composer 2.5 independently reviewed the
same repaired charter and found no further material defect. Final verdicts:

- `composer-2.5`: `CHARTER_STABLE`
- `cursor-grok-4.6-high-fast`: `CHARTER_STABLE`

Together they license only a separate fake-tested runner and later two-reviewer
runner-conformance gate.

The runner then passed 19 focused fake-contact tests and the combined 381-test
repository suite. Composer's first runner audit returned `REVISE_RUNNER`
because the prompt-mass counter reproduced the known no-tools template branch
instead of applying the verified inspect template, and because the frozen
tokenizer implementation was not copied into protocol and mass-control
evidence. The repair now applies the hash-verified inspect Jinja template with
`tools` and `enable_thinking` omitted, freezes `tokenizers-0.23.1` and
`jinja2-3.1.6`, and records both implementations. The real pinned tokenizer
then constructed exact prompt-token matches for both fresh worlds.

Composer 2.5 and Grok 4.6 independently checked the same repaired runner in
read-only Cursor sessions. Neither review called the participant model. Final
runner verdicts:

- `composer-2.5`: `RUNNER_CONFORMS`
- `cursor-grok-4.6-high-fast`: `RUNNER_CONFORMS`

Together they licensed the charter's single live contact.

## Contact disposition

The single contact then completed all 39 logical calls in 39 physical attempts
without retry. World G's exact challenge was unstable. World H's exact
challenge reproduced the source draft exactly. Neither world earned a revision
or withdrawal label, and both Formation and validation verdicts remain null.

The [evidence account](../evidence/draft-challenge-exploratory-contact-20260818/README.md)
and [post-contact boundary](POST_CHALLENGE_AUTHORSHIP_BOUNDARY.md) passed final
Composer 2.5 and Grok 4.6 interpretation review. The charter is consumed and
licenses no further contact.
