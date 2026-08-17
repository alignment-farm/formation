# Project-process instruments

This directory contains instruments that act on the research process itself.
They are not part of the Formation runtime, trajectory harness, developmental
lineage, or evidence plane.

## Waypoint

A waypoint is a defined navigational reference used to keep a voyage on its
intended course. This Waypoint makes a proposed task's route visible before an
agent starts it.

The agent must declare:

- what kind of work it proposes;
- which lifecycle boundary it targets;
- where success leads;
- where failure leads; and
- what maturity of claim the work could support.

Waypoint compares that declaration with the reviewed current route in
[`waypoint_route.json`](waypoint_route.json). It produces one of three results:

- `ON_ROUTE` (exit `0`): the work contacts the current lifecycle boundary;
- `SUPPORT_ONLY` (exit `1`): the work concretely supports that boundary but is
  not lifecycle progress; or
- `ROUTE_DRIFT` (exit `2`): the proposal skips the boundary, exceeds the claim
  level, opens another gate, or returns to model admission.

Show the current pressure:

```sh
python3 tools/waypoint.py show
```

Inspect the current implementation step:

```sh
python3 tools/waypoint.py inspect \
  --summary "Implement exact environment action application" \
  --kind lifecycle_step \
  --target environment_application \
  --success consequence_intake \
  --failure environment_application \
  --claim wire
```

An admission rabbit hole is deliberately loud:

```sh
python3 tools/waypoint.py inspect \
  --summary "Screen another model on generic JSON tasks" \
  --kind generic_competence_gate \
  --target model_selection \
  --success another_admission_packet \
  --failure another_model \
  --claim wire
```

The route state is public process policy, not discovered evidence. Change it
only when the root README and plan already name a new current boundary. A green
Waypoint result does not license code, establish a mechanism, or prove
Formation. It shows only that the proposed work has not repeated the declared
routing failure.
