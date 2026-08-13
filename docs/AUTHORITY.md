# Authority and information-flow boundary

Status: **Phase 0 draft specification; no implementation or effect claimed**.

Purpose: prevent the trajectory harness, evaluator, or model from supplying the
development that a formation mechanism is supposed to produce.

## Governing distinction

The formation runtime is the object under test. The trajectory harness is the
external instrument that arranges and measures tests of that object.

The runtime may be assigned a mechanism and a history. It must do its own
interpretation, governance, and activation using only runtime-visible material.
The harness may know what should transfer, which branch is treatment, and what
answer is correct. None of that privileged information may cross into the
runtime.

## Authorities

| Authority | Owns | Must not own |
| --- | --- | --- |
| Human protocol owner | Pre-contact question, mechanism definitions, branch plan, budget, stopping rule | Per-case rescue, post-contact rubric changes, hidden intervention presented as runtime behavior |
| Environment | Situation transitions, tool results, and externally observable consequences | Candidate lessons, admission, or claims about why the practitioner acted |
| Cold model | Inference outputs requested by the runtime, including candidate interpretations when asked | External facts, consequence truth, admission, evaluation verdicts, or claims of causal influence |
| Formation runtime | Execution and replay of runtime-visible lineage, invocation of the selected formation procedure and governor, activation, and the exact offer or intervention supplied to practice | Hidden case families, expected answers, counterfactual outcomes, scorer verdicts, branch labels, or governance decisions outside the declared governor |
| Runtime governor | Admission, suspension, revision, and revocation under a declared policy using runtime-visible evidence | Scientific verdicts or undisclosed evaluator knowledge |
| Consequence oracle | A declared judgment about an action or outcome when the environment does not yield one directly | Candidate content, activation, or retrospective protocol repair |
| Trajectory harness | Identical-prefix construction, assignment, forking, hidden case metadata, execution schedule, ablation, and evidence capture | Interpreting experience on the runtime's behalf or placing a correct abstraction in practitioner state |
| Scorer | Verdicts computed from frozen evidence and rubric | Runtime state, future activation, or case-by-case coaching |

The consequence oracle and scorer may be implemented within the harness
package. Their logical authorities remain separate: consequences may become
runtime-visible experience; experimental verdicts may not.

## Information classes

### Runtime-visible

- the situation available before action;
- the model request and returned output;
- the committed action;
- tool results and declared external consequences;
- runtime-authored interpretations and their source references;
- public mechanism configuration and governance policy;
- public ablation conditions actually applied by the runtime, without hidden
  assignment reasons or expected effects;
- admitted-change state and prior runtime activation receipts; and
- later counterevidence that an ordinary practitioner could observe.

### Harness-only

- branch and treatment labels;
- positive-transfer, non-transfer, and adversarial family labels;
- expected answers and scorer keys;
- held-out structural annotations used to construct cases;
- counterfactual outcomes not observed by the practitioner;
- aggregate results, stopping counters, and cross-branch comparisons; and
- ablation assignments before their effects are materialized in a branch.

### Protocol-public but not runtime input by default

- the research question and claim boundary;
- the list of experimental branches;
- run budgets and stopping rules; and
- the scorer specification.

Public documentation does not automatically authorize offering its contents to
the runtime. Each experiment must freeze the runtime-visible configuration.

## Permitted flow

```text
protocol owner -> harness configuration
protocol owner -> declared runtime mechanism configuration

harness -> environment setup -> runtime-visible situation
runtime -> cold-model request -> model output -> runtime
runtime -> committed action -> environment
environment or consequence oracle -> observed consequence -> runtime lineage

runtime experience -> runtime interpretation -> runtime governor
runtime governor -> admitted state -> later runtime activation
harness ablation assignment -> public ablation condition -> runtime application

runtime and environment receipts -> harness evidence -> scorer verdict
```

The same software process may host several boxes. Permission follows the role
and information class, not the process boundary.

## Forbidden flow

The following invalidate a formation comparison unless they are the explicitly
named baseline being tested:

- the harness writes candidate content or applicability rules into treatment;
- case-family labels, expected answers, or scorer feedback enter a model offer;
- retrieval is keyed by a hidden structural label unavailable in practice;
- a model-authored interpretation is recorded as an external consequence;
- a scorer verdict automatically admits, edits, or revokes runtime state;
- the harness supplies a precomputed or silently repaired practitioner view
  instead of assigning a public ablation condition for the runtime to apply;
- the treatment receives a richer foreground situation than its baseline;
- provider conversation state, prompt caching behavior, or an undeclared prefix
  carries experience across nominally cold invocations;
- a human repairs an individual trajectory after seeing its outcome; or
- an ablation changes unrelated state, foreground data, or execution settings.

## Fork discipline

A controlled formation comparison begins from one materialized prefix:

1. Build the foreground situation and acquisition experience once.
2. Record the exact runtime-visible prefix and model configuration.
3. Fork only for a declared comparison assignment. Mechanism branches bind
   their public persistence or formation condition at that point; branches that
   share a condition until a later ablation remain identical until that public
   condition is bound.
4. Construct each later foreground case once per comparison group.
5. Permit branches to differ only through their declared public conditions,
   persistent state, and downstream causal effects.

If the study concerns naturally diverging developmental trajectories, the
protocol must say so. Such a study answers a different question from a
fixed-history mechanism comparison and cannot use paired-case causal language
without accounting for the divergence.

For an ablation, the frozen protocol names the target and public condition; the
harness assigns them. The runtime must receive that condition explicitly and
apply its declared semantics.
When the condition excludes lineage-derived state, the runtime applies its own
replay semantics and exposes missing dependent state rather than accepting a
precomputed view. Other ablation mechanisms must declare an equivalent
runtime-visible boundary before use. The harness retains the hidden branch
label, causal-probe reason, and expected effect.

## Governance boundary

The runtime governor may be deterministic, rule-based, model-mediated, or
composite. Whatever its form, it must be declared before contact and operate on
runtime-visible evidence.

A candidate trial is an optional runtime-governance operation, not a scientific
test and not a universal lifecycle stage. A policy may require a sandboxed
trial, permit bounded probationary influence, admit directly from declared
consequence lineage, or reject without trial. When a trial is used, its
environment, inputs, and evaluator must be declared and runtime-visible; it may
use sandboxed or replayed encounters but not hidden trajectory families or
scorer keys. Passing it can warrant admission under policy but cannot establish
transfer.

“External controller receipt” means a receipt from this declared runtime
governor or an ordinary environment authority. It does not mean that the
trajectory harness may use its answer key to promote a candidate.

Admission establishes only that a candidate is eligible to influence future
practice. Benefit remains a scorer-owned prospective verdict.

## Inspection and redaction

Primary evidence must make the boundary auditable:

- record the digest or exact bytes of every runtime offer;
- record the model and provider configuration needed to rule out hidden session
  continuity;
- bind runtime rows to corresponding harness rows without copying harness-only
  fields into runtime lineage;
- retain enough environment and oracle evidence to reconstruct consequences;
  and
- make redaction explicit and fail closed when redacted material is required for
  a claimed check.

## Loses-condition

This boundary loses if an implementation can pass its conformance tests while
the harness directly inserts the correct lesson, leaks held-out family identity,
or lets scorer output govern later runtime behavior. It also loses if strict
separation prevents the runtime from receiving consequences that would be
available in ordinary practice.
