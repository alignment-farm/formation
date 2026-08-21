# Scoped candidate continuation evidence

This directory contains the completed 72-call continuation of the exact
model-authored mapping from the canonical-authorship contact. Three delivery
policies—candidate ablation, ungated delivery, and exact public-family-scoped
delivery—ran eight times on two new source-family devices and one new
opposite-profile device. The contact completed on 2026-08-19.

## Outcome

The candidate again changed both source-family action distributions from fully
wrong to fully correct.

| Case | Ablation | Ungated | Scoped |
| --- | ---: | ---: | ---: |
| Source family, target above | 0/8 | 8/8 | 8/8 |
| Source family, target below | 0/8 | 8/8 | 8/8 |
| Other family, target above | 8/8 | 8/8 | 8/8 |

Scoped and ungated delivery had identical actions on all 24 corresponding
calls. Scoped delivery differed from ablation by total variation distance
`1.0` on both source-family cases and `0.0` on the other-family case. Every
call returned a valid action.

## What this says

The beneficial source-family effect transferred to a second prospective pair
of devices with new action strings. Across this continuation and its source
contact, delivered model-authored mapping was 32/32 correct on new
source-family actions while ablation was 0/32.

The gate did not earn causal credit in this packet. Ungated delivery had caused
complete negative transfer in the source contact, but it caused no change on
this new other-family request. Because ungated and scoped actions were equal,
the observed selectivity could come from the cold model reading the candidate's
family scope rather than from governance withholding it.

The candidate phenomenon is now repeated, but its non-transfer behavior is
mixed. A stricter comparison should use fresh replicated acquisition worlds,
consequence-exposed and result-withheld authorship, cold and raw baselines,
delivery ablation, exact family governance, prospective same-family transfer,
and opposite-profile non-transfer. The verdict must remain narrower than
Formation because revision is not yet tested.

## Integrity and cost

- Model: `ai/qwen3:14B-Q6_K`
- Artifact digest:
  `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Protocol: `scoped-candidate-continuation-v1`
- Logical calls: 72/72
- Physical attempts: 72/76
- HTTP 200 responses: 72
- Retries: 0
- Valid actions: 72/72
- Prompt tokens reported by the provider: 22,952
- Completion tokens reported by the provider: 1,950
- Elapsed packet time: about 84 seconds

The directory contains the provider receipt, canonical specimen and packet,
and the exact request, response, and metadata files for every attempt. The
runner replayed the packet from raw evidence before exiting successfully. The
terminal Formation and full-validation verdicts remain null.
