#!/usr/bin/env Rscript
# Master validation script for the drug-response skill.
#
# Runs on simulated dose-response and prediction problems with known ground
# truth, so no PharmacoSet download (multi-gigabyte) is needed. The curve test
# additionally cross-checks against drc and nplr when they are installed.
#
# Usage:
#   Rscript run_all.R              # all tests
#   Rscript run_all.R curves       # one test
#
# Expected runtime: under 3 minutes
#
# Requirements:
#   curves      base R; optionally drc and nplr
#   prediction  glmnet

args <- commandArgs(trailingOnly = TRUE)

tests <- c("curves", "prediction")
if (length(args) > 0) {
  tests <- match.arg(args[1], tests)
}

cat("Drug Response Skill Validation\n")
cat("===============================\n")
cat(sprintf("Date: %s\n", Sys.time()))
cat(sprintf("R version: %s\n", R.version.string))

for (p in c("drc", "nplr", "glmnet")) {
  v <- tryCatch(as.character(packageVersion(p)), error = function(e) "not installed")
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
