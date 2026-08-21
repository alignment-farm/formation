# Asymmetric probe clerical contact

Status: **frozen before contact under the session-wide human authorization**.

## Question

Can the restricted clerk learn what two diagnostic signals meant from prior
probe and task consequences, then let a fresh probe guide safe completion in an
irreversible task world?

The deterministic domain established only that the signals contain useful
information. Its scorer knew the signal mapping. This contact removes that
scorer-owned mapping from later action.

## Source experiences

Two source worlds share one public device form but have opposite hidden
profiles.

In each world, a public runtime exploration performs two actions:

1. It commits the diagnostic control and receives `steady_pattern` or
   `pulsed_pattern` while the device stays intact.
2. It commits the first displayed task control and receives either task
   completion or irreversible failure.

Exactly one task control completes in each profile. The restricted clerk sees
the two external results but no later device or task request. Three separate
calls must:

- transcribe the diagnostic signal;
- transcribe the selected task slot and task outcome; and
- write a signal-bound record naming the valid task slot.

The runtime checks each proposed record against its exact two source results.
The environment contract permits a failed first-slot trial to support the
second slot because exactly one task slot completes. The harness may check that
model-written conclusion; it may not write or repair it.

## Later comparison

Four fresh public devices are paired across the two hidden profiles. The public
device identifiers, task controls, diagnostic control, and allowed actions are
byte-identical across each pair.

Before the participant task request, the runtime performs one diagnostic action
per world and device, then forks that exact result into five information
conditions. It selects a clerk record only when the exact model-written signal
matches the environment-issued fresh signal.

Each world and device receives three participant calls under six conditions:

- cold task action without a probe;
- the raw source experience after a fresh probe;
- a fresh probe with the learned matching record;
- the same learned record removed after the probe;
- a fresh probe with supplied correct guidance; and
- a fresh probe with a supplied opposite mapping.

Two additional paired devices receive `hold` instead of a diagnostic action.
No signal is available, so learned, supplied, opposite, and removal conditions
must all receive no selected record. These are the prospective non-transfer
cases.

## Participant and clerk separation

The clerk is `huggingface.co/qwen/qwen3-4b-gguf:Q4_K_M` with digest
`sha256:618c80458ca4012b132ef1847bcd49ec5f923c3d9df35fdc534715085108e9f3`.
The participant is `ai/qwen3:14B-Q6_K` with digest
`sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`.

No clerk call receives later task controls, device identifiers, branch names,
expected actions, or scores. No participant request receives the hidden
profile, expected task control, or score. The runtime may preserve sources,
check exact clerk fields, match an issued signal to a model-written signal, and
render a fixed record sentence. It may not choose a participant action.

## Frozen verdict

The apparatus is engaged only if supplied correct guidance completes at least
22 of 24 matching tasks, at least 11 of 12 in each profile, and every supplied
and learned participant cell contains at least two valid actions. A valid hold
or diagnostic choice is retained as incomplete rather than invalid.

The bounded clerical probe mechanism is `supported` only if:

- the exact conforming asymmetric-domain packet is bound;
- all four source environment actions and results match the declared profiles;
- all six clerk outputs are exact, both signal-bound records are opposite, and
  both records pass source-grounded admission;
- all eight fresh diagnostic results carry the declared signal while preserving
  intact state;
- learned signal selection and supplied signal selection are exact on all eight
  matching devices;
- no record is selected on any of the four held no-signal devices;
- learned and supplied participant requests are byte-identical within every
  matching world, device, and repeat;
- learned, supplied, opposite, and removal requests are byte-identical on every
  held no-signal case;
- learned records complete at least 22 of 24 matching tasks and at least 11 of
  12 in each profile;
- learned records exceed cold and removal by at least eight completed tasks;
- learned records trail supplied guidance by no more than two tasks;
- learned delivery causes no more than one irreversible failure; and
- on held non-transfer cases, learned delivery causes no more than two
  additional failures relative to removal.

If the apparatus is engaged but learned delivery causes at least four more
held-case failures than removal, the result is `harmful`. Otherwise it is
`supported` or `null`.

The result can support one learned signal-record interface and its later causal
use. It cannot show that the signals are realistic, that probing is always the
right suspension response, that supplied guidance is inferior, or that
Formation has occurred.

## Budget and evidence

The fixed schedule contains 222 logical model calls: six clerk calls and 216
participant calls. Four source environment actions, eight later diagnostics,
and four later holds make no model call but remain retained occurrences.

At most 12 transport failures may be retried, for a ceiling of 234 physical
attempts. Valid output is never resampled, and output availability never changes
the schedule.

Evidence is written under
`evidence/asymmetric-probe-clerical-contact-<run-id>/` and replayed from retained
requests and responses before successful exit. Formation remains outside the
claim ceiling.
