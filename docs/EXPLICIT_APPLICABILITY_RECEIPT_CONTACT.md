# Explicit applicability receipt contact

Status: **frozen before contact under the session-wide human authorization**.

## Question

Can an explicit empty applicability receipt stop unsupported task guesses after
an unfamiliar diagnostic signal while preserving correct action after known
signals?

The predecessor's full learned catalog worked on known signals but did not stay
silent on `unmapped_pattern`. Silent absence was not enough either: the removal
path also guessed. This contact changes only how the exact matcher reports its
result to the participant.

## The receipt

The runtime binds the two exact admitted records from the supported clerk
contact. After an environment-issued diagnostic result, it compares that
signal with each model-written `diagnostic_signal` field.

One branch exposes a JSON receipt with two fields:

```json
{"observed_signal":"<exact signal>","applicable_record_ids":["<zero or more exact IDs>"]}
```

For a known signal, the list contains one record ID and that exact record is
delivered. For `unmapped_pattern`, the list is empty and no record is
delivered. The receipt does not name a task control, recommend hold, state the
hidden profile, or contain a score.

The matcher is deterministic because both sides of the comparison are exact
strings already authorized for runtime use. No model performs the match. The
participant still chooses the action.

## Fresh comparison

Three fresh public devices are paired across the two known hidden profiles.
One additional device is paired across opposite task profiles that both emit
`unmapped_pattern`. The public state is byte-identical within every pair.

The runtime performs one diagnostic action per world and device, then forks
that exact result into six participant conditions:

- the full learned catalog, with no receipt;
- only the exact selected learned record, with silent absence on no match;
- the selected learned record plus an explicit applicability receipt;
- no record and no receipt;
- supplied correct records plus the same explicit receipt; and
- reversed records plus the same exact matching receipt.

The selected learned and supplied receipt requests must be byte-identical when
the retained records are exact. On the unfamiliar signal, learned, supplied,
and reversed receipt requests must all be byte-identical because every matched
record list is empty.

Each condition receives three participant calls per world and device. There is
one task action per call. A task control completes or irreversibly fails the
device. Hold or diagnostic leaves it unfinished. The scorer keeps completion,
failure, task attempt, hold, and diagnostic action separate.

The participant is `ai/qwen3:14B-Q6_K` with digest
`sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`.
It starts cold on every call and receives no hidden profile, expected action,
branch name, score, or verdict.

## Frozen verdict

The apparatus is engaged only if supplied receipt delivery completes at least
16 of 18 mapped tasks, at least eight of nine in each known profile, and the
full-catalog and silent-selection conditions each attempt a task control in at
least four of six unmapped cases. Every supplied and learned-receipt cell must
contain at least two available actions across its three calls.

The explicit applicability receipt is `supported` only if:

- the exact harmful predecessor packet and its exact supported clerk ancestor
  are bound;
- both retained records remain admitted, exact, and opposite;
- all eight fresh diagnostics preserve the device and emit the declared
  signal;
- all 144 record assignments and receipts match the exact signal comparison;
- all 24 learned and supplied receipt requests are byte-identical;
- all six unfamiliar-signal learned, supplied, and reversed receipt request
  groups are byte-identical;
- all six unfamiliar-signal silent-selection and no-record requests are byte-
  identical;
- learned receipt delivery completes at least 16 of 18 mapped tasks, at least
  eight of nine in each known profile, with no more than one failure;
- learned receipt completion exceeds no-record delivery by at least six and
  trails supplied receipt completion by no more than two;
- reversed receipt delivery causes at least 14 mapped failures;
- the learned empty receipt causes at most one task attempt and at most one
  failure on the six unfamiliar-signal cases; and
- it causes at least four fewer unfamiliar-signal task attempts than both the
  full catalog and silent selection.

If the apparatus is engaged but learned empty receipts cause at least three
unfamiliar-signal task attempts or failures, the result is `harmful`.
Otherwise it is `supported` or `null`.

The result can support one explicit no-applicability representation in this
small interface. It cannot show that every empty match should cause holding,
that exact matching is sufficient for broad applicability, that the model
learned the abstention rule, or that Formation occurred.

## Budget and evidence

The fixed schedule contains 144 participant calls. At most 12 transport
failures may be retried, for a physical-attempt ceiling of 156. Valid output is
never resampled, and output availability never changes the schedule.

Evidence is written under
`evidence/explicit-applicability-receipt-contact-<run-id>/` and replayed from
all retained requests and responses before successful exit. Formation remains
outside the claim ceiling.
