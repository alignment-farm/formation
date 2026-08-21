# Staged clerical instrument successor

## Main result

The structural classification mechanism worked, but the effect payload did
not. The frozen verdict is `normalization_only`.

The 4B clerk transcribed all four source experiences exactly. It normalized 10
of 12 later device descriptions exactly. An exact comparison of the two
normalized feature fields selected the correct stored scope in 10 of 12 cases
and made no false selection for novel or recombined devices.

The clerk's four effect sentences contained the correct two facts, but placed
the second-control sentence first. None matched the calibrated first-then-second
form. The participant did not use those reversed sentences, even when the
harness selected the right one.

## What changed from the first experiment

The clerk no longer interpreted the sensory report and wrote a complete record
in one step. One call transcribed the observed actuator, movement, and visible
features. A second call wrote the two control effects.

For later applicability, another clerk call normalized only the current visible
features. The harness compared that model-written pair with each model-written
source pair for exact equality. The harness did not interpret a feature or
choose a control action.

The participant received the short sentence form that passed the supplied
delivery calibration.

## Results

All four source transcriptions were exact. All four effect sentences stated the
correct relation, but in reversed sentence order. Their exact score was 0 of 4.

Later normalization was exact in 10 of 12 cases. The clerk called an arched
housing `smooth` in both directions for one lineage. It normalized every novel
and recombined device correctly.

| Applicability method | Exact selections | False novel or recombined selections |
| --- | ---: | ---: |
| Direct clerk selection | 10/12 | 2/4 |
| Exact match over model-normalized scopes | 10/12 | 0/4 |
| Exact match against supplied source scopes | 10/12 | 0/4 |

The direct selector repeated the first experiment's recombination error. Exact
equality over both normalized fields removed that error.

| Participant condition | Correct matching actions |
| --- | ---: |
| Cold | 16/32 |
| Raw sensory reports | 16/32 |
| Both clerk sentences | 16/32 |
| Direct-selector clerk sentence | 16/32 |
| Exact-match clerk sentence | 16/32 |
| Exact-match supplied sentence | 28/32 |
| Oracle-selected clerk sentence | 16/32 |
| Oracle-selected supplied sentence | 32/32 |

Every participant response was valid. The exact-match clerk pipeline made 4 of
16 unrelated actions, the same as cold. Raw reports made 8, while delivering
both clerk sentences made 6.

## What this supports

The result supports one component of the proposed learned instrument. A model
can normalize restricted sensory descriptions, and a mechanical equality check
over two model-written fields can enforce a conjunction better than asking the
same model to select a record directly. This operates across fresh family,
device, and control identities.

The result does not support the complete pipeline. The participant ceiling was
healthy, but the exact model-written payload was not in the calibrated order.
The participant therefore received correct facts in a form it did not use.

The next diagnostic should ask the clerk for named first-control and
second-control effect fields. A deterministic serializer can then place those
model-authored values into the calibrated sentence order. That serializer
would arrange declared fields; it would not infer an effect or action.

## Limits

This is one exploratory deterministic specimen. Exact scope matching is still
a retrieval mechanism, although its keys are model-written structural
descriptions rather than environment identity. The experiment does not show
Formation or development by one model acting alone.

## Audit details

- Clerical model: `huggingface.co/qwen/qwen3-4b-gguf:Q4_K_M`
- Clerical digest: `sha256:618c80458ca4012b132ef1847bcd49ec5f923c3d9df35fdc534715085108e9f3`
- Participant model: `ai/qwen3:14B-Q6_K`
- Participant digest: `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Logical calls: 420
- Physical attempts: 420
- Retries: 0
- Frozen specification SHA-256: `c1c49419d61f91ef6adb1c6ecc4213dde6379aa59d9b5d2cd66884e543a22140`
- Specimen SHA-256: `7530dd0752b9018fd82920c8ef9e9b3e90d4261ffe53d10e1881cdb35a0b072c`
- Packet SHA-256: `fbd47acdc4d6f493a46bcb0103d04449829b137b2ccdb4a3ec4a285cf5da7bc5`
- Frozen instrument verdict: `normalization_only`
- Formation verdict: `null`
- Replay: exact from retained request and response bytes

The computed record is [packet.json](packet.json). The fresh worlds and exact
information boundaries are in [specimen.json](specimen.json). Both model
identities are in [provider.json](provider.json). Every raw request and response
is under `attempts/`.
