# Formation

Formation is a research and engineering project about the instruments that let
a cold language model become an exceptional situated practitioner through
experience after training.

Its working thesis is:

> A frozen, intermittently invoked model can develop into a particular
> practitioner when a governed system converts experience and consequence into
> durable, selective, corrigible changes in future behavior.

The model may begin each invocation cold. The practitioner does not. What
persists is a developmental system around the model: experience lineage,
consequence attribution, candidate changes, governance and revocation,
activation policy, and prospective evaluation.

Game mastering, coding, writing, research, and operations are possible contact
domains. None is the project itself. They are places where formation can be
observed, challenged, and compared.

## The question

The ordinary agent loop is good at continuing work:

```text
assemble context -> infer -> act -> observe -> append -> repeat
```

Appending an observation does not establish development. More context can
produce a different answer without producing an earned or transferable change
in the practitioner.

Formation adds a second, governed loop:

```text
practice loop:    orient -> decide -> act -> observe consequence
formation loop:   attribute -> propose change -> govern eligibility
                  -> activate selectively -> revise or revoke
```

Governance may include a bounded trial, but the project does not assume that a
trial is a universal stage or that it must precede every permitted influence.

The central research question is not whether the system can remember an episode.
It is whether an experience can cause a warranted change that improves action in
a later, novel, structurally related situation without causing inappropriate
transfer elsewhere.

## The system boundary

Formation begins with three distinct roles:

- The **cold model** supplies inference. It is replaceable and receives no
  weight updates within the project boundary.
- The **formation runtime** acts with the model, preserves developmental
  lineage, and governs changes in the practitioner.
- The **trajectory harness** creates controlled histories, forks identical
  starting states, schedules environments and declared consequence oracles,
  assigns ablations, and captures evidence for prospective scoring.

This separation is load-bearing. If the trajectory harness interprets a
consequence and quietly hands the correct lesson to the model, the experiment
has measured oracle assistance rather than formation.

## What counts as progress

A formation claim requires more than changed behavior. At minimum, the system
must show:

1. **Acquisition:** consequential experience causes a later behavioral change.
2. **Transfer:** the change helps on prospective cases that do not permit answer
   copying or simple episode matching.
3. **Selectivity:** the change stays silent where its structure does not apply.
4. **Corrigibility:** later counterevidence can revise, suspend, or revoke it.
5. **Causal contribution:** ablation or controlled branching attributes the
   improvement to the acquired change.
6. **Net value:** the benefit survives the costs of context, checks, latency,
   maintenance, and negative transfer.

“Exceptional” is comparative, not celebratory. A formed practitioner must beat
the same cold model with static instructions and ordinary persistence on novel
work, while remaining governable.

## Relationship to Construct

[Construct](../construct/README.md) is the immediate experimental ancestor. It
found meaningful bounded results about offer quality, consequence-earned
authority, cross-session influence, selective eviction and recovery, and
governed continuity. Formation accepts those results within their original
evidence bounds.

Formation does **not** assume that Construct's provisional Body Core, event
schema, projectors, adapters, or vocabulary are the correct architecture for
development. Those are prior art and potential instruments, not inherited
requirements. Formation must earn its own objects and mechanisms.

Construct should remain reproducible as the lab that owns its findings. New
trajectory experiments and formation-runtime code belong here.

## Present state

The project is at **Phase 0 concept and boundary stage**. The documentation
packet remains a draft, pre-evidence contract, but it has completed a two-family
cold boundary review. That review removed the remaining permission for
harness-originated interpretation, kept fixture replay exclusion distinct from
ablation in general, and aligned semantic compatibility across the packet. No
formation mechanism or developmental effect has been earned.

The first deterministic [two-loop fixture](docs/FIXTURE.md) is now a
cold-reviewed semantic draft. It exists to pressure the boundary before schema
selection or code; its authored stubs and outcomes are wire-only, and its first
review removed pre-admission trial as a mandatory lifecycle stage.

The next layer remains Markdown-first. The [instrument map](docs/INSTRUMENTS.md)
describes the observable jobs, authority boundaries, receipts, and
loses-conditions that a future schema must serve. No machine schema or storage
syntax has been selected. Its first fixture handoff audit found and removed a
harness-derived ablation view and an authority collapse in the walkthrough.
Two independent constructions must now enumerate the fixture's semantic receipt
graph and refusal outcomes. Only a disagreement that prose cannot settle, or a
need to compute identity, should force the first materialization syntax.

The first milestone is a deterministic, inspectable two-loop skeleton that can
represent a practice trajectory and a candidate change without pretending the
candidate is learned or useful. The first experimental milestone comes later:
a same-model trajectory comparison that can distinguish consequence-governed
formation from raw episodic recall and authored lessons.

## Project map

| Place | Responsibility |
| --- | --- |
| [docs/](docs/README.md) | Concept, research program, and implementation boundary |
| `formation/` | Formation runtime; created only when the first build slice begins |
| `trajectory/` | External trajectory harness; created only when its contract is specified |
| `tests/` | Deterministic contract and separation tests |
| `evidence/` | Future primary trajectories and computed verdicts, never hand-written claims |

## Evidence and authority

When sources disagree, prefer the most specific authority for the question:

1. Primary developmental lineage and trajectory evidence for what occurred.
2. Frozen scorers and their computed output for experimental verdicts.
3. Reviewed experiment and mechanism specifications for the contacted contract.
4. The authority and record specifications for cross-experiment boundaries.
5. The concept document for working definitions and research questions.
6. This README for the project story, present state, and routing.
7. Plans and build documents for intended work.

No source in the first two classes exists yet. Future plans, fixtures, and
walking skeletons cannot promote themselves into evidence.

## Working here

Before substantive work:

1. Read this page and the nearest directory README.
2. Name whether the task serves concept formation, runtime engineering,
   trajectory instrumentation, or a specific experiment.
3. State what would distinguish the proposed mechanism from retrieval, answer
   copying, prompt accumulation, or harness assistance.
4. For experiments, name the same-model baseline, transfer target,
   non-transfer case, consequence oracle, and stopping condition before contact.
5. Keep claims at the maturity actually supported by code and evidence.

The current route is [concept](docs/CONCEPT.md), [authority](docs/AUTHORITY.md),
[record](docs/RECORD.md), [evaluation](docs/EVALUATION.md), [plan](docs/PLAN.md),
then [fixture](docs/FIXTURE.md), [instrument map](docs/INSTRUMENTS.md), and
[build boundary](docs/BUILD.md).
