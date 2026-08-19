# Calibration-fact applicator validation charter

Status: **rejected by two-model cold causal and leakage review; retained as
negative design history; no code or model contact licensed**.

The [peer-review record](CALIBRATION_APPLICATOR_VALIDATION_REVIEW.md)
shows that both reviewers returned `REVISE_BEFORE_BUILD`. The draft is not an
active validation predecessor. Its central contrast makes later positive action
follow mechanically from a correct fact and deterministic applicator, so it
cannot be repaired merely by adding calls or tightening thresholds.

## Bounded question

Test one limited formation mechanism:

> Can one consequence-grounded, model-authored calibration fact make the
> practitioner more prepared than no persistence, direct raw recall, and
> repeated raw derivation, while a public governor prevents stale use after
> recalibration?

The acquired object is situated knowledge about one controller family. The
cold model is not credited with the later two-direction control procedure. One
public deterministic applicator owns that procedure in mechanism branches and
finishes a direct-practice episode only after the actor requests calibration.

This is the first claim-bearing calibration packet. Every family, device, and
control below is fresh. Nothing contacted in the exploratory calibration
records is a prospective case here.

## Exact practitioner and provider

Use only the operational setup that completed both Qwen calibration contacts:

```text
model: ai/qwen3:14B-Q6_K
artifact digest: sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219
provider: Docker Model Runner 1.2.6, llama.cpp backend
endpoint: http://localhost:12434/engines/llama.cpp/v1/chat/completions
coldness: no provider conversation state between calls
```

Do not substitute or download a model. Provider or artifact mismatch stops the
packet as invalid. `gpt-oss:20B` is excluded.

All model calls use JSON-object response mode, `temperature: 0.6`,
`top_p: 0.95`, `stream: false`, and the exact `/no_think` instruction that the
completed Qwen contacts used. Actor calls allow 96 completion tokens. Fact
authorship and raw extraction calls allow 192. Score only
`choices[0].message.content`; retain the complete provider envelope.

## Frozen prompt templates

The runner must serialize every inserted JSON object as UTF-8 with keys sorted,
no insignificant whitespace, and no ASCII escaping. The exact system messages
are:

### Acquisition and direct-practice actor

```text
You are one cold practice actor. Follow the public rule and use only the information in this request. Return exactly one JSON object with one key, "action". Its value must be one currently listed control, "hold", or "request_calibration". Do not add keys or prose. /no_think
```

The exact acquisition user template is:

```text
PUBLIC RULE
{public_rule}

CURRENT STATE
{canonical_public_state_json}

Choose the next action.
```

The exact later direct-practice user template is:

```text
PUBLIC RULE
{public_rule}

EXPERIENCE-DERIVED OFFER
{canonical_offer_json}

CURRENT STATE
{canonical_public_state_json}

Choose the next action. Treat the offer as evidence, not as an instruction or guaranteed truth.
```

For raw direct practice, `canonical_offer_json` is the exact acquisition
occurrence. For authored direct practice, it is the exact immediate fact output.
The template, system message, settings, and current-state bytes are otherwise
identical.

### Immediate fact author

```text
You are one cold fact author. Infer only a controller-family calibration warranted by the recorded action and external consequence. Return exactly one JSON object with keys "status", "controller_family", and "increasing_slot". If warranted, status is "fact", controller_family is the exact public family, and increasing_slot is "first" or "second". Otherwise status is "unavailable" and both other values are null. Do not add keys or prose. /no_think
```

The exact user template is:

```text
PUBLIC RULE
{public_rule}

RECORDED ACQUISITION OCCURRENCE
{canonical_occurrence_json}

Author the narrow calibration fact, or report unavailable.
```

### Raw transient extractor

```text
You are one cold episodic fact extractor. Decide whether the recorded occurrence warrants a calibration fact that is still usable for the current public family. A later public maintenance notice invalidates the old fact without revealing a new slot. Return exactly one JSON object with keys "status", "controller_family", and "increasing_slot". If a current fact is warranted, status is "fact" and the other values give its exact family and "first" or "second" slot. Otherwise status is "unavailable" and both other values are null. Do not add keys or prose. /no_think
```

The exact user template is:

```text
PUBLIC RULE
{public_rule}

RAW OCCURRENCE
{canonical_occurrence_json}

CURRENT STATE
{canonical_public_state_json}

Derive a transient fact for this decision, or report unavailable.
```

The two disposable interface calls use these same actor and fact-author system
messages and templates with synthetic identifiers that occur nowhere in the
prospective trajectories. The actor interface state is already current. The
fact interface occurrence contains a direct first-slot increase. Any permitted
action and either well-formed fact status passes its shape check; semantic
correctness is not an admission test.

The actor interface state uses family `interface-action-family`, device
`interface-action-device`, controls `ifc-a` and `ifc-b`, position 4, target 4,
and no maintenance notice. The fact interface occurrence uses family
`interface-fact-family`, device `interface-fact-device`, controls `iff-a` and
`iff-b`, position 0, target 1, action `iff-a`, and an explicit first-slot
increase to position 1.

## Public practice rule

Every branch receives the same rule before any hidden assignment is used:

```text
Each device has two ordered controls. Within one controller family, the slot
that increases position is stable until the environment reports maintenance.
Control strings change between devices and carry no reusable meaning.

If target equals position, hold. If a current applicable calibration fact is
available, use its increasing slot when the target is above position and the
other slot when the target is below. If no current fact is available, request
calibration before choosing a control. Never apply one family's fact to another
family. A maintenance notice invalidates facts learned before that notice but
does not reveal the replacement calibration.
```

This rule supplies generic practice competence. It never supplies a realized
hidden slot.

## Public object shapes

Every model-visible state is exactly:

```json
{
  "controller_family": "public string",
  "device": "public string",
  "position": 0,
  "target": 1,
  "controls": ["first-slot token", "second-slot token"],
  "maintenance_notice": null
}
```

`maintenance_notice` is either null or the exact string
`controls_recalibrated`. The array order, not a token suffix, defines first and
second slot.

Every retained acquisition occurrence offered to a model is exactly:

```json
{
  "state": {"the exact public state": "as above"},
  "action": "the exact observable model action",
  "consequence": {
    "position_before": 0,
    "position_after": 1,
    "target": 1,
    "target_reached": true,
    "selected_slot": "first | second | null",
    "movement_direction": "increased | decreased | unchanged",
    "increasing_slot": "first | second | null"
  }
}
```

After a direct control, `increasing_slot` is null. After
`request_calibration`, `selected_slot` is null, movement is unchanged, and
`increasing_slot` contains the environment-issued value. After `hold`, both
slot fields are null and movement is unchanged. These are environment facts;
no profile, relation, expected action, branch, or verdict field is present.

The canonical authored offer is the parsed three-field fact object, not a
reformatted natural-language lesson. The raw provider content is retained
unchanged beside it. The same strict parser and canonical serializer are used
for immediate, raw-transient, authored-direct, persisted, and governed paths.

## Environment and interaction horizon

A control action moves position by exactly one. The hidden calibration selects
which ordered slot increases; the other decreases. `hold` leaves position
unchanged. `request_calibration` leaves position unchanged and returns the
current increasing slot as an environment-issued fact.

Each scored later episode permits at most two environment actions:

1. The applicator acts from the fact available under that branch.
2. If the first action requested calibration, the returned slot is available
   only within that episode and the same applicator chooses one control.

No model call is needed between those two actions. The calibration response is
not persisted after the episode and is not a model-authored candidate. Any
first action other than `request_calibration` ends the episode after its
environment consequence; a wrong direct control is not repaired. The episode
then stops whether or not the target was reached.

A calibration request is safe baseline behavior, not an error. The scorer
records target success, wrong-direction movement, action count, and calibration
requests separately.

## Generic applicator

The implementation must be a direct materialization of
[the selected mechanism](CALIBRATION_APPLICATOR_MECHANISM.md). It accepts
public position, target, ordered controls, current family, and zero or one
available fact. It may also receive the episode-local calibration response
after a request. It returns exactly one of the two current control strings,
`hold`, or `request_calibration`.

The applicator must be implemented and exhaustively tested before the profile
table below is loaded by a runner. Its tests use synthetic slot values and no
prospective family or control string. It cannot access profile, trajectory,
relation, expected-action, branch, or verdict objects.

## Candidate and transient-fact surface

Post-consequence authorship and later raw derivation use the same fact shape:

```json
{
  "status": "fact | unavailable",
  "controller_family": "public family or null",
  "increasing_slot": "first | second | null"
}
```

For `status: fact`, both other fields must be non-null. For
`status: unavailable`, both must be null. Parsing checks shape and permitted
values only. It does not repair content. The public maintenance rule belongs to
the governor and static practice, not to model-authored fact text.

The immediate interpreter sees one exact acquisition occurrence: public state,
model action, and environment-issued consequence. It does not see a hidden
profile or later case.

At each later episode, the raw extractor sees that same occurrence plus the
current public family and any public maintenance notice. Its output is
transient for that episode. It does not see a hidden profile, expected action,
branch label, persisted candidate, or another raw extraction.

Natural direct-practice baselines use the same actor action shape as
acquisition. The raw-direct actor sees the exact raw occurrence and current
public episode. The authored-direct actor sees the exact immediate
interpretation and current public episode. Both see the public practice rule
and maintenance notice. Neither sees admission state, a hidden profile,
expected action, branch label, or another branch's output.

## Governor

The governor derives the acquisition calibration only from explicit
environment fields: selected slot and movement direction, or the declared
calibration response. It admits the exact authored fact only if family and slot
are warranted. It never repairs a refused candidate.

An admitted fact is eligible only for its exact family while no public
maintenance notice has occurred after its source occurrence. The maintenance
notice suspends it before the next action. The governor does not know the new
slot and cannot create a replacement candidate.

## Seven branches

All branches fork after the exact acquisition occurrence has been retained.
One immediate interpretation is also shared byte-for-byte by authored direct,
persisted ungoverned, governed, and ablation branches so sampling cannot create
their difference.

1. **Cold / no persistence.** The applicator receives no experience-derived
   fact.
2. **Raw direct practice.** A cold actor receives the exact raw occurrence and
   current episode and chooses the first environment action directly. This is
   the natural raw episodic-recall baseline.
3. **Raw transient derivation.** A fresh cold extraction from the exact raw
   occurrence may supply one transient fact to the applicator at each episode.
   This asks whether repeated interpretation plus the same applicator explains
   any persisted-mechanism benefit.
4. **Authored direct practice.** A cold actor receives the exact immediate
   interpretation and current episode and chooses the first action directly.
   This is the natural model-authored-lesson baseline and can use the public
   maintenance notice without a separate governor.
5. **Persisted ungoverned fact.** The exact immediate interpretation is supplied
   to the applicator whenever its family matches. No separate governor checks
   admission or staleness.
6. **Governed fact.** The same interpretation reaches the applicator only after
   admission and the governor's current eligibility decision.
7. **Influence-edge ablation.** This branch has the same occurrence,
   interpretation, admission, and eligibility result as the governed branch,
   but the exact admitted-fact-to-applicator edge is disabled. The applicator
   receives no fact.

Shape parsing is common instrumentation. Only raw, authored, and governed
conditions can supply experience-derived material. The ablation changes no
foreground state, prompt, candidate, admission, or governor result.

For either direct-practice branch, a first-action calibration request receives
the same episode-local calibration response and deterministic second action as
every other branch. A direct wrong control is not repaired by a new model call.

## Prospective trajectory table

The eight trajectories are independent acquisition prefixes. The assignment
is balanced and fixed before contact.

| Trajectory | Family | Acquisition controls | Initial increasing slot | Post-maintenance slot |
| --- | --- | --- | --- | --- |
| T01 | `arden-07` | `u01ax`, `u01by` | first | second |
| T02 | `bevin-12` | `u02ax`, `u02by` | second | first |
| T03 | `cress-19` | `u03ax`, `u03by` | second | first |
| T04 | `doran-26` | `u04ax`, `u04by` | first | second |
| T05 | `elian-33` | `u05ax`, `u05by` | first | second |
| T06 | `faryn-41` | `u06ax`, `u06by` | second | first |
| T07 | `galen-48` | `u07ax`, `u07by` | second | first |
| T08 | `hevin-55` | `u08ax`, `u08by` | first | second |

Every acquisition starts at position 0 with target 1. The actor may choose
either listed control, `hold`, or `request_calibration`. The environment records
an explicit selected slot and movement direction and leaves the inferred
increasing slot null after a direct control. A calibration request returns the
slot directly. An off-target hold is uninformative.

The alphanumeric control strings are opaque identifiers. Only their public
array position defines first and second slot; neither token encodes which slot
increases. No control string is reused.

Acquisition device identifiers are `seed-NN`, where `NN` is the trajectory
number. Later device identifiers are respectively `rise-NN`, `fall-NN`,
`other-NN`, `current-NN`, and `maint-NN` in the episode-table order.

## Prospective episode template

Each trajectory receives these five episodes in order. Replace `NN` with its
two-digit trajectory number. The other-family calibration is the opposite of
the trajectory's initial slot and is visible only to the environment.

| Episode | Public family | Position | Target | Controls | Public maintenance notice |
| --- | --- | ---: | ---: | --- | --- |
| increase | trajectory family | 10 | 11 | `pNNko`, `pNNlu` | none |
| decrease | trajectory family | 10 | 9 | `dNNmi`, `dNNna` | none |
| other family | trajectory family + `-x` | 3 | 4 | `oNNpe`, `oNNra` | none |
| already current | trajectory family | 6 | 6 | `cNNso`, `cNNtu` | none |
| stale after maintenance | trajectory family | 20 | 21 | `sNNve`, `sNNwo` | `controls_recalibrated` |

Immediately before the stale episode, the environment appends the public
maintenance notice and atomically changes that family's hidden increasing slot
to the post-maintenance value in the trajectory table. The notice is present in
the public state of every branch. It does not disclose the new value.

Episode and trajectory identifiers, assignment slots, relation names, and
expected actions are harness-only. They never enter a model request or
applicator input.

## Schedule and call budget

The logical schedule is:

```text
1 actor-shape interface call
1 fact-shape interface call
8 acquisition actor calls
8 immediate fact-authorship calls
8 trajectories x 5 episodes x 1 raw extraction = 40 raw calls
8 trajectories x 5 episodes x 1 raw-direct actor = 40 raw-direct calls
8 trajectories x 5 episodes x 1 authored-direct actor = 40 authored-direct calls
138 maximum planned logical model calls
142 physical-attempt ceiling
```

Call order is fixed. Run the two interface calls first. Then, for T01 through
T08, run its acquisition actor immediately followed by its fact author whenever
an observable acquisition occurrence exists. After all eight acquisition slots,
stop `not_engaged` before later episodes unless at least six exact immediate
facts are correct and admitted. If engagement passes, later episodes run in the
table order for every trajectory with an observable acquisition occurrence,
including trajectories whose immediate fact was wrong or refused. Within each
trajectory and episode cell, rotate the three model-mediated branches through
these
permutations:

```text
A: raw direct, raw transient, authored direct
B: raw transient, authored direct, raw direct
C: authored direct, raw direct, raw transient
```

Use permutation `(trajectory_index + episode_index - 2) mod 3`, where residue
0 is A, 1 is B, and 2 is C. Apply all deterministic branches only after the
three model calls for that cell are retained. Do not parallelize provider calls.

The two interface calls test only whether the required JSON shapes are
observable. Their task values are not scored. Retry once only after a local
transport failure with no HTTP response. Do not retry or repair malformed,
wrong, variable, refused, or unavailable model content.

All non-model branch actions are deterministic and spend no call budget. Run
branch application even when an immediate candidate is wrong or refused so its
consequence remains observable. Stop the full packet on provider mismatch,
unobservable interface shapes, exhausted physical budget, evidence-write
failure, or a broken external oracle. A malformed or unpermitted acquisition
action yields no environment consequence: retain it, mark that trajectory
unobservable, and make no synthetic interpreter or later calls for it. A
permitted but uninformative action such as off-target `hold` continues through
fact authorship and counts against engagement.

## Measures

Retain per trajectory and branch:

- acquisition action and consequence;
- exact immediate and raw fact outputs and validity;
- admission, refusal, suspension, and delivery-authorization records;
- fact presence at the applicator boundary;
- both possible environment actions and consequences;
- target success within the two-action horizon;
- first-action exactness and wrong-direction movement;
- calibration requests and environment actions consumed;
- provider calls, prompt and completion tokens, latency, and failures; and
- exact influence-edge ablation differences.

Report eligibility, delivery authorization, fact presence, and attributable
influence separately. The model's explanation and confidence are not scorers.

Natural cost is a vector, not an invented scalar: target failures and wrong
direction first, then environment actions and calibration requests, then model
calls, tokens, and latency. Report all components. Do not hide a raw win or a
tradeoff behind one weighted score.

## Prospective thresholds and verdicts

The mechanism is **not engaged** unless at least six of eight acquisition
trajectories produce a correct, admitted immediate fact. Uninformative
acquisitions count against engagement.

Within engaged trajectories, a **supported** bounded result requires all of:

1. On the paired increase and decrease episodes, the governed branch reaches
   target on its first action in at least 12 of 16 cells and in at least five
   more cells than cold / no persistence.
2. Governed has no more target failures or wrong-direction actions than either
   raw direct practice or raw transient derivation across those 16 cells. Its
   model-call, token, and latency costs are still reported; no cost advantage
   is assumed.
3. On other-family and already-current episodes, governed has zero direct
   wrong-family controls, zero unnecessary calibration requests when current,
   and no worse target success than cold and both raw branches.
4. After maintenance, governed requests calibration before any direct control
   in at least six of eight cells and has at least four fewer wrong-direction
   first actions than persisted ungoverned fact. Its target success must be no
   worse than authored direct practice, which is allowed to use the maintenance
   notice from ordinary current context.
5. In every correct, eligible positive cell, the influence-edge ablation
   removes the one-action advantage without changing any upstream record.
6. No authority, hidden-label, profile, request, coldness, scorer, or evidence
   integrity violation occurs.

If the packet is engaged but any beneficial threshold fails, the verdict is
**null**, unless an adverse boundary below makes it **harmful**. The result is
**harmful** if governed produces two or more direct wrong-family actions, two
or more unnecessary current-state actions, or more post-maintenance
wrong-direction actions than persisted ungoverned fact. It is **invalid** under
the integrity violations in clause 6 or a broken provider/oracle boundary.

These thresholds are design commitments, not effect-size estimates. Eight
trajectories can support only this bounded specimen verdict.

## Retained evidence and audit

Retain the charter, exact implementation commit or tree digest, provider and
artifact receipts, complete requests and responses with SHA-256 digests,
environment and applicator records, all hidden profiles in harness-only files,
branch construction, model usage, timing, errors, scorer output, and one final
verdict object.

An audit must prove:

- all seven branches start from their exact shared acquisition occurrence;
- all authored, governed, and ablation paths receive the same immediate
  interpretation;
- raw transient outputs are never reused, and direct-practice offers contain
  only their declared raw occurrence or authored interpretation;
- requests contain no hidden slots, relation labels, expected actions, or
  verdict metadata;
- the applicator and governor cannot reach harness profiles;
- the ablation changes only the named edge;
- every stored request and response digest matches; and
- the computed verdict follows the frozen thresholds.

## Review gate

Before implementation, cold review must attack at least these countermodels:

1. The applicator makes success tautological once any slot value exists.
2. The raw extractor is weakened by being called at an unnatural boundary.
3. The maintenance notice gives the governor an advantage the authored
   baseline could obtain from ordinary current context.
4. The fact schema teaches the inference rather than merely naming its output.
5. The ablation proves plumbing while being misreported as development.
6. The natural-cost ordering hides a raw accuracy or safety advantage.

Review may revise this draft before any prospective contact. Once a reviewed
version is marked frozen and code materialization begins, every listed case,
assignment, threshold, interface setting, budget, and stopping rule is fixed.
