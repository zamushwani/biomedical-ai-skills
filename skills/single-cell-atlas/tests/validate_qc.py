#!/usr/bin/env python3
"""Validate QC and preprocessing against the 10x PBMC 3k reference dataset.

Checks matrix dimensions, QC metric distributions, the filter cascade,
MAD-based filtering, doublet detection, and feature selection.

Expected runtime: 2-4 minutes (6 MB download, cached after first run)
Requires: scanpy>=1.12, scikit-image (for scrublet)
"""

import numpy as np
import scanpy as sc

print("=== Single-Cell QC Validation (PBMC 3k) ===\n")
_pass = _fail = 0


def check(name, condition):
    global _pass, _fail
    if bool(condition):
        print(f"  PASS: {name}")
        _pass += 1
    else:
        print(f"  FAIL: {name}")
        _fail += 1


# --- Load reference data ---
print("Downloading PBMC 3k...")
adata = sc.datasets.pbmc3k()

check("Raw matrix is 2700 x 32738", adata.shape == (2700, 32738))
print(f"  Shape: {adata.shape[0]} cells x {adata.shape[1]} genes")

check("X holds raw integer counts", np.allclose(adata.X.data, np.round(adata.X.data)))

# --- Gene detection ---
n_3cells = int((np.diff(adata.X.tocsc().indptr) >= 3).sum())
print(f"  Genes detected in >=3 cells: {n_3cells}")
check("13714 genes pass min_cells=3", n_3cells == 13714)

# --- QC metrics ---
adata.var["mt"] = adata.var_names.str.startswith("MT-")
print(f"  MT- genes on the panel: {int(adata.var['mt'].sum())}")
check("13 mitochondrial genes present", int(adata.var["mt"].sum()) == 13)

sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], percent_top=None, log1p=True, inplace=True)

med_genes = float(np.median(adata.obs["n_genes_by_counts"]))
med_umi = float(np.median(adata.obs["total_counts"]))
med_mt = float(np.median(adata.obs["pct_counts_mt"]))
min_genes = int(adata.obs["n_genes_by_counts"].min())

print(f"  Median genes/cell: {med_genes:.0f}")
print(f"  Median UMI/cell:   {med_umi:.0f}")
print(f"  Median mito %:     {med_mt:.2f}")
print(f"  Min genes/cell:    {min_genes}")

check("Median genes/cell is 817", med_genes == 817)
check("Median UMI/cell is 2197", med_umi == 2197)
check("Median mito % is ~2.0", abs(med_mt - 2.0) < 0.05)

# min_genes=200 removes nothing on this dataset. If a pipeline reports cells
# dropped at that step, the filter is being applied to the wrong axis.
check("Lowest-complexity cell still has >200 genes", min_genes == 212)

# --- Filter cascade ---
print("\nFilter cascade...")
n_mito_only = int((adata.obs["pct_counts_mt"] < 5).sum())
n_gene_only = int((adata.obs["n_genes_by_counts"] < 2500).sum())
keep = (
    (adata.obs["n_genes_by_counts"] > 200)
    & (adata.obs["n_genes_by_counts"] < 2500)
    & (adata.obs["pct_counts_mt"] < 5)
)
n_standard = int(keep.sum())

print(f"  mito < 5% only:              {n_mito_only}")
print(f"  genes < 2500 only:           {n_gene_only}")
print(f"  standard combined filter:    {n_standard}")

check("Standard QC keeps exactly 2638 cells", n_standard == 2638)
check("57 cells removed by mito >= 5%", 2700 - n_mito_only == 57)
check("5 cells removed by genes >= 2500", 2700 - n_gene_only == 5)

# --- MAD-based filtering (the approach the skill recommends) ---
print("\nMAD-based filtering...")


def mad_outlier(vals, nmads=3, direction="both"):
    med = np.median(vals)
    mad = np.median(np.abs(vals - med)) * 1.4826
    if direction == "higher":
        return vals > med + nmads * mad
    if direction == "lower":
        return vals < med - nmads * mad
    return (vals < med - nmads * mad) | (vals > med + nmads * mad)


log_counts = np.log1p(adata.obs["total_counts"].values)
log_genes = np.log1p(adata.obs["n_genes_by_counts"].values)

for nmads, lo, hi in [(3, 2450, 2600), (5, 2600, 2680)]:
    discard = (
        mad_outlier(log_counts, nmads)
        | mad_outlier(log_genes, nmads)
        | (adata.obs["pct_counts_mt"].values >= 5)
    )
    kept = int((~discard).sum())
    print(f"  {nmads} MADs + mito<5%: {kept} cells retained")
    check(f"{nmads}-MAD filter retains {lo}-{hi} cells", lo <= kept <= hi)

# MAD filtering does not reproduce the fixed-threshold count, and should not be
# expected to. Assert the range, never the exact 2638.

# --- Doublet detection ---
print("\nDoublet detection (Scrublet)...")
adata_qc = adata[keep].copy()
sc.pp.filter_genes(adata_qc, min_cells=3)

try:
    sc.pp.scrublet(adata_qc, random_state=0, verbose=False)
    n_doublets = int(adata_qc.obs["predicted_doublet"].sum())
    rate = 100 * n_doublets / adata_qc.n_obs
    print(f"  Predicted doublets: {n_doublets} ({rate:.2f}%)")
    check("Doublet rate is 1-3%", 1.0 <= rate <= 3.0)
    # scDblFinder's prior for 2700 cells is 0.008 * 2.7 = 2.16%.
    # Scrublet empirically calls ~1.4% here. Both are defensible.
    check("Doublet rate is not runaway (<5%)", rate < 5.0)
except ImportError:
    print("  SKIP: scrublet requires scikit-image (pip install scanpy[scrublet])")

# --- Normalization ---
print("\nNormalization...")
adata_qc.layers["counts"] = adata_qc.X.copy()
sc.pp.normalize_total(adata_qc, target_sum=1e4)
sc.pp.log1p(adata_qc)

max_val = float(adata_qc.X.max())
print(f"  Max log-normalized value: {max_val:.2f}")
check("Log-normalized values in 0-10 range", 0 < max_val < 10)
check("Raw counts preserved in layers", "counts" in adata_qc.layers)

# --- Feature selection ---
print("\nFeature selection...")
adata_hvg = adata_qc.copy()
adata_hvg.X = adata_hvg.layers["counts"].copy()
sc.pp.highly_variable_genes(adata_hvg, flavor="seurat_v3", n_top_genes=2000)
hvgs = set(adata_hvg.var_names[adata_hvg.var["highly_variable"]])

print(f"  HVGs selected: {len(hvgs)}")
check("2000 HVGs selected", len(hvgs) == 2000)

markers = ["CD79A", "FCER1A", "PPBP", "MS4A7", "GNLY", "CD14"]
found = [m for m in markers if m in hvgs]
print(f"  Canonical markers captured: {len(found)}/{len(markers)} ({', '.join(found)})")
check("At least 5 of 6 canonical markers are HVGs", len(found) >= 5)

housekeeping = [g for g in ["ACTB", "GAPDH"] if g in hvgs]
check("Housekeeping genes not in HVGs", len(housekeeping) == 0)

print(f"\n=== QC: {_pass} passed, {_fail} failed ===")
