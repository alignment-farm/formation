# Granite returned valid containers with four wrong answers

This gate asked one exact local Granite 4.0 H Tiny model to solve four basic
computations. Every request required a JSON object through the same grammar
that removed formatting failures in the preceding Gemma trial.

Granite returned valid JSON all four times. It returned the wrong value all
four times.

| Task | Required answer | Granite answer |
| --- | --- | --- |
| filter and order jobs | `ash`, `maple` | `maple`, `ash`, `birch` |
| apply four operations | `17` | `10` |
| keep latest enabled revisions | `oak` | `oak`, `pine` |
| follow reachable dependencies | `clay`, `fuel`, `kiln`, `mold` | those four plus unreachable `sand` |

The errors are straightforward. `birch` was below the priority threshold.
`pine` was disabled by its latest revision. `sand` could only be reached from
an unused branch. The ordered arithmetic was also incorrect.

This result closes the exact Granite artifact as `computation_unreliable`. It
does not earn a full admission charter. It also does not show that Granite
models generally lack these abilities: this was one quantized artifact, one
inference setup, four tasks, and one call per task.

The gate tested a prerequisite, not Formation. It supplied no developmental
experience, persistence, lesson, repair, or transfer case. The complete
prompts, outputs, request and model receipts, hashes, and scores are retained
beside this file. Independent cold audit returned `EVIDENCE_VALID`.
