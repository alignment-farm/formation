# Learned signal records guided safe action

## Main result

The restricted clerk turned two past diagnostic and task results into two
correct signal records. Those records then let the participant complete all 24
fresh tasks after a diagnostic probe, with no irreversible failure.

Removing the records cut completion to 12 of 24 and caused 12 failures. Raw
source events produced the same result. Supplying correct copies of the records
again completed all 24 tasks. Reversing their meaning caused all 24 tasks to
fail.

This is a supported result for one harness mechanism. It is not evidence that a
model developed on its own, and it is not a Formation result.

## The task

Each device had two task controls and one diagnostic control. One task control
completed the task. The other caused an irreversible failure. The diagnostic
control preserved the device and emitted one of two signals.

The source experience made the meaning of each signal available through
consequence:

- a steady signal was followed by a successful trial of the first task
  control; and
- a pulsed signal was followed by a failed trial of the first task control.

The public device rule said that exactly one task control completes. From the
second result, the clerk could therefore infer that the second task control was
valid after a pulsed signal.

The clerk saw only these old diagnostic and task results. It did not see later
device identifiers, controls, action requests, correct answers, or scores.

## What changed

The two source histories and all later environments stayed fixed. A small
clerical model made three restricted calls for each source world. It copied the
signal, copied the task outcome, and wrote a record that joined the signal to
the valid displayed task slot.

On a fresh device, the runtime performed one diagnostic action. It delivered a
clerk record only when the signal written in that record exactly matched the
new environment signal. The runtime did not choose or repair the participant's
task action.

Six later conditions separated the useful information from nearby
alternatives: no probe, raw source events, the learned record, the same record
removed, a supplied correct record, and a supplied record with the mapping
reversed.

## What happened

Both clerk records were exact and passed their source checks:

- `steady_pattern` meant the first displayed task control; and
- `pulsed_pattern` meant the second displayed task control.

All eight fresh diagnostic results preserved the device and carried the
expected signal. All eight learned record selections were exact.

Across the 24 fresh signaled tasks in each condition:

| Information available | Tasks completed | Irreversible failures |
| --- | ---: | ---: |
| Learned signal record | 24 | 0 |
| Supplied correct record | 24 | 0 |
| Learned record removed | 12 | 12 |
| Raw source events | 12 | 12 |
| No prior probe or record | 6 | 5 |
| Supplied reversed record | 0 | 24 |

The learned and supplied requests were byte-identical in all 24 paired cells.
Their equal results show that the learned record reached the participant in the
same usable form as the positive control. The reversed record shows that the
participant followed the record's meaning rather than merely becoming more
cautious when any record was present.

Four paired devices received a hold result instead of a diagnostic signal. No
record was selected for any of them. In all 12 repeated requests per condition,
the learned, removed, supplied, and reversed paths were byte-identical. The
participant held every time. The learned mechanism therefore stayed silent
when its required signal was absent in these cases.

## What this supports

The result supports a narrow substrate mechanism:

1. a restricted second model can write a compact relation from old external
   consequences;
2. the runtime can check that relation against its exact source events;
3. a later environment signal can select the relation without exposing the
   hidden task answer; and
4. delivering that relation can cause a separate cold model to choose the safe
   task action.

The causal comparison is stronger than a changed answer. Removing the record
removed the benefit, supplying the same content restored it, and reversing the
content reversed the outcome.

## What this does not support

The runtime chose the diagnostic action before the participant request. The
result therefore does not show that the practitioner learned when to probe.
It shows only that the retained records made the result of a probe useful.

The signal language was small, the task rule was explicit, and the later
devices changed opaque identifiers rather than domain structure. The learned
record tied supplied guidance. No model weights changed. Formation remains
null.

The next experiment should present the intact uncertain device before any
probe. The participant must decide whether to risk a task control, hold without
learning, or use the diagnostic control. If it probes, a later request can test
whether the same retained records guide the final task action.

## Audit details

- Clerk model: `huggingface.co/qwen/qwen3-4b-gguf:Q4_K_M`
- Clerk digest: `sha256:618c80458ca4012b132ef1847bcd49ec5f923c3d9df35fdc534715085108e9f3`
- Participant model: `ai/qwen3:14B-Q6_K`
- Participant digest: `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Logical calls: 222
- Physical attempts: 222
- Retries: 0
- Packet SHA-256: `4c7bf10b7ea53abe4f1a9b4ddd477674b07101fc92139c37ed9abc2c2a06f005`
- Frozen specimen SHA-256: `eac3629bf130828d11cecb7c4dd8acd8570ba2869fd0a61ec21176e819a449a9`
- Frozen verdict: `supported`
- Replay: exact from retained requests and responses
- Formation verdict: `null`

The complete calls, occurrences, assignments, scores, and verdict are in
[packet.json](packet.json). The exact pre-contact specimen is in
[specimen.json](specimen.json), and the model and provider receipt is in
[provider.json](provider.json).
