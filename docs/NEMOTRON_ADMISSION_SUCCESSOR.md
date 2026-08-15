# Corrected Nemotron admission successor

Status: **contact-ready exploratory successor; independently reviewed runner
licensed; no successor model call made**.

## Purpose and ancestry

Resolve the Nemotron 4B admission question left open by the first
[small-model packet](MODEL_ADMISSION_EXPLORATION.md). That packet stopped when
Nemotron used Python's ordinary `all(...)` builtin inside a sandbox that did not
provide it. The prompt had not disclosed the restriction. Independent audit
therefore returned `EVIDENCE_PARTIAL` rather than treating the stop as clean
model unreliability.

This successor changes the instrument openly. It uses new prompts, names,
vectors, and database contents. It states the Python execution vocabulary in
every Python prompt. The earlier prompt, output, scorer, and hashes remain
blocked development material and are not rewritten.

This remains exploratory model admission. It cannot establish a Formation
effect.

## Model and inference

Use only the already verified text artifact:

```text
nvidia/nemotron-3-nano-4b@q4_k_m
indexed artifact: nvidia/nemotron-3-nano-4b@lmstudio-community/NVIDIA-Nemotron-3-Nano-4B-GGUF/NVIDIA-Nemotron-3-Nano-4B-Q4_K_M.gguf
GGUF bytes: 2837072896
GGUF SHA-256: 083af225449463dd7c38bebc888f9dcad187b834d8b15e08c297dda37c968b50
embedded chat-template SHA-256: ab7813c3abdd9cb655905a410728b26c7884eca45ddfab8d9f931553485a7862
embedded chat-template characters: 10504
```

Use the same text-only LM Studio load and exact sampling JSON as the first
packet: 8,192-token context, maximum GPU offload, parallelism one, no vision,
no speculative decoding, one user message, no history or tools, temperature
`0.2`, top-p `0.95`, top-k `40`, repeat penalty `1`, presence and frequency
penalties `0`, and at most 768 output tokens. Anchors use seeds 2001 through
2004. Each target condition uses seeds 2101, 2102, and 2103.

Every receipt requirement and one-empty-output retry rule from
[the first normative appendix](MODEL_ADMISSION_VECTORS.md) applies unchanged.
The exact prompts, vectors, labels, and order are expanded in the
[successor appendix](NEMOTRON_ADMISSION_SUCCESSOR_VECTORS.md). If this charter
and that appendix conflict, refuse contact and repair the documents before a
model call.

## Disclosed Python environment and output gate

Every Python prompt ends with the exact block below. The placeholder in the
summaries in this charter means literal insertion of this block; the normative
appendix contains each expanded prompt with no placeholder.

```text
Execution environment:
- available builtins are ValueError, TypeError, all, any, bool, dict, int, isinstance, len, list, set, str, tuple, and type;
- no other builtin, import, file, network, dynamic execution, or additional definition is available.
- each input runs in a fresh process with a one-second CPU and wall-clock limit, an empty working directory, and no writable file;
- do not mutate payload or write to stdout or stderr.

Source requirements:
- define one top-level synchronous function with the requested name and exactly one ordinary positional-or-keyword argument named payload; do not use a positional-only argument, default, variadic argument, or keyword-only argument; annotations are allowed;
- do not use another top-level statement, decorator, class, async function, nested function or class, lambda, import, global, nonlocal, await, yield, yield from, exec, eval, compile, open, or dunder attribute.

Return exactly the function definition. Return no imports, tests, prose, or Markdown fence.
```

The child must provide exactly the listed builtins and enforce exactly the
stated restrictions. A source that names another builtin may parse, but a
resulting `NameError` fails the executable check under a now-disclosed
contract. Mutation, timeout, process crash, stdout, or stderr fails the affected
vector. These restrictions select a tiny executable instrument, not a general
Python sandbox.

The successor appendix freezes how raw output is parsed, how the exact
signature and whole syntax tree are checked, how Python literals enter the
child, and how execution results are compared. It also freezes the SQLite
query gate. Model-visible disclosure and harness enforcement are separate
contracts; both must agree before contact.

## Four new anchors

### C-P1

```text
Write this Python function:

    combine_labels(payload)

Contract:
- payload must be a tuple containing exactly two values;
- each value must have exact Python type str;
- return the two strings joined by one slash;
- raise ValueError for every invalid input.

<EXECUTION_ENVIRONMENT_BLOCK>
```

Vectors: `('east','wing') -> 'east/wing'`; `('','') -> '/'`; and exact
`ValueError` for `None`, `['east','wing']`, `()`, `('east',)`,
`('east','wing','roof')`, `(1,'wing')`, and `('east',None)`. The tuple remains
unchanged.

### C-P2

```text
Write this Python function:

    accept_mode(payload)

Contract:
- payload must have exact Python type str;
- if payload is exactly "active", return "active";
- raise ValueError for every other input.

<EXECUTION_ENVIRONMENT_BLOCK>
```

Vectors: `'active' -> 'active'`; exact `ValueError` for `'Active'`, `''`,
`None`, `['active']`, and `1`.

### C-S1

```text
You are writing one SQLite query.

Database:
CREATE TABLE endpoints(id INTEGER PRIMARY KEY, hostname TEXT NOT NULL, online INTEGER NOT NULL);

Question: return hostnames of online endpoints, ordered by hostname.

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence.
```

Execute against both variants:

| Id | Inserts | Expected rows |
| --- | --- | --- |
| C-S1-01 | `INSERT INTO endpoints VALUES (1,'cairn',1),(2,'delta',0),(3,'ember',1);` | `(('cairn',),('ember',))` |
| C-S1-02 | `INSERT INTO endpoints VALUES (8,'willow',0),(9,'larch',1),(10,'spruce',0);` | `(('larch',),)` |

### C-S2

```text
You are writing one SQLite query.

Database:
CREATE TABLE readings(sensor TEXT NOT NULL, value INTEGER NOT NULL);

Question: return each sensor and the sum of its values, ordered by sensor.

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence.
```

Execute against both variants:

| Id | Inserts | Expected rows |
| --- | --- | --- |
| C-S2-01 | `INSERT INTO readings VALUES ('r',4),('s',7),('r',2);` | `(('r',6),('s',7))` |
| C-S2-02 | `INSERT INTO readings VALUES ('north',5),('south',3),('north',-2),('south',8);` | `(('north',3),('south',11))` |

All four anchors must pass. Any failure stops the successor as
`contract_unreliable` without target calls or family cells.

## Python cold target

```text
Write this Python function:

    parse_versions(payload)

Contract:
- payload is a dictionary with exactly the keys "client_version" and "server_version";
- both values must be Python integers;
- both values must be at least zero;
- client_version must be less than or equal to server_version;
- return (client_version, server_version);
- raise ValueError for every invalid input.

<EXECUTION_ENVIRONMENT_BLOCK>
```

The ordinary class has nineteen vectors: two exact returns followed by
seventeen exact `ValueError` refusals. In order, their shapes are:

```text
{'client_version':0,'server_version':4} -> (0,4)
{'client_version':6,'server_version':6} -> (6,6)
None; [0,4]; {}; either missing key; one extra key;
string, float, None, and list in either value position;
negative value in either position; client_version greater than server_version
```

Every semicolon-separated invalid shape expands to the literal cases in the
successor appendix. The three held vectors are:

```text
{'client_version':True,'server_version':4}
{'client_version':0,'server_version':False}
{'client_version':False,'server_version':True}
```

The correct outcome for each held vector is exact `ValueError`. A cold call is
`full_pass` when all ordinary and held vectors pass. It is `boundary_miss` only
when every ordinary vector passes and at least one held vector returns normally
instead of raising `ValueError`, with no other held failure. This is useful
headroom, not the correct answer.

## Python direct-rule target

```text
Write this Python function:

    parse_slots(payload)

Contract:
- payload is a dictionary with exactly the keys "used_slots" and "total_slots";
- both values must have exact Python type int; bool is invalid even though bool is a subclass of int;
- both values must be at least zero;
- used_slots must be less than or equal to total_slots;
- return (used_slots, total_slots);
- raise ValueError for every invalid input.

<EXECUTION_ENVIRONMENT_BLOCK>
```

The direct-rule target has its own nineteen ordinary vectors and four held
vectors. Its ordinary shape sequence matches the cold ordinary sequence, with
keys and literal values replaced. Its held sequence separately places `True`
and `False` in each integer position. The successor appendix assigns every case
an exact id, literal, class, expected outcome, and order. No cold target input
is reused.

## SQLite cold target

```text
You are writing one SQLite query.

Database:
CREATE TABLE volumes(id INTEGER PRIMARY KEY, title TEXT NOT NULL);
CREATE TABLE loans(id INTEGER PRIMARY KEY, volume_id INTEGER);

Question: return titles of volumes that have never been loaned, ordered by title.

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence.
```

| Id | Inserts | Expected rows | Class |
| --- | --- | --- | --- |
| C-Q-O01 | `INSERT INTO volumes VALUES (1,'fjord'),(2,'grove'),(3,'heath'); INSERT INTO loans VALUES (10,1);` | `(('grove',),('heath',))` | ordinary |
| C-Q-O02 | `INSERT INTO volumes VALUES (5,'mire'),(8,'nook'),(9,'orchard'); INSERT INTO loans VALUES (20,8),(21,9);` | `(('mire',),)` | ordinary |
| C-Q-H01 | `INSERT INTO volumes VALUES (11,'pearl'),(12,'quill'),(13,'rune'); INSERT INTO loans VALUES (30,12),(31,NULL);` | `(('pearl',),('rune',))` | held |
| C-Q-H02 | `INSERT INTO volumes VALUES (21,'tarn'),(22,'umber'),(23,'vale'),(24,'wold'); INSERT INTO loans VALUES (40,22),(41,NULL),(42,24);` | `(('tarn',),('vale',))` | held |

## SQLite direct-rule target

```text
You are writing one SQLite query.

Database:
CREATE TABLE depots(id INTEGER PRIMARY KEY, code TEXT NOT NULL);
CREATE TABLE shipments(id INTEGER PRIMARY KEY, depot_id INTEGER);

Question: return codes of depots with no shipment, ordered by code. A NULL shipment depot does not identify any depot and must not remove unrelated rows. Express absence with a correlated NOT EXISTS condition.

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence.
```

| Id | Inserts | Expected rows | Class |
| --- | --- | --- | --- |
| D-Q-O01 | `INSERT INTO depots VALUES (2,'ax'),(4,'by'); INSERT INTO shipments VALUES (10,2);` | `(('by',),)` | ordinary |
| D-Q-O02 | `INSERT INTO depots VALUES (6,'cz'),(7,'du'),(9,'ev'); INSERT INTO shipments VALUES (20,7);` | `(('cz',),('ev',))` | ordinary |
| D-Q-H01 | `INSERT INTO depots VALUES (12,'fw'),(13,'gx'); INSERT INTO shipments VALUES (30,NULL),(31,12);` | `(('gx',),)` | held |
| D-Q-H02 | `INSERT INTO depots VALUES (30,'hy'),(31,'iz'),(32,'ja'),(33,'kb'); INSERT INTO shipments VALUES (40,31),(41,NULL),(42,33);` | `(('hy',),('ja',))` | held |

## Order, scoring, and stop

The maximum is sixteen logical calls:

```text
01 C-P1 seed 2001
02 C-P2 seed 2002
03 C-S1 seed 2003
04 C-S2 seed 2004
05-07 SQLite cold seeds 2101,2102,2103
08-10 SQLite direct-rule seeds 2101,2102,2103
11-13 Python cold seeds 2101,2102,2103
14-16 Python direct-rule seeds 2101,2102,2103
```

SQLite remains first, as it was in the original Nemotron schedule. This avoids
introducing an unnecessary order change while the successor repairs the Python
instrument.

Use the exact per-call, family, and terminal classifiers from the first charter.
A complete packet ends with one of `admitted:Python`, `admitted:SQLite`,
`admitted:Python,SQLite`, `cold_ceiling`, `not_teachable_here`,
`contract_unreliable`, or `mixed_unstable`.

## Claim and loses-conditions

An admitted result means only that this exact Nemotron artifact occupies the
developmental band on the named development family. It licenses a separate
Formation exploration using fresh material. It does not show that persistence,
governance, or Formation improves the model.

This successor loses if it hides the builtin vocabulary again; reuses a prompt,
input, schema, name set, or expected row from the first packet; changes the
model or inference settings; repairs output; continues after an anchor failure;
or promotes these development cases into a later claim.

The executable appendix and runner with disclosed builtins now pass fake tests,
and independent cold reviews returned `ADMISSION_PROTOCOL_STABLE` and
`RUNNER_LICENSED`. Model contact must still use the frozen runner without
editing this packet.
