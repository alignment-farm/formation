# Knowledge-cost interaction specimen

Status: **frozen deterministic specimen**.

## Purpose

Build the smallest zero-call world in which retained knowledge could change
the value of seeking information before the participant acts.

The preceding world made diagnostic action attractive in every branch. It
preserved the device, revealed a signal, and left a task action available.
Cold and removal therefore probed even though they could not interpret the
signal. Adding a cost alone would not repair that problem: before paying it,
the participant must also be able to tell whether its retained records cover
the signals the diagnostic can return.

This specimen makes the diagnostic alphabet and its external cost public. It
keeps the hidden emitted signal and valid task control private. It is an
instrument, not a behavioral result or contact charter.

## Public device and service window

Every initial state contains:

- an opaque device identifier;
- two opaque task controls;
- one opaque diagnostic control;
- the exact two-signal alphabet the diagnostic may emit;
- either `consume_service_window` or `free` as the diagnostic cost;
- a service window in state `available`;
- task status `intact`; and
- episode phase `first_action`.

The service window represents a separate scheduled opportunity. A costly
diagnostic occupies it. A free diagnostic does not. Task completion remains
possible after either diagnostic, so the window consequence is not another
name for task failure or delay. The environment reports no scalar reward and
does not rank task completion, service-window preservation, failure avoidance,
diagnostic action, or holding.

The cost mode is identical across covered and uncovered devices within each
comparison. Only the public alphabet differs.

## Covered and uncovered alphabets

The covered device publishes `steady_pattern` and `pulsed_pattern`. The fixed
record fixtures contain one exact record for each signal. They associate the
signals with opposite displayed task slots.

The uncovered device publishes `banded_pattern` and `broken_pattern`. Neither
signal occurs in the record fixtures. Signal names are public before the first
action, but the hidden profile determines which member of the published pair
will be emitted.

Both device classes have two hidden profiles. The first profile emits the
first published signal and accepts the first task slot. The second emits the
second signal and accepts the second task slot. The same public state bytes are
used for both hidden profiles.

These deterministic relations prove only that the proposed cases are
executable. A later participant request must not reveal the hidden profile,
emitted signal, valid slot, expected action, score, or verdict.

## Episode rules

At `first_action`:

- the valid task control completes the task and terminates the episode;
- the other task control fails irreversibly and terminates the episode;
- `hold` terminates the episode without consuming the service window; and
- the diagnostic preserves the intact task, reveals the profile's signal, and
  opens exactly one `post_diagnostic` action.

A costly diagnostic changes the service window from `available` to `consumed`.
A free diagnostic leaves it `available`. The result records information
acquisition and service-window consumption separately.

At `post_diagnostic`, one task control or `hold` terminates the episode. A
second diagnostic is refused. Every action after termination is refused
without changing state or charging a cost.

## Exact-match receipt

After a diagnostic, a deterministic matcher compares the environment-issued
signal with the exact signal field in each record fixture. Its receipt contains
only the observed signal and matching record IDs.

Covered signals produce one matching ID. Uncovered signals produce an empty
ID list. The receipt does not name a task control, recommend holding, state the
hidden profile, or contain a score. Selected record text belongs to a later
participant interface, not to this environment result.

## Frozen predictions for a later exploration

The following predictions are frozen before runner work or model contact:

1. **Coverage, not correctness, drives the first action.** Under cost, learned,
   supplied, and reversed records should attract diagnostic first actions at
   similar rates on covered devices. Reversed records should cause failure
   after the signal rather than reduce probing before it.
2. **Removal crosses both alphabets.** Removal must run on covered and uncovered
   devices. A covered-alphabet probe advantage under removal would expose a
   signal-name or alphabet-familiarity effect rather than retained-record
   influence.
3. **First and second actions remain separate.** First-action probe, hold, and
   direct task attempt are distinct. Post-probe task attempt, hold, completion,
   failure, exact-match receipt, and service-window consumption are also
   distinct. Empty-receipt abstention cannot substitute for the first-action
   interaction.

A compact later exploration may compare learned, removal, supplied, and
reversed records under cost, plus learned and removal with a free diagnostic.
The free-removal cell is an engagement check: if it does not probe often, a
reduction under cost cannot be interpreted as cost sensitivity.

## Prospective conformance cases

The zero-call packet must establish:

- public-state identity across the two hidden profiles for every device and
  cost mode;
- exact publication of covered and uncovered alphabets before action;
- the same cost mode and service-window semantics across both device classes;
- opposite terminal task outcomes across profiles;
- terminal first-action hold without a window charge;
- exact costly and free diagnostic window transitions;
- exactly one post-diagnostic action and refusal of a repeated diagnostic;
- one-record receipts for covered signals and empty receipts for uncovered
  signals;
- separate task, information, abstention, and cost fields;
- input immutability, repeat equality in distinct objects, order independence,
  and malformed-input refusals; and
- exact replay from the retained packet.

## Pass condition and claim boundary

The specimen conforms only if every prospective case and refusal above passes.

Conformance establishes that the world can expose a knowledge-by-cost
interaction without hiding the cost, revealing the current signal, combining
outcomes into a utility score, or allowing hold to postpone the first choice.
It does not show that a model will probe, that retained records cause probing,
that the cost matters behaviorally, that the records were learned, or that
Formation occurred.

No participant-model request, contact charter, behavioral threshold, or live
authorization is part of this specimen.

## Evidence

The specimen makes no model calls. It writes exact states, profiles,
transitions, trajectories, receipts, refusals, predictions, and replay facts
under `evidence/knowledge-cost-interaction-specimen-<run-id>/`.
