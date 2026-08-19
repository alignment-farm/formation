# Exploratory developmental contact: observed record

The cold model already solved the visible revision rule without developmental
history. Adding the raw experience or the runtime-authored interpretation did
not improve that baseline. On the already-current probe, both offers instead
produced an unnecessary rebuild in both repetitions. This is an exploratory
observation about request-conditioned behavior, not evidence of formation or
negative transfer.

## Execution receipt

The contact ran on 2026-08-17 under the frozen
[brief](../../docs/EXPLORATORY_DEVELOPMENTAL_CONTACT.md) with
`ai/qwen3:14B-Q6_K`, artifact digest
`sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`,
and Docker Model Runner 1.2.6 using its llama.cpp backend.

All 27 planned logical calls completed in 27 physical attempts. Every response
was HTTP 200 and ended normally. Every actor response contained one permitted
action. No retry, repair, or stopping condition was used. The run consumed
4,252 prompt tokens and 437 completion tokens as reported by the provider.

The disposable interface call returned `rebuild_then_release`. The acquisition
at artifact revision 7 and authority revision 8 returned the same action. The
external environment rebuilt to revision 8 and accepted the release.

## What happened later

Each table entry shows the two actions from the two cold repetitions.

| Offer | Adjacent mismatch 41/42 | Reversed mismatch 8/7 | Already current 2/2 |
| --- | --- | --- | --- |
| No offer | rebuild, rebuild | rebuild, rebuild | release, release |
| Raw experience | release, rebuild | rebuild, release | rebuild, rebuild |
| Runtime interpretation | rebuild, rebuild | rebuild, rebuild | rebuild, rebuild |
| Frozen lesson | rebuild, rebuild | rebuild, rebuild | release, release |

On the two mismatch probes, the no-offer and frozen-lesson paths were accepted
in every repetition. The runtime-interpretation path produced the same actions.
The raw-experience path varied within both mismatch cells and produced one
rejected release in each.

On the already-current probe, no offer and the frozen lesson both selected the
least-work action, `release`. Raw experience and runtime interpretation both
selected `rebuild_then_release` twice. The environment accepted those actions,
but the rebuild was unnecessary under the task instruction.

The model-authored interpretation was:

> This experience suggests that when the artifact revision is one less than
> the authority revision, the system may respond by performing a rebuild
> followed by a release. However, this interpretation is uncertain, as it is
> based on a single instance and does not account for potential variations in
> other situations. Evidence that would count against this interpretation
> might include cases where the same revision difference leads to a different
> action, such as rejection or a simple release without rebuilding.

The later actor did not apply that literal scope selectively. It rebuilt for
the reversed mismatch and for equality as well as for the adjacent mismatch.
Behavior alone therefore does not show that the actor followed the retained
interpretation as a rule.

## What this contact located

The present task does not create an information gap. The field names, current
state, action names, and least-work instruction let this model infer the useful
rule on each later request. The no-offer path consequently left no positive
room for experience or interpretation to help. The successful acquisition
episode also made one action salient; copying that action is a simpler account
of the already-current behavior than acquired competence.

The next hard experimental problem is therefore **experience-dependent,
selective use under an information gap**: construct a small environment where
the relevant consequence teaches something that the later task foreground does
not itself reveal, while keeping the information and presentation of compared
offers close enough to distinguish interpretation use from ordinary prompt
content. That problem should be worked before prospective validation cases are
frozen.

Two repetitions per cell expose immediate disagreement but cannot estimate
behavioral rates. Every offer also changes request text, length, or structure.
The observed differences remain compatible with ordinary prompt-content and
sampling effects. This record establishes no hidden formed state, transfer,
selectivity, governance benefit, harmful result, or advantage over static
instruction.

## Evidence map and integrity check

- [Protocol](protocol.json) records the frozen schedule, prompts, offers,
  settings, budget, and claim boundary.
- [Provider receipt](provider.json) records the exact model inspection,
  installed inventory, runner status, endpoint, and version.
- [Acquisition experience](acquisition_experience.json) records the situation,
  action, and external consequence before interpretation.
- [Runtime interpretation](runtime_interpretation.json) records the exact
  interpreter request and output.
- [Summary](summary.json) contains descriptive cell outcomes and a null
  `formation_verdict`.
- [`calls/`](calls/) contains exact serialized request and response bytes,
  per-attempt metadata, and logical-call records for all 27 calls.

A post-run audit recomputed the SHA-256 digest of all 54 stored request and
response artifacts and found no mismatch. Actor settings had one exact shape
across all branches. Searches of serialized requests found no offer key, probe
identifier, expected action, or verdict label.
