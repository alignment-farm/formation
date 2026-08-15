# Formation

Formation studies how a language model that starts each call with no memory of
prior work can still become a particular skilled practitioner through later
experience. The model weights stay frozen. What must change is the governed
system around the model: what experience is kept, what changes are proposed,
which changes may affect later action, and how those changes are checked or
revoked.

Its working thesis is:

> A frozen, intermittently invoked model can develop into a particular
> practitioner when a governed system converts experience and consequence into
> durable, selective changes in future behavior that later counterevidence can
> revise, suspend, or revoke.

Here *cold* means the model itself carries no project memory between calls.
The *practitioner* is the model plus the developmental system that persists
across calls.

Game mastering, coding, writing, research, and operations are useful places to
test formation. None of them is the project. They are contact domains where
formation can be observed and adjusted.

## The question

The ordinary agent loop is good at continuing work:

```text
assemble context -> infer -> act -> observe -> append -> repeat
```

Appending an observation can change the next answer without earning a change
that should transfer to a later, related situation. More context is not the
same as development.

Formation adds a second, governed loop:

```text
practice loop:    orient -> decide -> act -> observe consequence
formation loop:   attribute -> propose change -> govern eligibility
                  -> activate selectively -> revise or revoke
```

A bounded trial may be part of governance. The project does not treat trial as
a required stage before every permitted influence.

The central research question is whether an experience can cause a warranted
change that improves action in a later, novel, structurally related situation,
and stays silent where that structure does not apply.

## The system boundary

Formation begins with three distinct roles:

- The **cold model** supplies inference. It is replaceable and receives no
  weight updates within the project boundary.
- The **formation runtime** acts with the model, preserves developmental
  lineage, and governs changes in the practitioner.
- The **trajectory harness** creates controlled histories, forks identical
  starting states, schedules environments and declared consequence oracles,
  assigns ablations, and captures evidence for prospective scoring.

The separation matters because of a concrete failure mode. If the harness
interprets a consequence and quietly hands the correct lesson to the model, the
experiment measures oracle assistance rather than formation.

## What counts as progress

A formation claim requires more than changed behavior. At minimum, the system
must show:

1. **Acquisition:** consequential experience causes a later behavioral change.
2. **Transfer:** the change helps on prospective cases that do not permit answer
   copying or simple episode matching.
3. **Selectivity:** the change stays silent where its structure does not apply.
4. **Revision:** later counterevidence can revise, suspend, or revoke an
   admitted change.
5. **Causal contribution:** ablation or controlled branching attributes the
   improvement to the acquired change.
6. **Net value:** the benefit survives the costs of context, checks, latency,
   maintenance, and negative transfer.

“Exceptional” is comparative. A formed practitioner must beat the same cold
model with static instructions and ordinary persistence on novel work, while
remaining governable.

## Relationship to Construct

[Construct](../construct/README.md) is the immediate experimental ancestor. It
produced bounded results on offer quality, consequence-earned authority,
cross-session influence, selective eviction and recovery, and governed
continuity. Formation accepts those results within their original evidence
bounds.

Formation does not inherit Construct's provisional runtime objects or
vocabularies as requirements. Those are prior art and candidate instruments.
Formation must earn its own objects and mechanisms.

Construct remains the lab that owns its findings and should stay reproducible.
New trajectory experiments and formation-runtime code belong here.

## Present state

No formation effect has been earned. What exists today is a reviewed account
of what the system may do, plus nine small code slices that prove identity and
role separation in one deterministic scenario.

The Phase 0 packet —
[concept](docs/CONCEPT.md), [authority](docs/AUTHORITY.md),
[record](docs/RECORD.md), [evaluation](docs/EVALUATION.md),
[fixture](docs/FIXTURE.md), and [instrument map](docs/INSTRUMENTS.md) — defines
roles, records, baselines, and refusal outcomes in Markdown. Independent
readers from two model families reconstructed one compatible semantic object
from that packet. Agreement on meaning closed the semantic gate. It did not
select a machine schema or prove any developmental effect.

Markdown serves as a semantic prototype here. It states who may decide what,
what must be recorded, what must be refused, and what result would prove the
account wrong. Independent readers then reconstruct the implied system without
seeing an implementation. Their disagreements expose missing or contradictory
rules before code turns those rules into incidental architecture. Code begins
only when the fixture needs a machine to compute identity, validation, or an
exchange between components.

The current code uses exact bytes where byte equality matters and typed objects
where equal-looking data must not be allowed to substitute for its source or
authority. Nine fixture-local slices are implemented and tested:

1. [Shared acquisition prefix](docs/MATERIALIZATION.md). Every fork starts from
   the same six developmental records as exact bytes with a content binding.
   Eleven tests refuse forged handoffs, replacement bytes, mutated sources,
   altered bindings, and post-binding tampering.
2. [Condition append](docs/CONDITION_APPEND.md). After the fork, each runtime
   records only its public formation condition. Hidden branch assignments stay
   in trajectory evidence. The six-line prefix stays unchanged. Twenty-six
   tests cover both this slice and the prefix.
3. [Admitted roots](docs/ADMITTED_ROOT.md). On the two treatment branches, a
   distinct interpreter authors one candidate from retained experience, and a
   distinct governor admits that exact proposal once within an explicit scope.
   The harness schedules and witnesses; it does not author or admit. Forty-five
   tests preserve and revalidate the source-to-admission chain.
4. [Replay-constraint append](docs/REPLAY_CONSTRAINT_APPEND.md). The ablation
   branch receives one public constraint bound at the exact admitted head. The
   slice does not implement constrained replay itself. Sixty-four tests cover
   the combined boundary.
5. [Shared foreground delivery](docs/FOREGROUND_DELIVERY.md). One protocol
   source is frozen once, then delivered once to each exact current branch
   head. The runtime returns the received value; the harness checks it against
   the same freeze. Eighty tests cover the combined boundary.
6. [Positive encounter opening](docs/ENCOUNTER_OPENING.md). Each exact received
   foreground becomes one runtime-authored `encounter opened` append and one
   new current root. A sealed binding keeps freeze and comparison-group state
   unreachable from developmental lineage. Ninety-six tests cover the combined
   boundary.
7. [Positive activation decisions](docs/POSITIVE_ACTIVATION_DECISION.md). The
   baseline applies the public activation policy to an empty eligible set and
   withholds. Governed activates the exact admission reached through its own
   encounter lineage and originates one privately held handoff. The ablation
   root remains excluded until constrained replay can derive its eligible set.
   One hundred seventeen tests cover the combined boundary.
8. [Practice-request construction](docs/PRACTICE_REQUEST.md). Baseline prepares
   a request with no intervention-shaped field. Governed consumes the exact
   private activation handoff once and places that object in its request. No
   prompt format or model invocation is selected. One hundred thirty-six tests
   cover the combined boundary.
9. [Deterministic model invocation](docs/MODEL_INVOCATION.md). One stateless
   actor capability receives both exact requests and alone issues their model
   proposal objects. The runtime records those proposals without committing an
   action. One hundred fifty tests cover the combined boundary.

These slices establish local identity, authority separation, and provenance
checks. They do not establish learning, transfer, governance effectiveness, or
any formation claim.

Some later steps are precise enough to describe but have not earned code.
Proposal and admission records do not yet need a byte format. Constrained
replay must derive its result from the preserved dependency history rather than
return a prepared answer for a known target. But one fixed example cannot show
whether code performs a general dependency traversal or merely validates that
example, so the project has not selected replay code or a replay schema.
Likewise, selective activation must carry the exact admitted change into one
model request and remain absent from withheld paths. Those same-runtime
identity checks still do not require an activation format.

Shared foreground delivery is now implemented. Independent review rejected two
green intermediate builds. The first could repeat or alter authority outside
one controller. The second delivered the right values to the right roots but
did not retain which exact freeze and comparison group had authorized them.
The repaired boundary rechecks source, authority, recipient lineage, freeze,
group, one-time consumption, and all three returned handoffs. It selects no byte
format and does not claim that an encounter opened.

Positive [encounter opening](docs/ENCOUNTER_OPENING.md) is now implemented.
Independent review rejected two green builds: one did not make the returned
roots current and allowed a second opener to reuse the handoff; the next leaked
private foreground provenance through a root verifier and allowed an alternate
controller path. The repaired boundary registers one opening authority, keeps
the full handoff outside developmental lineage, retires each predecessor at the
encounter layer, and returns three exact current encounter roots. A foreground
witness is now an input to an encounter append, but neither witness is a model
request, action, or evidence of formation.

Positive [activation decisions](docs/POSITIVE_ACTIVATION_DECISION.md) are now
implemented for the two roots that can decide from already materialized public
state. Baseline records consideration under the same public policy as governed,
but over an empty eligible set, and withholds. Governed selects the exact
admission and proposal retained by its encounter lineage, records activation,
and returns only a sealed binding to a private encounter-local handoff.
Independent review rejected a green build that allowed a cached decision input
to be replaced by the ablation branch's equal-looking admission. The repaired
boundary rechecks the exact condition, admission, and proposal at append time;
the combined 117-test suite and independent recheck pass.

Positive [practice requests](docs/PRACTICE_REQUEST.md) are now implemented for
baseline and governed. The baseline request has no intervention-shaped field.
The governed request consumes the exact private activation handoff once and
retains that object rather than copied admission or candidate fields.
Independent review rejected green states that accepted counterfeit verifiers,
restored rights by resetting guards, let a fake owner claim the registry, or
consumed a handoff outside live request preparation. The repaired boundary and
combined 136-test suite pass two final independent rechecks.

Deterministic [model invocation](docs/MODEL_INVOCATION.md) now exercises those
semantic requests without an LM. The same stateless actor proposes `release`
for baseline and `rebuild_then_release` for governed from request-visible roles.
Only the actor issues proposal capabilities; the runtime records them. Review
found and repaired a post-invocation verifier replacement path before the
combined 150-test suite and final recheck passed.

The lifecycle boundary remains deliberately split. A model proposal is not a
committed action, and the fixture actor is not evidence of model learning.
Ablation remains blocked on runtime-derived constrained replay.

The next named computation is now licensed in Markdown. The
[positive action-commitment contract](docs/ACTION_COMMITMENT.md) requires the
runtime to turn each exact actor-issued proposal into a distinct commitment
event and a sealed environment binding. It keeps proposal authorship, runtime
commitment, and later environment consequence separate. Implementation remains
pending.

The first engineering milestone is still ahead: a deterministic two-loop
framework that can represent a practice trajectory and a candidate change without
pretending the candidate is learned or useful. The first experimental milestone
comes later: a same-model trajectory comparison that can distinguish
consequence-governed formation from raw episodic recall and authored lessons.

## Project map

| Place | Responsibility |
| --- | --- |
| [docs/](docs/README.md) | Concept, research program, and implementation boundary |
| [formation/](formation/README.md) | Runtime-owned fixture producers, constraint binding, and foreground consumption; not yet a general runtime |
| [trajectory/](trajectory/README.md) | Harness-owned fixture validation, assignment, provenance, and witness checks; not yet a general harness |
| [tests/](tests/README.md) | Deterministic contract and separation tests |
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
functional frameworks cannot promote themselves into evidence.

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
