#!/usr/bin/env python3
"""Validate clustering, resolution behaviour, and annotation against PBMC 3k.

Checks that cluster count depends on n_pcs as much as on resolution, that the
canonical PBMC cell types are recovered at the right proportions, and that
marker genes behave as documented.

Expected runtime: 3-6 minutes
Requires: scanpy>=1.12, leidenalg or igraph
"""

import numpy as np
import scanpy as sc

print("=== Clustering and Annotation Validation (PBMC 3k) ===\n")
_pass = _fail = 0


def check(name, condition):
    global _pass, _fail
    if bool(condition):
        print(f"  PASS: {name}")
        _pass += 1
    else:
        print(f"  FAIL: {name}")
        _fail += 1


# --- Reference annotations ---
print("Loading pre-processed reference...")
ref = sc.datasets.pbmc3k_processed()

check("Reference is 2638 x 1838", ref.shape == (2638, 1838))
check("Reference carries louvain labels", "louvain" in ref.obs)

n_types = ref.obs["louvain"].nunique()
print(f"  Cell types in reference: {n_types}")
# scanpy's reference uses 8 labels (CD4 T is one cluster).
# The Seurat tutorial uses 9 by splitting naive vs memory CD4 T.
check("8 cell types (scanpy convention)", n_types == 8)

# --- Cell type proportions ---
print("\nCell type composition...")
props = ref.obs["louvain"].value_counts(normalize=True) * 100

expected = {
    "CD4 T cells": (40, 48),
    "CD14+ Monocytes": (15, 25),
    "B cells": (8, 15),
    "CD8 T cells": (6, 14),
    "NK cells": (4, 9),
    "FCGR3A+ Monocytes": (3, 8),
    "Dendritic cells": (0.8, 3),
    "Megakaryocytes": (0.2, 1.5),
}

for ctype, (lo, hi) in expected.items():
    if ctype in props.index:
        pct = props[ctype]
        print(f"  {ctype:22s} {pct:5.1f}%")
        check(f"{ctype} is {lo}-{hi}%", lo <= pct <= hi)
    else:
        print(f"  {ctype:22s} not found (label naming differs)")

check("Proportions sum to 100%", abs(props.sum() - 100) < 0.01)

# --- Clustering: n_pcs drives cluster count as much as resolution ---
print("\nClustering (n_pcs sensitivity)...")
adata = sc.datasets.pbmc3k()
adata.var["mt"] = adata.var_names.str.startswith("MT-")
sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], percent_top=None, log1p=True, inplace=True)
adata = adata[
    (adata.obs["n_genes_by_counts"] > 200)
    & (adata.obs["n_genes_by_counts"] < 2500)
    & (adata.obs["pct_counts_mt"] < 5)
].copy()
sc.pp.filter_genes(adata, min_cells=3)

adata.layers["counts"] = adata.X.copy()
sc.pp.highly_variable_genes(adata, flavor="seurat_v3", n_top_genes=2000, layer="counts")
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
adata.raw = adata
adata = adata[:, adata.var["highly_variable"]].copy()
sc.pp.scale(adata, max_value=10)
sc.tl.pca(adata, n_comps=50, svd_solver="arpack")

print(f"  QC'd matrix: {adata.raw.shape[0]} cells")
check("2638 cells after standard QC", adata.raw.shape[0] == 2638)

results = {}
for n_pcs, res in [(10, 0.5), (40, 0.5), (40, 1.0)]:
    key = f"leiden_pc{n_pcs}_r{res}"
    sc.pp.neighbors(adata, n_neighbors=10, n_pcs=n_pcs)
    # flavor defaults to leidenalg with a FutureWarning; pin it explicitly
    sc.tl.leiden(adata, resolution=res, key_added=key,
                 flavor="igraph", n_iterations=2, directed=False, random_state=0)
    n = adata.obs[key].nunique()
    results[(n_pcs, res)] = n
    print(f"  n_pcs={n_pcs:2d}, resolution={res}: {n} clusters")

# Same resolution, different depth, different answer. This is the point.
check("n_pcs=10, res=0.5 gives 9 clusters", results[(10, 0.5)] == 9)
check("n_pcs=40, res=0.5 gives 6-7 clusters", 6 <= results[(40, 0.5)] <= 7)
check("n_pcs=40, res=1.0 gives 9 clusters", results[(40, 1.0)] == 9)
check(
    "Same resolution yields different counts at different n_pcs",
    results[(10, 0.5)] != results[(40, 0.5)],
)

# At n_pcs=40 / res=0.5 the CD8 T and NK compartments have not separated yet.
# Resolution alone is not a proxy for biological granularity.

# --- Marker gene specificity ---
print("\nMarker gene specificity...")
ref_raw = ref.raw.to_adata() if ref.raw is not None else ref


def pct_expressing(gene, label):
    if gene not in ref_raw.var_names:
        return None
    mask = (ref.obs["louvain"] == label).values
    if mask.sum() == 0:
        return None
    vals = ref_raw[mask, gene].X
    vals = vals.toarray().ravel() if hasattr(vals, "toarray") else np.asarray(vals).ravel()
    return 100 * float((vals > 0).mean())


# Genes that are genuinely specific
for gene, label, floor in [
    ("CD79A", "B cells", 85),
    ("FCER1A", "Dendritic cells", 75),
    ("PPBP", "Megakaryocytes", 90),
    ("MS4A7", "FCGR3A+ Monocytes", 70),
]:
    p = pct_expressing(gene, label)
    if p is None:
        print(f"  {gene}: not in reference, skipped")
        continue
    print(f"  {gene:8s} in {label:22s} {p:5.1f}%")
    check(f"{gene} marks {label} (>{floor}%)", p >= floor)

# Genes commonly used as markers that are NOT specific.
# These assertions document the failure mode, not good practice.
print("\n  Markers that misfire:")
lyz_cd4 = pct_expressing("LYZ", "CD4 T cells")
if lyz_cd4 is not None:
    print(f"  LYZ      in CD4 T cells         {lyz_cd4:5.1f}%  (pan-myeloid, not CD14-specific)")
    check("LYZ fires broadly outside monocytes (>30%)", lyz_cd4 > 30)

nkg7_cd8 = pct_expressing("NKG7", "CD8 T cells")
if nkg7_cd8 is not None:
    print(f"  NKG7     in CD8 T cells         {nkg7_cd8:5.1f}%  (not NK-specific)")
    check("NKG7 fires on CD8 T cells (>80%)", nkg7_cd8 > 80)

cd14_mono = pct_expressing("CD14", "CD14+ Monocytes")
if cd14_mono is not None:
    print(f"  CD14     in CD14+ Monocytes     {cd14_mono:5.1f}%  (only ~66% sensitive)")
    check("CD14 is under 80% sensitive in its own cell type", cd14_mono < 80)

print(f"\n=== Clustering: {_pass} passed, {_fail} failed ===")
