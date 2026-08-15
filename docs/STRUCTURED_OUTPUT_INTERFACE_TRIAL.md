# Paired structured-output interface trial

Status: **cold-reviewed pre-contact protocol; runner licensed; model contact
not yet run**.

## Purpose

Separate two questions that the small-model screens have mixed together:

1. Can the model return a value with the required JSON structure?
2. Is the value computationally correct?

The preceding Gemma screen stopped both models on Markdown fences. The 1B
payload was also wrong after mentally removing the fence: it omitted one record
and lacked the required object. A JSON grammar could prevent the fence and
shape errors, but it cannot decide which records belong in the answer.

This trial changes only the response interface. Each pair uses the same exact
model, prompt, task, seed, sampling fields, and cold-call boundary. The bare
call has no response constraint. The paired call adds one JSON Schema through
LM Studio's `response_format` request field. No output from either call enters
the other.

This is an inference-interface trial, not model admission and not Formation.
Its two tasks are too few to establish a general capability claim.

## Authority and ancestry

The exact model artifacts, template checks, live load requirements, provider-
content boundary, empty-content retry, receipt fields, and cleanup rules from
the completed [Gemma staircase](GEMMA_CONTRACT_STAIRCASE.md) apply unchanged
unless this document replaces them explicitly.

All prior prompts, inputs, outputs, and oracles remain blocked development
material. This trial uses new inputs and answers. Its own contacted material
may not score a later admission or Formation claim.

## Models and inference

Use the same two exact local artifacts in this order:

```text
google/gemma-3-270m@q4_0
GGUF bytes: 241410208
GGUF SHA-256: 5f4b2e17722e510122c464573b880587f4983347a40e5472b858d5a3c1ab8095
embedded chat-template characters: 1532
embedded chat-template SHA-256: 7de1c58e208eda46e9c7f86397df37ec49883aeece39fb961e0a6b24088dd3c4

google/gemma-3-1b@q4_0
GGUF bytes: 720425472
GGUF SHA-256: b25d35b00fe699ef52bf399fa579f2c56664897c013aeba2686965fdb6265f0f
embedded chat-template characters: 1532
embedded chat-template SHA-256: 7de1c58e208eda46e9c7f86397df37ec49883aeece39fb961e0a6b24088dd3c4
```

Use the staircase's exact file paths, load commands, live identifiers, 8,192-
token context, maximum GPU offload, parallelism one, text-only check, and
attachment refusals. Recompute both artifact and template bindings before
contact. Unload before and after every model. Reuse of the screen-named live
identifiers `formation-gemma-screen-270m` and `formation-gemma-screen-1b` is
intentional; each is only a local runtime identifier and is recorded with this
trial's distinct packet.

Both conditions use exactly these common sampling fields:

```json
{
  "frequency_penalty": 0,
  "max_tokens": 256,
  "presence_penalty": 0,
  "repeat_penalty": 1,
  "seed": "<4001 or 4002>",
  "stream": false,
  "temperature": 0.2,
  "top_k": 40,
  "top_p": 0.95
}
```

Do not send a stop string or any other optional inference field. The sole
condition-dependent exception is the frozen constrained `response_format`.
If LM Studio rejects any listed common field, requires an additional inference
choice, or cannot preserve this exact difference between conditions, refuse
contact and amend this protocol if no logical call has begun. If discovered
after contact begins, follow the request-contract abort rule below. Never
silently omit, substitute, or add a field.

Every request uses `/v1/chat/completions`, one user message, no authored system
message, no history, no tools, and no reasoning control. Only
`choices[0].message.content` is scored. Retain but never score provider
reasoning fields. This visible content is the declared action surface for both
conditions. JSON duplicated into reasoning, schema metadata, a tool field, or
any other provider field does not make an empty `content` successful and does
not change the frozen empty-content retry rule.

## The one changed request field

The `bare` request omits `response_format` entirely.

The `constrained` request adds exactly one task-specific object under
`response_format`. No other field changes. LM Studio documents this field as
grammar-based sampling for GGUF models. The schema constrains JSON structure
and primitive types only. It contains no allowed-answer enumeration, model
output, task oracle, item count, string pattern, numeric range, or other answer
hint.

Before sending either member and again from the stored request envelopes,
assert mechanically that removing `response_format` from the constrained
request makes its complete JSON value exact-type equal to the bare request;
that the bare top-level object has no `response_format` key; and that the
constrained value equals the frozen task schema. A failed assertion refuses
contact before the first call or becomes `request_contract_rejected` after
contact has begun, including when the post-storage assertion discovers drift
after one member ran. That completed member remains retained but cannot enter a
pair because the packet aborts without the other verified member.

If the server rejects either schema or changes the response endpoint contract,
refuse contact and amend this document if no logical call has begun. If
discovered after contact begins, follow the request-contract abort rule below.
Do not fall back to JSON mode, a tool call, prompt repair, or a different
schema.

## Task A: conjunctive selection

Task ID: `selection`.

Seed: `4001`.

Exact prompt for both conditions:

```text
Compute the requested result from this JSON input:
{"records":[{"tag":"alder","open":true,"rank":2},{"tag":"birch","open":false,"rank":8},{"tag":"clover","open":true,"rank":5},{"tag":"drift","open":true,"rank":1}]}

Return tags of records whose open value is true and whose rank is at least 2. Sort the tags alphabetically.
Return exactly one JSON object with the single key "answer". Its value must be a JSON array of strings. Return no prose or Markdown fence.
Your complete response has a limit of 256 tokens.
```

Oracle answer:

```json
["alder","clover"]
```

The scorer compares the value under `answer` with this bare oracle value. The
attempt record stores that same bare value under `oracle_answer`; it does not
wrap the oracle in another object.

Exact constrained `response_format`:

```json
{
  "type": "json_schema",
  "json_schema": {
    "name": "selection_answer",
    "strict": true,
    "schema": {
      "type": "object",
      "properties": {
        "answer": {
          "type": "array",
          "items": {"type": "string"}
        }
      },
      "required": ["answer"],
      "additionalProperties": false
    }
  }
}
```

## Task B: ordered state update

Task ID: `ordered_update`.

Seed: `4002`.

Exact prompt for both conditions:

```text
Compute the requested result from this JSON input:
{"start":17,"operations":[{"kind":"subtract","value":4},{"kind":"double"},{"kind":"add","value":3}]}

Begin with start. Apply the operations from left to right: subtract removes value, double multiplies the current result by 2, and add increases it by value. Return the final integer.
Return exactly one JSON object with the single key "answer". Return no prose or Markdown fence.
Your complete response has a limit of 256 tokens.
```

Oracle answer:

```json
29
```

The scorer compares the value under `answer` with this bare oracle value. The
attempt record stores that same bare value under `oracle_answer`; it does not
wrap the oracle in another object.

Exact constrained `response_format`:

```json
{
  "type": "json_schema",
  "json_schema": {
    "name": "update_answer",
    "strict": true,
    "schema": {
      "type": "object",
      "properties": {
        "answer": {"type": "integer"}
      },
      "required": ["answer"],
      "additionalProperties": false
    }
  }
}
```

## Output scoring

Use the staircase's exact raw-fence, strip, duplicate-key, nonfinite-number,
JSON-decode, exact-object, and recursive exact-type rules. Both conditions use
the same external scorer. Do not trust schema compliance reported by the
provider without parsing the visible content again.

Each call receives one state:

- `invalid` — the JSON gate refuses;
- `valid_wrong` — the exact `{answer: ...}` structure passes but the answer is
  not exact-type equal to the oracle; or
- `valid_correct` — structure and exact answer both pass.

Store this value in a new `call_state` field. Retain the inherited `call_label`
field and derive it without discretion:

| Trial event | Inherited `call_label` | Trial `call_state` |
| --- | --- | --- |
| first empty attempt, retry still owed | `retry_pending` | null |
| accepted structure and exact oracle answer | `full_pass` | `valid_correct` |
| accepted structure and non-oracle answer | `wrong_answer` | `valid_wrong` |
| any terminal JSON-gate refusal, including second empty | `gate_fail` | `invalid` |

The pair classifier uses `call_state`, never `call_label`. A provider-envelope
failure has neither terminal field because it aborts the packet rather than
becoming a model result.

For a terminal accepted JSON object, `decoded_answer` stores only the bare
value under its `answer` key. For a gate refusal it is null. Thus
`decoded_answer` and `oracle_answer` have the same frozen shape and can be
compared directly with the exact-type rule.

Retain the ordinary gate refusal code as well. `finish_reason`, provider schema
metadata, and reasoning text never override the visible-content verdict.

For each model and task, classify the ordered `(bare, constrained)` pair:

| Bare state | Constrained state | Pair label |
| --- | --- | --- |
| `invalid` | `valid_correct` | `invalid_to_correct` |
| `invalid` | `valid_wrong` | `invalid_to_wrong` |
| `invalid` | `invalid` | `invalid_to_invalid` |
| `valid_wrong` | `valid_correct` | `wrong_to_correct` |
| `valid_wrong` | `valid_wrong` | `wrong_to_wrong` |
| `valid_wrong` | `invalid` | `wrong_to_invalid` |
| `valid_correct` | `valid_correct` | `correct_to_correct` |
| `valid_correct` | `valid_wrong` | `correct_to_wrong` |
| `valid_correct` | `invalid` | `correct_to_invalid` |

These labels describe observed paired outputs. `invalid_to_correct` means only
that the constrained call produced a usable correct action where the bare call
did not under this frozen but order-unbalanced schedule. It is not a schedule-
controlled interface effect, evidence that the model learned, or evidence that
formatting was the bare call's only error. Never pool the models to cancel
their different schedules.

## Order, retries, and stopping

There are exactly eight logical calls. All run even after an invalid or wrong
answer because each pair is the object of the trial.

Gemma 270M:

```text
01 Task A bare seed 4001
02 Task A constrained seed 4001
03 Task B bare seed 4002
04 Task B constrained seed 4002
```

Gemma 1B reverses condition order within each task to expose gross scheduling
dependence while retaining `(bare, constrained)` classification order:

```text
01 Task A constrained seed 4001
02 Task A bare seed 4001
03 Task B constrained seed 4002
04 Task B bare seed 4002
```

Assemble each pair by exact `(model_key, task_id)` equality and select its
members by the `condition` field. The only permitted model keys are
`google/gemma-3-270m` and `google/gemma-3-1b`; the only task IDs are
`selection` and `ordered_update`; and the only conditions are `bare` and
`constrained`. Never infer a pair from chronological adjacency or
`logical_index`. The pair record always writes bare state first and constrained
state second, regardless of contact order.

Every call is cold and independent. Reversing order does not remove all order
effects, and the report must not pool the two model results as if it did.

There is exactly one logical call for each permitted `(model_key, task_id,
condition)` triple and exactly one terminal attempt for that call after any
permitted empty retry. A duplicate logical call or second terminal attempt
refuses contact before the packet begins or becomes
`request_contract_rejected` after it begins.

The staircase's exact empty-content rule applies: retry once only for `null` or
the exact empty string. A first empty attempt is `retry_pending`; a second is an
`invalid` call with `empty_output`. Nonempty malformed or truncated content
does not retry. A provider-envelope failure aborts the packet rather than
becoming a model result.

## Records and bounded conclusion

Retain the staircase's exact attempt and packet receipt fields, with the
following explicit nullable extension for aborting exchanges. Add `task_id`,
`condition`, `call_state`, and the exact `response_format` value or null to
every attempt record. `call_state` is null on `retry_pending` and aborting
attempts; otherwise it is one of the three terminal trial states. `call_label`
is null only on an aborting attempt; otherwise it retains its inherited enum.
On either abort reason, `gate_refusal`, `decoded_answer`, `call_label`, and
`call_state` are all null, while `oracle_answer` retains the task's frozen bare
oracle value. This nullable abort rule replaces the inherited non-null
`call_label` enum only for the rejected exchange. For `bare`,
`response_format` is null in the record and
absent from the stored request envelope. For `constrained`, both locations
contain the task's exact frozen object. A retry repeats the same `task_id` and
`condition`; only the terminal attempt supplies the pair member's
`call_state`. Retain the request and response of every HTTP attempt, including
inconvenient outputs: eight logical calls when complete, plus every permitted
empty-content retry.

Each completed pair record contains exactly these semantic fields:

```text
model_key
task_id
bare_call_id
bare_call_state
constrained_call_id
constrained_call_state
pair_label
```

The packet summary contains `pairs`. On completion it contains exactly four
pair records in this order: 270M `selection`, 270M `ordered_update`, 1B
`selection`, 1B `ordered_update`. On abort it is the ordered subset of those
four whose two members already have terminal states; it contains no null hole
or incomplete pair. The summary also contains `trial_status`, which is
`complete` only after all eight logical calls have terminal attempts.

The packet summary retains the staircase's artifact-verification records and
two model summaries. Each model summary contains all chronological
logical-call reports actually attempted and its completed pair records. Add
the packet-level `pairs` and `trial_status` fields specified above.

If a provider-envelope failure aborts the packet, retain every attempt and any
pair record completed before the failure, set `trial_status` to `aborted`, set
`abort_reason` to the exact token `provider_envelope_invalid`, and do not emit a
trial conclusion. On completion, set `abort_reason` to null. Omit any pair
lacking both terminal member states. No completed pair is rewritten or treated
as the trial result after an abort.

If a schema or common request field is rejected, or an additional inference
choice becomes necessary after any logical call has begun, apply the same
retention and no-conclusion rules but set `abort_reason` to the exact token
`request_contract_rejected`. The rejected HTTP exchange is retained as an
attempt with its raw request and response under the shared nullable abort shape
above, and it receives no pair membership.

If an inherited artifact, template, load, live-inventory, unload, or other
runtime verification fails after the first logical call has begun, apply the
same retention and no-conclusion rules and set `abort_reason` to the exact
token `infrastructure_invalid`. Before the first call, the same failure refuses
contact and produces no evidence packet. The only abort-reason tokens are
`provider_envelope_invalid`, `request_contract_rejected`, and
`infrastructure_invalid`.

This trial may conclude only which state transition occurred for each of four
model-task pairs. With two tasks, it cannot establish a general benefit from
structured output, choose a developmental model, or show a Formation effect.

The trial loses its value if the schema constrains an answer rather than its
shape, if bare and constrained prompts or seeds differ, if output crosses
between calls, if a failed call stops its pair, if the scorer trusts provider
metadata instead of visible content, or if a pair transition is described as
learning.

Independent cold review returned `INTERFACE_PROTOCOL_STABLE`. The separate
runner passed 13 fake-contact tests and the combined 239-test suite. Independent
runner review returned `RUNNER_LICENSED`; the eight logical calls are licensed.
