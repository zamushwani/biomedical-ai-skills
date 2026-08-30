# AGENTS.md

Validated protocol files for cancer bioinformatics and multi-omics research.

This repository is a library of **16 SKILL.md files**. Each is a self-contained protocol for one domain: what to run, which parameter values and why, and the mistakes that produce plausible-looking wrong answers. They are plain Markdown with no tool-specific syntax, so any agent can read them directly.

## Using a skill

Read the relevant `skills/<name>/SKILL.md` **before** writing analysis code in that domain, and follow it in place of a default approach. Each file states when it applies in its own `## When to Use This Skill` section.

| Skill | Domain |
|---|---|
| `cancer-multiomics` | Expression, mutation, CNV and methylation for TCGA/GEO |
| `immune-deconvolution` | Immune and stromal composition from bulk RNA-seq |
| `survival-analysis` | Kaplan-Meier, Cox, competing risks, RMST |
| `single-cell-atlas` | scRNA-seq from raw counts to annotation and trajectory |
| `spatial-transcriptomics` | Visium, Xenium, MERSCOPE, CosMx |
| `foundation-models` | scGPT, Geneformer, UCE, and when a linear baseline wins |
| `meta-analysis` | Systematic review, pooling, network meta-analysis |
| `variant-annotation` | VCF normalization, ACMG/AMP, oncogenicity, TMB, MSI |
| `drug-response` | Dose-response fitting, GDSC/CTRP, sensitivity prediction |
| `clinical-nlp` | Clinical text extraction, assertion, de-identification |
| `computational-pathology` | Whole-slide imaging, tiling, MIL, cell segmentation |
| `biomedical-mcp` | MCP servers over GDC, GEO and biomarker databases |
| `multiomics-integration` | MOFA+, SNF, iClusterPlus, DIABLO |
| `checkpoint-biomarkers` | PD-L1, TMB, MSI, IFN-gamma/TIS/TIDE signatures |
| `radiotherapy-response` | DDR profiling, Radiosensitivity Index, GARD |
| `epigenomics` | ATAC-seq and ChIP-seq, peak calling, differential binding |

Every skill carries a `README.md` (a gotchas summary) and a `tests/` directory validating its claims against public data or live registries.

## Working in this repository

The rules that govern changes here live in `CLAUDE.md` and apply to any agent, not only Claude Code. The ones that matter most:

1. **Verify before you write.** Never state a version number, function signature, argument name or default from memory. Check it against the registry and the package source before it goes in a file.
2. **Changing a skill means releasing it.** A committed but unreleased edit leaves `pip install` serving stale content.
3. **Never report success from an intermediate signal.** A green CI run is not evidence the artifact is correct. Verify the artifact itself.
4. **Never claim a test passes unless you executed it.** If it was not run, say "written but not executed" and say why.
5. **Stage explicit paths.** Never `git add .` — untracked personal files sit in the repository root.

## Commands

```bash
python3 tools/run_benchmarks.py               # run every skill's validation suite
python3 tools/check_portability.py            # verify the skills stay tool-neutral
cd skills/<name>/tests && python run_all.py   # one skill (some use run_all.R)
```

## Layout

```
skills/<name>/SKILL.md      the protocol
skills/<name>/README.md     gotchas summary
skills/<name>/tests/        validation suite
src/biomedical_ai_skills/   pip package and CLI
tools/                      benchmark and portability runners
```

## A note on portability

The SKILL.md files deliberately contain no agent-specific syntax: no argument placeholders, no file-include directives, no inline shell execution. That is what lets the same file work in Claude Code, Codex CLI, Cursor, Gemini CLI and anything else that reads Markdown. `tools/check_portability.py` enforces it, so a skill that acquires tool-specific syntax fails the check rather than silently breaking elsewhere.
