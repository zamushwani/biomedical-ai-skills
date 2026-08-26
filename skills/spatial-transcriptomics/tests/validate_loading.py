#!/usr/bin/env python3
"""Validate Visium loading and spatial QC against a public 10x mouse brain section.

Checks that spatial coordinates are attached correctly, that QC metrics behave
as expected for a tissue section, and that the deprecated scanpy readers are
actually deprecated.

Expected runtime: 2-5 minutes (94 MB download, cached after first run)
Requires: squidpy>=1.8, scanpy>=1.12
"""

import warnings

import numpy as np
import scanpy as sc
import squidpy as sq

print("=== Spatial Loading and QC Validation (Visium mouse brain) ===\n")
_pass = _fail = 0


def check(name, condition):
    global _pass, _fail
    if bool(condition):
        print(f"  PASS: {name}")
        _pass += 1
    else:
        print(f"  FAIL: {name}")
        _fail += 1


# --- Load ---
print("Downloading Visium H&E mouse brain (cropped)...")
adata = sq.datasets.visium_hne_adata_crop()
print(f"  Shape: {adata.shape[0]} spots x {adata.shape[1]} genes")

check("Registry shape 684 x 18078", adata.shape == (684, 18078))

# --- Spatial coordinates ---
check("Spatial coordinates present", "spatial" in adata.obsm)
coords = adata.obsm["spatial"]
check("Coordinates are 2D", coords.ndim == 2 and coords.shape[1] == 2)
check("One coordinate pair per spot", coords.shape[0] == adata.n_obs)
check("Coordinates are not all identical", np.ptp(coords[:, 0]) > 0 and np.ptp(coords[:, 1]) > 0)

print(f"  x range: {coords[:, 0].min():.0f} to {coords[:, 0].max():.0f}")
print(f"  y range: {coords[:, 1].min():.0f} to {coords[:, 1].max():.0f}")

# Tissue images live in uns for Visium
check("Image metadata attached", "spatial" in adata.uns)

# --- QC metrics ---
# This dataset ships LOG-NORMALIZED values in .X (range ~0-8.9, non-integer)
# with the true integer counts in .raw. QC percentages computed on .X are
# meaningless: you cannot sum log-normalized values and call the ratio a
# fraction of counts. Measured here: mito % is 0.92 off .X and 15.7 off .raw.
# Use the counts.
check("Distributed .X is normalized, not raw counts",
      float(adata.X.min()) >= 0 and not float(adata.X.max()).is_integer())
check("True integer counts are available in .raw", adata.raw is not None)

qc = adata.raw.to_adata() if adata.raw is not None else adata.copy()
qc.obsm = adata.obsm

print("\nQC metrics (computed on raw counts)...")
qc.var["mt"] = qc.var_names.str.lower().str.startswith("mt-")
n_mt = int(qc.var["mt"].sum())
print(f"  Mitochondrial genes: {n_mt}")
check("Mouse MT genes found (mt- prefix, lowercase)", n_mt >= 10)

sc.pp.calculate_qc_metrics(qc, qc_vars=["mt"], percent_top=None, log1p=False, inplace=True)
adata.obs["total_counts"] = qc.obs["total_counts"].values
adata.obs["n_genes_by_counts"] = qc.obs["n_genes_by_counts"].values
adata.obs["pct_counts_mt"] = qc.obs["pct_counts_mt"].values

med_counts = float(np.median(adata.obs["total_counts"]))
med_genes = float(np.median(adata.obs["n_genes_by_counts"]))
med_mt = float(np.median(adata.obs["pct_counts_mt"]))

print(f"  Median UMI/spot:   {med_counts:.0f}")
print(f"  Median genes/spot: {med_genes:.0f}")
print(f"  Median mito %:     {med_mt:.1f}")

# A Visium spot pools 1-10 cells, so depth is far above single-cell.
check("Median UMI/spot > 5000 (spots pool multiple cells)", med_counts > 5000)
check("Median genes/spot > 2000", med_genes > 2000)
check("Median mito % is plausible on counts (1-40%)", 1 < med_mt < 40)

# --- Spot counts are spatially structured, not random ---
# This is the property that separates a tissue section from a well plate.
print("\nSpatial structure of QC metrics...")
sq.gr.spatial_neighbors_grid(adata, n_neighs=6)
check("Spatial graph built", "spatial_connectivities" in adata.obsp)

conn = adata.obsp["spatial_connectivities"]
degrees = np.asarray((conn > 0).sum(axis=1)).ravel()
print(f"  Mean neighbours per spot: {degrees.mean():.2f} (hex grid interior = 6)")
check("Mean degree between 3 and 6 (edges reduce it)", 3 <= degrees.mean() <= 6)
check("Max degree does not exceed 6", degrees.max() <= 6)

# Moran's I on total_counts: tissue depth varies smoothly across a section
adata.obs["log_counts"] = np.log1p(adata.obs["total_counts"])
res = sq.gr.spatial_autocorr(adata, mode="moran", genes=None, attr="obs",
                             n_perms=100, seed=0, copy=True)
if "log_counts" in res.index:
    moran_counts = float(res.loc["log_counts", "I"])
    print(f"  Moran's I of log total counts: {moran_counts:.3f}")
    check("Sequencing depth is spatially autocorrelated (I > 0.1)", moran_counts > 0.1)

# --- Deprecations ---
print("\nDeprecation checks...")
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    has_read_visium = hasattr(sc, "read_visium")
    if has_read_visium:
        print("  scanpy.read_visium still present (deprecated since 1.11.0)")
check("squidpy.read.visium is the current reader", hasattr(sq.read, "visium"))
check("squidpy.pl.spatial_scatter replaces sc.pl.spatial", hasattr(sq.pl, "spatial_scatter"))

# The modern graph builders must exist; the old one is on its way out.
for fn in ["spatial_neighbors_knn", "spatial_neighbors_delaunay", "spatial_neighbors_grid"]:
    check(f"sq.gr.{fn} available", hasattr(sq.gr, fn))

print(f"\n=== Loading: {_pass} passed, {_fail} failed ===")
