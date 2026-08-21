# Learned clerical instrument exploration

Status: **frozen before contact under the session-wide human authorization**.

## The idea

A second model can help the formation runtime record experience without seeing
the participant model's whole task. It acts as a clerk, not as another
participant and not as an answer oracle.

This experiment gives a 4B model two narrow jobs. First, it turns a sensory
account of one action and its consequence into a small effect record. Later,
it compares a new device description with the scopes of stored records and
names the records that appear relevant. The 4B model never receives the new
device's controls, position, target, action request, expected action, or score.

The 14B participant receives the full action request. It never receives the
clerk's prompt or hidden environment profile. The harness only moves exact
bytes between the declared surfaces.

This is a test of learned instrumentation. It does not test whether one model
develops alone.

## Question

Can a restricted clerical model encode consequences and classify later
applicability well enough for a separate cold participant to use the right
experience on new devices?

The observation that matters is a complete chain:

1. The clerk writes correct records from restricted sensory reports.
2. The clerk selects those records for structurally matching new devices and
   selects nothing for novel or recombined devices.
3. The participant improves on matching actions when the selected records are
   delivered.
4. The participant does not lose unrelated actions.

## Deterministic world

There are two independent lineages. Each lineage encounters two source
devices. The source devices have different visible designs and opposite
first-control effects. Each source action produces an environment result.

Later devices have fresh controller-family IDs, device IDs, and control
strings. A later device may share both visible design features with a source
device. It may instead have a wholly new design or recombine one feature from
each source. Thus no later matching case can be selected by source device or
controller-family identity.

The environment owns the true control effects and applies every participant
action. The harness knows those effects so it can execute and score the world.
It does not put them into a clerk classification request.

## Clerk input boundary

The clerical model is
`huggingface.co/qwen/qwen3-4b-gguf:Q4_K_M` with digest
`sha256:618c80458ca4012b132ef1847bcd49ec5f923c3d9df35fdc534715085108e9f3`.
It uses the local Docker Model Runner chat-completions interface.

For encoding, it receives only:

- a natural-language description of two visible design features;
- whether the first or second displayed actuator was used; and
- whether the position gauge rose or fell.

It is told that exactly one displayed actuator raises the gauge and the other
lowers it. It must return a JSON record containing the two normalized scope
features and the two actuator effects.

It does not receive the participant's action prompt, controller-family ID,
device ID, control strings, starting position, target, future cases, expected
action, environment profile, or score.

For later classification, it receives only:

- a natural-language description of the current device's two visible
  features; and
- record IDs paired with their parsed scope features.

It does not receive record effects. It returns the IDs whose complete scope
matches the current description. The harness may parse this declared JSON
surface and retrieve exactly those records. It may not add a record, repair a
record, infer a scope, infer an effect, or choose an action.

Every clerk input and output is retained. A malformed output remains malformed.
A valid output is never resampled.

## Participant boundary

The participant remains `ai/qwen3:14B-Q6_K` with digest
`sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
through the same local interface.

It receives the full later device, including the visible design description,
fresh controls, current position, target, allowed actions, and whatever
retained material the assigned branch permits. It returns one action. The
environment applies that action before the scorer compares it with the
environment-owned answer.

## Comparisons

Each lineage has six later cases: A above, A below, B above, B below, a wholly
novel design, and a recombination of the two learned designs. Every case gets
four identical participant calls in seven conditions:

- **Cold:** no retained material.
- **Raw:** both restricted sensory reports, without clerical interpretation.
- **All clerk records:** both model-written records, without classification.
- **Clerk pipeline:** the clerk classifies among its own records and the
  harness delivers exactly the selected records.
- **Clerk selection over supplied records:** the clerk classifies scopes from
  known-correct supplied records. This isolates classification from encoding.
- **Oracle selection of clerk records:** the harness uses the known structural
  match to select a model-written record. This isolates encoding and
  consumption from classification.
- **Oracle selection of supplied records:** the harness selects a known-correct
  record. This is an interface ceiling, not a developmental condition.

The supplied and oracle conditions may calibrate the apparatus. They cannot
support a learned-instrument result on their own.

## Prospective interpretation

The apparatus is not engaged unless oracle-selected supplied records make at
least 29 of 32 matching actions, at least 14 of 16 in each design position,
and at least 14 of 16 in each target direction. Every four-call participant
cell must also contain at least three valid action objects.

An encoding result requires at least three of four clerk records to be exact
and oracle-selected clerk records to make at least 27 of 32 matching actions.

A classification result requires the clerk to make at least 10 of 12 exact
classifications over supplied scopes, with no false selection in at least
three of the four novel or recombined cases. Clerk-selected supplied records
must make at least 27 of 32 matching actions.

A full pipeline candidate additionally requires:

- at least 10 of 12 exact classifications over clerk-written scopes;
- at least 27 of 32 matching actions under the clerk pipeline;
- at least eight more matching actions than cold;
- at least four more matching actions than raw experience;
- at least four more matching actions than delivery of all clerk records;
- no more than four fewer matching actions than the oracle-selected supplied
  ceiling; and
- no more than two fewer unrelated actions than cold.

If the apparatus is not engaged, the verdict is `not_engaged`. If the full
pipeline loses at least four unrelated actions relative to cold, it is
`harmful`. Otherwise the verdict is `pipeline_candidate`, `encoding_only`,
`classification_only`, or `null` according to the observations above.

This is exploratory. Even `pipeline_candidate` would show that a restricted
second model can serve as useful formation instrumentation in this specimen.
It would not establish Formation, general competence, or that the participant
developed by itself.

## Budget and stopping rule

The frozen schedule contains 368 logical calls:

- four participant source actions;
- four clerical encoding calls;
- 24 clerical classification calls; and
- 336 later participant actions.

At most eight transport failures may be retried. The physical ceiling is 376
attempts. Model output never changes the schedule. The runner stops after the
fixed schedule or either ceiling.

Evidence is written under
`evidence/learned-clerical-instrument-<run-id>/` and replayed from the retained
request and response bytes before successful exit.
