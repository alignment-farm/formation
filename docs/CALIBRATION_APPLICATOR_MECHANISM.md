# Calibration-fact applicator mechanism

Status: **coherent diagnostic architecture, but closed as the next
claim-bearing mechanism after two-model peer review; no contact licensed**.

## Decision

This direction was selected for review and then rejected as the next Formation
validation mechanism. The
[review record](CALIBRATION_APPLICATOR_VALIDATION_REVIEW.md) found that correct
later action would follow mechanically once a fact reached the applicator. The
design remains useful for studying fact caching, scope, suspension, and cost,
but not for attributing acquired procedural competence to later cold-model
action.

The next mechanism will treat the acquired object as a model-authored fact
about one controller family, not as a model-authored control procedure.

The fact has the narrow meaning:

```text
for controller family F, ordered slot S increases position
```

A generic runtime applicator, frozen before any hidden calibration is assigned,
converts an available fact and the current public device state into an action.
This is the smallest mechanism that addresses the failure found by the
[explicit-consequence contact](EXPLICIT_CONSEQUENCE_CONTACT.md): the model
authored the right fact but used it only for the direction named positively.

This choice studies acquired situated knowledge in a practitioner. It does not
test or claim that the cold model acquired a bidirectional procedure. The
practitioner includes the runtime, and the runtime supplies the generic
procedure openly.

## Why this direction comes first

The completed contact already located one exact missing edge. Candidate
authorship, consequence-grounded admission, and delivery succeeded in the
counter-prior world. Complete use failed. Asking the model to write a larger
conditional lesson would mix that failure with a new prompt and representation
question. A deterministic applicator instead makes the influence edge visible
and ablatable.

This is deliberately a limited scientific target. If the project later asks
whether a model can author and execute new procedure rather than supply a world
fact, that requires a separate mechanism and fresh evidence.

## Public generic applicator

The applicator is fixed before the environment assigns any family calibration.
It receives only:

- the public current position and target;
- the ordered pair of public controls on the current device;
- the current public controller family; and
- zero or one exact calibration fact available under the branch's declared
  persistence and governance condition.

Its rule is:

```text
target equals position
  -> hold

target differs and no applicable fact is available
  -> request_calibration

target is above position and an applicable fact is available
  -> choose the control in the increasing slot

target is below position and an applicable fact is available
  -> choose the control in the other slot
```

The applicator may compare the fact's public family with the current family. It
may not inspect a hidden profile, expected action, case label, future device,
or trajectory verdict. It may not infer a calibration from action tokens.

The realized hidden slot is a parameter learned after protocol freeze, never a
constant in the applicator or static practice instruction.

## Model responsibility

After the shared acquisition occurrence, a cold interpreter may author one
candidate fact from the exact situation, action, and environment-issued
consequence. The candidate must bind its family and slot. The model may be
wrong, malformed, overbroad, or silent. The runtime does not repair it.

The candidate representation should contain only the fact and its public
family scope. It must not contain current-device action tokens, a
case-conditioned action table, or prospective answers. The generic applicator
owns the already-public two-slot procedure, and the governor owns the public
maintenance invalidation policy. Neither is model-authored content.

## Governor responsibility

The governor may admit a candidate only when runtime-visible consequence facts
warrant its family and increasing slot. It may check scope against the
acquisition family and may later suspend or replace the fact after exact public
counterevidence. It may not use the hidden profile or prospective cases.

Admission establishes that the fact is warranted under the declared policy.
It does not establish benefit. Delivery authorization and fact presence remain
separate from attributable influence.

## Comparison branches

A later validation charter must begin from one shared recorded acquisition and
include at least:

1. **Cold / no persistence.** No acquired fact is available. The generic
   applicator holds when current and otherwise requests calibration.
2. **Raw episodic derivation.** The exact occurrence is supplied to a cold
   extractor at each later decision. Any well-formed transient fact it authors
   may enter the same applicator for that decision only. Nothing synthesized is
   persisted between decisions.
3. **Persisted authored fact.** The immediate post-consequence model-authored
   fact is available to the same applicator without a separate eligibility
   decision.
4. **Governed fact.** The exact candidate enters the applicator only after the
   declared governor admits it and the current situation passes public scope
   and status checks.
5. **Influence-edge ablation.** This branch matches the governed branch but
   prevents the admitted fact from reaching the applicator. The applicator
   therefore receives no fact and follows its ordinary hold-or-calibrate rule.

The raw branch is intentionally strong. It may match or beat persistence by
reconstructing the fact when needed. Its repeated model calls, tokens, latency,
and errors count at natural cost. A token-matched diagnostic may be added, but
it cannot replace that comparison.

All branches receive the same static explanation of ordered controls, family
stability, safe calibration, and the applicator rule. None receives the hidden
assignment unless its declared experience-derived path produces it.

## Attributable influence

For this mechanism, influence is not inferred from a request receipt. It is the
paired behavioral difference between the governed branch and its exact
influence-edge ablation when:

- both start from the same acquisition prefix;
- both hold the same admitted fact and governance state;
- only the public edge from that fact to the applicator is removed; and
- the deterministic external environment records the resulting actions and
  consequences.

Because the applicator is deterministic, this contrast can identify the fact's
effect on practitioner action. It cannot identify a hidden change in model
state or model reasoning.

## Fresh validation pressures

Before contact, a validation charter must freeze fresh families and action
tokens not used by either calibration exploration. It must include:

- both movement directions for every positive-transfer family;
- new devices and controls after acquisition;
- other-family cases where calibration must be requested;
- already-current cases where no fact is needed;
- a public maintenance or recalibration event that can make an admitted fact
  stale, followed by cases that require suspension and safe calibration;
- prospective scorer rules and complete natural-cost accounting; and
- enough repetitions to distinguish stable behavior from the two-repetition
  exploratory observations.

The governor must have a predeclared opportunity to help or hurt. A packet in
which authored and governed facts are always exposed identically cannot test
governance value.

The existing exploratory world says a calibration is stable within a family
without exception. Under that rule, an exactly warranted admitted fact cannot
become stale, so authored and governed branches have no natural reason to
separate after admission. A fresh validation environment must therefore state
in advance that calibration is stable only until an observable maintenance or
recalibration event. The event is public environment state, not a harness case
label. It does not reveal the new slot; it only invalidates the old fact and
licenses a new calibration request. Persisting a replacement fact after that
request is a later lifecycle question, not required by this first validation.

## Authority and leakage review

The selected mechanism is coherent only under these separations:

- The environment owns hidden calibration, movement, and any public
  maintenance event. It never writes a candidate or a prospective answer.
- The model owns the candidate family and slot value. The candidate schema may
  name the kind of fact but cannot contain the realized value or a control
  table.
- The governor checks exact candidate content against already recorded public
  consequence facts. It may suspend on a public maintenance event. It cannot
  infer from hidden profiles, expected actions, or case-family labels.
- The applicator owns only the generic two-slot computation. Its implementation
  and tests must be frozen before hidden assignments and must accept the same
  fact type from raw, authored, and governed paths.
- The trajectory harness assigns profiles, schedules branches, and scores
  retained actions. It cannot construct, repair, route, or revoke a candidate.
- The raw extractor receives the same candidate surface as the post-experience
  interpreter, but its transient output is derived again from the exact raw
  occurrence at each decision and is never retained.

Naming an `increasing_slot` field tells the model what kind of fact to report;
it does not reveal whether the value is `first` or `second`. That field is
therefore instrumentation, provided it is identical for raw and persisted
authorship and no branch-specific examples disclose a value.

The influence-edge ablation is expected to change applicator output whenever a
fact is necessary. That contrast establishes that the named edge works; it is
not by itself evidence that the acquired fact is beneficial. Benefit still
requires fresh external outcomes against cold, raw, and authored branches.

A calibration request is also not automatically an error. The validation
scorer must allow the environment to answer it and must price the extra action,
latency, and model work. Otherwise the mechanism would win merely because the
baseline was forbidden to acquire missing information safely.

The review therefore closes the representation choice but leaves four items
for a prospective charter: the exact public recalibration semantics, the
interaction horizon after a request, the natural-cost score, and enough fresh
replication to support its verdict thresholds.

## What would be learned—and what would not

If a correct governed fact improves fresh outcomes over cold and raw branches,
survives the ablation test, avoids non-transfer, responds to counterevidence,
and remains favorable after cost, the bounded claim would concern governed
acquisition of situated calibration knowledge by the practitioner.

It would not establish transferable craft, model learning, a universal
formation lifecycle, or superiority over retrieval in other practices.

The mechanism loses or changes interpretation if raw episodic derivation
matches it after cost, if the candidate or governor receives the hidden answer,
if the applicator contains a realized calibration, if governance never changes
exposure, if negative transfer or stale use crosses the frozen boundary, or if
the ablation changes anything beyond the fact-to-applicator edge.

## Current boundary

The next work is a fresh prospective validation charter that freezes the public
recalibration semantics, interaction horizon, cases, scorers, repetitions, and
budget. That charter must receive a cold leakage and causal review before it
can license implementation or contact. This document does not license a model
call, a new model download, or another representation repair.
