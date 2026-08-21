# Formation

Formation studies how a language model that starts each call with no memory of
prior work can still become a particular skilled practitioner through later
experience. The model weights stay frozen. What changes is the governed system
around the model: which experiences it preserves, which proposed changes may
affect later action, and how later evidence can revise or revoke those changes.

Its working thesis is:

> A frozen, intermittently invoked model can develop into a particular
> practitioner when a governed system converts experience and consequence into
> durable, selective changes in future behavior that later counterevidence can
> revise, suspend, or revoke.

Here *cold* means that the model carries no project memory between calls. The
*practitioner* is the cold model together with the developmental system that
persists across calls.

Game mastering, coding, writing, research, and operations are possible test
domains. None of them defines the project.

## The question

An ordinary agent loop is good at continuing work:

```text
assemble context -> infer -> act -> observe -> append -> repeat
```

But appending an observation can change the next answer without creating a
change that should transfer to a new situation. More context is not the same as
development.

Formation adds a second, governed loop:

```text
practice loop:    orient -> decide -> act -> observe consequence
formation loop:   attribute -> propose change -> govern eligibility
                  -> activate selectively -> revise or revoke
```

A bounded trial may be part of governance. The project does not require a trial
before every permitted influence.

The central question is whether experience can cause a warranted change that
improves action in a later, novel, structurally related situation while staying
silent where that structure does not apply.

## The system boundary

Formation begins with three separate roles:

- The **cold model** supplies inference. It is replaceable and receives no
  weight updates within the project boundary.
- The **formation runtime** acts with the model, preserves developmental
  lineage, and governs changes in the practitioner.
- The **trajectory harness** creates controlled histories, forks identical
  starting states, schedules environments and declared consequence oracles,
  assigns ablations, and captures evidence for prospective scoring.

This separation prevents a specific mistake. If the harness interprets a
consequence and quietly gives the model the correct lesson, the experiment
measures oracle assistance rather than formation.

## What counts as progress

A changed answer is not enough. A Formation claim requires at least:

1. **Acquisition:** consequential experience causes a later behavioral change.
2. **Transfer:** the change helps on prospective cases that prevent answer
   copying and simple episode matching.
3. **Selectivity:** the change stays silent where its structure does not apply.
4. **Revision:** later counterevidence can revise, suspend, or revoke it.
5. **Causal contribution:** ablation or controlled branching attributes the
   improvement to the acquired change.
6. **Net value:** the benefit survives the costs of context, checks, latency,
   maintenance, and negative transfer.

“Exceptional” is comparative. A formed practitioner must outperform the same
cold model with static instructions and ordinary persistence on novel work,
while remaining governable.

## Relationship to Construct

[Construct](../construct/README.md) is the immediate experimental ancestor. It
produced bounded results on offer quality, consequence-earned authority,
cross-session influence, selective eviction and recovery, and governed
continuity. Formation accepts those results within their original evidence
bounds.

Formation does not inherit Construct’s runtime objects or vocabulary as
requirements. They are prior work and candidate instruments. Formation must
earn its own mechanisms.

Construct remains the lab that owns its findings and should stay reproducible.
New trajectory experiments and formation-runtime code belong here.

## Present state

No Formation effect has been earned. The project has deterministic machinery,
several completed exploratory contacts, and a narrower measurement problem.
Working code, stored text, and changed model output remain instrument or
observation facts unless a prospective comparison supports a stronger claim.

### Current empirical problem

The latest experiment repaired a representation boundary exposed by a harmful
result. A restricted clerk had turned earlier consequences into checked signal
records, but the participant guessed when a new signal matched none of them.
The successor gave the participant an explicit runtime receipt: either the
exact matching record, or the fact that no record matched.

The comparison reused 72 exact request bodies from the harmful parent run.
With a known signal, learned and supplied receipts each completed 18 of 18
tasks; reversed receipts failed all 18. With an unfamiliar signal, the full
catalog and silent absence each guessed six times and failed three. An explicit
empty receipt produced six holds and no failures. The frozen verdict is
`supported`.

This supports the receipt as a representation of what the runtime found. It
does not show that the receipt chose an action, that the learned record beats
supplied guidance, or that Formation has occurred.

The current question is whether retained knowledge can change the value of
seeking information. In the existing two-step world, probing is nearly free:
even a branch with no useful mapping can probe and still retain its chance to
guess. The next deterministic world must give probing an external cost or lost
opportunity. It must keep completion, failure, abstention, information, and
probe cost separate, without telling the participant which first action is
preferred.

Read the [latest evidence account](evidence/matched-applicability-receipt-successor-20260820T232130Z/README.md)
for the exact result and limits. The [research history](docs/RESEARCH_HISTORY.md)
owns the route that led here, and the [plan](docs/PLAN.md) owns standing
milestones and stopping conditions. Formation remains null.

### Working method

> Move quickly enough to encounter reality, then become deliberate when
> interpreting evidence or making a claim.

Discovery comes before validation. An exploratory contact needs a clear
question, an observation that would matter, an exact model and interface, a
small budget and stopping condition, and a place to retain evidence. It does
not need a new chain of license documents or automatic model reviews.

If repeated evidence exposes a phenomenon that bears on the Formation thesis,
the project can then test it again with prospective controls, transfer and
non-transfer cases, replication, and outside criticism. Cursor models may help
with occasional internal critique when a human requests it. They are not
external peer reviewers and do not decide whether an experiment may proceed.

The route to this result matters. Earlier contacts showed that interface
compliance and computation are separate, that shape constraints can repair JSON
without repairing an answer, and that several model setups could not perform
their assigned responsibility. Later contacts exposed problems in consequence
interpretation, selective influence, and model-authored reusable changes. Those
results are retained as bounded research history; they are not another
admission ladder. See [Research history](docs/RESEARCH_HISTORY.md).

### Supporting implementation lane

A separate deterministic lane records the runtime and harness boundaries needed
for causal work. Its fixture-local contracts run from materialization through
[experience closure](docs/EXPERIENCE_CLOSURE.md).

This lane does not gate the exploratory contact. Completing it would establish
plumbing and authority separation, not model development. The detailed
milestones and stopping conditions live in the [plan](docs/PLAN.md).

## Project map

| Place | Responsibility |
| --- | --- |
| [docs/](docs/README.md) | Concept, research contracts, history, and forward plan |
| [docs/RESEARCH_HISTORY.md](docs/RESEARCH_HISTORY.md) | Chronological account of closed research routes and how each exposed the next problem |
| [formation/](formation/README.md) | Runtime-owned fixture producers, constraint binding, and foreground consumption; not yet a general runtime |
| [trajectory/](trajectory/README.md) | Harness-owned fixture validation, assignment, provenance, and witness checks; not yet a general harness |
| [contact/](contact/README.md) | Narrow executors for bounded exploratory and validation contacts |
| [tests/](tests/README.md) | Deterministic contract, separation, and fake-contact tests |
| `evidence/` | Retained contact records and future primary trajectories, with bounded computed verdicts and explanations |

## Evidence and authority

When sources disagree, prefer the most specific authority for the question:

1. Primary developmental lineage and trajectory evidence for what occurred.
2. Frozen scorers and their computed output for experimental verdicts.
3. Reviewed experiment and mechanism specifications for the contacted contract.
4. The authority and record specifications for cross-experiment boundaries.
5. The concept document for working definitions and research questions.
6. This README for the project story, present state, and routing.
7. Plans and build documents for intended work.

Research history explains how the project arrived here. It does not override a
specification, evidence record, scorer, or current route.

Retained contacts occupy the first two classes only for their own bounded
questions. Their computed Formation verdicts remain null; no beneficial
Formation effect has been earned. Plans, fixtures, and functional frameworks
cannot promote themselves into evidence.

## Working here

Run `uv sync` once to create the locked Python 3.14 environment. Run the full
deterministic and fake-contact suite with `uv run pytest -q`.

Before substantive work:

1. Read this page and the nearest directory README.
2. Name whether the task serves the current empirical problem, the
   deterministic supporting lane, concept formation, or later validation.
3. For mechanism or validation work, state what would distinguish the proposed
   account from retrieval, answer copying, prompt accumulation, or harness
   assistance.
4. For exploration, name the question, observation of interest, model and
   interface, budget, stopping rule, and evidence destination. Record external
   consequences and branch information when the experiment uses them. For
   validation, also freeze the same-model baseline, transfer target,
   non-transfer case, oracle, replication plan, and prospective verdict before
   contact.
5. Keep claims at the maturity actually supported by code and evidence.

The governing route is [concept](docs/CONCEPT.md),
[authority](docs/AUTHORITY.md), [record](docs/RECORD.md),
[evaluation](docs/EVALUATION.md), [plan](docs/PLAN.md), [fixture](docs/FIXTURE.md),
[instrument map](docs/INSTRUMENTS.md), and [build boundary](docs/BUILD.md).
The current result and active empirical question appear only in
[Present state](#present-state). Do not infer the active route from an older
specification, evidence account, or plan entry. No new model search, admission
packet, or procedural review program is on this route.
