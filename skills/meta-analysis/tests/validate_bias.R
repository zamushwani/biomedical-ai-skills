#!/usr/bin/env Rscript
# Validate small-study effect tests and sensitivity diagnostics.
#
# Checks that Egger's test runs and is interpreted with k in view, that
# trim-and-fill attenuates the estimate rather than confirming suppression,
# and that leave-one-out reports a range rather than a single number.
#
# Expected runtime: under 15 seconds. No downloads.
# Requirements: metafor, metadat

suppressPackageStartupMessages({
  library(metafor)
  library(metadat)
})

cat("=== Small-Study Effects and Sensitivity Validation (BCG) ===\n\n")
pass <- 0; fail <- 0

check <- function(name, condition) {
  if (isTRUE(condition)) {
    cat(sprintf("  PASS: %s\n", name)); pass <<- pass + 1
  } else {
    cat(sprintf("  FAIL: %s\n", name)); fail <<- fail + 1
  }
}

data(dat.bcg, package = "metadat")
dat <- escalc(measure = "RR", ai = tpos, bi = tneg, ci = cpos, di = cneg,
              data = dat.bcg)
res <- rma(yi, vi, data = dat, method = "REML")

# --- The k >= 10 gate ---
cat(sprintf("  k = %d\n", res$k))
check("k >= 10, so an asymmetry test is defensible here", res$k >= 10)

# With fewer than 10 studies the test should not be run at all. Demonstrate
# that it still returns a number, which is exactly why the rule is needed.
small <- rma(yi, vi, data = dat[1:6, ], method = "REML")
rt_small <- regtest(small, model = "lm")
cat(sprintf("  On k=6 the test still returns p = %.4f (it should not be used)\n",
            rt_small$pval))
check("Egger's test runs on k=6 without complaint (hence the manual rule)",
      is.numeric(rt_small$pval))

# --- Egger's regression test ---
rt <- regtest(res, model = "lm")
cat(sprintf("\n  Egger's test: statistic %.4f, p = %.4f\n", rt$zval, rt$pval))

check("Egger statistic is -1.4013", abs(rt$zval - (-1.4013)) < 1e-3)
check("Egger p-value is 0.1887", abs(rt$pval - 0.1887) < 1e-3)
check("No significant asymmetry detected in BCG", rt$pval > 0.05)

# A non-significant result is not evidence of no bias, only of no detected
# asymmetry. The test is underpowered even at k = 13.

# --- Rank correlation test, for comparison ---
rk <- ranktest(res)
cat(sprintf("  Begg's rank test: tau = %.4f, p = %.4f\n", rk$tau, rk$pval))
check("Rank test also non-significant here", rk$pval > 0.05)
check("The two tests agree in direction on this dataset",
      (rt$pval > 0.05) == (rk$pval > 0.05))

# --- Trim-and-fill ---
tf <- trimfill(res)
cat(sprintf("\n  trim-and-fill imputed %d studies\n", tf$k0))
cat(sprintf("  original estimate : %.4f\n", coef(res)))
cat(sprintf("  adjusted estimate : %.4f\n", coef(tf)))

check("trim-and-fill imputed 1 study", tf$k0 == 1)
check("Adjusted estimate is -0.6571", abs(coef(tf) - (-0.6571)) < 1e-3)
check("Adjustment attenuates toward the null", abs(coef(tf)) < abs(coef(res)))
check("Conclusion survives the adjustment", tf$ci.ub < 0)

# The imputed count is a mathematical construction that restores symmetry.
# It is not a count of suppressed trials, and this test asserts nothing of the kind.

# --- Leave-one-out ---
l1 <- leave1out(res)
lo <- min(l1$estimate); hi <- max(l1$estimate)
cat(sprintf("\n  leave-one-out estimates range: %.4f to %.4f\n", lo, hi))
cat(sprintf("  full-data estimate           : %.4f\n", coef(res)))

check("Leave-one-out minimum is -0.7948", abs(lo - (-0.7948)) < 1e-3)
check("Leave-one-out maximum is -0.6284", abs(hi - (-0.6284)) < 1e-3)
check("Full estimate lies inside the leave-one-out range",
      coef(res) >= lo && coef(res) <= hi)
check("No single study flips the direction of effect", hi < 0)
# leave1out() returns a list.rma, not a data.frame, so nrow() is NULL here
check("One leave-one-out fit per study", length(l1$estimate) == res$k)

# --- Influence diagnostics ---
inf <- influence(res)
cook <- inf$inf$cook.d
cat(sprintf("\n  Cook's distance: max %.4f at study %d\n", max(cook), which.max(cook)))
check("Cook's distance computed for every study", length(cook) == res$k)
check("Cook's distance is non-negative", all(cook >= 0))

# Being an outlier is not the same as being influential. A small outlier moves
# nothing. The Baujat plot separates the two, which is why the skill recommends it.

cat(sprintf("\n=== Bias and sensitivity: %d passed, %d failed ===\n", pass, fail))
if (fail > 0) quit(status = 1)
