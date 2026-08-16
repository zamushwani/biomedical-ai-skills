#!/usr/bin/env Rscript
# Validate dose-response curve behaviour and the IC50-vs-AUC claim.
#
# Simulates 4PL curves with known parameters so the ground truth is exact,
# then checks the two things the skill asserts: a plateauing curve has no
# IC50 by observation, while AUC is always defined; and drc will silently
# extrapolate an IC50 beyond the biological range for such a curve.
#
# Cross-checks a base-R 4PL/AUC reimplementation against drc and nplr when
# they are installed, so the test runs anywhere but is stronger with them.
#
# Expected runtime: under 30 seconds. No downloads.
# Requirements: base R. Optional: drc, nplr (used if present).

cat("=== Dose-Response Curve Validation ===\n\n")
pass <- 0; fail <- 0

check <- function(name, condition) {
  if (isTRUE(condition)) {
    cat(sprintf("  PASS: %s\n", name)); pass <<- pass + 1
  } else {
    cat(sprintf("  FAIL: %s\n", name)); fail <<- fail + 1
  }
}

set.seed(1)

# Four-parameter log-logistic. Viability decreases with concentration.
fourpl <- function(x, lower, upper, ec50, slope) {
  lower + (upper - lower) / (1 + (x / ec50)^slope)
}

conc <- 10^seq(-3, 1, length.out = 9)   # 0.001 to 10 uM

# Responsive drug: viability falls to ~10%. Plateau drug: never below ~60%.
resp <- fourpl(conc, lower = 10, upper = 100, ec50 = 0.5, slope = 1.5)
plat <- fourpl(conc, lower = 60, upper = 100, ec50 = 0.3, slope = 1.5)

check("Responsive curve reaches below 50% viability", min(resp) < 50)
check("Plateau curve never reaches 50% viability", min(plat) > 50)
cat(sprintf("  responsive min viability: %.1f%%, plateau min: %.1f%%\n",
            min(resp), min(plat)))

# --- IC50 by observation ---
# A curve that never crosses 50% viability has no IC50. The honest answer is NA.
ic50_observed <- function(conc, viab) {
  if (min(viab) > 50) return(NA_real_)
  10^approx(x = viab, y = log10(conc), xout = 50, ties = mean)$y
}

ic50_resp <- ic50_observed(conc, resp)
ic50_plat <- ic50_observed(conc, plat)

cat(sprintf("\n  observed IC50: responsive %.4f uM, plateau %s\n",
            ic50_resp, ifelse(is.na(ic50_plat), "NA (undefined)", "defined")))
check("Responsive IC50 is near the true ec50 of 0.5", abs(ic50_resp - 0.5) < 0.2)
check("Plateau IC50 is undefined (NA), not a number", is.na(ic50_plat))

# --- AUC is always defined ---
auc_norm <- function(conc, viab) {
  lx <- log10(conc); v <- viab / 100
  sum(diff(lx) * (head(v, -1) + tail(v, -1)) / 2) / (max(lx) - min(lx))
}

auc_resp <- auc_norm(conc, resp)
auc_plat <- auc_norm(conc, plat)

cat(sprintf("  AUC: responsive %.4f, plateau %.4f\n", auc_resp, auc_plat))
check("AUC is defined for the responsive curve", is.finite(auc_resp))
check("AUC is defined for the plateau curve (where IC50 is not)", is.finite(auc_plat))
check("AUC lies in [0, 1]", auc_resp >= 0 && auc_resp <= 1)
check("The responsive drug is more potent (lower AUC)", auc_resp < auc_plat)

# --- AAC = 1 - AUC ---
aac_resp <- 1 - auc_resp
check("AAC equals 1 minus AUC", abs(aac_resp - (1 - auc_resp)) < 1e-12)
check("Higher AAC means more sensitive (responsive > plateau)",
      aac_resp > (1 - auc_plat))
cat("    -> a sign flip between AUC and AAC silently inverts every result\n")

# --- drc, if installed: the silent extrapolation trap ---
if (requireNamespace("drc", quietly = TRUE)) {
  suppressPackageStartupMessages(library(drc))
  set.seed(42)
  cc <- rep(conc, each = 3)
  yy <- fourpl(cc, 5, 100, 0.5, 1.3) + rnorm(length(cc), 0, 3)
  fit <- drm(viability ~ concentration,
             data = data.frame(concentration = cc, viability = yy),
             fct = LL.4(names = c("slope", "lower", "upper", "ec50")))

  cat("\n  drc LL.4 fit on the responsive drug:\n")
  # drc stores convergence as a LOGICAL: TRUE means converged.
  # NOT the optim integer convention where 0 means success.
  conv <- fit$fit$convergence
  cat(sprintf("    fit$fit$convergence = %s (drc uses TRUE = converged)\n", conv))
  check("drc convergence is a logical, TRUE when converged", isTRUE(conv))
  check("isTRUE(convergence) is the correct check, not == 0", isTRUE(conv) && !identical(conv, 0))

  ed <- ED(fit, 50, interval = "delta", display = FALSE)
  cat(sprintf("    ED50 = %.4f, CI [%.4f, %.4f]\n", ed[1], ed[3], ed[4]))
  check("drc ED50 recovers the true ec50 within CI", ed[3] < 0.5 && ed[4] > 0.5)

  # The plateau trap: drc returns an ED50 even when the curve never crosses 50%.
  yp <- fourpl(cc, 62, 100, 0.3, 1.3) + rnorm(length(cc), 0, 3)
  fitp <- drm(viability ~ concentration,
              data = data.frame(concentration = cc, viability = yp),
              fct = LL.4(names = c("slope", "lower", "upper", "ec50")))
  lower_p <- coef(fitp)["lower:(Intercept)"]
  ed_p <- suppressWarnings(tryCatch(ED(fitp, 50, interval = "none", display = FALSE)[1],
                                    error = function(e) NA_real_))
  cat(sprintf("    plateau: fitted lower asymptote %.1f%%, ED50 returned %s\n",
              lower_p, ifelse(is.na(ed_p), "NA", sprintf("%.4f", ed_p))))
  check("Fitted lower asymptote stays above 50% for the plateau drug", lower_p > 50)
  check("drc still returns an ED50 for a curve that never reaches 50%",
        !is.na(ed_p))
  cat("    -> that ED50 is an extrapolation, not a measurement. Report AUC.\n")
} else {
  cat("\n  SKIP: drc not installed (base-R checks above still ran)\n")
}

# --- nplr, if installed ---
if (requireNamespace("nplr", quietly = TRUE)) {
  suppressPackageStartupMessages(library(nplr))
  set.seed(42)
  cc <- rep(conc, each = 3)
  yy <- fourpl(cc, 5, 100, 0.5, 1.3) + rnorm(length(cc), 0, 3)
  np <- nplr(x = cc, y = yy / 100, useLog = TRUE, silent = TRUE)
  ic <- getEstimates(np, 0.5)$x
  cat(sprintf("\n  nplr IC50 estimate: %.4f (true 0.5)\n", ic))
  check("nplr IC50 recovers the true ec50", abs(ic - 0.5) < 0.15)
} else {
  cat("\n  SKIP: nplr not installed\n")
}

cat(sprintf("\n=== Curves: %d passed, %d failed ===\n", pass, fail))
if (fail > 0) quit(status = 1)
