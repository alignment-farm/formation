# Source-grounded revision admission

Status: **frozen before the deterministic diagnostic**.

## Problem

The learned revision exploration found that a clerk can write a complete-
looking effect record when a needed measurement is missing. The hidden clerk
was told that gauge movement was unavailable. It still claimed a movement in
all four cases, and the runtime treated those claims as possible new versions.

A record's shape therefore cannot decide whether its source supports it. The
runtime needs a separate admission rule before chronology may make the record
current.

## Proposed rule

Every clerk proposal is bound to the exact sensory request that produced it and
to the environment occurrence behind that request. The runtime reads only the
source receipt and the proposal's structural validity.

A proposed effect record is eligible only when:

- the sensory request identifies which displayed actuator was engaged;
- the sensory request reports that the gauge rose or fell;
- the proposal contains one named effect for each displayed control; and
- the proposal is linked to the exact retained sensory-request bytes.

If an actuator or movement measurement is missing, the proposal is retained as
quarantined evidence. It cannot supersede the old eligible version. A complete
source permits admission, but does not prove that the clerk interpreted the
source correctly.

The rule does not compare the proposal with an expected answer. It does not
infer the unobserved control effect, repair a proposal, inspect a future action
request, or score whether the proposal would help.

## Deterministic diagnostic

The diagnostic reads the exact retained packet and sensory requests from the
completed learned revision exploration. It evaluates the four exposed and four
hidden revision proposals.

The mechanism conforms only if:

- all four exposed proposals are admitted;
- all four hidden proposals are quarantined for missing movement;
- exposed chronology selects version 2 for all four record lineages;
- hidden chronology leaves version 1 active for all four lineages;
- the same complete-looking claim is admitted with a complete source and
  quarantined with a missing-movement source; and
- every decision binds the retained request hash and source-occurrence hash.

This diagnostic makes no model requests. It reuses model output only as fixed
input to a deterministic provenance test. Its result can establish that the
admission rule implements the stated boundary. It cannot establish that the
clerk is accurate, that admitted records help action, or that Formation has
occurred.

## Fixed input and evidence

The source is
`evidence/learned-clerical-revision-20260820T174848Z/`.

- Source packet SHA-256:
  `9387ac057bebe2fb1ca422e268f470dc8d424a6b9577dbcf8799665abc2bec7f`
- Source specimen SHA-256:
  `5bd2e2e82991312bdb03ad159711e7cf40e1bc47bcff84cce0fdad06658e2cfe`
- New model-call budget: 0
- Output: `evidence/source-grounded-revision-admission-<run-id>/`

The output must contain the frozen specimen, every decision, the computed
verdict, and an exact deterministic replay.
