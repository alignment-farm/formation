# Suspension-consequence specimen

Status: **frozen deterministic specimen**.

## Question

After one contradictory observation suspends a record, what external cost does
each available response create?

The uncertain-sequence specimen counted withholding steps. This specimen asks
what those steps mean in the existing two-control world.

## Common uncertainty

The exact supported mirrored packet is the source. One stable world still uses
the current relation. One changed world uses the opposite relation. Both expose
the same public device, controls, position, target, current record, and newest
opposite proposal. Both have produced the same one contradictory public
observation.

The runtime cannot tell whether that observation was an anomaly or a real
change. Hidden relation labels are available only to the deterministic scorer.

The specimen uses one target-above and one target-below device from the retained
packet, with all three retained cold repeats in both worlds.

## Responses

The specimen compares six declared responses:

- act from the current record, then use the observed movement to finish;
- act from the newest opposite proposal, then use the movement to finish;
- use the exact retained cold-model action, then use the movement to finish;
- explore with the first control, then use the movement to finish;
- hold for one step without further action; and
- hold once, then explore with the first control and finish.

A non-hold action reveals which control increases position because the domain
is deterministic and the two effects are exact opposites. If the first action
reaches the target, the trial ends. If it moves one step away, the now-known
correct control needs two more actions to reach the target.

The scorer reports first-step target hits, movements away from target, holds,
relation resolution, unresolved trials, and total actions to target. It does
not collapse them into one reward.

## Frozen result condition

The specimen conforms only if:

- the exact supported mirrored packet and all selected cold action receipts are
  bound;
- the stable and changed trials have byte-identical public devices and opposite
  hidden relations;
- all retained cold actions select the second displayed control;
- current-record, newest-proposal, retained-cold, and first-control exploration
  each reach the target on six of twelve trials, move away on six, resolve the
  relation on all twelve, and require 24 total actions to finish all trials;
- the four non-hold responses distribute those successes across different
  world or target cells rather than receiving hidden truth;
- hold alone never moves away, never resolves the relation, and leaves all 12
  trials unfinished after 12 holds; and
- hold followed by exploration has the same six target hits and six movements
  away as first-control exploration, but requires 36 total actions because of
  the added hold.

This can show whether the current domain distinguishes suspension responses. It
cannot establish model behavior beyond the retained cold actions, assign a
universal cost to delay or wrong movement, or establish Formation.

## Evidence

The specimen makes no model calls. It writes exact source bindings, strategies,
environment trajectories, outcome vectors, and replay material under
`evidence/suspension-consequence-specimen-<run-id>/`.
