# Calibration mechanism-discovery contact: observed record

The contact successfully created an information gap, but Qwen3 14B did not use
the contradictory experience. Its behavior was consistent with one fixed
assumption: the first listed control increases position and the second
decreases it. That assumption happened to fit World A and failed throughout
World B. Raw occurrence, authored interpretation, and governed availability did
not change a single later action relative to no persistence.

This is an exploratory information-use result, not a Formation verdict or a
general claim about Qwen.

## Execution receipt

The contact ran on 2026-08-17 under the frozen
[charter](../../docs/CALIBRATION_MECHANISM_DISCOVERY.md) with
`ai/qwen3:14B-Q6_K`, artifact digest
`sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`,
and Docker Model Runner 1.2.6 using its llama.cpp backend.

All 69 planned logical calls completed in 69 physical attempts. Every response
was HTTP 200 and ended normally. Every actor response contained one permitted
action. There were no retries, repairs, or within-cell disagreements. The
provider reported 19,244 prompt tokens and 890 completion tokens.

## Acquisition and candidate authorship

In both worlds, the acquisition actor chose the first listed control.

- In World A, `dax` moved position from 0 to 1. The model then authored
  `first` as the increasing slot. The runtime derived the same fact from the
  transition and admitted the candidate.
- In World B, `brin` moved position from 0 to -1 while the target was 1. The
  transition therefore identifies the second slot as increasing. The model
  nevertheless authored `first`. The runtime independently derived `second`
  and refused the candidate as `candidate_transition_mismatch`.

The refusal used only the public acquisition state, chosen action, and external
before/after result. It did not read the hidden environment profile.

## Later behavior

Every offer produced the same two actions in every cell. The counts below are
exact expected-action matches out of two repetitions.

| World and relation | No persistence | Raw occurrence | Authored interpretation | Governed candidate |
| --- | ---: | ---: | ---: | ---: |
| A: same-family increase | 2/2 | 2/2 | 2/2 | 2/2 |
| A: same-family decrease | 2/2 | 2/2 | 2/2 | 2/2 |
| A: unobserved family | 0/2 | 0/2 | 0/2 | 0/2 |
| A: already current | 2/2 | 2/2 | 2/2 | 2/2 |
| B: same-family increase | 0/2 | 0/2 | 0/2 | 0/2 |
| B: same-family decrease | 0/2 | 0/2 | 0/2 | 0/2 |
| B: unobserved family | 0/2 | 0/2 | 0/2 | 0/2 |
| B: already current | 2/2 | 2/2 | 2/2 | 2/2 |

In World A, the fixed first-increases assumption selected the correct new
control token for both target directions. In World B, it selected the wrong new
token for both directions. This remained true when the raw offer showed that
the first acquisition control moved from 0 to -1.

For both unobserved-family decoys, every condition guessed the first listed
control instead of choosing `request_calibration`. One guess moved away from
the target and the other happened to reach it because the hidden decoy profiles
were mirrored. Both were classified as `unwarranted_guess`; luck did not turn
an unsupported control into selective behavior.

All conditions chose `hold` on already-current states.

## What the governor did and did not show

The public transition check distinguished a supported candidate from a false
one. In World A it admitted and exposed the exact model-authored candidate on
same-family movement. In World B it refused the false candidate and exposed
`NONE` instead. On other-family and already-current cases, governed requests
were byte-identical to no-persistence requests.

This is mechanism conformance, not governance benefit. World A's cold baseline
already behaved as if the admitted fact were true. World B's cold baseline and
governed branch were identically wrong. The gate prevented a false candidate
from becoming eligible, but it did not improve action in this contact.

## What this contact located

The environment now supplies the missing information, changes later action
tokens, balances both calibration directions, and exposes unwarranted use on a
different family. The remaining blocker is **counter-prior consequence use**:
can an operational model turn a simple observed transition that contradicts
its default slot assumption into a later action policy?

For this model and prompt surface, the failure occurs before a governance-value
comparison can engage. The raw actor ignored the contradictory transition, and
the interpreter inverted it when authoring the candidate. More governance
machinery cannot repair a candidate that the model did not derive, and tuning
the harness to do that derivation would substitute runtime machinery for the
development under study.

The next bounded step is one disclosed operational substitution with a larger
already-installed model on the same consumed exploratory packet. That can show
whether the blocker is specific to this model setup or remains in the contact
surface. It is not admission, model ranking, or prospective validation.

## Claim boundary and integrity

Two repetitions per cell cannot estimate stable rates. The contact changes
later request content across mechanisms and cannot identify a hidden model
state. The result establishes no transfer, selectivity, negative transfer,
governance benefit, or superiority over static instruction.

The evidence directory retains the protocol, provider receipt, both exact
acquisition occurrences, both interpretation outputs, both governance receipts,
a null `formation_verdict`, and all per-call records. A post-run audit
recomputed the SHA-256 digests of all 138 stored request and response artifacts
and found no mismatch. Actor request settings had one exact shape. Serialized
model requests contained no world identifier, probe identifier, relation key,
offer key, expected action, or verdict label.
