---
description: Estimate immune cell composition from bulk RNA-seq. Use when the user asks about tumour microenvironment, immune infiltration, CIBERSORT/quanTIseq/xCell, or immune cell fractions.
argument-hint: [expression-file] [method]
allowed-tools: Read Grep Glob Bash(Rscript *)
---

Estimate immune composition for `$0` using method `$1` (default: quanTIseq).

Follow the `immune-deconvolution` skill. The parts that are usually got wrong:

1. **Method dictates the input scale.** quanTIseq and CIBERSORT expect TPM; some methods want un-logged values. Feeding log-TPM where TPM is expected produces plausible-looking, wrong fractions.
2. **Know what the output means.** quanTIseq and EPIC give *fractions comparable across cell types within a sample*; xCell and MCP-counter give *scores comparable across samples within a cell type*. Comparing an xCell score between two cell types is meaningless.
3. **Correct for tumour purity** where it matters — immune fractions are diluted by tumour content, so a purity difference between groups masquerades as an immune difference.
4. **Run more than one method** and report where they disagree. Agreement across methods is the only cheap validation available.

Report: the fraction/score matrix, which method and input scale were used, and a cross-method comparison for the key cell types.

If `$0` is empty, ask for the expression matrix.
