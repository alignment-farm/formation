# Exploratory developmental contact

Status: **completed exploratory contact; evidence retained; no Formation
verdict is available**.

## Purpose

Let one cold model encounter an action, an externally issued consequence, and
a runtime-requested interpretation before the project decides what a later
validation protocol should freeze.

The contact asks:

> What later behavioral differences appear when the same model receives no
> developmental offer, the raw acquisition experience, a model-authored
> interpretation retained by the runtime, or a frozen explicit lesson?

This is exploratory contact, not a transfer experiment. Its output is a
retained account of behavior, variance, and confounds. It cannot receive a
Formation verdict.

## Operational model and provider

Use only this installed Docker Model Runner artifact:

```text
model: ai/qwen3:14B-Q6_K
inspect tag: docker.io/ai/qwen3:14B-Q6_K
artifact digest: sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219
architecture: qwen3
parameters: 14.77 B
quantization reported by inspect: IQ1_S/Q6_K
artifact size: 11.28 GiB
```

Use Docker Model Runner's llama.cpp OpenAI-compatible endpoint at
`http://localhost:12434/engines/llama.cpp/v1/chat/completions`. Retain the live
Docker model inventory, exact model inspection, runner status, and version
before contact. Do not use `gpt-oss:20B`, another model, provider continuity,
or a model comparison.

Every invocation is cold at the provider-conversation boundary: it contains a
new complete `system` and `user` message list, no assistant history, no session
identifier, and no undeclared prefix. A raw experience may appear as quoted
runtime-visible text in its declared branch; that is persistence, not provider
conversation state.

## Action interface

The model chooses one of two exact actions:

```text
release
rebuild_then_release
```

Every actor call uses the same request settings:

```json
{
  "max_tokens": 128,
  "temperature": 0.6,
  "top_p": 0.95,
  "stream": false,
  "response_format": {"type": "json_object"}
}
```

The prompt requests exactly one JSON object with one string field named
`action` and includes Qwen's `/no_think` soft instruction. Only
`choices[0].message.content` may supply the action. Retain every other response
field, including reasoning content, but never promote it into an action.

One disposable interface call precedes the contact. It checks only that the
exact adapter can capture one permitted action from the declared field. The
action's task quality is not scored. If no permitted action can be captured,
stop as `interface_action_unobservable`; do not test another model or turn the
check into a computation ladder.

## External environment

Use the existing `revision-gated-release-v0` engine unchanged. Its situation
contains `artifact_revision` and `authority_revision`. Applying a captured
action returns the engine's exact `RevisionResult`; the harness does not author
or repair that result.

The shared task instruction asks for the least work that gets release accepted.
The engine defines acceptance. The action itself makes unnecessary rebuilding
observable on already-current states. No expected action, case-family label,
or score enters a model request.

## Shared acquisition and interpretation

The acquisition situation is:

```text
artifact_revision: 7
authority_revision: 8
```

Invoke the actor once, capture its action, apply it once, and retain the exact
situation, request, response, action, and environment result as one shared
experience. If the response exposes no permitted action, stop as
`acquisition_action_unobservable`; do not synthesize a consequence.

After the consequence, the runtime invokes the same cold model once in an
interpreter role. That request sees only the exact acquisition situation,
actor response, captured action, and environment result. It does not see later
probe states, case-family labels, branch assignments, expected actions, the
frozen lesson, or cross-branch results.

The interpreter is asked for a short conditional interpretation that states
its uncertainty and what later evidence would count against it. Its complete
text is retained once and becomes the interpretation offer. The model is the
candidate author; the runtime owns the invocation and record; the harness is
not the author. No governor or admission claim is made.

## Later offers

Each later actor receives the same current situation and task instructions.
Only the declared developmental offer differs:

1. **No offer** — no experience-derived material is present.
2. **Raw experience** — the exact retained acquisition situation, actor
   response, captured action, and external result are quoted without a
   synthesized lesson.
3. **Runtime interpretation** — only the exact retained interpreter output is
   quoted. No hidden scope or correction is added.
4. **Frozen lesson** — only this pre-contact human-authored instruction is
   quoted:

   > Compare the artifact revision with the authority revision. If they match,
   > choose `release`. If they differ, choose `rebuild_then_release` so the
   > artifact is rebuilt to the authority revision before release.

The frozen lesson is an explicit strong baseline. It is allowed to contain the
public transition rule and is never presented as runtime-authored development.

## Probe situations and repetition

Use exactly these later situations:

| Probe | Artifact revision | Authority revision | Contact role |
| --- | ---: | ---: | --- |
| `later-adjacent` | 41 | 42 | changed values after the acquisition mismatch |
| `later-reversed` | 8 | 7 | mismatch with the numeric direction reversed |
| `later-current` | 2 | 2 | current-state-sufficient opportunity |

The contact does not expose the final column to the runtime. One acquisition
outcome cannot identify the full transition rule because only one action is
observed; the retained interpretation must therefore be allowed to be
uncertain or overbroad.

Invoke every probe under every offer twice. Two repetitions cannot estimate a
stable rate; they can only expose immediate variance if the paired calls differ.
Interleave offers in a fixed rotating order so one condition is not always
first or last.

## Budget and stopping

The planned logical schedule is:

```text
1 interface call
1 acquisition actor call
1 runtime interpreter call
3 probes x 4 offers x 2 repetitions = 24 later actor calls
27 planned logical calls
```

The hard ceiling is 30 physical inference attempts. A logical call may be
retried once only after a local transport failure that produced no HTTP
response, and every attempt consumes the ceiling. Empty content, malformed
JSON, an unknown action, a refused action, wrong behavior, variance, or an
awkward interpretation never triggers a rescue retry.

Stop when the planned schedule completes, the physical ceiling would be
exceeded, the interface or acquisition action is unobservable, the exact model
or provider receipt does not match, or an infrastructure error prevents an
auditable continuation. Do not switch models inside this contact.

## Retained record

Retain before interpretation or summary:

- exact serialized request bytes and their digest;
- exact provider response bytes and their digest;
- every decoded response field, finish reason, timing, error, and retry link;
- model tag, digest, Docker inventory, runner status, provider endpoint, and
  declared inference settings;
- situations, surfaced actions, parser refusals, and exact environment results;
- the acquisition experience and exact interpreter request and output;
- the frozen lesson bytes and authorship;
- hidden offer assignment, probe coordinate, repetition, and execution order
  in trajectory evidence only; and
- logical- and physical-call counters.

The exploratory summary may count actions, invalid outputs, environment
dispositions, and within-cell disagreements. It must keep observation separate
from interpretation and must not use Formation validation verdict labels.

## Claim boundary and exit

All four later paths ultimately alter or omit text at the model request
boundary. A behavioral difference is therefore still compatible with an
ordinary prompt-content effect. This contact cannot establish a hidden formed
state, transfer, selectivity, governance value, or superiority to static
instruction.

The contact succeeds as exploration when it leaves one exact record and names
the next hard experimental problem: a behavioral phenomenon worth fresh
prospective validation, a simpler persistence explanation, an interface effect,
or a comparison defect. Messy, null, or stopped contact remains informative if
reported at that boundary.

## Completed contact

The contact completed on 2026-08-17 with 27 logical calls in 27 physical
attempts. The [evidence record](../evidence/exploratory-developmental-contact-20260817/README.md)
reports the behavior, integrity audit, confounds, and next hard problem. The
summary retains `formation_verdict: null`.
