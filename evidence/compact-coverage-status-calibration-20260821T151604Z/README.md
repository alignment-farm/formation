# A plain coverage status still produced guesses

## Main result

The compact coverage status did not guide the first action. The participant did
not probe under either `complete` or `none`. It mostly guessed a task control
directly and failed across every status condition.

The frozen verdict is `harmful`. The prospective route decision is
`stop_coverage_representation_route`. This result closes the current sequence
of alphabet, receipt, and status variants. Formation remains null.

## Why this calibration was small

The preceding successor placed a detailed coverage receipt beside the full
catalog. Catalog branches still probed every uncovered case, while removal
mostly guessed. That left one plausible explanation: the catalog might have
overwhelmed an otherwise usable coverage fact.

This calibration removed the catalog and reduced the fact to one exact field:

```json
{"coverage_status":"complete"}
```

or:

```json
{"coverage_status":"none"}
```

`complete` meant that every public diagnostic signal had a matching retained
record. `none` meant that no public signal did. The status named no action and
gave no advice. The run stopped after the first action, so no later receipt
could rescue the result.

## What happened

| Status source | Public alphabet | Probes | Holds | Direct guesses | Failures |
| --- | --- | ---: | ---: | ---: | ---: |
| Learned `complete` | Covered | 0/6 | 0/6 | 6/6 | 3 |
| Supplied `complete` | Covered | 0/6 | 0/6 | 6/6 | 3 |
| Reversed `complete` | Covered | 0/6 | 0/6 | 6/6 | 3 |
| Learned `none` | Uncovered | 0/6 | 0/6 | 6/6 | 2 |
| Supplied `none` | Uncovered | 0/6 | 0/6 | 6/6 | 3 |
| Reversed `none` | Uncovered | 0/6 | 0/6 | 6/6 | 4 |
| Removal `none` | Covered | 0/6 | 2/6 | 4/6 | 3 |
| Removal `none` | Uncovered | 0/6 | 0/6 | 6/6 | 4 |

The learned, supplied, and reversed `complete` requests were byte-identical in
all six paired cells. Every `none` request was also byte-identical within its
public device cell, including removal. The different provenance labels existed
only in the scorer.

The exact parent controls remained engaged. The full learned catalog caused
six of six probes on both alphabets. Free removal also caused six of six probes
on both alphabets. All 24 parent first-request hashes matched their retained
bytes.

## What this teaches

The participant did not use the compact status as a promise that a useful
record would be delivered after probing. Removing the catalog removed the
catalog-driven probe, but the model did not replace it with selective
information-seeking. It guessed instead.

This is no longer a good target for more representation variants. Three forms
have now failed for different reasons:

- a public alphabet beside the catalog did not make coverage usable;
- a detailed coverage receipt beside the catalog did not override catalog
  presence; and
- an isolated compact status did not cause probe under `complete` or hold under
  `none`.

The useful result is the stopping decision. The project should not continue
changing receipt wording in search of one that makes this participant perform
the desired first action.

## What this does not show

The result does not show that retained records are useless. Earlier comparisons
showed that exact learned records guide action after an environment signal is
available, lose their effect under removal, reverse behavior when their meaning
is reversed, and can be revised after counterevidence.

It does show that this cold participant did not turn record applicability into
safe, costly information-seeking through the tested interfaces. Whether such a
decision belongs in an explicitly governed runtime policy is a separate
mechanism question. It should not be smuggled in as another prompt or receipt.

## Audit details

- Participant model: `ai/qwen3:14B-Q6_K`
- Participant digest: `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Logical calls: 72
- Physical attempts: 72 of a ceiling of 84
- Retries: 0
- Exact parent first-request hashes: 24
- Exact compact-status assignments: 48
- Parent packet SHA-256: `c9e3dc22c2ba65d4164d322054e9a61028901b83503d04972c547577a82c6456`
- Frozen specimen SHA-256: `789477f993db524319cb46e82f4618ff218c4e72cb16a5dc78cfc5a9e067ed1a`
- Packet SHA-256: `861af7714add42452da4b2a3aaec6310f9ed18a3b2c54a4825cd4eadc26e5f5c`
- Frozen verdict: `harmful`
- Route decision: `stop_coverage_representation_route`
- Replay: exact from retained requests and responses
- Formation verdict: `null`

The prospective contract is in [specimen.json](specimen.json). Exact calls,
actions, consequences, controls, and the route decision are in
[packet.json](packet.json). The model and interface receipt is in
[provider.json](provider.json).
