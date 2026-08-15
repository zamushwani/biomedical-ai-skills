# Validation Tests

Tests establish the baseline that a foundation model has to beat, and verify the two input contracts that fail silently.

**Executed 2026-08-15** on Python 3.11.13 with scanpy 1.11.5, scikit-learn 1.8.0, numpy 1.26.4: **32 assertions, 0 failures.**

## Running

```bash
python run_all.py               # all tests, 2-5 min
python run_all.py vocabulary    # gene identifier matching
python run_all.py tokenization  # Geneformer rank-value encoding
python run_all.py baseline      # HVG+PCA baseline on PBMC 3k
```

Ordered cheapest-first, so the two contract tests run before the clustering benchmark.

## What each test checks

**vocabulary** (13 assertions). Foundation models carry a fixed gene vocabulary and drop unlisted genes without error. Confirms that passing Ensembl IDs to a symbol-based vocabulary matches **0 of 32,738 genes** while the model still returns embeddings. Also checks that duplicate symbols are resolved before matching, and provides the `match_rate()` check every pipeline should surface.

**tokenization** (12 assertions). Reimplements Geneformer's rank-value encoding — normalize by cell total, divide by the gene's corpus median, rank descending, truncate — and compares raw counts against log-normalized input. Also confirms two properties of the encoding: it is invariant to library size, and it is *not* invariant to the corpus medians, which is why V1 and V2 dictionaries cannot be mixed.

**baseline** (7 assertions). Runs HVG+PCA on PBMC 3k and scores KMeans against the 8 reference cell types. KMeans rather than Leiden because k is fixed to the reference count, which is how scIB-style benchmarks score embeddings and removes resolution tuning as a confounder. If a precomputed foundation model embedding is present in `.obsm`, it is scored against the baseline; otherwise that comparison is skipped and the baseline still stands.

## Requirements

```bash
pip install scanpy scikit-learn scipy
```

**numpy must be ≤ 2.1.** scanpy imports numba, and numba refuses numpy ≥ 2.2 with `ImportError: Numba needs NumPy 2.1 or less`. A base environment on numpy 2.4 will fail to import scanpy at all. Use an isolated environment pinned to numpy 1.26.

`torch` and model checkpoints are optional. Weights are multi-gigabyte, so the head-to-head comparison is skipped without them, which is the intended behaviour rather than a failure.

## Expected values

Measured, not quoted.

### Baseline on PBMC 3k (2,638 annotated cells, 8 cell types)

| Configuration | ARI | NMI |
|---|---|---|
| HVG (2000) + PCA, 30 PCs | **0.8789** | **0.8606** |
| HVG (2000) + PCA, 50 PCs | 0.8523 | 0.8341 |
| All genes + PCA, 50 PCs | 0.5468 | 0.7152 |

HVG selection is worth **0.332 ARI** on this dataset — more than most model choices.

### Geneformer tokenization, raw counts vs log-normalized

| Comparison | Value |
|---|---|
| top-1 token identical | 67.3% |
| top-100 gene-set overlap | 70.3% |
| top-100 **order** identical | **0.0%** |
| mean Spearman of that order | **0.008** |

### Vocabulary matching against a symbol vocabulary

| Input | Match rate |
|---|---|
| Gene symbols | 100.0% |
| Ensembl IDs | **0.0%** (0 of 32,738 genes) |
| Vocabulary covering 60% of the panel | 60.0% |

## Notes

- The baseline is the point of this suite. **ARI 0.879 from HVG+PCA** is what any zero-shot embedding must clear to justify its compute, and the published critiques report that they frequently do not.
- Both silent failures produce *valid-looking* output. The tokenization mistake yields a token order with **essentially zero rank correlation** to the correct one, and the vocabulary mistake discards the entire panel. Neither raises an error.
- The baseline test looks for an embedding under `X_scGPT`, `X_geneformer`, `X_uce`, or `X_scvi` in `.obsm`. Generate one and rerun to score it.
