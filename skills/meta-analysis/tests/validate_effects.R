#!/usr/bin/env Rscript
# Validate effect size computation and pooling against the BCG vaccine dataset.
#
# dat.bcg is the canonical binary-outcome meta-analysis benchmark: 13 trials of
# BCG vaccine against tuberculosis. Values asserted here were measured by
# running metafor, not taken from a textbook.
#
# Expected runtime: under 10 seconds. No downloads.
# Requirements: metafor, metadat

suppressPackageStartupMessages({
  library(metafor)
  library(metadat)
})

cat("=== Effect Size and Pooling Validation (BCG) ===\n\n")
pass <- 0; fail <- 0

check <- function(name, condition) {
  if (isTRUE(condition)) {
    cat(sprintf("  PASS: %s\n", name)); pass <<- pass + 1
  } else {
    cat(sprintf("  FAIL: %s\n", name)); fail <<- fail + 1
  }
}

cat(sprintf("  metafor %s, metadat %s\n\n",
            packageVersion("metafor"), packageVersion("metadat")))

# --- Dataset integrity ---
data(dat.bcg, package = "metadat")
check("dat.bcg has 13 trials", nrow(dat.bcg) == 13)
check("2x2 columns present",
      all(c("tpos", "tneg", "cpos", "cneg") %in% names(dat.bcg)))
check("No missing cell counts",
      !any(is.na(dat.bcg[, c("tpos", "tneg", "cpos", "cneg")])))

# --- escalc ---
dat <- escalc(measure = "RR", ai = tpos, bi = tneg, ci = cpos, di = cneg,
              data = dat.bcg)

check("yi computed for every trial", sum(!is.na(dat$yi)) == 13)
check("vi computed for every trial", sum(!is.na(dat$vi)) == 13)
check("All sampling variances positive", all(dat$vi > 0))

# RR is returned on the log scale. A value near 0 means no effect, not RR = 0.
cat(sprintf("  log RR range: %.3f to %.3f\n", min(dat$yi), max(dat$yi)))
check("yi is on the log scale (range within +/- 3)", all(abs(dat$yi) < 3))

# Hand-check trial 1 against the 2x2 table
manual <- log((dat.bcg$tpos[1] / (dat.bcg$tpos[1] + dat.bcg$tneg[1])) /
              (dat.bcg$cpos[1] / (dat.bcg$cpos[1] + dat.bcg$cneg[1])))
check("yi[1] matches hand-computed log RR", abs(dat$yi[1] - manual) < 1e-8)

# --- Random-effects model ---
res <- rma(yi, vi, data = dat, method = "REML")

cat(sprintf("\n  Pooled log RR : %.4f  (RR %.4f)\n", coef(res), exp(coef(res))))
cat(sprintf("  95%% CI        : %.4f to %.4f\n", res$ci.lb, res$ci.ub))

check("Pooled log RR is -0.7145", abs(coef(res) - (-0.7145)) < 1e-3)
check("Pooled RR is ~0.49 (BCG is protective)", abs(exp(coef(res)) - 0.4894) < 1e-3)
check("CI lower bound -1.0669", abs(res$ci.lb - (-1.0669)) < 1e-3)
check("CI upper bound -0.3622", abs(res$ci.ub - (-0.3622)) < 1e-3)
check("CI excludes the null", res$ci.ub < 0)
check("k equals 13", res$k == 13)
check("REML is the default method", res$method == "REML")

# --- Equal-effects vs fixed-effects: identical numbers, different claims ---
ee <- rma(yi, vi, data = dat, method = "EE")
fe <- rma(yi, vi, data = dat, method = "FE")

cat(sprintf("\n  EE estimate: %.6f\n  FE estimate: %.6f\n", coef(ee), coef(fe)))
check("EE and FE give identical estimates", abs(coef(ee) - coef(fe)) < 1e-12)
check("EE and FE give identical standard errors", abs(ee$se - fe$se) < 1e-12)
check("EE tau^2 is exactly zero", ee$tau2 == 0)
# They differ only in what may be claimed from them, which no test can check.

check("Random-effects estimate differs from equal-effects",
      abs(coef(res) - coef(ee)) > 1e-3)

# --- Ratio measures are pooled on the log scale ---
# Pooling raw ratios instead would give a different, wrong answer.
raw_mean <- mean(exp(dat$yi))
check("Back-transformed pooled RR differs from the mean of raw RRs",
      abs(exp(coef(res)) - raw_mean) > 0.01)
cat(sprintf("  exp(pooled log RR) = %.4f vs mean of raw RRs = %.4f\n",
            exp(coef(res)), raw_mean))

# --- metafor 4.x / 5.x boundary for ROM ---
# 5.0 applies a second-order Taylor bias correction to ROM by default.
# 4.x accepts correct= but does not apply it to ROM. This detects which you have.
cat("\n  metafor version boundary (ROM bias correction):\n")
data(dat.normand1999, package = "metadat")
romT <- escalc(measure = "ROM", m1i = m1i, sd1i = sd1i, n1i = n1i,
               m2i = m2i, sd2i = sd2i, n2i = n2i,
               data = dat.normand1999, correct = TRUE)
romF <- escalc(measure = "ROM", m1i = m1i, sd1i = sd1i, n1i = n1i,
               m2i = m2i, sd2i = sd2i, n2i = n2i,
               data = dat.normand1999, correct = FALSE)
differs <- !isTRUE(all.equal(romT$yi, romF$yi))
mfv <- packageVersion("metafor")

cat(sprintf("    correct=TRUE and correct=FALSE differ: %s\n", differs))
if (mfv >= "5.0-0") {
  check("metafor >= 5.0 applies ROM bias correction (TRUE != FALSE)", differs)
} else {
  check("metafor < 5.0 does not apply correction to ROM (TRUE == FALSE)", !differs)
  cat("    NOTE: on metafor >= 5.0 these diverge. A ROM meta-analysis run on 4.x\n")
  cat("          will not reproduce on 5.x at the default. Pin the version.\n")
}

cat(sprintf("\n=== Effects: %d passed, %d failed ===\n", pass, fail))
if (fail > 0) quit(status = 1)
