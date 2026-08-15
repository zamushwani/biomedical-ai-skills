# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [0.3.1] - 2026-08-15

### Added
- variant-annotation validation tests: 62 assertions across three R scripts, executed on 2026-08-15 with 0 failures. Runs offline against data shipped with VariantAnnotation and maftools, with no bcftools or VEP dependency. Encodes the framework rules (ACMG/AMP has no somatic application; tier assignment requires a tumour type; truncating variants are strong evidence only in tumour suppressors), reimplements minimal-representation trimming and checks idempotence, shows multiallelic splitting raises the record count by exactly the number of extra alleles, and demonstrates that synonymous inclusion inflates TMB by 27.4% while captureSize scales it exactly linearly
- The suite documents that `maftools::tmb()` silently omits samples with zero non-synonymous variants, whose true TMB is 0 rather than missing, and that the same 3,181 cancer hotspots share no coordinates between GRCh37 and GRCh38

## [0.3.0] - 2026-08-15

### Added
- variant-annotation skill: VCF normalization and filtering with bcftools, functional annotation with Ensembl VEP 116.1 including transcript-selection semantics, germline classification under ACMG/AMP 2015 with ClinGen's criterion-level refinements, somatic oncogenicity under the ClinGen/CGC/VICC 2022 SOP, somatic clinical significance under the AMP/ASCO/CAP 2017 tiers, OncoKB and CIViC lookup, tumour mutational burden with its assay-dependence, microsatellite instability, and neoantigen prediction with pVACtools
- Documents that germline pathogenicity, somatic oncogenicity and somatic clinical significance are three separate frameworks on two different axes, and that ClinGen's guidance is to apply both somatic frameworks rather than choose between them

## [0.2.6] - 2026-08-15

### Added
- foundation-models validation tests: 32 assertions across three Python scripts, executed on 2026-08-15 with 0 failures. Establishes the HVG+PCA baseline on PBMC 3k (ARI 0.879, NMI 0.861 at 30 PCs) that a zero-shot embedding has to clear, and shows HVG selection alone is worth 0.332 ARI. Reimplements Geneformer's rank-value encoding to show that log-normalized input changes the token order for 100% of cells with a mean Spearman of 0.008. Confirms that passing Ensembl IDs to a symbol vocabulary matches 0 of 32,738 genes while the model still returns embeddings. Model weights are optional, so the head-to-head comparison skips when absent
- Every skill in the repository now has a validation suite

## [0.2.5] - 2026-08-12

### Added
- meta-analysis validation tests: 81 assertions across four R scripts, executed on 2026-08-12 with 0 failures. Runs offline against `metadat` and `netmeta` shipped datasets. Verifies pooled estimates against a hand-computed log risk ratio, demonstrates that `method="EE"` and `method="FE"` are numerically identical, shows the prediction interval crossing zero while the confidence interval does not, shows I^2 rising from 92.2% to 98.4% at unchanged tau^2 when precision increases, confirms trim-and-fill attenuates toward the null, and checks multi-arm correlation handling in a network via degrees of freedom (18, not k-1 = 25)
- The test suite detects the metafor 4.x/5.x boundary directly: on 4.x `escalc(measure="ROM", correct=)` has no effect, and from 5.0 the bias correction is applied by default

## [0.2.4] - 2026-08-11

### Added
- meta-analysis skill (effect estimation): effect measure selection, `escalc()` for binary, continuous and time-to-event outcomes, equal-effects vs fixed-effects vs random-effects models, tau^2 estimator choice, the Knapp-Hartung adjustment, heterogeneity quantification with prediction intervals, subgroup analysis via the omnibus moderator test, meta-regression, hazard ratio reconstruction from published Kaplan-Meier curves, and forest plots
- Documented the metafor 5.0 default changes that silently alter results relative to 4.x: bias correction now applied by default for `ROM`, `ROMC`, `CVR` and `CVRC`, and a changed default `add` for eight measures
- meta-analysis skill (advanced methods): small-study effects with the five competing explanations for funnel asymmetry, Egger's regression under the k >= 10 rule, trim-and-fill framed as a sensitivity analysis per the Cochrane Handbook, selection models and Copas/limit meta-analysis as principled alternatives, leave-one-out and influence and Baujat and cumulative diagnostics, network meta-analysis with transitivity assessed before fitting, correlated multi-arm handling via `pairwise()`, inconsistency via node-splitting and design-by-treatment decomposition, ranking with its instability caveats, Bayesian NMA, and GRADE/CINeMA certainty rating

## [0.2.3] - 2026-08-11

### Added
- meta-analysis skill (study selection): PROSPERO pre-specification, PICO search construction with MeSH/Emtree syntax and the Cochrane Highly Sensitive Search Strategy, programmatic PubMed retrieval via rentrez, deduplication with synthesisr, two-reviewer screening with Cohen's and Fleiss' kappa, PRISMA 2020 flow diagrams with the arithmetic that has to reconcile, data extraction templates and median-to-mean conversions, risk of bias tool selection (RoB 2, ROBINS-I, ROBINS-E, QUADAS-2, QUIPS, ROB ME, Newcastle-Ottawa) and robvis visualization
- Skills badge restored to the README, now at 7

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

[Unreleased]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.3.1...HEAD
[0.3.1]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.2.6...v0.3.0
[0.2.6]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.2.5...v0.2.6
[0.2.5]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.2.4...v0.2.5
[0.2.4]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/zamushwani/biomedical-ai-skills/releases/tag/v0.1.0
