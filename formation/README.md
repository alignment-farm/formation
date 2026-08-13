# Fixture-local formation code

This directory contains the runtime-owned parts of three fixture-local slices:
the shared six-receipt prefix, the first post-fork formation-condition receipt,
and the in-memory proposal-to-admission root boundary. The first two adapt
runtime sources and emit frozen bytes. The third reads the retained source,
keeps interpreter authorship and governor authority distinct, and issues typed
semantic capabilities without selecting proposal or admission bytes.

It is not yet a general formation runtime. See
[`docs/MATERIALIZATION.md`](../docs/MATERIALIZATION.md) and
[`docs/CONDITION_APPEND.md`](../docs/CONDITION_APPEND.md), and
[`docs/ADMITTED_ROOT.md`](../docs/ADMITTED_ROOT.md).
