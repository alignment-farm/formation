# First learned clerical instrument experiment

## Main result

The experiment did not test the full idea because the participant could not
reliably use even a supplied correct record. The frozen verdict is
`not_engaged`.

The restricted 4B clerk nevertheless performed one part of the proposed job
well. It classified every matching device correctly and rejected every wholly
novel device. It failed the harder recombination test: when a device combined
one feature from each stored scope, it selected one of those incomplete
matches. This produced 10 correct classifications out of 12 with both
model-written and supplied record scopes.

The encoding stage was weak. All four clerk outputs were valid JSON and all
four normalized the visible features correctly. Only one of the four described
the actuator effects correctly. None matched the required exact byte form.

## What the models saw

The 14B participant acted in a small device world. Each later device had new
identity strings and new controls. A matching device shared two visible design
features with an earlier source device.

The 4B clerk never saw the participant's controls, position, target, action
request, expected action, or score. During encoding it saw a description of the
source device, which displayed actuator had been used, and whether the gauge
rose or fell. During classification it saw a later device description and the
scope fields of stored records, but not their control effects.

The harness moved the clerk's exact outputs between these declared surfaces.
It did not repair an output or replace a valid answer.

## What happened

The participant made 32 matching actions in each condition.

| Condition | Correct matching actions |
| --- | ---: |
| Cold, with no retained material | 12/32 |
| Both raw sensory reports | 10/32 |
| Both clerk records without selection | 12/32 |
| Clerk-selected clerk records | 14/32 |
| Clerk-selected supplied records | 15/32 |
| Oracle-selected clerk records | 15/32 |
| Oracle-selected supplied records | 15/32 |

The last row was the strong interface check. It needed at least 29 correct
actions and made only 15. Because the participant did not use a known-correct,
correctly selected record, its later scores cannot tell us whether the clerk's
pipeline would have helped under a usable delivery form.

Every participant response was a valid action object. All branches made 8 of
16 unrelated actions, the same as cold. The clerk pipeline therefore caused no
observed unrelated loss in this run.

## What this teaches us

The asymmetric model boundary worked mechanically. The clerk performed
classification without receiving action information, and matching generalized
across fresh family and device identities. Its failure on recombined features
is also informative: the model often treated one shared feature as enough even
though the prompt required both.

Two other stages need repair before the complete mechanism can be judged.
Natural-language consequence encoding did not reliably preserve which
actuator moved the gauge in which direction. The retained record used a new
container and field names that the participant had never been shown to use.
Even the supplied record failed, so this delivery surface was not calibrated.

The next experiment should isolate the participant interface with supplied
records. If a direct effect payload works, a later clerical successor can stage
sensory transcription before record compilation and can normalize current
features before a mechanical exact-scope match. That would preserve the
restricted second-model role while removing the two failures observed here.

## Limits

This run does not support a learned clerical pipeline, acquisition, or
Formation. It also does not show that a second model is unhelpful. The strong
participant ceiling failed, so the full causal chain never became measurable.

The 10-of-12 classification result is an exploratory observation from one
small deterministic domain. It needs a fresh prospective comparison before it
can become a finding.

## Audit details

- Clerical model: `huggingface.co/qwen/qwen3-4b-gguf:Q4_K_M`
- Clerical digest: `sha256:618c80458ca4012b132ef1847bcd49ec5f923c3d9df35fdc534715085108e9f3`
- Participant model: `ai/qwen3:14B-Q6_K`
- Participant digest: `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Logical calls: 368
- Physical attempts: 368
- Retries: 0
- Frozen specification SHA-256: `5e08fcdc604e98724b7c1c2e7e04bdd07a96f4a7559a063325f0c46b2e26b1f6`
- Specimen SHA-256: `34e45a113171ee190eb70f03074953998384eb0f0dca24962e44c3187127389f`
- Packet SHA-256: `ae9edf7cb79f0dd89f6bec29e4458f0e73328c0706a7e7eced2c4bb6e7d7b6eb`
- Frozen instrument verdict: `not_engaged`
- Formation verdict: `null`
- Replay: exact from retained request and response bytes

The computed record is [packet.json](packet.json). The fresh worlds and
information boundaries are in [specimen.json](specimen.json). The exact model
identities are in [provider.json](provider.json). Every raw request and response
is under `attempts/`.
