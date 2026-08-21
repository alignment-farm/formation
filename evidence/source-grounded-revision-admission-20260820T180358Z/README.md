# Source-grounded revision admission

## Main result

The deterministic admission rule passed its fixed diagnostic. It admitted all
four clerk proposals whose exact sensory requests contained both the selected
actuator and gauge movement. It quarantined all four proposals whose requests
said that gauge movement was unavailable. In those hidden cases, the old
record stayed current.

No model was called. This result establishes one provenance check in the
substrate. It does not establish that an admitted clerk record is true.

## The rule

A complete-looking record is not enough. Before a proposed version may become
current, the runtime binds it to the exact sensory-request bytes and the exact
environment occurrence that produced those bytes. The request must contain an
observed actuator and an observed movement. The proposal must also have the two
named effect fields expected by the interface.

If a required measurement is missing, the runtime retains the proposal but
marks it quarantined. Chronology ignores quarantined proposals and leaves the
latest older eligible version active.

The rule does not compute whether the record would improve action. It does not
fill either effect field or compare the record with a future answer.

## What was tested

The diagnostic read the exact eight revision paths from the preceding live
experiment. Four clerk requests contained a selected actuator and an actual
rise or fall. Four parallel requests contained the actuator but said that
movement was unavailable.

All eight clerk outputs looked structurally complete. The diagnostic bound
each output to its retained sensory request and source occurrence before making
an admission decision.

| Source condition | Admitted | Quarantined | Active version |
| --- | ---: | ---: | ---: |
| Actuator and movement present | 4/4 | 0/4 | New version 2 |
| Movement missing | 0/4 | 4/4 | Old version 1 |

The same proposed record was also tested with a complete source and with a
missing-movement source. Its content hash stayed the same. The complete source
was admitted, and the missing source was quarantined.

## What this supports

The result supports a narrow source-completeness gate. A clerk cannot make a
missing measurement appear present merely by writing a plausible value. Exact
request and occurrence bindings also prevent a proposal from borrowing support
from another sensory event.

This repairs the specific hidden-consequence defect found in the revision
exploration. It does so without deleting the unsupported proposal or letting
the harness write a replacement record.

## What this does not support

A second comparator deliberately inverted a complete record while leaving its
source intact. The gate admitted both the original and inverted records. That
is expected: this mechanism checks whether the source measurements exist, not
whether the clerk interpreted them correctly.

The next instrument question is therefore semantic source support. A
restricted verifier can receive the sensory facts and a proposed record, but
no later action problem, and judge whether the claim follows from its source.
That verifier must distinguish a correct revision from a stale opposite record
as well as reject claims based on missing movement.

This diagnostic made no new participant or clerk calls. It provides no new
behavioral result and no Formation evidence.

## Audit details

- New model calls: 0
- Source revision packet SHA-256: `9387ac057bebe2fb1ca422e268f470dc8d424a6b9577dbcf8799665abc2bec7f`
- Source revision specimen SHA-256: `5bd2e2e82991312bdb03ad159711e7cf40e1bc47bcff84cce0fdad06658e2cfe`
- Frozen specification SHA-256: `41a236920b53d4deb69dcc60a563949aba922c4405c2ea583f4ca5ed3ee08d5b`
- Diagnostic specimen SHA-256: `df6b28a7a6389257e88771ddcc74b152386a8f84fcee9da2b52a0a191828d74a`
- Packet SHA-256: `c5e344827f157754b241074e9a67e6d3207a22deae8d9f9c5145e00bfb7eaad5`
- Frozen verdict: `conforms`
- Formation verdict: `null`
- Replay: exact deterministic replay from the retained revision evidence

The decisions are in [packet.json](packet.json). The fixed input hashes and
decision surface are in [specimen.json](specimen.json). The source model
requests and responses remain in the preceding
[revision evidence](../learned-clerical-revision-20260820T174848Z/README.md).
