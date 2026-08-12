#!/usr/bin/env Rscript
# Master validation script for the meta-analysis skill.
#
# Runs against datasets shipped with metadat and netmeta. Nothing is downloaded,
# so the whole suite completes in under a minute offline.
#
# Usage:
#   Rscript run_all.R              # run all tests
#   Rscript run_all.R effects      # run one test
#
# Expected runtime: under 1 minute
#
# Requirements:
#   metafor, metadat   effects, heterogeneity, bias
#   netmeta, meta      network meta-analysis

args <- commandArgs(trailingOnly = TRUE)

tests <- c("effects", "heterogeneity", "bias", "nma")
if (length(args) > 0) {
  tests <- match.arg(args[1], tests)
}

cat("Meta-Analysis Skill Validation\n")
cat("===============================\n")
cat(sprintf("Date: %s\n", Sys.time()))
cat(sprintf("R version: %s\n", R.version.string))

for (p in c("metafor", "metadat", "netmeta", "meta")) {
  v <- tryCatch(as.character(packageVersion(p)), error = function(e) "NOT INSTALLED")
  cat(sprintf("%s: %s\n", p, v))
}
cat(sprintf("Tests to run: %s\n\n", paste(tests, collapse = ", ")))

script_dir <- tryCatch(dirname(sys.frame(1)$ofile), error = function(e) ".")
if (is.null(script_dir) || is.na(script_dir) || script_dir == "") script_dir <- "."

failed <- character()

for (test in tests) {
  script <- file.path(script_dir, sprintf("validate_%s.R", test))
  if (file.exists(script)) {
    cat(sprintf("\n--- Running %s validation ---\n\n", test))
    status <- system2("Rscript", script)
    if (!identical(status, 0L)) failed <- c(failed, test)
  } else {
    cat(sprintf("Script not found: %s\n", script))
    failed <- c(failed, test)
  }
}

cat("\n===============================\n")
if (length(failed) == 0) {
  cat("All validations passed.\n")
} else {
  cat(sprintf("Failed: %s\n", paste(failed, collapse = ", ")))
  quit(status = 1)
}
