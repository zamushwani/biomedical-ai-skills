# spatial-transcriptomics

Spatially resolved transcriptomics across sequencing-based (Visium, Visium HD, Slide-seq, Stereo-seq) and imaging-based (Xenium, MERSCOPE, CosMx) platforms. Dual-language: Python (squidpy/SpatialData) and R (SpatialExperiment/Seurat v5).

```mermaid
graph TD
    A["spatial-transcriptomics<br>SKILL.md"] --> B["Loading<br>spatialdata-io · VisiumIO"]
    A --> C["QC<br>SpotSweeper · SpaceTrooper"]
    A --> D["Spatially variable genes<br>Moran's I · nnSVG · SPARK-X"]
    A --> E["Deconvolution<br>RCTD · cell2location · CARD"]
    A --> F["Domains & niches<br>BANKSY · CellCharter"]
    A --> G["Communication<br>LIANA+ · CellChat v2"]
    style A fill:#1a1a2e,stroke:#00d9ff,color:#fff,stroke-width:2px
    style B fill:#1a1a2e,stroke:#4ecdc4,color:#fff,stroke-width:2px
    style C fill:#1a1a2e,stroke:#ff6b6b,color:#fff,stroke-width:2px
    style D fill:#1a1a2e,stroke:#87b13f,color:#fff,stroke-width:2px
    style E fill:#1a1a2e,stroke:#276DC3,color:#fff,stroke-width:2px
    style F fill:#1a1a2e,stroke:#e84d3c,color:#fff,stroke-width:2px
    style G fill:#1a1a2e,stroke:#f39c12,color:#fff,stroke-width:2px
```

## Usage

```bash
# Claude Code
cp SKILL.md your-project/.claude/skills/

# Cursor
cp SKILL.md your-project/.cursor/skills/
```

## The distinction that drives everything

| | Sequencing-based | Imaging-based |
|---|---|---|
| Platforms | Visium, Visium HD, Slide-seq, Stereo-seq | Xenium, MERSCOPE, CosMx |
| Resolution | 55 um spots to 2 um bins | single cell / subcellular |
| Transcriptome | whole | targeted panel (500-5,000 genes) |
| Spots hold | 1-10 cells | one cell |
| You need | **deconvolution** | **segmentation + cell typing** |
| Dominant error | reference mismatch | segmentation |

## Validation

Tests in [`tests/`](tests/) run against public 10x Visium mouse brain and an IMC dataset:

- Graph builders (kNN, Delaunay, radius) differ in degree and in the enrichment they produce
- Visium loading, spatial coordinates, spot-level QC, spatial autocorrelation of depth
- Moran's I bounds, anatomically restricted genes outranking housekeeping genes

```bash
python tests/run_all.py             # all tests
python tests/run_all.py neighbors   # cheapest, 1.6 MB download
```

## Languages covered

| Step | Python | R |
|------|--------|---|
| Visium loading | `squidpy.read.visium()` | `VisiumIO::TENxVisium()` |
| Visium HD | `spatialdata_io.visium_hd()` | `VisiumIO::TENxVisiumHD()` |
| Xenium | `spatialdata_io.xenium()` | `XeniumIO::TENxXenium()` |
| Spatial QC | `squidpy.experimental.im.qc_image()` | `SpotSweeper` / `SpaceTrooper` |
| SVGs | `sq.gr.spatial_autocorr()` | `nnSVG()` |
| Deconvolution | `cell2location` | `spacexr` (RCTD), `SPOTlight` |
| Domains | `cc.tl.ClusterAutoK()` | `Banksy::clusterBanksy()` |
| Communication | `li.mt.bivariate()` | `CellChat` spatial mode |
