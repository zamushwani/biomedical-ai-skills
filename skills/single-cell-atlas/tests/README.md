# Validation Tests

Tests run the single-cell pipeline against 10x PBMC 3k and Kang et al. 2018, and check the output against measured reference values.

These are Python rather than R because both fixtures load in one call from `scanpy`/`pertpy`, with no GitHub-only package installs.

## Running

```bash
python run_all.py               # all tests (~15-25 min)
python run_all.py qc            # QC metrics, filter cascade, doublets, HVGs
python run_all.py clustering    # resolution behaviour, cell types, markers
python run_all.py integration   # Harmony on 8 donors, batch mixing vs biology
```

## What each test checks

**qc**: Loads PBMC 3k raw. Verifies matrix dimensions, median genes/UMI/mito per cell, and that the standard filter reproduces 2,638 cells with the removals attributed correctly. Runs MAD-based filtering and asserts a range rather than an exact count. Checks Scrublet's doublet rate, log-normalization output, and that HVG selection captures canonical markers but not housekeeping genes.

**clustering**: Verifies the 8 reference cell types and their proportions. Clusters at three (n_pcs, resolution) combinations to show that **n_pcs changes the cluster count as much as resolution does** — the same resolution 0.5 gives 9 clusters at 10 PCs and 6-7 at 40 PCs. Then measures marker specificity, including the markers that misfire.

**integration**: Loads 8 donors under control and IFN-beta stimulation. Runs Harmony, then checks both halves of the trade-off: batch neighbourhood purity must drop, and the ground-truth cell types must survive (ARI, NMI, per-type cluster coherence). Over-correction is caught by asserting the cluster count does not collapse.

## Requirements

```bash
pip install "scanpy>=1.12" leidenalg scikit-learn scikit-image
pip install pertpy harmonypy          # integration test
pip install scib-metrics              # optional integration metrics
```

## Expected values (PBMC 3k)

| Check | Expected | Notes |
|-------|----------|-------|
| Raw matrix | 2,700 x 32,738 | exact |
| Genes in >=3 cells | 13,714 | exact |
| Cells after standard QC | 2,638 | Seurat and scanpy filters agree |
| Median genes/cell | 817 | 820 after QC |
| Median UMI/cell | 2,197 | 2,214 after QC |
| Median mitochondrial % | 2.0 | +/- 0.05 |
| MT- genes on panel | 13 | exact |
| Cells removed by mito >=5% | 57 | of 62 total |
| Cells removed by genes >=2500 | 5 | of 62 total |
| 3-MAD filter retention | ~2,520 | range, not exact |
| Scrublet doublet rate | 1-2% | threshold is seed-dependent |
| Leiden res=0.5, n_pcs=10 | 9 clusters | reproduces the Seurat path |
| Leiden res=0.5, n_pcs=40 | 6-7 clusters | CD8 T and NK not yet separated |
| Leiden res=1.0, n_pcs=40 | 9 clusters | stable across seeds |

Cell type proportions: CD4 T 40-48%, CD14+ Mono 15-25%, B 8-15%, CD8 T 6-14%, NK 4-9%, FCGR3A+ Mono 3-8%, DC 0.8-3%, Platelet 0.2-1.5%.

## Notes

- `min_genes=200` removes nothing from PBMC 3k. The lowest-complexity cell has 212 genes. If a pipeline reports cells dropped at that step, the filter is on the wrong axis.
- MAD-based filtering does not reproduce 2,638 and should not be expected to. It keeps ~2,520 at 3 MADs and ~2,635 at 5 MADs.
- `sc.tl.leiden` still defaults to the leidenalg backend with a `FutureWarning`. Tests pin `flavor="igraph", n_iterations=2`.
- `sce.pp.harmony_integrate` is broken against harmonypy 2.0.0, which changed `Z_corr` to cells x PCs while scanpy still transposes unconditionally. The integration test calls `harmonypy.run_harmony` directly and orients by shape.
- `scib_metrics.kbet()` returns a tuple; only `kbet_per_label()` returns a scalar. `pcr_comparison()` needs integer codes with `categorical=True`.
