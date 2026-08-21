# Clerical source-support verifier

Status: **frozen before contact under the session-wide human authorization**.

## Question

Can the restricted 4B clerical model judge whether a proposed two-control
record follows from its exact sensory source?

The verifier receives no later device, controls, position, target, action
request, expected action, or score. It receives only one retained sensory
report and one proposed effect record.

## Why this test follows

The source-completeness gate can reject a proposal when gauge movement is
missing. It cannot distinguish a correct record from its exact opposite when
both are attached to a complete source.

The verifier is a learned clerical instrument for that narrower semantic task.
It may label a proposal supported or unsupported. It may not repair the record,
write a replacement, select a later record, or advise the participant.

## Fixed cases

The test reuses four old occurrences and four contradictory counteroccurrences
from the completed learned revision exploration. Each lineage and design
contributes four pair types:

- an old complete sensory report with its correct old record;
- a counterexperience report with its correct revised record;
- that same counterexperience report with the stale opposite record; and
- a movement-hidden report with the complete-looking record the clerk wrote
  from it.

The first two pairs are source-supported. The last two are unsupported. The
labels do not enter the model prompt.

Each of the sixteen pairs is requested three times in a rotating schedule, for
48 logical calls. Valid outputs are never resampled. Up to eight transport
retries are allowed, for a physical ceiling of 56 attempts.

## Interface

The model receives the exact three-field sensory report and a record with
named effects for the first and second displayed controls. The system message
states the domain fact that exactly one control raises position and the other
lowers it.

The verifier must return exactly one JSON object:

```json
{"source_support":"supported"}
```

The only other allowed value is `unsupported`. A missing actuator or movement
must produce `unsupported`. A complete source supports a record only when the
selected control's claimed effect agrees with the observed movement and the
other control has the opposite effect.

## Prospective interpretation

The interface is not engaged unless at least 44 of 48 outputs are valid.

A `verifier_candidate` requires at least 11 of 12 correct labels in each of the
four pair types. This permits at most one false support for the stale class and
at most one false support for the missing-movement class.

Any engaged result that misses a class floor is `null`. A run below the valid-
output floor is `not_engaged`.

A candidate would justify adding this verifier as a comparison in a fresh
end-to-end revision validation. It would not by itself license automatic
admission. The same model family produced some of the proposals, and a learned
verifier can share its errors.

## Model and evidence

The verifier is
`huggingface.co/qwen/qwen3-4b-gguf:Q4_K_M` with digest
`sha256:618c80458ca4012b132ef1847bcd49ec5f923c3d9df35fdc534715085108e9f3`.

The fixed source packet is
`evidence/learned-clerical-revision-20260820T174848Z/packet.json` with SHA-256
`9387ac057bebe2fb1ca422e268f470dc8d424a6b9577dbcf8799665abc2bec7f`.

Evidence is written under
`evidence/clerical-source-support-verifier-<run-id>/`. Every raw request and
response is retained and replayed before successful exit. Formation remains
outside the claim ceiling.
