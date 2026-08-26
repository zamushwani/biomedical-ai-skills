---
description: Differential expression from a count matrix with DESeq2. Use when the user has bulk RNA-seq counts and wants DEGs, a volcano plot, or asks which genes differ between conditions.
argument-hint: [counts-file] [condition-column]
allowed-tools: Read Grep Glob Bash(Rscript *)
---

Run a differential expression analysis on `$0` using the condition column `$1`.

Follow the `cancer-multiomics` skill. The parts that are usually got wrong:

1. **Feed DESeq2 raw integer counts.** Not TPM, not FPKM, not anything normalized. DESeq2 models counts and its dispersion estimates are invalid on normalized input.
2. **Set the factor reference level explicitly** with `relevel()`, or the sign of every log2 fold change is a coin flip.
3. **Use `lfcShrink()` for ranking and plotting**, not the raw `log2FoldChange`. Low-count genes have wildly inflated effect sizes otherwise.
4. **Report adjusted p-values.** `padj`, not `pvalue`, and state the threshold.
5. **Check the design matrix is full rank** before fitting; a confounded batch/condition design fails in a confusing way.

Report: number of genes tested, number passing padj < 0.05, the top up- and down-regulated genes with shrunk effect sizes, and any genes dropped by independent filtering.

If `$0` is empty, ask which count matrix to use before running anything.
