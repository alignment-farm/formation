# Clerical selected-effect projection

## Main result

The restricted 4B clerk copied the requested record field exactly on all 48
calls. It handled both actuator positions, both effect values, correct records,
stale opposite records, and records written from hidden movement. The frozen
verdict is `projection_candidate`.

This repairs the specific comparison failure by decomposition. It does not yet
establish that the combined admission mechanism is correct or that an admitted
record improves action. Formation remains null.

## The task

Each request contained an `observed_actuator` value and a proposed record with
one named effect for each control. If the actuator was `first`, the clerk had to
copy `first_control_effect`. If it was `second`, it had to copy
`second_control_effect`.

The clerk did not see gauge movement or decide whether the record was
supported. It did not see a later device, action controls, position, target,
expected answer, or score.

The sixteen exact source-record pairs from the failed verifier were each
requested three times. This retained the hard stale and missing-measurement
inputs while removing the broad judgment that had failed.

## What happened

| Original pair type | Exact projections |
| --- | ---: |
| Correct old record | 12/12 |
| Correct revised record | 12/12 |
| Stale opposite record | 12/12 |
| Complete-looking record from hidden movement | 12/12 |

The field combinations were also exact:

| Observed actuator and copied value | Exact |
| --- | ---: |
| First, decreases position | 9/9 |
| First, increases position | 9/9 |
| Second, decreases position | 12/12 |
| Second, increases position | 18/18 |

All outputs had the required JSON shape. There were no retries or unavailable
calls.

## What this supports

The result supports one narrow learned clerical operation: selecting a named
field from a proposed record. The failed verifier tried to combine source
availability, field selection, and semantic comparison in one judgment. This
experiment shows that field selection itself is reliable on the retained set.

A composed gate can now use separate checks:

1. The retained source must contain actuator and movement measurements.
2. The sensory transcription must match those retained measurements.
3. The projector must copy the proposed effect for the transcribed actuator.
4. The copied effect must equal the transcribed observed effect.

Those checks preserve model authorship of the measurement and record fields.
The runtime performs provenance checks and exact equality rather than asking a
model for an unrestricted trust judgment.

## What this does not support

This is a field-copying result. It does not show that the original sensory
transcription is always true, that a whole record should be admitted, or that
later behavior benefits.

The cases come from one small deterministic domain and one retained revision
experiment. The next step is a zero-call composition diagnostic over the exact
retained source, transcription, record, and projection bytes. A later fresh
behavioral validation is still required.

## Audit details

- Clerical model: `huggingface.co/qwen/qwen3-4b-gguf:Q4_K_M`
- Model digest: `sha256:618c80458ca4012b132ef1847bcd49ec5f923c3d9df35fdc534715085108e9f3`
- Logical calls: 48
- Physical attempts: 48
- Valid outputs: 48
- Exact projections: 48
- Retries: 0
- Frozen specification SHA-256: `9e0ebd85647f43f067c4cde0a18b8829b7461fb443bff08bfe26f58392b1c3d0`
- Specimen SHA-256: `da533e21e49101bc834e94cd8116c99f467d1e0398b3ab7b918d2c86995993bd`
- Packet SHA-256: `00eb809394b53f813635846252a07ff046e9e78dcfeb781dd170ef5d8437756f`
- Frozen projection verdict: `projection_candidate`
- Formation verdict: `null`
- Replay: exact from retained request and response bytes

The computed calls are in [packet.json](packet.json). The fixed field cases are
in [specimen.json](specimen.json). The exact model identity is in
[provider.json](provider.json). Every raw request and response is under
`attempts/`.
