# Executable prediction revision exploratory charter

Status: **consumed by one completed independently reviewed contact; retained as
the exact contract for that evidence and licenses no rerun, successor,
influence test, validation packet, or Formation claim**.

## Charter decision

Charter one bounded authorship-only contact under the reviewed
[executable prediction revision mechanism](EXECUTABLE_PREDICTION_REVISION_MECHANISM.md).

The contact asks what functions appear in the first model-authored successor
after a retained parent prediction encounters one independent result. It also
runs the mechanism's no-result, no-parent, sampling, same-response, repeated-
source, restatement, visible-material, and static controls.

The report contains only atomic condition facts and complete denominators. It
has no success, revision, validation, or Formation verdict. Wrong, constant,
copied, prose, fenced, empty, out-of-scope, unavailable, unchanged, and
overcorrected outputs all complete the contact.

## Operational model and provider

Use the installed Qwen artifact that completed the prior contact:

```text
request model: ai/qwen3:14B-Q6_K
inspect tag: docker.io/ai/qwen3:14B-Q6_K
artifact digest: sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219
format: GGUF
architecture: qwen3
quantization: IQ1_S/Q6_K
parameters: 14.77 B
endpoint: http://localhost:12434/engines/llama.cpp/v1/chat/completions
```

Freeze this serving stack:

```text
Docker Model Runner client/server: v1.2.6
Docker Desktop: 4.87.0 (236836)
Docker Engine: 29.7.2
llama.cpp backend: b9879-metal
backend digest: sha256:b70706f473b4043ca3e0c32704a7fda3412b83bceef0564684187b8011230de8
```

Before contact, retain fresh model list, inspect, Model Runner version and
status, Docker version, backend, and endpoint receipts. Stop before the first
request if any frozen identity differs or cannot be observed. Do not use
`gpt-oss:20B`, download a replacement, compare models, or reopen admission.

Every call is cold: one system/user pair, no assistant history, provider
conversation, session identifier, undeclared prefix, tool definition, or
response reuse. Only `choices[0].message.content` supplies participant output.
Reasoning fields remain audit evidence and never replace content.

The installed artifact's `tokenizer.chat_template` is also frozen:

```text
UTF-8 length: 4,100 bytes
SHA-256: 57f1fd00f0013a2be96aa79b857391f27e23df5b5f847072b524c897e24d0361
```

Before contact, the runner must retain the exact inspect bytes and verify both
values. Its render audit uses that template with exactly one system message,
one user message, `tools` omitted, `add_generation_prompt=True`, and
`enable_thinking` omitted and therefore undefined. The HTTP body itself sends
only the two declared messages and the settings below. Retain any provider
cache or prefix metadata that exists. Passive backend caching that the provider
does not report remains a limitation on the sampling comparisons; it cannot be
turned into evidence of independence.

## Inference settings

Every ordinary rule-authorship call uses:

```json
{"max_tokens":512,"model":"ai/qwen3:14B-Q6_K","stream":false,"temperature":0.6,"top_p":0.95}
```

Do not send `response_format` on ordinary rule calls. Their complete content is
the raw rule. Do not send `seed`, `top_k`, `repeat_penalty`, authorization,
tools, or any unlisted option.

Acquisition and disposable-interface calls use the same settings except
`max_tokens = 128` and `response_format = {"type":"json_object"}`.

Same-response calls use the ordinary settings except `max_tokens = 1024` and
`response_format = {"type":"json_object"}`. This is the mechanism's disclosed
non-parity interface. Every user message ends in `/no_think`.

The provider-output ceiling is therefore 512 tokens for every single rule and
1024 tokens for the two-rule same-response envelope. The recognizer must remain
total for every content string within those ceilings.

Freeze these instrument identifiers:

```text
canonical JSON: executable-prediction-canonical-json-v1
rule recognizer: executable-prediction-rule-recognizer-v1
rule evaluator: executable-prediction-rule-evaluator-v1
witness constructor: executable-prediction-witness-v1
```

## Public fields and prediction vocabularies

Every public test input has exactly these keys in this order when rendered:

```text
facet
mark
zone
```

Order is presentation only; evaluator input is a map. Each world has a separate
two-token prediction vocabulary:

```text
World J: [zafren, ulmec]
World K: [qoril, vesan]
```

No input key or value equals a vocabulary token, case coordinate, hidden role,
or result-field name. World material never crosses between requests.

## Fresh worlds and oracle

The following complete manifests freeze before contact. Only the input maps and
public prediction vocabularies may enter participant requests. Coordinates,
roles, and expected results remain harness-only until a scheduled atomic result
is revealed.

### World J

| Coordinate | Hidden role | facet | mark | zone | Oracle result |
| --- | --- | --- | --- | --- | --- |
| J0 | acquisition | fira | mela | zuna | ulmec |
| J1 | primary_test | fira | melo | zuna | zafren |
| J2 | transfer | firo | mela | zuna | zafren |
| J3 | transfer | firo | melo | zuna | ulmec |
| J4 | non_transfer | fira | mela | zuno | zafren |
| J5 | non_transfer | fira | melo | zuno | ulmec |
| J6 | copy_control | fira | mela | zuni | zafren |
| J7 | copy_control | firo | melo | zuni | ulmec |
| J8 | later_revision_test | firo | mela | zuno | ulmec |

The frozen oracle is:

```text
zone zuna: zafren exactly when exactly one of facet=fira and mark=mela is true;
           otherwise ulmec
zone zuno: reverse the zuna result
zone zuni: zafren when facet=fira; otherwise ulmec
```

### World K

| Coordinate | Hidden role | facet | mark | zone | Oracle result |
| --- | --- | --- | --- | --- | --- |
| K0 | acquisition | dara | kela | puna | vesan |
| K1 | primary_test | dara | kelo | puna | qoril |
| K2 | transfer | daro | kela | puna | qoril |
| K3 | transfer | daro | kelo | puna | vesan |
| K4 | non_transfer | dara | kela | puno | qoril |
| K5 | non_transfer | dara | kelo | puno | vesan |
| K6 | copy_control | dara | kela | puni | qoril |
| K7 | copy_control | daro | kelo | puni | vesan |
| K8 | later_revision_test | daro | kela | puno | vesan |

The frozen oracle is:

```text
zone puna: qoril exactly when exactly one of facet=dara and mark=kela is true;
           otherwise vesan
zone puno: reverse the puna result
zone puni: qoril when facet=dara; otherwise vesan
```

The primary inputs differ from acquisition inputs. J1 and K1 are new external
events, not replayed acquisition receipts. J8 and K8 are fixed before either
successor exists and may confirm, contradict, or fall outside the successor's
scope.

The case-manifest artifact is canonical JSON with top-level keys
`protocol_version` and `worlds`. Its protocol version is
`executable-prediction-case-manifest-v1`. World order is J then K. Each world
has `world`, `prediction_vocabulary`, and `cases`; case order is coordinate 0
through 8, and each case has `coordinate`, `hidden_role`, `input`, and
`oracle_result`. Using the canonical serializer frozen below, the complete
artifact is 2,473 UTF-8 bytes with SHA-256
`2a07f9b6b4982af60df69353f5893f04d4fcc9b537140f0226bf9e1eafd2084b`.
The runner must independently reproduce this binding before contact.

## Held-out non-identification witness

Let `H` have the exact meaning fixed by the mechanism: every AST rule that
returns a vocabulary prediction on all nine cases in its world.

All nine public maps in each world are unique. For any complete assignment of
vocabulary outputs to those maps, the following finite AST is in `H`:

1. For each case assigned the world's second vocabulary token, build a selector
   that compares all three public fields to that case's values and joins the
   comparisons with `and`.
2. In manifest order, nest one `if` per selected case. Its `then` branch is the
   second vocabulary literal.
3. The final `else` branch is the world's first vocabulary literal.
4. Set `when` to `{"bool":true}`.

For every revealed prefix and held-out case `h`, exhibit two compact assignments.
Both use the world's first vocabulary token as their default. For each revealed
case whose result is the second vocabulary token, add one exact three-field
selector returning that second token. The first witness keeps the default on
`h`; the second adds one selector for `h` returning the second token. Applying
the constructor produces two members of `H` that agree on the visible prefix
and disagree on `h`, with at most one selector per revealed case plus one for
`h`.

The required prefixes are exactly:

```text
after_acquisition: J0 or K0
after_primary:     J0,J1 or K0,K1
after_later:       J0,J1,J8 or K0,K1,K8
```

At each prefix, the held-out cases are coordinates 2 through 7 in that world.
This yields 18 pairs per world and 36 pairs total.

The witness constructor is byte-deterministic. It serializes JSON with keys
sorted by Unicode code-point order, separators `,` and `:` with no following
space, UTF-8, and no ASCII escaping. A three-field selector compares `facet`,
then `mark`, then `zone`; it joins the first two comparisons with `and`, then
joins that result to the third comparison. The manifest order is coordinate 0
through 8. To make the lowest selected coordinate the outermost `if`, build
selected cases in reverse manifest order. Each rule is exactly `RULE_AST_V1`,
one LF byte, and the canonical JSON object with `when={"bool":true}` and the
constructed `predict` expression. The complete witness artifact is one
canonical JSON object with this shape:

```json
{"protocol_version":"executable-prediction-witness-v1","worlds":[{"pairs":[{"heldout":"coordinate","left_raw":"complete-rule","left_vector":["nine-results"],"prefix":"prefix-name","revealed":["coordinates"],"right_raw":"complete-rule","right_vector":["nine-results"]}],"static_rule_raw":"complete-rule","static_rule_vector":["nine-results"],"world":"J-or-K"}]}
```

World order is J then K. Pair order is prefix order above and then held-out
coordinate order. The charter-time materialization has:

```text
UTF-8 length: 45,357 bytes
SHA-256: 754169a7eeb1ab36ce3a0172551022c48fd2d16dd9b76152b0b52847ba11333e
World J static rule: 906 bytes, SHA-256 f315863c5f69ced00aadd5f03c5e5e18fba8ec94bb17dbba0156149621d9a7c8
World K static rule: 905 bytes, SHA-256 6d366d96ce11104227d63ef08b7335190c49d31456eed026db23e07dda79d521
```

The J and K static vectors are respectively:

```json
["ulmec","zafren","zafren","ulmec","zafren","ulmec","zafren","ulmec","ulmec"]
["vesan","qoril","qoril","vesan","qoril","vesan","qoril","vesan","vesan"]
```

Before any participant request, the runner must independently materialize the
artifact, match its length and hash, evaluate every pair over the complete
manifest, and retain the exact artifact. Any mismatch, missing witness,
non-vocabulary evaluation, selector collision, or disagreement with a visible
prefix stops the packet. Witnesses never enter runtime lineage or model
requests.

This witness proves only that revealed results do not determine a held-out
answer inside the DSL. It does not show that the witness functions are simple
or plausible.

## Exact request construction

Every text block in this section denotes the bytes between the fences: no
leading LF and no trailing LF. A placeholder in angle brackets is replaced
exactly once by the named canonical value. No other formatting, indentation,
line wrapping, or substitution is permitted.

Canonical JSON is UTF-8 JSON with keys sorted by Unicode code-point order,
separators `,` and `:` with no following space, and unescaped Unicode. Raw
model strings are represented as JSON string values without trimming or
repair. Public input maps consequently render in `facet`, `mark`, `zone` order.

## Rule language shown to the model

Every ordinary rule call uses this exact system-message template:

```text
You are the rule-authoring component of a cold practitioner. You have no memory
outside this request.

PUBLIC INPUT FIELDS
facet, mark, zone

PREDICTION VOCABULARY
<PREDICTION_VOCABULARY_JSON>

RULE OUTPUT
Your complete response is one rule. Any response string is a rule with global
scope that predicts that exact string.

To author conditional scope or predictions, respond with RULE_AST_V1 on the
first line followed by one JSON object:
{"when":<boolean-expression>,"predict":<string-expression>}

A string expression is exactly one of:
{"lit":<string>}
{"field":<field-name-string>}
{"if":[<boolean-expression>,<string-expression>,<string-expression>]}

A boolean expression is exactly one of:
{"bool":<true-or-false>}
{"exists":<field-name-string>}
{"eq":[<string-expression>,<string-expression>]}
{"neq":[<string-expression>,<string-expression>]}
{"and":[<boolean-expression>,<boolean-expression>]}
{"or":[<boolean-expression>,<boolean-expression>]}
{"not":<boolean-expression>}

Use only public fields and the evidence supplied in this request. Do not add an
explanation outside the rule.
```

This message defines generic syntax. It contains no filled conditional example,
case value, oracle relation, hidden role, expected rule, score, or governor
result.

Replace `PREDICTION_VOCABULARY_JSON` with exactly `["zafren","ulmec"]` for
World J and `["qoril","vesan"]` for World K. The disposable-interface system
message is separate and has no such replacement.

## Acquisition contact and first occurrence

The disposable interface and acquisition system message is:

```text
You are a cold predictor. You have no memory outside this request. Return one
JSON object with the single key "prediction". Its value must be one token from
the supplied prediction vocabulary. Do not add keys or commentary.
```

Its user message is:

```text
PUBLIC INPUT
<PUBLIC_INPUT_JSON>

PREDICTION VOCABULARY
<PREDICTION_VOCABULARY_JSON>

Choose one prediction.
/no_think
```

The disposable call uses this third input and vocabulary, which appear in no
world:

```json
{"input":{"facet":"sava","mark":"temi","zone":"woku"},"prediction_vocabulary":["bren","cavo"]}
```

Any exact prediction of `bren` or `cavo` passes the minimal interface check.
Correctness is not scored. Invalid content stops the packet after retaining
that one call; it is an interface stop, not model inadmission.

World J and K acquisition calls use J0 and K0. A valid listed prediction is
committed even when wrong. The oracle then issues its atomic result. Invalid
action content is retained as `prediction_unavailable`; the oracle result still
occurs and the world continues, but no later report may call its first
experience consequential prediction feedback.

The canonical first occurrence is produced by exactly one of these two total
templates:

```json
{"input":<PUBLIC_INPUT_JSON>,"prediction":{"status":"available","value":<PREDICTION_TOKEN_JSON>},"result":{"authority":"environment_oracle","value":<RESULT_TOKEN_JSON>}}
{"input":<PUBLIC_INPUT_JSON>,"prediction":{"status":"prediction_unavailable","value":null},"result":{"authority":"environment_oracle","value":<RESULT_TOKEN_JSON>}}
```

The first applies only when strict acquisition parsing returns one vocabulary
token. The second applies to every other response. `PREDICTION_TOKEN_JSON` and
`RESULT_TOKEN_JSON` are canonical JSON strings, not bare text.

## Ordinary authorship request

Every ordinary rule call uses the shared world-specific system message above.
Its user message is:

```text
FIRST EXPERIENCE
<FIRST_OCCURRENCE_JSON>

RUNTIME MATERIAL
<RUNTIME_MATERIAL_JSON>

AUTHORSHIP RESPONSIBILITY
Author the one prediction rule you can support now from the supplied evidence.
Your complete response becomes the first retained attempt for this condition.
/no_think
```

Every material object has exactly these six keys. The parent-call base is:

```json
{"additional_experience":null,"external_result":{"status":"not_available","value":null},"parent_attempt_coordinate":null,"parent_raw":null,"test_input":null,"trial":{"status":"not_available","value":null}}
```

The parent-reference coordinates that may enter material are exact strings:

```text
iv04.content  iv05.content
iv08.content  iv17.content
pvj01         pvk01
```

The first row names the J and K parent outputs, the second row their selected
first-successor outputs, and the third row the protocol-authored visible
parents. The strings contain no role or condition word.

For a selected first successor, render this object after replacing every JSON
placeholder with its canonical value:

```json
{"additional_experience":null,"external_result":{"status":"revealed","value":<RESULT_TOKEN_JSON>},"parent_attempt_coordinate":<PARENT_COORDINATE_JSON>,"parent_raw":<PARENT_RAW_JSON_OR_NULL>,"test_input":<PUBLIC_INPUT_JSON>,"trial":{"status":<TRIAL_STATUS_JSON>,"value":<TRIAL_VALUE_JSON_OR_NULL>}}
```

`PARENT_COORDINATE_JSON` is `"iv04.content"` or `"iv05.content"` even when
provider content is unavailable. `PARENT_RAW_JSON_OR_NULL` is the exact content
string or null. The only trial forms are:

```json
{"status":"prediction","value":<EXACT_PREDICTION_JSON>}
{"status":"out_of_scope","value":null}
{"status":"evaluation_unavailable","value":null}
{"status":"rule_unavailable","value":null}
```

`EXACT_PREDICTION_JSON` may be outside the public vocabulary. The result-
withheld object is byte-identical to the selected object except that
`external_result` is exactly
`{"status":"result_not_revealed","value":null}`. This is the charter's exact
binding of the mechanism marker. The parent-withheld object is:

```json
{"additional_experience":null,"external_result":{"status":"revealed","value":<RESULT_TOKEN_JSON>},"parent_attempt_coordinate":null,"parent_raw":null,"test_input":<PUBLIC_INPUT_JSON>,"trial":{"status":"not_available","value":null}}
```

Visible-material successor objects use the selected template with the exact
control literal as `parent_raw`. World J uses `pvj01` as its parent-reference
coordinate; World K uses `pvk01`.

Repeated-occurrence calls retain the acquisition occurrence in `FIRST
EXPERIENCE` and place the same exact canonical occurrence JSON in
`additional_experience`; every other material field equals the parent-call
base. This duplication is the treatment being measured. Deterministic-
restatement calls instead use exactly one of these strings as
`additional_experience`:

```text
The public input was fira, melo, zuna. The environment result was zafren.
The public input was dara, kelo, puna. The environment result was qoril.
```

They retain the acquisition occurrence in `FIRST EXPERIENCE` and every other
material field equals the parent-call base. The renderer contains no relation
inference.

### Later-cycle material

The later selected call uses the selected object template with the exact raw
content from call 08 or 17 and J8 or K8 as `test_input`. Its
`parent_attempt_coordinate` is `"iv08.content"` for J or `"iv17.content"` for
K, including when the referenced content is unavailable. If that call has no
string content, `parent_raw` is null and trial is exactly
`{"status":"rule_unavailable","value":null}`. Otherwise the trial is one of
the other three frozen forms, produced only by evaluating that exact rule on J8
or K8. Its external result is the J8 or K8 atomic oracle result. The acquisition
occurrence remains unchanged in `FIRST EXPERIENCE`; primary-cycle material
does not recur elsewhere in the request.

The later repeated-successor request is byte-identical to that later selected
request. The later result-withheld request changes only `external_result` to
the exact `result_not_revealed` object. The later parent-withheld request uses
the parent-withheld template with J8 or K8 and its result. These are the complete
bindings for calls 26 through 29 and 31 through 34.

## Same-response condition

The first-cycle same-response system message is the exact ordinary system
message, followed by two LF bytes and this suffix:

```text
SAME-RESPONSE ENVELOPE
Return exactly one JSON object with keys "parent" and "successor" in that order.
Each value must be either a string containing one complete raw rule under RULE
OUTPUT or null for unavailable content. Do not add keys or commentary.
```

Its user message is:

```text
FIRST EXPERIENCE
<FIRST_OCCURRENCE_JSON>

PRIMARY EXPERIENCE
{"input":<PUBLIC_INPUT_JSON>,"result":{"authority":"environment_oracle","value":<RESULT_TOKEN_JSON>}}

SAME-RESPONSE RESPONSIBILITY
First author the parent you would support if PRIMARY EXPERIENCE were absent.
Then author the successor you support using all supplied evidence.
Return both through the required envelope.
/no_think
```

The later-cycle same-response call uses the same augmented system message and
this user message:

```text
FIRST EXPERIENCE
<FIRST_OCCURRENCE_JSON>

CURRENT PARENT
<PARENT_RAW_JSON>

LATER EXPERIENCE
{"input":<PUBLIC_INPUT_JSON>,"result":{"authority":"environment_oracle","value":<RESULT_TOKEN_JSON>}}

SAME-RESPONSE RESPONSIBILITY
Put CURRENT PARENT unchanged in "parent", including JSON null when it is null.
Author one successor using all supplied evidence and put it in "successor".
Return both through the required envelope.
/no_think
```

For calls 30 and 35, `FIRST_OCCURRENCE_JSON` is the unchanged J or K acquisition
occurrence. `PARENT_RAW_JSON` is the canonical JSON string for the exact content
from call 08 or 17, or the JSON literal `null` when that content is unavailable.
`PUBLIC_INPUT_JSON` and `RESULT_TOKEN_JSON` are J8 and its result for call 30,
and K8 and its result for call 35. These are the complete substitutions; J1 and
K1 do not enter the later same-response request.

Strict parsing retains string values exactly and null values as unavailable
content. Malformed, reversed, other non-string, or extra-key output makes the
comparator unavailable without retry. This condition is
non-parity: the result was visible for the whole first-cycle call; JSON mode,
the augmented system message, the different user message, two-slot output, and
the 1,024-token allowance all differ from ordinary calls. Later-cycle parent
copying is also instructed. Only equality between the envelope successor's
complete nine-case functional vector and the corresponding selected
successor's complete vector can collapse a separate-lineage explanation for
that observed function. Raw equality, AST equality, primary-only equality, and
mismatch support no causal conclusion.

## Static and visible-material controls

The static-instruction call uses the ordinary world-specific system message and
one of these exact user messages. It contains no `FIRST EXPERIENCE` or runtime
material.

```text
STATIC LESSON
zone zuna: zafren exactly when exactly one of facet=fira and mark=mela is true;
otherwise ulmec
zone zuno: reverse the zuna result
zone zuni: zafren when facet=fira; otherwise ulmec

AUTHORSHIP RESPONSIBILITY
Author the one prediction rule that expresses STATIC LESSON.
Your complete response becomes the first retained attempt for this condition.
/no_think
```

```text
STATIC LESSON
zone puna: qoril exactly when exactly one of facet=dara and mark=kela is true;
otherwise vesan
zone puno: reverse the puna result
zone puni: qoril when facet=dara; otherwise vesan

AUTHORSHIP RESPONSIBILITY
Author the one prediction rule that expresses STATIC LESSON.
Your complete response becomes the first retained attempt for this condition.
/no_think
```

The case tables, not this prose, are the operational oracle. The static lesson
is a disclosed answer-bearing ceiling.

The static-rule evaluator ceiling is the exact AST and vector bound by the
witness artifact hashes above. It is protocol-authored, evaluated once on all
cases, and never enters a model request.

The visible-material parents are these exact raw literal strings:

```text
World J: CONTROLJQPXMV
World K: CONTROLKZRWHD
```

They do not begin with `RULE_AST_V1`, are not vocabulary tokens, and differ
from both primary results. Each is wrong on every case, including both
copy-control cases. The deterministic protocol constructor authors the control
proposal receipt. The evaluator records the literal prediction; the oracle
reveals J1 or K1; and a cold successor receives the same material fields as the
selected condition.

No byte- or token-mass parity claim is made. Prompt mass remains a disclosed
unmatched explanation.

## Exact logical schedule and budget

Freeze this 35-call order before contact:

```text
01 disposable interface
02 J acquisition                 03 K acquisition
04 J parent                      05 K parent
06 J repeated parent             07 K repeated parent
08 J selected successor          09 J repeated successor
10 J result withheld             11 J parent withheld
12 J same response               13 J repeated occurrence
14 J deterministic restatement   15 J visible-material successor
16 J static instruction
17 K selected successor          18 K repeated successor
19 K result withheld             20 K parent withheld
21 K same response               22 K repeated occurrence
23 K deterministic restatement   24 K visible-material successor
25 K static instruction
26 J later successor             27 J later repeated successor
28 J later result withheld       29 J later parent withheld
30 J later same response
31 K later successor             32 K later repeated successor
33 K later result withheld       34 K later parent withheld
35 K later same response
```

Each logical call has a distinct frozen invocation coordinate:

```text
01 iv01  02 iv02  03 iv03  04 iv04  05 iv05  06 iv06  07 iv07
08 iv08  09 iv09  10 iv10  11 iv11  12 iv12  13 iv13  14 iv14
15 iv15  16 iv16  17 iv17  18 iv18  19 iv19  20 iv20  21 iv21
22 iv22  23 iv23  24 iv24  25 iv25  26 iv26  27 iv27  28 iv28
29 iv29  30 iv30  31 iv31  32 iv32  33 iv33  34 iv34  35 iv35
```

These coordinates remain in lineage and never enter request text. An
acquisition output coordinate is `<invocation>.prediction`. An ordinary
single-rule output and any resulting proposal coordinate is
`<invocation>.content`. Same-response coordinates are `<invocation>.parent`
and `<invocation>.successor`. Thus the byte-identical calls 06, 07, 09, 18, 27,
and 32 still have distinct model invocations and candidate identities. The
parent-reference field in request material points backward to `iv04.content`,
`iv05.content`, `iv08.content`, or `iv17.content`; it never takes the current
call's invocation coordinate. Protocol-authored visible parents have proposal
coordinates `pvj01` and `pvk01`. Protocol-authored static rules have coordinates
`svj01` and `svk01`.

Calls 09 and 18 are byte-identical to 08 and 17 respectively. Calls 06 and 07
are byte-identical to 04 and 05. Calls 27 and 32 are byte-identical to 26 and 31.
Every first output remains a separate invocation and candidate identity.

Every condition has two assigned trajectory units, one in each mirrored world.
World-specific strings are compared only through atomic predicates, never exact
cross-world bytes.

The schedule binds request classes without discretion:

| Calls | Request construction |
| --- | --- |
| 01–03 | Acquisition system and user templates with the scheduled input and vocabulary |
| 04–07 | Ordinary template with the parent-call base material |
| 08–10, 17–19 | Ordinary template with selected first-cycle material; calls 10 and 19 use the single withheld-result mutation |
| 11, 20 | Ordinary template with first-cycle parent-withheld material |
| 12, 21 | First-cycle same-response templates |
| 13, 22 | Ordinary template with repeated-occurrence material |
| 14, 23 | Ordinary template with deterministic-restatement material |
| 15, 24 | Ordinary template with visible-material selected material |
| 16, 25 | Static-instruction templates |
| 26–28, 31–33 | Ordinary template with later-cycle material; calls 28 and 33 use the single withheld-result mutation |
| 29, 34 | Ordinary template with later-cycle parent-withheld material |
| 30, 35 | Later-cycle same-response templates |

There is no unlisted prompt branch. Condition labels, schedule coordinates,
hidden roles, expected results, witness data, and scorer fields never enter a
request.

The planned logical completion allowance is 18,816 tokens:

```text
3 interface or acquisition calls * 128 = 384
28 ordinary rule calls * 512             = 14,336
4 same-response calls * 1,024            = 4,096
total                                    = 18,816
```

A transport retry may consume an unobserved backend completion. The separate
physical contingency ceiling is therefore 21,888 tokens: the planned allowance
plus three worst-case 1,024-token attempts. Report planned logical and physical
contingency usage separately. Neither ceiling may be repurposed into an extra
logical call.

The hard logical-call ceiling is 35. The hard physical-attempt ceiling is 38.
A logical call may retry once only after a connection failure or timeout before
any HTTP response. Every physical attempt spends the ceiling. Do not retry HTTP
status responses, malformed envelopes, missing content, truncation, awkward
rules, unavailable evaluations, wrong predictions, or scorer outcomes.

Stop immediately at 38 physical attempts. Any unmade logical calls remain
preassigned unavailable units in the denominator.

## Frozen report

Apply the mechanism's recognizer, evaluator, vector, and atomic projections
without change. Report each world and condition separately and then report:

```text
atomic fact count / 2 assigned world units
```

for every contacted condition. Unavailable calls and evaluations contribute
zero to facts they do not satisfy and remain in the denominator.

Retain raw equality, recognized rule kind, AST equality, functional-vector
equality, primary prediction/result equality, every per-role prediction change,
correct-to-wrong and wrong-to-correct counts, scope changes, and per-role
correctness counts. Report the static-rule ceiling separately without a model-
call denominator.

Pair slots are frozen as follows. Selected, result-withheld, visible-material,
later-selected, and later-result-withheld conditions use their supplied parent
as the parent slot and their returned rule as the successor slot. Repeated
parent is compared to the original parent; repeated successor is compared to
the selected successor for the same cycle. A same-response envelope supplies
its own parent and successor slots, with complete-vector comparison to the
selected successor reported separately. Parent-withheld, repeated-occurrence,
deterministic-restatement, and static-instruction each supply one
`comparator_rule` slot; no parent is invented. For each such output report its
own vector and vector equality to the corresponding selected first successor.
Later parent-withheld is treated the same way against the selected later
successor. Unavailable slots remain explicitly unavailable.

Do not compute a compound pass, revision, success, validation, or Formation
label. The terminal summary must contain exactly:

```json
{"formation_verdict":null,"validation_verdict":null}
```

## Retention and integrity

Retain exact request and response bytes, parsed provider envelopes, HTTP status,
usage, finish reason, reasoning fields, logical and physical order, model and
provider receipts, all raw rules, recognized forms, candidate identities,
trial receipts, consequence receipts, case-manifest hash, witness ASTs and
evaluations, assignments, control authorship, functional vectors, atomic facts,
and the terminal summary.

The integrity report must recompute every retained request, response, manifest,
rule, witness, trial, consequence, and summary binding before interpretation.
Integrity failure makes the packet invalid and does not license repair or a
second contact.

## Stopping and redirect rule

This charter is consumed by its first participant-model request after the
disposable interface. The interface call itself may stop the packet but cannot
be rerun under this charter.

Complete the frozen schedule through wrong, copied, constant, prose, fenced,
out-of-scope, unavailable, or inconvenient behavior unless the physical ceiling
or provider stop prevents it. Do not change prompts, cases, vocabulary, oracle,
witnesses, model, settings, order, parser, evaluator, controls, or report after
contact begins.

After one packet, close the charter. A messy, null, confirming, malformed,
unavailable, or control-reproduced result is complete. No outcome licenses
prompt repair, a new DSL, more cases, resampling, model substitution, another
charter, influence testing, validation, or a Formation claim.

## Work licensed by this charter

The two stable reviews license only a separate implementation decision. They do
not license implementation, a runner, or participant-model contact by
themselves.

## Review question

Independent reviewers must try to show that the case packet leaks its oracle,
the witness proof is vacuous, the initial or primary events teach the full rule,
the controls change several causes at once, raw strings stop being executable,
same-response matching is overread, the call arithmetic is wrong, a condition
has fewer than two assigned units, unavailable worlds disappear from the
denominator, or the charter silently licenses a success claim.

They must also check exact model identity, settings, prompts, material fields,
oracle independence, acquisition continuation, later-cycle mirroring, retry
semantics, and the boundary before implementation.

## Review record

The review question above was asked in three read-only Cursor rounds using the
exact model identifiers `composer-2.5` and `cursor-grok-4.6-high-fast`.

Both reviewers first returned `REVISE_CHARTER`. They found that the system and
control prompts still had placeholders whose exact substitutions were not
owned, several runtime status values and later-cycle materials were only
described in prose, the same-response and static requests were not byte-frozen,
and the leakage witness had no deterministic serialization or preflight hash.

The repaired text froze the prompt renderer, all material shapes, the later
cycle, the case manifest, the 36 witness pairs, the static rules, comparison
slots, and retry-token contingency. Both reviewers again returned
`REVISE_CHARTER`. Composer found that model invocation and proposal coordinates
were not predeclared. Grok found that calls 30 and 35 did not bind J8/K8 or the
unavailable-parent path exactly.

The final text assigns `iv01` through `iv35`, derives unique output coordinates,
keeps parent references backward-only, and makes the later ordinary and
same-response paths total when call 08 or 17 has no string content. Both
reviewers independently reconstructed the case-manifest and witness hashes,
checked all request classes, denominators, and budgets, and found no remaining
blocker.

Final verdicts:

- `composer-2.5`: `CHARTER_STABLE`
- `cursor-grok-4.6-high-fast`: `CHARTER_STABLE`
