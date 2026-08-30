<div align="center">

# Biomedical Skills

SKILL.md files for cancer bioinformatics. Drop one into your project and your AI coding agent handles TCGA data, normalization, and statistics correctly.

[![GitHub Stars](https://img.shields.io/github/stars/zamushwani/biomedical-ai-skills?style=for-the-badge&logo=github&logoColor=white&labelColor=1a1a2e&color=00d9ff)](https://github.com/zamushwani/biomedical-ai-skills/stargazers)
[![License](https://img.shields.io/github/license/zamushwani/biomedical-ai-skills?style=for-the-badge&labelColor=1a1a2e&color=4ecdc4)](https://github.com/zamushwani/biomedical-ai-skills/blob/main/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/zamushwani/biomedical-ai-skills?style=for-the-badge&logo=git&logoColor=white&labelColor=1a1a2e&color=ff6b6b)](https://github.com/zamushwani/biomedical-ai-skills/commits/main)

[![Skills](https://img.shields.io/badge/Skills-16-00d9ff?style=flat-square&labelColor=1a1a2e)](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills)
[![PyPI](https://img.shields.io/pypi/v/biomedical-ai-skills?style=flat-square&logo=pypi&logoColor=white&labelColor=1a1a2e&color=00d9ff)](https://pypi.org/project/biomedical-ai-skills/)
[![Downloads](https://img.shields.io/pypi/dm/biomedical-ai-skills?style=flat-square&labelColor=1a1a2e&color=4ecdc4)](https://pypi.org/project/biomedical-ai-skills/)
[![Python](https://img.shields.io/pypi/pyversions/biomedical-ai-skills?style=flat-square&logo=python&logoColor=white&labelColor=1a1a2e)](https://pypi.org/project/biomedical-ai-skills/)
[![R](https://img.shields.io/badge/R-≥_4.3-276DC3?style=flat-square&logo=r&logoColor=white&labelColor=1a1a2e)](https://www.r-project.org/)
[![Bioconductor](https://img.shields.io/badge/Bioconductor-3.19-87b13f?style=flat-square&labelColor=1a1a2e)](https://bioconductor.org/)
[![TCGA](https://img.shields.io/badge/TCGA-GDC_Portal-e84d3c?style=flat-square&labelColor=1a1a2e)](https://portal.gdc.cancer.gov/)

**Works with** Claude Code · Cursor · Codex CLI · Gemini CLI

<img src="https://raw.githubusercontent.com/zamushwani/biomedical-ai-skills/main/assets/workflow.png" width="820" alt="Browse skills, copy SKILL.md to your project, the agent reads domain protocols, you get correct code with tested parameters">

</div>

---

## Skills

| Skill | Description | Tests |
|-------|-------------|-------|
| [`cancer-multiomics`](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/cancer-multiomics/) | Multi-omics analysis for [TCGA](https://portal.gdc.cancer.gov/)/[GEO](https://www.ncbi.nlm.nih.gov/geo/) — expression ([DESeq2](https://bioconductor.org/packages/DESeq2/)), mutation ([maftools](https://bioconductor.org/packages/maftools/)), CNV ([GISTIC2](https://www.broadinstitute.org/cancer/cga/gistic)), methylation ([minfi](https://bioconductor.org/packages/minfi/), [DMRcate](https://bioconductor.org/packages/DMRcate/)) | [TCGA-LUAD](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/cancer-multiomics/tests/) |
| [`immune-deconvolution`](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/immune-deconvolution/) | Tumor microenvironment estimation via [immunedeconv](https://omnideconv.org/immunedeconv/) — [quanTIseq](https://icbi.i-med.ac.at/software/quantiseq/doc/), [EPIC](https://github.com/GfellerLab/EPIC), CIBERSORT, [xCell](https://xcell.ucsf.edu/), [MCP-counter](https://github.com/ebecht/MCPcounter), TIMER, ESTIMATE, tumor purity correction | [TCGA-BRCA](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/immune-deconvolution/tests/) |
| [`survival-analysis`](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/survival-analysis/) | Time-to-event analysis — Kaplan-Meier ([ggsurvfit](https://www.danieldsjoberg.com/ggsurvfit/)), Cox PH ([survival](https://cran.r-project.org/package=survival)), competing risks ([tidycmprsk](https://mskcc-epi-bio.github.io/tidycmprsk/)), RMST ([survRM2](https://cran.r-project.org/package=survRM2)), optimal cutpoints, forest plots | [TCGA-GBM](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/survival-analysis/tests/) |
| [`single-cell-atlas`](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/single-cell-atlas/) | Full scRNA-seq pipeline — QC, doublet detection, normalization, batch integration ([Harmony](https://portals.broadinstitute.org/harmony/), [scVI](https://scvi-tools.org/)), Leiden clustering, annotation ([CellTypist](https://www.celltypist.org/)), pseudobulk DE, trajectory ([scVelo](https://scvelo.readthedocs.io/), [Monocle3](https://cole-trapnell-lab.github.io/monocle3/)), cell communication ([CellChat](https://github.com/jinworks/CellChat), [LIANA](https://liana-py.readthedocs.io/)), TF activity ([decoupleR](https://decoupler-py.readthedocs.io/)). [Seurat v5](https://satijalab.org/seurat/) + [scanpy](https://scanpy.readthedocs.io/) | [PBMC 3k](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/single-cell-atlas/tests/) |
| [`spatial-transcriptomics`](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/spatial-transcriptomics/) | Visium, Visium HD, Xenium, MERSCOPE, CosMx — loading ([spatialdata](https://spatialdata.scverse.org/), [VisiumIO](https://bioconductor.org/packages/VisiumIO/)), spatially local QC ([SpotSweeper](https://bioconductor.org/packages/SpotSweeper/)), spatially variable genes ([squidpy](https://squidpy.readthedocs.io/), [nnSVG](https://bioconductor.org/packages/nnSVG/)), deconvolution ([RCTD](https://bioconductor.org/packages/spacexr/), [cell2location](https://cell2location.readthedocs.io/)), domains ([BANKSY](https://bioconductor.org/packages/Banksy/), [CellCharter](https://cellcharter.readthedocs.io/)), communication ([LIANA+](https://liana-py.readthedocs.io/)) | [Visium mouse brain](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/spatial-transcriptomics/tests/) |
| [`foundation-models`](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/foundation-models/) | [scGPT](https://github.com/bowang-lab/scGPT), [Geneformer](https://huggingface.co/ctheodoris/Geneformer), [UCE](https://github.com/snap-stanford/UCE), [TranscriptFormer](https://github.com/czi-ai/transcriptformer), [Nicheformer](https://github.com/theislab/nicheformer), [Tahoe-x1](https://github.com/tahoebio/tahoe-x1) — zero-shot embeddings, fine-tuning for annotation, in-silico perturbation, and the benchmark evidence for when a linear baseline wins instead | [PBMC 3k](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/foundation-models/tests/) |
| [`variant-annotation`](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/variant-annotation/) | VCF normalization and filtering ([bcftools](https://samtools.github.io/bcftools/)), functional annotation ([VEP](https://www.ensembl.org/info/docs/tools/vep/), SnpEff, ANNOVAR), germline classification ([ACMG/AMP](https://www.clinicalgenome.org/tools/clingen-variant-classification-guidance/) with ClinGen refinements), somatic oncogenicity (ClinGen/CGC/VICC) and clinical tiers (AMP/ASCO/CAP, [OncoKB](https://www.oncokb.org/), [CIViC](https://civicdb.org/)), TMB, MSI ([msisensor-pro](https://github.com/xjtu-omics/msisensor-pro)), neoantigen prediction ([pVACtools](https://pvactools.readthedocs.io/)) | [TCGA-LAML](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/variant-annotation/tests/) |
| [`drug-response`](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/drug-response/) | Dose-response modeling and drug sensitivity prediction — IC50/AUC curve fitting ([drc](https://cran.r-project.org/package=drc), [nplr](https://cran.r-project.org/package=nplr), gdscIC50), GDSC/CTRP/PRISM retrieval and cross-dataset harmonization ([PharmacoGx](https://bioconductor.org/packages/PharmacoGx/), [DepMap](https://depmap.org/portal/)), sensitivity prediction with regularized regression, tissue-corrected pharmacogenomic biomarkers | [simulated](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/drug-response/tests/) |
| [`clinical-nlp`](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/clinical-nlp/) | Information extraction from clinical free text — note sectioning and biomedical NER ([scispaCy](https://allenai.github.io/scispacy/), [cTAKES](https://ctakes.apache.org/)), assertion and negation via ConText ([medspaCy](https://github.com/medspacy/medspacy)), concept normalization to [UMLS](https://www.nlm.nih.gov/research/umls/index.html) and ICD-10 ([MedCAT](https://github.com/CogStack/MedCAT)), temporal relations, adverse events, de-identification ([Presidio](https://microsoft.github.io/presidio/)) | [synthetic](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/clinical-nlp/tests/) |
| [`computational-pathology`](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/computational-pathology/) | Whole-slide imaging — reading vendor formats ([OpenSlide](https://openslide.org/)), the level-0 coordinate frame and microns-per-pixel semantics behind most WSI bugs, tissue detection, tiling, stain normalization ([torchstain](https://github.com/EIDOSLAB/torchstain), [HistomicsTK](https://digitalslidearchive.github.io/HistomicsTK/)), H&E colour deconvolution, pathology foundation models as tile encoders ([UNI](https://huggingface.co/MahmoodLab/UNI), [CONCH](https://huggingface.co/MahmoodLab/CONCH), [Phikon](https://huggingface.co/owkin/phikon-v2)) with their gating and licence constraints, multiple instance learning ([CLAM](https://github.com/mahmoodlab/CLAM), DSMIL, TransMIL), cell segmentation ([StarDist](https://github.com/stardist/stardist), HoVer-Net), and spatial statistics on cell positions ([squidpy](https://squidpy.readthedocs.io/)) | [validated](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/computational-pathology/tests/) |
| [`biomedical-mcp`](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/biomedical-mcp/) | Building [Model Context Protocol](https://modelcontextprotocol.io/) servers that give AI agents tested access to biomedical databases — MCP tool design ([mcp](https://pypi.org/project/mcp/) 2.0), the [GDC REST API](https://api.gdc.cancer.gov/) behind TCGA (projects, mutations, clinical), [GEO](https://www.ncbi.nlm.nih.gov/geo/) search and Series Matrix retrieval, aggregating the [CIViC](https://civicdb.org/), [OncoKB](https://www.oncokb.org/) and [ClinVar](https://www.ncbi.nlm.nih.gov/clinvar/) biomarker databases, pagination and caching, and the data-shape traps (GDC expression is file references, GEO rows are probes not genes, CIViC evidence lives on molecular profiles, OncoKB is token-gated, cross-source nomenclature does not match) | [validated](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/biomedical-mcp/tests/) |
| [`multiomics-integration`](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/multiomics-integration/) | Joint analysis across molecular layers — method selection, the preprocessing that decides whether integration works (sample intersection, per-view scaling, feature-count imbalance), factor analysis ([MOFA2](https://biofam.github.io/MOFA2/)), similarity network fusion ([SNFtool](https://cran.r-project.org/package=SNFtool)), joint clustering ([iClusterPlus](https://bioconductor.org/packages/iClusterPlus/)), supervised integration ([DIABLO](http://mixomics.org/mixdiablo/)), and survival on integrated features | [validated](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/multiomics-integration/tests/) |
| [`checkpoint-biomarkers`](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/checkpoint-biomarkers/) | Predictive biomarkers for immune checkpoint blockade — why PD-L1 [CPS/TPS](https://arupconsult.com/ati/pd-l1-immunohistochemistry) are IHC scores that expression cannot reproduce, antibody-clone dependence, TMB and MSI as assay-derived calls, and the expression signatures that RNA can give you (IFN-γ, TIS, [TIDE](https://github.com/jingxinfu/TIDEpy)) with [GSVA](https://bioconductor.org/packages/GSVA/) 2.x scoring | [validated](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/checkpoint-biomarkers/tests/) |
| [`radiotherapy-response`](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/radiotherapy-response/) | Genomic predictors of radiation response — the Radiosensitivity Index written out in full (no package implements it), why its inputs are ranks and why higher means *resistant*, GARD and its dose dependence, DNA damage repair scored by pathway rather than as one block ([msigdbr](https://cran.r-project.org/package=msigdbr)), post-irradiation immune signatures, and the abscopal effect's lack of a validated predictor | [validated](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/radiotherapy-response/tests/) |
| [`epigenomics`](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/epigenomics/) | ATAC-seq and ChIP-seq — the filtering before peak calling (chrM, [ENCODE blacklist](https://github.com/Boyle-Lab/Blacklist), Tn5 shift), ATAC peak calling with [MACS3](https://macs3-project.github.io/MACS/), differential binding and the [DiffBind](https://bioconductor.org/packages/DiffBind/) 3.x defaults that silently change results, motif enrichment and [chromVAR](https://bioconductor.org/packages/chromVAR/) TF-motif activity, and peak-to-gene assignment where nearest is not target | [validated](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/epigenomics/tests/) |
| [`meta-analysis`](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/meta-analysis/) | Systematic review from protocol to synthesis — PROSPERO pre-specification, PICO search construction (MeSH, Emtree, [Cochrane CHSSS](https://training.cochrane.org/handbook)), deduplication ([synthesisr](https://cran.r-project.org/package=synthesisr)), two-reviewer screening with [kappa](https://cran.r-project.org/package=irr), [PRISMA 2020](https://www.prisma-statement.org/) flow diagrams, data extraction, risk of bias ([RoB 2](https://www.riskofbias.info/), ROBINS-I, ROBINS-E, [robvis](https://cran.r-project.org/package=robvis)), pooling with [metafor](https://cran.r-project.org/package=metafor) (REML, Knapp-Hartung, prediction intervals), subgroup analysis, meta-regression, small-study effects, network meta-analysis ([netmeta](https://cran.r-project.org/package=netmeta), transitivity, inconsistency, rankings) and GRADE/CINeMA certainty | [BCG](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/meta-analysis/tests/) |

## Benchmarks

Every skill carries a validation suite. One runner executes them all and reports pass/fail/skip and wall-clock time per skill:

```bash
python3 tools/run_benchmarks.py                 # every skill
python3 tools/run_benchmarks.py epigenomics     # one skill
```

The table distinguishes a suite that **ran and failed** from one that **could not run** because a dependency or network is absent — the difference that decides whether a red cell means broken code or an unconfigured machine.


## Slash commands

Ten Claude Code slash commands that run the protocols above. Clone the repo and they work immediately — commands live in `.claude/commands/`, which Claude Code picks up per project.

| Command | Arguments | Skill it follows |
|---|---|---|
| [`/analyze-degs`](https://github.com/zamushwani/biomedical-ai-skills/blob/main/.claude/commands/analyze-degs.md) | `[counts-file] [condition-column]` | cancer-multiomics |
| [`/run-gsea`](https://github.com/zamushwani/biomedical-ai-skills/blob/main/.claude/commands/run-gsea.md) | `[de-results-file] [gene-set-collection]` | cancer-multiomics |
| [`/plot-survival`](https://github.com/zamushwani/biomedical-ai-skills/blob/main/.claude/commands/plot-survival.md) | `[clinical-file] [group-column]` | survival-analysis |
| [`/annotate-variants`](https://github.com/zamushwani/biomedical-ai-skills/blob/main/.claude/commands/annotate-variants.md) | `[vcf-file] [tumour-type]` | variant-annotation |
| [`/deconvolve-immune`](https://github.com/zamushwani/biomedical-ai-skills/blob/main/.claude/commands/deconvolve-immune.md) | `[expression-file] [method]` | immune-deconvolution |
| [`/qc-single-cell`](https://github.com/zamushwani/biomedical-ai-skills/blob/main/.claude/commands/qc-single-cell.md) | `[h5ad-file]` | single-cell-atlas |
| [`/analyze-spatial`](https://github.com/zamushwani/biomedical-ai-skills/blob/main/.claude/commands/analyze-spatial.md) | `[data-path] [platform]` | spatial-transcriptomics |
| [`/fit-dose-response`](https://github.com/zamushwani/biomedical-ai-skills/blob/main/.claude/commands/fit-dose-response.md) | `[data-file]` | drug-response |
| [`/tile-wsi`](https://github.com/zamushwani/biomedical-ai-skills/blob/main/.claude/commands/tile-wsi.md) | `[slide-path] [target-mpp]` | computational-pathology |
| [`/query-tcga`](https://github.com/zamushwani/biomedical-ai-skills/blob/main/.claude/commands/query-tcga.md) | `[project-id] [gene]` | biomedical-mcp |

```
/annotate-variants sample.vcf melanoma
/plot-survival clinical.tsv IDH_status
/tile-wsi slide.svs 0.5
```

Each command carries the pitfalls from its skill inline, so the protocol travels with the prompt rather than depending on the skill being loaded. Arguments are optional — a command invoked bare asks for what it needs.


## Quick start

```bash
pip install biomedical-ai-skills
```

From your project directory:

```bash
biomedical-skills list                                    # what's available
biomedical-skills install spatial-transcriptomics         # -> .claude/skills/
biomedical-skills install --all                           # everything
biomedical-skills install cancer-multiomics --target .cursor/skills
```

No dependencies, so it installs in a couple of seconds.

Or skip the package and copy the files directly:

```bash
git clone https://github.com/zamushwani/biomedical-ai-skills.git

mkdir -p your-project/.claude/skills/cancer-multiomics
cp skills/cancer-multiomics/SKILL.md your-project/.claude/skills/cancer-multiomics/
```

## What's a SKILL.md?

A file that gives AI coding agents domain knowledge for a specific field. The agent reads it before generating code and follows tested protocols instead of guessing at parameters.

**Without a skill:** agent runs DESeq2 without pre-filtering, skips `lfcShrink()`, uses wrong contrast syntax.
**With a skill:** agent pre-filters low-count genes, applies `apeglm` shrinkage, handles TCGA barcodes correctly.

## Contributing

See [CONTRIBUTING.md](https://github.com/zamushwani/biomedical-ai-skills/blob/main/CONTRIBUTING.md) and [SECURITY.md](https://github.com/zamushwani/biomedical-ai-skills/blob/main/SECURITY.md).

## License

[MIT](https://github.com/zamushwani/biomedical-ai-skills/blob/main/LICENSE)
