# Learned contested-counterevidence continuation

Status: **frozen before contact under the session-wide human authorization**.

## Question

Can the restricted clerk turn several ordered observations into source-bound
record proposals, and can the governor use the resulting history to replace,
restore, or suspend a record before later action?

The experiment tests the next step after the deterministic accumulation
specimen. It does not assume that every contradictory observation is a stable
change in the world.

## Concrete task

Each lineage begins with two admitted version-2 records, one for scope A and
one for scope B. The current A record says what each of two controls does.
A public exploration policy presses the first displayed control. It does not
know the control effects or the answer to any later action problem.

Four lineages receive different ordered histories:

- **Repeated contradiction:** two complete movements support the same opposite
  A relation. The governor should replace A's current record.
- **Self-correction:** one movement supports the opposite relation, then one
  supports the current relation. The governor should restore the current A
  record and close the first contradiction as uncorroborated.
- **Isolated contradiction:** one complete movement supports the opposite
  relation. The governor should suspend A while awaiting another observation.
- **Contested movement:** the environment reports that the movement direction
  is disputed. The governor should suspend A without selecting either record.

Scope B never changes. Every source occurrence keeps its own order, action,
environment result, clerk output, and admission decision.

## Clerk and governor

The restricted clerk receives only a sensory report. For each occurrence it
transcribes the selected control and movement, writes both control effects,
parses those facts into named fields, and projects the proposed effect for the
selected control. It never receives a later device, target, allowed control,
answer, branch, governance state, or score.

The runtime checks the clerk proposal against the retained sensory report. A
complete proposal may support the current or opposite record. A proposal from
the contested report cannot be admitted because no movement direction is
available.

The governor processes admitted receipts in order:

- one contradiction suspends A pending corroboration;
- two consecutive contradictions supporting the same proposal replace A;
- later support for the current record restores A and closes the earlier
  contradiction; and
- contested movement suspends A as unresolved.

The decision retains every receipt. It may not use the later environment
profile, an expected answer, or a scorer label.

## Later comparison

Each lineage receives fresh A-above, A-below, B-above, B-below, novel, and
recombined devices. Every case receives three participant calls under six
conditions:

- cold, with no retained material;
- the raw ordered sensory history;
- the catalog allowed by the final governance state;
- the latest complete clerk proposal without accumulation governance;
- removal of A while leaving B intact; and
- a supplied correct A-and-B catalog.

For the later environment, repeated contradiction remains changed. The
self-correcting, isolated, and contested lineages use the current A relation.
This makes the cost of caution visible. In the isolated lineage, immediate use
of the lone opposite proposal should be worse than suspension if the event was
transient. The scorer knows these later profiles; the clerk and governor do
not.

The learned normalizer sees only the current device description. The runtime
compares its two model-written visible fields with the eligible record scopes.
Novel and recombined cases should receive no record.

## Frozen interpretation

The apparatus is engaged only if supplied correct records make at least 43 of
48 matching actions, make at least five of six A and five of six B actions in
each lineage, and every supplied and governed participant cell contains at
least two valid actions. Invalid outputs elsewhere remain wrong.

The bounded result is `supported` only if:

- the exact supported parent packet and all eight version-2 admissions bind;
- all six explorations commit the first displayed control;
- the five complete occurrences have their prospectively declared movements,
  and the contested occurrence has no settled movement;
- all five complete clerk records and selected-effect projections are exact
  and pass composed admission;
- the contested proposal is quarantined regardless of what the clerk writes;
- all six intermediate governance states and all four final states match the
  declared histories while preserving exact source order;
- at least 20 of 24 later normalizations are exact, with no more than two false
  unrelated selections;
- every later catalog assignment matches the declared governance, latest,
  removal, supplied, or empty role;
- governed repeated contradiction and self-correction each make at least five
  of six A actions and exceed A-removal by at least two;
- the governed catalog makes at least 21 of 24 unchanged-B actions;
- isolation suspension exceeds immediate use of the lone opposite proposal by
  at least two A actions;
- suspension sends no A record in the isolated and contested lineages; and
- governed delivery loses no more than three unrelated actions relative to
  cold delivery.

If the apparatus is engaged but governed delivery loses at least six unrelated
actions, the result is `harmful`. Otherwise it is `supported` or `null`.

This experiment can support one learned, source-preserving accumulation
mechanism in a tiny controlled world. It cannot show that two observations are
an optimal threshold, that the system handles natural sensor noise, that the
learned records outperform supplied guidance, or that Formation has occurred.

## Models, budget, and evidence

The clerk is `huggingface.co/qwen/qwen3-4b-gguf:Q4_K_M` with digest
`sha256:618c80458ca4012b132ef1847bcd49ec5f923c3d9df35fdc534715085108e9f3`.
The participant is `ai/qwen3:14B-Q6_K` with digest
`sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`.

The fixed schedule contains 480 logical model calls: 24 clerk calls over six
source occurrences, 24 later scope normalizations, and 432 later participant
calls. The six public exploration actions and environment results make no
model call but remain retained occurrences.

At most 12 transport failures may be retried, for a ceiling of 492 physical
attempts. Valid model output is never resampled. Output availability never
changes the schedule.

Evidence is written under
`evidence/learned-contested-counterevidence-continuation-<run-id>/` and replayed
from retained requests and responses before successful exit. Formation remains
outside the claim ceiling.
