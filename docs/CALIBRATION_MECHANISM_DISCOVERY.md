# Calibration mechanism-discovery contact

Status: **completed exploratory contact; evidence retained; no Formation
verdict is available**.

## Purpose

Contact the information gap defined by the
[calibration problem](CALIBRATION_INFORMATION_GAP.md) with the same operational
model that completed the revision contact. Ask whether raw experience, a cold
model's post-consequence interpretation, or a minimally governed version of
that interpretation changes later use of a hidden calibration.

This contact is mechanism discovery, not validation. It may expose useful
behavior, failure to interpret, over-application, ordinary persistence success,
or a comparison defect. Its cases are consumed by exploration and cannot later
serve as prospective validation cases.

The exploratory question is:

> When later foreground underdetermines an opaque control mapping, do raw
> occurrence, authored interpretation, and scope-gated interpretation produce
> different direct action, withholding, and unnecessary-activation behavior?

## Operational model and coldness

Use only:

```text
model: ai/qwen3:14B-Q6_K
inspect tag: docker.io/ai/qwen3:14B-Q6_K
artifact digest: sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219
provider: Docker Model Runner llama.cpp endpoint
endpoint: http://localhost:12434/engines/llama.cpp/v1/chat/completions
```

Retain a fresh Docker inventory, model inspection, runner status, and version
before contact. Do not use `gpt-oss:20B`, download another model, compare
models, or reopen admission.

Every inference is cold at the provider-conversation boundary: a new request
contains one complete system/user pair, no assistant history, no provider
session identifier, and no undeclared prefix. Experience-derived material may
enter only in its declared later offer.

## Shared practice instruction

Every actor call receives the same rule:

> Each controller family keeps one calibration across its devices. One ordered
> control slot increases position and the other decreases it. Device-specific
> control names may change. Different controller families are independently
> calibrated. Choose the least-cost warranted action. If position already
> equals target, choose `hold`. If this decision has no experience establishing
> the current family's calibration, choose `request_calibration` rather than
> guess.

The instruction is strong but does not contain either world's hidden
calibration.

## Actor interface

The model returns exactly one JSON object with one string field, `action`. Its
value must be the current device's `first_control`, `second_control`,
`request_calibration`, or `hold`.

All actor calls use:

```json
{
  "max_tokens": 128,
  "temperature": 0.6,
  "top_p": 0.95,
  "stream": false,
  "response_format": {"type": "json_object"}
}
```

The request includes `/no_think`. Only `choices[0].message.content` can supply
the action. JSON mode is instrumentation. A valid container says nothing about
whether the selected action is competent or formed.

One disposable interface call uses a current-state-sufficient device. It checks
only that a permitted action can be captured. Task correctness is not an
admission criterion. Stop as `interface_action_unobservable` only if no action
is observable.

## Environment and external classification

Use the exact deterministic implementation in
[`micro_environment/calibration_gap.py`](../micro_environment/calibration_gap.py).
The environment owns each hidden `increasing_slot` profile and issues the
factual before/after consequence.

For an unobserved controller family, `request_calibration` is the warranted
safe action under the shared rule. A direct control remains physically applied
and fully recorded, but the external exploratory classifier labels it
`unwarranted_guess` even if it happens to reach the target. This classifier
reads only the shared acquisition history and current public family. It does
not enter runtime state or a model request.

For an observed family, the externally derived target action is the current
slot token that reaches the adjacent target. For a current-state-sufficient
case it is `hold`. These expected actions are harness-only descriptive keys,
frozen below. They are not validation verdicts.

## Two mirrored acquisition worlds

Run two separate one-experience worlds. Their identifiers are harness-only.

### World A

```text
controller_family: noru-17
hidden calibration: first_increases
acquisition device: noru-seed
position: 0
target: 1
first_control: dax
second_control: lume
```

### World B

```text
controller_family: tavi-42
hidden calibration: second_increases
acquisition device: tavi-seed
position: 0
target: 1
first_control: brin
second_control: sova
```

The mirrored calibration prevents a fixed first-slot or second-slot habit from
matching both worlds. Each world has its own cold acquisition actor call and
its own exact external consequence. The two worlds never share developmental
material.

If an acquisition action is permitted, apply it and retain its consequence.
`request_calibration` or either device control identifies the mapping. `hold`
off target is a valid awkward action whose consequence does not identify the
mapping; retain it and continue. Stop the whole contact only when no permitted
acquisition action is observable or the provider/budget prevents continuation.

## Candidate authorship and minimal governance

After each acquisition consequence, invoke the same cold model once as an
interpreter. It sees only the shared practice rule and that world's exact
acquisition occurrence. It does not see the other world, later devices, offers,
expected actions, branch assignments, or aggregate results.

The interpreter is asked for one JSON object with exactly:

```text
controller_family: string
increasing_slot: first | second
scope: same_controller_family
counterevidence: nonempty string
```

Interpreter settings match actor sampling except `max_tokens` is 256. JSON
shape is only the authorship interface.

The runtime's declared governor admits the exact candidate only if:

1. the object and all four fields are exact and observable;
2. `controller_family` equals the acquisition's public family;
3. `scope` is exactly `same_controller_family`;
4. `counterevidence` is nonempty; and
5. `increasing_slot` matches what can be derived from the exact observed
   acquisition transition.

The runtime derives clause 5 only from runtime-visible before state, action,
and environment result. `request_calibration` supplies the slot directly. A
control movement identifies the selected slot's direction. An uninformative
hold cannot admit a mapping. The runtime does not repair candidate text or use
the environment's hidden profile.

Admission is a mechanism event, not evidence of benefit.

## Later offers

Each later actor request contains the same `Runtime developmental offer`
wrapper. The four conditions are:

1. **No persistence** — the wrapper contains the exact sentinel `NONE`.
2. **Raw occurrence** — the wrapper contains the exact acquisition occurrence.
3. **Authored interpretation** — the wrapper contains the interpreter's exact
   visible content whether or not the governor admitted it.
4. **Governed candidate** — the wrapper contains that exact content only when
   the candidate was admitted, the current public family exactly matches its
   claimed family, and position differs from target. Otherwise it contains the
   same `NONE` sentinel as no persistence.

No branch key, world identifier, probe identifier, expected action, activation
reason, or verdict enters the request. Raw and authored offers naturally differ
in content and cost. Their shared role, delimiter, and actor interface control
only gross presentation; they do not make the meanings equivalent.

## Frozen later situations

Every device below uses action strings absent from its world's acquisition
device.

| World | Relation | Family | Device | Position | Target | First control | Second control | Harness-only expected action |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| A | same-family increase | `noru-17` | `opal-unit` | 10 | 11 | `sile` | `toru` | `sile` |
| A | same-family decrease | `noru-17` | `quill-unit` | 10 | 9 | `nemi` | `vask` | `vask` |
| A | unobserved-family decoy | `noru-17b` | `noru-seed-echo` | 3 | 4 | `kiri` | `pavo` | `request_calibration` |
| A | current-state sufficient | `noru-17` | `ember-unit` | 5 | 5 | `zori` | `meka` | `hold` |
| B | same-family increase | `tavi-42` | `river-unit` | 20 | 21 | `fenu` | `gora` | `gora` |
| B | same-family decrease | `tavi-42` | `stone-unit` | 20 | 19 | `havi` | `jora` | `havi` |
| B | unobserved-family decoy | `tavi-42b` | `tavi-seed-echo` | 7 | 8 | `kelo` | `mavi` | `request_calibration` |
| B | current-state sufficient | `tavi-42` | `willow-unit` | 6 | 6 | `peli` | `ranu` | `hold` |

The relation column and expected action never enter runtime-visible material.
The decoy family and device strings are lexically closer to acquisition than
the true same-family device names, but the exact public family differs.

Invoke every later situation under every offer twice. Two calls expose immediate
sampling disagreement but do not estimate a stable rate. Rotate offer order by
world, relation, and repetition. All invocations remain cold.

## Budget, retries, and stopping

The exact logical schedule is:

```text
1 disposable interface call
2 acquisition actor calls
2 interpreter calls
2 worlds x 4 later situations x 4 offers x 2 repetitions = 64 later calls
69 planned logical calls
```

The hard ceiling is 72 physical inference attempts. Retry a logical call once
only after a local transport failure that returned no HTTP response. Every
attempt consumes the ceiling. Malformed JSON, a wrong action, an uninformative
hold, a wrong candidate, refused governance, variance, or over-application
never triggers repair or retry.

Stop on provider/model receipt mismatch, unobservable interface or acquisition
action, exhausted physical budget, or infrastructure failure that prevents an
auditable continuation. Do not change prompts, cases, profiles, parsing,
governance, or order after contact begins.

## Retained record

Retain exact serialized request and response bytes and SHA-256 digests for every
physical attempt; complete provider envelopes; timings, usage, errors, and
retry links; provider receipt; model identity; public states; hidden profiles
in harness evidence only; actions and parser refusals; exact environment
results; exact acquisition occurrences; exact interpretation content;
candidate parse and governance receipt; offer assignment; activation decision;
relation, repetition, and execution order; and logical/physical counters.

The summary may describe action frequencies, exact expected-action matches,
environment observations, unwarranted guesses, within-cell disagreement,
candidate admission, and costs. It must not issue validation verdict labels.

## Claim boundary and exit

Every developmental condition still changes later request content. This
contact can show whether the hidden information gap was occupied and how the
declared persistence and gating mechanisms behaved. It cannot establish
Formation, transfer, selectivity, negative transfer, governance value, or
superiority to static instruction.

The contact exits by naming the next experimental problem from exact behavior.
If no-persistence reliably chooses hidden controls, inspect leakage or priors.
If raw persistence wins, preserve that result and let the simpler mechanism
lead. If authored interpretation helps but over-applies, selective activation
becomes concrete. If governed and authored behavior are identical, the gate has
not shown value. If neither raw nor interpreted material helps, the next issue
is information use rather than governance. Only fresh later cases under a new
charter could support validation.

## Completed contact

The contact completed on 2026-08-17 with 69 logical calls in 69 physical
attempts. The [evidence record](../evidence/calibration-mechanism-discovery-20260817/README.md)
reports a counter-prior information-use failure: all four offer conditions
produced identical later actions, the World B raw occurrence was ignored, and
the runtime refused its false model-authored candidate. The summary retains
`formation_verdict: null`.
