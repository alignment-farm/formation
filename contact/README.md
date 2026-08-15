# Model-contact runners

This directory contains narrow executors for reviewed contact charters. A runner
may assemble frozen prompts, invoke the named cold model, execute an external
oracle, and retain evidence. It may not interpret experience for the runtime or
turn calibration results into formation findings.

The first runner implements the
[SQLite contact charter](../docs/SQLITE_CONTACT_CHARTER.md). Its tests use fake
participant outputs and spend no model-contact budget.

The second runner implements the
[strict Python boundary contact](../docs/PYTHON_BOUNDARY_CONTACT_CHARTER.md).
It accepts one restricted function, runs every frozen input in a fresh child
process, and stops after exploration unless the predeclared boolean-as-integer
contrast appears. Its tests also use fake participant outputs.

The third runner implements the
[small-model admission exploration](../docs/MODEL_ADMISSION_EXPLORATION.md).
It verifies two exact local GGUF artifacts and their embedded chat templates,
loads each without vision or speculative decoding, and admits only a model that
is reliable on ordinary work while showing a repeatable, directly teachable
boundary gap. Its tests use fake inference envelopes.

The fourth runner implements the
[corrected Nemotron successor](../docs/NEMOTRON_ADMISSION_SUCCESSOR.md) without
rewriting the first packet. It exposes the complete restricted Python
environment to the model, uses fresh prompts and vectors, and stores ordinary
and held class labels on the vectors themselves. Its tests spend no model-call
budget.

The fifth runner implements the
[Gemma structured-action staircase](../docs/GEMMA_CONTRACT_STAIRCASE.md). It
screens exact 270M and 1B artifacts on four JSON computations before either can
earn a full admission packet. It scores only provider message content, never
reasoning text, and its tests use fake envelopes.
