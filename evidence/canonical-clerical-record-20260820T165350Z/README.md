# Canonical clerical record diagnostic

## Main result

Named effect fields repaired two of four records, but the clerk still failed
when it had to infer the unobserved control's opposite effect. The frozen
verdict is null.

Two structured records were exact and rendered into the calibrated sentence.
In the other two, the clerk wrote `decreases_position` for both controls. Those
records were rejected and produced no sentence.

## What was tested

This diagnostic reused four exact sensory transcriptions and 12 valid later
scope normalizations from the staged clerical experiment. It verified the
source packet and specimen hashes before contact.

The 4B clerk received each exact transcription and returned named first-control
and second-control effect fields. A deterministic serializer inserted those
values into the sentence order that had made 32 of 32 actions in the delivery
calibration. The serializer did not read the sensory report or infer an effect.

The participant then acted on fresh device, family, position, and control
identities.

## Results

The two correct structured records were the cases where the second control
increased. In both cases where the second control decreased, the clerk copied
that observed decrease into both fields instead of assigning the opposite
effect to the first control.

| Participant condition | Correct matching actions |
| --- | ---: |
| Cold | 16/32 |
| Retained raw sensory reports | 16/32 |
| Both rendered records | 16/32 |
| Normalized selection of rendered records | 20/32 |
| Normalized selection of supplied sentences | 28/32 |
| Oracle selection of rendered records | 24/32 |
| Oracle selection of supplied sentences | 32/32 |

Every participant output was valid. Every branch made 8 of 16 unrelated
actions, so the attempted repair caused no observed unrelated loss.

The retained normalized matcher again selected correctly in 10 of 12 cases
and made no false selection for the novel or recombined devices.

## What this teaches us

The deterministic renderer is not the remaining problem. When the clerk filled
both named fields correctly, it produced the exact participant sentence. The
failure happened one step earlier: the model did not reliably infer the
unobserved opposite effect from one observed effect.

The prior clerk sentences already contain both facts correctly. Their only
problem was order. A cleaner clerical task is therefore to parse those explicit
facts into named fields. That requires language extraction, not causal
completion. If parsing works, the serializer can impose the calibrated order
without adding a lesson.

## Limits

This diagnostic composes retained outputs with new clerk calls and fresh action
cases. It is not a fresh end-to-end experiment. It does not support a complete
learned instrument or Formation.

## Audit details

- Clerical model: `huggingface.co/qwen/qwen3-4b-gguf:Q4_K_M`
- Clerical digest: `sha256:618c80458ca4012b132ef1847bcd49ec5f923c3d9df35fdc534715085108e9f3`
- Participant model: `ai/qwen3:14B-Q6_K`
- Participant digest: `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Logical calls: 340
- Physical attempts: 340
- Retries: 0
- Frozen specification SHA-256: `6b15af7236ff353284e2c651794ddb840a2cee1cda124b3fe479a2b395547f45`
- Specimen SHA-256: `2a9e37a3ba3cf23f24fc1d3a3b1d936227359f8c82c892fe820ccbc4a27c8701`
- Packet SHA-256: `935438e4c8cdc6dbbf7b33305a6614afb32159a7cd00876deda0ab28cf6baec8`
- Frozen instrument verdict: `null`
- Formation verdict: `null`
- Replay: exact from retained request and response bytes

The computed record is [packet.json](packet.json). The retained source hashes
and fresh cases are in [specimen.json](specimen.json). Both model identities are
in [provider.json](provider.json). Every raw request and response is under
`attempts/`.
