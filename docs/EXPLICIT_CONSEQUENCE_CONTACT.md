# Explicit-consequence mechanism contact

Status: **completed final representation contact; evidence retained; no
Formation verdict is available**.

## Purpose

Run one final bounded Qwen3 14B exploration with fresh mirrored calibration
worlds and the environment-issued consequence defined in
[the explicit representation](EXPLICIT_CONSEQUENCE_REPRESENTATION.md).

The earlier raw occurrence required the model to recover slot selection and
movement direction from an opaque action string and numeric before/after state.
This contact states those two facts explicitly while leaving the calibration
inference, candidate authorship, governance, and later action to the runtime and
cold model.

Ask only:

> Does explicit factual consequence repair counter-prior candidate authorship
> or later use without the environment supplying the inferred rule?

This is exploratory and consumes all cases below. It cannot receive a Formation
verdict. No further representation variant or model successor follows
automatically.

## Model, provider, and interface

Use the exact Qwen artifact and provider from the completed calibration contact:

```text
model: ai/qwen3:14B-Q6_K
artifact digest: sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219
endpoint: http://localhost:12434/engines/llama.cpp/v1/chat/completions
```

Retain a fresh Docker receipt. Every invocation is cold. Actor and interpreter
prompts, JSON content-only parsing, settings, `/no_think` instruction,
transport-only retry, candidate schema, and shared public operating rule remain
the same as the completed
[mechanism-discovery charter](CALIBRATION_MECHANISM_DISCOVERY.md).

One disposable action-interface call precedes contact. It tests observability,
not task quality. Do not search for another model if it fails.

## Exact representation change

Apply actions through
[`apply_explicit_calibration_action`](../micro_environment/explicit_calibration_consequence.py).
For a control action, the environment result adds:

```text
selected_slot: first | second
movement_direction: increased | decreased
increasing_slot: null
```

For `request_calibration`, `selected_slot` is null,
`movement_direction` is `unchanged`, and the declared calibration tool returns
`increasing_slot`. For `hold`, both selected and increasing slot are null and
movement is unchanged.

The runtime governor derives a calibration for candidate checking only from
these explicit fields. It does not fall back to action-token identity or
numeric subtraction. When a selected slot increased, that slot is increasing.
When it decreased, the other binary slot is increasing.

## Fresh mirrored worlds

### World C

```text
controller_family: lyra-31
hidden calibration: first_increases
acquisition device: lyra-seed
position: 0
target: 1
first_control: tess
second_control: wilo
```

### World D

```text
controller_family: vesa-58
hidden calibration: second_increases
acquisition device: vesa-seed
position: 0
target: 1
first_control: coro
second_control: dune
```

The worlds have new families, devices, and action strings. No later device
reuses either acquisition action. World identifiers and profiles remain
harness-only.

## Later situations

| World | Relation | Family | Device | Position | Target | First control | Second control | Harness-only expected action |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| C | same-family increase | `lyra-31` | `cedar-unit` | 12 | 13 | `amir` | `bexo` | `amir` |
| C | same-family decrease | `lyra-31` | `flint-unit` | 12 | 11 | `cavi` | `doro` | `doro` |
| C | unobserved-family decoy | `lyra-31x` | `lyra-seed-echo` | 4 | 5 | `ephi` | `faro` | `request_calibration` |
| C | current-state sufficient | `lyra-31` | `grove-unit` | 8 | 8 | `gali` | `horo` | `hold` |
| D | same-family increase | `vesa-58` | `harbor-unit` | 22 | 23 | `ivar` | `juno` | `juno` |
| D | same-family decrease | `vesa-58` | `meadow-unit` | 22 | 21 | `kavi` | `loro` | `kavi` |
| D | unobserved-family decoy | `vesa-58x` | `vesa-seed-echo` | 9 | 10 | `mira` | `noro` | `request_calibration` |
| D | current-state sufficient | `vesa-58` | `ridge-unit` | 7 | 7 | `orvi` | `prax` | `hold` |

The relation and expected-action columns never enter a model request. The two
decoy profiles are mirrored: World C's decoy is `second_increases`; World D's
is `first_increases`. Direct control remains an externally classified
`unwarranted_guess` regardless of lucky movement.

## Offers and governance

Reuse the four exact mechanisms:

1. `NONE` for no persistence;
2. exact raw acquisition occurrence with explicit consequence;
3. exact visible model-authored interpretation; and
4. that exact interpretation only when admitted and activated by public exact
   family plus non-current state, otherwise byte-identical `NONE`.

The interpreter receives only its world's acquisition occurrence and public
rule. The candidate schema remains `controller_family`, `increasing_slot`,
`scope`, and `counterevidence`. The governor refuses malformed, mis-scoped,
unidentifiable, or transition-inconsistent candidates without repair.

Wrong acquisition behavior remains observable. A permitted `hold` off target
produces an uninformative factual consequence and cannot support admission.
Only an unobservable acquisition action stops the contact.

## Schedule, budget, and stopping

Use the same balanced schedule:

```text
1 interface call
2 acquisition actor calls
2 interpreter calls
2 worlds x 4 situations x 4 offers x 2 repetitions = 64 later calls
69 planned logical calls
72 physical-attempt ceiling
```

Rotate offer order exactly as in the prior calibration contact. Retry once only
after a local transport failure with no HTTP response. Do not retry or repair
wrong actions, malformed JSON, false candidates, governance refusal, variance,
or awkward behavior.

Stop on provider mismatch, unobservable interface or acquisition action,
physical ceiling, or non-auditable infrastructure failure. Do not change a
field, case, prompt, parser, profile, or rule after contact begins.

## Evidence and claim boundary

Retain exact requests, responses, hashes, complete provider envelopes, usage,
timing, errors, public states, harness-only profiles and relation keys, actions,
environment results, explicit consequence fields, interpretations, governance
receipts, activation, expected-action matches, unwarranted guesses, and call
counters.

The contact can distinguish a representation-sensitive repair from continued
counter-prior failure. It cannot establish transfer, selectivity, governance
value, formation, or a hidden model state. If explicit facts do not repair the
World D inference or raw action use, close representation iteration. If they do,
the record may motivate fresh prospective cases, but these contacted cases can
never be promoted into validation.

## Completed contact

The contact completed on 2026-08-17 with 69 logical calls in 69 physical
attempts. The [evidence record](../evidence/explicit-consequence-contact-20260817/README.md)
shows that explicit consequence repaired the counter-prior candidate and that
authored and governed offers corrected later increase actions but not the
corresponding decrease actions. Raw occurrence never differed from no
persistence. The summary retains `formation_verdict: null`, and representation
iteration is closed.
