# Validation Tests

No package implements RSI, so the model in `SKILL.md` *is* the specification. These checks confirm the gene list and coefficients, and demonstrate the two errors that produce a wrong score without erroring.

**Executed 2026-08-30: 11 assertions, 0 failures** (Python 3.13.5, numpy). Synthetic data, fixed seed, no download.

```bash
cd skills/radiotherapy-response/tests && python run_all.py
```

## Measured

| Rank basis | Value range | RSI sd |
|---|---|---|
| full transcriptome (correct) | 20 – 19,980 | **719.6** |
| within the ten genes (wrong) | 1 – 10 | **0.39** |

Ranking within the ten genes gives every sample exactly `{1..10}` and collapses between-sample variance by **~1,800×** — while still returning a plausible-looking number. That is why the check exists.

The suite also confirms `ABL1` carries the largest positive weight and `IRF1` the largest negative, that all ten coefficients appear in the skill, and that the direction (higher = more resistant) and the missing-gene rule are both documented.

## Requirements

`numpy`. Skips cleanly without it.
