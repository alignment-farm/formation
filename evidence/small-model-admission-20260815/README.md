# First small-model admission packet

Status: **exploratory evidence partially valid; stopped at the first anchor**.

## What we tested

We began with two local models: Ministral 3B and Nemotron 4B. Each model first
received an easy Python task. A model had to pass four such anchors before it
could reach the coding boundaries used to measure cold headroom and direct-rule
teachability.

The runner verified the exact local model files and chat templates, loaded each
model without vision or speculative decoding, and sent one cold request with
the same frozen sampling settings.

## What happened

Ministral wrapped its function in a Markdown code fence even though the prompt
explicitly prohibited fences. The source gate refused the output and the runner
stopped that model. This is a valid contract failure for the contacted prompt.

Nemotron returned an unfenced function with the right overall logic. It used
Python's ordinary `all(...)` builtin to check the two list elements. The hidden
execution sandbox did not provide `all`, so otherwise valid inputs raised
`NameError` and the runner stopped the model.

That second stop is mechanically faithful to the frozen scorer, but it is not
a fair conclusion that Nemotron could not follow the stated task. The prompt
never told the model that `all` was unavailable. The failure belongs partly to
the instrument.

## What this means

Ministral does not pass this packet's first response-contract anchor. Nemotron
remains unclassified. Neither model reached the cold-versus-direct-rule probes,
so this packet found no developmental band and says nothing about whether
either model can benefit from Formation.

The useful result is methodological. A restricted execution environment is
part of the task contract even when its builtin list is hidden in a technical
charter. If ordinary safe Python is unavailable, the participant must be told.
Otherwise the experiment can mistake an undisclosed tool restriction for model
incompetence.

A corrected successor must keep this run unchanged, use new prompts and
vectors, and state the available Python builtins directly. It may continue the
unresolved Nemotron admission. It may not reinterpret or erase this stop.

## Audit trail

[`summary.json`](summary.json) retains the mechanical results. Each model
directory contains its exact prompt, output, request and response envelopes,
executable report, artifact and runtime receipt, and stopping reason. The
runner unloaded both models and restored Ministral's optional vision projector.
An independent audit reproduced the results and returned `EVIDENCE_PARTIAL`.
