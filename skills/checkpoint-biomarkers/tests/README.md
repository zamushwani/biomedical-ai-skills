# Validation Tests

The central scoring claim is that a mean-of-z signature is defined relative to whatever cohort was present when it was computed. This measures that drift directly.

**Executed 2026-08-30: 9 assertions, 0 failures** (Python 3.13.5, numpy). Synthetic data, fixed seed, no download.

```bash
cd skills/checkpoint-biomarkers/tests && python run_all.py
```

## Measured

Scores for the **same first 20 samples**, after adding 10 more:

| Scoring method | max \|change\| |
|---|---|
| mean-of-z | **0.5285** |
| rank-based single-sample | **0.0000** |

Recomputing a mean-of-z signature after accrual silently rewrites every earlier sample's score. A rank-based single-sample score is exactly stable.

The suite also asserts the skill keeps its central corrections intact: that CPS/TPS cannot be computed from expression, that the four PD-L1 clones are named, that the GSVA parameter-object API is recorded, that assay-derived and expression-derived biomarkers stay separated, and that MSI requires loci examined alongside the percentage.

## Requirements

`numpy`. Skips cleanly without it.
