# A model-written observation repaired table authorship

## Main point

One cold call first recorded the selected slot and movement. A second cold call
used that short observation to write the complete controller table.

All eight observations were correct. The staged author then wrote 24 correct
tables out of 24. Direct authorship from the raw result produced 9 of 24.
Removing the model-written observation produced none.

This selects staged authorship for a fresh end-to-end action experiment. It
does not yet show transfer or Formation.

## Scorer correction

The runner initially reported `not_engaged` even though the model had written
all eight observations correctly. The scorer generated JSON keys in sorted
order instead of the order frozen in the prompt. It also misspelled
`decreases_position` in its expected value.

The original packet is preserved as `packet.pre-correction.json`. The scorer
was repaired to match the frozen specification, and `packet.corrected.json`
was rebuilt from the same 88 retained requests and responses. No model call was
added. `correction.json` records both packet hashes and the reason.

## Comparison

Eight fresh experiences selected the first slot three times and the second slot
five times. Three final-table conditions were repeated three times:

| Condition | Correct tables |
| --- | ---: |
| Model-written observation, then table | 24/24 |
| Directly from raw action and result | 9/24 |
| Observation removed | 0/24 |

The staged process was correct in every family. Direct authorship failed on all
five second-slot experiences and on two first-slot experiences.

## Next step

The next experiment reconnects this writing process to later action. It will
compare staged delivery with cold action, raw experience, direct authorship,
removal of the staged table, ungated delivery, and a supplied correct lesson.
The family gate must preserve unrelated behavior.

## Audit details

- Frozen specification:
  [STAGED_OBSERVATION_AUTHORSHIP.md](../../docs/STAGED_OBSERVATION_AUTHORSHIP.md)
- Model: `ai/qwen3:14B-Q6_K`
- Logical calls: 88/88
- Physical attempts: 88/96
- Retries: 0
- Original packet SHA-256:
  `f01357b267920ad683c43c11b6093c51819eece6df84ce28dbcb64add9a2982d`
- Corrected packet SHA-256:
  `96e934d3fe76a390a3366be0aedff2c226a0e17871a9842d110485269a853c1e`
- Corrected verdict: `candidate_found`
- Formation verdict: null
