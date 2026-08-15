# Corrected Nemotron admission result

Nemotron 4B did not qualify for the admission experiment. It spent most of the
fixed completion budget on internal reasoning, so its returned Python function
ended halfway through an expression. The frozen runner stopped immediately and
sent no other prompt.

This is a valid result for this exact model and inference setup. It is not
evidence that Formation works, and it does not show how the model would perform
with a different output budget or reasoning configuration.

## Why this run was needed

The first Nemotron packet was inconclusive. The model used Python's ordinary
`all` function, but the test process did not provide it and the prompt did not
warn the model. That hidden restriction made the failure ours rather than the
model's.

The successor repaired the instrument before contact. It used a new function,
new inputs, and new database tasks. The prompt listed every available Python
builtin, including `all`, and stated the source and process restrictions that
could reject an answer. Independent review approved the protocol and runner
before this call.

## What happened

The first task asked for one small function that validates a pair of strings
and joins them with a slash. Nemotron's response began correctly but stopped at:

```python
return payload[0] +
```

The response record says the model reached the fixed 768-token completion
limit. It used 702 of those tokens for internal reasoning and left only an
incomplete function as the answer. The Python parser therefore rejected the
answer with a syntax error.

This differs from the earlier hidden-builtin failure. The exact model, prompt,
sampling settings, and completion limit were frozen in advance. The answer was
nonempty, so the protocol did not permit the empty-response retry. An easy
anchor failure required the runner to stop as `contract_unreliable`.

## What the result means

Under this exact local artifact and inference contract, Nemotron did not
produce a usable answer to the first easy coding task. Its internal
reasoning described a complete solution, but an unreturned solution cannot be
executed and is not a passing action.

No target family ran. The packet therefore says nothing about whether Nemotron
has a teachable Python type boundary or SQLite `NULL` boundary. It also says
nothing about persistence, transfer, governed formation, or model quality in
other settings.

Together, the two initial candidates leave no admitted model: Ministral 3B
violated the required plain-code response in the first packet, and Nemotron 4B
failed to finish the first successor anchor. The next admission attempt must be
a new pre-contact packet. It may select another model or another declared
inference setup, but it may not rewrite this completed run.

## Record

- Terminal result: `contract_unreliable`
- Stopping call: `C-P1`, logical call 1 of at most 16
- Model: `nvidia/nemotron-3-nano-4b@q4_k_m`
- Model artifact SHA-256:
  `083af225449463dd7c38bebc888f9dcad187b834d8b15e08c297dda37c968b50`
- Prompt bytes: 1,277
- Raw answer bytes: 266
- Prompt SHA-256:
  `ebf2f76dea6964bfd087a6787cbfa596adb096de19ca173295d6cbd6c90bb5df`
- Raw answer SHA-256:
  `dfb75d5bdf362bcffc8ececeffe56803612569a9bda1ca6d8846df66122cbf32`
- Packet summary SHA-256:
  `065966e6ce92cf4af3abfe17dde19248eee9454a839cee23ec83129f00300e39`
- Model summary SHA-256:
  `c27afd665f6c2621ad0e9e687fc9fbfccf8e5992316073bdb75f88bc78a81f88`
- Independent evidence verdict: `EVIDENCE_VALID`

The JSON records retain the exact request, full provider response, usage,
reasoning text, source-gate result, executable vector report, artifact and chat
template verification, load receipt, timestamps, and hashes.
