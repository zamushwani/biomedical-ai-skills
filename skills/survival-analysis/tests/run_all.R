#!/usr/bin/env Rscript
# Master validation script for survival-analysis skill
#
# Tests survival methods against TCGA-GBM clinical data.
# Uses clinical metadata only — no expression download needed.
#
# Usage:
#   Rscript run_all.R              # run all tests
#   Rscript run_all.R survival     # run one test
#
# Expected runtime: 10-20 minutes
#
# Requirements:
#   Core: TCGAbiolinks, survival
#   Optional: ggsurvfit (for plot tests, not required for validation)

args <- commandArgs(trailingOnly = TRUE)

tests <- c("survival", "cox", "prognostic")
if (length(args) > 0) {
  tests <- match.arg(args[1], tests)
}

cat("Survival Analysis Skill Validation\n")
cat("===================================\n")
cat(sprintf("Date: %s\n", Sys.time()))
cat(sprintf("R version: %s\n", R.version.string))
cat(sprintf("Tests to run: %s\n\n", paste(tests, collapse = ", ")))

# sys.frame(1) exists only when this file is source()d. Under Rscript it
# errors outright, so the fallback must be inside tryCatch, not after it.
script_dir <- tryCatch(dirname(sys.frame(1)$ofile), error = function(e) ".")
if (is.null(script_dir) || script_dir == "") script_dir <- "."

for (test in tests) {
  script <- file.path(script_dir, sprintf("validate_%s.R", test))
  if (file.exists(script)) {
    cat(sprintf("\n--- Running %s validation ---\n\n", test))
    tryCatch(
      source(script, local = new.env()),
      error = function(e) {
        cat(sprintf("\nERROR in %s validation: %s\n", test, e$message))
      }
    )
  } else {
    cat(sprintf("Script not found: %s\n", script))
  }
}

cat("\n===================================\n")
cat("Validation complete.\n")
