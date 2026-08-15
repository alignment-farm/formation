# Revision micro-environment

This package contains one isolated deterministic transition engine licensed by
the [micro-environment charter](../docs/MICRO_ENVIRONMENT_CHARTER.md). It reads
an immutable revision state and one exact action, then returns a fresh immutable
result.

It contains no formation runtime, trajectory harness, developmental lineage,
environment handoff, scorer, or persistence mechanism. Passing its conformance
suite establishes only state-dependent computation over the charter's frozen
domain. The reviewed implementation passes all 98 prospective cases in three
frozen orders plus the charter's refusal and shortcut-comparator checks.
