# A catalog caused costly probes even when it covered nothing

## Main result

The participant paid for the diagnostic whenever it received a signal catalog,
even when the device's public alphabet had no match in that catalog. Learned,
supplied, and reversed catalogs each caused six of six costly probes on both
covered and uncovered devices.

On covered devices, the learned and supplied catalogs then completed all six
tasks. Reversed records failed all six. On uncovered devices, the empty
post-probe receipt caused all three costly catalog branches to hold. The device
was safe, but the service window had already been consumed for information the
catalog could not use.

The frozen exploratory verdict is `harmful`. Record presence, not record
coverage, drove the first action. Formation remains null.

## The comparison

Every initial request published:

- the two opaque task controls;
- the diagnostic control;
- both signals the diagnostic could emit;
- whether the diagnostic would consume the service window; and
- the exact retained material for that branch.

The current signal and valid task control remained hidden. First-action task or
hold ended the episode. Diagnostic action opened one final request containing
the environment result and an exact-match receipt.

The 72 episodes crossed two public alphabets, two hidden profiles, three
repeats, and six conditions: learned, removal, supplied, and reversed catalogs
under cost, plus learned and removal with a free diagnostic. At most two calls
were allowed per episode.

## First action under cost

| Retained material | Covered probes | Uncovered probes | Direct guesses | First-action holds |
| --- | ---: | ---: | ---: | ---: |
| Learned catalog | 6/6 | 6/6 | 0 | 0 |
| Supplied catalog | 6/6 | 6/6 | 0 | 0 |
| Reversed catalog | 6/6 | 6/6 | 0 | 0 |
| Learned catalog removed | 3/6 | 0/6 | 9 | 0 |

The correct and reversed catalogs had the same covered probe rate, satisfying
the prediction that correctness should not govern the first action. The more
important coverage prediction failed: every catalog also attracted every
uncovered probe.

Removal behaved differently across the two signal alphabets. It probed three
of six covered cases but no uncovered case. Because neither removal request
contained records, that difference cannot be attributed to retained knowledge.
It is evidence that the `steady_pattern` and `pulsed_pattern` names themselves,
or another alphabet-specific feature, affected the first action. The frozen
removal-crossing check correctly rejected the interaction claim.

No branch held on the first action. When removal did not probe, it guessed a
task control directly. Those nine direct guesses completed four tasks and
failed five.

## Free-probe engagement

Both free branches probed all twelve covered and uncovered episodes. The
engagement condition therefore passed: the model still used the diagnostic
when its service-window cost was absent.

This also exposed a second interface effect. After a free probe returned an
empty receipt, the learned and removal branches each guessed in all six
uncovered cases and failed three. After a costly probe returned the same empty
match fact, the learned, supplied, and reversed branches held in all eighteen
uncovered cases.

The post-probe result therefore replicates safe empty-receipt behavior only in
the costly state. It does not repair the first action, and it is not stable
across the free and costly interfaces.

## Record use after a covered probe

| Retained material | Completed | Failed |
| --- | ---: | ---: |
| Learned catalog | 6/6 | 0/6 |
| Supplied catalog | 6/6 | 0/6 |
| Reversed catalog | 0/6 | 6/6 |

The learned and supplied initial requests were byte-identical in all twelve
paired cells. Their outcomes also matched. Reversal changed every second
action outcome without changing the covered first action. The participant used
the selected record's meaning after the probe.

## What this supports

The experiment separates three facts that the earlier free world merged:

- A catalog made the diagnostic look worth taking.
- The participant did not determine before action whether that catalog covered
  the published alphabet.
- An empty receipt could stop the later guess after the cost had already been
  paid, but only in the costly interface.

The result is not a knowledge-by-coverage interaction. It is a narrower
representation failure: publishing the alphabet and catalog separately did not
make their exact set relation behaviorally available before action.

## What this does not support

The run does not show that learned records improve information-seeking. Learned
and supplied catalogs were byte-identical, and both caused the same useful and
useless probes. It does not show a general failure to reason about cost; removal
behaved differently under costly and free diagnostics, but confounded that
difference with alphabet-specific behavior and direct guessing.

The next narrow question is whether the runtime must expose its exact
pre-action coverage computation, just as the post-probe receipt exposed an
exact signal match. Such a receipt could list which published signals have
matching record IDs and which do not. It must not recommend probing or holding,
and reversed records must still appear fully covering.

## Audit details

- Participant model: `ai/qwen3:14B-Q6_K`
- Participant digest: `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Episodes: 72
- Logical calls: 135 of a ceiling of 144
- Physical attempts: 135 of a ceiling of 156
- Retries: 0
- Instrument packet SHA-256: `d302ae1eb6fa1cd5034de639ce189bd5d48ba705064548205af0d88723492708`
- Learned-record packet SHA-256: `4c7bf10b7ea53abe4f1a9b4ddd477674b07101fc92139c37ed9abc2c2a06f005`
- Receipt packet SHA-256: `ff828090bd36dbafcf82c9b95922cba5898d43d1111d3caecbe11e31546e7e26`
- Frozen specimen SHA-256: `1aa9df6e2a6da6b3b4aa9fa7f7eec18b591e43901b6d38a6846a4caf29e6facc`
- Packet SHA-256: `7c56a0b7d08ad6e6c5a51ae4a5f4c4cc9b2ea4c1517faa2f62c08e2e25862374`
- Frozen verdict: `harmful`
- Replay: exact from retained requests and responses
- Formation verdict: `null`

The exact prospective contract is in [specimen.json](specimen.json). The
complete calls, episodes, external consequences, comparisons, and verdict are
in [packet.json](packet.json). The exact model and interface receipt is in
[provider.json](provider.json).
