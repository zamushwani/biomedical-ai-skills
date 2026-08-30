# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [0.15.0] - 2026-08-30

### Added
- Cross-platform entry files, so the compatibility claim in the README is backed by something. `AGENTS.md` is the cross-tool standard read natively by Codex CLI, Cursor's Agent mode, Copilot, Zed and Windsurf among others; `GEMINI.md` for Gemini CLI; and `.cursor/rules/biomedical-skills.mdc` for Cursor's Chat and Composer modes, which do not read `AGENTS.md`. `AGENTS.md` is the single source of truth and the others point at it
- `tools/check_portability.py`, run this session with 15 assertions and 0 failures. It verifies each platform's entry file exists, that they agree on the skill count, that `AGENTS.md` names every published skill and carries no frontmatter (the spec forbids it), that the Cursor rule uses only documented frontmatter fields, and that no `SKILL.md` has acquired agent-specific syntax such as an argument placeholder, a file-include directive or inline shell execution
- The check was itself verified by injecting a `$ARGUMENTS` placeholder into a skill and a skill-count drift into `AGENTS.md` in a scratch copy; both were caught

### Changed
- The README's "Works with" line now links each platform to its entry file, and a new Cross-platform section states plainly what is verified and what is not: the format contracts were read from each tool's documentation and portability is enforced by the check, but the skills have not been executed inside Cursor, Codex CLI or Gemini CLI, which would require those tools installed
- The adapter files ship with the source distribution

## [0.14.0] - 2026-08-30

### Added
- Benchmark framework: `tools/run_benchmarks.py` discovers every skill's validation suite, runs it, and reports pass/fail/skip counts with wall-clock time. The status column distinguishes a suite that ran and failed from one that could not run because a dependency or network is absent, which is the difference between broken code and an unconfigured machine
- Validation suites for the four skills that had none, closing the gap: multiomics-integration (11 assertions), checkpoint-biomarkers (9), radiotherapy-response (11) and epigenomics (16). **All sixteen skills now carry a suite**
- radiotherapy-response tests demonstrate the rank-basis error numerically: ranking within the ten RSI genes gives every sample exactly 1..10 and collapses between-sample variance by roughly 1,800-fold, while still returning a plausible number
- checkpoint-biomarkers tests measure the cohort-dependence claim: after adding ten samples, mean-of-z scores for the original twenty move by up to 0.5285 while rank-based single-sample scores move by exactly 0
- epigenomics tests check each DiffBind claim twice, once against the package's own NEWS file and once that SKILL.md still records it, so a future release that changes the story surfaces in the suite
- multiomics-integration tests confirm mixOmics on CRAN is still 6.3.2 from 2018, that `run_mofa()` carries `use_basilisk = FALSE` read from source, and that per-feature scaling leaves a 200:1 variance imbalance between a 20,000-gene and a 100-protein view

### Fixed
- Three R test runners (cancer-multiomics, immune-deconvolution, survival-analysis) could not execute under `Rscript` at all. They resolved their script directory with a bare `dirname(sys.frame(1)$ofile)`, which errors outside a `source()` call before the intended fallback line can run. Wrapping it in `tryCatch`, as the three newer runners already did, fixes it: cancer-multiomics goes from zero assertions to 27. The benchmark runner found this

## [0.13.0] - 2026-08-30

### Added
- epigenomics skill: ATAC-seq and ChIP-seq from the filtering that precedes peak calling through differential binding, motif enrichment, TF-motif activity and peak-to-gene assignment
- Records three DiffBind 3.x changes verified from the package's own NEWS that alter results without erroring: `dba.count()` now centres on summits by default giving 401 bp intervals where earlier versions did not recentre, the modelling default changed so reproducing a pre-3.0 analysis needs `dba.contrast(design = FALSE)`, and the normalization options `bSubControl`, `bFullLibrarySize`, `filter` and `filterFun` moved from `dba.analyze()` to the new `dba.normalize()` and are silently lost otherwise
- Records two current DiffBind issues: before 3.22.2 a `bSubControl` set in `dba.count()` was not preserved so analysis could silently fall back to control subtraction, and `dba.plotProfile()` has been disabled since 3.22.1 because its backend is uninstallable, returning NULL invisibly
- Records that development moved from MACS2 (last released 2023-07) to MACS3 3.0.4, that ATAC needs `--nomodel` because MACS's paired-peak model assumes point-source ChIP structure, and that combining `BAMPE` with `--shift` double-corrects fragments that are already correctly placed
- States the pre-peak filtering that decides the result: mitochondrial reads routinely take 20-50% of an ATAC library, the ENCODE blacklist otherwise produces confident peaks in every sample, and the Tn5 shift is +4/-5 because Tn5 inserts as a dimer spanning 9 bp
- States that motif background must be GC- and accessibility-matched, that chromVAR reports TF-motif rather than TF activity, that the JASPAR release changes enrichment invisibly (2024 is the latest; 2026 does not exist), and that nearest-TSS assignment is an assumption rather than a target

## [0.12.0] - 2026-08-29

### Added
- radiotherapy-response skill: DNA damage repair profiling by pathway, the Radiosensitivity Index and the Genomic-Adjusted Radiation Dose, post-irradiation immune signatures, and the abscopal effect
- Writes the RSI model out in full because **no package implements it** on CRAN, Bioconductor or PyPI: the ten genes (AR, JUN, STAT1, PRRT2, RELA, ABL1, SUMO1, CDK1, HDAC9, IRF1) with their published coefficients
- Records the two errors that invert the result: the model's inputs are within-sample **ranks** rather than expression values, and a **higher RSI means more radio-resistant** because the score predicts survival fraction at 2 Gy, which the name obscures. Ranking within the ten genes rather than across the transcriptome destroys the signal while still producing plausible output
- Records that GARD is dose-dependent by construction and meaningless without total dose, fractionation and the assumed alpha/beta ratio, and that dose adjustment from RSI or GARD is investigational and directly contested in the literature, so the skill reports scores rather than prescriptions
- Records that DDR is not one pathway, since HR deficiency sensitizes to radiation while MMR deficiency drives MSI instead, that msigdbr renamed `category`/`subcategory` to `collection`/`subcollection`, and that it moved to calendar versioning (10.0.2 to 24.1.0 to 26.1.1) so semantic version pins misbehave
- States plainly that no validated abscopal biomarker panel exists, and that mechanistic correlates should be labelled mechanistic rather than predictive

## [0.11.0] - 2026-08-29

### Added
- checkpoint-biomarkers skill: separating the assay-derived checkpoint biomarkers from the expression-derived ones, PD-L1 scoring and its antibody-clone dependence, TMB and MSI as predictive calls, and the IFN-gamma, TIS and TIDE signatures that RNA can produce
- Corrects a common request directly: **CPS and TPS cannot be computed from expression data**. Both are counts of individual stained cells on an IHC slide, and CPS additionally requires distinguishing a stained tumour cell from a stained lymphocyte or macrophage. Bulk RNA has no cells in it, so `CD274` expression is a correlate of PD-L1 IHC rather than a substitute, and a CPS estimated from expression has no clinical meaning
- Records that PD-L1 assays are not interchangeable (22C3, 28-8, SP142, SP263), that SP142 stains a smaller fraction so the same sample can flip between assays, and that a result without the clone, scoring system and cutoff is not reportable
- Records the GSVA 2.6.6 breaking API change: the package dispatches on parameter objects such as `ssgseaParam()`, and the 1.x `gsva(expr, gene_sets, method = ...)` call no longer exists
- Records that the TIDE web tool returns HTTP 403 to programmatic requests with `tidepy` 1.3.9 as the scripted route, that TIDE expects expression normalized against a control cohort, and that a mean-of-z-scores changes every earlier sample's score when new samples are added

## [0.10.0] - 2026-08-29

### Added
- multiomics-integration skill: choosing an integration method from the question rather than by popularity, the preprocessing that decides whether integration works at all, MOFA+ factor analysis, similarity network fusion, joint clustering with iClusterPlus, supervised integration with DIABLO, and survival models on integrated features
- Records that CRAN carries mixOmics 6.3.2 from 2018 while Bioconductor has 6.36.0, so `install.packages()` silently returns an eight-year-old API, and that SNFtool was last released 2021-06-11
- Records that MOFA2's R package is a front end over the Python solver mofapy2, that `run_mofa()` takes `use_basilisk = FALSE` by default and so uses whatever Python reticulate finds, and that its managed environment pins numpy 1.26.4
- States the preprocessing rules that decide the result: report the sample intersection, centre and scale each view, select features per view because a 20,000-gene view dominates a 100-protein one even after scaling, and use M-values rather than beta-values for variance-based selection
- States the interpretation rules: `num_factors` is an upper bound, a factor loading on one view is that view's internal structure, MOFA Factor 1 is usually purity or sex or batch, SNF returns a similarity matrix rather than clusters, and testing survival across clusters on the samples that defined them is circular

## [0.9.0] - 2026-08-26

### Added
- Phase 4 integration: an audit confirming every cross-link between skills resolves, every published skill carries a SKILL.md, a README and tests, the root README table and badge match the twelve published skills, and each skill is enumerated in all three packaging locations

### Fixed
- **The single-cell-atlas and spatial-transcriptomics suites had never been executed.** Both now run green: 37 and 56 assertions, 0 failures. The blocker was `llvmlite`, which dropped prebuilt Intel-Mac wheels after 0.45.1, so `pip install scanpy` fell back to a source build requiring `cmake`. Pinning `llvmlite==0.45.1` with `numba<0.63` resolves it
- spatial-transcriptomics QC was computed on the wrong matrix. `visium_hne_adata()` ships log-normalized values in `.X` with true counts in `.raw`; mitochondrial percentage off `.X` is 0.92 and meaningless, while off `.raw` it is 15.7. The suite now computes QC from `.raw` and asserts that `.X` is normalized
- spatial-transcriptomics permutation tests failed on macOS with a bare `RuntimeError`/`EOFError`. squidpy goes through joblib, which defaults to the spawn start method, so workers re-imported the test module and re-ran it. Neither `n_jobs=1` nor `JOBLIB_MULTIPROCESSING=0` prevents this; setting the start method to `fork` does
- Both tests READMEs now record the undeclared dependencies a first run exposes: `scikit-misc` for `seurat_v3` HVG selection and `igraph`/`leidenalg` for Leiden clustering, neither of which is a scanpy dependency and both of which fail only at the call site

## [0.8.0] - 2026-08-26

### Added
- Prompt library: ten Claude Code slash commands in `.claude/commands/` that run the repository's protocols, covering nine of the twelve published skills. Each command carries its skill's pitfalls inline, so the protocol travels with the prompt rather than depending on the skill being loaded
- `/analyze-degs`, `/run-gsea`, `/plot-survival`, `/annotate-variants`, `/deconvolve-immune`, `/qc-single-cell`, `/analyze-spatial`, `/fit-dose-response`, `/tile-wsi`, `/query-tcga`
- `.claude/validate_commands.py`, a validator run this session with 13 assertions and 0 failures. It checks frontmatter against the fields Claude Code actually supports, confirms each command points at a skill that is published (via `git ls-files`, not merely present on disk), and catches the argument-numbering trap where `$0` is the first argument and `$1` the second, the opposite of the shell convention
- The commands ship with the source distribution

## [0.7.3] - 2026-08-25

### Added
- biomedical-mcp validation tests: 27 assertions across three Python scripts, executed on 2026-08-25 with 0 failures. These are live-API integration checks that confirm the documented contracts still hold against the GDC, GEO/E-utilities, CIViC, OncoKB and ClinVar services, using urllib only and skipping cleanly when offline. **Every skill in the package now has an executed test suite.**
- The suite confirms the GDC contracts (clinical needs `expand`, pagination is `from`/`size`, expression returns 28,315 file references rather than a matrix, `primary_site` is a list), the GEO contracts (a `gds` UID converts to a GSE accession, the Series Matrix path is computed from the last three digits, and GSE2034 parses to 22,283 probe rows), and the biomarker contracts (CIViC's two evidence paths agree for all 12 BRAF variants, V600E carries PREDICTIVE evidence via its molecular profile, OncoKB is 401 without a token, and ClinVar returns a germline classification)
- This completes the biomedical-mcp skill and the Phase 4 MCP arc: TCGA/GDC, GEO, biomarker databases, and validation

## [0.7.2] - 2026-08-24

### Added
- biomedical-mcp (part 3, biomarker databases): aggregating CIViC, OncoKB and ClinVar for variant clinical significance, with the access, nomenclature and evidence-scale mismatches that make a naive aggregator wrong. All biomarker tool bodies executed against the live APIs, six checks passing
- Records the three access models: CIViC is open GraphQL, OncoKB is token-gated REST (401 without a token, non-commercial licence), and ClinVar is open E-utilities, so a server that hard-fails without the OncoKB token must degrade rather than take down the open sources
- Records that CIViC evidence attaches to a molecular profile rather than a variant, that cross-source variant nomenclature does not match (V600E vs NM_004333.6(BRAF):c.1799T>A), that CIViC A-E, OncoKB 1-4/R1-R2 and ClinVar gold stars are not one scale, and that a ClinVar germline classification is not somatic actionability

### Fixed
- biomedical-mcp: an earlier draft of the CIViC section claimed `evidenceItems(variantId:)` returns zero and that evidence is reachable only through the molecular profile. Verified against the live API, the two paths agree for simple variants (12/12 BRAF variants); the correct reason to use the molecular profile is to keep the compound-condition context, and a variant with no curation returns zero by both paths. The claim was corrected before release

## [0.7.1] - 2026-08-23

### Added
- biomedical-mcp (part 2, GEO): searching GEO through NCBI E-utilities, retrieving expression as a Series Matrix from the FTP server, mapping probe IDs to genes through the GPL platform table, and the RNA-seq exception. All GEO tool bodies executed against the live NCBI API and FTP, six checks passing
- Records the GEO data-shape traps: search returns metadata while values live in a Series Matrix on the FTP, a `gds` UID (200002034) is not the accession (GSE2034), Series Matrix rows are probe IDs not gene symbols, the FTP path is computed by turning the last three digits of the GSE number into `nnn`, and array series carry a real value table (GSE2034 has 22,283 probe rows) while RNA-seq series usually carry values only as supplementary files
- Records that NCBI E-utilities allows 3 requests per second without an API key and 10 with one, and that a Python server should use GEOparse or geofetch rather than the R package GEOquery

## [0.7.0] - 2026-08-23

### Added
- biomedical-mcp skill (part 1, TCGA/GDC): building Model Context Protocol servers that give agents tested access to biomedical databases, covering MCP tool design (service-prefixed verb-led names, type-hints-as-schema, errors in the result object), the GDC REST API behind TCGA with search, mutation and clinical tools, pagination by from/size, and caching keyed on the data release. GEO and biomarker databases follow in later parts
- Records that mcp 2.0.0 is a major version whose server class is `MCPServer` from `mcp.server`, not the 1.x `FastMCP` import, and that a Python MCP server should call the GDC REST API directly rather than wrapping the R package TCGAbiolinks (which is what TCGAbiolinks calls underneath)
- Records the GDC data-shape traps, each checked against the live API (Data Release 46.0): expression is returned as ~28,000 downloadable file references rather than a matrix, clinical fields need `expand=demographic,diagnoses`, `ssms` counts distinct mutations while `ssm_occurrences` counts mutation-in-a-case, and fields such as `primary_site` are lists even when they look scalar

## [0.6.3] - 2026-08-23

### Added
- computational-pathology validation tests: 24 assertions across three Python scripts, executed on 2026-08-23 with 0 failures (26 when a multi-level slide is supplied). The synthetic suites need no data; the OpenSlide suite downloads a ~1.9 MB public test slide at runtime and deletes it, so nothing is committed. **Every skill in the package now has an executed test suite.**
- The suite verifies scikit-image's colour-deconvolution clipping (784 of 1024 random pixels lose a channel; the round trip is 1.11e-16 where nothing clipped and 6.12e-01 where it did), that a saturation threshold keeps pale tissue an intensity threshold discards, that `.convert("RGB")` turns unscanned area black, and OpenSlide's coordinate-frame semantics against the real Aperio CMU-1 slide, whose `level_downsamples` are (1.0, 4.000122, 16.000486) - level 1 is 4.000122 rather than 4, and `get_best_level_for_downsample(4)` returns 0 because it errs toward more resolution

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

[Unreleased]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.15.0...HEAD
[0.15.0]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.14.0...v0.15.0
[0.14.0]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.13.0...v0.14.0
[0.13.0]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.12.0...v0.13.0
[0.12.0]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.11.0...v0.12.0
[0.11.0]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.10.0...v0.11.0
[0.10.0]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.7.3...v0.8.0
[0.7.3]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.7.2...v0.7.3
[0.7.2]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.7.1...v0.7.2
[0.7.1]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.7.0...v0.7.1
[0.7.0]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.6.3...v0.7.0
[0.6.3]: https://github.com/zamushwani/biomedical-ai-skills/compare/v0.6.2...v0.6.3
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
