# Validation Tests

Tests run the spatial pipeline against public 10x Visium mouse brain and an imaging mass cytometry dataset.

## Running

```bash
python run_all.py               # all tests (~8-15 min)
python run_all.py neighbors     # graph builders, neighbourhood enrichment (1.6 MB)
python run_all.py loading       # Visium loading, spatial QC, deprecations (94 MB)
python run_all.py svg           # Moran's I, marker ranking, graph sensitivity
```

Tests are ordered cheapest-download-first, so `neighbors` runs before the Visium downloads.

## What each test checks

**neighbors**: Builds kNN, Delaunay, and radius graphs on the same coordinates and shows they differ in mean degree and degree variance. Runs neighbourhood enrichment on two of them and verifies the results correlate but are **not** identical. This is the point of the test: enrichment is a property of the graph you built, not of the tissue.

**loading**: Verifies spatial coordinates attach correctly and are two-dimensional, that Visium spot depth is far above single-cell depth (spots pool 1-10 cells), that mouse mitochondrial genes are found with the lowercase `mt-` prefix, and that sequencing depth is spatially autocorrelated across a section. Also asserts the current squidpy readers exist, since the scanpy ones are deprecated.

**svg**: Computes Moran's I and checks it is bounded, sorted, and that anatomically restricted genes (Mbp and Plp1 in white matter, Ttr in choroid plexus) outrank housekeeping genes. Then shows that a large fraction of genes pass FDR < 0.05, which is why rank cutoffs are preferred over significance thresholds.

## Requirements

```bash
pip install "squidpy>=1.8" "scanpy>=1.12"
```

Both require **Python >= 3.12**. Python 3.11 was dropped in squidpy 1.8.3 and spatialdata 0.8.0.

## Datasets

| Test | Dataset | Size |
|------|---------|------|
| neighbors | `sq.datasets.imc()` — 4,668 cells x 34 channels | 1.6 MB |
| loading, svg | `sq.datasets.visium_hne_adata_crop()` — 684 spots x 18,078 genes | 94 MB |

Downloads are cached under `scanpy.settings.datasetdir` after the first run.

## Expected behaviour

| Check | Expected |
|-------|----------|
| IMC shape | 4,668 x 34 |
| Visium crop shape | 684 x 18,078 |
| Visium median UMI/spot | > 5,000 (spots pool multiple cells) |
| Hex grid mean degree | 3-6 (edge spots lower the mean) |
| Delaunay mean degree | 4-8 (planar triangulation averages just under 6) |
| Radius graph degree SD | higher than kNN (kNN forces uniform degree) |
| Self-enrichment diagonal | positive (same-type cells cluster in tissue) |
| Delaunay vs kNN enrichment | correlated (r > 0.5) but not identical |
| Top Moran's I | > 0.3 |
| Mbp / Plp1 / Ttr | rank above Actb and Gapdh |

## Notes

- `sq.gr.spatial_neighbors` is deprecated since squidpy 1.7.0 and removed in 1.9.0. These tests use the mode-specific builders (`spatial_neighbors_knn`, `_delaunay`, `_radius`, `_grid`).
- Mouse mitochondrial genes use the lowercase `mt-` prefix, not `MT-`. Using the human pattern silently returns zero MT genes.
- squidpy 1.8.2 changed the Geary's C variance calculation, so `mode="geary"` results are not comparable across that version boundary. These tests use Moran's I only.
- The SVG test deliberately asserts that FDR significance is a poor filter. Benchmarking found p-value calibration broken for most SVG methods, so ranking is the recommended selection.

## Execution status

**Executed 2026-08-26: 56 assertions, 0 failures** (Python 3.13.5, squidpy 1.8.3, scanpy 1.12.3).

Running these for the first time exposed two real bugs, both now fixed:

**QC was computed on the wrong matrix.** `sq.datasets.visium_hne_adata()` ships **log-normalized** values in `.X` (range 0–8.86, non-integer) with the true integer counts in `.raw` (range 0–23,703). Mitochondrial percentage computed off `.X` is 0.92 and meaningless — you cannot sum log-normalized values and call the ratio a fraction of counts. Off `.raw` it is **15.7**, comfortably inside the plausible band. The suite now computes QC from `.raw` and asserts that `.X` is normalized.

**The permutation tests died on macOS.** squidpy's `spatial_autocorr` and `nhood_enrichment` go through joblib, which defaults to the **spawn** start method on macOS: workers re-import the test module, re-run it top to bottom, and the run fails with a bare `RuntimeError`/`EOFError`. Neither `n_jobs=1` nor `JOBLIB_MULTIPROCESSING=0` prevents it. Setting the start method to `fork` does, because fork does not re-import the parent module.

### Installing on an Intel Mac

Same `llvmlite` constraint as the single-cell suite:

```bash
pip install "llvmlite==0.45.1" "numba<0.63"
pip install squidpy
```

The Visium dataset (~400 MB) downloads to `tests/data/` on first run and is gitignored.
