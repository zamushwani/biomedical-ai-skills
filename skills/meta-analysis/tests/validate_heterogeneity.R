#!/usr/bin/env Rscript
# Validate heterogeneity quantification and the choices that change intervals.
#
# Demonstrates three things the skill claims:
#   REML and DerSimonian-Laird give different tau^2
#   Knapp-Hartung widens the confidence interval
#   The prediction interval can cross the null when the CI does not
#
# Expected runtime: under 10 seconds. No downloads.
# Requirements: metafor, metadat

suppressPackageStartupMessages({
  library(metafor)
  library(metadat)
})

cat("=== Heterogeneity Validation (BCG) ===\n\n")
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

# --- Q, tau^2, I^2 ---
cat(sprintf("  Q = %.2f on %d df, p = %.3g\n", res$QE, res$k - 1, res$QEp))
cat(sprintf("  tau^2 = %.4f\n", res$tau2))
cat(sprintf("  I^2   = %.2f%%\n", res$I2))

check("Q statistic is 152.23", abs(res$QE - 152.23) < 0.05)
check("Q has k-1 = 12 degrees of freedom", res$k - 1 == 12)
check("Q is highly significant", res$QEp < 1e-20)
check("tau^2 (REML) is 0.3132", abs(res$tau2 - 0.3132) < 1e-3)
check("I^2 is 92.2%", abs(res$I2 - 92.22) < 0.1)
check("I^2 is a percentage, not a proportion", res$I2 > 1 && res$I2 <= 100)

# --- tau^2 estimator changes the answer ---
tau_reml <- rma(yi, vi, data = dat, method = "REML")$tau2
tau_dl   <- rma(yi, vi, data = dat, method = "DL")$tau2
tau_pm   <- rma(yi, vi, data = dat, method = "PM")$tau2

cat(sprintf("\n  tau^2 by estimator: REML %.4f | DL %.4f | PM %.4f\n",
            tau_reml, tau_dl, tau_pm))
check("REML and DL give different tau^2", abs(tau_reml - tau_dl) > 1e-4)
check("tau^2 (DL) is 0.3088", abs(tau_dl - 0.3088) < 1e-3)
check("All estimators agree the heterogeneity is substantial",
      all(c(tau_reml, tau_dl, tau_pm) > 0.2))

# --- Knapp-Hartung widens the interval ---
res_z    <- rma(yi, vi, data = dat, method = "REML", test = "z")
res_knha <- rma(yi, vi, data = dat, method = "REML", test = "knha")

w_z    <- res_z$ci.ub - res_z$ci.lb
w_knha <- res_knha$ci.ub - res_knha$ci.lb

cat(sprintf("\n  CI width, test='z'    : %.4f  (%.4f to %.4f)\n",
            w_z, res_z$ci.lb, res_z$ci.ub))
cat(sprintf("  CI width, test='knha' : %.4f  (%.4f to %.4f)\n",
            w_knha, res_knha$ci.lb, res_knha$ci.ub))

check("test='z' is the default", res$test == "z")
check("Knapp-Hartung widens the CI", w_knha > w_z)
check("KNHA CI width is 0.7878", abs(w_knha - 0.7878) < 1e-3)
check("Both intervals still exclude the null here", res_knha$ci.ub < 0 && res_z$ci.ub < 0)

# The point estimate is unchanged; only the uncertainty around it moves.
check("KNHA does not change the point estimate",
      abs(coef(res_knha) - coef(res_z)) < 1e-10)

# --- Prediction interval vs confidence interval ---
p <- predict(res)
cat(sprintf("\n  Confidence interval: %.4f to %.4f\n", res$ci.lb, res$ci.ub))
cat(sprintf("  Prediction interval: %.4f to %.4f\n", p$pi.lb, p$pi.ub))

check("Prediction interval is wider than the CI",
      (p$pi.ub - p$pi.lb) > (res$ci.ub - res$ci.lb))
check("Prediction interval lower bound -1.8667", abs(p$pi.lb - (-1.8667)) < 1e-3)
check("Prediction interval upper bound 0.4376", abs(p$pi.ub - 0.4376) < 1e-3)

# This is the whole argument for reporting prediction intervals: the average
# effect is clearly protective, yet a new trial could plausibly show no benefit.
check("CI excludes the null but the prediction interval does NOT",
      res$ci.ub < 0 && p$pi.ub > 0)
cat("    -> average effect is protective; a NEW trial could still show no benefit\n")

# --- I^2 depends on precision, not only on tau^2 ---
# Inflating the sample sizes shrinks sampling error, so I^2 rises even though
# the true between-study variance is unchanged.
dat_precise <- dat
dat_precise$vi <- dat$vi / 4          # as if each trial were 4x larger
res_precise <- rma(yi, vi, data = dat_precise, method = "REML")

cat(sprintf("\n  I^2 original: %.1f%%   I^2 with 4x precision: %.1f%%\n",
            res$I2, res_precise$I2))
check("I^2 increases when studies get more precise", res_precise$I2 > res$I2)
cat("    -> I^2 is a proportion of variability, not an amount of heterogeneity\n")

cat(sprintf("\n=== Heterogeneity: %d passed, %d failed ===\n", pass, fail))
if (fail > 0) quit(status = 1)
