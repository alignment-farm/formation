# Exploratory accumulation of two staged tables

## Main result

Both lessons remained available after sequential acquisition, but the model did
not reliably select between them when both tables were delivered in one list.

All eight observations and tables were exact. When the external family check
delivered only the matching table, later calls made 44 of 48 matching actions:
23 of 24 on the first-acquired family and 21 of 24 on the second. Unrelated
action matched cold at 24 of 24.

When both tables were delivered together, later calls made 36 of 48 matching
actions. They made all 24 actions for family A but only 12 of 24 for family B.
The supplied exact joint control produced the identical 24-to-12 split. This
points to joint-container selection, not bad model-written lessons.

The frozen accumulation verdict is null because joint authored delivery needed
at least 40 matching actions and at least 19 for each family. It scored 36 and
only 12 for family B. Gated authored delivery also missed its upward floor by
one action, scoring 20 of 24 instead of 21.

## What was tested

Four independent lineages each acquired two controller families in sequence.
The families used opposite hidden relations, and their relation assignment was
balanced across lineages. Family A was acquired first and family B second.

After both model-written tables existed, new devices required upward and
downward action in each family. New unrelated devices tested selectivity. The
comparison included cold action, both raw experiences, gated and joint authored
tables, first-only and second-only retention, and gated and joint supplied
tables.

In gated branches, the external exact-family check delivered one matching table
or nothing. In joint branches, both unchanged tables were placed in one ordered
list and the model had to select the matching family.

## Results

| Later information | Matching actions | Unrelated actions |
| --- | ---: | ---: |
| No retained information | 24/48 | 24/24 |
| Both raw experiences | 26/48 | 24/24 |
| Both authored tables with family gate | 44/48 | 24/24 |
| Both authored tables together | 36/48 | 12/24 |
| First table only | 35/48 | 24/24 |
| Second table only | 33/48 | 24/24 |
| Both supplied exact tables together | 36/48 | 12/24 |
| Both supplied exact tables with family gate | 45/48 | 24/24 |

The gated authored branch made all 24 downward actions and 20 of 24 upward
actions. The joint authored branch split evenly by direction at 18 of 24, but
its family split was stark: 24 of 24 for A and 12 of 24 for B.

## What this supports

This run supports bounded coexistence in storage. Acquiring family B did not
erase family A, and the external gate could still deliver either exact table.
It does not support model-side selection from the tested joint list.

Because supplied exact tables failed in the same way, the joint failure does
not come from model authorship. The ordered list placed A before B in every
request. A small interface diagnostic should reverse that order and compare a
container keyed directly by controller family. If the favored family follows
list position, the problem is order. If a keyed container repairs both
families, it becomes a better substrate for accumulated lessons.

This remains retrieval-like scoped persistence in one artificial domain. It
does not establish general composition, net value, or Formation.

## Audit details

- Model: `ai/qwen3:14B-Q6_K`
- Model digest: `sha256:2853c9d6ea67819135d15d12d6d9d02eb8932ac56cb1531bd52aa0816075c219`
- Logical calls: 600
- Physical attempts: 600
- Retries: 0
- Frozen specification SHA-256: `586331996d6da4340e2c5c7f24c9ef00ea0baeff036f9dd40b5107762177bd78`
- Specimen SHA-256: `9368cbd51181ee400d8da9e6218ee4d2745b8099203e959a460be82b1d673945`
- Packet SHA-256: `c9c12ca3ef2db355bc6832d76db390657179579ca305f945f9949456c11381ab`
- Frozen accumulation verdict: `null`
- Formation verdict: `null`
- Replay: exact from retained request and response bytes

The computed record is [packet.json](packet.json). The frozen lineages are in
[specimen.json](specimen.json). The exact provider identity is in
[provider.json](provider.json). Every raw request and response is retained under
`attempts/`.
