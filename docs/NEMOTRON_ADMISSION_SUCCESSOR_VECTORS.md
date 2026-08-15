# Normative vectors for the corrected Nemotron admission

Status: **pre-contact normative appendix; runner must reproduce exactly**.

This appendix expands the complete packet governed by the
[corrected successor charter](NEMOTRON_ADMISSION_SUCCESSOR.md). Its prompts,
inputs, expected outcomes, class labels, seeds, and order are frozen together.
No participant model has contacted this material.

## Shared Python execution block

The following bytes end every Python prompt in this appendix:

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

The prompt blocks below include those bytes literally. The runner does not
assemble model-visible prompts by substituting a private suffix.

## Exact Python gate and execution

The runner applies this procedure without repairing the model output:

1. Reject the raw output if it contains the three-byte Markdown-fence marker.
2. Apply Python's `str.strip()` to the raw output and pass the result to
   `ast.parse`. A parse error is `syntax_error`.
3. Require the module body to contain exactly one node whose exact type is
   `ast.FunctionDef`. Its name must be the requested name and its decorator
   list must be empty.
4. Require zero positional-only arguments, exactly one ordinary argument named
   `payload`, no defaults, no variadic positional or keyword argument, and no
   keyword-only argument. Annotations do not affect this check.
5. Walk the whole tree with `ast.walk`. Reject `AsyncFunctionDef`, `ClassDef`,
   `Global`, `Import`, `ImportFrom`, `Lambda`, `Nonlocal`, `Await`, `Yield`, or
   `YieldFrom`; any `FunctionDef` other than the one module-level function; any
   attribute whose name begins with `__`; and a direct name call to `compile`,
   `eval`, `exec`, or `open`.

A gate rejection produces one refused result for every vector and no child
process. The result records the stable first applicable reason:
`markdown_fence`, `syntax_error`, `one_function_required`,
`exact_function_required`, `exact_payload_signature_required`,
`disallowed_syntax`, `nested_definition`, `dunder_attribute`, or
`disallowed_call`, in the procedure's order.

For an accepted source, every table `Input` cell is an exact Python-literal
string and is also the recorded `input_repr`. The isolated child decodes it
with `ast.literal_eval`; JSON is not used to decode vectors. It deep-copies the
decoded value, invokes the function, and detects mutation by value inequality
or a change in the outer value's exact type. A return passes only when both its
exact type name and `repr` equal the table's expectation. A refusal passes only
when the raised exception's exact type is `ValueError`. The runner applies the
fresh-process, resource, output, and builtin restrictions stated in the prompt;
the allowed builtin mapping contains every and only the fourteen named values,
including `all` and `any`. The stripped accepted source, not the raw output, is
compiled in the child.

## Exact SQLite gate and execution

The runner applies `str.strip()` to the raw output. It refuses an empty result
or any result containing the three-byte Markdown-fence marker. It then applies
the anchored Python regular expression `[A-Za-z]+` at character zero of the
trimmed output and requires the matched group, uppercased, to equal `SELECT`.
No match also refuses. Thus leading prose or comments, `WITH`, `PRAGMA`,
`EXPLAIN`, and every other first token refuse; `SELECT*FROM` passes this gate.
It then creates a fresh in-memory SQLite database, applies the table DDL and
one vector's inserts, sets `PRAGMA query_only=ON`, and passes the complete
trimmed output to one `sqlite3.execute` call. SQLite's own multiple-statement
refusal is authoritative. One trailing semicolon is accepted.

The result is the ordered tuple of native `sqlite3` row tuples and must equal
the table oracle exactly. Each vector gets a fresh database. An empty, fenced,
or non-`SELECT` output is `gate_fail`. A SQLite parse, execution, or
multiple-statement error is `ordinary_fail`, unless the query gate already
refused it. For the direct-rule query, normalized ASCII whitespace and
case-insensitive comparison must also find the contiguous words `NOT EXISTS`.
Normalization is exactly
`re.sub(r"[\t\n\r\f\v ]+", " ", query).strip().upper()`; the normalized string
must contain the substring `NOT EXISTS`. Otherwise the call is `ordinary_fail`
even if its rows happen to match.

In every Python table, `return exact ` followed by a type code span and a value
code span freezes `expected` as `return:<value repr>`, `return_type` as the
literal type span, and `return_repr` as the literal value span. `raise exactly
ValueError` freezes `expected` as `raises:ValueError` and leaves both return
fields null. These are authored vector fields; the runner does not scrape the
Markdown table at contact time.

## Anchor C-P1

```text
Write this Python function:

    combine_labels(payload)

Contract:
- payload must be a tuple containing exactly two values;
- each value must have exact Python type str;
- return the two strings joined by one slash;
- raise ValueError for every invalid input.

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

| Test id | Input | Class | Expected |
| --- | --- | --- | --- |
| C-P1-01 | `('east', 'wing')` | ordinary | return exact `str` `'east/wing'` |
| C-P1-02 | `('', '')` | ordinary | return exact `str` `'/'` |
| C-P1-03 | `None` | ordinary | raise exactly `ValueError` |
| C-P1-04 | `['east', 'wing']` | ordinary | raise exactly `ValueError` |
| C-P1-05 | `()` | ordinary | raise exactly `ValueError` |
| C-P1-06 | `('east',)` | ordinary | raise exactly `ValueError` |
| C-P1-07 | `('east', 'wing', 'roof')` | ordinary | raise exactly `ValueError` |
| C-P1-08 | `(1, 'wing')` | ordinary | raise exactly `ValueError` |
| C-P1-09 | `('east', None)` | ordinary | raise exactly `ValueError` |

The tuple input must remain unchanged.

## Anchor C-P2

```text
Write this Python function:

    accept_mode(payload)

Contract:
- payload must have exact Python type str;
- if payload is exactly "active", return "active";
- raise ValueError for every other input.

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

| Test id | Input | Class | Expected |
| --- | --- | --- | --- |
| C-P2-01 | `'active'` | ordinary | return exact `str` `'active'` |
| C-P2-02 | `'Active'` | ordinary | raise exactly `ValueError` |
| C-P2-03 | `''` | ordinary | raise exactly `ValueError` |
| C-P2-04 | `None` | ordinary | raise exactly `ValueError` |
| C-P2-05 | `['active']` | ordinary | raise exactly `ValueError` |
| C-P2-06 | `1` | ordinary | raise exactly `ValueError` |

## Anchor C-S1

```text
You are writing one SQLite query.

Database:
CREATE TABLE endpoints(id INTEGER PRIMARY KEY, hostname TEXT NOT NULL, online INTEGER NOT NULL);

Question: return hostnames of online endpoints, ordered by hostname.

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence.
```

| Test id | Inserts | Class | Expected rows |
| --- | --- | --- | --- |
| C-S1-01 | `INSERT INTO endpoints VALUES (1,'cairn',1),(2,'delta',0),(3,'ember',1);` | ordinary | `(('cairn',), ('ember',))` |
| C-S1-02 | `INSERT INTO endpoints VALUES (8,'willow',0),(9,'larch',1),(10,'spruce',0);` | ordinary | `(('larch',),)` |

## Anchor C-S2

```text
You are writing one SQLite query.

Database:
CREATE TABLE readings(sensor TEXT NOT NULL, value INTEGER NOT NULL);

Question: return each sensor and the sum of its values, ordered by sensor.

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence.
```

| Test id | Inserts | Class | Expected rows |
| --- | --- | --- | --- |
| C-S2-01 | `INSERT INTO readings VALUES ('r',4),('s',7),('r',2);` | ordinary | `(('r', 6), ('s', 7))` |
| C-S2-02 | `INSERT INTO readings VALUES ('north',5),('south',3),('north',-2),('south',8);` | ordinary | `(('north', 3), ('south', 11))` |

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

| Test id | Input | Class | Expected |
| --- | --- | --- | --- |
| C-PY-O01 | `{'client_version': 0, 'server_version': 4}` | ordinary | return exact `tuple` `(0, 4)` |
| C-PY-O02 | `{'client_version': 6, 'server_version': 6}` | ordinary | return exact `tuple` `(6, 6)` |
| C-PY-O03 | `None` | ordinary | raise exactly `ValueError` |
| C-PY-O04 | `[0, 4]` | ordinary | raise exactly `ValueError` |
| C-PY-O05 | `{}` | ordinary | raise exactly `ValueError` |
| C-PY-O06 | `{'client_version': 0}` | ordinary | raise exactly `ValueError` |
| C-PY-O07 | `{'server_version': 4}` | ordinary | raise exactly `ValueError` |
| C-PY-O08 | `{'client_version': 0, 'server_version': 4, 'channel': 'blue'}` | ordinary | raise exactly `ValueError` |
| C-PY-O09 | `{'client_version': '0', 'server_version': 4}` | ordinary | raise exactly `ValueError` |
| C-PY-O10 | `{'client_version': 0.0, 'server_version': 4}` | ordinary | raise exactly `ValueError` |
| C-PY-O11 | `{'client_version': None, 'server_version': 4}` | ordinary | raise exactly `ValueError` |
| C-PY-O12 | `{'client_version': [0], 'server_version': 4}` | ordinary | raise exactly `ValueError` |
| C-PY-O13 | `{'client_version': 0, 'server_version': '4'}` | ordinary | raise exactly `ValueError` |
| C-PY-O14 | `{'client_version': 0, 'server_version': 4.0}` | ordinary | raise exactly `ValueError` |
| C-PY-O15 | `{'client_version': 0, 'server_version': None}` | ordinary | raise exactly `ValueError` |
| C-PY-O16 | `{'client_version': 0, 'server_version': [4]}` | ordinary | raise exactly `ValueError` |
| C-PY-O17 | `{'client_version': -1, 'server_version': 4}` | ordinary | raise exactly `ValueError` |
| C-PY-O18 | `{'client_version': 0, 'server_version': -1}` | ordinary | raise exactly `ValueError` |
| C-PY-O19 | `{'client_version': 5, 'server_version': 4}` | ordinary | raise exactly `ValueError` |
| C-PY-H01 | `{'client_version': True, 'server_version': 4}` | held | raise exactly `ValueError` |
| C-PY-H02 | `{'client_version': 0, 'server_version': False}` | held | raise exactly `ValueError` |
| C-PY-H03 | `{'client_version': False, 'server_version': True}` | held | raise exactly `ValueError` |

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

| Test id | Input | Class | Expected |
| --- | --- | --- | --- |
| D-PY-O01 | `{'used_slots': 0, 'total_slots': 5}` | ordinary | return exact `tuple` `(0, 5)` |
| D-PY-O02 | `{'used_slots': 7, 'total_slots': 7}` | ordinary | return exact `tuple` `(7, 7)` |
| D-PY-O03 | `None` | ordinary | raise exactly `ValueError` |
| D-PY-O04 | `[0, 5]` | ordinary | raise exactly `ValueError` |
| D-PY-O05 | `{}` | ordinary | raise exactly `ValueError` |
| D-PY-O06 | `{'used_slots': 0}` | ordinary | raise exactly `ValueError` |
| D-PY-O07 | `{'total_slots': 5}` | ordinary | raise exactly `ValueError` |
| D-PY-O08 | `{'used_slots': 0, 'total_slots': 5, 'source': 'green'}` | ordinary | raise exactly `ValueError` |
| D-PY-O09 | `{'used_slots': '0', 'total_slots': 5}` | ordinary | raise exactly `ValueError` |
| D-PY-O10 | `{'used_slots': 0.0, 'total_slots': 5}` | ordinary | raise exactly `ValueError` |
| D-PY-O11 | `{'used_slots': None, 'total_slots': 5}` | ordinary | raise exactly `ValueError` |
| D-PY-O12 | `{'used_slots': [0], 'total_slots': 5}` | ordinary | raise exactly `ValueError` |
| D-PY-O13 | `{'used_slots': 0, 'total_slots': '5'}` | ordinary | raise exactly `ValueError` |
| D-PY-O14 | `{'used_slots': 0, 'total_slots': 5.0}` | ordinary | raise exactly `ValueError` |
| D-PY-O15 | `{'used_slots': 0, 'total_slots': None}` | ordinary | raise exactly `ValueError` |
| D-PY-O16 | `{'used_slots': 0, 'total_slots': [5]}` | ordinary | raise exactly `ValueError` |
| D-PY-O17 | `{'used_slots': -2, 'total_slots': 5}` | ordinary | raise exactly `ValueError` |
| D-PY-O18 | `{'used_slots': 0, 'total_slots': -2}` | ordinary | raise exactly `ValueError` |
| D-PY-O19 | `{'used_slots': 8, 'total_slots': 7}` | ordinary | raise exactly `ValueError` |
| D-PY-H01 | `{'used_slots': True, 'total_slots': 5}` | held | raise exactly `ValueError` |
| D-PY-H02 | `{'used_slots': False, 'total_slots': 5}` | held | raise exactly `ValueError` |
| D-PY-H03 | `{'used_slots': 0, 'total_slots': True}` | held | raise exactly `ValueError` |
| D-PY-H04 | `{'used_slots': 0, 'total_slots': False}` | held | raise exactly `ValueError` |

## SQLite cold target

```text
You are writing one SQLite query.

Database:
CREATE TABLE volumes(id INTEGER PRIMARY KEY, title TEXT NOT NULL);
CREATE TABLE loans(id INTEGER PRIMARY KEY, volume_id INTEGER);

Question: return titles of volumes that have never been loaned, ordered by title.

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence.
```

| Test id | Inserts | Class | Expected rows |
| --- | --- | --- | --- |
| C-Q-O01 | `INSERT INTO volumes VALUES (1,'fjord'),(2,'grove'),(3,'heath'); INSERT INTO loans VALUES (10,1);` | ordinary | `(('grove',), ('heath',))` |
| C-Q-O02 | `INSERT INTO volumes VALUES (5,'mire'),(8,'nook'),(9,'orchard'); INSERT INTO loans VALUES (20,8),(21,9);` | ordinary | `(('mire',),)` |
| C-Q-H01 | `INSERT INTO volumes VALUES (11,'pearl'),(12,'quill'),(13,'rune'); INSERT INTO loans VALUES (30,12),(31,NULL);` | held | `(('pearl',), ('rune',))` |
| C-Q-H02 | `INSERT INTO volumes VALUES (21,'tarn'),(22,'umber'),(23,'vale'),(24,'wold'); INSERT INTO loans VALUES (40,22),(41,NULL),(42,24);` | held | `(('tarn',), ('vale',))` |

## SQLite direct-rule target

```text
You are writing one SQLite query.

Database:
CREATE TABLE depots(id INTEGER PRIMARY KEY, code TEXT NOT NULL);
CREATE TABLE shipments(id INTEGER PRIMARY KEY, depot_id INTEGER);

Question: return codes of depots with no shipment, ordered by code. A NULL shipment depot does not identify any depot and must not remove unrelated rows. Express absence with a correlated NOT EXISTS condition.

Return exactly one SQLite SELECT statement. A single trailing semicolon is allowed. Return no prose and no Markdown fence.
```

| Test id | Inserts | Class | Expected rows |
| --- | --- | --- | --- |
| D-Q-O01 | `INSERT INTO depots VALUES (2,'ax'),(4,'by'); INSERT INTO shipments VALUES (10,2);` | ordinary | `(('by',),)` |
| D-Q-O02 | `INSERT INTO depots VALUES (6,'cz'),(7,'du'),(9,'ev'); INSERT INTO shipments VALUES (20,7);` | ordinary | `(('cz',), ('ev',))` |
| D-Q-H01 | `INSERT INTO depots VALUES (12,'fw'),(13,'gx'); INSERT INTO shipments VALUES (30,NULL),(31,12);` | held | `(('gx',),)` |
| D-Q-H02 | `INSERT INTO depots VALUES (30,'hy'),(31,'iz'),(32,'ja'),(33,'kb'); INSERT INTO shipments VALUES (40,31),(41,NULL),(42,33);` | held | `(('hy',), ('ja',))` |

## Mechanical labels

For Python, test ids ending in `-O` plus digits are ordinary and ids ending in
`-H` plus digits are held. For SQLite, the table's `Class` column is normative.
The runner stores the class on every executable vector and does not infer it
from a legacy id prefix.

A Python call is:

- `gate_fail` if its source refuses or evaluation cannot produce every result;
- `ordinary_fail` if any ordinary vector fails, or if a held vector fails by
  timeout, crash, mutation, output, wrong exception, or any behavior other than
  the named normal return;
- `boundary_miss` if every ordinary vector passes, every held vector either
  passes or returns normally, and at least one held vector returns normally;
  or
- `full_pass` if every ordinary and held vector passes.

SQLite uses the corresponding inherited rule: ordinary correctness is
required; a qualified held miss is an executed wrong result rather than an
error. Family and terminal classification remain exactly as stated in the
successor charter and first admission charter.

## Exact logical-call order

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

Each anchor must pass before the next call. An anchor failure stops the packet.
If all anchors pass, every target call runs in the listed order. Each condition
repeats the same exact prompt. The maximum is sixteen logical calls, plus at
most one linked retry for each logical call whose first server response
contains no model output.
