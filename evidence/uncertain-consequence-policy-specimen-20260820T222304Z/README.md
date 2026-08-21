# Uncertain-consequence policy tradeoff

## Main result

The deterministic specimen conforms. It exposes a clear tradeoff between
reacting quickly and avoiding false revision.

Across 30 ordered observations, immediate revision delivered a wrong record on
six steps and suspended on one. Requiring two consecutive confirmations never
delivered a wrong record, but suspended on eleven steps.

No model was called. Formation remains null.

## The comparison

Each history began with relation 0 as the current record. The public
consequence channel then reported relation 0, relation 1, or unresolved
movement. Five histories represented:

- a stable world with isolated anomalous reports;
- a clean lasting relation change;
- alternating reports in a stable world;
- a lasting change interrupted by unresolved movement; and
- a lasting change followed by one old-relation anomaly.

The governors saw only the ordered public reports. The scorer separately knew
which relation was actually in force.

## Results

| Policy | Correct record delivered | Wrong record delivered | Suspended | False replacements |
| --- | ---: | ---: | ---: | ---: |
| Revise after one report | 23 | 6 | 1 | 6 |
| Require two consecutive reports | 19 | 0 | 11 | 0 |

Immediate revision adapted to a clean change on the first changed observation.
The two-confirmation policy waited one more observation.

When an unresolved report interrupted a real change, the two-confirmation
policy waited three observations from the actual change before delivering the
new record. The unresolved report broke the consecutive sequence, so
confirmation had to begin again.

In the stable histories, that same caution prevented every false replacement.
Isolated or alternating opposite reports caused suspension, not a wrong active
record.

## What this supports

This supports a source-preserving computation of the safety-responsiveness
tradeoff. The current policy is conservative in a precise way: it exchanges
wrong active guidance for periods with no guidance.

The result also shows why “more cautious” is not a complete verdict. Withholding
a record can itself be costly, and unresolved observations can extend that cost
well beyond one step.

## Limits and next question

The five histories were authored examples, not samples from a measured noise
distribution. The hidden relation helped score the policies but never entered
their decisions. No clerk interpreted the reports, and no participant acted
under the intermediate states.

The next experiment should attach consequences to suspension. In a small
mirrored world, it should measure what happens when the runtime must choose
between acting with the current record, acting cold, holding, or spending
another exploration to resolve uncertainty. That comparison can test the cost
of caution instead of counting suspended steps as automatically safe.

## Audit details

- Model calls: 0
- Frozen specification SHA-256: `4a3a1f9a561573feca7139cae602641b72fba9d555c501a5a7d2d77b5f681a43`
- Packet SHA-256: `47a086e0fad8f4502ae8ad528a60b18099a210e359848d70250a5d5a6ffef694`
- Specimen verdict: `conforms`
- Finding: `tradeoff_exposed`
- Formation verdict: `null`
- Replay: exact deterministic reconstruction

The exact histories, public policy inputs, transitions, and scorer-only truth
fields are in [packet.json](packet.json).
