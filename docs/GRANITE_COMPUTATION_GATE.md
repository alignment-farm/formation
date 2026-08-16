# Granite computation gate

Status: **cold-reviewed pre-contact protocol; runner and model contact not yet
licensed**.

## Decision

Test Granite 4.0 H Tiny as the next candidate, before any larger local model.
It is the smallest untested text-only checkpoint already present on this
machine. Its 7B total parameters use 1B active parameters per token. The choice
does not claim that architecture or size predicts success.

The prior Gemma trial settled the immediate interface question: a JSON grammar
removed fences but did not repair computation. This gate therefore uses the
grammar as a fixed action surface and asks only whether Granite can perform
four basic computations reliably enough to justify a full admission charter.

This is candidate selection, not admission and not Formation. A pass earns a
new prospective admission charter. A failure closes this exact Granite setup
and returns selection to the remaining candidates.

## Blocked ancestry

All prompts, inputs, answers, outputs, and oracles from earlier contacts are
blocked development material. This gate uses four fresh tasks. Its contacted
material may not later score admission, transfer, or Formation.

The structured-output interface trial supplies only the already-tested request
mechanism, exact JSON gate, provider-content boundary, retry rule, abort
taxonomy, and receipt discipline. None of its task material is reused.

## Exact model and runtime

Use only this local artifact:

```text
model key: ibm/granite-4-h-tiny
selected variant: ibm/granite-4-h-tiny@q4_k_m
live identifier: formation-granite-computation-gate
artifact path: ~/.lmstudio/models/lmstudio-community/granite-4.0-h-tiny-GGUF/granite-4.0-h-tiny-Q4_K_M.gguf
artifact bytes: 4230975936
artifact SHA-256: 064bea0136420b38d0b65697fa5e772e28b112eee1757aacc7f64eba6bf37810
embedded chat-template characters: 6099
embedded chat-template SHA-256: fed2756d2d24e127b951dcf139d0b03ab7db8ef23a456128ebc9c2db4901d476
```

Before contact, recompute all four artifact bindings. Refuse on any mismatch.
Unload all models, then use exactly this command:

```text
lms load ibm/granite-4-h-tiny --gpu max --context-length 8192 --parallel 1 --no-speculative-draft-mtp --identifier formation-granite-computation-gate -y
```

Read `lms ps --json` and require a one-item array whose item has the exact
identifier and selected variant above, `contextLength: 8192`, `parallel: 1`,
and `vision: false`. Refuse any other live item or value. No projector, adapter,
tools, history, or authored system message may be present. Unload all models
after the packet, including on failure.

Every request uses `/v1/chat/completions`, one user message, and these exact
common fields:

```json
{
  "frequency_penalty": 0,
  "max_tokens": 256,
  "presence_penalty": 0,
  "repeat_penalty": 1,
  "stream": false,
  "temperature": 0.2,
  "top_k": 40,
  "top_p": 0.95
}
```

Add the task's exact seed and `response_format`. Do not send stop strings or
other optional inference fields. If the server rejects a frozen field, requires
another inference choice, or cannot preserve the exact schema, refuse contact
before the first call or abort `request_contract_rejected` afterward.

Every request sets `model` to the exact live identifier
`formation-granite-computation-gate` and `messages` to exactly one object with
`role: "user"` and the task's literal prompt as `content`.

Only `choices[0].message.content` is scored. Retain but never score reasoning,
tool, or schema metadata. A missing choice/message/content or non-string,
non-null content aborts `provider_envelope_invalid`.

## Task 1: filtered ordering

Task ID: `filtered_ordering`. Seed: `5001`.

Exact prompt:

```text
Compute the requested result from this JSON input:
{"jobs":[{"id":"maple","ready":true,"priority":3},{"id":"cedar","ready":false,"priority":9},{"id":"ash","ready":true,"priority":5},{"id":"birch","ready":true,"priority":1}]}

Return the ids of jobs whose ready value is true and whose priority is at least 3. Sort by priority from highest to lowest, breaking ties alphabetically by id.
Return exactly one JSON object with the single key "answer". Its value must be a JSON array of strings. Return no prose or Markdown fence.
Your complete response has a limit of 256 tokens.
```

Bare oracle value:

```json
["ash","maple"]
```

Exact `response_format`:

```json
{
  "type": "json_schema",
  "json_schema": {
    "name": "filtered_ordering_answer",
    "strict": true,
    "schema": {
      "type": "object",
      "properties": {"answer": {"type": "array", "items": {"type": "string"}}},
      "required": ["answer"],
      "additionalProperties": false
    }
  }
}
```

## Task 2: ordered operations

Task ID: `ordered_operations`. Seed: `5002`.

Exact prompt:

```text
Compute the requested result from this JSON input:
{"start":9,"operations":[{"kind":"add","value":5},{"kind":"triple"},{"kind":"subtract","value":8},{"kind":"halve"}]}

Begin with start. Apply the operations from left to right. Add increases the current value, triple multiplies it by 3, subtract removes value, and halve divides the current value by 2. All intermediate and final values in this input are integers. Return the final integer.
Return exactly one JSON object with the single key "answer". Return no prose or Markdown fence.
Your complete response has a limit of 256 tokens.
```

Bare oracle value:

```json
17
```

Exact `response_format`:

```json
{
  "type": "json_schema",
  "json_schema": {
    "name": "ordered_operations_answer",
    "strict": true,
    "schema": {
      "type": "object",
      "properties": {"answer": {"type": "integer"}},
      "required": ["answer"],
      "additionalProperties": false
    }
  }
}
```

## Task 3: latest enabled revisions

Task ID: `latest_enabled_revisions`. Seed: `5003`.

Exact prompt:

```text
Compute the requested result from this JSON input:
{"records":[{"name":"iris","revision":1,"enabled":true},{"name":"oak","revision":2,"enabled":true},{"name":"iris","revision":3,"enabled":false},{"name":"pine","revision":1,"enabled":true},{"name":"oak","revision":4,"enabled":true},{"name":"pine","revision":2,"enabled":false}]}

For each name, select only its record with the greatest revision. Keep the name only when that selected record has enabled equal to true. Return the kept names sorted alphabetically.
Return exactly one JSON object with the single key "answer". Its value must be a JSON array of strings. Return no prose or Markdown fence.
Your complete response has a limit of 256 tokens.
```

Bare oracle value:

```json
["oak"]
```

Exact `response_format`:

```json
{
  "type": "json_schema",
  "json_schema": {
    "name": "latest_enabled_revisions_answer",
    "strict": true,
    "schema": {
      "type": "object",
      "properties": {"answer": {"type": "array", "items": {"type": "string"}}},
      "required": ["answer"],
      "additionalProperties": false
    }
  }
}
```

## Task 4: dependency reachability

Task ID: `dependency_reachability`. Seed: `5004`.

Exact prompt:

```text
Compute the requested result from this JSON input:
{"start":["forge"],"dependencies":{"forge":["kiln","mold"],"kiln":["fuel"],"mold":["clay","fuel"],"fuel":[],"clay":[],"unused":["sand"],"sand":[]}}

Starting from every name in start, repeatedly follow dependencies. Return every reachable dependency, but do not include the starting names. Include each name once and sort the result alphabetically. Do not follow entries that are not reachable from start.
Return exactly one JSON object with the single key "answer". Its value must be a JSON array of strings. Return no prose or Markdown fence.
Your complete response has a limit of 256 tokens.
```

Bare oracle value:

```json
["clay","fuel","kiln","mold"]
```

Exact `response_format`:

```json
{
  "type": "json_schema",
  "json_schema": {
    "name": "dependency_reachability_answer",
    "strict": true,
    "schema": {
      "type": "object",
      "properties": {"answer": {"type": "array", "items": {"type": "string"}}},
      "required": ["answer"],
      "additionalProperties": false
    }
  }
}
```

## Scoring, order, and stop

Run the tasks once each in numbered order. There are exactly four logical
calls. Every call is cold: no earlier prompt or output enters a later request.
Run all four even after a wrong or invalid answer because the candidate profile
is the object of this gate. There is no repair prompt.

Use the structured-output trial's exact raw-fence, strip, duplicate-key,
nonfinite-number, JSON-decode, exact-object, and recursive exact-type rules.
Store the bare value under both `decoded_answer` and `oracle_answer` when the
object is accepted. Classify each call as `invalid`, `valid_wrong`, or
`valid_correct` using the same fixed mapping.

Retry once only when visible content is null or the exact empty string. Retain
both attempts. Whitespace, malformed JSON, fences, truncation, and wrong values
do not retry. A second empty attempt is terminal `invalid` with
`empty_output`.

The candidate result is:

- `gate_pass` only if all four calls are `valid_correct`;
- `computation_unreliable` otherwise.

This all-four rule is deliberately strict because these are basic anchors, not
the narrow headroom cases of a full admission packet.

## Records, aborts, and claim boundary

Retain the structured-output trial's attempt fields and packet receipt, with
one condition value: `constrained`. Store the exact prompt and output bytes in
separate hash-bound files. The model summary contains all four call reports and
these exact terminal fields:

```text
packet_status: "complete" | "aborted"
abort_reason: null | "provider_envelope_invalid" | "request_contract_rejected" | "infrastructure_invalid"
candidate_result: "gate_pass" | "computation_unreliable" | null
```

On normal completion, set `packet_status` to `complete`, `abort_reason` to null,
and `candidate_result` from the all-four rule. On abort, set `packet_status` to
`aborted`, set the applicable non-null reason, and set `candidate_result` to
null.

Before the first call, artifact, runtime, load, request-contract, or provider
incompatibility refuses contact. After contact begins, retain completed and
rejected attempts, set packet status `aborted`, emit no candidate result, and
use exactly one applicable reason:

```text
provider_envelope_invalid
request_contract_rejected
infrastructure_invalid
```

This gate may conclude only whether this exact Granite artifact and setup
returned four correct machine-readable actions. It cannot establish general
reasoning ability, teachable headroom, acquired competence, admission, or a
Formation effect.

The gate loses its value if prior task material is reused, a schema encodes an
answer, an output is repaired, calls share history, a failure silently changes
the inference setup, or anything short of four exact answers is called a pass.

No call is licensed until independent cold review returns one stable protocol
and an independently reviewed fake-tested runner is licensed.

Independent cold review returned `GRANITE_GATE_STABLE`. Runner implementation
and its separate license remain pending.
