#!/usr/bin/env Rscript
# Validate VCF parsing and the normalization rules that fail silently.
#
# Uses VCFs shipped with VariantAnnotation, so nothing is downloaded. Checks
# multiallelic detection, minimal-representation trimming, and the chromosome
# naming mismatch that returns no annotations rather than an error.
#
# Expected runtime: under 1 minute. No downloads.
# Requirements: VariantAnnotation

suppressPackageStartupMessages({
  library(VariantAnnotation)
})

cat("=== VCF Processing Validation ===\n\n")
pass <- 0; fail <- 0

check <- function(name, condition) {
  if (isTRUE(condition)) {
    cat(sprintf("  PASS: %s\n", name)); pass <<- pass + 1
  } else {
    cat(sprintf("  FAIL: %s\n", name)); fail <<- fail + 1
  }
}

cat(sprintf("  VariantAnnotation %s\n\n", packageVersion("VariantAnnotation")))

# --- A single-allelic VCF ---
f1 <- system.file("extdata", "chr22.vcf.gz", package = "VariantAnnotation")
v1 <- readVcf(f1, "hg19")
n_alt1 <- elementNROWS(alt(v1))

cat(sprintf("  chr22.vcf.gz: %d variants, %d samples\n", nrow(v1), ncol(v1)))
check("chr22.vcf.gz has 10376 variants", nrow(v1) == 10376)
check("5 samples", ncol(v1) == 5)
check("Genome recorded as hg19", unique(genome(v1)) == "hg19")
check("No multiallelic records in this file", sum(n_alt1 > 1) == 0)

# --- Chromosome naming: the mismatch that returns nothing ---
sl <- seqlevels(v1)
cat(sprintf("  seqlevels: %s\n", paste(head(sl, 3), collapse = ", ")))
check("Seqlevel is Ensembl style ('22'), not UCSC ('chr22')", "22" %in% sl)
check("No 'chr' prefix present", !any(grepl("^chr", sl)))

# A cache or reference using UCSC naming matches nothing here, and the failure
# is an empty result rather than an error.
ucsc_style <- paste0("chr", c(1:22, "X", "Y"))
check("UCSC-style names overlap this VCF in zero contigs",
      length(intersect(sl, ucsc_style)) == 0)
cat("    -> a 'chr'-prefixed reference would return no annotations, silently\n")

# --- A VCF that DOES contain multiallelic records ---
f2 <- system.file("extdata", "hapmap_exome_chr22.vcf.gz", package = "VariantAnnotation")
v2 <- suppressWarnings(readVcf(f2, "hg19"))
n_alt2 <- elementNROWS(alt(v2))

cat(sprintf("\n  hapmap_exome_chr22.vcf.gz: %d variants, %d multiallelic\n",
            nrow(v2), sum(n_alt2 > 1)))
check("1011 variants", nrow(v2) == 1011)
check("40 multiallelic records", sum(n_alt2 > 1) == 40)

# Splitting multiallelics increases the record count. A pipeline that reports
# the same count before and after `bcftools norm -m -any` did not split.
after_split <- sum(n_alt2)
cat(sprintf("  records before split: %d, after: %d\n", nrow(v2), after_split))
check("Splitting increases the record count", after_split > nrow(v2))
check("Increase equals the number of extra alleles",
      after_split - nrow(v2) == sum(n_alt2 - 1))

# --- Minimal representation ---
# Two spellings of the same event must reduce to one, or a knowledgebase
# lookup keyed on the canonical form misses.
minimal_rep <- function(pos, ref, alt) {
  # trim shared trailing bases
  while (nchar(ref) > 1 && nchar(alt) > 1 &&
         substr(ref, nchar(ref), nchar(ref)) == substr(alt, nchar(alt), nchar(alt))) {
    ref <- substr(ref, 1, nchar(ref) - 1)
    alt <- substr(alt, 1, nchar(alt) - 1)
  }
  # trim shared leading bases, advancing the position
  while (nchar(ref) > 1 && nchar(alt) > 1 &&
         substr(ref, 1, 1) == substr(alt, 1, 1)) {
    ref <- substr(ref, 2, nchar(ref))
    alt <- substr(alt, 2, nchar(alt))
    pos <- pos + 1
  }
  list(pos = pos, ref = ref, alt = alt)
}

a <- minimal_rep(100, "AAT", "AT")    # 1 bp deletion, written with padding
b <- minimal_rep(100, "CAT", "CGT")   # MNV that is really a single substitution
cat(sprintf("\n  minimal_rep(100,'AAT','AT')  -> pos %d ref %s alt %s\n", a$pos, a$ref, a$alt))
cat(sprintf("  minimal_rep(100,'CAT','CGT') -> pos %d ref %s alt %s\n", b$pos, b$ref, b$alt))
check("Trailing shared base trimmed", nchar(a$ref) < 3)
check("Deletion reduces to a 2-to-1 representation",
      nchar(a$ref) == 2 && nchar(a$alt) == 1)

# Trailing bases are trimmed before leading ones, per the VCF specification.
# For a simple indel the leading trim therefore never fires, and the position
# is unchanged. It fires only when both sides remain longer than one base,
# as with an MNV that collapses to a single substitution.
check("Deletion position is unchanged (trailing trim runs first)", a$pos == 100)
check("MNV collapses to an SNV", b$ref == "A" && b$alt == "G")
check("MNV position advances by the trimmed prefix length", b$pos == 101)

# An already-minimal SNV must be left untouched.
s <- minimal_rep(500, "A", "G")
check("A minimal SNV is unchanged",
      s$pos == 500 && s$ref == "A" && s$alt == "G")

# Idempotence: normalizing twice equals normalizing once.
once <- minimal_rep(100, "AAT", "AT")
twice <- minimal_rep(once$pos, once$ref, once$alt)
check("Normalization is idempotent", identical(once, twice))

# --- Indels are where representation actually varies ---
r1 <- ref(v1)
is_indel <- width(r1) != 1
cat(sprintf("\n  chr22 indel records: %d of %d\n", sum(is_indel), length(r1)))
check("File contains indels, where normalization matters", sum(is_indel) > 0)
check("SNVs are the majority", sum(!is_indel) > sum(is_indel))

cat(sprintf("\n=== VCF: %d passed, %d failed ===\n", pass, fail))
if (fail > 0) quit(status = 1)
