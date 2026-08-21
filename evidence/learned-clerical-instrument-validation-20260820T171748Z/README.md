# Learned clerical instrument validation

## Main result

The fresh two-model instrument passed its frozen validation. The full
consequence-exposed pipeline made all 48 matching actions and preserved
unrelated behavior at the cold score. The frozen learned-instrument verdict is
`supported`.

This is a bounded result about the substrate around a cold participant. It is
not a Formation finding.

## The task

A 14B participant acted on source devices and received an environment result.
A separate 4B clerk saw only a restricted sensory account: two visible design
features, which displayed actuator had been used, and whether the gauge rose or
fell.

The clerk transcribed that account, stated both control effects in prose, and
parsed those explicit facts into named fields. A deterministic serializer put
the fields into a sentence form the participant had already shown it could
use.

For each later device, the clerk saw only its visible description and returned
two normalized features. The runtime compared both model-written feature
fields for exact equality. On a complete match it delivered the exact rendered
sentence to a new cold participant call.

The clerk never saw the later controls, position, target, action request,
expected action, or score.

## What changed and what stayed fixed

Four independent lineages each contained two source designs with opposite
control effects. The same visible features had opposite effects in different
lineages, so a feature name alone could not determine the answer.

Every later device used fresh family, device, position, and control strings.
Matching devices shared both visible features with a source. Unrelated devices
were either wholly novel or recombined one feature from each source.

A consequence-hidden clerk received the same selected actuator but not the
gauge movement. A removal branch computed the exposed instrument but withheld
its selected sentence before action. Other branches supplied raw reports, both
sentences without selection, or known-correct sentences.

## Component results

| Component | Exact |
| --- | ---: |
| Consequence-exposed sensory transcriptions | 8/8 |
| Prose accounts containing both effects | 8/8 |
| Parsed named-effect records | 8/8 |
| Fixed-order rendered sentences | 8/8 |
| Later device normalizations | 24/24 |
| Exact structural selections | 24/24 |
| False selections on novel or recombined devices | 0/8 |

The consequence-hidden chain happened to produce two correct records out of
eight. It did not support reliable later action.

## Action results

| Condition | Correct matching actions |
| --- | ---: |
| Cold | 26/48 |
| Raw exposed sensory reports | 24/48 |
| Full exposed clerical pipeline | 48/48 |
| Consequence-hidden clerical pipeline | 21/48 |
| Exposed guidance removed | 27/48 |
| Both rendered sentences without selection | 29/48 |
| Normalized selection of supplied sentence | 48/48 |
| Oracle selection of exposed model sentence | 48/48 |
| Oracle selection of supplied sentence | 48/48 |

The exposed pipeline made all 24 actions in both design positions and all 24
actions in both target directions. Every participant cell contained three
valid action objects.

The full pipeline made 12 of 24 unrelated actions, exactly the cold score. Its
normalizer selected no record for any novel or recombined device, so those
participant requests contained no retained sentence. Delivering both sentences
without selection made 18 unrelated actions in this run, an incidental gain
rather than evidence for safe applicability.

## What this supports

The validation supports a restricted learned clerical instrument in this
deterministic domain. Consequence produced a model-mediated record. A separate
model-mediated description of a new device selected that record by complete
structural match. The selected record then caused correct action across new
identities and controls.

The hidden-consequence and removal gaps support causal attribution to the
exposed record and its delivery. The raw comparison shows that merely carrying
the sensory reports was not enough. Novel and recombined devices show that the
mechanism can remain silent when the complete learned structure is absent.

The result also clarifies the harness boundary. The runtime performed exact
field comparison and fixed serialization. It did not decide which feature
matters, infer a control relation, or select an action. Those semantic fields
came from the restricted clerk, and the action came from the participant.

## What this does not support

Known-correct supplied guidance also made all 48 actions. This experiment
validates the learned instrument, not superiority over static instruction.

The scope is a small two-feature control world. Exact equality over normalized
features remains a structured retrieval mechanism. The experiment does not yet
show revision after counterevidence, accumulation across a longer trajectory,
net value, or exceptional practice. Formation therefore remains null.

The next question is whether the clerical substrate can revise a stored record
after the same visible structure produces a different consequence, while
keeping the old record available for causal comparison and preventing stale
guidance from acting.

## Audit details

- Clerical model: `huggingface.co/qwen/qwen3-4b-gguf:Q4_K_M`
- Clerical digest: `sha256:618c80458ca4012b132ef1847bcd49ec5f923c3d9df35fdc534715085108e9f3`
- Participant model: `ai/qwen3:14B-Q6_K`
- Participant digest: `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Logical calls: 728
- Physical attempts: 728
- Retries: 0
- Frozen specification SHA-256: `be3beef00927b57d367d944f3798c23b526fac32fd222bb00929e7ae8121d729`
- Specimen SHA-256: `ade31b95717dc616bbf114a73f6bf068c694ea843232611fc57c85831b3c5fd1`
- Packet SHA-256: `61f04a3435adc87322df786ab94d9c19ddfefc2d8fa93aa75403ee626a07ecbd`
- Frozen learned-instrument verdict: `supported`
- Formation verdict: `null`
- Replay: exact from retained request and response bytes

The computed record is [packet.json](packet.json). The fresh worlds and fixed
schedule are in [specimen.json](specimen.json). Both model identities are in
[provider.json](provider.json). Every raw request and response is under
`attempts/`.
