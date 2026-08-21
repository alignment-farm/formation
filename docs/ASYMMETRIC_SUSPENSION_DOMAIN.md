# Asymmetric suspension domain

Status: **frozen deterministic specimen**.

## Purpose

Build the smallest environment in which acting under uncertainty, holding, and
probing have genuinely different consequences.

The preceding suspension specimen could not distinguish ordinary action from
exploration. Every non-hold action was reversible and revealed the complete
relation. This domain adds one irreversible task consequence and one lower-cost
diagnostic action. It is an instrument, not a Formation result.

## Public state and actions

Each trial begins with one intact device. The public state contains:

- an opaque device identifier;
- two opaque task-control strings;
- one opaque diagnostic-control string; and
- status `intact`.

`hold` is also allowed. The public state does not contain the hidden profile,
the valid task control, a diagnostic interpretation, an expected result, or a
score.

## Hidden profiles

The environment has two profiles behind the same public state:

- profile 0 accepts the first task control;
- profile 1 accepts the second task control.

The profiles also produce different diagnostic signals. The signal names are
`steady_pattern` and `pulsed_pattern`. The environment reports a signal; it
does not report which task control is valid.

## Transition rules

From an intact state:

- The valid task control changes status to `completed`.
- The other task control changes status to `failed`.
- Failure is irreversible within the trial.
- The diagnostic control leaves status `intact`, consumes one step, and returns
  the profile's signal.
- `hold` leaves status `intact`, consumes one step, and returns no signal.

A completed or failed state is terminal. Every later action must refuse rather
than change it.

The result reports only the committed action, status before and after,
application disposition, diagnostic signal if any, and step cost. It does not
state the hidden profile, valid task control, or scorer verdict.

## Prospective conformance cases

Apply all four actions—the two task controls, diagnostic control, and hold—to
the same public intact state under both hidden profiles. The eight results must
show:

- each task control completes one profile and irreversibly fails the other;
- diagnostic action completes or fails neither profile and emits opposite
  signals;
- hold completes or fails neither profile and emits no signal; and
- public input bytes remain equal across profiles.

Then apply a fixed external diagnostic interpreter only in the scorer. It maps
`steady_pattern` to the first task slot and `pulsed_pattern` to the second. A
diagnostic step followed by the interpreted task action must complete both
profiles in two steps without failure. This interpreter is a conformance oracle,
not a runtime capability licensed for later contact.

## Refusals

The engine must refuse:

- missing, extra, empty, or non-string state fields;
- unknown status or action;
- equal task-control strings;
- reuse of `hold` as a device control;
- mismatched profile and public device identity;
- caller-supplied hidden profile, valid control, signal, result, or score; and
- any action after `completed` or `failed`.

Inputs are immutable. Repeated execution returns equal values in distinct
result objects, and case order cannot change a transition.

## Pass condition and claim boundary

The specimen passes only if all eight transitions, both probe-then-act
trajectories, public identity checks, refusals, immutability checks, repeat
checks, and order checks conform.

Passing establishes one computational fact: this domain separates irreversible
task risk, uninformative delay, and lower-cost information gathering. It does
not show that a clerk can interpret the signal, that a governor should probe,
that a participant will use the result, that the costs are realistic, or that
Formation has occurred.

## Evidence

The specimen makes no model calls. It writes its exact cases, transitions,
probe trajectories, refusal witnesses, and replay packet under
`evidence/asymmetric-suspension-domain-<run-id>/`.
