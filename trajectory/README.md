# Fixture-local trajectory code

This directory contains the harness-owned parts of five fixture-local slices:
prefix validation and fork comparison; public-condition assignment, validation,
witness, and append checks; and the label-blind treatment batch plus
proposal/admission witnesses and admitted-root verification; and the hidden
ablation selection, public constraint delivery, witness, and exact returned-root
checks; and the one-time comparison-group freeze, root-bound shared-foreground
deliveries, and complete three-recipient witness set.

It is not yet a general trajectory harness. See
[`docs/MATERIALIZATION.md`](../docs/MATERIALIZATION.md) and
[`docs/CONDITION_APPEND.md`](../docs/CONDITION_APPEND.md), and
[`docs/ADMITTED_ROOT.md`](../docs/ADMITTED_ROOT.md), and
[`docs/REPLAY_CONSTRAINT_APPEND.md`](../docs/REPLAY_CONSTRAINT_APPEND.md), and
[`docs/FOREGROUND_DELIVERY.md`](../docs/FOREGROUND_DELIVERY.md).
