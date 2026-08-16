# Validation Tests

Tests run on simulated dose-response and prediction problems with a known ground truth, so no PharmacoSet download (multi-gigabyte) is needed. The curve test additionally cross-checks against `drc` and `nplr` when they are installed.

**Executed 2026-08-16** on R 4.5.1 with drc 3.0.1, nplr 0.1.8, glmnet 4.1.10: **22 assertions, 0 failures.**

## Running

```bash
cd skills/drug-response/tests
Rscript run_all.R              # all tests, under 3 min
Rscript run_all.R curves       # 4PL, IC50 vs AUC, drc convergence
Rscript run_all.R prediction   # feature leakage, tissue confounding
```

Run from the `tests/` directory so `run_all.R` can find the scripts.

## What each test checks

**curves** (16 assertions). Builds 4PL curves with known parameters. Confirms a plateauing curve (never below 60% viability) has **no IC50 by observation** — the function returns NA rather than a number — while AUC is defined for both, and AAC = 1 − AUC. When `drc` is installed it fits the real 4PL, verifies the convergence flag is a **logical** (`TRUE` = converged, not the optim `== 0` convention), and shows `drc` will still return an ED50 of 0.278 for the plateau curve whose lower asymptote is 62.8% — an extrapolation, not a measurement.

**prediction** (6 assertions). Simulates a response driven by only 5 of 800 genes. Selecting features on the full data before cross-validating reports r ≈ 0.82; nested selection inside each fold reports r ≈ 0.35 on the same data. Then a lineage-confounded response: random-fold CV reports r ≈ 0.95 while leave-lineage-out collapses to a negative correlation, because the model was memorizing per-lineage offsets rather than learning drug-specific signal.

## Requirements

```r
install.packages("glmnet")            # required (prediction)
install.packages(c("drc", "nplr"))    # optional (strengthens curves)
```

No internet access is needed at run time.

## Expected values

Curve values are deterministic. Prediction correlations are seed-dependent, so the suite asserts the direction and a substantial gap, not exact numbers.

### Curves

| Quantity | Value |
|---|---|
| Responsive IC50 (observed) | 0.5933 µM (true ec50 0.5) |
| Plateau IC50 (observed) | **NA — undefined** |
| Responsive / plateau AUC | 0.7064 / 0.8475 |
| drc convergence flag | `TRUE` (logical) |
| drc ED50, responsive | 0.4341, CI [0.367, 0.501] |
| drc ED50, plateau (extrapolated) | 0.278, lower asymptote 62.8% |
| nplr IC50 | 0.5114 |

### Prediction

| Comparison | Typical value |
|---|---|
| Feature leakage: select-then-CV r | ~0.82 |
| Feature leakage: nested-CV r | ~0.35 |
| Confounding: random-fold r | ~0.95 |
| Confounding: leave-lineage-out r | ~ −0.84 |

## Notes

- **`drc` convergence is a logical, not an integer.** `fit$fit$convergence` is `TRUE` when the fit converged. Checking `== 0` (the optim convention) is wrong and returns `FALSE` for a good fit. Use `isTRUE(fit$fit$convergence)`. This test exists partly because the earlier skill text used the wrong check.
- **`drc` extrapolates an IC50 for curves that never reach 50% inhibition.** It returned ED50 = 0.278 for a curve plateauing at 62.8% viability. That number is not a measurement; report AUC.
- **The prediction test uses simulation, not a public panel,** because the point is a controlled ground truth. A real PharmacoSet would need PharmacoGx plus a multi-gigabyte download; the traps demonstrated here are properties of the cross-validation scheme, not of any particular dataset.
