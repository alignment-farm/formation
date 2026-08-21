# Uncertain-consequence policy specimen

Status: **frozen deterministic specimen**.

## Question

What does the current two-confirmation policy gain and cost when observations
may be anomalous, alternating, or unresolved?

The preceding mirrored contact showed that recovery can causally guide later
action. It did not show that two matching observations are the right amount of
evidence. This specimen compares that policy with immediate revision before
another learned contact.

## Histories

Each history begins with relation 0 as the current record. Every occurrence
retains its order, the relation that was actually in force for scoring, and the
relation reported by the public consequence channel. The governors receive the
reported relation or an unresolved marker. They do not receive the hidden
relation in force.

Five six-occurrence histories are fixed:

- a stable relation with two isolated opposite reports;
- one clean lasting change;
- a stable relation with alternating reports;
- a lasting change interrupted by one unresolved report; and
- a lasting change followed by one isolated old-relation report.

The hidden relation is used only to score whether a delivered record was
correct, wrong, or withheld.

## Policies

The **immediate** policy replaces the current record after one complete
opposite report. An unresolved report suspends delivery until another complete
report arrives.

The **two-confirmation** policy suspends after one complete opposite report. It
replaces the current record only after two consecutive complete reports support
the same opposite relation. A report supporting the current record closes a
pending contradiction. An unresolved report suspends delivery and breaks the
consecutive sequence.

Both policies retain every occurrence and every state transition. Neither may
read the hidden relation, collapse the history into a vote, or erase a report
after recovery.

## Frozen result condition

The specimen conforms only if both policies preserve all 30 occurrences and
replay exactly, and if the comparison exposes both sides of the tradeoff:

- immediate revision delivers a wrong record on six steps and withholds on one;
- two-confirmation delivers no wrong record and withholds on eleven steps;
- immediate revision makes six false replacements while two-confirmation makes
  none;
- on the clean lasting change, immediate revision adapts on the first changed
  observation and two-confirmation adapts one observation later; and
- after the change interrupted by unresolved movement, two-confirmation waits
  three observations from the true change before it can deliver the new record.

The specimen may show a safety-responsiveness tradeoff. It cannot select a
universally correct threshold, establish probabilities from five authored
histories, show learned-clerk behavior, or establish Formation.

## Evidence

The specimen makes no model calls. It writes its exact histories, policy
transitions, scores, and replay material under
`evidence/uncertain-consequence-policy-specimen-<run-id>/`. Hidden truth remains
in the scorer fields and never enters either policy input.
