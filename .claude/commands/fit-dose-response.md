---
description: Fit dose-response curves and compute IC50/AUC. Use when the user has viability data across drug concentrations, or asks about IC50, EC50, or drug sensitivity.
argument-hint: [data-file]
allowed-tools: Read Grep Glob Bash(Rscript *)
---

Fit dose-response curves for `$0`.

Follow the `drug-response` skill. The parts that are usually got wrong:

1. **Report AUC, not IC50, as the primary metric.** A drug that plateaus at 60% viability has *no* IC50 — pipelines substitute the maximum tested concentration, which is not a measurement. AUC is always defined and correlates better with clinical response.
2. **Check convergence.** `drc` stores it as a **logical** in `fit$fit$convergence` where `TRUE` means converged — not the optim `== 0` convention. Use `isTRUE(fit$fit$convergence)`.
3. **Fit on a log concentration scale** (`LL2.4`), since screens span orders of magnitude.
4. **Constrain the asymptotes.** Unconstrained fits produce negative viability or a 130% upper asymptote.
5. **Flag extrapolated IC50s.** `drc` will happily return an ED50 for a curve that never crosses 50% inhibition.

Report per curve: AUC, IC50 with CI (flagged if extrapolated), convergence status, and the fitted asymptotes.

If `$0` is empty, ask for the viability data.
