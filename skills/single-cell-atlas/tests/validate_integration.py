#!/usr/bin/env python3
"""Validate batch integration on a real multi-batch PBMC dataset.

Uses Kang et al. 2018 (GSE96583): 8 donors, control vs IFN-beta stimulated,
with ground-truth cell type labels. Checks that integration mixes batches
without collapsing biology, and that the standard metrics move the right way.

Expected runtime: 8-15 minutes (38 MB download, Harmony on ~25k cells)
Requires: scanpy>=1.12, pertpy, harmonypy
Optional: scib-metrics (integration quality metrics)
"""

import numpy as np
import scanpy as sc

print("=== Batch Integration Validation (Kang 2018 PBMC) ===\n")
_pass = _fail = 0


def check(name, condition):
    global _pass, _fail
    if bool(condition):
        print(f"  PASS: {name}")
        _pass += 1
    else:
        print(f"  FAIL: {name}")
        _fail += 1


# --- Load multi-batch data ---
try:
    import pertpy as pt
except ImportError:
    print("SKIP: pertpy not installed (pip install pertpy)")
    raise SystemExit(0)

print("Downloading Kang 2018...")
adata = pt.data.kang_2018()
print(f"  Shape: {adata.shape[0]} cells x {adata.shape[1]} genes")

check("Roughly 24-25k cells", 24000 <= adata.n_obs <= 25000)
check("Condition label present", "label" in adata.obs)
check("Donor replicate present", "replicate" in adata.obs)
check("Ground-truth cell types present", "cell_type" in adata.obs)

n_donors = adata.obs["replicate"].nunique()
n_types = adata.obs["cell_type"].nunique()
print(f"  Donors: {n_donors}, conditions: {adata.obs['label'].nunique()}, cell types: {n_types}")
check("8 donors", n_donors == 8)
check("8 cell types", n_types == 8)

# Use condition as the batch key: IFN-beta produces a strong, real batch effect
# that naive PCA cannot mix.
BATCH, LABEL = "label", "cell_type"

# --- Preprocess ---
print("\nPreprocessing...")
adata.layers["counts"] = adata.X.copy()
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000, batch_key=BATCH)
adata.raw = adata
adata = adata[:, adata.var["highly_variable"]].copy()
sc.pp.scale(adata, max_value=10)
sc.tl.pca(adata, n_comps=50, svd_solver="arpack")
check("PCA embedding computed", "X_pca" in adata.obsm)

# --- Harmony ---
print("\nRunning Harmony...")
try:
    import harmonypy
except ImportError:
    print("SKIP: harmonypy not installed")
    raise SystemExit(0)

ho = harmonypy.run_harmony(adata.obsm["X_pca"], adata.obs, [BATCH])
Z = np.asarray(ho.Z_corr)
# harmonypy 2.0.0 returns cells x PCs; older versions returned PCs x cells.
# scanpy's sce.pp.harmony_integrate still transposes unconditionally and breaks
# against 2.0.0, so call harmonypy directly and orient by shape.
if Z.shape[0] != adata.n_obs:
    Z = Z.T
adata.obsm["X_harmony"] = Z

check("Harmony embedding matches cell count", adata.obsm["X_harmony"].shape[0] == adata.n_obs)
check("Harmony preserved PC count", adata.obsm["X_harmony"].shape[1] == 50)

# --- Batch mixing, measured by neighbourhood composition ---
print("\nBatch mixing...")


def batch_purity(rep):
    """Mean fraction of a cell's neighbours sharing its batch. 1.0 = no mixing."""
    sc.pp.neighbors(adata, use_rep=rep, n_neighbors=30, key_added=f"nn_{rep}")
    conn = adata.obsp[f"nn_{rep}_connectivities"]
    codes = adata.obs[BATCH].cat.codes.values
    same = np.zeros(adata.n_obs)
    for i in range(adata.n_obs):
        nb = conn[i].indices
        if len(nb):
            same[i] = (codes[nb] == codes[i]).mean()
    return float(same.mean())


purity_pca = batch_purity("X_pca")
purity_harmony = batch_purity("X_harmony")
print(f"  Batch purity before: {purity_pca:.3f}")
print(f"  Batch purity after:  {purity_harmony:.3f}")

check("Unintegrated data is batch-separated (>0.75)", purity_pca > 0.75)
check("Harmony reduces batch purity", purity_harmony < purity_pca)
check("Harmony mixes batches substantially (<0.70)", purity_harmony < 0.70)

# --- Biology preserved (the other half of the trade-off) ---
print("\nBiological conservation...")
sc.pp.neighbors(adata, use_rep="X_harmony", n_neighbors=15)
sc.tl.leiden(adata, resolution=1.0, key_added="leiden_int",
             flavor="igraph", n_iterations=2, directed=False, random_state=0)

try:
    from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

    ari = adjusted_rand_score(adata.obs[LABEL], adata.obs["leiden_int"])
    nmi = normalized_mutual_info_score(adata.obs[LABEL], adata.obs["leiden_int"])
    print(f"  ARI vs ground truth: {ari:.3f}")
    print(f"  NMI vs ground truth: {nmi:.3f}")
    check("ARI > 0.40 (cell types recovered)", ari > 0.40)
    check("NMI > 0.60 (cell types recovered)", nmi > 0.60)
except ImportError:
    print("  SKIP: scikit-learn not installed")

n_clust = adata.obs["leiden_int"].nunique()
print(f"  Clusters after integration: {n_clust}")
# Over-correction signature: everything collapses toward a single blob.
check("Not over-corrected (>=6 clusters remain)", n_clust >= 6)

# Each ground-truth cell type should still dominate at least one cluster.
recovered = 0
for ct in adata.obs[LABEL].unique():
    mask = adata.obs[LABEL] == ct
    top = adata.obs.loc[mask, "leiden_int"].value_counts(normalize=True).iloc[0]
    if top > 0.5:
        recovered += 1
print(f"  Cell types mapping cleanly to one cluster: {recovered}/{n_types}")
check("At least 6 of 8 cell types stay coherent", recovered >= 6)

# --- Optional: scib-metrics ---
print("\nIntegration metrics (scib-metrics)...")
try:
    from scib_metrics.nearest_neighbors import pynndescent
    import scib_metrics as sm

    nn_pca = pynndescent(adata.obsm["X_pca"], n_neighbors=90)
    nn_har = pynndescent(adata.obsm["X_harmony"], n_neighbors=90)

    ilisi_pre = sm.ilisi_knn(nn_pca, adata.obs[BATCH])
    ilisi_post = sm.ilisi_knn(nn_har, adata.obs[BATCH])
    print(f"  iLISI before: {ilisi_pre:.4f}")
    print(f"  iLISI after:  {ilisi_post:.4f}")
    check("iLISI increases after integration", ilisi_post > ilisi_pre)

    gc_post = sm.graph_connectivity(nn_har, adata.obs[LABEL])
    print(f"  Graph connectivity: {gc_post:.4f}")
    check("Graph connectivity > 0.80", gc_post > 0.80)

    # pcr_comparison needs integer codes and categorical=True; passing strings
    # raises a JAX dtype error and a one-hot matrix raises a reshape error.
    import pandas as pd

    codes = pd.Categorical(adata.obs[BATCH]).codes
    pcr = sm.pcr_comparison(adata.obsm["X_pca"], adata.obsm["X_harmony"], codes, categorical=True)
    print(f"  PCR comparison: {pcr:.4f}")
    check("PCR comparison > 0 (batch variance removed)", pcr > 0)
except ImportError:
    print("  SKIP: scib-metrics not installed (pip install scib-metrics)")

print(f"\n=== Integration: {_pass} passed, {_fail} failed ===")
