# Explicit calibration consequence representation

Status: **pre-contact representation specification; deterministic formatter
implemented; no model behavior or Formation effect claimed**.

## Main point

The calibration environment created a real information gap, but its first live
contact encoded the decisive event only as an action token and two positions.
Qwen3 14B saw the first control move from 0 to -1 and still authored that the
first slot increases.

The environment already knows two simpler facts about its own transition:

```text
selected_slot: first
movement_direction: decreased
```

Expose those facts in the external consequence. Do not expose the inferred
lesson that the second slot increases. The model must still combine the factual
observation with the public two-slot invariant, author a candidate, and use it
later.

This change tests whether the prior failure was caused by incidental decoding
of the event representation or by failure to use counter-prior consequence at
all.

## Authority boundary

The environment may report which ordered slot received the exact action because
it owns the current device's control mapping. It may report whether position
increased, decreased, or stayed unchanged because it owns the before and after
state.

Those are observed transition facts. They are not a candidate, scope,
governance decision, expected later action, or claim about why the model acted.
The environment must not fill `increasing_slot` after an ordinary control
action. That opposite-slot conclusion remains the interpreter's work.

`request_calibration` is different: its declared environment function is to
return the increasing slot directly. It may therefore retain the existing
`increasing_slot` field. `hold` reports no selected slot and unchanged movement.

The harness may retain hidden profiles and expected actions for evidence. It
may not add, edit, or repair the explicit consequence.

## Exact factual fields

The new immutable result contains the original factual transition fields plus:

```text
selected_slot: first | second | null
movement_direction: increased | decreased | unchanged
```

The rules are mechanical:

- selecting the current state's `first_control` reports `first`;
- selecting `second_control` reports `second`;
- `request_calibration` and `hold` report no selected slot;
- a larger after-position reports `increased`;
- a smaller after-position reports `decreased`; and
- equal before and after positions report `unchanged`.

The implementation is
[`micro_environment/explicit_calibration_consequence.py`](../micro_environment/explicit_calibration_consequence.py).
It calls the frozen calibration transition and renders these two facts. It has
no model, runtime, interpreter, governor, retriever, scorer, or trajectory
assignment.

## Identifying pressure

In a binary calibration, observing the first slot decrease logically implies
that the second slot increases. The representation deliberately stops one step
before that implication. A model that returns `first` after receiving the
explicit facts has not been confused by action-token position or arithmetic
alone.

Fresh later devices must still replace both control strings and require both
movement directions. Fresh mirrored worlds must still cover
`first_increases` and `second_increases`. An unrelated family and an
already-current state remain necessary selective-use pressures.

The raw occurrence, authored interpretation, no-persistence, and governed
candidate conditions remain distinct mechanisms. Shared formatting can control
gross presentation but cannot make their semantics equivalent.

## Design attacks

The representation loses its purpose if:

- the environment writes the unobserved opposite-slot conclusion after a
  control action;
- a runtime or harness component adds the factual fields after seeing expected
  later behavior;
- explicit fields disagree with the exact action or before/after state;
- hidden calibration, branch, relation, expected action, or score enters the
  public result;
- fresh action tokens recur from acquisition; or
- a successful candidate is credited as Formation without prospective
  behavioral and causal comparison.

Six deterministic tests check the factual mapping, preserve direct calibration
requests, keep holds slot-free, and refuse candidate or experimental fields in
the result type.

## Next boundary and stopping rule

One final bounded exploratory contact may use fresh mirrored worlds and this
exact result representation with the already-contacted Qwen3 14B artifact. It
must freeze all cases and budgets before contact, retain the old representation
as history rather than rewrite it, and issue no validation verdict.

If explicit environment facts still fail to produce a correct counter-prior
candidate or raw later use, stop representation variants. The next research
problem would then be the practice or model responsibility itself, not another
formatter, output constraint, or model search.
