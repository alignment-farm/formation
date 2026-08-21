# An empty match receipt stopped unsupported guesses

## Main result

An explicit empty match receipt changed the participant's action after an
unfamiliar diagnostic signal. The exact parent full-catalog and silent-absence
requests both attempted a task control in all six cases and failed three. The
learned receipt stated that no retained record matched. It produced six holds
and no failures.

On known signals, the same receipt delivered the matching learned record and
completed all 18 tasks. Supplied receipts also completed all 18. Reversing the
record meanings failed all 18.

The frozen verdict is `supported`. This is a result about a harness
representation, not autonomous model development. Formation remains null.

## Why this successor was needed

The first receipt contact changed the shared participant explanation. Its
silent and no-record controls unexpectedly held on every unfamiliar-signal
case, so there was no unsafe baseline for the receipt to improve. Its verdict
was `not_engaged`.

This successor restored the exact participant system prompt, request schema,
device states, diagnostic results, and catalog rendering from the earlier
harmful contact. Seventy-two full-catalog and no-record control requests matched
their retained parent SHA-256 hashes exactly.

Only the new receipt conditions added material. The receipt lived inside the
old `retained_material` field. No shared instruction explained it.

## The receipt

The runtime compared the environment-issued signal with the exact signal field
in each model-written record. It then wrote a factual receipt containing the
observed signal and the IDs of matching records.

For a known signal, one ID and its exact record text followed. For
`unmapped_pattern`, the ID list was empty and no task record followed. The
receipt did not name a task control, recommend hold, or reveal the hidden
profile.

The comparison was deterministic string equality. No model classified the
match, and the runtime did not choose the participant action.

## What happened on known signals

| Representation | Tasks completed | Irreversible failures |
| --- | ---: | ---: |
| Learned match receipt | 18 | 0 |
| Supplied match receipt | 18 | 0 |
| Exact parent full catalog | 15 | 3 |
| Exact parent silent absence | 5 | 6 |
| Duplicate exact no-record control | 5 | 4 |
| Reversed match receipt | 0 | 18 |

Learned and supplied receipt requests were byte-identical in all 24 paired
cells, including known and unfamiliar signals. The reversed result shows that
the participant followed the selected record's meaning rather than treating a
nonempty receipt as a generic instruction to act.

## What happened on the unfamiliar signal

| Representation | Task attempts | Holds | Failures |
| --- | ---: | ---: | ---: |
| Exact parent full catalog | 6 | 0 | 3 |
| Exact parent silent absence | 6 | 0 | 3 |
| Duplicate exact no-record control | 5 | 1 | 2 |
| Learned empty receipt | 0 | 6 | 0 |
| Supplied empty receipt | 0 | 6 | 0 |
| Reversed empty receipt | 0 | 6 | 0 |

The full and silent controls reproduced the pressure that the first receipt
contact had lost. The learned, supplied, and reversed empty-receipt requests
were byte-identical in all six unfamiliar-signal cells. Their safe behavior
there depended on the empty match representation, not on a hidden difference
in record provenance or task meaning.

## What this supports

The learned clerical substrate now has a bounded way to represent both sides of
applicability:

- a nonempty receipt says which exact model-written record matched a fresh
  environment signal; and
- an empty receipt says that the matcher found no such record.

That distinction mattered behaviorally. Silent omission looked like missing
context and invited a guess. Explicitly representing the empty result produced
abstention without supplying a task answer.

The receipt also improved known-signal use from 15 of 18 under the full catalog
to 18 of 18 under exact selection. This run did not isolate whether that gain
came from the receipt or from showing one selected record instead of two. The
unfamiliar-signal comparison is the cleaner causal result because both receipt
paths contained no record text.

## What this does not support

The runtime performed the diagnostic before this request. The result does not
show that retained experience caused the participant to seek information. The
preceding self-directed contact could not establish that because cold and
removal already probed.

An empty receipt is an explicit runtime statement about applicability. The
participant did not learn that matching operation on its own. Exact string
matching is also much narrower than semantic applicability in realistic work.

The next empirical problem is the first action. A new domain must make probing
useful when a learned mapping exists but costly or useless when it does not.
Only then can learned and removal branches distinguish information-seeking
instead of sharing the same obvious diagnostic choice.

## Audit details

- Participant model: `ai/qwen3:14B-Q6_K`
- Participant digest: `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Harmful parent packet SHA-256: `92fe84ff6a8579aa6e9c4d70ff443de04732815712e2d0c8fca1b228a9e39ebb`
- Not-engaged parent packet SHA-256: `a68e4934da537e5af3f58ba33c14fe7450666d22a34702dacb7da180e7e575f9`
- Logical calls: 144
- Physical attempts: 144
- Retries: 0
- Exact parent control request hashes: 72
- Packet SHA-256: `ff828090bd36dbafcf82c9b95922cba5898d43d1111d3caecbe11e31546e7e26`
- Frozen specimen SHA-256: `6adcdd5373b672a4df6bdab657f8fc1df719b73ef41d644a432bf4e058905912`
- Frozen verdict: `supported`
- Replay: exact from retained requests and responses
- Formation verdict: `null`

The complete calls, parent hashes, assignments, outcomes, and verdict are in
[packet.json](packet.json). The frozen bindings and budget are in
[specimen.json](specimen.json), and the provider receipt is in
[provider.json](provider.json).
