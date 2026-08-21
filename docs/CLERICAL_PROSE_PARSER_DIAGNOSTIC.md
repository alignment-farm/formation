# Clerical prose parser diagnostic

Status: **frozen before contact under the session-wide human authorization**.

## The narrow question

The staged 4B clerk wrote four effect sentences that stated both control facts
correctly but reversed their order. A later structured-record call failed in
the two cases where it still had to infer an unobserved opposite effect.

Can the clerk reliably extract two facts that are already explicit in its own
retained sentence, allowing a deterministic serializer to place them in the
participant's calibrated order?

This is the clerical NLP role without causal completion. The parser does not
see a sensory report, future device, target, controls, expected action, or
score. It sees one sentence pair in which both effects are stated.

## Mechanism

The retained sentence may put either control first. The clerk returns one JSON
object with named first-control and second-control effect fields. Both values
must be present and opposite.

The harness then inserts those exact values into a fixed sentence template:

```text
The first displayed control <effect> position. The second displayed control <effect> position.
```

This serializer changes order and inflection only. It does not derive the
second effect, interpret a consequence, select a record, or choose an action.

Later applicability reuses the staged successor's retained feature
normalizations. The harness compares both model-written scope fields for exact
equality and delivers the rendered sentence only on a complete match.

## Retained source

The source remains
`evidence/staged-clerical-instrument-20260820T164000Z/packet.json` with SHA-256
`fbd47acdc4d6f493a46bcb0103d04449829b137b2ccdb4a3ec4a285cf5da7bc5`.
Its specimen SHA-256 is
`7530dd0752b9018fd82920c8ef9e9b3e90d4261ffe53d10e1881cdb35a0b072c`.

Before contact, the runner must require all four source transcriptions to be
exact, all four retained sentence pairs to state both correct effects, all 12
later normalizations to be valid, at least 10 to be exact, and no false
selection from the retained exact matcher on novel or recombined cases.

## Fresh action comparison

The later descriptions and true relations remain fixed, but every participant
device receives new family IDs, device IDs, positions, and control strings.
Each case receives four calls under seven conditions:

- no retained material;
- the two retained raw sensory reports;
- both rendered parsed records without selection;
- a rendered parsed record selected by retained normalization and exact scope
  equality;
- a supplied sentence selected by the same retained normalization;
- a rendered parsed record selected by the environment-owned match; and
- a supplied sentence selected by the environment-owned match.

## Prospective interpretation

The apparatus is not engaged unless the oracle-selected supplied sentence
makes at least 29 of 32 matching actions, at least 14 of 16 in each design and
direction, and every participant cell contains at least three valid actions.

The parser repair is found only if at least three of four parsed records are
semantically exact and oracle-selected rendered records make at least 27 of 32
matching actions.

A composed pipeline candidate additionally requires:

- retained normalized scope selection correct in at least 10 of 12 cases, with
  no more than one false novel or recombined selection;
- at least 27 of 32 matching actions with normalized rendered records;
- at least eight more matching actions than cold;
- at least four more matching actions than raw reports;
- at least four more matching actions than both unselected rendered records;
- no more than four fewer matching actions than the supplied ceiling; and
- no more than two fewer unrelated actions than cold.

The verdict is `not_engaged`, `harmful`, `pipeline_candidate`, `parser_only`,
or `null`.

A candidate would still be a component result assembled from retained source
outputs. It would justify a fresh end-to-end experiment; it would not itself
establish Formation.

## Models, budget, and evidence

The clerical model is
`huggingface.co/qwen/qwen3-4b-gguf:Q4_K_M` with digest
`sha256:618c80458ca4012b132ef1847bcd49ec5f923c3d9df35fdc534715085108e9f3`.
The participant is `ai/qwen3:14B-Q6_K` with digest
`sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`.
Both use the local Docker Model Runner chat-completions interface.

The fixed schedule contains four parser calls and 336 participant calls, for
340 logical calls. At most eight transport failures may be retried. The
physical ceiling is 348 attempts. A valid answer is never resampled.

Evidence is written under
`evidence/clerical-prose-parser-<run-id>/` and replayed from retained raw
requests and responses before successful exit.
