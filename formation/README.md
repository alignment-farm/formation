# Fixture-local formation code

This directory contains the runtime-owned parts of six fixture-local slices:
the shared six-receipt prefix, the first post-fork formation-condition receipt,
the in-memory proposal-to-admission root boundary, and the public replay-
constraint append. The first two adapt runtime sources and emit frozen bytes.
The third reads the retained source,
keeps interpreter authorship and governor authority distinct, and issues typed
semantic capabilities without selecting proposal or admission bytes. The
fourth resolves one public target role within the exact admitted lineage and
binds a typed constraint without deriving a replay view. The fifth consumes
one exact root-bound shared-foreground delivery per branch and returns a typed
received handoff without claiming that an encounter opened.
The sixth consumes a sealed binding for that exact handoff, appends one positive
encounter, and returns a current encounter root without making the handoff's
harness provenance reachable from developmental lineage.

It is not yet a general formation runtime. See
[`docs/MATERIALIZATION.md`](../docs/MATERIALIZATION.md) and
[`docs/CONDITION_APPEND.md`](../docs/CONDITION_APPEND.md), and
[`docs/ADMITTED_ROOT.md`](../docs/ADMITTED_ROOT.md), and
[`docs/REPLAY_CONSTRAINT_APPEND.md`](../docs/REPLAY_CONSTRAINT_APPEND.md), and
[`docs/FOREGROUND_DELIVERY.md`](../docs/FOREGROUND_DELIVERY.md).
See also [`docs/ENCOUNTER_OPENING.md`](../docs/ENCOUNTER_OPENING.md).
