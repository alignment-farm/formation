# Phase-coupled exploratory contact: observed record

The contact reached the model but did not reach the planned candidate-content
comparison. After each two-control occurrence, the model returned a parseable
interpretation. In both worlds its proposed change copied an opaque control
token from that occurrence. The runtime therefore refused both candidates under
the frozen rule against treating one device's action name as a reusable family
relation.

This is an exploratory result, not a failed admission test. It shows what the
model did when asked to turn experience into a reusable change: each proposed
change was one of the episode's control tokens. Because neither candidate was
admitted, no governed candidate, presence ablation, or content ablation was
delivered. The contact contains no authorized governed-versus-content
comparison and supports no Formation verdict.

## Execution receipt

The contact ran on 2026-08-18 under the frozen
[charter](../../docs/PHASE_COUPLED_EXPLORATORY_CHARTER.md) with
`ai/qwen3:14B-Q6_K`, artifact digest
`sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`,
and Docker Model Runner 1.2.6.

All 69 planned logical calls completed in 69 physical attempts under the
72-attempt ceiling. Every response was HTTP 200. Every actor response contained
the requested number of permitted actions. There were no retries or action
repairs. The provider reported 30,230 prompt tokens and 2,354 completion tokens.
Both `formation_verdict` and `validation_verdict` are null.

## Acquisition and interpretation

Both acquisition calls produced valid two-action commitments, and the
environment applied each complete pair without intermediate feedback.

- In World A, the model selected the two controls in listed order. Both actions
  increased position, and the device reached its target. The interpretation
  used the first control token as `change` and the second as `counterevidence`.
  The runtime refused both copied fields.
- In World B, the model again selected the two controls in listed order. Both
  actions decreased position, and the device missed its target. This remained
  an informative occurrence because the pair identified the hidden profile.
  The interpretation used the second control token as `change` and
  `movement_direction` as `counterevidence`. The runtime refused the copied
  change.

The governor did not judge whether the prose meant the right thing. It checked
only source binding, nonempty fields, and exact reuse of acquisition control
tokens. It did not repair either interpretation.

## Later behavior

Raw occurrence and authored direct supplied distinct later material. The other
four scheduled labels all supplied `{"material":null}` after candidate refusal.
For each case those four model requests were byte-identical, so the table keeps
their samples in one equivalence class. A split means identical requests
returned different samples; it is not an ablation effect.

| Case | Null-request class | Raw occurrence | Authored direct |
| --- | --- | --- | --- |
| A, phase 0, target up | 4 of 4 match | match | match |
| A, phase 0, target down | 0 of 4 match | miss | miss |
| A, phase 1, target up | 0 of 4 match | miss | miss |
| A, phase 1, target down | split: 2 of 4 match | miss | match |
| B, phase 0, target up | 0 of 4 match | miss | miss |
| B, phase 0, target down | split: 3 of 4 match | miss | match |
| B, phase 1, target up | 4 of 4 match | match | match |
| B, phase 1, target down | 0 of 4 match | miss | miss |

Each raw and authored entry is one cold stochastic observation. The null class
contains four independent samples of the same request, not four mechanisms.
The authored-direct and no-persistence samples matched the same four cases;
raw occurrence matched two. These descriptive facts do not estimate condition
effects: there was one observation per distinct-material cell, the candidate
was not admitted, and authored text can change an answer as ordinary prompt
content.

On the unobserved-family cases, all four World A offers guessed a control. In
World B, only raw occurrence held; the other three offers guessed. Those guesses
were unwarranted under the public rule even where one happened to move toward
the target. Every already-current offer in both worlds correctly held. The
lexical-decoy diagnostic was available in both worlds. It cannot support
lexical-selectivity language about governed delivery because no candidate was
admitted.

## What this contact located

The immediate problem occurs before governed use. A cold model saw action,
external consequence, and the generic device rule, but its model-authored
candidate remained tied to an episode token that the rule itself said had no
meaning across devices. More restrictive output syntax could prevent that
string from appearing, but it would not make the model author the missing
relation.

The next research boundary is therefore **experience-grounded authorship**:

> How can a practitioner turn a consequential occurrence into a reusable,
> scope-bounded relation without the interface naming that relation and without
> merely copying episode tokens?

That question should be explored as developmental behavior, not converted into
another admission gate. This one contact cannot tell whether the limiting fact
was the occurrence, the one-shot authorship responsibility, the model's
interpretation, or their interaction. A successor must preserve those
possibilities rather than encode the desired phase profile in a schema or
scorer.

## Claim boundary and integrity

The record establishes interface observability, two valid acquisitions, two
parseable but refused interpretations, and the absence of an authorized content
comparison. It does not establish acquired competence, transfer, selectivity,
governance value, candidate-content influence, or a model defect that should be
screened away.

The evidence directory retains the frozen protocol, provider receipt, exact
world occurrences, complete requests and responses, parsed content, governance
receipts, per-cell actions, and null verdicts. A post-run audit recomputed the
request and response SHA-256 digests for all 69 call records with no mismatch.
All 69 calls had four retained artifacts. Serialized model requests contain no
world, case, relation, offer, expected-action, or verdict labels.
