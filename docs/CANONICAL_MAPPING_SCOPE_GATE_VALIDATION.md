# Canonical mapping scope-gate successor validation

Status: **frozen before contact under the session-wide human authorization**.

## Question

Does exact public-family gating preserve the two acquired candidates' benefit
on new matching-family devices while preventing their prospectively identified
downward-target harm on new nonmatching families?

The candidates and source families are bound to the completed two-world
candidate validation. This successor does not repeat or rescore acquisition.
It validates only the later delivery gate.

## Comparison

Each source lineage receives four fresh cases: matching-family target above,
matching-family target below, nonmatching-family target above, and nonmatching-
family target below. The nonmatching family has the opposite controller
profile. Every case runs four byte-identical repeats under:

1. candidate ablation;
2. ungated exact candidate delivery; and
3. exact-family-scoped delivery.

The scope gate compares the current public controller-family string with the
candidate's acquisition-family string. It does not parse candidate prose or
receive case labels, expected actions, or hidden profiles.

The exact model and action interface remain unchanged. The budget is 96 logical
calls, a 100-attempt ceiling, and at most four transport retries. Evidence is
retained under `evidence/canonical-mapping-scope-gate-validation-<run-id>/` and
replayed from raw attempts.

## Frozen verdict

The scope-gate validation is `supported` only if both source lineages satisfy
all of these conditions:

- scoped delivery scores at least 3/4 on both matching-family cases;
- scoped delivery beats ablation by at least three actions on both matching-
  family cases;
- scoped and ungated matching-family correctness differ by at most one;
- scoped delivery is no more than one action below ablation on either
  non-transfer direction;
- scoped delivery beats ungated delivery by at least three actions on the
  downward non-transfer case; and
- every condition-case has at least three valid actions.

It is `harmful` if scoped delivery loses at least two actions to ablation on any
non-transfer case. It is `not_engaged` if ungated candidate delivery scores
fewer than 3/4 on either matching-family case. A replay, identity, branch, or
physics failure is `invalid`. Otherwise the verdict is `null`.

This verdict concerns only the delivery gate. Formation remains null because
revision, revocation, far transfer, and cumulative development are not tested.
