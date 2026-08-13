# Instrument map

Status: **Phase 0 Markdown contract; no machine schema or implementation
selected**.

Purpose: describe the instruments needed to make Formation observable without
turning fixture stubs, Construct organs, or convenient module boundaries into an
unearned architecture.

## Markdown-first rule

Formation will keep an instrument in prose while prose can still expose the
important disagreement.

For each instrument, the documentation should make five things answerable:

1. What question does the instrument let the project ask?
2. Which authority may operate it?
3. What information may it read?
4. What receipt or externally inspectable effect must it produce?
5. What condition shows that the instrument has crossed the boundary or failed
   to measure its claimed object?

A data structure, class, service, or file format is warranted only after this
contract leaves an ambiguity that prevents two independent implementations from
exchanging the deterministic fixture. The first machine syntax should resolve a
named ambiguity, not merely make the repository look build-ready.

Markdown is not a substitute for later validation. It is the least expensive
place to discover that an object, transition, or field has not yet been earned.

## Roles are not instruments

An authority says who may know or decide something. An instrument is a means of
observing, preserving, arranging, or applying that authority.

One process may host several instruments, and one instrument may call several
processes. Neither fact changes information permissions. Names in this document
therefore describe observable jobs, not required services, modules, agents, or
classes.

The fixture's `blind-commit-v0`, `revision-check-candidate-v0`,
`consequence-warrant-v0`, and `declared-role-match-v0` are authored probes of
these jobs. They are not project-level instruments and do not license matching
production components.

## Boundary-required instrument surfaces

| Instrument surface | Operating authority | May read | Must produce | Must not do |
| --- | --- | --- | --- | --- |
| Practice boundary | Formation runtime | Current runtime-visible situation, declared practitioner state, exact model output | Committed action and its causal inputs | Treat model preference or harness expectation as an external consequence |
| Consequence intake | Environment or declared consequence oracle, recorded by runtime | Committed action and externally available result | Attributed consequence occurrence, including missing or contested status | Insert an interpretation or application scope |
| Developmental recorder and replayer | Formation runtime | Runtime-visible occurrence, interpretation, governance, and influence receipts | Append-only lineage and a reconstructable state view | Accept branch labels, hidden case families, scorer verdicts, or silently repaired history |
| Formation procedure boundary | Formation runtime and declared runtime governor | Preserved experience, public mechanism configuration, runtime-visible evidence | Attributable proposed changes and governance receipts, if the selected mechanism emits them | Receive a correct abstraction, eligibility decision, or future case label from the harness |
| Influence boundary | Formation runtime | Current situation and state currently permitted to influence practice | Considered, selected, or withheld influence plus the exact intervention binding | Equate storage, retrieval, or prompt presence with causal use |
| Trajectory recorder | Trajectory harness | Assignments, runtime and environment receipts, hidden metadata, costs, scorer inputs | Append-only experimental record joined to lineage by opaque coordinates and digests | Replay trajectory-only material into practitioner state |
| Prefix, fork, and ablation controller | Trajectory harness | Frozen protocol, one materialized prefix, declared assignment and ablation targets | Comparable branches and explicit causal exclusions | Change unrelated state, foreground inputs, or runtime-visible reasons |
| Scorer | Scorer under the frozen protocol | Trajectory evidence and declared rubric | Case and trajectory verdicts outside developmental lineage | Govern admission, edit runtime state, or coach later cases |

These surfaces are required by the current questions. Their decomposition is
not. A first runtime may combine practice, recording, replay, governance, and
influence behind one explicit boundary as long as the receipts preserve their
distinct authorities and causal roles.

## Practice boundary

The practice boundary makes a current decision externally consequential. It
binds the situation actually available, any practitioner-state influence, the
cold-model request and response, and the action that the runtime commits.

It is needed because an answer in a transcript is not necessarily an action,
and a model output is not an environment result.

The instrument loses if a later account cannot distinguish:

- what the model proposed from what the runtime committed;
- information present in the request from state that actually influenced its
  construction; or
- the committed action from the consequence observed afterward.

No tool protocol, action language, or agent framework is selected here.

## Consequence intake

Consequence intake preserves what the environment made observable after an
action and binds it to that action. It must represent absent, delayed, partial,
contested, and corrected consequences without manufacturing closure.

The environment is preferred. A declared consequence oracle may stand in only
when the world does not yield a directly inspectable result. The logical
authority remains distinct even if harness code hosts the adapter.

The instrument loses if model self-evaluation, scorer output, or an authored
lesson can enter lineage as an external consequence.

## Developmental recorder and replayer

The developmental recorder preserves only material available to the situated
practitioner. Replay derives practitioner state at a named lineage head; cached
views have no independent authority.

This surface must keep occurrence, interpretation, governance, and influence
separately attributable. It does not require separate stores or event families
for every future mechanism. In particular, trial receipts exist only when a
selected governance policy performs a trial.

The instrument loses if:

- replay needs branch assignment or scorer state;
- an interpretation mutates the occurrence it interprets;
- missing or redacted parents become silently valid state; or
- two clean replays of the same retained lineage produce different views.

Storage engine, serialization, hash canonicalization, concurrency, and
compaction remain unselected.

## Formation procedure boundary

This boundary is where a runtime may turn preserved experience into a proposed
change and decide whether that proposal is eligible to affect practice. It may
be deterministic, model-mediated, composite, or absent in a baseline.

The boundary requires attribution and declared inputs; it does not require
separate interpreter and governor processes. It also does not require a
candidate trial. A policy may reject, admit directly from a consequence
warrant, impose probationary limits, or perform a bounded trial using only
runtime-visible material.

The instrument loses if the harness can supply candidate content, application
scope, or an eligibility decision while the resulting trace still appears
runtime-authored.

This surface distinguishes formation machinery from raw retrieval: retrieval
may expose retained material, but it does not by itself author or govern a
change in future preparedness.

## Influence boundary

The influence boundary observes whether permitted practitioner state changes a
later decision. The current vocabulary calls a selected use `activation`, but
implementations need not build a universal activator service.

The receipt must identify the current situation, the eligible state considered,
the selected or withheld influence, and the exact materialization or
intervention supplied to practice. Later causal attribution still belongs to a
harness comparison or ablation.

The instrument loses if presence in a store, search result, prompt, or tool list
is sufficient to claim activation, or if hidden case-family information is
needed to decide what should influence practice.

## Trajectory recorder

The trajectory recorder preserves the experiment's view: protocol identity,
branch and case assignment, common-prefix and foreground bindings, witnessed
runtime events, costs, ablations, and scorer results.

It shares coordinates and digests with developmental lineage only for audit.
The join must not become a merge.

The instrument loses if a trajectory row can be replayed into practitioner
state, or if the record cannot show that compared branches received the same
foreground material.

## Prefix, fork, and ablation controller

This harness instrument materializes an acquisition prefix once, creates
declared branches, and removes named causal material for ablation probes. It may
arrange experience; it may not interpret experience for the runtime.

A fork receipt must identify the shared head and public condition delivered to
each runtime without delivering the hidden branch label. An ablation must
remove dependent state transitively or make it explicitly unresolved.

The instrument loses if a fork quietly changes foreground data, if an ablation
repairs the branch, or if the runtime learns the hidden reason or expected
effect of the exclusion.

No copy strategy, process-isolation mechanism, or storage snapshot format is
selected here.

## Scorer

The scorer applies a frozen rubric to trajectory evidence. It owns experimental
verdicts, not runtime governance. A deterministic environment result may be one
of its inputs without making the scorer the source of that consequence.

The instrument loses if its output changes practitioner state, if its rubric is
repaired after seeing a case, or if a model's account of its own improvement is
accepted as the primary verdict.

## Deferred and fixture-only machinery

The following are not required instruments at this stage:

- a candidate-trial runner;
- a skill, disposition, or lesson registry;
- a retrieval index or semantic matcher;
- an always-on activation service;
- a Body Core-compatible projector or adapter;
- a promotion queue, curriculum scheduler, or background metabolism loop;
- a cryptographically authenticated writer network; or
- a production evidence warehouse.

Any may become useful. Each needs a contacted question, a consumer, and a
loses-condition before it becomes part of the Formation runtime or harness.

## Pressure that would justify machine syntax

Markdown stops being sufficient when at least one of these occurs:

1. Two independent fixture encodings disagree about a field required for
   replay or information separation.
2. A refusal leg cannot identify the exact forbidden location or causal
   reference without typed structure.
3. Byte identity, digest scope, append binding, or redaction semantics must be
   computed rather than inspected.
4. A deterministic materializer is ready to emit records and needs fail-closed
   validation before any runtime or harness code can consume them.

Until then, selecting JSON, JSON Lines, a schema language, or a storage model
would answer an implementation question the research has not yet forced.

## Loses-condition

This instrument map loses if it can be satisfied only by reproducing the
fixture's four stubs or Construct's provisional organs. It also loses if its
flexibility permits the harness to perform interpretation, governance, or
influence on the runtime's behalf without an auditable authority violation.
