# An asymmetric world for suspension

## Main result

The deterministic domain conforms. It separates irreversible task risk,
uninformative delay, and lower-cost information gathering.

The same public task control completes one hidden profile and irreversibly fails
the other. Holding preserves the device but reveals nothing. A dedicated
diagnostic action preserves the device, costs one step, and emits a different
signal in each profile.

No model was called. Formation remains null.

## The world

Both hidden profiles share one exact public state:

- two opaque task controls;
- one opaque diagnostic control;
- the allowed action `hold`; and
- device status `intact`.

In profile 0, the first task control completes the task and the second fails it.
In profile 1, those outcomes reverse. Failure is terminal within the trial.

| Action | Profile 0 | Profile 1 |
| --- | --- | --- |
| First task control | Completed | Failed |
| Second task control | Failed | Completed |
| Diagnostic control | Intact, `steady_pattern` | Intact, `pulsed_pattern` |
| Hold | Intact, no signal | Intact, no signal |

The public input bytes remain the same across profiles. Neither the state nor
the result names the valid task control.

## Probe trajectory

For conformance only, an external scorer interprets `steady_pattern` as the
first task slot and `pulsed_pattern` as the second. Diagnostic action followed
by that interpreted task action completed both profiles in two steps without a
failure.

That interpreter is not a runtime capability. It demonstrates that the signal
contains useful information while keeping the environment from returning the
answer directly.

All eight one-step transitions, both probe trajectories, two terminal-state
refusals, eight malformed-input refusals, input immutability, repeat identity,
distinct result objects, and order independence passed.

## What this supports

This supports one computational instrument for studying action under
uncertainty. Ordinary task action now risks irreversible failure. Hold avoids
that risk but provides no information. Probe delays completion by one step but
can distinguish the hidden profiles without damaging the device.

The preceding two-control world could not create this comparison because every
task action was reversible and fully informative. This domain supplies the
missing pressure.

## Limits and next question

The diagnostic signals and costs are fixture values. The scorer's interpreter
does not show that a clerk can learn or apply the signal relation. No
participant selected an action, and no developmental history earned the
mapping.

The next live question is whether the restricted clerk can build signal-bound
records from prior probe and task consequences, then use a fresh probe to
select the right record without seeing the later task controls or answer. The
participant comparison should include cold task action, current and newest
records, hold, learned probe use, supplied probe guidance, and causal removal.

## Audit details

- Model calls: 0
- Frozen specification SHA-256: `0450b06fe031a9178a01cc3068d13c4841665f908f5820ebbda87e96517aa777`
- Packet SHA-256: `ae76cdc2f41a608b50bc78a6bb701206f0640655a8dc5450f931925855238a31`
- Specimen verdict: `conforms`
- Finding: `asymmetric_probe_domain_available`
- Formation verdict: `null`
- Replay: exact deterministic reconstruction

The exact public state, hidden profiles, transitions, probe trajectories,
refusals, and scorer-only interpreter are in [packet.json](packet.json).
