# Canonical clerical record diagnostic

Status: **frozen before contact under the session-wide human authorization**.

## The narrow question

The staged clerical successor produced four exact sensory transcriptions and
four semantically correct effect sentences. The sentences put the second
control first, while the participant calibration had established a reliable
first-then-second order. The participant ignored the reversed form.

Can the clerk instead place the two effects in named fields, allowing a
deterministic serializer to produce the calibrated sentence without inferring
an effect?

This diagnostic reuses the retained transcriptions and later scope
normalizations from the staged successor. It verifies that source packet and
specimen before contact. It then makes four new clerk calls and tests the
rendered sentences on fresh participant devices.

## Mechanism boundary

The 4B clerk receives one exact retained transcription. It returns:

```json
{
  "first_control_effect": "increases_position",
  "second_control_effect": "decreases_position"
}
```

The two values must be opposites. The harness rejects any other shape. For a
valid record, it performs only this fixed rendering:

```text
The first displayed control increases position. The second displayed control decreases position.
```

The words `increases` and `decreases` come directly from the named model output
fields. The serializer does not read the sensory report, infer the unobserved
effect, inspect a later target, or choose an action.

The retained later normalization remains restricted to visible device
description. Exact equality over both normalized fields selects the rendered
sentence. The participant alone receives controls, position, target, and the
selected sentence.

## Retained source

The source is
`evidence/staged-clerical-instrument-20260820T164000Z/packet.json` with SHA-256
`fbd47acdc4d6f493a46bcb0103d04449829b137b2ccdb4a3ec4a285cf5da7bc5`.
Its specimen SHA-256 is
`7530dd0752b9018fd82920c8ef9e9b3e90d4261ffe53d10e1881cdb35a0b072c`.

Before contact, the runner must require all four retained transcriptions to be
exact, all 12 later normalizations to be valid, at least 10 to be exact, and
the retained exact matcher to have made no false selection on novel or
recombined cases.

## Comparison

The fresh participant devices preserve the source descriptions and true
relations but use new family IDs, device IDs, positions, and control strings.
Each lineage again has A above, A below, B above, B below, novel above, and
recombined below cases.

Every case receives four calls under seven conditions:

- no retained material;
- the two retained raw sensory reports;
- both rendered model records without selection;
- a rendered model record selected by retained model normalization and exact
  scope equality;
- a supplied sentence selected by the same retained normalization;
- a rendered model record selected by the environment-owned match; and
- a supplied sentence selected by the environment-owned match.

The supplied oracle condition is the participant ceiling. The model oracle
condition isolates structured effect authorship and rendering. The normalized
supplied condition preserves the prior normalization check.

## Prospective interpretation

The apparatus is not engaged unless the oracle-selected supplied sentence
makes at least 29 of 32 matching actions, at least 14 of 16 in each design and
direction, and every four-call participant cell contains at least three valid
action objects.

The canonical record repair is found only if at least three of four structured
effect records are semantically exact and oracle-selected rendered records
make at least 27 of 32 matching actions.

A composed pipeline candidate additionally requires:

- the retained normalized matcher to select correctly in at least 10 of 12
  cases with no more than one false novel or recombined selection;
- at least 27 of 32 matching actions with normalized rendered records;
- at least eight more matching actions than cold;
- at least four more matching actions than raw reports;
- at least four more matching actions than both unselected rendered records;
- no more than four fewer matching actions than the supplied ceiling; and
- no more than two fewer unrelated actions than cold.

The verdict is `not_engaged`, `harmful`, `pipeline_candidate`,
`canonical_record_only`, or `null` according to those observations.

Even a candidate would be a component result. It would compose retained
outputs from one contact with a new clerical record surface and fresh action
cases. It would not be a fresh end-to-end validation or a Formation finding.

## Models, budget, and retention

The clerical model remains
`huggingface.co/qwen/qwen3-4b-gguf:Q4_K_M` with digest
`sha256:618c80458ca4012b132ef1847bcd49ec5f923c3d9df35fdc534715085108e9f3`.
The participant remains `ai/qwen3:14B-Q6_K` with digest
`sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`.
Both use the local Docker Model Runner chat-completions interface.

The frozen schedule contains four clerk record calls and 336 participant
calls, for 340 logical calls. At most eight transport failures may be retried,
so the physical ceiling is 348 attempts. Valid outputs are never resampled.

Evidence is written under
`evidence/canonical-clerical-record-<run-id>/` and replayed from retained raw
requests and responses before successful exit.
