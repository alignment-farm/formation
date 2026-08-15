# Normative vectors for strict Python boundary contact

Status: **pre-contact normative appendix; runner must reproduce exactly**.

These are the complete executable vectors for
[the Python boundary contact](PYTHON_BOUNDARY_CONTACT_CHARTER.md). Table order is
test-report order. Python literal spelling is the required `input_repr`.

Every vector runs in a fresh process. Before the call, the harness deep-copies
the input using its own trusted encoder. After the call or exception, any change
to the participant input sets `mutated: true` and fails the vector. A returned
value passes only when its exact type and value match the listed return. A
refusal passes only when the function raises exactly `ValueError`.

## Exploration: `parse_limits`

| Test id | Input | Expected |
| --- | --- | --- |
| E-O01 | `{'soft': 0, 'hard': 3}` | return `(0, 3)` |
| E-O02 | `{'soft': 2, 'hard': 2}` | return `(2, 2)` |
| E-O03 | `None` | raise `ValueError` |
| E-O04 | `[0, 3]` | raise `ValueError` |
| E-O05 | `(0, 3)` | raise `ValueError` |
| E-O06 | `'x'` | raise `ValueError` |
| E-O07 | `{}` | raise `ValueError` |
| E-O08 | `{'soft': 0}` | raise `ValueError` |
| E-O09 | `{'hard': 3}` | raise `ValueError` |
| E-O10 | `{'soft': 0, 'hard': 3, 'mode': 'x'}` | raise `ValueError` |
| E-O11 | `{'soft': '0', 'hard': 3}` | raise `ValueError` |
| E-O12 | `{'soft': 0.0, 'hard': 3}` | raise `ValueError` |
| E-O13 | `{'soft': None, 'hard': 3}` | raise `ValueError` |
| E-O14 | `{'soft': [0], 'hard': 3}` | raise `ValueError` |
| E-O15 | `{'soft': 0, 'hard': '3'}` | raise `ValueError` |
| E-O16 | `{'soft': 0, 'hard': 3.0}` | raise `ValueError` |
| E-O17 | `{'soft': 0, 'hard': None}` | raise `ValueError` |
| E-O18 | `{'soft': 0, 'hard': [3]}` | raise `ValueError` |
| E-O19 | `{'soft': -1, 'hard': 3}` | raise `ValueError` |
| E-O20 | `{'soft': 0, 'hard': -1}` | raise `ValueError` |
| E-O21 | `{'soft': 4, 'hard': 3}` | raise `ValueError` |
| E-H01 | `{'soft': True, 'hard': 3}` | raise `ValueError` |
| E-H02 | `{'soft': 0, 'hard': False}` | raise `ValueError` |
| E-H03 | `{'soft': False, 'hard': True}` | raise `ValueError` |

Engagement ordinary tests are E-O01 through E-O21. Held tests are E-H01 through
E-H03.

## V1: `parse_revisions`

| Test id | Input | Expected |
| --- | --- | --- |
| V1-01 | `{'artifact_revision': 0, 'authority_revision': 3}` | return `(0, 3)` |
| V1-02 | `{'artifact_revision': 8, 'authority_revision': 8}` | return `(8, 8)` |
| V1-03 | `None` | raise `ValueError` |
| V1-04 | `[0, 3]` | raise `ValueError` |
| V1-05 | `{}` | raise `ValueError` |
| V1-06 | `{'artifact_revision': 0}` | raise `ValueError` |
| V1-07 | `{'authority_revision': 3}` | raise `ValueError` |
| V1-08 | `{'artifact_revision': 0, 'authority_revision': 3, 'source': 'x'}` | raise `ValueError` |
| V1-09 | `{'artifact_revision': '0', 'authority_revision': 3}` | raise `ValueError` |
| V1-10 | `{'artifact_revision': 0, 'authority_revision': 3.0}` | raise `ValueError` |
| V1-11 | `{'artifact_revision': None, 'authority_revision': 3}` | raise `ValueError` |
| V1-12 | `{'artifact_revision': 0, 'authority_revision': [3]}` | raise `ValueError` |
| V1-13 | `{'artifact_revision': -1, 'authority_revision': 3}` | raise `ValueError` |
| V1-14 | `{'artifact_revision': 0, 'authority_revision': -1}` | raise `ValueError` |
| V1-15 | `{'artifact_revision': True, 'authority_revision': 3}` | raise `ValueError` |
| V1-16 | `{'artifact_revision': 0, 'authority_revision': False}` | raise `ValueError` |
| V1-17 | `{'artifact_revision': False, 'authority_revision': 3}` | raise `ValueError` |
| V1-18 | `{'artifact_revision': 0, 'authority_revision': True}` | raise `ValueError` |

## V2: `parse_window`

| Test id | Input | Expected |
| --- | --- | --- |
| V2-01 | `[0, 3]` | return `(0, 3)` |
| V2-02 | `[2, 2]` | return `(2, 2)` |
| V2-03 | `None` | raise `ValueError` |
| V2-04 | `(0, 3)` | raise `ValueError` |
| V2-05 | `{'low': 0, 'high': 3}` | raise `ValueError` |
| V2-06 | `[]` | raise `ValueError` |
| V2-07 | `[1]` | raise `ValueError` |
| V2-08 | `[1, 2, 3]` | raise `ValueError` |
| V2-09 | `['0', 3]` | raise `ValueError` |
| V2-10 | `[0.0, 3]` | raise `ValueError` |
| V2-11 | `[None, 3]` | raise `ValueError` |
| V2-12 | `[0, '3']` | raise `ValueError` |
| V2-13 | `[0, 3.0]` | raise `ValueError` |
| V2-14 | `[0, None]` | raise `ValueError` |
| V2-15 | `[4, 3]` | raise `ValueError` |
| V2-16 | `[True, 3]` | raise `ValueError` |
| V2-17 | `[0, False]` | raise `ValueError` |
| V2-18 | `[False, 3]` | raise `ValueError` |
| V2-19 | `[0, True]` | raise `ValueError` |

## V3: `total_counts`

| Test id | Input | Expected |
| --- | --- | --- |
| V3-01 | `{'primary': 0, 'secondary': 3}` | return `3` |
| V3-02 | `{'primary': 2, 'secondary': 2}` | return `4` |
| V3-03 | `None` | raise `ValueError` |
| V3-04 | `[0, 3]` | raise `ValueError` |
| V3-05 | `{}` | raise `ValueError` |
| V3-06 | `{'primary': 0}` | raise `ValueError` |
| V3-07 | `{'secondary': 3}` | raise `ValueError` |
| V3-08 | `{'primary': 0, 'secondary': 3, 'other': 1}` | raise `ValueError` |
| V3-09 | `{'primary': '0', 'secondary': 3}` | raise `ValueError` |
| V3-10 | `{'primary': 0, 'secondary': 3.0}` | raise `ValueError` |
| V3-11 | `{'primary': None, 'secondary': 3}` | raise `ValueError` |
| V3-12 | `{'primary': 0, 'secondary': [3]}` | raise `ValueError` |
| V3-13 | `{'primary': -1, 'secondary': 3}` | raise `ValueError` |
| V3-14 | `{'primary': 0, 'secondary': -1}` | raise `ValueError` |
| V3-15 | `{'primary': True, 'secondary': 3}` | raise `ValueError` |
| V3-16 | `{'primary': 0, 'secondary': False}` | raise `ValueError` |
| V3-17 | `{'primary': False, 'secondary': 3}` | raise `ValueError` |
| V3-18 | `{'primary': 0, 'secondary': True}` | raise `ValueError` |

The exact return type for V3-01 and V3-02 is `int`, not `bool` or another
numeric type.

## N1: `parse_feature_flags`

| Test id | Input | Expected |
| --- | --- | --- |
| N1-01 | `{'audit': False, 'cache': False}` | return `(False, False)` |
| N1-02 | `{'audit': False, 'cache': True}` | return `(False, True)` |
| N1-03 | `{'audit': True, 'cache': False}` | return `(True, False)` |
| N1-04 | `{'audit': True, 'cache': True}` | return `(True, True)` |
| N1-05 | `None` | raise `ValueError` |
| N1-06 | `[False, True]` | raise `ValueError` |
| N1-07 | `{}` | raise `ValueError` |
| N1-08 | `{'audit': False}` | raise `ValueError` |
| N1-09 | `{'cache': True}` | raise `ValueError` |
| N1-10 | `{'audit': False, 'cache': True, 'other': False}` | raise `ValueError` |
| N1-11 | `{'audit': 0, 'cache': True}` | raise `ValueError` |
| N1-12 | `{'audit': 1, 'cache': True}` | raise `ValueError` |
| N1-13 | `{'audit': False, 'cache': 0}` | raise `ValueError` |
| N1-14 | `{'audit': False, 'cache': 1}` | raise `ValueError` |
| N1-15 | `{'audit': 'false', 'cache': True}` | raise `ValueError` |
| N1-16 | `{'audit': False, 'cache': None}` | raise `ValueError` |

## N2: `parse_gate`

| Test id | Input | Expected |
| --- | --- | --- |
| N2-01 | `(True, 0)` | return `(True, 0)` |
| N2-02 | `(False, 3)` | return `(False, 3)` |
| N2-03 | `None` | raise `ValueError` |
| N2-04 | `[True, 0]` | raise `ValueError` |
| N2-05 | `()` | raise `ValueError` |
| N2-06 | `(True,)` | raise `ValueError` |
| N2-07 | `(True, 0, 1)` | raise `ValueError` |
| N2-08 | `(0, 0)` | raise `ValueError` |
| N2-09 | `(1, 0)` | raise `ValueError` |
| N2-10 | `('true', 0)` | raise `ValueError` |
| N2-11 | `(None, 0)` | raise `ValueError` |
| N2-12 | `(True, True)` | raise `ValueError` |
| N2-13 | `(False, False)` | raise `ValueError` |
| N2-14 | `(True, '0')` | raise `ValueError` |
| N2-15 | `(True, 0.0)` | raise `ValueError` |
| N2-16 | `(True, None)` | raise `ValueError` |
| N2-17 | `(True, -1)` | raise `ValueError` |

## Report order and secrecy

Acquisition reports list E-O01 through E-O21, then E-H01 through E-H03. A raw
offer and lesson-authorship prompt may contain that complete report after
engagement. No V1, V2, V3, N1, or N2 vector or expected result may enter any
participant prompt. Validation reports remain evidence only and are never
offered to another validation call in this protocol.
