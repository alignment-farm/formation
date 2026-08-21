# Governed diagnostic encounter policy

Status: **deterministic mechanism specification; no participant contact or
effect claimed**.

## Question

Can an acquired record govern whether a costly diagnostic encounter is opened
without letting the harness choose an action or telling the cold model what to
do?

The recent participant experiments answered a different question. They asked
the cold model to decide whether to probe. A full catalog made it probe even
when none of the public signals was covered. A compact `complete` or `none`
fact made it guess a task control instead. More wording would test the prompt,
not the proposed developmental system.

This mechanism moves one decision into declared runtime governance. It does
not claim that the model learned to value information.

## Division of authority

The public device names its diagnostic control, its complete signal alphabet,
and the external service-window cost. Admitted signal records name an exact
signal and an observed task slot. Those are the only inputs to the policy.

The runtime governor decides whether the diagnostic encounter may open. It
does not know the hidden device profile, the signal that will be emitted, the
valid task control, a branch label, or a scorer answer. The harness schedules
the cases and retains hidden comparisons. The environment alone emits the
signal and consumes the service window. If a diagnostic is opened, the cold
model later chooses the task control from the observed signal and one exactly
matching record.

Withholding is not a model-authored `hold` and is not a task action. The
runtime simply does not open an encounter that would spend the service window.
No model is invoked, no diagnostic is applied, and no task outcome is
manufactured.

## Frozen policy

Policy `exact-public-alphabet-coverage-v1` applies one rule:

1. Compare every signal in the public diagnostic alphabet with the signal
   field of the admitted records.
2. Authorize the diagnostic only when each public signal has exactly one
   matching admitted record.
3. Withhold when any public signal has no match.
4. Refuse ambiguous coverage, duplicate lineage identifiers, malformed
   records, a stale authorization, or a non-initial device state.

The rule does not inspect the record's task-slot claim when it authorizes the
diagnostic. Correct and reversed records therefore have the same coverage and
must receive the same decision. This is the central collapse test: if reversal
changes authorization, correctness or hidden task knowledge has leaked into
the governor.

An authorization binds the exact public state and the complete considered
record set by hash. It cannot be reused after either input changes. After the
environment returns a signal, exact matching may select one of the records
that the authorization considered. Request construction for a later contact
must consume that selected record rather than reopen mutable storage.

## Deterministic comparisons

The zero-call specimen crosses these cases before any participant work:

| Records and alphabet | Required decision | What it checks |
| --- | --- | --- |
| Learned records, covered alphabet | Authorize | Acquired lineage can govern acquisition. |
| Content-equivalent supplied records, covered alphabet | Authorize | Provenance alone does not change the rule. |
| Reversed records, covered alphabet | Authorize | Coverage, not correctness, governs opening. |
| Removal, covered alphabet | Withhold | The decision depends on retained records. |
| Learned records, uncovered alphabet | Withhold | Familiar records do not cover new signals. |
| Duplicate matches | Refuse | Ambiguity fails closed. |

For each authorized path, both hidden profiles are applied only after the
decision. The environment must consume the costly service window and emit the
profile signal. Exact matching must then select one record. Correct learned
and supplied records should lead to task completion under the deterministic
record interpreter; reversed records should lead to failure. Those later
outcomes show that the authorization ignored correctness. They are not model
behavior.

## Stop condition

Stop this route before model contact if the specimen cannot prove all of the
following:

- learned, supplied, and reversed coverage receive the same authorization;
- removal and uncovered alphabets withhold without an environment action;
- decisions are identical across hidden profiles because profiles never enter
  the policy;
- reversal changes the later selected task slot but not authorization;
- ambiguous, malformed, stale, and mismatched inputs fail closed;
- exact replay reproduces every decision and external transition; and
- no scorer or harness-only field enters a runtime receipt.

If the specimen conforms, a live contact is still optional. The next question
would be whether the governed system's post-signal action outcomes justify the
cost across learned, removal, supplied, reversed, and uncovered paths. The
first-action difference would be a deterministic policy fact, not evidence of
model planning.

## Claim boundary

Conformance would establish only that a declared runtime governor can let
admitted signal records control access to a costly diagnostic without hidden
harness assistance. It would not show autonomous information seeking,
authorship quality, learned value-of-information, participant improvement,
transfer, or Formation.
