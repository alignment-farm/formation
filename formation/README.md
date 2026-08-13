# Fixture-local formation code

This directory contains the runtime-owned parts of two fixture-local slices:
the shared six-receipt prefix and the first post-fork formation-condition
receipt. Both adapt runtime sources, emit frozen bytes, and issue current-run
handoffs.

It is not yet a general formation runtime. See
[`docs/MATERIALIZATION.md`](../docs/MATERIALIZATION.md) and
[`docs/CONDITION_APPEND.md`](../docs/CONDITION_APPEND.md).
