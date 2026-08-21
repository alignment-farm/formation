# Retained-rule clause-order evidence

This directory contains the completed 72-call clause-order trial. It compared
empty retained material with two semantically equivalent controller rules. One
rule described the increasing slot first. The other described the first
displayed slot first. Each condition ran eight times on two fresh same-family
cases and one opposite-profile non-transfer case. The contact completed on
2026-08-19.

## Outcome

The second-then-first rule matched empty delivery on every call. The
first-then-second rule changed both same-family distributions and left the
other family unchanged.

| Case | Empty | Second then first | First then second |
| --- | ---: | ---: | ---: |
| Same family, target above | 0/8 correct | 0/8 correct | 7/8 correct |
| Same family, target below | 0/8 correct | 0/8 correct | 8/8 correct |
| Other family, target above | 8/8 correct | 8/8 correct | 8/8 correct |

For the two same-family cases, the first-then-second rule differed from the
equivalent reverse-order rule by total variation distances `0.875` and `1.0`.
The upward request returned the correct second control seven times and the
wrong first control once. All other condition-case requests were stable across
their eight repeats.

## What this says

The preceding result was not explained by copying the first slot mentioned in
the retained sentence. The effective sentence mentioned the first slot first,
yet the model chose the first slot for a downward target and the second slot
for an upward target. That is the behavior expected from using the complete
mapping.

Equivalent surface forms were not equivalent for this model and interface. A
rule ordered by displayed slot—first control, then second control—made the
mapping influential. A rule ordered by movement direction—first the increasing
control, then the decreasing control—was inert in this fresh packet.

One upward draw still varied, so the result supports a distributional
interface observation rather than determinism. It also remains an authored
static lesson supplied by the harness. It is not evidence that experience
caused the model to acquire or author the mapping.

The next developmental contact should give the model an acquisition occurrence
and external result, require it to author one first-then-second mapping sentence
without supplying the mapping answer, and compare later authored delivery with
authored ablation, raw occurrence, and the exact static mapping. The authored
text must be delivered as returned, without repair.

## Integrity and cost

- Model: `ai/qwen3:14B-Q6_K`
- Artifact digest:
  `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Protocol: `retained-rule-clause-order-trial-v1`
- Logical calls: 72/72
- Physical attempts: 72/76
- HTTP 200 responses: 72
- Retries: 0
- Valid actions: 72/72
- Prompt tokens reported by the provider: 23,304
- Completion tokens reported by the provider: 2,019
- Elapsed packet time: about 79 seconds

The directory contains the provider receipt, canonical specimen and packet,
and the exact request, response, and metadata files for every attempt. The
runner replayed the packet from raw evidence before exiting successfully. The
terminal verdicts remain:

```json
{"formation_verdict":null,"validation_verdict":null}
```
