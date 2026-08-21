# Clerical source-support verifier

## Main result

The restricted 4B verifier did not reliably decide whether a complete effect
record agreed with its sensory source. It returned valid JSON on all 48 calls,
but accepted 9 of 12 stale records that directly contradicted the observed
movement. The frozen verdict is `null`.

The verifier did reliably reject claims when movement was missing. That repeats
the simpler source-completeness distinction. It does not add the semantic check
needed for safe record admission.

No participant model was called. Formation remains null.

## The task

The verifier received one sensory report and one proposed record. For example,
the report might say that the first displayed actuator was engaged and the
gauge fell. A supported record must then say that the first control decreases
position and the second increases it.

The test used four kinds of pair. An old report was paired with its correct old
record. A contradictory counterexperience was paired with its correct new
record. The same counterexperience was also paired with the stale opposite
record. Finally, a movement-hidden report was paired with the complete-looking
record written from that incomplete source.

Each of the sixteen exact pairs was requested three times. The model saw no
later controls, position, target, action request, expected action, class label,
or score.

## What happened

| Source and proposed record | Correct labels | Model labels |
| --- | ---: | --- |
| Complete old source with correct old record | 12/12 | 12 supported |
| Complete counterexperience with correct revision | 12/12 | 12 supported |
| Complete counterexperience with stale opposite record | 3/12 | 9 supported, 3 unsupported |
| Movement-hidden source with complete-looking claim | 12/12 | 12 unsupported |

All 48 responses had the required JSON shape. There were no unavailable calls
or retries.

The stale result was stable rather than random. One of the four exact stale
pairs was labeled unsupported on all three repeats. The other three were
labeled supported on all three repeats.

## What this supports

The model can follow the verifier interface. It also distinguishes an absent
measurement from a present one in these cases.

The result localizes the failure. The model mostly treated a complete sensory
report plus a complete record as sufficient. It did not reliably bind the
observed movement to the specifically selected control field.

## What this does not support

This model output cannot govern semantic record admission. Doing so would admit
most of the stale opposite records in the tested set.

The next bounded instrument can split the failed comparison. The clerk can be
asked only to copy the proposed effect for the observed actuator into one named
field. The runtime can then compare that field with the separately transcribed
observed movement. This keeps semantic extraction with the clerk while leaving
the runtime one exact equality check. The existing source-completeness gate
still blocks missing measurements before that comparison.

This was a verifier-interface experiment, not a behavioral or Formation
result.

## Audit details

- Verifier model: `huggingface.co/qwen/qwen3-4b-gguf:Q4_K_M`
- Model digest: `sha256:618c80458ca4012b132ef1847bcd49ec5f923c3d9df35fdc534715085108e9f3`
- Logical calls: 48
- Physical attempts: 48
- Valid outputs: 48
- Retries: 0
- Frozen specification SHA-256: `194af5048ced35e4e5a02ac31c4bdd8d82f65c4789882ca54d1a8b958ab1ca47`
- Specimen SHA-256: `39dc2f262cc6b764289319fb632e80a139103e939044ca8df716514d681e0db7`
- Packet SHA-256: `ef388dc519dca042aa858534b0d9290cfd82f09efcd794fae4df14a3b22d71e1`
- Frozen verifier verdict: `null`
- Formation verdict: `null`
- Replay: exact from retained request and response bytes

The computed calls and labels are in [packet.json](packet.json). The fixed
pairs and request hashes are in [specimen.json](specimen.json). The exact model
identity is in [provider.json](provider.json). Every raw request and response is
under `attempts/`.
