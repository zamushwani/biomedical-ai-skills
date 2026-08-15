#!/usr/bin/env Rscript
# Validate tumour mutational burden and why it is not comparable across assays.
#
# Uses the TCGA-LAML cohort shipped with maftools. Demonstrates that both the
# denominator (panel size) and the numerator rule (synonymous variants) change
# the reported TMB substantially, which is why a cutoff validated on one assay
# does not transfer to another.
#
# Expected runtime: under 1 minute. No downloads.
# Requirements: maftools

suppressPackageStartupMessages({
  library(maftools)
  library(data.table)
})

cat("=== Tumour Mutational Burden Validation (TCGA-LAML) ===\n\n")
pass <- 0; fail <- 0

check <- function(name, condition) {
  if (isTRUE(condition)) {
    cat(sprintf("  PASS: %s\n", name)); pass <<- pass + 1
  } else {
    cat(sprintf("  FAIL: %s\n", name)); fail <<- fail + 1
  }
}

cat(sprintf("  maftools %s\n\n", packageVersion("maftools")))

laml <- read.maf(system.file("extdata", "tcga_laml.maf.gz", package = "maftools"),
                 verbose = FALSE)

n_samples <- as.numeric(laml@summary[ID == "Samples", summary])
n_nonsyn <- nrow(laml@data)
n_syn <- nrow(laml@maf.silent)

cat(sprintf("  samples: %d\n", n_samples))
cat(sprintf("  non-synonymous variants: %d\n", n_nonsyn))
cat(sprintf("  synonymous variants:     %d\n", n_syn))

check("193 samples", n_samples == 193)
check("1732 non-synonymous variants", n_nonsyn == 1732)
check("475 synonymous variants", n_syn == 475)
check("Synonymous variants are stored separately from the main table",
      n_syn > 0 && n_nonsyn > n_syn)

# --- The numerator rule ---
# Some vendors count synonymous variants, most published pipelines do not.
inflation <- n_syn / n_nonsyn
cat(sprintf("\n  including synonymous inflates the count by %.1f%%\n", inflation * 100))
check("Counting synonymous variants inflates the numerator by 20-35%",
      inflation > 0.20 && inflation < 0.35)
cat("    -> two labs analysing the same sample can differ by this much\n")
cat("       before any biology is involved\n")

# --- The denominator ---
# captureSize is the callable megabases of the assay. It scales TMB linearly.
suppressMessages({
  t30 <- tmb(laml, captureSize = 30, logScale = FALSE)
  t50 <- tmb(laml, captureSize = 50, logScale = FALSE)
})

m30 <- median(t30$total_perMB)
m50 <- median(t50$total_perMB)

cat(sprintf("\n  captureSize 30 Mb: median TMB %.4f\n", m30))
cat(sprintf("  captureSize 50 Mb: median TMB %.4f\n", m50))

check("Median TMB at 30 Mb is 0.30", abs(m30 - 0.30) < 1e-6)
check("Median TMB at 50 Mb is 0.18", abs(m50 - 0.18) < 1e-6)

ratio <- m30 / m50
cat(sprintf("  ratio: %.6f   (50/30 = %.6f)\n", ratio, 50 / 30))
check("TMB scales exactly linearly with 1/captureSize",
      abs(ratio - 50 / 30) < 1e-6)
cat("    -> passing the wrong captureSize rescales every value in the cohort\n")

check("TMB values are non-negative", all(t30$total_perMB >= 0))

# --- Samples with zero eligible mutations disappear from the table ---
# tmb() returns one row per sample PRESENT IN @data. A sample whose only
# variants are synonymous has no rows there, so it is absent from the output
# entirely. Its true TMB is 0, not missing, and a naive join loses the patient.
clin <- as.character(laml@clinical.data$Tumor_Sample_Barcode)
scored <- as.character(t30$Tumor_Sample_Barcode)
dropped <- setdiff(clin, scored)

cat(sprintf("\n  samples in clinical data : %d\n", length(clin)))
cat(sprintf("  samples scored by tmb()  : %d\n", nrow(t30)))
cat(sprintf("  silently dropped         : %d (%s)\n",
            length(dropped), paste(head(dropped, 2), collapse = ", ")))

check("tmb() returns fewer rows than the cohort has samples", nrow(t30) < length(clin))
check("Exactly one sample is dropped here", length(dropped) == 1)

if (length(dropped) > 0) {
  ns <- sum(laml@data$Tumor_Sample_Barcode %in% dropped)
  sil <- sum(laml@maf.silent$Tumor_Sample_Barcode %in% dropped)
  cat(sprintf("  dropped sample has %d non-synonymous and %d silent variants\n", ns, sil))
  check("The dropped sample has zero non-synonymous variants", ns == 0)
  check("It does have variants, just only silent ones", sil > 0)
  cat("    -> its true TMB is 0, not NA. Left-join on the cohort and fill 0,\n")
  cat("       or the patient disappears from every downstream analysis.\n")
}

# --- Why a fixed cutoff does not transfer ---
# The FDA TMB-high indication uses >= 10 mut/Mb as measured by one specific
# assay. Applying that number to a different denominator changes who qualifies.
cutoff <- 10
cat(sprintf("\n  samples at or above %d mut/Mb:\n", cutoff))
for (cs in c(30, 50)) {
  suppressMessages(tt <- tmb(laml, captureSize = cs, logScale = FALSE))
  n_high <- sum(tt$total_perMB >= cutoff)
  cat(sprintf("    captureSize %d Mb: %d of %d\n", cs, n_high, nrow(tt)))
}
# LAML is a low-mutation-burden disease, so both are near zero. The point is
# that the count is a function of the denominator, not only of the tumour.
check("LAML is a low-TMB cohort, as expected biologically", m30 < 5)

# --- Per-sample counts are integers before division ---
counts <- t30$total
check("Underlying mutation counts are integers", all(counts == round(counts)))
check("One count per scored sample", length(counts) == nrow(t30))

cat(sprintf("\n=== TMB: %d passed, %d failed ===\n", pass, fail))
if (fail > 0) quit(status = 1)
