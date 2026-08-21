# Staged clerical instrument successor

Status: **frozen before contact under the session-wide human authorization**.

## The repair

The first clerical experiment exposed three separate facts. The restricted 4B
model classified 10 of 12 later devices correctly, but it accepted two
recombined partial matches. Its one-step consequence records described only one
of four control relations correctly. The 14B participant also failed to use
the new JSON record container.

A supplied-record calibration then found a reliable participant interface: a
short effect sentence made all 32 actions.

This successor changes each failed boundary directly:

1. The clerk first transcribes the sensory report into a small observation.
2. A separate clerk call turns that observation into the calibrated effect
   sentence.
3. For a later device, the clerk normalizes only its two visible features.
4. The harness compares the two model-written feature pairs for exact equality.
5. If they match, the harness delivers the exact model-written sentence to the
   participant.

The harness performs string equality. It does not decide which feature matters,
infer a control effect, write guidance, or choose an action.

## Question

Can a staged, restricted clerical model turn consequence into a useful sentence
and later select it through a complete two-feature match on fresh devices?

The observation that matters is a full pipeline that improves matching action,
rejects novel and recombined devices, and approaches an oracle-selected
supplied-sentence ceiling.

## Information separation

The clerk is `huggingface.co/qwen/qwen3-4b-gguf:Q4_K_M` with digest
`sha256:618c80458ca4012b132ef1847bcd49ec5f923c3d9df35fdc534715085108e9f3`.

During sensory transcription it receives only a natural-language device
description, which displayed actuator was used, and whether the gauge rose or
fell. It returns normalized scope features, observed slot, and observed effect.

During sentence writing it receives only that exact transcript and the domain
fact that the two displayed controls have opposite effects. It returns one
sentence stating both effects. It does not receive a future device or action
request.

During later normalization it receives only the current device description. It
returns two normalized scope features. It does not receive stored effects,
record IDs, controls, position, target, expected action, or score.

A direct-selector diagnostic also receives the current description and stored
scope fields without effects. It returns applicable record IDs. This preserves
the first experiment's classifier for comparison with exact matching over the
normalized feature pair.

The participant remains `ai/qwen3:14B-Q6_K` with digest
`sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`.
It alone receives controls, position, target, allowed actions, and selected
guidance.

Both models use the local Docker Model Runner chat-completions interface. Every
input and output is retained. Malformed outputs remain malformed, and valid
outputs are never resampled.

## World and comparisons

Two fresh lineages each contain two source designs with opposite control
relations. Later devices have new family IDs, device IDs, and control strings.
Each lineage has six later cases: A above, A below, B above, B below, a wholly
novel design, and a recombination containing one feature from each source.

Every later case receives four participant calls under eight conditions:

- no retained material;
- both raw sensory reports;
- both model-written sentences without selection;
- a model-written sentence selected by the direct clerk classifier;
- a model-written sentence selected by exact equality between model-normalized
  current scope and model-transcribed source scope;
- a supplied correct sentence selected by model normalization against supplied
  source scopes;
- a model-written sentence selected by the environment-owned structural match;
  and
- a supplied sentence selected by the environment-owned structural match.

The last condition is the participant ceiling. The supplied conditions isolate
normalization and delivery. The oracle-selected model sentence isolates
transcription and sentence writing. None can support the full pipeline alone.

## Prospective interpretation

The apparatus is not engaged unless the oracle-selected supplied sentence
makes at least 29 of 32 matching actions, at least 14 of 16 in each source
design and direction, and every four-call participant cell contains at least
three valid action objects.

Staged encoding is found only if at least three of four transcriptions and
three of four sentences are exact, and oracle-selected model sentences make at
least 27 of 32 matching actions.

Normalization is found only if at least 10 of 12 current feature pairs are
exact, exact matching selects the correct supplied sentence in at least 10 of
12 cases, produces no more than one false selection across the four novel or
recombined cases, and makes at least 27 of 32 matching actions.

A full pipeline candidate additionally requires:

- exact matching over model-written scopes to select correctly in at least 10
  of 12 cases, with no more than one false selection;
- at least 27 of 32 matching actions;
- at least eight more matching actions than cold;
- at least four more matching actions than raw reports;
- at least four more matching actions than both unselected sentences;
- no more than four fewer matching actions than the supplied ceiling; and
- no more than two fewer unrelated actions than cold.

If the apparatus is not engaged, the verdict is `not_engaged`. If the full
pipeline loses at least four unrelated actions, it is `harmful`. Otherwise the
verdict is `pipeline_candidate`, `encoding_only`, `normalization_only`, or
`null` according to the observations above.

This remains exploratory. A candidate would support a learned clerical
instrument in this deterministic specimen, not Formation or development by one
model acting alone.

## Budget and stopping rule

The schedule contains 420 logical calls:

- four participant source actions;
- four clerical transcriptions;
- four clerical sentence-writing calls;
- 12 later scope-normalization calls;
- 12 direct-selector calls; and
- 384 later participant actions.

At most eight transport failures may be retried. The physical ceiling is 428
attempts. Model output never changes the schedule. The runner stops after the
fixed schedule or either ceiling.

Evidence is written under
`evidence/staged-clerical-instrument-<run-id>/` and replayed from retained raw
requests and responses before successful exit.
