import multiprocessing as mp

# squidpy's permutation tests go through joblib. On macOS the default start
# method is spawn, so workers re-import this module, re-run it top to bottom,
# and the run dies with a RuntimeError/EOFError rather than a useful message.
# n_jobs=1 and JOBLIB_MULTIPROCESSING=0 do not prevent it; switching to fork
# does, because fork does not re-import the parent module.
try:
    mp.set_start_method("fork", force=True)
except RuntimeError:
    pass

#!/usr/bin/env python3
"""Validate spatial graph construction and neighbourhood statistics.

Uses an imaging mass cytometry dataset (4,668 cells, 34 channels, 1.6 MB) so
the test runs fast and exercises the single-cell-resolution path rather than
the spot-grid path.

Checks that the graph builder determines the answer, which is the single most
misunderstood property of neighbourhood enrichment.

Expected runtime: 1-3 minutes (1.6 MB download)
Requires: squidpy>=1.8
"""

import numpy as np
import squidpy as sq

print("=== Spatial Graph and Neighbourhood Validation (IMC) ===\n")
_pass = _fail = 0


def check(name, condition):
    global _pass, _fail
    if bool(condition):
        print(f"  PASS: {name}")
        _pass += 1
    else:
        print(f"  FAIL: {name}")
        _fail += 1


print("Downloading IMC dataset...")
adata = sq.datasets.imc()
print(f"  Shape: {adata.shape[0]} cells x {adata.shape[1]} channels")

check("Registry shape 4668 x 34", adata.shape == (4668, 34))
check("Spatial coordinates present", "spatial" in adata.obsm)
check("Cell type annotation present", "cell type" in adata.obs or "cell_type" in adata.obs)

cluster_key = "cell type" if "cell type" in adata.obs else "cell_type"
n_types = adata.obs[cluster_key].nunique()
print(f"  Cell types: {n_types}")
check("At least 5 cell types", n_types >= 5)

# --- Graph builders ---
print("\nGraph builders...")


def mean_degree(ad):
    conn = ad.obsp["spatial_connectivities"]
    return float(np.asarray((conn > 0).sum(axis=1)).ravel().mean())


a_knn = adata.copy()
sq.gr.spatial_neighbors_knn(a_knn, n_neighs=6)
deg_knn = mean_degree(a_knn)
print(f"  kNN (n_neighs=6):  mean degree {deg_knn:.2f}")
# kNN is symmetrized, so mean degree exceeds n_neighs
check("kNN mean degree >= 6", deg_knn >= 6)

a_del = adata.copy()
sq.gr.spatial_neighbors_delaunay(a_del)
deg_del = mean_degree(a_del)
print(f"  Delaunay:          mean degree {deg_del:.2f}")
# Planar Delaunay triangulation averages just under 6 neighbours
check("Delaunay mean degree 4-8", 4 <= deg_del <= 8)

a_rad = adata.copy()
coords = adata.obsm["spatial"]
span = float(np.ptp(coords[:, 0]))
sq.gr.spatial_neighbors_radius(a_rad, radius=span / 40)
deg_rad = mean_degree(a_rad)
print(f"  Radius (span/40):  mean degree {deg_rad:.2f}")
check("Radius graph produces some edges", deg_rad > 0)

# Radius graphs have heterogeneous degree; kNN forces uniformity. This is the
# reason the two disagree on dense vs sparse regions.
conn_rad = a_rad.obsp["spatial_connectivities"]
deg_rad_all = np.asarray((conn_rad > 0).sum(axis=1)).ravel()
conn_knn = a_knn.obsp["spatial_connectivities"]
deg_knn_all = np.asarray((conn_knn > 0).sum(axis=1)).ravel()
print(f"  Degree SD: kNN {deg_knn_all.std():.2f} vs radius {deg_rad_all.std():.2f}")
check("Radius graph has more variable degree than kNN",
      deg_rad_all.std() > deg_knn_all.std())

# --- Neighbourhood enrichment ---
print("\nNeighbourhood enrichment...")
# n_jobs=1: the permutation test otherwise spawns workers that re-import
# this module. On macOS (spawn start method) that recurses and dies with
# a RuntimeError/EOFError rather than a useful message.
sq.gr.nhood_enrichment(a_del, cluster_key=cluster_key, n_perms=100, seed=0, n_jobs=1)
check("Enrichment results stored", f"{cluster_key}_nhood_enrichment" in a_del.uns)

zscore = a_del.uns[f"{cluster_key}_nhood_enrichment"]["zscore"]
check("Z-score matrix is square over cell types", zscore.shape == (n_types, n_types))
check("Z-score matrix is symmetric", np.allclose(zscore, zscore.T, equal_nan=True))

diag = np.diag(zscore)
print(f"  Mean self-enrichment (diagonal): {np.nanmean(diag):.2f}")
# Cells of the same type cluster spatially in tissue, so the diagonal is
# positive. If it is not, the coordinates are probably scrambled.
check("Self-enrichment is positive on average", np.nanmean(diag) > 0)

# --- The graph determines the answer ---
print("\nGraph sensitivity of enrichment...")
sq.gr.nhood_enrichment(a_knn, cluster_key=cluster_key, n_perms=100, seed=0, n_jobs=1)
z_knn = a_knn.uns[f"{cluster_key}_nhood_enrichment"]["zscore"]

mask = ~(np.isnan(zscore) | np.isnan(z_knn))
corr = float(np.corrcoef(zscore[mask].ravel(), z_knn[mask].ravel())[0, 1])
print(f"  Correlation between Delaunay and kNN z-scores: {corr:.3f}")
check("Graphs broadly agree (r > 0.5)", corr > 0.5)
check("Graphs are not interchangeable (r < 0.999)", corr < 0.999)

# --- Interaction matrix ---
print("\nInteraction matrix...")
im = sq.gr.interaction_matrix(a_del, cluster_key=cluster_key, normalized=False, copy=True)
check("Interaction matrix is square", im.shape == (n_types, n_types))
check("Interaction counts are non-negative", im.min() >= 0)

total_edges = int(np.asarray((a_del.obsp["spatial_connectivities"] > 0).sum()))
print(f"  Total directed edges: {total_edges}, interaction matrix sum: {int(im.sum())}")
check("Interaction matrix accounts for all edges", int(im.sum()) == total_edges)

print(f"\n=== Neighbours: {_pass} passed, {_fail} failed ===")
