# Contested counterevidence accumulation

Status: **frozen deterministic specimen**.

## Question

Can an observation-grounded governor preserve several source occurrences and
distinguish stable contradiction from self-correction, isolated contradiction,
and unresolved evidence before changing a current record?

## Fixture

The current record says the first control increases position and the second
decreases it. A proposed opposite record may be source-supported by a complete
occurrence. Each occurrence remains an immutable ordered receipt with its own
source, selected control, movement status, movement, proposed record, and
composed-admission status.

The specimen contains four prospective histories:

- two complete first-control decreases supporting the same opposite proposal;
- one complete first-control decrease followed by a complete first-control
  increase supporting the current record;
- one complete first-control decrease with no corroborating occurrence; and
- one explicitly contested first-control movement whose direction is
  unresolved.

## Frozen policy

Only complete, uncontested, composed-admitted occurrences may support a record.
Missing or contested movement is never counted as support or contradiction.

The governor processes receipts in order:

- two consecutive eligible contradictions supporting the same proposal
  supersede the current version;
- eligible support for the current record after a contradiction leaves the
  current version active and closes that contradiction as uncorroborated;
- one eligible contradiction without corroboration suspends activation pending
  another occurrence; and
- a relevant unresolved contested occurrence suspends activation without
  selecting either record.

The decision must cite every considered occurrence and separately cite its
supporting, contradicting, closed, and unresolved subsets. It may derive a
count, but it may not replace the receipts with a vote or use a harness truth
label.

## Conformance

The specimen conforms only if repeated contradiction yields `superseded`, the
self-correcting history yields `current_retained`, the isolated contradiction
yields `suspended_pending_corroboration`, and contested evidence yields
`suspended_unresolved`. Every decision must preserve exact order and source
references.

This is a governance computation result. It cannot show that a clerk will
write the needed records, that later action improves, or that this policy is
optimal.

## Evidence

The specimen makes no model calls. It writes its packet under
`evidence/contested-counterevidence-accumulation-<run-id>/` and verifies exact
deterministic replay. Formation remains null.
