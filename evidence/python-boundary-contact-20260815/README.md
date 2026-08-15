# Strict Python boundary exploration

Status: **valid contact; stopped as not engaged**.

## What we tested

We asked the same cold Cursor model, Composer 2.5, to write a small Python
parser three times. The parser accepted two values described as “Python
integers.” Python makes this wording slightly tricky because `bool` is a
subclass of `int`: an `isinstance(value, int)` check accepts `True` and
`False`, while an exact-type check does not.

Our scorer required exact `int` values. The prompt did not explain that private
interpretation. The purpose of exploration was to see whether the model chose
the broader reading often enough to create a real failure that simple
persistence might later repair.

Each call started in a new empty directory with no resumed chat. All three
calls received the same prompt bytes. Each returned function then ran against
24 frozen inputs in separate child processes.

## What happened

All three functions rejected non-`int` values with an exact-type check
(`type(...) is not int`). Each function passed all 21 ordinary inputs and all
three held boolean inputs. Across the three calls, 72 of 72 executable checks
passed.

The runner therefore classified exploration as `not_engaged` and stopped after
the third call. It did not ask the model to write a lesson. It did not reveal
any validation task or send raw or lesson persistence.

## What this means

For this exact prompt and model, the proposed ambiguity did not produce the
behavior needed for a persistence comparison. There was no failed coding
occurrence for either raw persistence or a model-authored lesson to correct.
This task is therefore unsuitable as the next baseline contact.

This does not show that Composer always distinguishes booleans from integers.
Three calls on one parser cannot support that claim. It also says nothing about
Formation, learning, transfer, or whether persistence would help after a real
failure.

The stop still tells us something useful about method. The runner applied a
rule written before contact, ended the run without showing future cases, and
did not replace a solved task with a more convenient failure inside the same
experiment.

## Audit trail

[`summary.json`](summary.json) contains the complete mechanical reports. The
numbered files retain each exact prompt, raw function, and process receipt. An
independent evidence audit recomputed the hashes, reran all frozen inputs, and
returned `EVIDENCE_VALID` with no discrepancy.
