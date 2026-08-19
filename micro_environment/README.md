# Deterministic environment specimens

This package contains four isolated deterministic transition engines. The first
is licensed by the
[revision micro-environment charter](../docs/MICRO_ENVIRONMENT_CHARTER.md). It
reads an immutable revision state and one exact action, then returns a fresh
immutable result.

It contains no formation runtime, trajectory harness, developmental lineage,
environment handoff, scorer, or persistence mechanism. Passing its conformance
suite establishes only state-dependent computation over the charter's frozen
domain. The reviewed implementation passes all 98 prospective cases in three
frozen orders plus the charter's refusal and shortcut-comparator checks.

The second is licensed by the
[calibration information-gap problem](../docs/CALIBRATION_INFORMATION_GAP.md).
It applies one opaque device control, calibration request, or hold operation
under an environment-owned family calibration. Its tests show that identical
public foreground can require opposite actions, one consequence can identify
the two-slot mapping, new device tokens defeat action copying, and another
family remains underdetermined.

Neither specimen contains or establishes a formation mechanism. The calibration
engine does not license model contact, select prospective cases, or decide how
an unobserved-family action should be scored.

The explicit consequence renderer is a versioned representation over the
calibration transition. It reports which ordered slot was selected and whether
position increased, decreased, or stayed unchanged. It does not state the
unobserved opposite-slot rule, author a candidate, or decide applicability.

The third engine is the reviewed
[phase-coupled control specimen](../docs/PHASE_COUPLED_CONTROL_SPECIMEN.md). It
applies opaque controls under a two-phase family profile and can execute an
already committed two-control pair without intermediate feedback. Canonical
occurrence and action-interface helpers remain separate from the pure
transition, while warrant scoring lives outside this package. Nineteen tests
establish only the proposal's deterministic pre-contact obligations.

The fourth engine implements only the hidden opaque-control physics for the
[unselected lineage behavior specimen](../docs/UNSELECTED_LINEAGE_BEHAVIOR_SPECIMEN.md).
It distinguishes unavailable content from an available empty proposal, applies
only already committed actions, and returns factual movement, hold, refusal, or
not-applied results. Branch construction, retained foregrounds, role assignment,
and scoring remain outside the environment module.
