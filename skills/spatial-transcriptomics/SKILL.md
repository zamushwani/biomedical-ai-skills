# Spatial Transcriptomics

Processing and analysis of spatially resolved transcriptomics across sequencing-based (Visium, Visium HD, Slide-seq, Stereo-seq) and imaging-based (Xenium, MERSCOPE, CosMx) platforms. Covers loading, QC, normalization, and spatially variable gene detection. Dual-language: Python (squidpy/SpatialData) and R (SpatialExperiment/Seurat v5).

## When to Use This Skill

Activate when the user requests:
- Visium or Visium HD data loading and quality control
- Xenium, MERSCOPE, CosMx, or Stereo-seq processing
- Spatial quality control and artifact detection
- Spatially variable gene (SVG) detection
- Spatial autocorrelation (Moran's I, Geary's C)
- Conversion between spatial data containers
- Any analysis where transcript measurements carry coordinates

## Platform Types

The single most important distinction. It determines every downstream choice.

```
Sequencing-based (spot/bin resolution, whole transcriptome):
  Visium        55 um spots, ~1-10 cells per spot, ~18k genes
  Visium HD     2 um bins (binned to 8/16 um), subcellular grid, whole transcriptome
  Slide-seq V2  10 um beads
  Stereo-seq    220 nm DNB, binned
  -> Spots mix cell types. You need DECONVOLUTION.

Imaging-based (single-cell/subcellular, targeted panel):
  Xenium        ~5k genes max (Prime 5K), segmented cells
  MERSCOPE      ~500-1000 genes
  CosMx         ~1000-6000 genes
  -> Cells are already segmented. You need CELL TYPING, not deconvolution.
     Segmentation quality is the dominant error source.
```

## Inputs

| Platform | Format | Reader |
|----------|--------|--------|
| Visium | Space Ranger `outs/` (h5 + `tissue_positions.csv` + images) | `squidpy.read.visium`, `VisiumIO::TENxVisium` |
| Visium HD | Space Ranger `outs/` with `binned_outputs/`, `tissue_positions.parquet` | `spatialdata_io.visium_hd`, `VisiumIO::TENxVisiumHD` |
| Xenium | Xenium Onboard Analysis output bundle | `spatialdata_io.xenium`, `XeniumIO::TENxXenium` |
| MERSCOPE | Vizgen output (`cell_by_gene.csv`, `cell_metadata.csv`) | `spatialdata_io.merscope` |
| CosMx | NanoString flat files | `spatialdata_io.cosmx`, `readCosmxSXE` |
| Stereo-seq | STOmics GEF/GEM (v7.x only) | `spatialdata_io.stereoseq` |

---

## Environment

Version pins that matter. The spatial stack moved fast and broke things.

```
Python (all require Python >= 3.12 as of squidpy 1.8.3 / spatialdata 0.8.0)
  squidpy         1.8.3
  spatialdata     0.8.0
  spatialdata-io  0.7.1
  scanpy          1.12.3
  anndata         0.13.2

R (Bioconductor 3.23, R 4.6)
  SpatialExperiment       1.22.0
  SpatialFeatureExperiment 1.14.0
  Voyager                 1.14.0
  VisiumIO / XeniumIO     1.8.0 / 1.4.0
  SpotSweeper             1.8.0
  nnSVG                   1.16.1
  Seurat                  5.5.1
```

Python 3.11 was dropped in squidpy 1.8.3 and spatialdata 0.8.0. `zarr>=3` is required.

---

## Loading Data

### Deprecations to know first

| Deprecated | Since | Use instead |
|------------|-------|-------------|
| `scanpy.read_visium` | scanpy 1.11.0 | `squidpy.read.visium` |
| `scanpy.pl.spatial` | scanpy 1.11.0 | `squidpy.pl.spatial_scatter` |
| `scanpy.datasets.visium_sge` | scanpy 1.11.0 | `squidpy.datasets.visium` |
| `SpatialExperiment::read10xVisium` | SpatialExperiment 1.15.2 | `VisiumIO::TENxVisium` |

Scanpy adopted the SPEC-0 deprecation schedule in 1.12.0, so these are on a removal clock. Treat them as dead code in new pipelines.

### Visium (Python)

```python
import squidpy as sq

adata = sq.read.visium(
    "path/to/outs",
    counts_file="filtered_feature_bc_matrix.h5",  # note: counts_file, not count_file
    load_images=True,
)
adata.var_names_make_unique()
```

`squidpy.read.visium` parses `tissue_positions.csv` only. It does not read `tissue_positions.parquet`, so it cannot load Visium HD. Space Ranger v1/v2/v3 position-file variants are handled automatically (header presence is sniffed at runtime).

### Visium HD (Python)

```python
import spatialdata_io as sdio

sdata = sdio.visium_hd(
    "path/to/outs",
    bin_size=8,                      # pass 2, 8, or 16 explicitly; None loads ALL bins
    bins_as_squares=True,            # False draws circles, which is geometrically wrong
    load_segmentations_only=False,   # set explicitly: default flips to True in a future release
)

# Table for a given bin lives in sdata.tables
adata = sdata.tables["square_008um"]
```

```
Bin size selection:
  2 um   subcellular grid, mostly empty, only for segmentation input
  8 um   default working resolution, roughly one cell
  16 um  use when 8 um is too sparse for your panel or tissue
```

Space Ranger 4.0.1+ runs nucleus and cell segmentation by default on H&E, using a custom StarDist implementation. `bin2cell` is now only needed for IF rather than H&E images, reprocessing pre-4.0 outputs, or custom bin-joining logic.

### Xenium, MERSCOPE, CosMx, Stereo-seq (Python)

```python
import spatialdata_io as sdio

sdata = sdio.xenium("path/to/xenium_out", gex_only=False)   # gex_only=False keeps control probes
sdata = sdio.merscope("path/to/merscope_out")
sdata = sdio.cosmx("path/to/cosmx_out")
sdata = sdio.stereoseq("path/to/stereoseq_out")             # v7.x only, v8.x unsupported
```

Three Xenium reader behaviours that cause silent problems:

```
gex_only=True is the DEFAULT.
  It drops negative control probes, unassigned codewords, and antisense features.
  You need those to compute the false-discovery rate. Pass gex_only=False.

cells_as_circles default changed to False in spatialdata-io 0.7.0.
  The table region key follows it:
    cells_as_circles=True  -> region "cell_circles"
    cells_as_circles=False -> region "cell_labels"
  Code matching on obs["region"] == "cell_circles" breaks across that version boundary.

n_jobs= is a deprecated no-op since 0.7.0.
```

### SpatialData as the container

`SpatialData` is the current standard for Python spatial work: OME-NGFF/Zarr for images and labels, Parquet for shapes and points, AnnData for tables.

```python
sdata.write("sample.zarr")

import spatialdata as sd
sdata = sd.read_zarr("sample.zarr")

# Provenance: reader name and spatialdata-io version are stamped in since 0.7.0
print(sdata.attrs)
```

Use `squidpy.read.*` when you want a flat `AnnData` for plain Visium. Use `spatialdata_io` for everything else, and whenever images need to be first-class elements.

### R

```r
library(VisiumIO)

# Visium
spe <- TENxVisium(
  spacerangerOut = "path/to/outs",
  processing = "filtered",
  images = "lowres"
) |> import()

# Visium HD — bin_size is a ZERO-PADDED character vector
spe <- TENxVisiumHD(
  spacerangerOut = "path/to/outs",
  bin_size = "008"
) |> import()

# Xenium
library(XeniumIO)
spe <- TENxXenium(xeniumOut = "path/to/xenium_out") |> import()
```

When you need negative control probes kept as `altExps` (the cleanest route to control-probe QC in R):

```r
library(SpatialExperimentIO)
spe <- readXeniumSXE(
  dirName = "path/to/xenium_out",
  altExps = c("NegControlProbe", "UnassignedCodeword", "NegControlCodeword", "antisense", "BLANK")
)
```

### Seurat v5

```r
library(Seurat)  # 5.5.1

obj <- Load10X_Spatial("path/to/outs")                    # Visium
obj <- Load10X_Spatial("path/to/outs", bin.size = c(8, 16))  # Visium HD
obj <- LoadXenium("path/to/xenium_out", mols.qv.threshold = 20)
obj <- LoadVizgen("path/to/merscope_out", fov = "fov")
```

```
Seurat 5.4.0 changed the binned Visium coordinate convention:
  x now maps to imagecol, y to imagerow, origin top-left, matching 10x.
  Plots and hand-written coordinate math from Seurat <= 5.3.x are transposed.
  Re-derive coordinates if you are porting old code.

LoadVizgen hard-codes filter = "^Blank-", removing blank codewords before you
see them. Read them separately if you need a blank-codeword FDR.
```

---

## Quality Control

### Sequencing-based platforms

The standard four metrics are library size, detected genes, mitochondrial proportion, and (where segmentation exists) cells per spot.

The practice that changed: **global thresholds are no longer recommended.** A tissue section has regionally varying cell density and RNA content. A global cutoff removes whole anatomical regions (low-cellularity white matter, necrotic cores) rather than low-quality spots. Spatially local outlier detection compares each spot against its own neighbourhood.

```r
library(SpotSweeper)
library(scrapper)

is_mito <- grepl("^MT-", rowData(spe)$symbol)
spe <- quickRnaQc.se(spe, subsets = list(mito = is_mito))
# adds colData: sum, detected, subset.proportion.mito

spe <- localOutliers(spe, metric = "sum",      direction = "lower",  log = TRUE)
spe <- localOutliers(spe, metric = "detected", direction = "lower",  log = TRUE)
spe <- localOutliers(spe, metric = "subset.proportion.mito", direction = "higher", log = FALSE)

# Detect technical artifacts (edge/hangnail effects) rather than biological variation
spe <- findArtifacts(spe, mito_percent = "expr_chrM_ratio", n_order = 7, shape = "hexagonal")
```

`localOutliers` defaults to `n_neighbors = 36` and `cutoff = 3` MADs computed within the local neighbourhood. `findArtifacts` defaults to `n_order = 5`; OSTA uses 7.

Illustrative global thresholds, for reference only (DLPFC Visium): <600 UMI, <400 genes, mito >0.28.

### Imaging-based platforms

Different failure modes, so different metrics. Segmentation errors dominate.

```
What actually goes wrong:
  Over-segmentation   one cell split into fragments -> low counts, small area
  Under-segmentation  two cells merged -> mixed profiles, large area, high counts
  Transcript bleed    signal assigned to a neighbouring cell
  FOV border effects  partial cells at field-of-view edges

Metrics that catch these:
  cell area, signal density (transcripts/um2), aspect ratio,
  negative-control fraction, distance to FOV border
```

```r
library(SpaceTrooper)

spe <- spatialPerCellQC(spe, micronConvFact = 0.12)
# adds: Area_um, log2SignalDensity, log2AspectRatio, log2Ctrl_total_ratio, dist_border

spe <- computeQCScore(spe)
spe <- computeQCScoreFlags(spe, qsThreshold = 0.5)
spe <- computeSpatialOutlier(spe)   # FOV-border rule
```

A stricter rule for Xenium, using transcript density normalized by cell area:

```r
nc <- spe$total_counts / spe$cell_area
ol <- scuttle::isOutlier(nc, log = TRUE, type = "lower", nmads = 3)
discard <- ol | spe$control_probe_counts > 0 | spe$control_codeword_counts > 0
```

This flags roughly 16% of cells on a typical Xenium run. That is expected, not a sign of a bad experiment.

### Negative-control FDR (Xenium)

Xenium panels carry dedicated negative controls: 20 negative control targets on v1 pre-designed panels (27 on the Mouse Brain base panel), 40 on Prime panels, plus negative control codewords and genomic control probes.

```
Estimated false positives per cell =
  (negative control probe counts / n_negative_control_probes / n_cells) x n_target_genes

Only Q-Score >= 20 transcripts enter analysis.
```

10x publishes no numeric pass/fail threshold. Report the run's control-derived FDR, compare across runs on the same panel, and treat any cell with nonzero control counts as suspect rather than chasing an absolute cutoff.

### Image QC

```python
import squidpy as sq

sq.experimental.im.qc_image(
    sdata, image_key="morphology_focus",
    is_hne=False, detect_tissue=True, detect_outliers=True,
)
```

Computes sharpness (Tenengrad, variance of Laplacian, FFT high-frequency energy), intensity, H&E stain separation, tissue fold fraction, and tissue coverage. This API is under `experimental` and may change.

---

## Normalization

```
Which normalization?

  Visium / Visium HD (spots contain multiple cells)
    -> Library-size normalization + log1p. Same as scRNA-seq.
    -> sc.pp.normalize_total(adata, target_sum=1e4); sc.pp.log1p(adata)
    -> SCTransform also works and is common in Seurat spatial workflows.

  Imaging-based (segmented cells, targeted panel)
    -> Normalize by total counts, but DO NOT assume a fixed target sum matched
       to whole-transcriptome data. The panel is targeted, so total counts
       reflect panel composition, not library complexity.
    -> Consider normalizing by cell volume/area instead of counts when
       segmentation quality is high.

  Never
    -> TPM/FPKM. Spatial UMI counts are not length-biased.
```

```python
adata.layers["counts"] = adata.X.copy()
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
```

Keep raw counts. Deconvolution methods (cell2location, RCTD) and pseudobulk DE all require them.

---

## Spatially Variable Genes

A spatially variable gene has expression structured by location beyond what cell type composition alone explains. This is the spatial analogue of highly variable gene selection.

### Method selection

```
Which SVG method?

  Default, Python, any dataset size
    -> Moran's I via sq.gr.spatial_autocorr(mode="moran")
    -> Competitive with dedicated methods in benchmarks, fast, maintained.

  Need calibrated p-values
    -> SPARK-X (R). The only method besides SPARK with well-calibrated p-values.
    -> Caveat: GitHub-only, unmaintained since 2022.

  Need to regress out covariates
    -> nnSVG (Bioconductor, X= argument). The only actively maintained,
       properly distributed method in the top-performing group.
    -> Slower; keep the dataset modest.

  Very large dataset, memory constrained
    -> SOMDE (best memory + runtime) or SPARK-X.

  Do NOT use
    -> SpatialDE (PyPI 1.1.3, abandoned since 2019; ~150 GB at 40k spots)
    -> SPARK proper (~250 GB at 20k spots)
```

### The p-value problem

Benchmarking of 14 SVG methods (Li et al., Genome Biology 2025;26:285) found p-value calibration broken for most methods: only SPARK and SPARK-X produced well-calibrated p-values, six were over-conservative, and four failed to control type I error.

```
Consequence for practice:
  Select SVGs by a fixed RANK cutoff (e.g. top 2000 by score),
  not by FDR-adjusted significance.

Overall ranking: SPARK-X (4.3) > SpaGFT (5.4) > Moran's I (third).
For downstream spatial domain detection specifically, Moran's I ranked
best (6.5), then SpatialDE2 (6.6), then nnSVG (6.8).

Known shared failure: most methods (SPARK-X, nnSVG, Moran's I, Spanve)
do poorly on genes expressed highly in a small area and absent elsewhere.
```

### Moran's I (Python)

```python
# sq.gr.spatial_neighbors is deprecated since squidpy 1.7.0 and is removed in
# 1.9.0. Use the mode-specific builders.
sq.gr.spatial_neighbors_grid(adata, n_neighs=6)        # Visium hex grid
sq.gr.spatial_autocorr(adata, mode="moran", n_perms=100, n_jobs=4)

svgs = adata.uns["moranI"].head(2000).index    # rank, do not threshold on p
```

```
Graph builder by platform:
  Visium (hex grid)     spatial_neighbors_grid(n_neighs=6)
  Visium HD (square)    spatial_neighbors_grid(n_neighs=4)   8 with diagonals
  Imaging-based         spatial_neighbors_delaunay()  or  spatial_neighbors_knn(n_neighs=6)
  Fixed physical range   spatial_neighbors_radius(radius=30)   radius in coordinate units

Replacements for the deprecated call:
  spatial_neighbors_knn, spatial_neighbors_radius, spatial_neighbors_delaunay,
  spatial_neighbors_grid, spatial_neighbors_from_builder, plus mask_graph.

When passing a SpatialData object, table_key is REQUIRED and keyword-only.
```

squidpy 1.8.2 changed the Geary's C variance calculation to use normality assumptions. Geary's C p-values from 1.8.1 and earlier are not comparable to 1.8.2+.

### nnSVG (R)

```r
library(nnSVG)

spe <- spe[, colSums(counts(spe)) > 0]
spe <- logNormCounts(spe)

# X = model matrix of covariates to regress out (e.g. known domain labels)
spe <- nnSVG(spe, X = NULL, n_neighbors = 10, n_threads = 4)

svgs <- rownames(spe)[order(rowData(spe)$rank)][1:2000]
```

### Seurat

```r
obj <- FindSpatiallyVariableFeatures(
  obj, assay = "Spatial", layer = "scale.data",
  selection.method = "moransi", nfeatures = 2000
)
```

Seurat offers only `markvariogram` and `moransi`, neither in the benchmark's top tier. `slot=` was soft-deprecated in favour of `layer=` in 5.3.0. Bugs in this function were fixed in 5.3.0 and 5.5.0, so results from 5.2.x and earlier are suspect.

---

## Common Pitfalls

### Loading
1. **Using `scanpy.read_visium`**: deprecated since scanpy 1.11.0 and on a removal clock. Use `squidpy.read.visium`, and note the argument is `counts_file`, not `count_file`.
2. **Trying to load Visium HD with `squidpy.read.visium`**: it parses CSV position files only, and HD ships `tissue_positions.parquet`. Use `spatialdata_io.visium_hd` or `VisiumIO::TENxVisiumHD`.
3. **Leaving `bin_size=None` on Visium HD**: this loads every bin size at once and blows up memory. Always pass the bin size you want.
4. **Keeping `gex_only=True` on Xenium then trying to compute control-probe FDR**: the default drops exactly the features you need. Pass `gex_only=False`.
5. **Matching on `obs["region"] == "cell_circles"`**: the `cells_as_circles` default flipped to `False` in spatialdata-io 0.7.0, changing the region key to `cell_labels`. Pin the version or set the argument explicitly.
6. **Porting Seurat binned-Visium coordinate code across 5.4.0**: x/y mapping was corrected to match 10x. Older hand-rolled coordinate math is transposed.

### QC
7. **Global QC thresholds on tissue sections**: a fixed UMI cutoff removes low-cellularity anatomy (white matter, adipose, necrosis) rather than bad spots. Use spatially local outlier detection (`SpotSweeper::localOutliers`).
8. **Treating imaging-based data like sequencing-based data**: for Xenium/MERSCOPE/CosMx the dominant error is segmentation, not sequencing depth. Check cell area, aspect ratio, and signal density, not just counts.
9. **Ignoring FOV borders**: cells clipped by field-of-view edges have systematically truncated counts. Flag cells within one mean cell radius of a border.
10. **Chasing an absolute negative-control threshold**: 10x publishes none. Compare control-derived FDR across runs on the same panel.

### SVG detection
11. **Thresholding SVGs on adjusted p-values**: p-value calibration is broken for most methods. Use a fixed rank cutoff.
12. **Using SpatialDE at modern scale**: unmaintained since 2019 and needs ~150 GB at 40k spots. SpatialDE2 was never released to PyPI.
13. **Wrong neighbourhood graph for the platform**: Visium is a hex grid (`n_neighs=6`). Using a generic k-NN graph on grid data, or a grid assumption on imaging data, distorts every spatial statistic downstream.
14. **Comparing Geary's C across squidpy 1.8.2**: the variance calculation changed. Re-run rather than compare.

## Related Skills

- `single-cell-atlas`: reference atlas construction, the input to spatial deconvolution
- `cancer-multiomics`: bulk expression analysis and TCGA retrieval

## Public Datasets for Testing

| Dataset | Platform | Access |
|---------|----------|--------|
| Mouse brain sagittal | Visium | `squidpy.datasets.visium("V1_Adult_Mouse_Brain")` |
| Mouse brain H&E | Visium | `squidpy.datasets.visium_hne_adata()` |
| Human breast cancer | Visium | 10x Genomics public datasets |
| Human lymph node | Visium | 10x Genomics; standard cell2location benchmark |
| Mouse brain | Xenium | 10x Genomics public datasets |
