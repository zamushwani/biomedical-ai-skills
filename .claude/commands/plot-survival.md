---
description: Kaplan-Meier curves and Cox models from clinical data. Use when the user asks about survival, prognosis, hazard ratios, or wants a KM plot.
argument-hint: [clinical-file] [group-column]
allowed-tools: Read Grep Glob Bash(Rscript *)
---

Build survival analysis for `$0`, stratified by `$1`.

Follow the `survival-analysis` skill. The parts that are usually got wrong:

1. **Check the event coding.** `survival` expects 1 = event, 0 = censored. A flipped indicator silently inverts every conclusion.
2. **Test the proportional hazards assumption** with `cox.zph()` before reporting any hazard ratio. A violated PH assumption makes a single HR meaningless.
3. **Do not dichotomize a continuous variable at the median by reflex.** If you use an optimal cutpoint, correct for the multiple testing it induces.
4. **Report median survival with its CI, the number at risk, and the log-rank p** — a KM plot without a risk table is not interpretable.
5. **Use competing risks** (Fine-Gray or cumulative incidence) when death from other causes is common; a naive KM overestimates the event probability.

Report: median survival per group with CI, log-rank p, hazard ratio with CI, and the PH test result.

If `$0` is empty, ask which clinical table to use.
