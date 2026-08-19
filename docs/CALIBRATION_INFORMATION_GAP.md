# Calibration information-gap problem

Status: **pre-protocol problem specification; deterministic information-gap
specimen implemented; no model contact or Formation verdict licensed**.

## Main point

The next experiment needs a fact that later foreground state does not reveal.
It also needs later actions that cannot be solved by repeating the acquisition
action.

Use a family of opaque two-control devices. Within one controller family, the
first listed control always moves position in one direction and the second
listed control moves it in the other direction. Which slot increases position
is hidden until an external consequence reveals it. New devices in the same
family have new control names but preserve the slot rule. Other controller
families are calibrated independently.

This creates a small, inspectable question:

> Can one consequence support later use of a hidden calibration on new devices
> in the same family, including the opposite movement, while staying silent for
> another family and when the current state already satisfies the task?

This is a problem definition, not a validation charter. It fixes the causal
pressure and a pure transition specimen. It does not freeze a model, prompt,
case set, branch schedule, scorer, budget, or verdict.

## Why this specimen

The completed revision contact failed to create an information gap. Its field
names, action names, and current state exposed the useful rule on every later
request. A stronger model could therefore solve the no-offer condition without
experience.

Three replacements were considered:

- An arbitrary hidden label-to-action table creates a memory test but little
  state-dependent work.
- A hidden formatting convention mostly tests whether a later prompt repeats a
  string rule.
- A stochastic reward rule makes one consequence too ambiguous to justify a
  narrow interpretation.

Ordered control calibration is smaller and cleaner. Two opposite physical
worlds can present identical foreground bytes while requiring different
controls. One observed movement distinguishes those worlds. Later devices can
change every action token while preserving the learned slot relation.

Ordinary raw persistence remains a serious comparator and is allowed to win.
The specimen does not presume that an authored or governed interpretation is
better.

## Public rule and hidden fact

The following rule may be shared with every practitioner branch:

> Each controller family keeps one calibration across its devices. One ordered
> control slot increases position and the other decreases it. Device-specific
> control names may change. Different controller families are independently
> calibrated. If the current position already equals the target, hold. If the
> required family's calibration is not established by experience, request
> calibration rather than guess.

This rule states how evidence may generalize. It does not reveal the hidden
fact for any family:

```text
first_increases | second_increases
```

The environment owns that fact. It is chosen before contact and never appears
in ordinary later foreground. The harness may retain it for setup and scoring,
but it may not author a candidate, retrieval key, scope, or action from it.

## Public state and actions

A public situation contains exactly:

```text
controller_family
device_id
position
target
first_control
second_control
```

`first_control` and `second_control` are distinct opaque strings local to that
device. They must not equal the two public meta-actions:

```text
request_calibration
hold
```

The permitted action is one of the current device's two control strings or one
of those meta-actions. Hidden calibration, expected action, branch assignment,
case-family label, and score are absent from public state.

## Deterministic transition

For a control action, the environment finds its ordered slot and applies the
family calibration:

- the increasing slot adds one to position;
- the decreasing slot subtracts one; and
- the factual observation says whether the resulting position reached the
  target.

`request_calibration` leaves position unchanged and returns the environment's
exact increasing slot as an external observation. `hold` leaves position
unchanged and reports whether the position was already at the target.

The pure implementation in
[`micro_environment/calibration_gap.py`](../micro_environment/calibration_gap.py)
owns only this computation. It has no practitioner memory, runtime,
interpreter, governor, retriever, branch, scorer, or model call.

## Executable identifying contrasts

The deterministic tests establish five facts about the problem, not about a
model:

1. **Foreground underdetermination.** Identical public state and action yield
   opposite movement under the two possible calibrations. Current foreground
   alone cannot identify the right control.
2. **Acquisition sufficiency.** Executing either control reveals its slot's
   direction through before and after position. A calibration request reveals
   the increasing slot directly. Any one of these consequences identifies the
   two-slot mapping.
3. **Structural reuse.** A new device in the same family may use completely new
   control strings while preserving the ordered-slot calibration.
4. **Action-copy failure.** The acquisition control string is not a permitted
   action on the new device. Later targets above and below the current position
   require different new action strings.
5. **Non-transfer underdetermination.** After one family's calibration is
   known, two worlds can remain identical in all observations about that family
   while assigning opposite calibrations to another family. Applying the first
   family's mapping to the second is not warranted.

An already-satisfied state adds a sixth practical pressure: `hold` is correct
without using any calibration. A retained interpretation that prompts a
control or another calibration request there is unnecessarily active.

## Acquisition and later problem shape

A future contact should begin with one shared acquisition encounter on one
device. The actor may choose either current control or request calibration.
The exact external result must make the calibration identifiable without the
harness explaining it. If the actor holds off target or produces no observable
action, that behavior is retained; exploration may stop or continue only under
its own frozen rule.

Later, fresh device tokens should cover at least these relations:

- same family, movement in the acquisition direction;
- same family, movement in the opposite direction;
- another family whose calibration has not been observed;
- an already-satisfied state; and
- a lexical decoy that looks more like the acquisition device but belongs to
  the other family.

Those are relation requirements, not frozen cases. Exact names, values, order,
repetitions, and assignments remain unselected. Prospective validation cases
must be fresh after any exploratory contact.

## Comparison discipline

Every future branch must receive the same public rule, action interface, and
later foreground bytes. Branch-local material may differ only through its
declared handling of the shared acquisition experience.

The natural comparisons remain:

- no experience-derived persistence;
- the exact raw occurrence;
- the cold model's exact post-consequence interpretation;
- a governed candidate derived by the runtime from that interpretation and
  runtime-visible evidence; and
- a declared ablation of a named governed causal edge.

Raw persistence may use the public controller family only through a retrieval
policy frozen before contact. It may not receive a hidden transfer label. A
governor may check a candidate against the observed transition and its claimed
public scope, but it may not read held-out cases or the environment's hidden
assignment directly.

Raw occurrence text and interpreted content are not semantically
information-matched; they are different mechanisms. Their natural token and
latency costs must be reported rather than padded away. A secondary
presentation control may use the same message role, delimiter, and formatting
surface for every branch-local offer. Equal length can diagnose gross prompt
salience but cannot make different meanings causally equivalent.

## Static instruction boundary

The strong static-practice instruction is the shared public rule above. It can
teach the cold model how calibration evidence should be used, but it cannot
contain the actual post-assignment calibration without ceasing to be a
pre-contact static baseline.

A human- or harness-authored message that states the hidden increasing slot is
an oracle-informed diagnostic ceiling. It may be useful to show that the actor
can use the fact, but it is not the ordinary static-instruction comparator and
cannot be credited as formation.

This distinction prevents a hidden randomized fact from being smuggled into a
supposedly static baseline while preserving a strong shared instruction about
the practice.

## Design attacks and losing observations

This problem loses or changes interpretation if any of the following occurs:

- public names, ordering, examples, or target construction correlate with the
  hidden calibration;
- later action strings recur from acquisition, restoring answer copying;
- the runtime receives a hidden relation label or the harness chooses a
  retrieval result from prospective case metadata;
- one observed consequence does not identify the calibration actually claimed
  by the candidate;
- the candidate's family scope is supplied or repaired by the harness;
- a different-family direct control is rewarded merely because a blind guess
  happened to move in the useful direction;
- presentation changes are described as formation evidence;
- the no-persistence model reliably reconstructs the hidden calibration from
  later foreground alone; or
- raw persistence matches or beats the governed mechanism after costs. In that
  last case the simpler system wins; the problem itself remains valid.

The safety treatment for an unobserved family still needs a concrete external
rule before contact. A future charter must decide whether direct control is
environment-refused, externally scored as unwarranted, or allowed as a costly
trajectory gamble. That choice changes the scientific question and is not made
here.

## Current exit and next boundary

The implemented specimen establishes that the proposed environment can contain
an experience-dependent fact, can transfer it across changed action tokens,
and can withhold justification for another family. It does not show that a
model can interpret or use the fact.

The next executable boundary is a bounded **mechanism-discovery contact
charter**, not a validation protocol. Before any model call, that charter must
freeze the operational model and coldness receipt, acquisition mode, candidate
authorship surface, treatment of unobserved-family actions, later relation
families, presentation controls, budget, and exploratory claim boundary.
