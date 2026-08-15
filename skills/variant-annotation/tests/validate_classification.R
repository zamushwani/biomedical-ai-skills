#!/usr/bin/env Rscript
# Validate the classification framework rules the skill documents.
#
# Three frameworks sit on two axes. This encodes the rules as functions and
# checks the properties that reports get wrong: tiers are tumour-type specific,
# oncogenicity criteria depend on the gene's mechanism, ACMG/AMP does not apply
# to somatic variants, and population frequency must use popmax.
#
# Also checks that hotspot reference tables are build-specific, using the
# cancerhotspots tables shipped with maftools.
#
# Expected runtime: under 30 seconds. No downloads.
# Requirements: maftools (for the shipped hotspot tables), data.table

suppressPackageStartupMessages({
  library(data.table)
})

cat("=== Classification Framework Validation ===\n\n")
pass <- 0; fail <- 0

check <- function(name, condition) {
  if (isTRUE(condition)) {
    cat(sprintf("  PASS: %s\n", name)); pass <<- pass + 1
  } else {
    cat(sprintf("  FAIL: %s\n", name)); fail <<- fail + 1
  }
}

# --- Framework applicability ---
# ACMG/AMP assumes germline inheritance, segregation, and population frequency
# as evidence of benignity. None of that transfers to a somatic variant.
framework_for <- function(origin, question) {
  if (origin == "germline" && question == "pathogenicity") return("ACMG/AMP 2015")
  if (origin == "somatic" && question == "oncogenicity") return("ClinGen/CGC/VICC 2022")
  if (origin == "somatic" && question == "clinical") return("AMP/ASCO/CAP 2017")
  NA_character_
}

check("Germline pathogenicity uses ACMG/AMP",
      framework_for("germline", "pathogenicity") == "ACMG/AMP 2015")
check("Somatic oncogenicity uses ClinGen/CGC/VICC",
      framework_for("somatic", "oncogenicity") == "ClinGen/CGC/VICC 2022")
check("Somatic clinical significance uses AMP/ASCO/CAP",
      framework_for("somatic", "clinical") == "AMP/ASCO/CAP 2017")
check("ACMG/AMP has no somatic application",
      is.na(framework_for("somatic", "pathogenicity")))

# Oncogenicity and clinical significance are separate questions about the same
# somatic variant, so both must resolve to a framework.
check("A somatic variant needs BOTH somatic frameworks, not one",
      !is.na(framework_for("somatic", "oncogenicity")) &&
      !is.na(framework_for("somatic", "clinical")))

# --- Tiers are tumour-type specific ---
assign_tier <- function(variant, tumour_type) {
  if (is.null(tumour_type) || is.na(tumour_type) || tumour_type == "") {
    stop("tier assignment requires a tumour type")
  }
  key <- paste(variant, tumour_type, sep = "|")
  switch(key,
    "BRAF V600E|melanoma"          = "IA",
    "BRAF V600E|colorectal"        = "IIC",
    "KRAS G12C|NSCLC"              = "IA",
    "KRAS G12D|pancreatic"         = "III",
    "III")
}

t_mel <- assign_tier("BRAF V600E", "melanoma")
t_crc <- assign_tier("BRAF V600E", "colorectal")
cat(sprintf("\n  BRAF V600E: melanoma -> Tier %s, colorectal -> Tier %s\n", t_mel, t_crc))

check("BRAF V600E is Tier IA in melanoma", t_mel == "IA")
check("BRAF V600E is Tier IIC in colorectal cancer", t_crc == "IIC")
check("The same variant receives different tiers by tumour type", t_mel != t_crc)
check("Tier assignment without a tumour type is an error",
      inherits(try(assign_tier("BRAF V600E", NA), silent = TRUE), "try-error"))
cat("    -> a tier reported without naming the tumour type is meaningless\n")

# --- Oncogenicity is not clinical significance ---
# KRAS G12D is unambiguously a driver and can still be Tier III.
oncogenic <- function(v) v %in% c("BRAF V600E", "KRAS G12C", "KRAS G12D")
check("KRAS G12D is oncogenic", oncogenic("KRAS G12D"))
check("KRAS G12D is Tier III in pancreatic cancer",
      assign_tier("KRAS G12D", "pancreatic") == "III")
check("Oncogenic and actionable are independent",
      oncogenic("KRAS G12D") && assign_tier("KRAS G12D", "pancreatic") == "III")

# --- Gene mechanism selects the criteria ---
# A truncating variant is strong evidence in a tumour suppressor and
# essentially uninformative in an oncogene.
truncating_evidence <- function(gene_role) {
  switch(gene_role,
    "tumour_suppressor" = "strong",
    "oncogene"          = "none",
    "unknown")
}

check("Truncating variant is strong evidence in a tumour suppressor",
      truncating_evidence("tumour_suppressor") == "strong")
check("Truncating variant is uninformative in an oncogene",
      truncating_evidence("oncogene") == "none")
check("Evidence strength differs by gene mechanism",
      truncating_evidence("tumour_suppressor") != truncating_evidence("oncogene"))

# --- Population frequency: popmax, not global ---
# A variant rare globally can be common in one ancestry group. Using the global
# AF hides evidence of benignity and inflates VUS in under-represented groups.
benign_by_frequency <- function(af, threshold = 0.05) af > threshold

global_af <- 0.001
popmax_af <- 0.04
cat(sprintf("\n  global AF %.3f vs popmax AF %.3f\n", global_af, popmax_af))
check("Global AF alone does not reach the benign threshold",
      !benign_by_frequency(global_af))
check("Popmax AF is 40x the global AF here", popmax_af / global_af == 40)
check("Popmax is the value that must be evaluated", popmax_af > global_af)
cat("    -> using global AF is how VUS accumulate in under-represented populations\n")

# Allele number matters: a frequency from a handful of alleles is not evidence.
sufficient_evidence <- function(allele_number, min_an = 2000) allele_number >= min_an
check("A frequency from 4 alleles is not evidence", !sufficient_evidence(4))
check("A frequency from a large cohort is evidence", sufficient_evidence(120000))

# --- PM2 strength, per current ClinGen guidance ---
pm2_strength <- "supporting"   # recalibrated from the 2015 "moderate"
check("PM2 is applied at supporting strength", pm2_strength == "supporting")
check("PM2 is not moderate under current guidance", pm2_strength != "moderate")

# --- Hotspot tables are build-specific ---
h37_f <- system.file("extdata", "cancerhotspots_v2_GRCh37.tsv", package = "maftools")
h38_f <- system.file("extdata", "cancerhotspots_v2_GRCh38.tsv", package = "maftools")

if (nzchar(h37_f) && nzchar(h38_f)) {
  h37 <- fread(h37_f, header = FALSE)
  h38 <- fread(h38_f, header = FALSE)
  cat(sprintf("\n  cancerhotspots GRCh37: %d rows | GRCh38: %d rows\n",
              nrow(h37), nrow(h38)))
  check("GRCh37 hotspot table loads", nrow(h37) > 1000)
  check("GRCh38 hotspot table loads", nrow(h38) > 1000)
  check("Both builds describe a comparable number of hotspots",
        abs(nrow(h37) - nrow(h38)) < 0.1 * nrow(h37))

  # The same hotspots, different coordinates. Annotating against the wrong
  # build lands in a different position.
  pos37 <- h37[[2]][1:200]
  pos38 <- h38[[2]][1:200]
  identical_pos <- sum(pos37 == pos38)
  cat(sprintf("  identical coordinates in the first 200 rows: %d\n", identical_pos))
  check("Coordinates differ between builds", identical_pos < 200)
  cat("    -> a build mismatch silently relocates every variant\n")
} else {
  cat("\n  SKIP: cancerhotspots tables not found in this maftools version\n")
}

cat(sprintf("\n=== Classification: %d passed, %d failed ===\n", pass, fail))
if (fail > 0) quit(status = 1)
