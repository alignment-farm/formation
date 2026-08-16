# Qwen computation gate

Status: **cold-reviewed pre-contact protocol; runner licensed; model contact
not yet run**.

## Decision and ancestry

Test the installed Qwen 3.5 9B MLX checkpoint next. It is a moderate dense-model
step above the closed small and 1B-active candidates and below Bonsai 27B. This
ordering is a resource-conscious search choice, not a capability claim.

Reuse the four computation families fixed before Granite contact: filtered
ordering, ordered operations, latest-revision selection, and dependency
reachability. Use the fresh inputs and answers below. Granite's prompts,
answers, and outputs do not enter this packet and did not determine these task
families. This packet becomes blocked development material after contact.

The gate is candidate selection only. A 4/4 pass earns a prospective full
admission charter. Anything else closes this exact setup as
`computation_unreliable`. Neither result is admission or Formation.

## Exact MLX package and runtime

Model key: `qwen/qwen3.5-9b`.
Selected variant: `qwen/qwen3.5-9b@4bit`.
Live identifier: `formation-qwen-computation-gate`.
Package directory:
`~/.lmstudio/models/lmstudio-community/Qwen3.5-9B-MLX-4bit`.

Before contact, require exactly these package files and SHA-256 bindings:

```text
chat_template.jinja a4aee8afcf2e0711942cf848899be66016f8d14a889ff9ede07bca099c28f715
config.json a96942cb6a8a1d3f1d17514d81a1925d04362a6a3233b389d13012211baaa9f8
model-00001-of-00002.safetensors 973cc1efdedb4d327993fb9c27865f0bcfd9015897d5f0ca9ffb6cda6a0768e5
model-00002-of-00002.safetensors 597dae0ed72b60acc07382e8ea0cdb9509c54128e07b0eaa9cf4996373d5ca7d
model.safetensors.index.json dd023913fb87cfdae27fb11dcf695117c925833796ccac3c64117d6652d8ff1e
preprocessor_config.json 27225450ac9c6529872ee1924fcb0962ff5634834f817040f444118116f4e516
processor_config.json 45fc17c8dd2474af6b493b52483c26c0584b0082d368c480f9fa611e73070040
tokenizer.json 06b9509352d2af50381ab2247e083b80d32d5c0aba91c272ca9ff729b6a0e523
tokenizer_config.json fa71760892f5c601d345e626ebd602055825a50beed7ee160709c95fffa475f0
video_preprocessor_config.json 7768af27c1fafa9cc9011c1dc20067e03f8915e03b63504550e11d5066986d13
vocab.json ce99b4cb2983d118806ce0a8b777a35b093e2000a503ebde25853284c9dfa003
```

Also bind the two LM Studio hub-control files that select template behavior:

```text
~/.lmstudio/hub/models/qwen/qwen3.5-9b/model.yaml 41e997d0ab4ca5572918e33c1c5284c5a9c4032ce3affe40b33ad76d7706746b
~/.lmstudio/hub/models/qwen/qwen3.5-9b/manifest.json c19d54c5855a8c596dd6197f715ffff20fc06dead920fce8faba9353edc6c8d1
```

Require `model.yaml` to declare the `enableThinking` custom field with
`defaultValue: true` and the `setJinjaVariable` effect targeting
`enable_thinking`. Refuse any binding or semantic mismatch.

Refuse missing, additional, or mismatched regular files. Unload all models,
then use exactly:

```text
lms load qwen/qwen3.5-9b --gpu max --parallel 1 --no-speculative-draft-mtp --identifier formation-qwen-computation-gate -y
```

Run `lms ps --json` after loading. Do not request an 8,192-token context: pre-contact inspection found that this
MLX variant loads at its native 262,144 tokens despite that CLI option. Require
the complete parsed inventory to be a one-item array. Require that sole item to
have the exact identifier and variant, `format: "safetensors"`,
`contextLength: 262144`, `parallel: 1`, and `vision: true`.

This is a text-only use of a multimodal model, not a text-only model. Every
message `content` is one plain string. No image, video, audio, content-part
array, projector argument, adapter, tool, history, or authored system message
is permitted. Retain explicit receipt booleans for all of those absences.
Unload all models after the packet, including on failure.

## Common inference contract

Use `/v1/chat/completions`, one user message, no history, and exactly:

```json
{
  "frequency_penalty": 0,
  "max_tokens": 1024,
  "presence_penalty": 0,
  "repeat_penalty": 1,
  "stream": false,
  "temperature": 0.2,
  "top_k": 40,
  "top_p": 0.95
}
```

Add only the task seed and exact `response_format`. The request `model` is the
live identifier above. Do not add stop strings, reasoning controls, or other
optional fields. LM Studio documents MLX structured output as using Outlines.
If any frozen field or schema is rejected, refuse before contact or abort
`request_contract_rejected` afterward.

Score only string or null `choices[0].message.content`. Retain but never score
reasoning or provider metadata. Missing or wrongly typed provider content
aborts `provider_envelope_invalid`.

Every `messages` value is exactly a one-item array containing only
`{"role":"user","content":"<literal task prompt>"}`. The content value is a
plain string, not an array of multimodal parts.

The bound `chat_template.jinja` enables its thinking path when no
`enable_thinking: false` template argument is supplied. This gate deliberately
uses that package default and sends no reasoning-control field or template
argument. Retain any provider `reasoning`, `reasoning_content`, or equivalent
field, but never concatenate it with visible content or score it. Null or exact
empty visible content follows the ordinary one-retry rule even when a reasoning
field is nonempty. The 1,024-token completion limit is larger than Granite's
because this default may spend completion tokens on reasoning; it remains
fixed for every call and does not guarantee that truncation cannot occur.
Outlines or LM Studio may suppress visible think tags or place thinking in a
separate provider field while enforcing the schema. Either presentation is
permitted and retained. It never changes the sole scored surface:
`choices[0].message.content`.

## Tasks

### 1. Filtered ordering

Task ID `filtered_ordering`, seed `6001`.

```text
Compute the requested result from this JSON input:
{"items":[{"code":"elm","active":true,"score":7,"cost":6},{"code":"fir","active":false,"score":10,"cost":2},{"code":"yew","active":true,"score":7,"cost":4},{"code":"oak","active":true,"score":5,"cost":8},{"code":"ash","active":true,"score":9,"cost":3}]}

Keep items whose active value is true and whose cost is at most 6. Sort by score from highest to lowest, breaking ties alphabetically by code. Return the codes.
Return exactly one JSON object with the single key "answer". Its value must be a JSON array of strings. Return no prose or Markdown fence.
Your complete response has a limit of 1024 tokens.
```

Oracle: `["ash","elm","yew"]`.

### 2. Ordered operations

Task ID `ordered_operations`, seed `6002`.

```text
Compute the requested result from this JSON input:
{"start":20,"operations":[{"kind":"add","value":6},{"kind":"double"},{"kind":"subtract","value":10},{"kind":"halve"}]}

Begin with start and apply every operation from left to right. Add increases the current value, double multiplies it by 2, subtract removes value, and halve divides the current value by 2. All intermediate and final values are integers. Return the final integer.
Return exactly one JSON object with the single key "answer". Return no prose or Markdown fence.
Your complete response has a limit of 1024 tokens.
```

Oracle JSON integer value: `21`.

### 3. Latest enabled revisions

Task ID `latest_enabled_revisions`, seed `6003`.

```text
Compute the requested result from this JSON input:
{"records":[{"name":"alpha","revision":1,"enabled":false},{"name":"beta","revision":2,"enabled":true},{"name":"gamma","revision":1,"enabled":false},{"name":"alpha","revision":3,"enabled":true},{"name":"beta","revision":4,"enabled":false},{"name":"gamma","revision":2,"enabled":true}]}

For each name, select only its record with the greatest revision. Keep the name only when that selected record has enabled equal to true. Return the kept names sorted alphabetically.
Return exactly one JSON object with the single key "answer". Its value must be a JSON array of strings. Return no prose or Markdown fence.
Your complete response has a limit of 1024 tokens.
```

Oracle: `["alpha","gamma"]`.

### 4. Dependency reachability

Task ID `dependency_reachability`, seed `6004`.

```text
Compute the requested result from this JSON input:
{"start":["hub"],"dependencies":{"hub":["north","south"],"north":["leaf1","shared"],"south":["leaf2","shared"],"leaf1":[],"leaf2":[],"shared":[],"isolated":["ghost"],"ghost":[]}}

Starting from every name in start, repeatedly follow dependencies. Return every reachable dependency, but do not include the starting names. Include each name once and sort the result alphabetically. Do not follow entries that are not reachable from start.
Return exactly one JSON object with the single key "answer". Its value must be a JSON array of strings. Return no prose or Markdown fence.
Your complete response has a limit of 1024 tokens.
```

Oracle: `["leaf1","leaf2","north","shared","south"]`.

## Exact response schemas

Tasks 1, 3, and 4 use this schema, replacing `<name>` respectively with
`filtered_ordering_answer`, `latest_enabled_revisions_answer`, and
`dependency_reachability_answer`:

```json
{
  "type": "json_schema",
  "json_schema": {
    "name": "<name>",
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

Task 2 uses the same outer object with name `ordered_operations_answer` and
`"answer": {"type": "integer"}`. No schema contains an enum, count, pattern,
range, oracle value, or other answer hint.

## Scoring and records

Run all four tasks once in numbered order, cold and without cross-call output.
Wrong or invalid answers do not stop the gate. There is no repair prompt.

Inherit the structured-output trial's exact JSON gate, recursive exact-type
equality, visible-content rule, attempt fields, hash-bound prompt/output files,
one exact-empty retry, nullable abort receipt, abort taxonomy, and cleanup
discipline. Condition is always `constrained`.

Replace the inherited single-GGUF artifact receipt with `package_verification`,
containing the sorted relative path, byte count, and SHA-256 for all eleven
package files plus the absolute path, byte count, and SHA-256 for both hub-
control files. Store that complete object in the packet receipt and top-level
summary. No single `artifact_sha256` may stand in for the package.

The summary fields are:

```text
packet_status: "complete" | "aborted"
abort_reason: null | "provider_envelope_invalid" | "request_contract_rejected" | "infrastructure_invalid"
candidate_result: "gate_pass" | "computation_unreliable" | null
```

The summary also contains `calls`, the chronological reports for every
completed logical call. Each report retains `logical_index`, `call_id`,
`task_id`, `condition`, `seed`, `gate_refusal`, `decoded_answer`,
`oracle_answer`, inherited `call_label`, and derived `call_state`. On normal
completion it contains exactly four reports. On abort it contains the completed
prefix only; the rejected exchange remains in its nullable attempt receipt and
is not fabricated into a completed call report.

`gate_pass` requires four `valid_correct` calls. Any completed packet with an
invalid or wrong call is `computation_unreliable`. An abort has no candidate
result and retains every completed or rejected exchange.

The gate may conclude only whether this exact Qwen package and runtime cleared
four basic constrained computations. It cannot establish general ability,
teachable headroom, admission, learning, or Formation. It loses value if prior
answers enter a task, the multimodal surface receives non-text content, a
schema hints an answer, output is repaired, history crosses calls, or anything
short of 4/4 is called a pass.

No inference call is licensed until cold review returns one stable protocol and
an independently reviewed fake-tested runner is licensed.

Independent cold review returned `QWEN_GATE_STABLE`. Runner implementation and
its 9-test fake-contact slice pass with the combined 258-test suite.
Independent runner review returned `RUNNER_LICENSED`; exactly four inference
calls are licensed.
