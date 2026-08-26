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
"""Validate spatially variable gene detection on Visium mouse brain.

Checks Moran's I bounds, that anatomically restricted genes outrank
housekeeping genes, and that graph choice changes the answer.

Expected runtime: 4-8 minutes
Requires: squidpy>=1.8, scanpy>=1.12
"""

import numpy as np
import scanpy as sc
import squidpy as sq

print("=== Spatially Variable Gene Validation (Visium mouse brain) ===\n")
_pass = _fail = 0


def check(name, condition):
    global _pass, _fail
    if bool(condition):
        print(f"  PASS: {name}")
        _pass += 1
    else:
        print(f"  FAIL: {name}")
        _fail += 1


print("Loading and normalizing...")
adata = sq.datasets.visium_hne_adata_crop()
adata.var_names_make_unique()
sc.pp.filter_genes(adata, min_cells=10)
adata.layers["counts"] = adata.X.copy()
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
print(f"  {adata.n_obs} spots x {adata.n_vars} genes ({int(adata.var['highly_variable'].sum())} HVGs)")

# --- Moran's I ---
print("\nComputing Moran's I...")
sq.gr.spatial_neighbors_grid(adata, n_neighs=6)
sq.gr.spatial_autocorr(adata, mode="moran", n_perms=100, n_jobs=1, seed=0)

check("Moran's I results stored", "moranI" in adata.uns)
mi = adata.uns["moranI"]
print(f"  Genes scored: {len(mi)}")

# Moran's I is bounded well inside [-1, 1] for real data
check("Moran's I within [-1, 1]", mi["I"].min() >= -1 and mi["I"].max() <= 1)
check("Top gene is strongly autocorrelated (I > 0.3)", mi["I"].max() > 0.3)
check("Results are sorted descending by I", mi["I"].is_monotonic_decreasing)

print(f"  Top 8 SVGs: {', '.join(mi.index[:8])}")
print(f"  I range: {mi['I'].min():.3f} to {mi['I'].max():.3f}")

# --- Anatomically restricted genes should outrank housekeeping genes ---
print("\nBiological sanity...")
ranks = {g: i for i, g in enumerate(mi.index)}

# Mbp/Plp1 mark white matter tracts; Ttr marks choroid plexus. All are confined
# to specific structures, so they must be strongly spatially autocorrelated.
structured = [g for g in ["Mbp", "Plp1", "Ttr", "Nrgn", "Camk2n1"] if g in ranks]
housekeeping = [g for g in ["Actb", "Gapdh", "Rpl13a"] if g in ranks]

for g in structured:
    print(f"  {g:10s} rank {ranks[g]:5d}  I = {mi.loc[g, 'I']:.3f}")
for g in housekeeping:
    print(f"  {g:10s} rank {ranks[g]:5d}  I = {mi.loc[g, 'I']:.3f}  (housekeeping)")

if structured:
    best_structured = min(ranks[g] for g in structured)
    check("An anatomically restricted gene ranks in the top 100", best_structured < 100)

if structured and housekeeping:
    worst_structured = max(ranks[g] for g in structured)
    best_housekeeping = min(ranks[g] for g in housekeeping)
    check(
        "Structured genes outrank housekeeping genes",
        worst_structured < best_housekeeping,
    )

# --- Rank, do not threshold ---
print("\nRank-based selection...")
top_svgs = mi.index[:2000]
check("Top-2000 rank cutoff selects 2000 genes", len(top_svgs) == 2000)

if "pval_norm_fdr_bh" in mi.columns:
    n_sig = int((mi["pval_norm_fdr_bh"] < 0.05).sum())
    frac = n_sig / len(mi)
    print(f"  Genes at FDR < 0.05: {n_sig} / {len(mi)} ({100 * frac:.1f}%)")
    # Benchmarks found p-value calibration broken for most SVG methods; a huge
    # significant fraction is exactly why a rank cutoff is preferred.
    check("FDR significance is not a useful filter (>20% pass)", frac > 0.20)

# --- Graph choice changes the answer ---
print("\nGraph sensitivity...")
adata_knn = adata.copy()
sq.gr.spatial_neighbors_knn(adata_knn, n_neighs=18)
sq.gr.spatial_autocorr(adata_knn, mode="moran", n_perms=None, n_jobs=1, seed=0)
mi_knn = adata_knn.uns["moranI"]

shared = mi.index[:200].intersection(mi_knn.index[:200])
overlap = len(shared) / 200
print(f"  Top-200 overlap between 6-neighbour grid and 18-neighbour kNN: {100 * overlap:.0f}%")
check("Graphs agree substantially (>50% overlap)", overlap > 0.50)
check("Graphs are not identical (<100% overlap)", overlap < 1.0)

print(f"\n=== SVG: {_pass} passed, {_fail} failed ===")
