---
description: Quality control and filtering for single-cell RNA-seq. Use when the user has an h5ad/h5/10x matrix and wants QC, cell filtering, doublet detection, or asks why their cell count dropped.
argument-hint: [h5ad-file]
allowed-tools: Read Grep Glob Bash(python3 *)
---

Run QC on `$0`.

Follow the `single-cell-atlas` skill. The parts that are usually got wrong:

1. **Use MAD-based thresholds, not fixed cutoffs.** A hard `n_genes > 200` throws away real cells in low-complexity tissue and keeps debris in others. Compute median absolute deviation per metric and justify the multiplier.
2. **Mitochondrial percentage is tissue-dependent.** A 5% cutoff is convention, not biology; cardiomyocytes and hepatocytes legitimately run far higher.
3. **Detect doublets before clustering**, not after. A doublet cluster looks like a novel intermediate cell type and gets written up as one.
4. **Report the filter cascade** — cells in, cells removed by each criterion, cells out. A single "after QC" number hides which filter did the damage.
5. **Filter genes on cells-expressing**, not total counts.

Report: the cascade table, the MAD thresholds actually used with their multipliers, doublet rate, and a before/after QC plot.

If `$0` is empty, ask which matrix to load.
