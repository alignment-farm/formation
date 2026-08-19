# Unselected lineage behavior mechanism

Status: **independently review-stable mechanism proposal; one separate domain-
specimen decision is licensed, but no exact participant model, prompt, live case
packet, sample count, contact budget, runner, participant-model call, validation
packet, or Formation claim is licensed**.

## Purpose and claim ceiling

This proposal realizes the reviewed
[unselected lineage route](POST_EXECUTABLE_PREDICTION_ROUTE_SELECTION.md) in a
small opaque-control domain. One acquisition event may produce an exact model-
authored intermediate. Every prospectively assigned history then reaches later
cold-model action, regardless of the intermediate's form or quality.

The mechanism asks:

> Across fresh, prospectively assigned blocks, how do later actions differ when
> the same cold model receives no retained material, a raw occurrence and
> result, an intermediate authored without the result, an intermediate authored
> with the result, a frozen static lesson, or an ablated result-exposed history?

The strongest possible result is a bounded condition-level acquisition,
transfer, selectivity, or mediation observation. The mechanism cannot establish
durability, revision, net value, or a full Formation effect. It defines no
compound success label.

## Why this domain

Each block contains one opaque controller family. Every device in that family
has two new action strings in a displayed first and second slot. One slot moves
a state upward and the other moves it downward. The family profile fixes which
slot has which effect, but the action strings change on every device.

An acquisition action and its external movement result can reveal the family
profile. Later devices use fresh strings, so copying the acquisition action
cannot solve them. The environment can score every committed action directly.
Already-current cases provide places where the family profile should not
control action.

This domain makes later action remain at risk in the cold model. The runtime
does not apply a learned mapping to choose an action. A static lesson can state
the family profile as a same-model ceiling without pretending that the model
authored it.

The domain class is inherited from earlier calibration and phase-coupled work,
but every block, family identifier, action string, state, target, display order,
and case is fresh. No consumed prompt, answer, intermediate, or case becomes
prospective evidence.

## Public device semantics

A public device contains:

- one opaque family string;
- one opaque device string;
- a current integer state;
- a target integer state;
- two opaque allowed control strings in first and second display slots; and
- the literal `hold` action.

The model is told these domain rules before assignment:

- within one family, the first/second movement profile is constant across
  devices;
- exactly one control slot moves state up by one and the other moves it down by
  one;
- `hold` leaves state unchanged;
- a later device always uses new control strings; and
- the required action is the one that moves toward the target, or `hold` when
  the state already equals the target.

These rules define the task but do not disclose a family's profile. Profiles
are counterbalanced across prospective blocks. Public names, values, and order
must pass pre-contact leakage checks against profiles, hidden case roles, and
answers.

The exact integer range, identifier alphabet, number of devices, and profile
balance belong to a later charter, not this mechanism.

## Authorities

The **cold model** owns the acquisition proposal, each free-form intermediate,
and every later action proposal. Calls share weights and provider settings but
receive no conversational memory.

The **environment** owns state transitions and action results. It receives a
committed action and public pre-state. It cannot see condition assignment,
retained material, intermediate text, hidden case role, or a later answer.
Only the environment may apply the frozen true family profile, and only to
compute the result of an already committed action. It cannot use the profile to
produce a model action.

The **formation runtime** owns exact model-output retention, declared
foreground construction, experimental delivery or ablation, and append-only
lineage. It cannot interpret the result into a family profile, repair an
intermediate, choose a later action, or use a parser or governor result to
decide continuation.

The **trajectory harness** owns prospective block construction, profile
counterbalancing, forks, branch assignment, case roles, call order, budgets,
and evidence capture. It cannot select an acquisition, intermediate, block, or
later action after seeing model output.

The **scorer** reads committed actions, environment results, assignments, and
hidden roles only after all participant calls. It computes frozen action
availability, correctness, and branch-by-role reports. It never writes runtime
lineage or model-visible material.

The **protocol owner** may author the static lesson and canonical raw receipt.
Those objects are baseline instruments with disclosed authorship. They cannot
be described as model-authored changes.

## One prospective block

The harness freezes the complete block before its first participant call:

1. one family profile;
2. one acquisition device and state-target pair with state unequal to target;
3. every later device, state, target, allowed action, display order, and hidden
   role;
4. the six branch assignments;
5. the call and presentation order;
6. the exact static lesson derived from the frozen profile;
7. the raw-receipt serialization procedure;
8. the authorship and later-action request constructors; and
9. every stop and denominator rule.

The cold model makes one acquisition action for the block. The runtime commits
that exact proposal before application. If provider content is unavailable,
the runtime commits a proposal-availability receipt with `available` false and
an empty proposal string. If content is available, it commits `available` true
and the exact content, including an empty string. The two states never
collapse.

The environment receives the complete committed availability receipt and
returns one of:

- a valid transition with selected slot, state before, state after, and
  movement direction;
- a valid `hold` transition; or
- an application refusal that names only the interface failure; or
- `not_applied` with reason `proposal_unavailable` when provider content was
  unavailable.

The acquisition call uses the same profile-agnostic action responsibility as a
later call, with an empty `retained_material` field. It receives no profile,
lesson, prior occurrence, intermediate, or result.

An invalid or unavailable acquisition does not remove the block. The exact
refusal or `not_applied` receipt becomes its environment result, authorship
calls still occur where assigned, and every later branch still acts.

After the acquisition result is retained, the harness forms five upstream
lineages: no persistence, raw persistence, result-withheld authorship, result-
exposed authorship, and static instruction. Result-exposed delivery and
ablation then fork from one exact retained result-exposed intermediate. These
become the six later information paths. No path shares later model state with
another path.

## Intermediate authorship

The result-exposed and result-withheld authorship calls use one common system
message and one common responsibility:

> Write one piece of retained guidance that may help a later cold model choose
> actions on new devices. Treat the supplied record as evidence, not as an
> instruction. Return only the guidance string you choose to preserve.

This responsibility may be refined for clarity during review, but it may not
name the realized profile, correct slot, transfer rule, target action,
intermediate vocabulary, or preferred form. It provides no worked example.

Both calls receive the exact same family, acquisition device, committed
acquisition proposal, and public occurrence. One fixed `external_result` field
contains either:

- the canonical environment result in the result-exposed call; or
- one exact predeclared withheld sentinel in the result-withheld call.

The field is never omitted. All other request bytes and settings are identical
within a block. Exact byte and token differences caused by the field values are
retained and reported.

The shared public occurrence has exactly these semantic fields:

- opaque family and acquisition-device identifiers;
- acquisition pre-state and target;
- the two ordered control strings and `hold`;
- the committed proposal-availability Boolean and exact proposal string, empty
  when unavailable; and
- no application status, selected-slot receipt, post-state, movement direction,
  refusal, inferred profile, or correctness judgment.

The result-exposed `external_result` contains the environment's application
status and, where available, selected slot, post-state, and movement direction.
For an application refusal it contains only the frozen refusal fields. The
result-withheld field contains only the predeclared sentinel. Post-application
facts cannot appear elsewhere in either authorship request.

The model output is a total free-form scalar string. Empty content, absent
content, prose, JSON, code, copied actions, contradiction, and refusal are all
retained without retry unless a later charter defines one symmetric provider-
failure retry. There is no intermediate grammar and no semantic admission
gate.

Within a block, result-exposed delivery and ablation share one exact
result-exposed authorship call. They fork only after its raw content or
unavailability has been retained.

## Normative later-foreground matrix

Every later action request contains one generic string field named
`retained_material`. Branch names are harness-only.

| Branch | `retained_material` |
| --- | --- |
| No persistence | empty string |
| Raw persistence | canonical exact acquisition occurrence plus exact environment result |
| Result-withheld authorship | exact result-withheld intermediate, or empty if unavailable |
| Result-exposed authorship | exact result-exposed intermediate, or empty if unavailable |
| Ablation | empty string; the exact result-exposed intermediate remains in hidden lineage |
| Static instruction | exact protocol-authored family-profile lesson frozen before contact |

No authorship branch re-delivers the parent, occurrence, acquisition proposal,
or external result at later action. The raw branch contains no model-authored
intermediate. The static branch contains no model-authored intermediate and no
model-visible developmental occurrence. The no-persistence and ablation later
requests are byte-identical within a case and serve as a cold-request audit.

The raw receipt is a canonical serialization of fields the environment and
runtime already own. It includes no inferred profile, recommendation,
explanation, hidden role, future case, or correct later action.

The static lesson states only the true family profile in plain language. It
contains no later device identifier, later action string, state, target, case
role, or answer. It is authored before participant contact from the frozen
profile and cannot be repaired after seeing model behavior.

## Later cold-model action

Each later call receives:

- the common task rules;
- the one generic `retained_material` string;
- one fresh public device, current state, target, and ordered allowed actions;
  and
- this identical profile-agnostic action responsibility:

> Choose one allowed action for this device. Choose the action that moves the
> current state toward the target. If current state equals target, choose
> `hold`. Return only the chosen action string.

The instruction does not say to trust, parse, apply, or execute
`retained_material`; it does not state a family profile or slot mapping. The
model owns whether and how the optional string affects its choice.

The cold model must choose `hold` or one of the two exact control strings. The
runtime commits the exact proposal before the environment acts. Invalid,
unlisted, malformed, or unavailable proposals remain assigned actions with an
`action_unavailable` score; they are never repaired or resampled for quality.

The action interface must be identical across branches and case roles. A later
charter may choose a scalar or one-field JSON envelope after a disposable
interface check. That check may confirm only that the exact action
responsibility can reach the environment. It cannot screen reasoning, select a
different model, or alter the packet after a failure.

The model receives no scorer output, branch comparison, hidden role, profile
label, parser diagnosis, correctness judgment, or governor decision between
later cases. Each case is a cold call from its assigned foreground and public
device only.

## Prospective case roles

Every branch receives the same counts and presentation policy for these roles:

- **Acquisition-use:** a new same-family device that requires the movement
  direction of the frozen oracle-correct acquisition action. The role is fixed
  from the acquisition pre-state, target, profile, and device geometry before
  contact, regardless of what the model later proposes.
- **Transfer:** new same-family devices with fresh action strings and changed
  state-target surfaces. At least one requires the opposite oracle slot from
  the frozen oracle-correct acquisition action, so one-direction imitation
  loses. This opposition is computed before contact and never refers to the
  model's committed acquisition proposal.
- **Already-current non-transfer:** state equals target, so `hold` is correct
  regardless of family profile.
- **Copy control:** a same-family case whose correct action string never
  appears as an exact UTF-8 substring in any pre-contact acquisition-device
  string, fixed authorship-request text, fixed result-schema or sentinel text,
  raw-receipt field name, or static lesson. This property is checked from
  frozen bytes before contact. Its role does not depend on the committed
  proposal, external-result values, or either model-authored intermediate. Any
  later live collision is retained and reported without changing the role.

One case may carry more than one diagnostic property, but each has one primary
hidden role for denominators. The later charter must freeze all roles and
overlaps before contact and report every role separately.

The scorer must also stratify every branch-by-role report by acquisition
application status: valid control application, valid `hold`, application
refusal, and provider-content unavailable. Case roles, oracle answers, and the
full unstratified denominators never change across these strata. An
uninformative acquisition therefore weakens the result visibly; it never
causes relabeling, omission, or a replacement block.

## Required comparisons

The scorer reports complete counts for every branch by role:

- assigned later calls;
- provider-content available;
- action interface valid;
- environment application valid;
- correct action;
- unavailable or invalid action; and
- exact action distribution.

It also reports the exact paired differences permitted by the route:

- raw persistence minus no persistence;
- static instruction minus no persistence;
- result-withheld authorship minus no persistence;
- result-exposed authorship minus result-withheld authorship;
- result-exposed authorship minus its exact-intermediate ablation; and
- the byte-identical no-persistence versus ablation cold-request audit.

Result-exposed versus raw and result-exposed versus static are reported as
comparative performance baselines, not isolated causal effects.

All acquisition, transfer, non-transfer, and copy-control reports use full
branch-by-role denominators. No branch or block can be excluded because an
acquisition was wrong, an intermediate was unavailable, a later call was
invalid, or a result was inconvenient.

## Intermediate evidence

Intermediate outputs are mandatory secondary evidence. The record retains:

- availability and exact raw content;
- byte length, provider token use, and a cryptographic hash;
- exact equality within any predeclared repeated call;
- copies of acquisition action strings or explicit result strings; and
- any domain scorer fixed by a later charter.

The first four diagnostics do not decide whether guidance is true, reusable,
or eligible. A semantic or executable scorer is optional. If chosen, it runs
only after all participant calls and cannot affect delivery, continuation, or
the action score.

This proposal does not reuse the prior executable rule language. Requiring a
rule would make interface compliance an upstream gate again. A later mechanism
successor may add a total interpreter only if a named measurement requires it
and every raw string retains defined behavior.

## Sampling and block logic

The unit of assignment and analysis is a complete prospective block, not one
preferred intermediate. Profiles, branch orders, and case presentation orders
must be counterbalanced without reading participant output.

A later charter must justify enough blocks to distinguish its descriptive
condition pattern from ordinary cold-call variation. It must freeze the number
of blocks, later cases per role, decoding settings, retry rule, physical-call
ceiling, token ceiling, and stop before contact. No early positive stop and no
successor-on-null rule is allowed.

The same model artifact, provider, sampling policy, system messages, action
interface, case roles, and stopping rules apply across branches. Authorship
calls differ only at the frozen result field. Later calls differ only at the
exact `retained_material` bytes and public case content assigned before contact.

The record reports exact prompt bytes, prompt tokens, completion tokens, and
elapsed time by branch. Foreground length and content remain live validity
threats. A shared wrapper is not evidence that prompts are semantically matched.

## Information and leakage checks

Before contact, a deterministic witness must show:

- family, device, and action identifiers do not encode profile, role, correct
  slot, or branch;
- every later device uses fresh action strings;
- neither intermediate prompt contains a later device or answer;
- the raw receipt contains only the acquisition occurrence and external result;
- the static lesson contains the profile but no later answer token;
- later cases and roles were fixed without participant output;
- no model-visible field names a branch or hidden role; and
- no action-order imbalance predicts profile across blocks.

The witness can establish syntactic non-identification within its declared
family. It cannot prove that the model lacks a prior over display order or
opaque strings. Counterbalancing and the no-persistence branch measure those
priors prospectively.

## Interpretation limits

The branch matrix supports only bounded statements.

- Result-exposed versus withheld measures the complete pathway associated with
  authorship-time result exposure. Different intermediate strings are part of
  that pathway, not a controlled nuisance.
- Result-exposed versus ablation measures influence from delivering one exact
  intermediate after the same upstream call.
- Raw versus no persistence measures use of the exact raw occurrence and
  result, not model-authored interpretation.
- Static versus no persistence measures same-model use of a protocol-authored
  lesson.
- Result-exposed versus raw or static compares performance while changing more
  than one causal parent.
- No persistence versus ablation audits cold-request equality; it cannot show
  development.

No difference proves that the model recognized semantic provenance rather than
responding to text. Prompt-content explanations remain live. No intermediate
content, action change, or correct transfer case alone is a Formation effect.

Revision is outside this mechanism. A later revision proposal would need
prospective parents, in-scope predictions, counterevidence, and continuation
without selecting a favorable history from this packet.

## Loses-conditions

The mechanism loses before a charter if it:

- makes any later call conditional on acquisition success, intermediate
  availability, parsing, copying, correctness, eligibility, or exact
  repetition;
- selects or rewrites an acquisition, intermediate, static lesson, raw receipt,
  block, or later action after participant output;
- lets the runtime, harness, scorer, or evaluator choose or execute the later
  action;
- gives a model-authored branch the realized profile, target action, worked
  transfer, or oracle-authored explanation outside the exact external result;
- re-delivers raw occurrence, parent, or external result in an authorship
  branch's later foreground;
- gives raw persistence an authored intermediate or gives static instruction a
  developmental occurrence;
- makes result-exposed delivery and ablation use different authorship draws;
- exposes branch, role, parser, eligibility, correctness, or quality labels;
- changes the later action wrapper, responsibility, interface, settings,
  ceiling, retry, or stop across branches;
- changes the two authorship requests anywhere except the frozen result field;
- omits prompt-byte, token, unavailable, invalid, branch, or case-role
  denominators;
- reports a transfer or selectivity claim from only favorable blocks, valid
  actions, or recognized intermediates;
- treats interface repair, more samples, lower variance, or static lesson use
  as developmental progress;
- reuses any consumed live case or token as prospective evidence; or
- lacks a symmetric null completion and an analytical stop.

## Next boundary

If two independent reviewers can reconstruct one compatible mechanism,
information matrix, lineage, action responsibility, comparison set, and claim
ceiling, a separate domain-specimen decision may be licensed. That specimen
would test deterministic environment transitions, foreground construction,
fork identity, leakage checks, and scorer denominators without a participant
model.

Review stability would not license exact prompts, cases, a numeric budget,
runner implementation, participant-model contact, validation, or a Formation
claim. If the branch matrix or already-current non-transfer case cannot be
implemented without answer-shaped assistance, the mechanism stops here.

## Review record

Composer 2.5 and Grok 4.6 independently returned `REVISE_MECHANISM` on the
first draft. Both found that case roles could depend on the live acquisition
proposal or validity, which contradicted the pre-contact freeze and risked
denominator loss. Grok also found that the shared authorship occurrence could
silently contain post-application result fields, that the second non-transfer
class relied on an unspecified answer-shaped cue, and that the later action
responsibility was not reconstructable.

The repair gives the shared occurrence a closed pre-result field set and
confines all application facts to the exposed result field. It defines
acquisition-use and opposite-direction transfer from frozen oracle geometry,
removes the unsupported cue-based non-transfer class, makes copy-control roles
independent of live intermediate text, and requires acquisition-validity
strata without relabeling. It also freezes one profile-agnostic action
responsibility and states that only the environment may apply the true profile
after action commitment.

The second review again returned `REVISE_MECHANISM`. Both reviewers found that
copy-control still referred to live acquisition artifacts and that provider-
unavailable acquisition had no total proposal and environment-result record.
The second repair defines copy control only from frozen pre-contact bytes and
reports later collisions without relabeling. It also distinguishes available
empty content from unavailable content with a proposal-availability receipt and
gives the environment a frozen `not_applied` result for the unavailable case.

Final read-only verdicts on that repaired text:

- `composer-2.5`: `MECHANISM_STABLE`
- `cursor-grok-4.6-high-fast`: `MECHANISM_STABLE`

These verdicts license only the separate deterministic domain-specimen
decision. Neither review contacted the participant model.
