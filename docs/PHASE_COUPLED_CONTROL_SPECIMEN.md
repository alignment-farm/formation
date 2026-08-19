# Phase-coupled control deterministic specimen

Status: **complete; 19 focused tests and two independent implementation reviews
return `SPECIMEN_CONFORMS`; no exploratory charter or model contact licensed**.

## What was built

The specimen implements the smallest machine needed to test the reviewed
phase-coupled domain before any participant-model request exists.

- `micro_environment/phase_coupled_control.py` owns only hidden profile physics,
  public state, factual consequences, and exact action refusals.
- `micro_environment/phase_coupled_specimen.py` owns deterministic opaque
  identifiers, canonical occurrence bytes, the common offer envelope, uniform
  permitted-action lists, and the generic action-object boundary.
- `phase_coupled_specimen_oracle.py` owns harness-only warrant classifications.
  Neither environment module imports it.
- `tests/test_phase_coupled_control.py` supplies the independent executable
  witnesses.

This split is load-bearing. The environment can apply an action under its
private profile, but it cannot see a candidate, governor, branch, expected
answer, scorer label, or model request.

## What the specimen establishes

The tests exhaust both hidden profiles and both starting phases. Where target
direction matters, they also exhaust increase and decrease targets.

1. One public foreground admits either hidden profile.
2. Every permitted two-control acquisition pair distinguishes those profiles.
3. The occurrence contains factual movement and phase consequences but no slot
   or profile answer.
4. Fresh-device controls reject copied acquisition tokens on both one-action
   and commitment paths.
5. Every distance-two no-feedback case has exactly one successful ordered pair;
   repeated controls remain valid and fail.
6. `hold` is the unique warranted action at an already-current state.
7. On an unobserved family, even a lucky toward-target control remains an
   `unwarranted_guess`; this classification exists only in the external oracle.
8. One canonical occurrence representation, common envelope, generic action
   schema, and uniform permitted lists serve every later branch shape.
9. The environment imports only `dataclasses` and exposes no harness or runtime
   authority.

These are deterministic contract results. They are not evidence that a model
can infer the profile, author a useful interpretation, use it later, or develop.

## Independent implementation review

The first code audit used exact model identifiers `composer-2.5` and
`cursor-grok-4.6-high-fast`. Composer returned `SPECIMEN_CONFORMS`; Grok returned
`REVISE_SPECIMEN`. The stricter verdict was accepted. It exposed missing direct
pair-gate refusals, incomplete quantifier coverage, a weak occurrence witness,
and scorer policy placed inside the environment package.

After those repairs, Composer again returned `SPECIMEN_CONFORMS`; Grok requested
two further test-only repairs: bind the opening occurrence state and actions to
their supplied inputs, and test overlong commitments at both gates. The final
identical snapshot received `SPECIMEN_CONFORMS` from both models.

Both final reviewers received this exact question through Cursor `agent` in
read-only `ask` mode:

> Work read-only and do not edit files. Review the current
> tests/test_phase_coupled_control.py together with
> micro_environment/phase_coupled_control.py,
> micro_environment/phase_coupled_specimen.py,
> phase_coupled_specimen_oracle.py, and executable obligations 1-9 in
> docs/PHASE_COUPLED_CONTROL_PROPOSAL.md. This is the final narrow confirmation
> after test-only repairs: the occurrence test now asserts the opening before
> dict equals the supplied state and both action fields equal the committed
> tokens; the environment commitment gate is tested against one and three
> actions, a list, hold, and a foreign token; the generic action-object gate is
> tested against one and three commitment actions and hold. The focused 19
> tests and full 331-test discovery suite pass. Decide whether any blocking
> implementation or witness defect remains that could hide failure of the nine
> obligations or smuggle scorer/runtime/harness authority into the environment.
> This can close only the deterministic specimen, not license a charter or
> model contact. Return exactly SPECIMEN_CONFORMS or REVISE_SPECIMEN, explain
> any blocking issue with precise references, and end with a final line exactly
> TERMINAL_VERDICT: &lt;verdict&gt;.

Terminal results:

- `composer-2.5`: `SPECIMEN_CONFORMS`
- `cursor-grok-4.6-high-fast`: `SPECIMEN_CONFORMS`

## Verification

```text
python3 -m unittest tests.test_phase_coupled_control
Ran 19 tests ... OK

python3 -m unittest discover -s tests
Ran 331 tests ... OK
```

## Next boundary

The specimen closes the pre-contact computation. The next permitted work is to
decide whether its results justify a separate, strict-budget exploratory
charter. That charter must freeze the participant model, minimal interface,
case schedule, branch parity, stopping rules, receipts, and weak interpretation
language before any request is sent. Specimen conformance does not decide those
questions and does not itself license contact.
