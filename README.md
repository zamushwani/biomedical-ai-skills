<div align="center">

# Biomedical Skills

SKILL.md files for cancer bioinformatics. Drop one into your project and your AI coding agent handles TCGA data, normalization, and statistics correctly.

[![GitHub Stars](https://img.shields.io/github/stars/zamushwani/biomedical-ai-skills?style=for-the-badge&logo=github&logoColor=white&labelColor=1a1a2e&color=00d9ff)](https://github.com/zamushwani/biomedical-ai-skills/stargazers)
[![License](https://img.shields.io/github/license/zamushwani/biomedical-ai-skills?style=for-the-badge&labelColor=1a1a2e&color=4ecdc4)](https://github.com/zamushwani/biomedical-ai-skills/blob/main/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/zamushwani/biomedical-ai-skills?style=for-the-badge&logo=git&logoColor=white&labelColor=1a1a2e&color=ff6b6b)](https://github.com/zamushwani/biomedical-ai-skills/commits/main)

[![Skills](https://img.shields.io/badge/Skills-7-00d9ff?style=flat-square&labelColor=1a1a2e)](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills)
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
| [`meta-analysis`](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/meta-analysis/) | Systematic review from protocol to synthesis — PROSPERO pre-specification, PICO search construction (MeSH, Emtree, [Cochrane CHSSS](https://training.cochrane.org/handbook)), deduplication ([synthesisr](https://cran.r-project.org/package=synthesisr)), two-reviewer screening with [kappa](https://cran.r-project.org/package=irr), [PRISMA 2020](https://www.prisma-statement.org/) flow diagrams, data extraction, risk of bias ([RoB 2](https://www.riskofbias.info/), ROBINS-I, ROBINS-E, [robvis](https://cran.r-project.org/package=robvis)), pooling with [metafor](https://cran.r-project.org/package=metafor) (REML, Knapp-Hartung, prediction intervals), subgroup analysis, meta-regression, small-study effects, network meta-analysis ([netmeta](https://cran.r-project.org/package=netmeta), transitivity, inconsistency, rankings) and GRADE/CINeMA certainty | [BCG](https://github.com/zamushwani/biomedical-ai-skills/tree/main/skills/meta-analysis/tests/) |

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
