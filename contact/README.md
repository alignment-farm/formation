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
