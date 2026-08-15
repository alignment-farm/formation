# Gemma structured-action screen

Neither Gemma model passed the first structured-action task. Both exact local
setups stopped as `contract_unreliable`, and neither model received tasks 2
through 4.

This is a valid screening result. It does not test Formation or show whether
either model could acquire a skill through experience.

## What the screen asked

The input contained three labeled records. Two had `kept` set to true. The
model had to return those two labels in alphabetical order inside one JSON
object:

```json
{"answer":["brim","dawn"]}
```

The prompt prohibited prose and Markdown fences. It also stated the complete
256-token response limit. The runner scored only the visible message content,
not any provider reasoning field.

## What 270M returned

Gemma 3 270M returned a fenced Python-like program. It appears intended to
collect kept labels, but it uses JSON booleans inside Python and does not sort
the result. More importantly, the requested action was one JSON object, not a
program. The raw Markdown fence caused the predeclared
`gate_fail:markdown_fence` result before JSON parsing.

The response ended normally after 72 tokens. It was not cut off by the token
limit.

## What 1B returned

Gemma 3 1B returned a fenced JSON array:

```json
["dawn"]
```

This answer had three independent problems: it used a Markdown fence, omitted
the required `answer` object, and left out `"brim"`. The frozen gate stops at
the first applicable reason, so the recorded result is
`gate_fail:markdown_fence`.

The response ended normally after 14 tokens. It was not cut off by the token
limit.

## What follows

The 270M and 1B checkpoints do not earn a full admission charter under this
bare text interface. The result also shows that response formatting is still
ending screens before more interesting computational boundaries run.

A later packet may declare grammar-constrained JSON as part of the common
inference interface. If used, that constraint must apply equally to every
condition and remain separate from Formation. It would remove a formatting
failure mode; it would not supply the correct computed answer. The 1B payload
already shows that valid JSON alone would not fix its missing record. Task 1 is
contacted development material, and all four frozen screen tasks are barred
from reuse in a promoted packet.

## Record

- 270M terminal result: `contract_unreliable` at logical call 1
- 1B terminal result: `contract_unreliable` at logical call 1
- Shared prompt bytes: 409
- Shared prompt SHA-256:
  `2790eb5d076043b28808f04c761315090c65c1f860e24cde37955a2c2c990748`
- 270M output bytes: 241
- 270M output SHA-256:
  `c0bfddfad48852b1ad6b4c1719e82917e4946d4bcbb1ca87aa1f7ed306a4bfc5`
- 1B output bytes: 24
- 1B output SHA-256:
  `4cc32d1e902dcf7ed246ccb7177fc3abb45bd715a69e80b20e4bd9cbf6d7e94d`
- Packet summary SHA-256:
  `a0fc5789081691d0b6c67988107d7f57c6b10b571c32cb8ece752bd7e272d7a7`
- Independent evidence verdict: `EVIDENCE_VALID`

The retained JSON records include the exact artifacts and chat template,
loads, prompts, outputs, requests, provider responses, token usage, gate
reports, timestamps, and stop decisions.
