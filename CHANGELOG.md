# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [0.2.2] - 2026-08-10

### Fixed
- README links were relative, so all 16 of them broke on the PyPI project page. Now absolute, which works on both GitHub and PyPI
- Replaced the mermaid workflow diagram with a rendered image. Mermaid is not supported on PyPI and was showing as raw source

### Added
- PyPI version, monthly downloads, and supported-Python badges

## [0.2.1] - 2026-08-10

### Added
- Installable via `pip install biomedical-ai-skills`, with a `biomedical-skills` command for copying skills into a project (`list`, `install`, `install --all`, `path`). No dependencies
- Automated PyPI publishing on release via Trusted Publishing, including a build-time check that only reviewed skills are packaged
- `CITATION.cff` so the repository can be cited directly

### Fixed
- README badges and clone URL pointed at the previous account after the repository moved

## [0.2.0] - 2026-08-08

### Added
- single-cell-atlas validation tests: QC metrics and filter cascade against PBMC 3k (2,700 raw, 2,638 after standard QC, 13,714 genes in >=3 cells), MAD filtering ranges, Scrublet doublet rate, HVG marker capture; clustering behaviour across n_pcs and resolution; marker specificity including LYZ/NKG7/CD14 misfires; Harmony integration on 8 donors from Kang et al. 2018 with batch-mixing and cell-type-conservation checks
- spatial-transcriptomics skill (Part 1 — processing): platform decision tree (sequencing- vs imaging-based), loading for Visium, Visium HD, Xenium, MERSCOPE, CosMx and Stereo-seq via spatialdata-io and VisiumIO/XeniumIO, spatially local QC (SpotSweeper, SpaceTrooper), negative-control FDR for Xenium, image QC, normalization, spatially variable genes (Moran's I, nnSVG, SPARK-X) with rank-based rather than FDR-based selection
- spatial-transcriptomics skill (Part 2 — deconvolution): RCTD via the Bioconductor spacexr API, cell2location two-step reference and mapping, Tangram, SPOTlight, reference atlas requirements and hard minimums, cell typing and segmentation for imaging platforms (Proseg, Baysor, segger, RESOLVI), Visium HD resolution horizon
- spatial-transcriptomics skill (Part 3 — niches): domain vs niche distinction, method selection by resolution and panel size, BANKSY lambda semantics, CellCharter, squidpy neighbourhood statistics, spatially resolved ligand-receptor (LIANA+ bivariate, CellChat v2 spatial), niche-specific differential expression via pseudobulk with a condition:domain interaction
- spatial-transcriptomics validation tests: graph builder comparison and enrichment sensitivity on IMC data, Visium loading and spatial QC, Moran's I bounds and marker ranking against 10x mouse brain
- foundation-models skill: scGPT and Geneformer checkpoints, APIs and tokenization contracts, UCE, TranscriptFormer, Nicheformer, Tahoe-x1, Arc STATE, C2S-Scale; the benchmark evidence on where foundation models lose to HVG+PCA and scVI; baseline protocol and compute costs

## [0.1.0] - 2026-03-30

### Added
- cancer-multiomics skill: expression analysis with DESeq2 v1.50+, pathway analysis (GSEA/ORA/GSVA/ssGSEA), gene ID conversion, batch correction, visualization
- cancer-multiomics skill: mutation analysis with maftools v2.22+ (MAF handling, TMB, mutational signatures, driver detection), CNV analysis (segment processing, GISTIC2.0, gene-level mapping)
- cancer-multiomics skill: methylation analysis with minfi/ChAMP (450K/EPIC processing, Funnorm, probe filtering), DMPs (limma on M-values), DMRs (DMRcate), CIMP subtyping, methylation-expression integration, probe-bias-corrected pathway analysis (missMethyl)
- cancer-multiomics validation tests: expression (DEG benchmarks), mutation (driver frequencies, TMB), CNV (segment interpretation, gene mapping), methylation (DMP detection, beta-value QC) — all against TCGA-LUAD
- immune-deconvolution skill: unified immunedeconv interface for quanTIseq, EPIC, CIBERSORT, xCell, MCP-counter, TIMER, ESTIMATE; tumor purity correction; cross-method benchmarking; BayesPrism for scRNA-seq-reference-based deconvolution
- immune-deconvolution validation tests: deconvolution methods (quanTIseq, EPIC, MCP-counter output checks, cross-method CD8 correlation), ESTIMATE purity (anticorrelation with immune score, cross-validation with quanTIseq), subtype ordering (Basal vs Luminal A) — all against TCGA-BRCA
- survival-analysis skill: Kaplan-Meier with ggsurvfit, Cox PH with Schoenfeld diagnostics and time-varying coefficients, competing risks (cause-specific + Fine-Gray via tidycmprsk), RMST (survRM2), optimal cutpoint selection (maxstat with validation caveats), forest plots (forestmodel)
- survival-analysis validation tests: KM median OS and 2-year survival, Cox age HR and PH diagnostics, C-index, IDH-mutant vs wildtype prognostic comparison — all against TCGA-GBM
- single-cell-atlas skill (Part 1 — QC/preprocessing): MAD-based filtering (scater, manual), doublet detection (scDblFinder, Scrublet), normalization (SCTransform v2, scran, log-normalize), feature selection (VST, deviance). Dual-language: Seurat v5 (R) + scanpy (Python)
- single-cell-atlas skill (Part 2 — integration/annotation): batch integration (Harmony, scVI, scANVI, CCA/RPCA via IntegrateLayers), Leiden clustering with resolution selection (clustree), cell type annotation (CellTypist, scType, manual markers), UMAP visualization guidelines
- single-cell-atlas skill (Part 3 — downstream): pseudobulk DE (DESeq2 via scuttle/decoupleR, not Wilcoxon), trajectory inference (PAGA + DPT, Monocle3, scVelo dynamical mode), cell-cell communication (CellChat v2, LIANA+ consensus), TF activity (decoupleR + CollecTRI, pySCENIC for GRN discovery)
- Repository structure, contributing guidelines, security policy

[Unreleased]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.2.2...HEAD
[0.2.2]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/zamushwani/biomedical-ai-skills/releases/tag/v0.1.0
