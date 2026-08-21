# Composed clerical record admission

## Main result

The composed admission mechanism passed its deterministic diagnostic. It
admitted all 24 retained calls containing a correct old or revised record. It
quarantined all 24 calls containing a stale opposite record or a claim based on
hidden movement. The frozen verdict is `conforms`.

No model was called. The diagnostic composes model outputs that were already
retained. It establishes the behavior of the admission checks on those bytes,
not fresh clerk reliability or later action benefit.

## How the mechanism works

The failed verifier tried to answer one broad question: “Does this record
follow from this source?” The composed mechanism splits that question into
small, inspectable checks.

First, the exact sensory source must contain a selected actuator and a gauge
movement. The clerk's sensory transcription must copy both facts exactly.

Second, the record must contain one opposite effect for each named control. A
separate clerk call copies the proposed effect field for the transcribed
actuator. The runtime compares that copied claim with the transcribed observed
effect.

The models write every semantic field. The runtime checks exact source
bindings, field shape, and equality. It does not fill a missing value, repair a
record, inspect later action, or select the effect that should pass.

## What happened

| Proposed record and source | Admitted | Quarantined | Reason when rejected |
| --- | ---: | ---: | --- |
| Correct old record with complete old source | 12/12 | 0/12 | — |
| Correct revision with complete counterexperience | 12/12 | 0/12 | — |
| Stale opposite record with complete counterexperience | 0/12 | 12/12 | Claimed effect differed from observed effect |
| Complete-looking record with movement hidden | 0/12 | 12/12 | Movement was missing |

Every request, response, sensory transcription, proposed record, and source
occurrence matched its retained hash. Correct revisions made version 2 active.
Rejected revision attempts left version 1 active.

Tamper tests also changed the projector output and sensory transcription. Each
change caused quarantine rather than a repaired value.

## What this supports

The result supports the composed mechanism on the retained evidence. It fixes
both defects exposed by the preceding experiments: a plausible clerk output
cannot manufacture a missing measurement, and a stale opposite record cannot
pass merely because all fields are present.

The result also shows a useful role for the second model. It performs narrow
semantic extraction and field projection. Deterministic code binds sources and
compares the model-written fields. Neither part must take over the
participant's action reasoning.

## What this does not support

This is a replay over retained outputs. It does not show that a fresh sensory
transcription, record, and projection chain will remain exact. It also does not
show that admitted revisions improve a fresh participant or preserve unrelated
behavior.

The next experiment should run the complete mechanism on fresh lineages. It
must compare admitted revisions with cold, raw, stale, hidden, removed, and
supplied paths. It must also retain rejected proposals and prove that
quarantine, rather than deletion or repair, prevents their influence.

Formation remains null.

## Audit details

- New model calls: 0
- Revision packet SHA-256: `9387ac057bebe2fb1ca422e268f470dc8d424a6b9577dbcf8799665abc2bec7f`
- Projection packet SHA-256: `00eb809394b53f813635846252a07ff046e9e78dcfeb781dd170ef5d8437756f`
- Frozen specification SHA-256: `93523a5c17b34da171f4b03957ab6382acd6a257fa2ca4cb125271195bc76f8a`
- Diagnostic specimen SHA-256: `f57f23c1e1d7d14cd3cb141d1e33098cb67870778f1aa26e2c1f16b223e3cf9b`
- Packet SHA-256: `f8abcdbc8a4ae16f92731ea911d059b9a27abbe6995dc8db8ecfa2c53bf6e2d3`
- Frozen verdict: `conforms`
- Formation verdict: `null`
- Replay: exact deterministic replay from retained source and projection bytes

The decisions and reason codes are in [packet.json](packet.json). The fixed
source hashes and check sequence are in [specimen.json](specimen.json). The
model requests and responses remain in the linked
[revision](../learned-clerical-revision-20260820T174848Z/README.md) and
[projection](../clerical-selected-effect-projection-20260820T181202Z/README.md)
evidence.
