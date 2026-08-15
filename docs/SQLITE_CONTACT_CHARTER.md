# First cold-model contact charter: SQLite nullable anti-joins

Status: **pre-contact charter; contact semantics stable, runner pending**.

## Purpose

Test whether a small, real executable consequence can expose a repeatable cold-
model error and whether ordinary persistence is already enough to correct it.
The task uses SQLite anti-joins when a subquery can return `NULL`.

This is baseline calibration. It does not test a governed formation mechanism,
because no such general mechanism is implemented for this task. If raw
persistence or a model-authored lesson solves the fresh cases, that simpler
result is the point.

## Model and coldness

Use Cursor CLI model `composer-2.5` for every call. Each call starts in a new
empty temporary directory with this exact command shape:

```text
agent -p --mode ask --model composer-2.5 --trust --workspace <empty-directory> <exact-prompt>
```

No call resumes a chat. The temporary directory contains no files. The model
receives no repository path, prior provider thread, or undeclared prompt prefix.
Exact prompts and raw outputs are retained outside developmental state.

`auto` is not allowed because it may route different calls to different model
families. Changing model or settings invalidates the comparison.

## Task interface

Each task uses this exact template, replacing only the two marked blocks:

```text
You are writing one SQLite query.

Database:
<SCHEMA_AND_INSERTS>

Question: <QUESTION>

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence.
```

Each task therefore gives:

- complete SQLite schema and inserts;
- one plain-language data question; and
- the instruction to return exactly one read-only SQL query, with no prose or
  Markdown fence.

The model cannot execute SQLite. A local harness treats the complete trimmed
output as the query. It rejects empty output, Markdown fences, or output whose
first case-insensitive token is not exactly `SELECT`. Python `sqlite3.execute`
must accept it as one statement; its built-in multiple-statement refusal is
authoritative. The connection sets `PRAGMA query_only=ON` before execution.
One trailing semicolon is allowed. Comments or prose before `SELECT`, `WITH`,
`PRAGMA`, `EXPLAIN`, and every non-`SELECT` first token refuse.

The harness executes accepted output in a fresh in-memory SQLite database and
compares ordered tuples of native Python `sqlite3` values with the precomputed
oracle tuples. SQLite `TEXT` compares as Python `str`; SQLite `INTEGER` compares
as Python `int`. Digit strings never substitute for integers.

Whenever rows enter a retained record or model offer, encode the ordered rows
as compact JSON arrays using `json.dumps(rows, ensure_ascii=True,
separators=(",", ":"))` after converting each tuple to a JSON array. Empty rows
encode exactly as `[]`; exploration oracle rows encode as
`[["Bex"],["Cy"]]`. This encoding is evidence transport only and is never an
engine input or hidden oracle offer.

The model receives no expected rows, case-family label, hidden nullable-risk
label, scorer feedback, or future case.

## Failure structure

In SQLite, `x NOT IN (subquery)` does not behave as a simple set subtraction
when the subquery contains `NULL`. The comparison becomes unknown and can remove
every candidate row. A correlated `NOT EXISTS` anti-join remains correct.

This explanation is protocol knowledge, not part of the cold task prompt.

## Exploration contact

Exploration asks one acquisition task three times in independent cold calls.
This budget is fixed before contact.

Schema:

```sql
CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER);
INSERT INTO customers VALUES (1,'Ada'),(2,'Bex'),(3,'Cy');
INSERT INTO orders VALUES (10,1),(11,NULL);
```

Question: return customer names for customers who have never placed an order,
ordered by name.

Oracle rows:

```text
Bex
Cy
```

The exact exploration prompt is the template above with the displayed SQL and
this question text:

```text
return customer names for customers who have never placed an order, ordered by name.
```

The three raw cold outputs are scored only to decide engagement:

- **engaged** if at least two calls pass extraction, contain `NOT IN` after
  collapsing ASCII whitespace runs to one space and comparing case-
  insensitively, execute to zero rows, and differ from the oracle rows;
- **not engaged** if at least two calls return correct rows;
- **unstable** otherwise, including executable wrong queries that do not meet
  the exact `NOT IN` and zero-row predicate.

Exploration is not evidence for a formation effect. If it closes `not engaged`
or `unstable`, stop this contact without changing prompts or shopping for a
failure.

## Acquisition consequence

Only if exploration is engaged, select the first call by numeric order that
meets the mechanical engagement predicate as the acquisition occurrence.
Execute it once more in a
fresh database and retain:

- the exact task prompt;
- exact model query;
- SQLite result rows;
- oracle rows;
- SQLite version; and
- the mechanical mismatch.

The harness records no lesson. It may state only that the query returned the
wrong rows for the supplied database.

In a separate cold call, send this exact prompt, substituting the retained
acquisition blocks without alteration:

```text
Review this SQLite attempt after its external result.

Task:
<EXACT_ACQUISITION_TASK_PROMPT>

Query returned by the model:
<EXACT_QUERY>

SQLite rows:
<EXACT_RETURNED_ROWS>

External check: incorrect.

Explain what caused this result. State any rule you infer from it. Do not solve or discuss any other task.
```

The exact response is the **model-authored lesson**. It is evidence to compare,
not ground truth. The lesson call receives neither oracle rows nor validation
cases.

## Frozen validation cases

The following cases are frozen before exploration begins. They are never shown
during exploration.

### V1 — near transfer: packages without scans

Schema and inserts:

```sql
CREATE TABLE packages(id INTEGER PRIMARY KEY, label TEXT NOT NULL);
CREATE TABLE scans(id INTEGER PRIMARY KEY, package_ref INTEGER);
INSERT INTO packages VALUES (1,'amber'),(2,'blue'),(3,'copper');
INSERT INTO scans VALUES (20,2),(21,NULL);
```

Question text:

```text
return labels of packages that have never been scanned, ordered by label.
```

Oracle rows: `amber`, `copper`.

### V2 — near transfer: authors without reviews

```sql
CREATE TABLE authors(id INTEGER PRIMARY KEY, handle TEXT NOT NULL);
CREATE TABLE reviews(id INTEGER PRIMARY KEY, author_id INTEGER);
INSERT INTO authors VALUES (4,'elm'),(5,'fir'),(6,'gum');
INSERT INTO reviews VALUES (30,4),(31,NULL),(32,6);
```

Question text:

```text
return handles of authors with no review, ordered by handle.
```

Oracle rows: `fir`.

### V3 — changed surface: reserved ports

```sql
CREATE TABLE ports(number INTEGER PRIMARY KEY);
CREATE TABLE reservations(port_number INTEGER);
INSERT INTO ports VALUES (8000),(8001),(8002),(8003);
INSERT INTO reservations VALUES (8001),(NULL),(8003);
```

Question text:

```text
return unreserved port numbers in ascending order.
```

Oracle rows: `8000`, `8002`.

### N1 — non-transfer: literal exclusion

```sql
CREATE TABLE jobs(id INTEGER PRIMARY KEY, state TEXT NOT NULL);
INSERT INTO jobs VALUES (1,'ready'),(2,'held'),(3,'done'),(4,'ready');
```

Question text:

```text
return job ids whose state is neither held nor done, ordered by id.
```

Oracle rows: `1`, `4`. There is no nullable subquery and no anti-join between
tables.

### N2 — current query already excludes nulls

```sql
CREATE TABLE devices(id INTEGER PRIMARY KEY, label TEXT NOT NULL);
CREATE TABLE leases(device_id INTEGER);
INSERT INTO devices VALUES (1,'a'),(2,'b'),(3,'c');
INSERT INTO leases VALUES (1),(NULL);
```

Question text:

```text
using NOT IN with a subquery that contains the exact filter WHERE device_id IS NOT NULL, return unleased device labels ordered by label.
```

Oracle rows: `b`, `c`.

N2 measures whether an offered lesson becomes an inflexible ban rather than
whether the rows can be obtained by an easier rewrite. For scoring, collapse
ASCII whitespace runs to one space and compare case-insensitively. The query
must contain both `NOT IN` and the exact normalized substring
`WHERE device_id IS NOT NULL`. Otherwise it refuses even if rows are correct.

## Baseline conditions

Every validation case is run in a fresh cold call. Complete the full
cold/static condition first, then raw persistence, then authored lesson. Within
each condition the case order is V2, N1, V1, N2, V3.

1. **Cold/static:** the exact task template and case blocks above.
2. **Raw persistence:** prefix the exact task prompt with the block below,
   substituting retained values verbatim. It includes the observed rows and
   external `incorrect` status, but not hidden oracle rows.
3. **Authored lesson:** prefix the exact task prompt with the second block below,
   substituting the model-authored response verbatim. The acquisition transcript
   is absent.

Raw prefix:

```text
Prior SQLite occurrence:

Task:
<EXACT_ACQUISITION_TASK_PROMPT>

Query returned by the model:
<EXACT_QUERY>

SQLite rows:
<EXACT_RETURNED_ROWS>

External check: incorrect.

Use this prior occurrence only if it is relevant to the current task.

Current task follows.

```

Authored-lesson prefix:

```text
Prior model-authored lesson:

<EXACT_MODEL_AUTHORED_LESSON>

Use this lesson only if it is relevant to the current task.

Current task follows.

```

The offers are otherwise identical. Raw persistence is allowed to win. The
authored lesson is allowed to harm N1 or violate N2. No governed condition or
ablation is fabricated for this calibration.

## Scoring

Primary scoring is executable:

- query parses as exactly one read-only statement;
- query returns the exact ordered oracle rows; and
- N2 obeys its explicit `NOT IN` and non-null-filter constraint.

Retain query text, rows, refusal reason, input and output sizes, and wall time.
Do not score whether the model mentions `NULL`, uses preferred wording, or
claims to have learned.

Report each case and condition separately. With five cases per condition, no
aggregate formation or transfer verdict is licensed. Descriptive outcomes are:

- cold success count;
- raw-persistence success count;
- authored-lesson success count;
- per-case differences on V1–V3;
- per-case differences or regressions on N1–N2; and
- input/output character counts and latency.

## Stopping rule

Maximum logical model calls:

- three cold exploration calls;
- one authored-lesson call only if engaged; and
- fifteen validation calls only if engaged.

Maximum total: nineteen logical calls. Do not revise prompts, schemas, ordering, oracle
rows, extraction rules, or conditions after the first exploration call. Any
operational failure may be retried once only when no model output was returned.
A retry is a second process attempt for the same logical call and does not add a
case. Thus the absolute maximum is nineteen logical calls and thirty-eight
process attempts. Retain both attempts and the retry reason.

For every call retain: Cursor CLI version, exact model id, exact CLI arguments,
fresh temporary-directory path and empty-directory check, no-resume status,
condition, case id, call index, exact prompt bytes, raw output bytes, start and
end time, process exit status, and retry link if any.

Stop as `not engaged` or `unstable` after exploration when required. Stop after
the frozen validation matrix otherwise. Do not add more SQLite puzzles.

## Claims and loses-conditions

This contact may show only whether the selected cold model exhibits the error
and whether two simple persistence offers change performance on these five
fresh tasks. It cannot show formation, transfer by a governed mechanism,
generality across SQL engines, or persistent practitioner development.

The contact loses if model identity or coldness changes; if engagement requires
non-mechanical causal judgment; if any prompt is paraphrased rather than
assembled from the frozen text; if validation prompts
are revised after exploration; if expected rows or hidden labels enter a model
offer; if the harness writes or repairs the lesson; if raw persistence omits an
unfavorable part of the acquisition transcript; if query scoring uses prose
judgment instead of SQLite results; if hidden oracle rows enter a raw or lesson
offer; or if a not-engaged pilot is replaced with another task to obtain a
favorable failure.

## Contact gate

No model call is licensed until independent cold readers agree on:

1. exact model and cold-session operation;
2. exploration engagement rule and stop;
3. frozen validation schemas, questions, order, and oracle rows;
4. exact cold, raw, and authored-lesson offers;
5. executable query extraction and scoring;
6. maximum call budget and retry rule; and
7. the absence of any governed-formation claim.

Two independent final cold readers reconstructed the same prompts, mechanical
engagement and stop, model and cold-session boundary, raw and authored-lesson
offers, SQL extraction, native row comparison, JSON evidence encoding,
condition schedule, retry budget, and claim boundary. Earlier reviews exposed
and repaired causal engagement judgment, paraphrasable prompts, hidden oracle
content in raw persistence, coached lesson authorship, ambiguous SQL extraction,
unfrozen provider order, row-byte ambiguity, and retry accounting.

The semantic contact gate is closed. Model contact still waits for a reviewed
runner that assembles these exact bytes, uses a new empty workspace for every
call, enforces read-only SQLite scoring, retains the required receipts, and
stops automatically on `not engaged` or `unstable`.
