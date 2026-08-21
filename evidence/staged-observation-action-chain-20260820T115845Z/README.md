# The staged chain worked, but one raw-history cell kept the verdict null

## Main point

Both fresh model-written observations were correct. Both staged effect tables
were correct. Gated delivery then produced all 16 correct matching actions and
preserved all 32 unrelated actions.

Cold action, direct table authorship, and removal of the staged table produced
none of the 16 matching actions. Raw experience produced 4 of 16 by solving one
downward cell in one world. The frozen scorer required staged delivery to beat
raw experience in every cell, so the chain verdict is null.

Ungated staged delivery harmed unrelated behavior. The family gate prevented
21 wrong actions across the eight unrelated cells.

This is repeated candidate evidence, not a passed validation or Formation
finding.

## Results

| Later history | Correct matching actions |
| --- | ---: |
| Cold | 0/16 |
| Raw experience | 4/16 |
| Direct authored table | 0/16 |
| Staged authored table, gated | 16/16 |
| Staged table removed | 0/16 |
| Staged authored table, ungated | 16/16 |
| Supplied correct table, gated | 16/16 |

Both staged observations and both staged tables were exact. Direct raw
authorship wrote the opposite table in both worlds.

## Next step

A fresh validation will add more source worlds and a staged author who does not
see the consequence. Its transfer comparison will be frozen over all
prospective cases while still requiring success in both movement directions.
This tests whether the staged chain adds a broad effect beyond occasional raw
history success.

## Audit details

- Specification:
  [STAGED_OBSERVATION_ACTION_CHAIN.md](../../docs/STAGED_OBSERVATION_ACTION_CHAIN.md)
- Model: `ai/qwen3:14B-Q6_K`
- Logical calls: 344/344
- Physical attempts: 344/352
- Retries: 0
- Chain verdict: null
- Formation verdict: null

The runner replayed the packet from all raw requests and responses.
