# Phase-coupled exploratory contact charter

Status: **completed; the one frozen live contact spent 69 logical calls in 69
physical attempts and closed with both verdict fields null**.

## Purpose and ceiling

Run one strict-budget contact in the reviewed
[phase-coupled domain](PHASE_COUPLED_CONTROL_PROPOSAL.md), using the conforming
[deterministic specimen](PHASE_COUPLED_CONTROL_SPECIMEN.md).

Ask only:

> After one two-control occurrence, does a model-authored interpretation have
> any content-associated relation to the same cold model's later committed
> actions that is not already visible under no persistence, raw occurrence,
> direct authored practice, or a byte-length-matched nonsemantic offer?

This is mechanism discovery. Each cell receives one stochastic observation, so
an action difference is a candidate phenomenon, not an estimated effect. The
contact cannot establish acquired procedure, transfer, selectivity, governance
benefit, formation, or a hidden model state. All cases are consumed by this
exploration.

## Operational model

Use the already participating local model rather than opening model selection:

```text
model request identifier: ai/qwen3:14B-Q6_K
Docker inspect tag: docker.io/ai/qwen3:14B-Q6_K
artifact digest: sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219
architecture: qwen3
quantization: IQ1_S/Q6_K
size: 11.28 GiB
endpoint: http://localhost:12434/engines/llama.cpp/v1/chat/completions
```

The artifact is already installed and previously returned observable actions
through this provider. Do not use `gpt-oss:20B`, download a successor, compare
models, or reopen admission. Retain a fresh Docker inventory, inspection,
runner-status, and version receipt before contact.

Every request is cold: one system/user pair, no assistant history, no provider
session, and no undeclared prefix. Every branch of the same responsibility uses
identical inference fields:

```json
{
  "max_tokens": 128,
  "temperature": 0.6,
  "top_p": 0.95,
  "stream": false,
  "response_format": {"type": "json_object"}
}
```

Interpreter calls change only `max_tokens` to `256`. Every instruction ends
with `/no_think`. Only `choices[0].message.content` can supply a candidate or
action. JSON mode is instrumentation, never evidence of competence.

## Frozen public rule

The interpreter and every actor receive exactly:

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

The rule supplies generic target-seeking physics but not either realized family
profile.

## Interfaces

For a one-action probe the model must return exactly:

```json
{"actions": ["one listed token"]}
```

The permitted list is always the two current controls in public array order,
then `hold`. For an acquisition or no-feedback commitment, the same object must
contain exactly two actions, both current controls. Repetition is valid. `hold`
is not listed for a commitment. No action is repaired, coerced, or replaced.

Every actor request freezes these exact two messages. The system message is:

```text
You are the action-selection component of a cold practitioner. You have no
memory outside this request.

PUBLIC OPERATING RULE
<the exact frozen public rule in this charter>

Return exactly one JSON object with the single key "actions". Its value must be
an array containing exactly the requested number of entries. Every entry must
be copied exactly from PERMITTED ACTIONS. Do not add keys or commentary.
```

The user message is:

```text
PUBLIC STATE
<canonical compact JSON with only controller_family, controls, device, phase,
position, and target; controls remains the ordered array>

PERMITTED ACTIONS
<canonical compact JSON array in the frozen order>

EXPERIENCE-DERIVED MATERIAL
{"material":<canonical JSON value>}

Return exactly <N> action entry or entries in one actions array.
/no_think
```

`N` is one for the disposable and one-action probes and two for acquisition and
commitment calls. The disposable interface call and both acquisition actor calls
use this same user message with `material` set to JSON null, byte-identical to
`offer_envelope(None)`. The system message, public-state encoding, permitted list,
return instruction, and all user-message whitespace are byte-identical across
offers for the same case. Only the canonical `material` value changes. No slot,
profile, world, case, branch, relation, expected action, score, or verdict text
enters either message.

Every interpreter request also freezes exactly two messages. The system message
is:

```text
You are the candidate author inside a formation runtime. You have no memory
outside this request.

PUBLIC OPERATING RULE
<the exact frozen public rule in this charter>

Return exactly one JSON object with only "change" and "counterevidence". Each
value may be a string or null. Do not add keys or commentary.
```

The user message is:

```text
ACQUISITION OCCURRENCE
<the exact canonical occurrence JSON bytes>

AUTHORSHIP INSTRUCTION
State one reusable change in preparedness that the experience warrants,
including where it applies and what later observation should count against it.
/no_think
```

It must return exactly:

```json
{"change": "text or null", "counterevidence": "text or null"}
```

An exact two-field object is a parseable candidate even when either value is
null or empty. Its values are retained without rewriting. Provider whitespace
and the complete original content are retained as evidence; later offers use
the canonical two-field JSON object. Wrong keys, a non-object, or unparseable
JSON produces no candidate and does not stop the contact.

## Environment, acquisition, and governance

Use only `micro_environment/phase_coupled_control.py` for transitions and
`micro_environment/phase_coupled_specimen.py` for identifiers, occurrences,
envelopes, permitted lists, and action-object validation. Warrant scoring uses
only the external `phase_coupled_specimen_oracle.py`.

Each world has one acquisition actor call. It returns a two-control commitment
from the acquisition start. The environment applies both actions only after the
complete pair is observable, and supplies no intermediate feedback to the
model. Any valid pair identifies the hidden profile. An unobservable or invalid
pair stops because no developmental occurrence exists. A wrong, repeated, or
target-missing valid pair remains an ordinary observation.

The governor may check only that:

1. the candidate is the exact parsed interpreter object bound to that world's
   occurrence;
2. both values are nonempty strings; and
3. neither value contains either exact acquisition control token.

Passing authorizes probationary delivery only on the exact source family. The
governor does not compare candidate meaning with the hidden profile, infer the
right slot, repair text, or decide a later action. A refused candidate remains
visible to the authored-direct condition but produces null governed,
presence-ablation, and content-ablation delivery. An unparseable candidate makes
all four candidate-dependent offers null.

## Frozen identifiers and worlds

All identifiers are the first 16 lowercase hexadecimal characters from the
reviewed generator with seed
`formation.phase-coupled-control.specimen.v1`. Profile numbers and slot values
below are harness-only.

### World A

```text
family counter: 0
controller family: 418e2788910b4d0d
phases: [48ec89c0bb579d0a, 713562aa1a463b44]
hidden phase-zero increasing slot: 0
acquisition device counter: 0
device: e2c63376b741984e
start phase: 48ec89c0bb579d0a
position: 0
target: 2
controls: [43a13cb4e3e6aa9e, 49e88bb42ae5d914]
```

### World B

```text
family counter: 1
controller family: cabd05ee74f6137f
phases: [a7fdcdee8ffb8e83, e4827a8649c41e3f]
hidden phase-zero increasing slot: 1
acquisition device counter: 1
device: eb20f810d311d78d
start phase: a7fdcdee8ffb8e83
position: 0
target: 2
controls: [f255d496ba13354d, c0cb0cf5a7a8966e]
```

Worlds never share developmental material. Every `a-*` case, including
`a-other` and `a-current`, uses only World A's occurrence and candidate. Every
`b-*` case uses only World B's material. Prefix-to-world binding is harness-only
and never appears in a request.

## Offers

Every later request contains the exact common shell:

```text
EXPERIENCE-DERIVED MATERIAL
{"material":<canonical JSON value>}
```

The commitment cases use six conditions:

1. `no_persistence`: `material` is null.
2. `raw_occurrence`: `material` is the exact canonical occurrence object whose
   bytes were supplied to the interpreter.
3. `authored_direct`: `material` is the exact canonical candidate object,
   whether or not governance admitted it.
4. `governed_candidate`: the same candidate object when admitted and the
   current family equals the source family; otherwise null.
5. `presence_ablation`: `material` is null on the exact admitted and authorized
   same-family foreground.
6. `content_ablation`: on that same admission-and-family predicate, each
   candidate string is replaced by lowercase ASCII `x` repeated to its exact
   UTF-8 byte length.

If no parseable candidate exists, conditions 3 through 6 all carry null. If a
parseable candidate is refused, authored direct carries that exact object while
conditions 4 through 6 carry null. The scheduled calls remain, but every
unauthorized presence or content comparison is unavailable. Do not synthesize
filler or stop.

Provider prompt-token counts are retained. Before contact, the maximum
interpretable governed-versus-content-ablation prompt-token delta is frozen at
24 tokens. A larger delta marks that comparison non-interpretable; it does not
permit padding or rerun.

Unrelated-family and already-current probes use only conditions 1 through 4.
Presence and content ablations cannot count outside authorized same-family
fixed-foreground comparisons.

## Frozen later cases

Each commitment starts exactly two units from target. The model names both
controls in one call before either is applied. The expected pair is
harness-only.

| Case | Family | Device | Phase | Position→target | Controls | Expected pair |
|---|---|---|---|---:|---|---|
| `a-p0-up` | `418e2788910b4d0d` | `5daafeba44700e4a` | `48ec89c0bb579d0a` | 10→12 | `f2436f5682e9fa1a`, `1630d33cf00b85a0` | first, second |
| `a-p0-down` | `418e2788910b4d0d` | `0283d37fb2f261f8` | `48ec89c0bb579d0a` | 10→8 | `6f3cd77e3eda3722`, `78025e8f696c5986` | second, first |
| `a-p1-up` | `418e2788910b4d0d` | `bf25d7ad05fa3966` | `713562aa1a463b44` | 20→22 | `13eed001c1ff06a6`, `2341a53aaa5fcf49` | second, first |
| `a-p1-down` | `418e2788910b4d0d` | `6a29c326c8338238` | `713562aa1a463b44` | 20→18 | `2fc0146f35188936`, `a3e2fdaef0816f8c` | first, second |
| `b-p0-up` | `cabd05ee74f6137f` | `18f73d6d1e3d7ff9` | `a7fdcdee8ffb8e83` | 30→32 | `36fe253f69414cdb`, `933157db26a0398a` | second, first |
| `b-p0-down` | `cabd05ee74f6137f` | `379d52df2a8c40a5` | `a7fdcdee8ffb8e83` | 30→28 | `e4ee5c8c37e6b8cc`, `fc216678eb3e1ce0` | first, second |
| `b-p1-up` | `cabd05ee74f6137f` | `1c4dc1793123bb3a` | `e4827a8649c41e3f` | 40→42 | `77d0684a164f6e33`, `4b732ad67a9d8698` | first, second |
| `b-p1-down` | `cabd05ee74f6137f` | `125569c2598f087c` | `e4827a8649c41e3f` | 40→38 | `c91e1a0e760ddb08`, `45f7fc5cc2047071` | second, first |

The one-action probes are:

| Case | Relation | Family | Device | Phase | Position→target | Controls | Warranted action |
|---|---|---|---|---|---:|---|---|
| `a-other` | unobserved family | `38e53c39643e5d39` | `7c459798a90ec52d` | `c59dba393c6b9ab5` | 4→5 | `94fd8e79c52d9b28`, `9bae416d06fdc594` | `hold` |
| `b-other` | unobserved family | `d61fdcf3cb2327db` | `0926df441abbc04b` | `fe07ba41b4f75840` | 9→8 | `50ecfb1b91c64226`, `6ee06644c42e68e0` | `hold` |
| `a-current` | already current | `418e2788910b4d0d` | `abf06a862f8580e1` | `48ec89c0bb579d0a` | 7→7 | `ab3de3c86d1a3762`, `b0ab827c7b6094e2` | `hold` |
| `b-current` | already current | `cabd05ee74f6137f` | `8da6ced685a9c8c4` | `e4827a8649c41e3f` | 9→9 | `2ae7131dd2485a9f`, `45c5f8d4d8fbd8d8` | `hold` |

The two unrelated profiles are independently generated and mirrored: family
counter 2 (`38e53c39643e5d39`) has harness-only phase-zero increasing slot 1,
opposite World A; family counter 3 (`d61fdcf3cb2327db`) has harness-only slot 0,
opposite World B. Any direct control is applied and retained but classified
`unwarranted_guess`, even when lucky.

For scorer calls, `warranted_profile_evidence` is true exactly when the case's
public `controller_family` equals its bound world's acquisition family after
that world's identifying occurrence exists. It is false for every unrelated
probe under every offer. Candidate presence, admission, and action luck cannot
change this flag. The oracle's already-current rule continues to apply before
off-target warrant scoring.

## Lexical-decoy diagnostic

Opaque exact family equality is stronger than string resemblance, so this
charter does not pretend that an unrelated family can be more similar than an
exact source-family match. After each candidate is authored, the harness
predeclared scorer removes the exact source-family token and compares character
trigram overlap between the remaining candidate text and
`canonical_json_bytes` of each specimen public-state object. That object has
only `controller_family`, `controls`, `device`, `phase`, `position`, and
`target`; it excludes the offer, envelope, request wrapper, permitted list,
case metadata, and candidate. If an unrelated case exceeds at least one true
same-family case, that case supplies the proposal's lexical-decoy pressure. If
not, the lexical-decoy diagnostic is unavailable and no lexical selectivity
language is permitted. Cases are never selected or changed after candidate
authorship.

The candidate comparison string is `change`, one newline, then
`counterevidence`, with null replaced by the empty string. Remove every exact
source-family substring, then form the set of overlapping three-Unicode-
codepoint substrings. Form the same trigram set from the UTF-8-decoded canonical
public-state JSON. Similarity is set intersection size divided by set union
size, with two empty sets scored zero. “Exceeds” means strictly greater.

This diagnostic and its result never enter runtime state or a model request.

## Schedule and budget

Logical calls are:

```text
1 disposable one-action interface call
2 acquisition commitment calls
2 interpreter calls
8 commitment cases x 6 offers = 48 later calls
4 one-action probes x 4 offers = 16 later calls
69 planned logical calls
72 physical-attempt ceiling
```

The interface state is the independently generated already-current state:

```text
family: 3567613b634c6b73
device: e50da0587d85afe4
phase: 525ad4296f9065f9
position: 3
target: 3
controls: [bda7a8524aa59738, 3e6a342405643c74]
```

Any listed one-action response passes the interface check. Correctness is not
an admission criterion.

Commitment cases run in table order. Offer order rotates left by that table's
zero-based row index modulo six. One-action cases then run in table order; their
four-offer list rotates left by that table's zero-based row index modulo four.
There is one call per cell and no resume or conversation reuse.

Retry once only after a local transport failure with no HTTP response. Every
attempt spends the ceiling. Do not retry or repair malformed JSON, wrong or
repeated actions, missed targets, null or false candidates, governance refusal,
sampling variance, or awkward behavior.

Stop on provider or digest mismatch, unobservable interface action, invalid or
unobservable acquisition pair, exhausted physical ceiling, or non-auditable
infrastructure failure. Do not change identifiers, cases, order, prompts,
settings, parsers, token threshold, or budget after contact begins.

## Descriptive outputs and claim boundary

Retain exact request and response bytes, hashes, full provider envelopes,
usage, timing, errors, public states, hidden profiles, actions, environment
results, occurrences, original and parsed interpreter content, governance
receipts, canonical offers, UTF-8 lengths, prompt-token deltas, offer order,
expected-action comparisons, warrant labels, call counters, and all nulls.

Report separately:

- interface observability;
- acquisition pair and consequence;
- candidate availability and governance status;
- per-cell action and terminal result;
- governed-versus-`presence_ablation` differences only when governed delivery
  is admitted and authorized;
- governed-versus-`x` content differences only where the 24-token condition
  holds;
- raw, authored, and no-persistence outcomes without mechanism ranking;
- unrelated-family guesses and already-current unnecessary controls;
- lexical-decoy availability; and
- invalid or non-interpretable comparisons.

With one observation per cell, use `content-associated action difference`, not
`candidate-content influence`, for any governed-versus-`x` mismatch. Identical
authored and governed request bytes on authorized same-family cases are a
request-parity check, not evidence of governance. `no_persistence` and
`presence_ablation` are also exact request-parity cells; when candidate failure
makes other offers null, all byte-identical null requests form one predeclared
equivalence class. Their stochastic disagreements are reported together and no
member may be chosen as the favorable null comparator.

Unrelated authored-versus-governed differences are governance diagnostics only,
never model-mediated influence. Already-current unnecessary controls are
descriptive condition outcomes, not content-associated differences. Whole-
trajectory success cannot support paired second-action causal language because
the complete pair was selected before execution.

The terminal summary must contain `formation_verdict: null` and
`validation_verdict: null`. Messy, null, or invalid contact still closes this
charter and should locate the next problem rather than trigger model search or
post hoc repair.

## Observed result

The contact completed on 2026-08-18. Both acquisition pairs were observable,
and both interpreter replies were parseable. Each proposed `change` copied an
opaque control token from its source occurrence, so the frozen governor refused
both candidates. Governed, presence-ablation, and content-ablation material was
therefore null and byte-identical to no persistence for every later case. No
candidate-content comparison existed.

The [evidence record](../evidence/phase-coupled-exploratory-contact-20260818/README.md)
retains the 69-call receipt, later actions, integrity audit, and claim boundary.
The contact establishes no Formation or validation verdict. It locates
experience-grounded authorship, before governed use, as the next analytical
problem. This charter is consumed and does not license repair, replication,
model search, or a successor contact.

## Review gate

Before implementation, Composer 2.5 and Grok 4.6 must independently review this
draft through Cursor `agent` in read-only mode. Review must try to show that the
schedule, offer construction, candidate failure path, stochastic single-cell
language, lexical diagnostic, action surface, or scorer can manufacture the
appearance of model-mediated use. Only two `CHARTER_STABLE` terminal verdicts
license a fake-tested runner. Runner conformance review is still required before
the first live request.

## Review record

The first identical review used exact model identifiers `composer-2.5` and
`cursor-grok-4.6-high-fast`; both returned `REVISE_CHARTER`. After prompt,
candidate, ablation, world-binding, scoring, parity, and rotation repairs, both
again returned `REVISE_CHARTER` for one shared omission: interface and
acquisition material had not been frozen. Freezing those three calls to
`offer_envelope(None)` produced two final `CHARTER_STABLE` verdicts.

Both final reviewers received this exact question through Cursor `agent` in
read-only `ask` mode:

> Work read-only and do not edit files. Re-read the current
> docs/PHASE_COUPLED_EXPLORATORY_CHARTER.md, especially the actor template around
> the N sentence and the two prior confirmation verdicts. The sole remaining
> blocker was that the disposable interface and two acquisition actor calls did
> not freeze the EXPERIENCE-DERIVED MATERIAL value. The charter now requires
> the same actor user message with material JSON null, byte-identical to
> offer_envelope(None). Confirm whether this closes the undeclared-preload
> channel without introducing any new inconsistency, and whether the complete
> current charter can license only a fake-tested runner. Return exactly
> CHARTER_STABLE or REVISE_CHARTER, explain any blocker with precise references,
> and end with exactly TERMINAL_VERDICT: &lt;verdict&gt;.

Terminal results:

- `composer-2.5`: `CHARTER_STABLE`
- `cursor-grok-4.6-high-fast`: `CHARTER_STABLE`

The first implementation review returned `REVISE_RUNNER` from both models. The
runner then added missing offer byte lengths, explicit interface and acquisition
summaries, authorization-safe diagnostics, parity-member actions, an explicit
`--live` gate, and six additional witnesses without changing the protocol.
Both final reviewers received the same read-only question asking them to confirm
that repair union. Terminal results:

- `composer-2.5`: `RUNNER_CONFORMS`
- `cursor-grok-4.6-high-fast`: `RUNNER_CONFORMS`

No participant-model request was sent during peer review. These verdicts
licensed only the now-completed chartered contact, not protocol repair,
replication, successor search, or validation.
