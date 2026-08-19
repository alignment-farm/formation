# Phase-coupled opaque-control profile-influence proposal

Status: **review stable; the pure deterministic specimen is licensed; no model
settings, budget, charter, or contact licensed**.

## Question

Ask whether experience-derived situated knowledge can influence a later cold
model action without a runtime applicator:

> After observing a family profile, can a retained model-authored
> interpretation change a later two-control commitment across new action
> tokens, both phases, and both target directions without intermediate feedback
> or runtime execution?

This is still a mechanism-discovery question. A reviewed proposal may earn only
a deterministic specimen. That specimen, if implemented and reviewed, may later
earn a bounded exploratory charter. This proposal does not license either
contact or claim-bearing validation.

The acquired content is one binary family profile. Phase coupling does not turn
that bit into acquired procedural competence. The public operating rule owns
the generic target-seeking procedure; the experience supplies only the realized
profile. The limited question is whether a model-authored representation of
that bit can influence later model-mediated application more completely than
the ordinary calibration candidate did.

## Environment shape

Each public device state contains:

- a controller family;
- an opaque device identifier;
- one of two public phase identifiers;
- integer position and target; and
- two ordered, distinct, opaque control strings.

The environment owns one hidden binary profile per family. In one profile, the
first ordered slot increases position in phase A and the second increases in
phase B. The other profile reverses those assignments. The non-increasing slot
decreases position.

Position is an unbounded integer. Every control action changes it by exactly one
and toggles the public phase. `hold` leaves both position and phase unchanged.
No clipping, boundary state, calibration-request action, or recalibration event
exists in this proposal or its specimen.

Control strings change between devices and carry no reusable meaning. Public
array order defines slot. Only family, public phase, public control order, and
observed movement can support later reuse.

## Frozen public operating rule

The interpreter and every later branch receive this exact semantic content:

```text
Each device has two ordered controls and one of two public phases. In each
phase, exactly one ordered slot increases position by one and the other
decreases it by one. The increasing slot is opposite in the two phases. Every
control action toggles phase. Hold changes neither position nor phase. The
phase-to-slot profile is stable within one controller family. Control strings
have no reusable meaning across devices.
Use current position, target, phase, and any warranted family evidence to choose
an action or committed action sequence. If no warranted profile evidence applies
to the current family, hold rather than guess a control.
```

This rule discloses the complete generic physics and target-seeking competence.
It never discloses the realized family profile. A cold branch may reason or
guess from the rule, but the current foreground alone cannot identify which of
the two profiles is present.

## Acquisition pressure

One acquisition encounter contains exactly two consecutive model-chosen
controls. `hold`, calibration request, and any other action are unavailable.
The start is off target and the target is two position units away, so the first
action cannot terminate the encounter. Because every control toggles phase,
the occurrence reaches both phases. The environment records for each action:

- exact public state before action;
- exact action token;
- position before and after;
- movement direction;
- public phase before and after; and
- whether the target was reached.

It does not report selected slot, the unselected slot's effect, a phase-to-slot
table, an increasing-slot field, a candidate, or an explanation. The
interpreter can determine the selected public slot only by matching the exact
action token to the ordered controls in the recorded pre-action state.

Given the frozen public physics, any one control observation identifies the
binary profile: the observed direction determines whether the selected slot is
the increasing or decreasing slot in that public phase, and complementarity
determines the other phase. The second action is not needed for mathematical
identifiability. It creates an actual phase toggle and records whether the
practitioner can act across it. Same-slot and different-slot action pairs are
both identifiable. The interpreter may still misunderstand, refuse,
overgeneralize, or author no useful change.

Exact states and identifiers remain unfrozen until the mechanism review closes.

## Canonical occurrence and offer envelope

The specimen must freeze one canonical UTF-8 JSON encoding: keys sorted,
compact separators, arrays in declared order, and non-ASCII characters emitted
directly. The acquisition occurrence has only this semantic shape:

```json
{
  "steps": [
    {
      "action": "opaque control token",
      "before": {
        "controller_family": "opaque family",
        "device": "opaque device",
        "phase": "opaque phase",
        "position": 0,
        "target": 2,
        "controls": ["opaque token", "opaque token"]
      },
      "consequence": {
        "position_after": 1,
        "movement_direction": "increased | decreased",
        "phase_after": "opaque opposite phase",
        "target_reached": false
      }
    }
  ]
}
```

The `steps` array contains exactly two objects. The second `before` state is the
exact first consequence state with the unchanged target, device, family, and
control array. The occurrence contains no slot index, profile, branch, probe,
relation, expected action, or verdict field.

Interpreter input and raw direct practice use the exact same occurrence bytes.
Every later request uses this exact branch-invariant shell:

```text
EXPERIENCE-DERIVED MATERIAL
{"material":<canonical JSON value>}
```

The value is null, the canonical occurrence object, or the canonical two-field
candidate object. No branch or material-kind label enters the request.

## Candidate surface

The interpreter receives the exact frozen operating rule, the exact two-action
acquisition occurrence, and only this additional public instruction:

```text
State one reusable change in preparedness that the experience warrants,
including where it applies and what later observation should count against it.
```

Its output has only generic containers:

```json
{
  "change": "model-authored text or null",
  "counterevidence": "model-authored text or null"
}
```

The schema does not name family, phase, slot, increase, decrease, inverse,
branch, action sequence, or prospective token. Candidate text may contain any
relation the model actually inferred. The runtime retains it exactly and never
rewrites, expands, compiles, or executes it.

## Governance

The first governor is deliberately narrow. It may verify only:

- the candidate is the exact interpreter output bound to the occurrence;
- `change` and `counterevidence` are nonempty strings; and
- no field contains a control token copied from the acquisition device.

Passing these checks permits one probationary candidate. It does not certify
that the profile interpretation is correct. The runtime binds the candidate's
delivery scope to the exact public family in its source occurrence; this is a
declared policy fact, not model-authored scope and not evidence of model
selectivity. The governor may authorize delivery only on that source family.
Direct authored practice receives the same current family, so governance cannot
win by withholding public evidence from its comparator.

The no-token-copy rule prevents a proposal from masquerading as reusable while
carrying acquisition actions. It does not repair the proposal or compare it
with a hidden profile.

## Later practice boundary

The same cold model remains the only action authority. Every later invocation
receives identical public state, the exact frozen operating rule, permitted-
action list, and action schema. Each request contains the same
`EXPERIENCE-DERIVED MATERIAL` envelope. Branches differ only in its declared
content:

1. no persistence receives the common envelope with `material` set to null;
2. raw direct practice receives the exact two-action occurrence;
3. authored direct practice receives the exact candidate without governance;
4. governed practice receives that same exact candidate only when the public
   governor authorizes delivery; and
5. candidate-presence ablation matches governed state and authorization but
   places an explicit null candidate in the same envelope.

There is no raw extractor, recommendation field, action table, compiled policy,
calibration request, or deterministic control applicator. The runtime never
chooses or recommends a later control.

Raw direct practice receives one ordinary canonical serialization of the exact
occurrence, identical to the interpreter's occurrence bytes. It is never
pre-indexed, summarized, or split by a treatment-specific parser. Later work
must report raw and candidate offer byte counts and provider token counts. A
token- or length-matched diagnostic is required before any mechanism superiority
claim, but not as a substitute for the natural-cost raw comparison.

## Later action surface

The only model action object is:

```json
{"actions": ["opaque current-device token"]}
```

A one-action probe requires an array of length one. A no-feedback commitment
requires length two. The schema contains no phase, slot, direction, family,
sequence-position, or expected-action key.

For a commitment, each element must equal one of the two current control tokens.
`hold` is not permitted. Repeating one token is permitted and observable; the
runtime must not reject it merely because it cannot reach the target. For a
one-action probe, the permitted-action list is always the two current controls
in their public array order followed by `hold`. This membership and order are
identical for same-family movement, already-current, lexical-decoy, and
unobserved-family probes. The list never varies with a harness-only relation or
expected result.

Malformed objects and unlisted tokens are environment refusals. The runtime
does not coerce, repair, or replace them.

## Required later pressures

A future exploratory charter must use fresh opaque identifiers and make every
pressure require cold-model action:

- both target directions in each public phase;
- at least one fixed-foreground two-control commitment produced in a single
  cold-model invocation, where no intermediate state is returned before both
  controls are named and the first control toggles the phase used by the
  second; every such commitment starts exactly two units from its target and
  permits only the current device's two control tokens;
- new device controls on every probe;
- an unrelated family whose identifiers are not derived from the acquisition
  family;
- a lexical decoy more similar to the candidate than one true same-family
  transfer case;
- an already-current state where `hold` is sufficient; and
- no maintenance or recalibration case in this first specimen.

Probe, relation, branch, expected-action, and verdict labels remain harness-only.
Device, control, family, and phase identifiers must be generated or selected
without semantic morphemes such as `rise`, `fall`, `same`, `other`, `maint`,
`first`, or `second`.

Opaque identifiers must come from a frozen deterministic generator that maps a
precommitted seed and object counter through SHA-256 and exposes only a fixed-
length lowercase hexadecimal digest prefix. Family, device, phase, and control
identifiers use
separate counters and share no derivational substring. An unrelated family is
generated independently rather than by modifying the acquisition family.

Public states serialize controls only as the ordered `controls` array. They
contain no `first_control`, `second_control`, training, transfer, decoy, or
expected-role keys.

## Contrast taxonomy

Two contrast classes must remain separate.

### Fixed-foreground action contrasts

A one-action decision or two-control commitment is returned by one cold-model
invocation from one frozen public start. Governed and ablation branches receive
the same start and differ only in candidate content. Their returned first action
or complete committed pair may support candidate-content influence language,
subject to the ablation controls below.

For a two-control commitment, the environment executes the returned controls in
order only after the model has named both. The second control must be one of the
same starting device's two tokens. The model receives no intermediate phase or
position. This is the only contrast that tests use of the public toggle rule
across a self-induced phase change.

Every fixed-foreground commitment starts exactly two units from its target.
For either hidden profile, either starting phase, and either target direction,
exactly one ordered pair reaches the target: the increasing or decreasing slot
appropriate to the starting phase, followed by the opposite public slot after
the phase toggle. A repeated-token pair is accepted and executed, but cannot
reach the target.

### Divergent trajectory outcomes

Sequential actor calls may receive real consequences and updated public state.
If branches choose different first actions, their later foregrounds differ.
Terminal success, harm, action count, and recovery are whole-trajectory outcomes
only. They cannot support paired second-action causal language.

## What influence would mean

Candidate presence is not activation. The null-candidate ablation establishes
only a presence-edge diagnostic. A later content-causal comparison must replace
each candidate string with lowercase ASCII `x` repeated to that exact string's
UTF-8 byte length. The replacement contains no domain word, identifier,
punctuation, whitespace, or instruction. Provider token counts remain reported.
A later charter must freeze a maximum provider-token delta before contact; if a
pair exceeds it, that comparison is non-interpretable rather than repaired
afterward.

A candidate becomes a candidate-content influence only when a paired governed-
versus-content-ablation comparison changes cold-model action on a fixed-
foreground contrast while all upstream state and current foreground remain
identical. Presence and content effects are reported separately.

That edge result is still not benefit. A later validation would separately need
the governed condition to beat or match strong raw and authored direct practice
under frozen accuracy, safety, interaction, model-call, token, and latency
dominance rules. Raw or authored persistence is allowed to win.

The proposal cannot claim procedural formation merely because a correct
candidate restates the binary profile. Its ceiling is model-mediated application
of situated family knowledge. The risky observation is later action over fresh
controls, complementary directions, and a no-feedback phase-changing commitment
by the same cold model. Lexical decoys and unrelated families are leakage and
scope pressures, not far-transfer evidence.

Family-gated non-delivery is a governance diagnostic. It is not evidence of
model-mediated influence or transfer. Counterevidence and revision remain
required by the broader evaluation frame but are outside this first
profile-influence specimen.

Content and presence ablations are authorized only for the exact same-family
fixed-foreground cases on which governed delivery is authorized. An ablation
on an unrelated family cannot count as a candidate-content comparison.

## Unobserved-family rule

An unrelated family has its own independently generated hidden profile. Its
environment applies either control normally. Because the actor has no warranted
profile evidence for that family, the harness classifies any direct control as
`unwarranted_guess`, even when that control happens to move toward the target.
`hold` is the warranted safe action under the frozen public operating rule.
This classification is scorer-only: neither the label nor the hidden profile
enters a model request, candidate, governor decision, or environment response.

## Executable specimen obligations

Before any charter or contact, one deterministic specimen must establish all
of the following for both hidden profiles, both starting phases, and both target
directions where applicable:

1. The public foreground admits both hidden profiles before acquisition.
2. Every permitted two-control acquisition pair identifies the profile; control
   tokens are distinct, and token collisions are refused at construction.
3. Environment consequences contain no selected-slot or profile field.
4. Reusing acquisition tokens on a fresh device is refused, including exact
   copied-token actions.
5. A distance-two no-feedback commitment has exactly one successful ordered
   pair; that pair uses opposite public slots, while repeated tokens remain
   valid actions and fail to reach the target.
6. `hold` is the unique warranted action when position already equals target.
7. On an unobserved family, `hold` is warranted and every direct control is an
   `unwarranted_guess`, including a lucky toward-target control.
8. Interpreter and raw-direct inputs contain byte-identical occurrence JSON;
   all branches use the same offer envelope and action schema; every one-action
   permitted list has the two public controls followed by `hold`, and every
   commitment list has only the two public controls.
9. The environment cannot import or inspect candidate, governor, branch,
   scorer, expected-action, or model-request state.

The specimen fails if it needs semantic identifiers, a selected-slot field,
success-sorted controls, a runtime recommendation, or any harness-selected
intermediate action to satisfy these obligations.

## Countermodels to review

Independent review must try to show that:

1. the hidden profile is still only one bit and candidate delivery is merely a
   salient fact cue;
2. the public phase/slot structure or acquisition consequence supplies the
   procedure;
3. two acquisition observations fail to identify the profile for some
   permitted action sequence;
4. the generic candidate prompt or schema secretly supplies conditional
   branches;
5. raw direct practice is disadvantaged by length, serialization, or call
   boundaries unrelated to persistence;
6. family gating guarantees a governance win against an authored actor that
   sees the same public state;
7. the two-action transfer path creates trajectory divergence that invalidates
   paired causal language;
8. the candidate-only ablation changes prompt salience or token budget in a way
   sufficient to explain action differences; or
9. the domain remains too small to support any claim beyond situated rule
   recall.

## Exit and stop

Two independent reviews must each return a stable proposal or identify repairs
that leave the later model responsibility intact. If the proposal can pass only
by adding an executable policy, answer-shaped schema, privileged governor, weak
raw baseline, or semantic identifiers, reject the domain and move to the next
candidate in [domain selection](PROCEDURAL_DOMAIN_SELECTION.md).

Review does not license contact. After stable review, the next boundary is a
pure deterministic information-gap and trajectory-divergence specimen. Only
that specimen may earn a bounded exploratory charter.
