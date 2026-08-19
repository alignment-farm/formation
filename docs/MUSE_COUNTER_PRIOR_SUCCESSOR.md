# Muse counter-prior successor contact

Status: **stopped exploratory successor; provider evidence retained; no model
behavior or Formation verdict is available**.

## Purpose

Run one operational model substitution on the exact consumed calibration
mechanism-discovery packet. The Qwen3 14B contact created a real information
gap but did not use a contradictory transition: raw occurrence and authored
interpretation both preserved a first-slot-increases prior.

This successor asks only:

> Does one larger, already-installed cold model use the same external
> consequence differently enough to show that counter-prior information use is
> contactable on this surface?

It is not an admission packet, a model search, a ranking, or validation. The
cases are already exploratory and remain ineligible for prospective claims.
No third model follows automatically.

## Exact model and provider

Use only:

```text
model: huggingface.co/meta-models/muse-glimmer-30b-gguf:Q4_K_XL
artifact digest: sha256:ad54b4b4122ee8e98fd5528a4e26bcbf59034b3b8d0d6d0d1acda98a5f759b6e
architecture: muse-glimmer
parameters: 27.85B
quantization: MOSTLY_Q4_K_M
artifact size: 18.29GiB
provider: Docker Model Runner llama.cpp endpoint
endpoint: http://localhost:12434/engines/llama.cpp/v1/chat/completions
```

The artifact was installed before this successor was selected. Retain a fresh
inventory, inspection, runner status, and version. Do not use `gpt-oss:20B`,
download another model, or test another checkpoint if this setup is awkward or
null.

Every call is cold at the provider-conversation boundary. Only the declared
request may carry experience-derived material.

## Fixed packet and only permitted changes

Reuse exactly from
[the completed calibration charter](CALIBRATION_MECHANISM_DISCOVERY.md):

- the public operating rule;
- both hidden profiles and acquisition states;
- all eight later public states and harness-only expected actions;
- raw, authored, governed, and no-persistence offer semantics;
- the transition-derived candidate governor;
- the unobserved-family `unwarranted_guess` classifier;
- the rotating two-repetition schedule;
- content-only action and candidate parsing;
- transport-only retry; and
- the exploratory claim boundary.

The only substantive substitution is the exact model artifact. The request
surface makes two disclosed model-native adjustments:

1. omit Qwen's `/no_think` soft instruction; and
2. allow 256 actor completion tokens and 384 interpreter completion tokens so
   the model's native reasoning channel does not force visible JSON truncation.

All actor calls use:

```json
{
  "max_tokens": 256,
  "temperature": 0.6,
  "top_p": 0.95,
  "stream": false,
  "response_format": {"type": "json_object"}
}
```

Interpreter calls use the same settings with `max_tokens: 384`. Only
`choices[0].message.content` supplies actions or candidates. Retain every other
response field, including provider reasoning. Do not promote reasoning text
into a missing or malformed answer.

These interface changes mean the successor is not a controlled model-only
comparison. It is an operational replication asking whether the scientific
problem can be contacted with this setup.

## Interface, authorship, and governance

Run the same disposable current-state interface check. It checks only whether
one permitted action is observable. Incorrect behavior, variance, failure to
use experience, or a refused candidate never starts another model loop.

Each world gets the same acquisition actor, exact external consequence, and
cold interpreter responsibilities. Candidate schema and governance clauses are
unchanged. The runtime checks a candidate only against runtime-visible
transition facts and never repairs it from the hidden profile.

Governed activation remains exact: expose the unmodified admitted candidate
only for a non-current device with the same public controller family. Otherwise
use the byte-identical `NONE` offer.

## Budget and stopping

The logical schedule remains:

```text
1 disposable interface call
2 acquisition actor calls
2 interpreter calls
64 later actor calls
69 planned logical calls
```

The physical ceiling remains 72 attempts. Retry once only after a local
transport failure with no HTTP response. Stop on exact model/provider mismatch,
unobservable interface or acquisition action, exhausted budget, or
infrastructure failure. Do not rescue malformed content, change a prompt, or
substitute a model.

## Retained record and exit

Retain the same exact provider, request, response, environment, candidate,
governance, activation, schedule, and classifier evidence required by the
completed charter. The summary may descriptively compare this successor with
the retained Qwen observation, while disclosing the model-native interface
changes. It must keep `formation_verdict` null.

The successor exits by resolving the route, not by passing a threshold:

- If it uses the contradictory experience, the next problem is whether raw,
  authored, and governed handling differ on fresh mechanism-discovery cases.
- If it repeats the prior or ignores the safety rule, the present contact
  surface has not engaged selective consequence use across two operational
  setups. Stop model substitution and redesign the representation or practice.
- If the interface is unobservable, retain that exact operational result and
  stop. Do not convert it into admission screening.

## Stopped contact

The successor stopped on 2026-08-17 after its first physical attempt. Docker's
llama.cpp backend returned HTTP 500 while loading the exact artifact because it
did not recognize the `muse-glimmer` architecture. The
[evidence record](../evidence/muse-counter-prior-successor-20260817/README.md)
contains the exact server response. No model message or action was observed,
and no further model substitution is licensed.
