# Contested counterevidence accumulation

## Main result

The deterministic specimen conforms. It keeps every source occurrence intact
and distinguishes four counterevidence histories without model calls or hidden
truth labels.

| History | Governance state |
| --- | --- |
| Two consistent contradictions | `superseded` |
| Contradiction followed by support for current record | `current_retained` |
| One uncorroborated contradiction | `suspended_pending_corroboration` |
| Contested movement | `suspended_unresolved` |

Formation remains null.

## What the specimen does

The current record says the first control increases position. Each occurrence
retains its own source, order, selected control, movement status, movement,
proposed record, and composed-admission status.

Two complete first-control decreases supporting the same opposite proposal
supersede the current record. One such decrease followed by a complete increase
closes the first contradiction as uncorroborated and keeps the current record.
A lone complete decrease suspends activation while awaiting another occurrence.
A contested movement suspends activation without treating missing direction as
a vote for either record.

Every decision cites all considered occurrences and separately preserves the
supporting, contradicting, closed, and unresolved subsets. The governor derives
a state from the receipts; it does not replace them with a summary count.

## What this supports

This supports one deterministic governance computation for accumulating
observational counterevidence. It supplies a boundary that the learned clerk
can be tested against later: a single contradictory observation need not
immediately replace current practice, while repeated consistent observations
can warrant supersession.

The policy also represents uncertainty as state. Suspension does not claim
that the current or proposed record is true. It prevents unresolved evidence
from silently becoming ordinary influence.

## Limits

The histories and proposal records are fixture values. No clerk wrote them, no
participant consumed the resulting states, and no environment established that
this two-occurrence threshold is optimal. The specimen does not measure later
behavior, costs, real noise, or Formation.

The next live question is whether the restricted clerk can produce consistent
source-bound proposals across several occurrences and whether these governance
states produce the intended later activation, suspension, and recovery
contrasts.

## Audit details

- Model calls: 0
- Frozen specification SHA-256: `05654b6e3af8c2444b38eb62bf617ab444c65a2ddf71e9a2154f802469c0c1a5`
- Packet SHA-256: `0949c2f98049e29d4fff91e9ea4b0e33b9d9796e8a425f2da49ce11e286d21a3`
- Specimen verdict: `conforms`
- Formation verdict: `null`
- Replay: exact deterministic reconstruction

The exact histories, occurrence receipts, decisions, and source subsets are in
[packet.json](packet.json).
