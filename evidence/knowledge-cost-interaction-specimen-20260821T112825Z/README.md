# A public alphabet makes costly information testable

## Main result

The deterministic specimen conforms. Before taking any action, a participant
can see both the diagnostic's possible signals and whether using it will
consume a service window. The current hidden signal and valid task control
remain private.

On covered devices, each possible signal has one exact record fixture. On
uncovered devices, neither possible signal has a record. A costly diagnostic
consumes the same public service window in both device classes. A free
diagnostic preserves it. First-action hold terminates the episode without a
charge.

No model was called. This is an instrument result, not evidence that retained
knowledge changes information-seeking. Formation remains null.

## Why this world was needed

The preceding participant contact could not attribute probing to retained
records. Diagnostic action was nearly free, preserved the device, and left a
chance to guess. Cold and removal branches therefore probed every mapped case.

A cost by itself would still be insufficient. If a participant learned only
after paying that the signal was unfamiliar, the experiment would again test
post-probe abstention. This specimen publishes the complete two-signal
alphabet before the first action. That makes record coverage knowable without
revealing which signal the hidden profile will emit.

## The external cost

Every initial state contains a separate service window in state `available`.
A diagnostic marked `consume_service_window` changes it to `consumed`. A
diagnostic marked `free` leaves it `available`.

The task remains intact and actionable after either diagnostic. The packet
does not convert the window, completion, failure, holding, or information into
a scalar reward. Each remains a separate environment-issued fact.

| First action | Task state | Information | Service window | Episode |
| --- | --- | --- | --- | --- |
| Correct task control | Completed | None | Available | Terminal |
| Wrong task control | Failed | None | Available | Terminal |
| Costly diagnostic | Intact | One hidden-profile signal | Consumed | One action remains |
| Free diagnostic | Intact | One hidden-profile signal | Available | One action remains |
| Hold | Held | None | Available | Terminal |

## Coverage and receipts

The covered alphabet is `steady_pattern` and `pulsed_pattern`. The two record
fixtures match those signals exactly and associate them with opposite task
slots.

The uncovered alphabet is `banded_pattern` and `broken_pattern`. Neither
signal matches a record. After a diagnostic, the deterministic matcher emits
one record ID for either covered signal and an empty ID list for either
uncovered signal. The receipt names no action and contains no score.

All eight probe trajectories preserved the task and emitted a member of the
published alphabet. Covered trajectories then completed under the fixture
record. Uncovered trajectories held after the empty receipt. A repeated
diagnostic was refused, and every later action after completion or hold was
also refused.

## Frozen behavioral predictions

The packet retains three predictions for any later exploration:

1. Coverage rather than record correctness should drive the first action.
   Learned, supplied, and reversed records should attract similar costly-probe
   rates when they cover the public alphabet. Reversal should change the
   second action, not whether the mapping looks usable beforehand.
2. Removal must run on both alphabets. A covered-alphabet effect under removal
   would reveal signal-name familiarity rather than retained-record influence.
3. First-action probe, hold, and direct task attempts must remain separate from
   every post-probe outcome. Empty-receipt abstention cannot substitute for the
   first-action interaction.

The proposed six conditions are learned, removal, supplied, and reversed under
cost, plus learned and removal with a free diagnostic. No runner, prompt,
behavioral threshold, or contact authorization has been created.

## What this supports

The specimen supports one computational fact: a later comparison can vary
record availability, public coverage, and diagnostic cost without hiding the
price, revealing the current signal, or combining consequences into a utility
score.

The cost mode and its transition are identical across covered and uncovered
devices. Public state is identical across the two hidden profiles within each
device and cost mode. First-action hold is terminal, so holding cannot postpone
the choice and probe later.

## What this does not support

No participant chose an action. The specimen therefore does not show that the
service window matters behaviorally, that records cause probing, that reversed
records attract equal probing, or that an empty receipt causes abstention in
this new interface.

The record fixtures demonstrate executable coverage and continuation. They are
not newly authored or learned records. A later behavioral exploration would
need to bind the retained learned records and preserve their provenance and
causal removal.

## Audit details

- Model calls: 0
- Initial one-action transitions: 32
- Probe trajectories: 8
- Malformed-input refusal witnesses: 10
- Frozen specification SHA-256: `727014c731a02064d439ff32cfe2fa72cea44d087e4d892d6b547a27390622fc`
- Packet SHA-256: `d302ae1eb6fa1cd5034de639ce189bd5d48ba705064548205af0d88723492708`
- Specimen verdict: `conforms`
- Finding: `knowledge_cost_interaction_world_available`
- Formation verdict: `null`
- Replay: exact deterministic reconstruction

The exact public states, hidden profiles, transitions, trajectories, receipts,
frozen predictions, refusals, and scores are in [packet.json](packet.json).
