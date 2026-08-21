# Clerical selected-effect projection

Status: **frozen before contact under the session-wide human authorization**.

## Question

Can the restricted 4B clerk copy the proposed effect for one named observed
actuator into a separate field?

The preceding verifier could detect missing measurements but accepted most
stale opposite records. This test removes the support judgment. It asks for one
clerical projection that a deterministic equality check can use later.

## Interface

Each request contains only:

- `observed_actuator`, whose value is `first` or `second`; and
- `proposed_effect_record`, with named effects for both displayed controls.

The clerk returns exactly one JSON object:

```json
{"claimed_selected_effect":"increases_position"}
```

The other allowed value is `decreases_position`. The clerk must choose the
field named by `observed_actuator` and copy that field's exact value. It does
not receive gauge movement, a support label, a later device, controls,
position, target, action request, answer, or score.

The runtime does not choose the projected effect. In a later composed
mechanism, it may compare this model-written field for exact equality with the
separately model-transcribed observed effect. The source-completeness gate must
run first so a hallucinated hidden measurement cannot support admission.

## Fixed cases and budget

The test reuses the sixteen source-record pairs from the failed verifier. They
cover correct old records, correct revisions, stale opposite records, and
complete-looking records written from hidden movement. Their support labels do
not enter this task.

The selected field covers both first and second actuators and both possible
effects. Every exact pair is requested three times in a rotating schedule, for
48 logical calls. Valid outputs are never resampled. Up to eight transport
retries are allowed, for a physical ceiling of 56 attempts.

## Prospective interpretation

The interface is not engaged unless at least 46 of 48 outputs are valid.

A `projection_candidate` requires at least 46 exact projections overall, at
least 11 of 12 in each original pair class, and no more than one error in each
observed-actuator by claimed-effect combination.

An engaged result that misses these floors is `null`. A result below the valid-
output floor is `not_engaged`.

A candidate would support composition with the already conforming source-
completeness gate and an exact comparison against the model-written observed
effect. It would not establish that the whole admission mechanism is safe or
that later action improves.

## Model and evidence

The clerk is
`huggingface.co/qwen/qwen3-4b-gguf:Q4_K_M` with digest
`sha256:618c80458ca4012b132ef1847bcd49ec5f923c3d9df35fdc534715085108e9f3`.

The fixed source packet is
`evidence/learned-clerical-revision-20260820T174848Z/packet.json` with SHA-256
`9387ac057bebe2fb1ca422e268f470dc8d424a6b9577dbcf8799665abc2bec7f`.

Evidence is written under
`evidence/clerical-selected-effect-projection-<run-id>/`. Every raw request and
response is retained and replayed before successful exit. Formation remains
outside the claim ceiling.
