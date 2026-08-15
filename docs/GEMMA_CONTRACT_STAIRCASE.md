# Small-model structured-action staircase

Status: **contact complete; both models validly stopped
`contract_unreliable` at task 1**.

## Purpose

Find out whether either of two much smaller instruction models can reliably
return a basic computed action before the project authors another full
admission packet.

The earlier admission runs spent their first call on Python source. Ministral
3B added a prohibited Markdown fence. Nemotron 4B later spent most of its fixed
completion budget on internal reasoning and returned incomplete source. Those
are useful stops, but they leave a simpler question unanswered: can a model at
the small end read supplied state, compute a result, and return one exact
machine-readable value?

This screen asks only that question. It does not test a teachable gap,
persistence, transfer, or Formation. Passing all four tasks licenses a new full
admission charter with fresh development material. Failing closes only this
model and inference setup.

## Why these two models

Use two instruction-tuned Gemma 3 models in increasing size:

1. Gemma 3 270M Instruct QAT Q4_0;
2. Gemma 3 1B Instruct QAT Q4_0.

Both are published in the [LM Studio Gemma 3
catalog](https://lmstudio.ai/models/gemma-3). The 270M model is the deliberately
small end rather than a likely winner selected after seeing these tasks. Its
[official model card](https://huggingface.co/google/gemma-3-270m-it) identifies
it as instruction-tuned and reports instruction-following evaluation, so it is
not an untuned base-model strawman.

The shared family, QAT method, quantization name, chat template, runtime, and
inference settings reduce irrelevant variation. The two checkpoints still have
different weights and training histories, so their results cannot establish a
causal scaling law.

No third model may be added after contact. A later screen may name another
family only after both results close.

## Exact local artifacts

```text
google/gemma-3-270m@q4_0
file: lmstudio-community/gemma-3-270m-it-qat-GGUF/gemma-3-270m-it-qat-Q4_0.gguf
GGUF bytes: 241410208
GGUF SHA-256: 5f4b2e17722e510122c464573b880587f4983347a40e5472b858d5a3c1ab8095
embedded chat-template characters: 1532
embedded chat-template SHA-256: 7de1c58e208eda46e9c7f86397df37ec49883aeece39fb961e0a6b24088dd3c4

google/gemma-3-1b@q4_0
file: lmstudio-community/gemma-3-1B-it-QAT-GGUF/gemma-3-1B-it-QAT-Q4_0.gguf
GGUF bytes: 720425472
GGUF SHA-256: b25d35b00fe699ef52bf399fa579f2c56664897c013aeba2686965fdb6265f0f
embedded chat-template characters: 1532
embedded chat-template SHA-256: 7de1c58e208eda46e9c7f86397df37ec49883aeece39fb961e0a6b24088dd3c4
```

The runner must recompute the file size, file digest, template length, and
template digest before loading either model. Any mismatch refuses contact.

## Inference contract

Load one model at a time in LM Studio with an 8,192-token context, maximum GPU
offload, parallelism one, no vision attachment, and no speculative decoding.
Unload every model before the next load and after the packet.

Use these exact load commands and live identifiers:

```text
lms load google/gemma-3-270m --gpu max --context-length 8192 --parallel 1 --no-speculative-draft-mtp --identifier formation-gemma-screen-270m -y
lms load google/gemma-3-1b --gpu max --context-length 8192 --parallel 1 --no-speculative-draft-mtp --identifier formation-gemma-screen-1b -y
```

After each load, `lms ps --json` must contain exactly one live instance. Its
identifier must be the named identifier, its selected variant must be the
matching `google/gemma-3-270m@q4_0` or `google/gemma-3-1b@q4_0`, its context
length must be 8,192, its parallel value must be one, and vision must be false.
No projector, adapter, draft model, speculative decoder, or tool may attach.
Any mismatch refuses contact rather than selecting another local variant.

Every logical call uses the local OpenAI-compatible `/v1/chat/completions`
endpoint and names the matching live identifier in `model`. It sends one user
message with no authored system message, tools, history, or prior response
identifier. The verified embedded template is part of the artifact. Any system
text it inserts is artifact behavior; the harness may not add or alter it.
Send exactly these sampling fields:

```json
{
  "frequency_penalty": 0,
  "max_tokens": 256,
  "presence_penalty": 0,
  "repeat_penalty": 1,
  "seed": "<the task seed>",
  "stream": false,
  "temperature": 0.2,
  "top_k": 40,
  "top_p": 0.95
}
```

Do not send a reasoning control, stop string, response schema, or other
optional inference field. Each prompt tells the model about the complete
256-token response limit. If the server rejects a listed field or requires an
additional inference choice, refuse contact and amend this pre-contact packet
rather than falling back to a default.

Only `choices[0].message.content` is the scored model output. The runner retains
the complete response envelope, including `reasoning_content` or any similar
provider field, but never concatenates, extracts, or scores those fields. A
missing `choices[0].message` or a content value of any type other than `str` or
`null` aborts the packet as `provider_envelope_invalid`; it is not a participant
failure.

A logical call may retry once only when `message.content` is `null` or the exact
empty string. Retain both attempts and link the second to the first. Whitespace
is nonempty model content: it does not retry and later refuses as
`empty_output`. A second `null` or exact empty string receives
`gate_fail:empty_output`. Truncated, fenced, malformed, or incorrect nonempty
content does not retry.

## Exact JSON gate

First reject raw model content containing the three-byte Markdown-fence marker.
Then apply `str.strip()`. Refuse an empty result. Decode the complete trimmed
content with Python `json.loads` and an `object_pairs_hook` that refuses every
duplicate object key. `NaN`, `Infinity`, and `-Infinity` refuse through a
`parse_constant` callback. Trailing or leading prose therefore refuses.

The decoded top level must have exact Python type `dict` and exactly one key,
`answer`. Compare the value under `answer` with the task oracle recursively:

- the exact Python type must match at every node, so `true` never substitutes
  for `1`;
- lists must have the same length and compare in order;
- dictionaries must have the same key set and recursively equal values; and
- strings, integers, booleans, and `null` compare by exact type and value.

Object-key order and insignificant JSON whitespace do not affect the verdict.
No repair, fence removal, substring extraction, or human interpretation is
allowed.

Every call receives exactly one label:

- `full_pass` — the gate accepts and `answer` equals the exact oracle;
- `wrong_answer` — the gate accepts but the exact answer differs; or
- `gate_fail` — extraction or complete evaluation refuses.

The gate report uses one stable refusal code:

- `markdown_fence` for a raw fence marker;
- `empty_output` after stripping, including a second empty-content attempt;
- `duplicate_key` for any repeated object key at any depth;
- `nonfinite_constant` for `NaN`, `Infinity`, or `-Infinity`;
- `invalid_json` for every other JSON decode failure; or
- `exact_object_required` when the decoded top level is not an exact `dict`
  with the single key `answer`.

An accepted object with a different exact answer has no gate refusal and is
`wrong_answer`.

## Task 1: selection

Seed: `3001`.

```text
Compute the requested result from this JSON input:
{"records":[{"label":"cove","kept":false},{"label":"brim","kept":true},{"label":"dawn","kept":true}]}

Return the labels whose kept value is true, sorted alphabetically.
Return exactly one JSON object with the single key "answer". Its value must be a JSON array of strings. Return no prose or Markdown fence.
Your complete response has a limit of 256 tokens.
```

Oracle:

```json
{"answer":["brim","dawn"]}
```

## Task 2: grouped totals

Seed: `3002`.

```text
Compute the requested result from this JSON input:
{"entries":[{"zone":"west","count":4},{"zone":"east","count":3},{"zone":"west","count":-1},{"zone":"east","count":5}]}

Sum count for each zone. Return one [zone,total] pair per zone, sorted alphabetically by zone.
Return exactly one JSON object with the single key "answer". Its value must be a JSON array of two-item arrays. Return no prose or Markdown fence.
Your complete response has a limit of 256 tokens.
```

Oracle:

```json
{"answer":[["east",8],["west",3]]}
```

## Task 3: ordered updates

Seed: `3003`.

```text
Compute the requested result from this JSON input:
{"start":12,"changes":[4,-7,3,-2]}

Starting at start, apply each change from left to right. Return the final integer.
Return exactly one JSON object with the single key "answer". Return no prose or Markdown fence.
Your complete response has a limit of 256 tokens.
```

Oracle:

```json
{"answer":10}
```

## Task 4: conjunctive filter

Seed: `3004`.

```text
Compute the requested result from this JSON input:
{"items":[{"id":"p","kind":"task","ready":true,"score":1},{"id":"q","kind":"note","ready":true,"score":4},{"id":"r","kind":"task","ready":false,"score":5},{"id":"s","kind":"task","ready":true,"score":3}]}

Return ids of items whose kind is exactly "task", whose ready value is true, and whose score is at least 2. Sort ids alphabetically.
Return exactly one JSON object with the single key "answer". Its value must be a JSON array of strings. Return no prose or Markdown fence.
Your complete response has a limit of 256 tokens.
```

Oracle:

```json
{"answer":["s"]}
```

## Order and stop

Run the 270M model first, then the 1B model. For each model, run tasks 1 through
4 in order. Stop that model after its first result other than `full_pass`, but
still screen the other model. The maximum is eight logical calls plus permitted
empty-content retries.

A model's terminal result is:

- `screen_pass` if all four calls are `full_pass`; or
- `contract_unreliable` at its first `wrong_answer` or `gate_fail`.

There is no partial credit and no cross-model majority. If both pass, prefer
270M for the next admission charter. If only one passes, only that model may
advance. If neither passes, close this staircase and choose a separately
chartered model or inference setup.

## Records and claim boundary

Each attempt record contains exactly these semantic fields, with storage paths
and JSON formatting left to the runner:

```text
logical_index
attempt_index
call_id
seed
model_key
live_identifier
prompt_sha256
output_sha256
request_envelope
response_envelope
started_at
ended_at
elapsed_seconds
retry_reason: null | "no_model_content"
retry_of_attempt: null | 1
gate_refusal: null | one frozen refusal code
decoded_answer: JSON value | null
oracle_answer: JSON value
call_label: "full_pass" | "wrong_answer" | "gate_fail" | "retry_pending"
packet_receipt
```

Store the exact prompt and output bytes in separate files. `prompt_sha256` and
`output_sha256` bind those files. A first empty attempt is `retry_pending` and
has no fabricated gate report; only the final attempt receives the logical
call's gate report and label.

The packet receipt stored with every attempt contains the exact model
configuration; artifact path, byte count, digest, template length, and template
digest; LM Studio CLI version; runtime inventory; server-start command, exit
status, stdout, and stderr; load command, exit status, stdout, stderr, and the
complete validated live instance; the complete sampling JSON without seed; and
explicit booleans for text-only operation, projector absence, adapter absence,
speculative-decoding absence, tool absence, and history absence.

The model summary contains its ordered logical-call reports, stopping call,
and terminal result. The packet summary contains both model summaries in
contact order and the artifact verification records. A stopped or skipped call
produces no synthetic prompt, output, attempt, or call receipt.

A pass means only that this exact local model and setup completed four basic
structured computations. It is not admission to a developmental band. The
screen contains no cold gap and no directly taught repair. All contacted tasks
become blocked development material and may not score a later claim.

The screen loses its value if a model is added after contact, an output is
repaired, the token limit or settings change between models, a failed model
continues, a passing screen is called Formation, or any of these four tasks is
reused in a promoted packet.

Independent cold review returned `STAIRCASE_PROTOCOL_STABLE`. The runner then
passed nine fake-contact tests and independent review returned
`RUNNER_LICENSED`. In contact, both models returned Markdown fences at task 1.
The 270M model returned Python instead of JSON. The 1B model returned a JSON
array with the wrong shape and omitted one required label. Both immediate
`contract_unreliable` stops passed independent audit as `EVIDENCE_VALID`.
