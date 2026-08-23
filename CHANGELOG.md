# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [0.6.2] - 2026-08-23

### Added
- computational-pathology (part 3, analysis): cell and nucleus segmentation, tumour region and tertiary lymphoid structure detection, spatial statistics on segmented cell positions, and integration with matched molecular data
- Records that StarDist ships a `2D_versatile_he` H&E nuclei model but `pip install stardist` pulls no deep-learning backend, so it fails at predict rather than install unless TensorFlow is added via `csbdeep[tf]`, and that its pretrained model expects `csbdeep.utils.normalize` percentile normalization rather than a 0-1 rescale
- Records that HoVer-Net is git-only (MIT, last pushed 2023-10) and classifies cells into its training panel's types, and that squidpy's spatial statistics require Python 3.12 or newer
- States the analysis-level discipline: segment at ~0.25 um/px and report cells per mm rather than per tile, mask Ripley's study region to tissue rather than the slide bounding box, treat neighbourhood-enrichment z-scores as within-slide, and integrate with molecular data at the registration level the data honestly supports rather than matching cells to spots across adjacent sections

## [0.6.1] - 2026-08-22

### Added
- computational-pathology (part 2, feature extraction): pathology foundation models as tile encoders, multiple instance learning with attention pooling, framework choice, and the splitting discipline that decides whether a slide-level result is real
- Records that nearly every pathology encoder is gated on HuggingFace, proven anonymously (`MahmoodLab/UNI` returns HTTP 401 where `owkin/phikon-v2` returns 200), and that UNI, UNI2-h, CONCH and Virchow2 carry CC-BY-NC-ND licences whose no-derivatives clause covers a fine-tuned checkpoint, while Virchow v1, Prov-GigaPath and H-optimus-0 are Apache-2.0
- Records two install traps: `pip install trident` fetches an astrophysics package rather than Mahmood Lab's pathology TRIDENT, which installs from git, and CTransPath requires a forked timm 0.5.4 from a Google Drive link against a current timm of 1.0.28
- Records the MIL framework licences: CLAM is GPL-3.0, DSMIL is MIT, and TransMIL declares none, so its reuse rights are unclear
- States the leakage rule directly: split by patient rather than tile or slide, hold out a site in multi-institution cohorts, report a mean-pooling baseline beside any attention model, and treat attention weights as hypotheses rather than explanations

## [0.6.0] - 2026-08-22

### Added
- computational-pathology skill (part 1, WSI processing): reading vendor formats with OpenSlide, the level-0 coordinate frame that `read_region` mixes with the target-level frame, downsamples as floats rather than powers of two, microns-per-pixel as the unit of scale instead of nominal magnification, MIRAX bounds, tissue detection by saturation, tile extraction with overlap and RGBA compositing, stain normalization, and H&E colour deconvolution
- Records the install trap that `openslide-python` is a binding whose only dependency is Pillow, so `openslide-bin` (or a system OpenSlide) is required separately, and that `staintools` was last released 2019-04-11 and archived on GitHub in 2021 with torchstain and HistomicsTK as the maintained replacements
- Records that torchstain ships Macenko, MultiMacenko and Reinhard but not Vahadane, and that sparse-NMF separation lives in HistomicsTK as `separate_stains_xu_snmf`
- Measures scikit-image's colour deconvolution clipping: `separate_stains` ends with `np.maximum(stains, 0)`, so on random RGB in [0.4, 0.9] 784 of 1024 pixels lose a channel, and the `rgb2hed`/`hed2rgb` round trip is exact to 1.1e-16 only where nothing clipped

## [0.5.1] - 2026-08-22

### Added
- clinical-nlp validation tests: 45 assertions across three Python scripts, executed on 2026-08-22 with 0 failures. All text is synthetic; no corpus is downloaded and no credentialed data is touched. Demonstrates the skill's central claim on a four-entity note, where the naive `is_negated`-only check reports three findings (a father's colon cancer, a resolved 2020 pneumonia, a penicillin allergy) while the correct five-attribute check reports none
- The dependency suite resolves real PyPI metadata rather than asserting pins from memory: on Python 3.11 scispaCy and medspaCy admit only spaCy 3.7.x while medspaCy and negspacy are disjoint, and a model URL built from the package version returns 404 where the published model version returns 200
- The de-identification suite pins Presidio's clinical behaviour: an MRN is typed `US_BANK_NUMBER`/`US_DRIVER_LICENSE`, a specimen accession is typed `US_DRIVER_LICENSE`, a provider name is `PERSON` like the patient, and a bare local phone number is missed entirely
- Two ConText gaps documented in the skill, both silent: "Patient at risk for stroke" and "Status post MI in 2019" return all five attributes False and so read as active findings

### Fixed
- clinical-nlp skill: the assertion example mapped "will rule out sepsis" to `is_hypothetical`. Measured against medspaCy 1.3.1, that phrasing sets `is_uncertain`; only an if-construction is hypothetical. Getting this backwards mislabels every deferred diagnosis in a cohort

## [0.5.0] - 2026-08-17

### Added
- clinical-nlp skill: corpus access and DUA constraints before any code, note sectioning, biomedical NER with scispaCy, assertion detection via medspaCy ConText, concept normalization to UMLS with MedCAT and QuickUMLS compared, ICD-10 candidate generation framed for coder review rather than billing, temporal relation extraction, adverse event identification with the indication confound, de-identification against HIPAA Safe Harbor, and when a rule-based pipeline beats a clinical transformer
- Records the scispaCy dependency conflicts verified this session: it pins `numpy<2.0` and `python<3.13`, its published models stop at 0.5.4 while the package is 0.6.2 so a version-matched URL 404s, and its spaCy pin is disjoint from medspaCy's on Python below 3.12
- Records that `philter-ucsf` was last released 2020-04-19 and names Presidio as the maintained replacement, and that MedCAT 2.x is a rewrite that will not run v1.9.x code

## [0.4.0] - 2026-08-16

### Added
- drug-response validation tests: 22 assertions across two R scripts, executed on 2026-08-16 with 0 failures. Runs on simulated dose-response and prediction problems with a known ground truth, cross-checking against drc and nplr when installed. Confirms a plateauing curve has no observed IC50 while AUC is defined, that drc extrapolates an ED50 for such a curve anyway, and that feature selection outside the cross-validation loop and lineage confounding both inflate apparent prediction accuracy
- **Phase 3 complete: all ten Phase 1-3 skills shipped and validated.** cancer-multiomics, immune-deconvolution, survival-analysis, single-cell-atlas, spatial-transcriptomics, foundation-models, meta-analysis, variant-annotation, drug-response, each with a test suite

### Fixed
- drug-response skill: the convergence check for a `drc` fit was `fit$fit$convergence == 0`, the optim integer convention. drc stores convergence as a logical, so `TRUE` means converged. Corrected to `isTRUE(fit$fit$convergence)`, verified against the real fitter during validation

## [0.3.3] - 2026-08-16

### Added
- drug-response skill: dose-response curve fitting (4PL via drc LL.4/LL2.4, the maintained nplr alternative, and GDSC's joint-model gdscIC50), why AUC beats IC50 as a response metric, curated retrieval through PharmacoGx with recomputed sensitivity measures, cross-dataset concordance and why it is only moderate, sensitivity prediction with a regularized-regression baseline and the feature-leakage and tissue-confounding traps, and tissue-corrected pharmacogenomic biomarker discovery
- Records that the cancerrxgene.org GDSC portal currently returns HTTP 410, that CRAN PharmacoGx is frozen at the 2016 version while Bioconductor is maintained, and that published IC50/AUC are not comparable across datasets

## [0.3.2] - 2026-08-15

### Fixed
- Removed an `Rplots.pdf` artifact that R generated while running the test suite and that was packaged into 0.3.1. Added it to `.gitignore` so it cannot recur

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

[Unreleased]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.6.2...HEAD
[0.6.2]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.6.1...v0.6.2
[0.6.1]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.5.1...v0.6.0
[0.5.1]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.3.3...v0.4.0
[0.3.3]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.3.1...v0.3.2
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
