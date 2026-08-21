# Documentation

This directory explains what Formation is trying to build, what each
experiment was designed to test, and how the work is governed. Start with the root
[README](../README.md) for the short project story. Do not start by opening a
random specification: many are exact audit records from closed experiments.

## Where current status lives

The root [README](../README.md#present-state) is the only current-state
narrative. It states the latest result, its limits, and the active empirical
question.

This directory preserves concepts, plans, specifications, and research history.
Those files may describe what was “next” at the time an experiment closed. That
language is historical and does not override the root README.

## Choose a reading path

- To understand the project, read the root [README](../README.md), then the
  [concept](CONCEPT.md).
- To see the current result and the evidence that owns it, follow the link from
  the root [current state](../README.md#present-state).
- To continue the work, read the root [current state](../README.md#present-state),
  then use the [plan](PLAN.md) for milestone rules and stopping conditions.
- To understand how the project reached this point, read the
  [research history](RESEARCH_HISTORY.md).
- To audit an experiment, read its evidence account first, then its frozen
  specification. The specification preserves exact prompts, comparisons, and
  limits; it is not the teaching version.

## What the files are for

| Kind of file | What it answers | Read it when |
| --- | --- | --- |
| Root README | What is the project doing now? | You need the broad story. |
| Concept | What would count as development? | You need the research thesis. |
| Plan | What milestone rules and stopping conditions govern the work? | You are continuing the work. |
| Evidence account | What actually happened in one experiment? | You want a result. |
| Experiment specification | What exact comparison was frozen before contact? | You are auditing the result. |
| Research history | Why did the project change direction? | You need the sequence of lessons. |
| Authority and record contracts | Who may supply information, and what must be retained? | You are changing the apparatus. |

Specifications own exact mechanism contracts. Evidence and scorers own
experimental verdicts. The plan states intended work. Research history explains
the sequence but cannot turn an observation into a finding.

## Recent experiments in plain language

| Question | Result | Best first read |
| --- | --- | --- |
| Does the same request always produce the same action? | No. One important request produced both actions across repeats. | [Repeatability evidence](../evidence/same-request-variation-20260819T231848Z/README.md) |
| Does carrying forward raw experience or a model-written lesson change later action? | Not in the first repeated comparison. | [Distributional evidence](../evidence/distributional-developmental-20260819T233903Z/README.md) |
| Can the model write a useful control rule after seeing a consequence? | Yes in narrow cases, but a supplied answer-like lesson worked just as well. | [Candidate validation evidence](../evidence/canonical-mapping-candidate-validation-20260820T000646Z/README.md) |
| Does that rule leave unrelated behavior alone? | No. It often reversed correct actions in the opposite direction. | [Non-transfer evidence](../evidence/candidate-nontransfer-sweep-20260820T001430Z/README.md) |
| Can a family check block that harm? | Yes, but the underlying rule still failed to guide some matching cases. | [Scope-gate evidence](../evidence/canonical-mapping-scope-gate-validation-20260820T001909Z/README.md) |
| Does changing the form of the model-written lesson solve the problem? | No. Writing the lesson correctly and using it later failed independently. | [Representation evidence](../evidence/representation-class-exploration-20260820T010342Z/README.md) |
| Can later calls use a correct lesson across fresh devices? | Yes for a sentence and effect table; no for the tested policy. Both usable forms still need the family gate. | [Consumption evidence](../evidence/representation-consumption-calibration-20260820T112303Z/README.md) |
| Can a staged model-written table change later action? | Strongly, but two strict validations each missed a subgroup floor by one action. | [Balanced validation](../evidence/balanced-relation-staged-validation-20260820T122857Z/README.md) |
| Is a sentence or table the better staged form? | Both made all matching actions. The formal table preference came from a flawed gate-benefit rule. | [Paired representation evidence](../evidence/staged-representation-consumption-20260820T124630Z/README.md) |
| Does the staged chain survive a larger frozen comparison? | Yes. It made 48/48 matching actions, preserved unrelated action, and passed the bounded validation. | [Aggregate validation](../evidence/staged-chain-aggregate-validation-20260820T130635Z/README.md) |
| Can counterevidence revise a previously useful table? | Yes in the bounded validation. Revised tables made 48/48 post-change actions. | [Revision validation](../evidence/staged-table-revision-validation-20260820T134318Z/README.md) |
| Can two earned tables coexist and be selected jointly? | They coexist behind an external gate, but tested joint containers were unreliable. | [Container diagnostic](../evidence/accumulated-table-container-20260820T142422Z/README.md) |
| Can a restricted second model encode and classify experience without seeing the action task? | Yes in the bounded validation. Its full pipeline made 48/48 matching actions and preserved unrelated action. | [Learned-instrument validation](../evidence/learned-clerical-instrument-validation-20260820T171748Z/README.md) |
| Can that instrument revise an active record after counterevidence? | It produced a revision candidate at 24/24 matching actions, but the clerk also invented records when the needed measurement was hidden. | [Learned revision evidence](../evidence/learned-clerical-revision-20260820T174848Z/README.md) |
| Can the runtime admit only source-supported clerk revisions? | A broad learned verifier failed, but decomposed projection plus exact checks admitted all 24 supported retained records and quarantined all 24 unsupported ones. | [Composed admission evidence](../evidence/composed-clerical-record-admission-20260820T181541Z/README.md) |
| Does composed admission survive a fresh behavioral validation? | Every mechanism comparison passed, but one invalid raw-control cell triggered the frozen global engagement veto. | [Fresh composed validation](../evidence/composed-clerical-revision-validation-20260820T183033Z/README.md) |
| Does it survive when engagement is tied to the tested interfaces? | Admitted revisions made 45/48 matching actions, tied supplied revisions, lost their benefit under removal, and passed the corrected frozen validation. | [Engagement successor](../evidence/composed-clerical-revision-engagement-successor-20260820T185545Z/README.md) |
| Can one record reach version 3 without corrupting a coexisting version 2? | Every later mechanism comparison passed, but one source action lacked frozen attribution to version 2, so the verdict was null. | [Selective longer lineage](../evidence/selective-longer-lineage-revision-20260820T192314Z/README.md) |
| Can the two counterevidence policies be computed without answer leakage? | Both use only retained record, action, target, and consequence facts; observation-grounded admits 4/4 and action-attributed 3/4. | [Authority diagnostic](../evidence/counterevidence-authority-diagnostic-20260820T194134Z/README.md) |
| Can deliberate exploration warrant revision without causal blame of the old record? | Observation-grounded exploration made 48/48 matching actions; action-attributed quarantine and removal each retained only the 24 unchanged-scope actions. | [Observational comparison](../evidence/observational-counterevidence-comparison-20260820T195003Z/README.md) |
| Can accumulated counterevidence remain source-preserving and governable? | Four exact histories reach superseded, retained, pending-corroboration, and unresolved states without model calls. | [Accumulation specimen](../evidence/contested-counterevidence-accumulation-20260820T200609Z/README.md) |
| Can the learned clerk and governor carry those histories into later behavior? | Every clerical and governance step passed, but recovered delivery tied removal at 6/6, so the frozen verdict was null. | [Learned continuation](../evidence/learned-contested-counterevidence-continuation-20260820T214847Z/README.md) |
| Does recovered delivery matter when cold action cannot distinguish opposite worlds? | Recovered and supplied records made 48/48; byte-identical cold and removal requests made 24/48. | [Mirrored recovery](../evidence/mirrored-recovery-influence-successor-20260820T221149Z/README.md) |
| What does requiring two confirmations gain and cost? | It eliminated six wrong deliveries and six false replacements, but increased suspension from one step to eleven. | [Uncertain-consequence policy](../evidence/uncertain-consequence-policy-specimen-20260820T222304Z/README.md) |
| Can the first suspension world distinguish active policies? | No. Every task action was reversible and informative, so the policies were observationally equivalent. | [Suspension consequences](../evidence/suspension-consequence-specimen-20260820T222814Z/README.md) |
| Can a world make uninformed task action dangerous while preserving a diagnostic? | Yes. A wrong task action now fails, while a separate diagnostic reveals a signal. | [Asymmetric domain](../evidence/asymmetric-suspension-domain-20260820T223216Z/README.md) |
| Can old consequences give that diagnostic signal useful meaning later? | Learned and supplied records each made 24/24 tasks; removal and raw history made 12/24; reversed records failed all 24. | [Clerical contact](../evidence/asymmetric-probe-clerical-contact-20260820T224335Z/README.md) |
| Do those records cause the participant to seek information? | No. Cold and removal already probed every time, and the learned path guessed beyond its evidence. The verdict was harmful. | [Self-directed probe](../evidence/self-directed-probe-contact-20260820T225832Z/README.md) |
| Does an explicit no-match receipt prevent unsupported action? | The first comparison did not engage because its controls changed behavior under new wording. | [First receipt contact](../evidence/explicit-applicability-receipt-contact-20260820T231222Z/README.md) |
| Does the receipt work against exact harmful controls? | Yes. Silent absence guessed and failed three of six unfamiliar cases; an explicit empty receipt held all six. | [Matched receipt successor](../evidence/matched-applicability-receipt-successor-20260820T232130Z/README.md) |
| Can a deterministic world expose whether retained knowledge changes the value of a costly diagnostic? | Yes as an instrument. It publishes the signal alphabet and service-window cost before action while keeping the emitted signal and valid control hidden. No model was called. | [Knowledge-cost specimen](../evidence/knowledge-cost-interaction-specimen-20260821T112825Z/README.md) |
| Does record coverage change whether the participant pays for a diagnostic? | No. Any catalog caused all costly probes, including when it covered neither published signal. Removal also differed by alphabet. The verdict was harmful. | [Knowledge-cost exploration](../evidence/knowledge-cost-interaction-exploration-20260821T132804Z/README.md) |
| Does an explicit pre-action coverage receipt repair that failure? | No beside the full catalog. Catalog paths still probed every uncovered case; removal mostly displaced probes into direct guesses. The verdict was harmful. | [Coverage-receipt successor](../evidence/preaction-coverage-receipt-successor-20260821T144006Z/README.md) |
| Can an isolated `complete` or `none` status guide the first action? | No. Every complete branch guessed, every none branch mostly guessed, and the frozen decision closed the coverage-representation route. | [Compact status calibration](../evidence/compact-coverage-status-calibration-20260821T151604Z/README.md) |
| Can admitted records govern access to the costly diagnostic without harness action choice? | Yes as a deterministic runtime mechanism. Complete learned, supplied, and reversed coverage authorizes; removal and uncovered alphabets withhold without an environment action. | [Governed policy specimen](../evidence/governed-diagnostic-policy-specimen-20260821T153245Z/README.md) |

## Authority reference

| Question | Owner |
| --- | --- |
| What phenomenon is Formation trying to produce and distinguish? | [CONCEPT.md](CONCEPT.md) |
| What is the current result and active question? | Root [README](../README.md#present-state) |
| What milestone rules and stopping conditions govern the work? | [PLAN.md](PLAN.md) |
| How did closed routes expose the current problem? | [RESEARCH_HISTORY.md](RESEARCH_HISTORY.md) |
| Who may know, decide, and write what? | [AUTHORITY.md](AUTHORITY.md) |
| What must developmental lineage and trajectory evidence retain? | [RECORD.md](RECORD.md) |
| What separates exploration from claim-bearing validation? | [EVALUATION.md](EVALUATION.md) |
| What should the first general implementation contain and exclude? | [BUILD.md](BUILD.md) |
| How should public findings and explanations be written? | [STYLE_GUIDE.md](../STYLE_GUIDE.md) |
| What governs opening a costly diagnostic encounter? | [GOVERNED_DIAGNOSTIC_ENCOUNTER_POLICY.md](GOVERNED_DIAGNOSTIC_ENCOUNTER_POLICY.md) |

## Earlier developmental route

These documents remain authoritative for the earlier problems and contacts in
the retained chain:

| Question or contact | Document |
| --- | --- |
| First bounded developmental comparison | [EXPLORATORY_DEVELOPMENTAL_CONTACT.md](EXPLORATORY_DEVELOPMENTAL_CONTACT.md) |
| Experience-dependent calibration gap | [CALIBRATION_INFORMATION_GAP.md](CALIBRATION_INFORMATION_GAP.md) |
| Raw, authored, and governed calibration offers | [CALIBRATION_MECHANISM_DISCOVERY.md](CALIBRATION_MECHANISM_DISCOVERY.md) |
| Single larger-model operational successor | [MUSE_COUNTER_PRIOR_SUCCESSOR.md](MUSE_COUNTER_PRIOR_SUCCESSOR.md) |
| Explicit environment consequence fields | [EXPLICIT_CONSEQUENCE_REPRESENTATION.md](EXPLICIT_CONSEQUENCE_REPRESENTATION.md) |
| Final explicit-consequence contact | [EXPLICIT_CONSEQUENCE_CONTACT.md](EXPLICIT_CONSEQUENCE_CONTACT.md) |
| Separation of availability from attributable influence | [AVAILABILITY_TO_INFLUENCE.md](AVAILABILITY_TO_INFLUENCE.md) |
| Rejected generic-applicator mechanism | [CALIBRATION_APPLICATOR_MECHANISM.md](CALIBRATION_APPLICATOR_MECHANISM.md) |
| Rejected prospective validation packet | [CALIBRATION_APPLICATOR_VALIDATION.md](CALIBRATION_APPLICATOR_VALIDATION.md) |
| Review that closed the applicator route | [CALIBRATION_APPLICATOR_VALIDATION_REVIEW.md](CALIBRATION_APPLICATOR_VALIDATION_REVIEW.md) |
| Model-mediated procedural influence problem | [PROCEDURAL_INFLUENCE_PROBLEM.md](PROCEDURAL_INFLUENCE_PROBLEM.md) |
| Selection of the phase-coupled domain | [PROCEDURAL_DOMAIN_SELECTION.md](PROCEDURAL_DOMAIN_SELECTION.md) |
| Phase-coupled mechanism and its review | [PHASE_COUPLED_CONTROL_PROPOSAL.md](PHASE_COUPLED_CONTROL_PROPOSAL.md), [PHASE_COUPLED_CONTROL_REVIEW.md](PHASE_COUPLED_CONTROL_REVIEW.md) |
| Deterministic phase-coupled specimen | [PHASE_COUPLED_CONTROL_SPECIMEN.md](PHASE_COUPLED_CONTROL_SPECIMEN.md) |
| Completed phase-coupled contact | [PHASE_COUPLED_EXPLORATORY_CHARTER.md](PHASE_COUPLED_EXPLORATORY_CHARTER.md) |
| Experience-grounded authorship problem and route choice | [EXPERIENCE_GROUNDED_AUTHORSHIP.md](EXPERIENCE_GROUNDED_AUTHORSHIP.md), [AUTHORSHIP_MECHANISM_SELECTION.md](AUTHORSHIP_MECHANISM_SELECTION.md) |
| Occurrence-accounting mechanism and completed contact | [OCCURRENCE_ACCOUNTING_MECHANISM.md](OCCURRENCE_ACCOUNTING_MECHANISM.md), [OCCURRENCE_ACCOUNTING_EXPLORATORY_CHARTER.md](OCCURRENCE_ACCOUNTING_EXPLORATORY_CHARTER.md) |

## Supporting deterministic apparatus

The [fixture](FIXTURE.md) and [instrument map](INSTRUMENTS.md) define the shared
deterministic scenario. Its contracts include:

1. [Materialization](MATERIALIZATION.md)
2. [Condition append](CONDITION_APPEND.md)
3. [Admitted roots](ADMITTED_ROOT.md)
4. [Replay-constraint append](REPLAY_CONSTRAINT_APPEND.md)
5. [Foreground delivery](FOREGROUND_DELIVERY.md)
6. [Encounter opening](ENCOUNTER_OPENING.md)
7. [Positive activation](POSITIVE_ACTIVATION_DECISION.md)
8. [Practice request](PRACTICE_REQUEST.md)
9. [Model invocation](MODEL_INVOCATION.md)
10. [Action commitment](ACTION_COMMITMENT.md)

Later contracts cover [environment application](ENVIRONMENT_APPLICATION.md),
[consequence intake](CONSEQUENCE_INTAKE.md), and
[experience closure](EXPERIENCE_CLOSURE.md). The
[micro-environment charter](MICRO_ENVIRONMENT_CHARTER.md) owns the isolated
state-dependent transition engine. This apparatus supports observation and
causal audit; it does not establish model development.

## Closed task selection and screening

The [SQLite](SQLITE_CONTACT_CHARTER.md) and
[Python-boundary](PYTHON_BOUNDARY_CONTACT_CHARTER.md) contacts are completed
task-selection results. The admission and model-screening ladder is also
closed:

- [Small-model admission](MODEL_ADMISSION_EXPLORATION.md)
- [Nemotron successor](NEMOTRON_ADMISSION_SUCCESSOR.md)
- [Gemma staircase](GEMMA_CONTRACT_STAIRCASE.md)
- [Structured-output trial](STRUCTURED_OUTPUT_INTERFACE_TRIAL.md)
- [Granite gate](GRANITE_COMPUTATION_GATE.md)
- [Qwen gate](QWEN_COMPUTATION_GATE.md)

Their vector appendices are [Python boundary vectors](PYTHON_BOUNDARY_CONTACT_VECTORS.md),
[model-admission vectors](MODEL_ADMISSION_VECTORS.md), and
[Nemotron successor vectors](NEMOTRON_ADMISSION_SUCCESSOR_VECTORS.md).

These packets remain authoritative for their exact contacts. They are not an
active path toward admitting a practitioner.
