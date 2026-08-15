# Validation Tests

Tests run against data shipped with `VariantAnnotation` and `maftools`. Nothing is downloaded, and no command-line tools (bcftools, VEP) are required.

**Executed 2026-08-15** on R 4.5.1 with VariantAnnotation 1.56.0 and maftools 2.26.0: **62 assertions, 0 failures.**

## Running

```bash
Rscript run_all.R                 # all tests, under 2 min
Rscript run_all.R classification  # framework rules, no dependencies
Rscript run_all.R vcf             # parsing, multiallelics, normalization
Rscript run_all.R tmb             # TMB and its assay dependence
```

## What each test checks

**classification** (26 assertions). Encodes the framework rules as functions and checks the properties reports get wrong: ACMG/AMP has no somatic application, a somatic variant needs *both* somatic frameworks, tier assignment without a tumour type raises an error, and a truncating variant is strong evidence in a tumour suppressor but uninformative in an oncogene. Also confirms the two hotspot tables shipped with maftools describe the same 3,181 hotspots at **entirely different coordinates** between GRCh37 and GRCh38.

**vcf** (20 assertions). Parses three shipped VCFs. Confirms `chr22.vcf.gz` uses Ensembl-style seqlevels (`22`, not `chr22`) and overlaps UCSC naming in **zero** contigs — the mismatch that returns no annotations instead of an error. Counts multiallelic records and verifies that splitting them increases the record count by exactly the number of extra alleles. Implements minimal-representation trimming and checks it against known cases, including idempotence.

**tmb** (16 assertions). Uses the TCGA-LAML cohort. Shows that including synonymous variants inflates the numerator by 27.4%, and that `captureSize` scales TMB *exactly* linearly. Also catches a sample-loss behaviour: `tmb()` silently returns fewer rows than the cohort has samples.

## Requirements

```r
BiocManager::install(c("VariantAnnotation", "maftools"))
```

No internet access needed at run time.

## Expected values

Measured, not quoted.

### VCFs (VariantAnnotation `extdata`)

| File | Variants | Multiallelic | Note |
|---|---|---|---|
| `chr22.vcf.gz` | 10,376 | 0 | 5 samples, hg19, 233 indels |
| `hapmap_exome_chr22.vcf.gz` | 1,011 | **40** | splits to 1,072 records |
| `ex2.vcf` | 5 | 2 | seqlevel `20` |

Seqlevels are Ensembl style. Overlap with UCSC-style names (`chr1`…`chrY`) is **zero contigs**.

### TMB (TCGA-LAML, maftools `extdata`)

| Quantity | Value |
|---|---|
| Samples (clinical) | 193 |
| Samples scored by `tmb()` | **192** |
| Non-synonymous variants | 1,732 |
| Synonymous variants | 475 |
| Synonymous inflation | **27.4%** |
| Median TMB, `captureSize = 30` | 0.30 |
| Median TMB, `captureSize = 50` | 0.18 |
| Ratio | exactly 50/30 |

### Hotspot tables

| Table | Rows | Coordinates shared with the other build |
|---|---|---|
| `cancerhotspots_v2_GRCh37.tsv` | 3,181 | **0 of the first 200** |
| `cancerhotspots_v2_GRCh38.tsv` | 3,181 | — |

## Notes

- **`tmb()` silently drops samples with zero non-synonymous variants.** In TCGA-LAML, `TCGA-AB-2903` has 0 non-synonymous and 1 silent variant, so it is absent from the output entirely. Its true TMB is **0, not NA**. Left-join on the cohort and fill zero, or the patient disappears from every downstream analysis.
- **Trailing bases are trimmed before leading ones**, per the VCF specification. For a simple indel the leading trim therefore never fires and the position is unchanged. It fires only when both alleles remain longer than one base, as with an MNV collapsing to a single substitution (`100 CAT>CGT` → `101 A>G`).
- The same 3,181 hotspots share **no coordinates** across builds. A build mismatch relocates every variant without raising an error.
- These tests deliberately do not require bcftools or VEP. The normalization rules are reimplemented so the behaviour can be asserted anywhere.
