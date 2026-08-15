#!/usr/bin/env python3
"""Establish the baseline a single-cell foundation model has to beat.

The skill's central claim is that for cell type clustering, HVG+PCA is
competitive with or better than zero-shot foundation model embeddings. This
measures the baseline on PBMC 3k so the claim is a number rather than an
opinion, and compares a foundation model against it when one is installed.

Clustering uses KMeans rather than Leiden: k is fixed to the number of
reference cell types, which is how scIB-style benchmarks score embeddings, and
it removes resolution tuning as a confounder.

Expected runtime: 1-3 minutes (30 MB download, cached after first run)
Requires: scanpy, scikit-learn
Optional: torch + a foundation model checkpoint (comparison is skipped without)
"""

import warnings

warnings.filterwarnings("ignore")

import numpy as np
import scanpy as sc
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

sc.settings.verbosity = 0

print("=== Foundation Model Baseline Validation (PBMC 3k) ===\n")
_pass = _fail = 0


def check(name, condition):
    global _pass, _fail
    if bool(condition):
        print(f"  PASS: {name}")
        _pass += 1
    else:
        print(f"  FAIL: {name}")
        _fail += 1


# --- Reference labels ---
ref = sc.datasets.pbmc3k_processed()
labels = ref.obs["louvain"].values
n_types = len(set(labels))

raw = sc.datasets.pbmc3k()
raw = raw[ref.obs_names].copy()  # align to the annotated subset

print(f"  cells: {raw.n_obs}, genes: {raw.n_vars}, reference cell types: {n_types}")
check("2638 annotated cells", raw.n_obs == 2638)
check("8 reference cell types", n_types == 8)


def score(embedding, k=n_types, seed=0):
    """ARI and NMI of KMeans on an embedding against the reference labels."""
    km = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(embedding)
    return (adjusted_rand_score(labels, km.labels_),
            normalized_mutual_info_score(labels, km.labels_))


# --- The baseline: HVG + PCA, exactly what the skill prescribes ---
print("\nHVG + PCA baseline...")
a = raw.copy()
sc.pp.filter_genes(a, min_cells=3)
sc.pp.normalize_total(a, target_sum=1e4)
sc.pp.log1p(a)
sc.pp.highly_variable_genes(a, n_top_genes=2000)
a = a[:, a.var.highly_variable].copy()
sc.pp.scale(a, max_value=10)
sc.tl.pca(a, n_comps=50, svd_solver="arpack")

ari30, nmi30 = score(a.obsm["X_pca"][:, :30])
ari50, nmi50 = score(a.obsm["X_pca"][:, :50])

print(f"  n_pcs=30: ARI {ari30:.4f}  NMI {nmi30:.4f}")
print(f"  n_pcs=50: ARI {ari50:.4f}  NMI {nmi50:.4f}")

check("Baseline ARI at 30 PCs exceeds 0.80", ari30 > 0.80)
check("Baseline NMI at 30 PCs exceeds 0.80", nmi30 > 0.80)
check("Baseline ARI at 30 PCs is ~0.879", abs(ari30 - 0.8789) < 0.05)
check("Fewer PCs is not worse here", ari30 >= ari50 - 0.01)

# This is a strong baseline. Any foundation model that does not clear it is
# not earning its compute for this task.

# --- Feature selection matters more than most model choices ---
print("\nControl: same pipeline without HVG selection...")
b = raw.copy()
sc.pp.filter_genes(b, min_cells=3)
sc.pp.normalize_total(b, target_sum=1e4)
sc.pp.log1p(b)
sc.pp.scale(b, max_value=10)
sc.tl.pca(b, n_comps=50, svd_solver="arpack")
ari_all, nmi_all = score(b.obsm["X_pca"][:, :50])

print(f"  all genes: ARI {ari_all:.4f}  NMI {nmi_all:.4f}")
check("Dropping HVG selection degrades ARI substantially", ari30 - ari_all > 0.20)
print(f"    -> HVG selection is worth {ari30 - ari_all:.3f} ARI on this dataset")

# --- Foundation model comparison, when one is available ---
print("\nFoundation model comparison...")
emb = None
try:
    import torch  # noqa: F401

    # An embedding is expected in .obsm under one of these keys. Producing it
    # requires model weights, which are multi-gigabyte and not downloaded here.
    for key in ("X_scGPT", "X_geneformer", "X_uce", "X_scvi"):
        if key in raw.obsm:
            emb = raw.obsm[key]
            print(f"  found precomputed embedding: {key}")
            break
    if emb is None:
        print("  SKIP: torch present but no precomputed embedding in .obsm")
        print("        Generate one and rerun to score it against the baseline.")
except ImportError:
    print("  SKIP: torch not installed")

if emb is not None:
    ari_fm, nmi_fm = score(np.asarray(emb))
    print(f"  foundation model: ARI {ari_fm:.4f}  NMI {nmi_fm:.4f}")
    print(f"  baseline        : ARI {ari30:.4f}  NMI {nmi30:.4f}")
    check("Foundation model beats the HVG+PCA baseline on ARI", ari_fm > ari30)
    if ari_fm <= ari30:
        print("    -> matches the published finding that zero-shot embeddings")
        print("       do not reliably beat HVG+PCA for cell type clustering")

print(f"\n=== Baseline: {_pass} passed, {_fail} failed ===")
raise SystemExit(1 if _fail else 0)
