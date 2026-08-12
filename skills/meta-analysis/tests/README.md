# Validation Tests

Tests run the meta-analysis pipeline against datasets shipped with `metadat` and `netmeta`. Nothing is downloaded, so the suite completes in under a minute offline.

**Executed 2026-08-12** on R 4.5.1 with metafor 4.8.0, metadat 1.4.0, netmeta 3.2.0, meta 8.2.1: **81 assertions, 0 failures.**

## Running

```bash
Rscript run_all.R                 # all tests, under 1 minute
Rscript run_all.R effects         # effect sizes and pooling
Rscript run_all.R heterogeneity   # tau^2, I^2, Knapp-Hartung, prediction intervals
Rscript run_all.R bias            # Egger, trim-and-fill, leave-one-out, influence
Rscript run_all.R nma             # network meta-analysis
```

## What each test checks

**effects** (21 assertions). Verifies `escalc()` output against a hand-computed log risk ratio, then checks the pooled estimate. Asserts that `method="EE"` and `method="FE"` produce **identical** numbers, since they differ only in interpretation. Shows that back-transforming the pooled log RR (0.4894) is not the mean of the raw ratios (0.5937), which is why ratio measures are pooled on the log scale.

**heterogeneity** (19 assertions). Checks Q, tau², and I² against measured values, then demonstrates three claims from the skill: REML and DerSimonian-Laird give different tau²; Knapp-Hartung widens the interval without moving the point estimate; and **the prediction interval crosses zero while the confidence interval does not**. Finally it divides every sampling variance by 4 to show I² rising from 92.2% to 98.4% at unchanged between-study variance — I² is a proportion of variability, not an amount of heterogeneity.

**bias** (18 assertions). Runs Egger's regression and Begg's rank test, and deliberately runs Egger on a k=6 subset to show it returns a number regardless, which is why the k ≥ 10 rule has to be applied by hand. Confirms trim-and-fill attenuates the estimate toward the null rather than confirming suppression. Reports the leave-one-out range instead of a single estimate.

**nma** (23 assertions). Asserts `pairwise()` is exported by **meta** and *not* by netmeta. Confirms the Senn 2013 network is connected via `netconnection()`, and that degrees of freedom for Q are 18 rather than k−1 = 25, which is the multi-arm correlation being handled. Checks node-splitting, design-by-treatment decomposition, and P-score ranking.

## Requirements

```r
install.packages(c("metafor", "metadat", "netmeta", "meta"))
```

No internet access needed at run time.

## Expected values

Measured, not quoted from a textbook.

### BCG vaccine (`dat.bcg`, 13 trials)

| Quantity | Value |
|----------|-------|
| Pooled log RR (REML) | −0.7145 (RR 0.4894) |
| 95% CI | −1.0669 to −0.3622 |
| Prediction interval | −1.8667 to 0.4376 |
| tau² (REML) | 0.3132 |
| tau² (DL) | 0.3088 |
| I² | 92.22% |
| Q (df = 12) | 152.23, p ≈ 2e−26 |
| CI width, `test="z"` | 0.7047 |
| CI width, `test="knha"` | 0.7878 |
| Equal-effects estimate | −0.4303 |
| Egger's test | statistic −1.4013, p = 0.1887 |
| Begg's rank test | tau = 0.0256, p = 0.9524 |
| Trim-and-fill | 1 study imputed, estimate −0.6571 |
| Leave-one-out range | −0.7948 to −0.6284 |

### Senn 2013 network (`Senn2013`, 26 trials, 10 treatments)

| Quantity | Value |
|----------|-------|
| Pairwise comparisons (k) | 26 |
| Designs | 15 |
| Multi-arm trials | 1 (Willms1999) |
| df for Q | 18 (not k − 1 = 25) |
| tau | 0.3297 |
| I² | 81.4% |
| Comparisons with direct + indirect | 11 |
| Top 3 by P-score | rosi, metf, piog |
| Rosiglitazone vs placebo | −1.233 (SE 0.128) |

## Notes

- **Egger's test and Begg's test disagree sharply here** (p = 0.19 vs p = 0.95) on the same data. That is the documented weak-to-moderate agreement between asymmetry tests, and the reason one non-significant test is not reassurance.
- The **metafor version boundary is tested directly.** On metafor < 5.0, `escalc(measure="ROM", correct=TRUE)` and `correct=FALSE` return identical values; from 5.0 the second-order Taylor bias correction is applied by default and they diverge. The test asserts whichever behaviour matches the installed version and prints a warning about reproducibility across that boundary.
- `leave1out()` returns a `list.rma`, not a data frame, so `nrow()` is `NULL`. Use `length(x$estimate)`.
- Connectivity is not a field on the `netmeta` object. Use `netconnection()`.
