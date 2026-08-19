# Executable prediction revision mechanism

Status: **independently review-stable mechanism proposal; one separate strict-
budget charter decision is licensed, but no operational model, exact prompt,
concrete case packet, numeric budget, implementation, runner, participant-model
call, influence test, validation packet, or Formation claim is licensed**.

## Purpose and claim ceiling

This proposal specifies the authorship route selected in the
[post-challenge route selection](POST_CHALLENGE_ROUTE_SELECTION.md). One cold
model call authors a prediction rule. A frozen evaluator measures the rule's
prediction on cases fixed before contact. An independent environment oracle
supplies the actual result. A later cold call receives the exact parent output
and the new occurrence and authors one successor attempt.

The mechanism asks:

> After a parent prediction encounters an independent external result, what
> functional differences appear in the first successor output, and which no-
> result, no-parent, repeated-successor, same-response, static, repeated-source,
> restatement, and visible-material conditions reproduce them?

The strongest result available here is a set of authorship observations over a
frozen case menu. The mechanism defines no causal revision label. It does not
activate a rule, choose a practitioner action, or test later influence.
Evaluator output is not practitioner behavior. A useful successor is not a
Formation effect.

## Authorities and information flow

The human protocol owner freezes the rule language, evaluator version, case-
manifest requirements, comparison conditions, call order, budget, and stopping
rule before a later contact.

The harness owns case construction, hidden role labels, assignments, forks,
call scheduling, evidence capture, and aggregate comparison. It freezes every
case and assignment before the first participant-model output. It may not add,
remove, choose, or reorder cases because of a returned rule.

The cold model owns every raw parent and successor output. It does not know
hidden case roles, expected results, branch labels, or scorer projections.

The formation runtime owns append-only model-invocation lineage, exact raw-
output retention, public mechanism configuration, and delivery of the exact
parent output and permitted occurrence. It does not translate or select model
content.

The **rule evaluator** is a deterministic measurement instrument. It receives
only one rule and one public input map. It returns `out_of_scope`, a prediction,
or `evaluation_unavailable`. It cannot see oracle results, hidden roles, branch
labels, another branch, or a practitioner action interface.

The environment oracle receives one public input map and returns one atomic
result under a rule fixed before contact. It cannot see the authored rule or
prediction. The result remains sealed until the parent evaluation is retained.

The scorer reads retained outputs, evaluator receipts, oracle receipts,
assignments, and hidden roles after authorship. It computes only frozen
descriptive projections and condition-level counts. Its output never enters
runtime lineage or a model request.

The evaluator and oracle may share a software process. Their logical inputs,
outputs, and authority remain separate.

## A total rule language over raw output

Every UTF-8-encodable Unicode-scalar provider content string is a valid rule.
There is no malformed-string class and no JSON wrapper requirement.

By default, the complete raw string means:

```text
scope:      all public inputs
prediction: the complete raw string
```

Bare opaque tokens, prose, fenced code, partial JSON, empty strings, field
names, and visible-material controls are therefore executable constant rules.
The runtime does not wrap or repair them. Their global scope and constant
prediction are the declared meaning of the raw form.

A model opts into conditional structure only when its complete content is:

```text
RULE_AST_V1\n<one exact JSON object>
```

The object has exactly two keys. Their serialized order is not significant:

```json
{"when":<boolean-expression>,"predict":<string-expression>}
```

A string expression is exactly one of:

```text
{"lit": <string>}
{"field": <string>}
{"if": [<boolean-expression>, <string-expression>, <string-expression>]}
```

A Boolean expression is exactly one of:

```text
{"bool": <true-or-false>}
{"exists": <field-name-string>}
{"eq": [<string-expression>, <string-expression>]}
{"neq": [<string-expression>, <string-expression>]}
{"and": [<boolean-expression>, <boolean-expression>]}
{"or": [<boolean-expression>, <boolean-expression>]}
{"not": <boolean-expression>}
```

Every expression object has exactly one key. Array lengths and value types are
fixed by the forms above. The JSON object rejects duplicate keys, non-scalar
Unicode, and extra keys. Ordinary JSON string escapes and either order of
`when` and `predict` are accepted. Any amount of ordinary JSON whitespace may
surround the object after the exact marker. No trailing non-whitespace content
is accepted.

If content begins with `RULE_AST_V1\n` but the remaining bytes do not form that
exact tree, the complete raw content keeps its default global-constant meaning.
It is not invalid and is not partially decoded. A code-fenced tree likewise
remains one literal constant.

The grammar accepts every finite tree that fits inside the later charter's
symmetric provider-output ceiling. There is no separate semantic depth or node
cap that admits short copied constants while screening longer wrong rules. The
recognizer and evaluator must be total for every response within that frozen
ceiling; an implementation that can fail from nesting depth does not conform.

The language has no action operator, environment call, table lookup, arithmetic
primitive, string concatenation, hidden-state read, random choice, recursion,
or side effect. It can express constants, field projections, comparisons,
authored scope, and finite conditionals. Its operators do not name a target
relation or expected prediction.

This valid copied rule remains executable without translation:

```text
opaque-token
```

Its meaning is a global constant prediction of `opaque-token`. A later contact
may explain the grammar, but it may not provide a filled conditional example
whose fields and values mirror the target cases.

## Recognizer and evaluator semantics

The recognizer receives the complete content string. It returns exactly one of:

- `literal_rule`, containing that exact string; or
- `ast_rule`, containing the exact raw string and parsed tree.

Only absent content, non-string content, or content that cannot be represented
as Unicode scalar text produces `rule_unavailable`. The raw provider response
is still retained, and the external event and successor call still occur.

The recognizer does not search prose for a tree, strip code fences, complete
braces, coerce values, rename keys, choose among objects, or read reasoning
fields. Failed AST recognition returns the raw literal rule; it never returns a
repaired tree.

The evaluator is the pure function:

```text
evaluate(rule, public_input) -> out_of_scope | prediction | evaluation_unavailable
```

`public_input` is a finite map from strings to strings. A literal rule is always
in scope and returns its exact raw string.

For an AST rule, `when` evaluates first. `false` returns `out_of_scope` and
does not evaluate `predict`. A `lit` returns its string. A `field` returns the
mapped string or a private tagged `missing` value. `exists` is true exactly when
the named field is present.

Boolean evaluation has three internal values: true, false, and unknown. `eq`
and `neq` return unknown if either operand is missing; otherwise they compare
strings exactly. `not unknown` is unknown. For `and`, false with any other
value is false, true with unknown is unknown, and unknown with unknown is
unknown. For `or`, true with any other value is true, false with unknown is
unknown, and unknown with unknown is unknown. The operators are symmetric in
their operands. An unknown `when` or `if` condition yields
`evaluation_unavailable`; it never becomes a positive scope match. `if`
otherwise evaluates only the selected branch. A top-level prediction that
yields the missing tag also returns `evaluation_unavailable`.

The missing tag cannot be authored as a string. Exact string equality uses no
trimming, case folding, token mapping, or semantic equivalence. The evaluator
produces no correctness judgment and has no action output.

The same recognizer and evaluator version applies to every model-authored,
protocol-authored, and control rule. Recognizer class and evaluator determinism
are instrument facts, not reasoning findings.

For a model-authored rule, the runtime uses one deterministic projection into
the existing candidate semantics:

- retained representation: the exact raw output and recognized rule;
- claimed applicability: global for a literal rule, or the authored `when`
  expression for an AST rule;
- expected effect: the authored prediction expression; and
- stated counterevidence: an independently observed atomic result on an in-
  scope input that differs from the committed prediction.

The scope and prediction come from the retained representation. The runtime
does not infer them from hidden case roles or semantic prose.

## Frozen case manifest and leakage checks

Before contact, the harness freezes one finite manifest. Every case contains:

- an opaque case coordinate;
- an exact public input map;
- one atomic oracle-result string from a frozen public prediction vocabulary;
- one hidden role;
- one predeclared condition assignment; and
- a model-visible presentation order chosen independently of live output.

The manifest must contain positive counts for these hidden roles:

- `primary_test` — the first result revealed after the parent attempt;
- `transfer` — new inputs where the same target relation applies;
- `non_transfer` — matched inputs where the target relation does not apply;
- `copy_control` — inputs on which frozen opaque literals cannot supply the
  answer; and
- `later_revision_test` — a later opportunity that may count against an
  overbroad or outdated successor.

The prediction vocabulary is visible before authorship so a rule can make a
prediction. An oracle result contains exactly one vocabulary member. It cannot
contain an explanation, case coordinate, delimiter, multiple answers, hidden
role, field name, or relation statement.

Every public input uses the same frozen key set. No key or value may equal a
prediction-vocabulary member, hidden role, case coordinate, or oracle field
name. Public input can therefore describe a situation but cannot contain the
atomic answer as a field value or use key presence as a hidden role signal.

The case packet must also supply a non-identification witness over one fixed
hypothesis family. Let `H` be every rule expressible in this mechanism's AST
language whose evaluation produces an in-vocabulary prediction on every case
in the frozen manifest. After the first consequential occurrence and after
every prefix of revealed primary or later-revision results, each still-held-out
transfer, non-transfer, and copy-control case must have two members of `H` that:

- agree with every result visible to the model at that prefix; and
- predict different results on that held-out case.

The witness functions and their evaluations remain harness-only. Passing this
check means only that at least one alternative answer remains expressible for
each held-out case after every revealed prefix. It does not show that the
alternatives are equally simple or likely, or that a public field is not a
suggestive hint. Field and case design remain separate leakage obligations.

The later charter must construct the witness without participant outputs. If it
cannot, the mechanism closes before contact.

Role names, expected results, structural annotations, admissible-function
witnesses, and held-out answers remain harness-only. The runtime receives only
a scheduled public input and the declared external result when its condition
permits.

The primary public input must differ from every public input in the first
consequential occurrence, and its environment result must be a new event rather
than a replay of an earlier result receipt. Primary and later-revision cases are
preassigned opportunities for falsification, not guaranteed contradictions to
arbitrary live rules. A confirmation, out-of-scope rule, or unavailable
prediction is a valid terminal observation. No live rule may cause the harness
to select another case.

## Parent attempt and version identity

The parent call receives the exact first consequential occurrence, the public
rule-language responsibility, and no primary-test input or result. A later
charter owns exact prompt bytes and the operational model.

The first provider content at the predeclared parent invocation coordinate is
the parent output. It is never replaced. Its `model invoked` developmental
receipt retains the exact request, raw response, content value, model
configuration, public mechanism configuration, and source occurrence.

Every recognized model-authored content string must append `candidate proposed`
for rule version 1. Its identity is the unique proposal coordinate bound to the
exact model invocation, raw content, recognized rule, recognizer version, and
source occurrence. Equivalent syntax or identical functions from another call
do not share identity. There is no policy choice that can keep a copied,
constant, prose, or awkward recognized rule out of the prediction trial.

Absent, non-string, or unrepresentable content produces no rule version. The
model-invocation receipt remains the parent-attempt identity and still becomes
a causal parent of the successor request.

## Prediction trial and external occurrence

The primary case and assignment exist before the parent call. After the parent
output is retained:

1. If rule version 1 exists, the runtime opens a declared candidate trial using
   only the public rule, public input, evaluator version, and no oracle result.
2. The evaluator appends `candidate trial observed` with `out_of_scope`,
   `evaluation_unavailable`, or the exact prediction.
3. If no rule exists, no trial is invented and the prediction status is
   `rule_unavailable`.
4. The environment oracle independently appends `consequence observed` with
   the public input and one atomic actual result.

The candidate-trial receipt and consequence receipt remain distinct causal
parents of the successor request. Neither receipt states equality, correctness,
support, contradiction, a hidden family, expected rule, score, or
recommendation. The cold successor receives both exact facts and must compare
them itself.

A protocol-authored control rule may follow the same trial surface only through
an explicit `candidate proposed` receipt whose author is the frozen
deterministic protocol constructor rather than the cold model. The constructor
is a declared baseline interpreter authority, not the trajectory harness acting
as treatment author. Its receipt is confined to the named control condition and
cannot count toward model-authorship observations.

The rule cannot choose an action that produces the result. Evaluator and oracle
are independent measurements of the same preassigned public input.

## First successor attempt

The selected successor call receives:

- the public rule-language responsibility;
- the exact raw parent content, including empty, prose, copied, or partial-JSON
  content;
- the parent-attempt coordinate;
- the exact primary public input;
- the exact candidate-trial observation when one exists, or the declared
  `no_prediction_available` marker; and
- the environment-issued atomic result.

It receives no recognizer class, hidden role, expected rule, held-out answer,
equality bit, aggregate score, governor decision, or peer-review language.

The first provider content at the successor coordinate is retained without
quality-dependent retry. Recognized string content becomes rule version 2 with
the exact parent attempt, trial receipt when present, consequence receipt,
mechanism configuration, and successor invocation as causal parents. It never
edits version 1. Unavailable content remains a successor attempt without a rule
version.

The successor call occurs even when the parent or prediction was unavailable.
That trajectory can report the later raw output but cannot report response to a
contradicted parent prediction.

## Later revision cycle

The mechanism supports one further cycle. The preassigned
`later_revision_test` input is evaluated against the exact first successor when
available. The independent atomic result is revealed afterward. A next cold
call receives the exact raw successor, separate trial and consequence receipts,
and authors one first next-successor attempt.

If the successor rule or prediction is unavailable, the preassigned external
event and next-successor call still occur. The result is not described as
counterevidence to an unavailable prediction. All raw-retention, information,
recognizer, evaluator, and no-replacement rules remain unchanged.

Any causal language about the later cycle requires its own result-withheld,
parent-withheld, repeated-successor, and same-response controls. Without those
mirrored conditions, the report stops at exact per-condition observations.

The assigned opportunity may confirm the successor. Confirmation is a complete
terminal outcome, not permission to choose another case.

## Mandatory comparison conditions

A later charter must assign a positive number of trajectory units to every
model-contact condition below before any live output. The static-rule evaluator
ceiling is a non-contacted reference evaluation and does not receive trajectory
units or consume model budget. The charter may choose identifiers, post-parent
order, and symmetric budgets. It may not remove a condition while retaining the
causal language that condition qualifies.

### Parent plus external result

The selected condition follows the full parent, trial, sealed-result,
consequence, and successor order above.

### Parent with result withheld

The later call receives the exact raw parent, the same primary public input,
and the same trial receipt, including the prediction value when one exists. It
receives a declared `result_not_revealed` marker instead of the oracle result.
This missing-result value is a disclosed interface difference. Apart from that
one result field, the later charter must keep the semantic request and settings
identical to the selected successor request.

### Result with parent withheld

The later call receives the initial experience and a primary external
consequence containing the public input and atomic result, but no parent output
or trial receipt. It authors one first rule under the same rule-language
responsibility. This measures raw new experience without parent revision.

### Independent repeated parent

The byte-identical parent request runs again at a predeclared coordinate. The
first repeated output is retained. It measures parent sampling without choosing
a preferred source.

### Independent repeated successor

The byte-identical selected successor request runs again at a predeclared
coordinate. Its first output remains a separate candidate identity. It measures
successor sampling after the exact same external history.

### Same-response sequence

One cold call receives the initial experience, primary public input, and atomic
result together and returns one parent attempt followed by one successor
attempt in a frozen ordered envelope. Both raw values are retained and
recognized separately.

The result was visible before either output committed, and the two-slot envelope
differs from the one-rule interface. This is a disclosed non-parity collapse
test only. If its successor function matches the selected condition, separate
lineage is not needed for that observed function. A mismatch cannot show that
separate lineage mattered.

### Repeated occurrence

A cold authorship call receives the exact first occurrence again without a
parent output, trial receipt, or new environment event and returns one rule.
This tests source repetition.

### Deterministic result restatement

A model-free renderer presents the primary public input and atomic result to a
cold authorship call without the parent output or model-authored lineage. The
call returns one rule under the same rule-language responsibility. The renderer
preserves public facts but performs no relation inference.

### Visible-material control

A source-blind constructor supplies one raw literal parent derived only from a
public seed and a size target frozen without live semantic content. Because
every raw string is a literal rule, the control remains executable without a
wrapper. The constructor must reject and deterministically advance past any
value beginning with `RULE_AST_V1\n`, so the selected control is unambiguously a
literal rule. The control literal and primary case are frozen together before
contact so the literal's prediction differs from the primary oracle result and
is wrong on at least one `copy_control` case.

The control then follows the full primary trial, independent consequence, and
cold successor lifecycle. Its successor sees an arbitrary visible parent, that
parent's prediction, and an actual contradicting result through the same fields
as the selected condition. The control parent is protocol-authored and never
creates a model-authored `candidate proposed` receipt. Instead, the frozen
constructor authors one control-only proposal version under the explicit rule
in the trial section. Its source, authorship, and condition remain visible in
lineage.

Exact byte or token mass, if claimed, requires a frozen tokenizer instrument in
the later charter. Instrument parity is not authorship progress.

### Static-instruction authorship

A cold call receives one frozen explicit lesson that states the target relation
without developmental lineage and authors one rule under the same rule-language
responsibility. This is the static-instruction ceiling for rule authorship. The
lesson is fixed before contact and never enters the selected condition.

### Static-rule evaluator ceiling

The protocol owner freezes one explicit rule before contact and evaluates it on
the same case manifest. It establishes what the language and evaluator can
express. It never enters a treatment model request and is never model-authored.

### Later-cycle controls

If a later charter uses causal language about the next successor, it repeats
the result-withheld, parent-withheld, repeated-successor, and same-response
conditions with version 2 and the preassigned later-revision opportunity. A
charter that omits them may report only the exact later outputs and functions.

## Frozen functional projections

For every rule `r` and ordered case set `S`, define:

```text
vector(r, S) = [evaluate(r, case.public_input) for case in S]
truth(S)     = [case.oracle_result for case in S]
```

`out_of_scope` and `evaluation_unavailable` remain explicit vector values and
never equal an oracle-result string.

For each parent-successor pair and condition, the scorer reports these atomic
facts separately:

- whether the parent made an in-scope prediction on the primary input;
- whether that prediction differed from the primary result;
- whether the successor content produced a rule;
- whether parent and successor raw bytes, recognized forms, or complete
  functional vectors were equal;
- which primary, transfer, non-transfer, copy-control, and later-revision
  predictions changed;
- which predictions changed from incorrect or unavailable to correct;
- which predictions changed from correct to incorrect or out of scope;
- which in-scope claims became out of scope, and which out-of-scope inputs
  became claimed; and
- correctness counts for parent and successor on each hidden role.

The mechanism defines no compound “selective,” “revision,” “improvement,” or
“success” predicate. A later exploratory charter may freeze only the atomic
counts, availability partitions, condition-by-condition differences, and exact
function comparisons defined here. It may not combine them into a pass
threshold, success label, causal revision label, or favorable terminal verdict.
A later validation design would have to earn any such predicate separately.

The later-cycle report uses the same atomic projections with version 2 as the
parent. It may say that an available prediction differed from the later result
and that the next function changed. It may not call the change revision without
the mirrored controls.

## Fixed denominator and comparison report

A later charter assigns a positive finite number of trajectory units to every
model-contact condition before any live output. For each such condition and
atomic fact, the report is:

```text
fact count / all assigned trajectory units
```

Unavailable content, literal prose, copied constants, out-of-scope rules,
unavailable evaluations, and wrong predictions remain in the denominator.
Transport attempts are reported separately and cannot remove a trajectory from
its assigned denominator.

The report gives the full mutually exclusive partition at each authored
position: unavailable provider content, literal rule, or AST rule. Evaluation
partitions are out of scope, unavailable, or exact prediction.

One selected-condition difference not reproduced by one control draw is not
causal evidence. A null or mixed packet closes the chartered contact; it does
not open resampling, prompt repair, language extension, case replacement, or
model search.

## Lineage and evidence

Every authorship call appends one `model invoked` developmental receipt. Every
recognized model-authored rule must append one `candidate proposed` version
whose author is the cold model. Protocol-authored visible-material and static
rules never receive model authorship.

The candidate trial preserves the prediction and its declared model or protocol
author separately from the environment consequence. Only the primary and
later-revision public inputs, trial receipts, oracle authority, and atomic
observed results enter runtime lineage. Hidden roles, alternate functions,
expected rules, branch labels, held-out vectors, and scorer facts remain
trajectory-only.

Held-out transfer, non-transfer, copy-control, and static evaluations are
trajectory evidence, not developmental occurrences. They never enter a model
request or practitioner replay.

Mechanism configuration is a causal parent of every recognition, evaluation,
authorship, trial, and occurrence receipt. Parent and successor coordinates
establish version lineage; content equality alone never does.

## Loses-conditions

The mechanism fails before a charter if:

- any provider content string is excluded from literal-rule semantics because
  it is prose, copied, malformed, fenced, empty, long, or awkward;
- the AST grammar, output explanation, field contract, case menu, evaluator, or
  oracle states the target relation or expected prediction;
- public inputs do not share one key set, or any public key or value can carry a
  prediction-vocabulary member, hidden role, case coordinate, or oracle field;
- an atomic result or revealed-result sequence identifies any held-out answer
  under the frozen DSL-expressible hypothesis witness;
- the primary public input repeats one from the first consequential occurrence,
  or its result reuses an earlier result receipt instead of creating a new
  external event;
- any case, role, result, assignment, order rule, static material, or visible-
  material control is chosen after a live output;
- the parent rule can choose an environment action or affect the oracle result;
- evaluator output can enter a practitioner action interface or count as
  practitioner behavior;
- candidate-trial output and environment consequence are merged into one
  authority or occurrence receipt;
- a trial or consequence states correctness, support, contradiction, hidden
  role, or scorer judgment to the successor;
- unavailable parent content or prediction prevents the external event or
  successor attempt in either revision cycle;
- any raw output is repaired, translated, semantically selected, or replaced;
- only successful, structured, or convenient trajectories remain in the
  denominator;
- parent, successor, and parity comparators use different rule languages,
  recognizers, evaluators, settings, or quality-dependent budgets;
- mandatory selected, result-withheld, parent-withheld, parent-sampling,
  successor-sampling, same-response, repeated-occurrence, restatement,
  visible-material, static-instruction, transfer, non-transfer, or later-cycle
  comparisons are absent while stronger language is kept;
- same-response mismatch is used as evidence for separate retained lineage;
- changed text, AST recognition, evaluator determinism, a correct function, or
  one atomic fact is counted as causal revision, later influence, or Formation;
- a charter combines atomic facts into a pass threshold, success predicate,
  causal revision label, or favorable terminal verdict;
- a result is described as counterevidence without an in-scope committed
  prediction that differs from it;
- any contacted condition receives zero assigned trajectory units;
- replication lacks a frozen event, assignment, aggregation rule, and full
  denominator; or
- a null automatically licenses another sample, prompt, language, case, model,
  or contact.

## Work licensed by this proposal

Independent review found the mechanism coherent. It licenses only a separate
strict-budget charter decision. That charter would have to choose the
operational model, exact prompts and envelopes, fresh case manifest, exhibited
`H` witness pairs, oracle, static lesson and rule, visible-material constructor,
positive assignment counts, inference settings, order, physical-attempt
ceiling, transport policy, frozen report, and stopping rule.

This proposal does not license the charter itself, implementation, tests, a
runner, participant-model contact, influence comparison, validation, or a
Formation claim.

## Review question

Independent reviewers must try to show that the mechanism turns the evaluator
into the practitioner, bakes the relation into grammar or public fields,
screens copied strings, selects favorable cases or trajectories, leaks held-out
answers through atomic results, merges interpretation with consequence,
mistakes ordinary in-context learning for revision, or permits causal language
from one functional difference.

They must also check whether every raw string remains executable, authored
scope is real, missing fields cannot create false equality, malformed parents
continue, each first output stays in the denominator, version identity follows
causal lineage, and later revision stops at observation without mirrored
controls.

The two stable reviews license only the separate charter decision described
above.

## Review record

Composer 2.5 and Grok 4.6 independently rejected the first draft. They found
that its exact JSON wrapper still screened the copied-token behavior from the
completed contact, its depth limit treated long wrong rules differently from
short constants, scope came from the protocol rather than the model, oracle
results could leak held-out answers, evaluator output was mixed into an
environment occurrence, and a compound success-shaped predicate hid missing
control contrasts.

The second draft gave every raw string global-constant semantics, added
authored scope, separated candidate trials from consequences, required atomic
results, added successor sampling and static-instruction controls, mirrored
later-cycle controls, and removed the compound predicate. Both reviewers still
returned `REVISE_MECHANISM`. They found an optional proposal receipt that could
screen valid literals at the record layer, a visible-material trial with no
declared proposal author, missing-field negation that could create positive
scope, an acquisition-replay loophole for the primary case, an undefined
hypothesis family behind the leakage witness, and a path for a later charter to
repackage atomic facts as success.

The current revision makes proposal creation mandatory for every recognized
model output, gives the visible-material control an explicit deterministic
protocol author, uses three-valued missing-field logic, requires a new primary
input and result event, fixes the leakage witness to DSL-expressible functions,
accepts ordinary JSON key order and trailing whitespace, and forbids compound
or favorable charter verdicts.

Composer 2.5 and Grok 4.6 independently returned `MECHANISM_STABLE` on that
text. They agreed that exact prompts, markers, concrete maps, exhibited witness
pairs, the operational model, positive assignment counts, inference settings,
and the physical output and attempt ceilings belong to the separate charter.

Final read-only Cursor verdicts:

- `composer-2.5`: `MECHANISM_STABLE`
- `cursor-grok-4.6-high-fast`: `MECHANISM_STABLE`
