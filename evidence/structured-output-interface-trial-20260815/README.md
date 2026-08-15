# A JSON guardrail fixed the container, not the answer

This trial asked two very small Gemma models to solve two simple problems. Each
model saw every problem twice. One request used the ordinary text interface.
The other added a JSON rule that could control the shape of the reply but could
not reveal the answer.

The rule did one job perfectly in these four comparisons: it turned every
reply into the requested JSON object. Without the rule, every reply used a
Markdown code fence and therefore failed the machine-readable action contract.

The rule did not make any answer correct.

| Model | Problem | Ordinary text | JSON-constrained |
| --- | --- | --- | --- |
| Gemma 270M | select matching records | invalid format | valid JSON, wrong answer |
| Gemma 270M | apply operations in order | invalid format | valid JSON, wrong answer |
| Gemma 1B | select matching records | invalid format | valid JSON, wrong answer |
| Gemma 1B | apply operations in order | invalid format | valid JSON, wrong answer |

The selection problem required `alder` and `clover`. The constrained 270M
reply returned all four tags. The constrained 1B reply also included `birch`,
whose `open` value was false. The update problem required this calculation:

```text
17 - 4 = 13
13 × 2 = 26
26 + 3 = 29
```

The constrained 270M reply was `4`; the constrained 1B reply was `7`.

This is useful because a machine-readable reply and a correct reply are
different properties. Here the JSON constraint cleared the format refusal in
all four comparisons. The values inside the resulting valid objects were still
wrong. The bare replies do not establish that either model had a correct answer
hidden behind its fence.

The trial does not show that structured output is generally helpful or harmful.
It used two tasks, one call per condition, and different condition orders for
the two models. It is not evidence of learning, Formation, or model admission.
It shows only four observed transitions under the frozen local setup.

The complete prompts, requests, responses, hashes, model receipts, scores, and
pair records are retained beside this file. Independent cold audit returned
`EVIDENCE_VALID`.
