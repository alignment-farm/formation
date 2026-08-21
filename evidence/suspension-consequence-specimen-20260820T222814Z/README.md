# What suspension costs in the current world

## Main result

The deterministic specimen conforms, but the current domain cannot distinguish
the main non-hold responses.

Acting from the current record, acting from the newest proposal, using the
retained cold-model action, and deliberately pressing the first control all had
the same aggregate result. Each reached the target immediately on 6 of 12
trials, moved one step away on 6, revealed the relation on all 12, and needed 24
total actions to finish.

No model was called. Formation remains null.

## Why the responses collapse

The specimen begins after one contradictory observation. A stable world still
uses the current relation. A changed world uses the opposite relation. Their
public device, controls, position, target, current record, and newest proposal
are identical.

In this two-control world, every non-hold action is also a perfect experiment.
Movement immediately reveals which control increases position. If the action
reaches the target, the trial ends in one step. If it moves away, the now-known
correct control reaches the target in two more steps.

The four non-hold responses choose different first actions:

- The current record succeeds in the stable world and moves away in the changed
  world.
- The newest proposal does the reverse.
- The retained cold model always chose the second displayed control, so its
  successes split by target direction.
- First-control exploration produced the complementary directional split.

Those choices allocate risk to different world-and-target cells. None reduces
the aggregate risk in this symmetric, reversible environment.

## Holding

Holding alone moved nowhere, caused no wrong movement, learned nothing, and left
all 12 trials unfinished.

Holding once and then exploring had the same six immediate exploration hits and
six movements away as exploring immediately. It needed 36 total actions instead
of 24 because every trial paid for the extra hold.

This does not make holding universally bad. It shows that the present world
assigns delay a cost while giving hold no information or protective benefit
beyond avoiding one reversible movement.

## What this supports

This supports a domain-boundary finding: “suspend the record” does not identify
a useful response policy here. Empty delivery still leads the cold participant
to act, and every task action simultaneously resolves the uncertainty.

The environment is therefore too symmetric and too forgiving to compare
cautious action policies. A policy can move risk between cells, but it cannot
reduce both error and delay.

## Limits and next question

The record-guided and exploration continuations are deterministic strategy
specimens, not new participant-model results. Only the cold first actions came
from retained model evidence.

The next domain needs asymmetric consequences. A wrong task action should have
a cost that cannot be erased by two corrective moves, and a deliberate probe
should be able to gain information at a smaller but nonzero cost. That domain
can ask whether suspension should trigger probing, holding, or ordinary action
without defining caution as success in advance.

## Audit details

- Source packet SHA-256: `5f829cf7c82cda235badf7bca35c30063caac4e2d011f04fbb4e523175a8b8c4`
- Model calls: 0
- Frozen specification SHA-256: `cb877f7cfbd36afa271c7641069200f0bca686b675783aac809cd6fdb97917da`
- Packet SHA-256: `e4ca778f76903be7938d3d2d08e407dd6adf3c887d6c9c77823bc7fbc784a6a9`
- Specimen verdict: `conforms`
- Finding: `symmetric_action_information_equivalence`
- Formation verdict: `null`
- Replay: exact deterministic reconstruction

The exact retained cold actions, public devices, hidden scorer relations,
strategies, environment trajectories, and outcome vectors are in
[packet.json](packet.json).
