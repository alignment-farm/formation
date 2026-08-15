# Normative packet for small-model admission

Status: **first packet complete; retained as contacted development material**.

This appendix freezes the complete development packet governed by
[the small-model admission charter](MODEL_ADMISSION_EXPLORATION.md). No prompt,
input, order, or inference field may change after the first model call.

## Model artifacts

The exact local variants are:

```text
mistralai/ministral-3-3b@q4_k_m
indexed artifact: mistralai/ministral-3-3b@lmstudio-community/Ministral-3-3B-Instruct-2512-GGUF/Ministral-3-3B-Instruct-2512-Q4_K_M.gguf
GGUF bytes: 2146498240
GGUF SHA-256: ee46f8f2cc4acf15e89699563e23b4a3919dce2e9ce7c44b53778d6590318e96

nvidia/nemotron-3-nano-4b@q4_k_m
indexed artifact: nvidia/nemotron-3-nano-4b@lmstudio-community/NVIDIA-Nemotron-3-Nano-4B-GGUF/NVIDIA-Nemotron-3-Nano-4B-Q4_K_M.gguf
GGUF bytes: 2837072896
GGUF SHA-256: 083af225449463dd7c38bebc888f9dcad187b834d8b15e08c297dda37c968b50
```

Before contact, the runner recomputes these values. A mismatch refuses contact
rather than silently selecting a new artifact.

Load each model in a separate LM Studio instance with an 8,192-token context
and maximum GPU offload, parallelism `1`, and speculative decoding disabled.
Load only the named text GGUF. Do not attach Ministral's `mmproj` file, a draft
model, adapter, or tool. The live selected variant must be the listed Q4_K_M
artifact. Record the server, runtime, model instance, and final load
configuration. Unload the first model before loading the second.

The embedded `tokenizer.chat_template` values are part of the frozen artifacts:

```text
Ministral template SHA-256: d28d7df94f0fd7e8d0075a22c473333d6e7dd2bc4c36c83e8b975300a0fb94bc
Ministral template characters: 7753
Nemotron template SHA-256: ab7813c3abdd9cb655905a410728b26c7884eca45ddfab8d9f931553485a7862
Nemotron template characters: 10504
```

The runner extracts and verifies those embedded bytes before loading. The
request contains no authored system message; any default system text inserted
by the frozen embedded template is part of the contacted model artifact, not a
harness instruction. Refuse if the template hash or length differs.

## Inference request

Every logical call uses one user message and no system message, tools, response
history, or prior response identifier. Send these explicit fields through the
OpenAI-compatible chat-completions endpoint:

```json
{
  "frequency_penalty": 0,
  "max_tokens": 768,
  "presence_penalty": 0,
  "repeat_penalty": 1,
  "seed": "<frozen integer for this logical call>",
  "stream": false,
  "temperature": 0.2,
  "top_k": 40,
  "top_p": 0.95
}
```

The three repetitions of a target condition use seeds `1101`, `1102`, and
`1103` in that order. The four anchors use seeds `1001`, `1002`, `1003`, and
`1004` in their listed order. The same seeds apply to both models. Retain the
complete request and response envelopes, including usage fields.

These fields, including `seed`, are exhaustive. Do not send `min_p`, mirostat,
reasoning controls, stop strings, logit bias, or any other optional inference
field. If LM Studio cannot honor this exact request shape, no inference is
licensed.

## Source and query gates

Python output uses the source boundary in
[the strict Python contact](PYTHON_BOUNDARY_CONTACT_CHARTER.md): exactly one
top-level synchronous function with the requested name and one argument named
`payload`; no fence, import, decorator, class, additional definition, async,
lambda, global, nonlocal, dynamic execution, file access, yield, or dunder
attribute. Each vector runs in a fresh restricted child process.

SQLite output uses the query boundary in
[the nullable anti-join contact](SQLITE_CONTACT_CHARTER.md): exactly one SQLite
`SELECT` statement, with one optional trailing semicolon and no prose or fence.
Each database variant is fresh and query-only before evaluation.

## Anchor A-P1: exact pair of strings

Prompt:

```text
Write this Python function:

    join_pair(payload)

Contract:
- payload must be a list containing exactly two values;
- each value must have exact Python type str;
- return the two strings joined by one colon;
- raise ValueError for every invalid input.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence.
```

Vectors, in order:

| Id | Input | Expected |
| --- | --- | --- |
| A-P1-01 | `['north', 'gate']` | return exact `str` `'north:gate'` |
| A-P1-02 | `['', '']` | return exact `str` `':'` |
| A-P1-03 | `None` | raise exactly `ValueError` |
| A-P1-04 | `('north', 'gate')` | raise exactly `ValueError` |
| A-P1-05 | `[]` | raise exactly `ValueError` |
| A-P1-06 | `['north']` | raise exactly `ValueError` |
| A-P1-07 | `['north', 'gate', 'west']` | raise exactly `ValueError` |
| A-P1-08 | `[1, 'gate']` | raise exactly `ValueError` |
| A-P1-09 | `['north', None]` | raise exactly `ValueError` |

The list must remain unchanged.

## Anchor A-P2: named allowed value

Prompt:

```text
Write this Python function:

    require_ready(payload)

Contract:
- payload must have exact Python type str;
- if payload is exactly "ready", return "ready";
- raise ValueError for every other input.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence.
```

Vectors, in order:

| Id | Input | Expected |
| --- | --- | --- |
| A-P2-01 | `'ready'` | return exact `str` `'ready'` |
| A-P2-02 | `'Ready'` | raise exactly `ValueError` |
| A-P2-03 | `''` | raise exactly `ValueError` |
| A-P2-04 | `None` | raise exactly `ValueError` |
| A-P2-05 | `['ready']` | raise exactly `ValueError` |
| A-P2-06 | `1` | raise exactly `ValueError` |

## Anchor A-S1: simple selection

Prompt:

```text
You are writing one SQLite query.

Database:
CREATE TABLE devices(id INTEGER PRIMARY KEY, label TEXT NOT NULL, enabled INTEGER NOT NULL);

Question: return labels of enabled devices, ordered by label.

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence.
```

Execute the returned query against both variants:

| Id | Inserts | Expected rows |
| --- | --- | --- |
| A-S1-01 | `INSERT INTO devices VALUES (1,'ash',1),(2,'birch',0),(3,'cedar',1);` | `(('ash',), ('cedar',))` |
| A-S1-02 | `INSERT INTO devices VALUES (7,'zinc',0),(8,'amber',1),(9,'moss',0);` | `(('amber',),)` |

## Anchor A-S2: grouped sum

Prompt:

```text
You are writing one SQLite query.

Database:
CREATE TABLE entries(category TEXT NOT NULL, amount INTEGER NOT NULL);

Question: return each category and the sum of its amounts, ordered by category.

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence.
```

Execute the returned query against both variants:

| Id | Inserts | Expected rows |
| --- | --- | --- |
| A-S2-01 | `INSERT INTO entries VALUES ('a',2),('b',5),('a',3);` | `(('a', 5), ('b', 5))` |
| A-S2-02 | `INSERT INTO entries VALUES ('west',4),('east',1),('west',-1),('east',6);` | `(('east', 7), ('west', 3))` |

## Python cold target

Prompt:

```text
Write this Python function:

    parse_limits(payload)

Contract:
- payload is a dictionary with exactly the keys "soft" and "hard";
- both values must be Python integers;
- 0 <= soft <= hard;
- return (soft, hard);
- raise ValueError for every invalid input.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence.
```

Use all 24 vectors `E-O01` through `E-H03` from
[the strict Python contact appendix](PYTHON_BOUNDARY_CONTACT_VECTORS.md).
The ordinary set is `E-O01` through `E-O21`. A qualified boundary miss requires
all 21 to pass and at least one of `E-H01` through `E-H03` to return normally.

## Python direct-rule target

Prompt:

```text
Write this Python function:

    parse_revisions(payload)

Contract:
- payload is a dictionary with exactly the keys "artifact_revision" and "authority_revision";
- both values must have exact Python type int; bool is invalid even though bool is a subclass of int;
- both values must be at least zero;
- return (artifact_revision, authority_revision);
- raise ValueError for every invalid input.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence.
```

Use the exact 18 vectors `V1-01` through `V1-18` from
[the strict Python contact appendix](PYTHON_BOUNDARY_CONTACT_VECTORS.md).
`V1-01` through `V1-14` are ordinary. `V1-15` through `V1-18` are the held
boolean boundary. These inputs and the function name are disjoint from the cold
target.

## SQLite cold target

Prompt:

```text
You are writing one SQLite query.

Database:
CREATE TABLE vessels(id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE inspections(id INTEGER PRIMARY KEY, vessel_id INTEGER);

Question: return names of vessels that have never been inspected, ordered by name.

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence.
```

Run the same query against these variants, in order:

| Id | Inserts | Expected rows | Class |
| --- | --- | --- | --- |
| S-C-O01 | `INSERT INTO vessels VALUES (1,'dune'),(2,'flint'),(3,'glass'); INSERT INTO inspections VALUES (10,1);` | `(('flint',), ('glass',))` | ordinary |
| S-C-O02 | `INSERT INTO vessels VALUES (4,'elm'),(8,'fir'),(9,'gum'); INSERT INTO inspections VALUES (20,8),(21,9);` | `(('elm',),)` | ordinary |
| S-C-H01 | `INSERT INTO vessels VALUES (10,'amber'),(11,'blue'),(12,'copper'); INSERT INTO inspections VALUES (30,11),(31,NULL);` | `(('amber',), ('copper',))` | held |
| S-C-H02 | `INSERT INTO vessels VALUES (21,'ibis'),(22,'jay'),(23,'kite'),(24,'loon'); INSERT INTO inspections VALUES (40,22),(41,NULL),(42,24);` | `(('ibis',), ('kite',))` | held |

## SQLite direct-rule target

Prompt:

```text
You are writing one SQLite query.

Database:
CREATE TABLE packages(id INTEGER PRIMARY KEY, label TEXT NOT NULL);
CREATE TABLE scans(id INTEGER PRIMARY KEY, package_id INTEGER);

Question: return labels of packages that have never been scanned, ordered by label. The query must remain correct when scans.package_id contains NULL. In SQLite, use NOT EXISTS, or if you use NOT IN, exclude NULL inside its subquery.

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence.
```

Run the same query against these variants, in order:

| Id | Inserts | Expected rows | Class |
| --- | --- | --- | --- |
| S-D-O01 | `INSERT INTO packages VALUES (1,'red'),(2,'teal'); INSERT INTO scans VALUES (10,1);` | `(('teal',),)` | ordinary |
| S-D-O02 | `INSERT INTO packages VALUES (5,'oak'),(6,'pine'),(7,'yew'); INSERT INTO scans VALUES (20,6);` | `(('oak',), ('yew',))` | ordinary |
| S-D-H01 | `INSERT INTO packages VALUES (20,'north'),(21,'south'); INSERT INTO scans VALUES (30,NULL),(31,20);` | `(('south',),)` | held |
| S-D-H02 | `INSERT INTO packages VALUES (30,'quartz'),(31,'reed'),(32,'stone'),(33,'wheat'); INSERT INTO scans VALUES (40,31),(41,NULL),(42,33);` | `(('quartz',), ('stone',))` | held |

## Exact logical-call order

Ministral 3B:

```text
01 A-P1 seed 1001
02 A-P2 seed 1002
03 A-S1 seed 1003
04 A-S2 seed 1004
05-07 Python cold seeds 1101,1102,1103
08-10 Python direct-rule seeds 1101,1102,1103
11-13 SQLite cold seeds 1101,1102,1103
14-16 SQLite direct-rule seeds 1101,1102,1103
```

Nemotron 4B:

```text
01 A-P1 seed 1001
02 A-P2 seed 1002
03 A-S1 seed 1003
04 A-S2 seed 1004
05-07 SQLite cold seeds 1101,1102,1103
08-10 SQLite direct-rule seeds 1101,1102,1103
11-13 Python cold seeds 1101,1102,1103
14-16 Python direct-rule seeds 1101,1102,1103
```

An anchor failure stops that model after its failing call. It does not change
the other model's order. Direct-rule calls otherwise run even after a cold
ceiling. The runner computes per-call, family, and model labels exactly as the
charter specifies.

## Required receipt keys

Every process attempt records at least:

```text
model key, selected variant, indexed artifact, GGUF SHA-256 and byte count
embedded chat-template SHA-256 and character count
LM Studio and inference-runtime versions, instance id, final load configuration
logical call, attempt, family, condition, seed, complete sampling JSON
exact request envelope, exact response envelope, prompt bytes, output bytes
prompt and output SHA-256, start/end time, duration, usage fields
retry reason and prior-attempt link, or explicit no-retry
source/query gate result, complete per-vector/database results
per-call label, family label when complete, terminal model result when complete
```

An anchor-stopped model has no family labels. Skipped calls produce no synthetic
receipts. Summary records state the exact stopping call and reason.

## Development-material block

Every prompt, vector, database variant, scorer input, output, and hash in this
packet becomes blocked development material after contact. A successor may use
the same general Python or SQLite principle only with newly authored prompts,
schemas, names, vectors, and data that were frozen under its own charter before
contact.
