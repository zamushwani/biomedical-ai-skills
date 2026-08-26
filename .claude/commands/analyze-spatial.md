---
description: Spatial transcriptomics analysis: loading, spatial QC, spatially variable genes, deconvolution, domains. Use for Visium, Xenium, MERSCOPE, or CosMx data.
argument-hint: [data-path] [platform]
allowed-tools: Read Grep Glob Bash(python3 *)
---

Analyse the spatial data at `$0` from platform `$1`.

Follow the `spatial-transcriptomics` skill. Platform determines almost everything:

```
Visium        spots, not cells. Each spot is a mixture -> deconvolution required.
Visium HD     2um bins; binning choice changes the analysis.
Xenium/CosMx  true single cells, but a targeted panel -> absent != not expressed.
MERSCOPE      single cells, panel-limited, segmentation-sensitive.
```

The parts that are usually got wrong:

1. **QC spatially, not just per-cell.** A low-count region can be biology (necrosis) or a tissue fold. A global count filter erases both without distinction.
2. **Do not report a Visium spot as a cell.** Deconvolve, and say which reference was used.
3. **Rank spatially variable genes, do not just FDR-filter them.** With thousands of genes almost everything is "significant"; the ranking is the result.
4. **For imaging platforms, check segmentation** before trusting per-cell counts — over-segmentation splits one cell into two low-count cells.

Report: platform-appropriate QC, SVGs with their ranking statistic, and domain/niche assignments with the method named.

If `$0` is empty, ask for the data path.
