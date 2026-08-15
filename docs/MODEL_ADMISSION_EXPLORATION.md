# Small-model admission exploration

Status: **first packet closed with partial evidence; Nemotron unresolved**.

## Purpose

Find a small local model that is strong enough to follow a controlled coding
task, weak enough to leave measurable room for improvement, and able to use a
directly stated rule that closes that gap.

This is model-and-task selection. It does not test Formation. Its contacted
prompts and outputs are development data and cannot later become validation
cases.

## Why this exploration is useful even if no model is admitted

Two Composer 2.5 contacts stopped because the cold model already handled the
target boundaries. Repeating that search with increasingly obscure mistakes
would measure our ability to stump a strong model, not the model's ability to
develop through governed experience.

This exploration instead looks for a measurable developmental margin:

```text
easy contract anchors: reliable
cold target behavior: incomplete
same kind of work with the rule stated directly: reliable
```

A model below this band cannot yet use the competence. A model above it does
not need to acquire the competence on the selected task.

## Initial models

Use these two already-installed LM Studio models, in this order:

1. `mistralai/ministral-3-3b`
2. `nvidia/nemotron-3-nano-4b`

Ministral 3 3B is the smallest dense member of Mistral's Ministral 3 family.
The installed Nemotron is NVIDIA's 4B dense-hybrid variant. Record the exact LM
Studio model identifier, quantization, file digest, runtime version, load
settings, context length, sampling settings, and hardware for every call.

Do not download or substitute another model inside the initial packet. A later
amendment may add the next smallest local candidate only after both initial
models receive a terminal admission result.

## Coldness and inference settings

Every call starts without a prior chat or retained model state. The runner sends
one complete prompt to the local LM Studio server and does not reuse a provider
conversation. Model weights and inference settings stay fixed within a model's
packet.

The normative appendix's request fields are the complete sampling contract.
Send every listed field and no unlisted sampling field. If the server rejects a
listed field or requires another sampling choice, refuse contact and amend the
pre-contact packet rather than falling back to a default.

No Formation record, raw transcript, model-authored lesson, validation answer,
or output from another model enters these calls.

## Probe families

The first packet uses two real, executable coding boundaries already understood
from the closed Composer contacts. Reuse is permitted only because this is
exploratory model admission. None of these prompts or close variants may later
score a promoted Formation comparison.

### Python exact integer type

The cold prompt uses ordinary “Python integers” language without explaining
that `bool` is a subclass of `int`. The direct-rule prompt uses a different
parser and states that values must have exact type `int` and that booleans must
refuse.

The existing restricted Python source gate and process-isolated executable
oracle apply. Ordinary container, shape, type, bound, mutation, and return
checks remain present. The held distinction is whether boolean values refuse in
integer positions.

A Python call is a qualified boundary miss only when its source passes the
gate, every ordinary vector passes, and at least one held boolean vector returns
normally instead of raising `ValueError`. A refusal, timeout, crash, or ordinary
failure is not useful headroom.

### SQLite nullable anti-join

The cold prompt asks for rows absent from a related table whose join column
contains `NULL`, without naming the SQL pitfall. The direct-rule prompt uses a
different schema and states that the query must remain correct when the
subquery contains `NULL`, either by using `NOT EXISTS` or by excluding `NULL`
inside a `NOT IN` subquery.

The existing single-`SELECT` restriction applies. The appendix must freeze at
least two unseen null-free databases and two unseen nullable databases under the
prompt's exact schema. Names, identifiers, row counts, and matching rows vary so
a literal answer cannot pass. The same returned query runs unchanged against
every database.

The null-free databases are the ordinary checks. A qualified boundary miss must
parse and execute, return the correct rows on every null-free database, and
return wrong rows on at least one nullable database. A parse error, execution
error, or wrong null-free result is ordinary failure, not useful headroom.

These are practical language and database behaviors, not claims about general
coding ability. They are two chances to locate a usable band without inventing
a synthetic world or shopping through unlimited puzzles.

For each family, cold and direct-rule prompts must use different function or
table names, different question text, and disjoint executable inputs. A
direct-rule prompt may state the general competence, but it may not contain the
cold schema, cold inputs, expected rows, test names, solution code, or a repair
of any observed cold output. All prompts and vectors freeze before contact.

## Contract anchors

Before target scoring, each model receives four easy, unambiguous tasks:

1. one Python function with an exact input shape and no ambiguous scalar type;
2. one Python function that must raise `ValueError` on a named invalid value;
3. one SQLite selection with no join or `NULL`; and
4. one SQLite aggregation with an exact expected ordering.

The source and SQL gates used by the target probes also govern the anchors.
All four anchors must parse, execute, and pass. Failure closes that model as
`contract_unreliable`; target failures from that model cannot establish useful
headroom.

The complete anchor prompts and executable vectors must be frozen in a
normative appendix before the first call.

## Schedule

For each model:

1. run the four contract anchors once each;
2. if all pass, follow the appendix's model-specific family order; and
3. within each family, run three cold calls followed by three direct-rule calls.

Each condition repeats one exact frozen prompt three times; repetitions measure
stability, not breadth. The maximum is sixteen logical calls per model and
thirty-two total. A logical call may retry once only when the server returns no
model output. Retain both attempts and their linkage. Stop a model after an
anchor failure, but still test the other initial model.

Probe-family order is Python then SQLite for the first model and SQLite then
Python for the second. Within each family, all cold calls precede direct-rule
calls, and every direct-rule call runs even when the cold calls already pass.
This is not a treatment comparison. With only two models, the reversal cannot
separate model identity from order; it can expose only gross server-state or
scheduling mistakes.

## Mechanical admission

Score each probe with its external executable oracle. Every call receives
exactly one label:

- `gate_fail` — output does not pass the source or query gate, or evaluation
  cannot produce a complete report;
- `ordinary_fail` — output executes but fails at least one ordinary vector or
  null-free database, or fails a held check in any way other than the
  predeclared boundary miss;
- `boundary_miss` — every ordinary check passes and at least one held boolean
  or nullable check fails in the predeclared way; or
- `full_pass` — every ordinary and boundary check passes.

For Python, only a normal return on a held boolean input qualifies as
`boundary_miss`. For SQLite, only correct results on every null-free database
followed by a wrong result on a nullable database qualifies.

Classify each family mechanically in this order:

- `ordinary_fragile` — any cold or direct-rule call is `gate_fail` or
  `ordinary_fail`;
- `in_band` — all three cold calls are `boundary_miss` or `full_pass`, at least
  two are `boundary_miss`, all three direct-rule calls are `boundary_miss` or
  `full_pass`, and at least two are `full_pass`;
- `cold_ceiling` — all three cold calls are `boundary_miss` or `full_pass` and
  at least two are `full_pass`;
- `not_teachable` — the cold calls meet the qualified-gap side of `in_band`, all
  direct-rule calls are `boundary_miss` or `full_pass`, and fewer than two
  direct-rule calls are `full_pass`.

A model occupies the developmental band for one family only when that family
is `in_band`. This requires:

- all four contract anchors pass;
- at least two of three cold calls fail the named boundary while passing every
  ordinary check;
- at least two of three direct-rule calls pass every ordinary and boundary
  check; and
- no accepted output depends on prose repair or human reinterpretation.

The first two models are both completed if their anchors pass. Report every
model-family cell. If both occupy a band, prefer the smaller model for the first
Formation exploration unless its output cost or latency is materially worse.
This preference selects a research instrument; it is not evidence that smaller
models benefit more from Formation.

## Terminal results

If any anchor fails, stop that model, do not score either family cell, and set
its terminal result to exactly `contract_unreliable`. Otherwise, after family
classification, each model receives one result in this order:

- `admitted:<family-list>` — at least one family is `in_band`; the exact value
  is `admitted:Python`, `admitted:SQLite`, or `admitted:Python,SQLite`, with no
  spaces and Python first;
- `cold_ceiling` — both families are `cold_ceiling`;
- `not_teachable_here` — at least one family is `not_teachable` and both family
  cells are either `not_teachable` or `cold_ceiling`;
- `mixed_unstable` — every remaining pattern.

If one family admits and another does not, retain both cell results and name
only the admitted family in the terminal result. `not_teachable_here` is about
these prompts and tasks, not an intrinsic limit of the model.

## Records

Retain exact prompt and output bytes, hashes, model and runtime identity,
sampling configuration, timestamps, duration, token counts where available,
retry linkage, parser or source refusal, executable result for every vector,
and the mechanically computed terminal result.

Store the packet under an `exploratory_only` evidence directory. Preserve all
failed and inconvenient outputs. Do not place its summary among Formation
findings.

## Promotion boundary

Admission licenses a separate Formation exploration charter, not validation.
That successor must use fresh tasks that were not contacted or used to tune
this packet. It may not paraphrase an admission prompt or reuse its executable
inputs. The successor must list the admission prompt, fixture, and scorer hashes
as blocked development material. It must compare the admitted model under at
least:

- cold static instructions;
- raw occurrence persistence;
- a model-authored lesson; and
- the proposed governed formation path.

It must also include related cases where influence should transfer, cases where
it should remain silent, an external consequence oracle, and explicit costs.
Only a later reviewed protocol with fresh prospective cases may support a
Formation claim.

## Stopping and loses-conditions

Stop after both initial model results or the thirty-two-call ceiling. Do not add
tasks, rewrite a failed output, relax an anchor, change inference settings, or
download a replacement model after the first call.

The exploration loses its value if it admits a model merely because it fails;
if direct-rule success is not executable; if the harness repairs code or SQL;
if model outputs leak between calls; if a model is changed between cold and
direct-rule conditions; if inspected development cases later score a promoted
claim; or if an admission result is reported as evidence that Formation works.

## Contact gate

No model call is licensed until a normative appendix freezes every anchor and
probe prompt, input vector, expected result, order, inference setting, receipt,
retry rule, and mechanical classifier; a runner proves automatic stopping and
spends no model budget in tests; and independent cold review confirms that
explicit-rule prompts teach a rule without disclosing answers to the cold
calls.
