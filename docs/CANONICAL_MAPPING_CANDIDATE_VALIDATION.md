# Canonical mapping candidate validation

Status: **frozen before contact; this specification permits one bounded
candidate validation under the session-wide human authorization**.

## Question

Can two fresh consequential experiences cause the same cold model to author
correct controller-family mappings that improve repeated action on new devices,
beat cold, raw, result-withheld, and delivery-ablation controls, and avoid harm
when an exact public-family governor withholds each candidate from a different
family?

This validation is narrower than Formation. It tests acquisition,
consequence-dependent authorship, near transfer, selectivity, and declared
causal edges. It does not test later counterevidence, revision, suspension, or
revocation. The Formation verdict therefore remains null regardless of outcome.

## Model and interface

- Model: `ai/qwen3:14B-Q6_K`
- Artifact digest:
  `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Provider: Docker Model Runner at the existing llama.cpp chat-completions
  endpoint
- Action settings: temperature `0.6`, top-p `0.95`, JSON-object response
  constraint, and 32 completion tokens
- Authorship settings: temperature `0.6`, top-p `0.95`, and 128 completion
  tokens

Every invocation is cold. No provider conversation identifier or prior model
output exists outside the exact request retained for that call.

## Two replicated worlds

Both source families have the hidden mapping “first decreases, second
increases.” Their identifiers, devices, and action strings are fresh. Their
acquisition target directions are opposite, so one observed result identifies
the first slot and the other identifies the second slot.

Each world has three prospective later cases:

1. a new same-family device whose target is one position above;
2. a new same-family device whose target is one position below; and
3. a new device from a world-local opposite-profile family whose first slot
   increases and whose target is above.

The other-family case is a non-transfer case. The runtime never receives the
case-family label or expected action.

## Shared acquisition and authorship fork

Each world makes one acquisition action with no retained material. The
environment applies the committed proposal and records selected slot, movement
direction, resulting position, and target status.

The same occurrence then feeds two model-authorship calls:

- **result exposed** receives the exact environment result;
- **result withheld** receives a fixed public withheld sentinel instead.

Both calls use one generic sentence grammar: describe the first displayed slot,
then the second. The grammar supplies no realized family mapping or later
action string. Returned text is retained and later delivered without repair.

## Later branches

Each world runs seven branches on all three later cases with six byte-identical
repeats per branch-case:

1. **Cold** receives no retained material.
2. **Raw** receives the exact acquisition occurrence and external result.
3. **Authored ungated** receives the result-exposed candidate on every case.
4. **Governed** admits the result-exposed candidate under an origin-family
   scope and delivers it only when the current public family exactly matches.
5. **Delivery ablation** has the same result-exposed candidate and scope but a
   public ablation prevents every delivery.
6. **Consequence-withheld governed** applies the same exact-family policy to
   the result-withheld candidate.
7. **Oracle static scoped** is a disclosed diagnostic ceiling. It delivers the
   correct first-then-second mapping only on matching-family cases. This branch
   is not credited as model development.

The governor compares exact public controller-family strings. It does not read
the hidden mapping, expected action, case label, or candidate prose. The
authored and delivery-ablation branches retain the same candidate identity;
only the declared delivery edge differs.

## Budget and stopping rule

- Acquisition calls: 2
- Authorship calls: 4
- Later calls: 2 worlds × 7 branches × 3 cases × 6 repeats = 252
- Logical-call budget: 258
- Physical-attempt ceiling: 266
- Total transport retries: at most 8, one retry per affected logical call

Malformed, refused, and unavailable outputs remain in their assigned
denominators. The runner stops at the fixed schedule or physical ceiling.
Evidence is written under `evidence/canonical-mapping-candidate-validation-<run-id>/`
and regenerated from raw attempts before completion.

## Frozen scorer

The candidate-validation class is one of `supported`, `null`, `harmful`,
`not_engaged`, or `invalid`. The full Formation verdict remains null.

The packet is `invalid` if model identity, frozen specimen, request replay,
branch construction, environment physics, or evidence regeneration fails.

It is `not_engaged` if either result-exposed candidate is unavailable or is not
the exact correct canonical mapping, or if the oracle-static diagnostic scores
fewer than 5/6 correct on any same-family case.

It is `harmful` if governed delivery scores at least three fewer correct actions
than cold on either non-transfer case.

It is `supported` only if every condition below holds in both worlds:

- governed delivery scores at least 5/6 correct on each same-family case;
- governed delivery exceeds cold, raw, delivery ablation, and
  consequence-withheld governed by at least four correct actions on each
  same-family case;
- governed non-transfer correctness is no more than one below cold;
- governed delivery exceeds authored ungated by at least four correct actions
  on the non-transfer case; and
- every later branch-case has at least five valid actions.

If the mechanism engages without meeting `supported` or `harmful`, the result
is `null`.

## Claim ceiling

A supported result would validate this exact candidate mechanism for two
opaque-control acquisition worlds and their prospective cases. It would not
show far transfer, revision, cumulative development, net product value, or a
general Formation effect. A null, harmful, not-engaged, or invalid result closes
only this frozen candidate validation.
