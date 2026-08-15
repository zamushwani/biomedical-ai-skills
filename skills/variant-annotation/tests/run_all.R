#!/usr/bin/env Rscript
# Master validation script for the variant-annotation skill.
#
# Runs entirely against data shipped with VariantAnnotation and maftools.
# Nothing is downloaded, and no command-line tools (bcftools, VEP) are needed.
#
# Usage:
#   Rscript run_all.R                 # all tests
#   Rscript run_all.R classification  # one test
#
# Expected runtime: under 2 minutes
#
# Requirements:
#   VariantAnnotation   VCF parsing and normalization checks
#   maftools            TMB and hotspot reference tables

args <- commandArgs(trailingOnly = TRUE)

tests <- c("classification", "vcf", "tmb")
if (length(args) > 0) {
  tests <- match.arg(args[1], tests)
}

cat("Variant Annotation Skill Validation\n")
cat("====================================\n")
cat(sprintf("Date: %s\n", Sys.time()))
cat(sprintf("R version: %s\n", R.version.string))

for (p in c("VariantAnnotation", "maftools")) {
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

cat("\n====================================\n")
if (length(failed) == 0) {
  cat("All validations passed.\n")
} else {
  cat(sprintf("Failed: %s\n", paste(failed, collapse = ", ")))
  quit(status = 1)
}
