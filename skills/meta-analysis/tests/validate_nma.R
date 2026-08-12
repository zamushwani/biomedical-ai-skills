#!/usr/bin/env Rscript
# Validate network meta-analysis on the Senn 2013 diabetes network.
#
# 26 trials of 10 glucose-lowering treatments, the standard NMA teaching
# dataset. Checks that multi-arm trials are handled as correlated comparisons,
# that inconsistency can be assessed, and that rankings behave as documented.
#
# Expected runtime: under 30 seconds. No downloads.
# Requirements: netmeta, meta

suppressPackageStartupMessages({
  library(netmeta)
  library(meta)
})

cat("=== Network Meta-Analysis Validation (Senn 2013) ===\n\n")
pass <- 0; fail <- 0

check <- function(name, condition) {
  if (isTRUE(condition)) {
    cat(sprintf("  PASS: %s\n", name)); pass <<- pass + 1
  } else {
    cat(sprintf("  FAIL: %s\n", name)); fail <<- fail + 1
  }
}

cat(sprintf("  netmeta %s, meta %s\n\n", packageVersion("netmeta"), packageVersion("meta")))

# --- pairwise() lives in meta, not netmeta ---
check("pairwise() is exported by the meta package",
      "pairwise" %in% getNamespaceExports("meta"))
check("pairwise() is NOT exported by netmeta",
      !("pairwise" %in% getNamespaceExports("netmeta")))

# --- Dataset ---
data(Senn2013)
n_studies <- length(unique(Senn2013$studlab))
n_treat <- length(unique(c(as.character(Senn2013$treat1),
                           as.character(Senn2013$treat2))))

cat(sprintf("  rows: %d | studies: %d | treatments: %d\n",
            nrow(Senn2013), n_studies, n_treat))
check("26 studies", n_studies == 26)
check("10 treatments", n_treat == 10)
check("More rows than studies (multi-arm trials present)", nrow(Senn2013) > n_studies)

# A trial contributing more than one row is multi-arm. Those comparisons share
# an arm and are therefore correlated.
multiarm <- names(which(table(Senn2013$studlab) > 1))
cat(sprintf("  multi-arm trials: %d (%s)\n", length(multiarm),
            paste(head(multiarm, 3), collapse = ", ")))
check("At least one multi-arm trial in the network", length(multiarm) >= 1)

# --- Fit ---
net <- netmeta(TE, seTE, treat1, treat2, studlab, data = Senn2013,
               sm = "MD", common = FALSE, random = TRUE,
               reference.group = "plac")

cat(sprintf("\n  k = %d pairwise comparisons, n = %d treatments, %d designs\n",
            net$k, net$n, length(unique(net$designs))))
check("k is 26", net$k == 26)
check("n is 10 treatments", net$n == 10)
# Connectivity is not a field on the netmeta object; it comes from netconnection().
# A disconnected network cannot be analysed as one network at all.
nc <- netconnection(Senn2013$treat1, Senn2013$treat2, Senn2013$studlab)
check("Network is connected (one subnetwork)", nc$n.subnets == 1)
check("Reference group is placebo", net$reference.group == "plac")

cat(sprintf("  tau = %.4f, I^2 = %.1f%%\n", net$tau, net$I2 * 100))
check("tau is 0.3297", abs(net$tau - 0.3297) < 1e-3)
check("I^2 is ~81%", abs(net$I2 * 100 - 81.4) < 1.0)

# --- Multi-arm correlation is actually handled ---
# Degrees of freedom for heterogeneity is not simply k - 1 when multi-arm
# trials are present, because their comparisons are not independent.
cat(sprintf("  df for Q: %d (k - 1 would be %d)\n", net$df.Q, net$k - 1))
check("Degrees of freedom account for multi-arm correlation", net$df.Q < net$k - 1)

# --- Estimates ---
est <- net$TE.random[, "plac"]
check("An estimate exists for every treatment vs placebo",
      sum(!is.na(est)) == net$n)
check("Placebo vs itself is exactly zero", est["plac"] == 0)

best <- names(which.min(est))
cat(sprintf("  largest reduction vs placebo: %s (%.3f)\n", best, min(est, na.rm = TRUE)))
check("At least one treatment beats placebo", min(est, na.rm = TRUE) < 0)

# --- Inconsistency ---
ns <- netsplit(net)
n_both <- sum(!is.na(ns$compare.random$p))
cat(sprintf("\n  comparisons with both direct and indirect evidence: %d\n", n_both))
check("11 comparisons allow a direct-vs-indirect split", n_both == 11)
check("Node-splitting p-values are valid probabilities",
      all(ns$compare.random$p[!is.na(ns$compare.random$p)] >= 0 &
          ns$compare.random$p[!is.na(ns$compare.random$p)] <= 1))

dd <- decomp.design(net)
check("Design-by-treatment decomposition returns a global test",
      !is.null(dd$Q.inc.random))

# Both tests are underpowered. A non-significant result is not evidence of
# transitivity, which is a clinical judgement made before fitting.

# --- Ranking ---
nr <- netrank(net, small.values = "desirable")
ps <- nr$ranking.random

cat(sprintf("  P-scores computed for %d treatments\n", length(ps)))
check("A P-score for every treatment", length(ps) == net$n)
check("P-scores lie in [0, 1]", all(ps >= 0 & ps <= 1))

top3 <- names(sort(ps, decreasing = TRUE))[1:3]
cat(sprintf("  top 3 by P-score: %s\n", paste(top3, collapse = ", ")))
check("Top-ranked treatment is rosiglitazone", top3[1] == "rosi")

# The ranking says nothing about how much evidence supports it. Show that the
# top-ranked treatment's estimate carries a confidence interval that must be
# reported alongside the rank.
se_top <- net$seTE.random[top3[1], "plac"]
cat(sprintf("  %s vs placebo: %.3f (SE %.3f)\n",
            top3[1], net$TE.random[top3[1], "plac"], se_top))
check("The top-ranked treatment has a reportable standard error",
      is.finite(se_top) && se_top > 0)

cat(sprintf("\n=== Network meta-analysis: %d passed, %d failed ===\n", pass, fail))
if (fail > 0) quit(status = 1)
