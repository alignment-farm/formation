# Staged sentence and table consumption

## Main result

The model wrote all six observations, all six relation sentences, and all six
effect tables exactly. With the family check in place, both model-written forms
then made all 36 matching actions. Their supplied exact controls also made all
36.

The frozen interface verdict is `table_preferred`, but that label is misleading
without its cause. The table did not make more matching actions. It passed one
threshold because unchecked table delivery caused more unrelated errors, so the
family check had more errors to prevent. The sentence missed that threshold by
one because it was less harmful when delivered without the check.

The bounded result is therefore that both forms were consumed perfectly on
matching cases in this run. It does not show that the table is a better action
interface.

## What was tested

Six fresh controller families were balanced across both possible relations.
The model acted once in each world and received the selected slot and actual
movement from the environment. A second cold call wrote one observation of that
result.

Two new cold calls received the same observation. One wrote a sentence that
named what both displayed actions did. The other wrote a JSON table with the
same relation. The harness preserved each output exactly.

Later calls acted on new matching and unrelated devices. The sentence and table
were tested with and without the existing exact-family check. Separate supplied
controls used the exact expected sentence and table.

## What happened

| Later information | Matching actions | Unrelated actions |
| --- | ---: | ---: |
| No retained information | 15/36 | 17/36 |
| Raw experience | 16/36 | 24/36 |
| Model-written sentence with family check | 36/36 | 19/36 |
| Model-written table with family check | 36/36 | 18/36 |
| Model-written sentence without family check | 36/36 | 10/36 |
| Model-written table without family check | 36/36 | 6/36 |
| Supplied exact sentence with family check | 36/36 | 19/36 |
| Supplied exact table with family check | 36/36 | 20/36 |

Both model-written forms made all 18 upward actions, all 18 downward actions,
and all 18 matching actions in each true-relation group. Every three-call cell
contained at least two valid action objects.

The family check improved the sentence's unrelated score by 9 and the table's
by 12. The frozen rule required an improvement of at least 10 before calling a
form usable. That rule classified only the table as usable and therefore
returned `table_preferred`. Requiring a representation to cause enough harm
without governance is not a sound preference rule. Lower ungated harm should
not count against a representation.

## What this supports

This experiment repairs the localized consumption concern from the preceding
validation. On six new worlds, both exact model-written representations guided
every matching action. The action requests for a model-written form and its
supplied control were byte-identical, so differences between those branch
samples are ordinary output variation rather than different instructions.

This does not establish a Formation effect. The packet intentionally omits
consequence withholding and lesson removal because those causal comparisons
were tested in the preceding validation. It also does not test revision,
several accumulated lessons, or another domain.

For later work, the effect table remains convenient because the harness can
check its fields exactly. That engineering convenience, not the formal
`table_preferred` label, is the reason to keep it. Future scorers should measure
negative transfer directly and record gate benefit separately. They should not
reward a representation for causing more harm when ungated.

## Audit details

- Model: `ai/qwen3:14B-Q6_K`
- Model digest: `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Logical calls: 600
- Physical attempts: 600
- Retries: 0
- Frozen specification SHA-256: `1f32db6675d9b61599bc9cfab9f8feab34000d87b5ed88615090e235e2d289f4`
- Specimen SHA-256: `f3efe93df7232bd82bb858414b2db0233fb04b0aec44aa21d2209e36548edc9c`
- Packet SHA-256: `900839670e0fa6eea84af8bc509283b211645f16fe8c246936f139793a9f7eb6`
- Frozen representation verdict: `table_preferred`
- Formation verdict: `null`
- Replay: exact from retained request and response bytes

The computed record is [packet.json](packet.json). The frozen worlds are in
[specimen.json](specimen.json). The exact provider identity is in
[provider.json](provider.json). Every raw request and response is retained under
`attempts/`.
