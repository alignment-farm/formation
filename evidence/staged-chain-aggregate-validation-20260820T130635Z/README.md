# Aggregate validation of the staged lesson chain

## Main result

The bounded staged mechanism passed its frozen validation. In all eight source
worlds, the model recorded the environment result exactly and turned it into
the correct effect table. Those model-written tables then produced all 48
correct matching actions on new devices.

The causal comparisons were much weaker. No retained information made 24
matching actions. Raw experience made 22. Hiding the consequence made 24.
Direct table writing made 3. Removing the staged table left 24. A supplied
exact table also made all 48.

The family check preserved unrelated behavior. Both the cold branch and the
checked staged branch made 28 of 48 unrelated actions. Without the check, the
staged table made only 2. The check prevented 26 observed errors, but that
number did not help the supported verdict.

## What was tested

Eight fresh controller families were balanced across both possible relations.
In four, the first displayed action increased position. In four, the second
did. Every source began with a target one step below the starting position.

The model chose the second action in every source. The environment reported
downward movement in the first-increases families and upward movement in the
second-increases families. One cold call wrote that selected slot and movement.
A second cold call inferred the other slot and wrote a complete JSON effect
table.

Each source then received new matching devices with targets above and below.
It also received two unrelated devices whose hidden relation was reversed.
Every branch and case received three identical calls.

## Results

| Later information | Matching actions | Unrelated actions |
| --- | ---: | ---: |
| No retained information | 24/48 | 28/48 |
| Raw experience | 22/48 | 30/48 |
| Directly written table | 3/48 | 28/48 |
| Exposed staged table with family check | 48/48 | 28/48 |
| Hidden-consequence staged table with family check | 24/48 | 28/48 |
| Exposed staged table removed | 24/48 | 27/48 |
| Exposed staged table without family check | 48/48 | 2/48 |
| Supplied exact table with family check | 48/48 | 27/48 |

The staged table made all 24 upward and all 24 downward matching actions. It
also made all 24 matching actions in each true-relation group and all 12 in
each relation-by-direction quadrant. Every three-call cell contained at least
two valid action objects.

## What this supports

This run validates one bounded mechanism in the opaque-control domain. An
environment consequence caused a model-written observation and table. That
table improved later action on new matching devices. The effect disappeared
when the table was removed, did not appear from raw experience or direct
writing, and stayed off unrelated families under the external family check.

This is not yet a Formation effect. The model-written table did not outperform
the supplied exact table. The run also did not test whether several lessons can
accumulate, whether a later contradiction can revise the table, whether the
change survives long delays, or whether the mechanism works in another domain.

The next experiment can now test revision. After a valid table guides action,
the environment relation can change. A new consequence should cause the model
to replace the stale table, while a hidden consequence and the old table should
not produce the same post-change behavior.

## Audit details

- Model: `ai/qwen3:14B-Q6_K`
- Model digest: `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Logical calls: 816
- Physical attempts: 816
- Retries: 0
- Frozen specification SHA-256: `6cd833dba4c20449100ab64c02cef9d312e9e311cbf91725737caf9d03beb2b4`
- Specimen SHA-256: `c804bc536be4e0aa3168bb08019485f01490d9522e8be0c1a3cea1ccdf7a09fa`
- Packet SHA-256: `1145f9afeec0ebc263e999cb6600bd23cb505ba7944cf0f75e69b48c9625b290`
- Frozen validation verdict: `supported`
- Formation verdict: `null`
- Replay: exact from retained request and response bytes

The computed record is [packet.json](packet.json). The frozen worlds are in
[specimen.json](specimen.json). The exact provider identity is in
[provider.json](provider.json). Every raw request and response is retained under
`attempts/`.
