# Explicit-consequence contact: observed record

Explicit environment facts repaired candidate authorship but only partly
changed later action. In the counter-prior world, the model correctly authored
and the runtime admitted `second` as the increasing slot. Authored and governed
offers then corrected later increase actions, while raw occurrence did not.
The same correct candidate failed to correct later decrease actions.

This is the first exploratory later-behavior difference in Formation that raw
persistence did not reproduce. It is narrow, asymmetric, and still compatible
with an ordinary prompt-content effect. It is not a Formation or transfer
finding.

## Execution receipt

The contact ran on 2026-08-17 under the frozen
[charter](../../docs/EXPLICIT_CONSEQUENCE_CONTACT.md) with
`ai/qwen3:14B-Q6_K`, artifact digest
`sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`,
and Docker Model Runner 1.2.6.

All 69 planned logical calls completed in 69 physical attempts. Every response
was HTTP 200 and ended normally. Every actor response contained one permitted
action. There were no retries, repairs, or within-cell disagreements. The
provider reported 20,109 prompt tokens and 917 completion tokens.

## Acquisition and interpretation

The acquisition actor again chose the first listed control in both worlds.

- In World C, `tess` selected the first slot and position increased from 0 to
  1. The model authored `first`; the runtime independently derived `first` from
  the explicit fields and admitted the candidate.
- In World D, `coro` selected the first slot and position decreased from 0 to
  -1. The model authored `second`; the runtime independently derived `second`
  and admitted the candidate.

Unlike the prior contact, the World D interpretation no longer preserved the
first-slot prior. The environment result stated only `selected_slot: first` and
`movement_direction: decreased`; it left the opposite-slot conclusion to the
model. The governor used those same two fields and did not fall back to numeric
subtraction or the hidden profile.

## Later behavior

Every table entry is the number of exact expected-action matches out of two
cold repetitions.

| World and relation | No persistence | Raw occurrence | Authored interpretation | Governed candidate |
| --- | ---: | ---: | ---: | ---: |
| C: same-family increase | 2/2 | 2/2 | 2/2 | 2/2 |
| C: same-family decrease | 2/2 | 2/2 | 2/2 | 2/2 |
| C: unobserved family | 0/2 | 0/2 | 0/2 | 0/2 |
| C: already current | 2/2 | 2/2 | 2/2 | 2/2 |
| D: same-family increase | 0/2 | 0/2 | 2/2 | 2/2 |
| D: same-family decrease | 0/2 | 0/2 | 0/2 | 0/2 |
| D: unobserved family | 0/2 | 0/2 | 0/2 | 0/2 |
| D: already current | 2/2 | 2/2 | 2/2 | 2/2 |

For World D increase, no persistence and raw occurrence chose the first control,
`ivar`, which moved away from the target. The exact model-authored candidate
said `increasing_slot: second`. Authored and governed offers then chose the new
second-control token, `juno`, and reached the target in both repetitions.

For World D decrease, all four conditions chose the second-control token,
`loro`, although the correct action was the new first-control token, `kavi`.
The candidate was present and the runner's pre-inference delivery flag was true
in both governed repetitions. That historical `activated` field records
delivery authorization, not attributable activation. The model used “second
increases” as a direct positive cue when increase was needed but did not use its
binary inverse when decrease was needed.

Raw occurrence matched no persistence in every later cell. Authored and
governed behavior also matched one another in every cell. On unobserved-family
decoys, every condition guessed the first control instead of requesting
calibration; one mirrored guess happened to reach the target, but both were
classified as unwarranted. Every condition held on already-current states.

## What this contact located

The causal chain is now separated more sharply:

```text
external consequence
  -> correct model-authored candidate
  -> transition-grounded admission
  -> scope-matched delivery
  -> partial later behavioral difference
```

The first four events are present in the record. Later influence is partial:
the same candidate changes the increasing decision but not the decreasing
decision that follows from the same two-slot relation. Candidate correctness,
admission, and availability therefore do not imply complete rule execution.

The next hard problem is **availability-to-influence semantics**. A declarative
candidate can be treated as a salient action cue rather than as a bidirectional
decision procedure. Formation now needs to ask what model-authored change can
carry a relation into practice without the runtime or harness writing the
case-specific policy on the model's behalf.

The contact does not show governance value. Governed and always-authored offers
were identical on applicable cases, and gating did not change behavior on
non-applicable cases because the cold baseline already guessed or held. Fresh
work must preserve raw persistence as a serious comparator and make a named
governance edge causally testable.

Representation iteration is closed. The environment has already made the
decisive facts explicit. Adding the inferred inverse, a case-conditioned action
table, or another prompt repair would move the missing practice competence into
the apparatus.

## Claim boundary and integrity

Two repetitions per cell cannot estimate stable rates. Every nonempty offer is
request text. The World D increase difference remains compatible with ordinary
semantic prompting and does not establish hidden model change, transfer,
selectivity, governance benefit, or durable formation.

The evidence directory retains the protocol, provider receipt, exact
acquisitions, interpretations, governance receipts, null `formation_verdict`,
and all per-call records. A post-run audit recomputed SHA-256 digests for all
138 stored request and response artifacts with no mismatch. Serialized model
requests contain no world, probe, relation, offer, expected-action, or verdict
labels.
