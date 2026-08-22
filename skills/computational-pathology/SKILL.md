# Computational Pathology

Whole-slide image processing for cancer histopathology. Covers reading vendor formats with OpenSlide, the coordinate and resolution semantics that cause most WSI bugs, tissue detection, tile extraction, stain normalization, and H&E colour deconvolution.

## When to Use This Skill

Activate when the user requests:
- Reading `.svs`, `.ndpi`, `.mrxs`, `.scn`, or other whole-slide formats
- OpenSlide, TiaToolbox, histolab, or slideio pipelines
- Tissue detection or background removal on a slide
- Tile or patch extraction for downstream modelling
- Stain normalization across slides or scanners
- H&E colour deconvolution, or separating hematoxylin from eosin
- Working at a target magnification or microns-per-pixel

## Inputs

| Data Type | Format | Source |
|-----------|--------|--------|
| Whole-slide image | `.svs`, `.ndpi`, `.mrxs`, `.tiff`, `.scn` | GDC (TCGA), CAMELYON, PANDA |
| Slide metadata | OpenSlide properties | embedded in the file |
| Annotations | GeoJSON, XML, `.qpdata` | QuPath, ASAP, pathologist review |
| Reference tile | RGB image | a slide chosen as the stain target |

---

## Environment

Versions verified 2026-08.

```bash
pip install openslide-python openslide-bin   # 1.4.6 and 4.0.1.2
```

```
openslide-python is a BINDING, not the library. Its only dependency is
Pillow, so `pip install openslide-python` alone gives you an import that
fails at load time with a missing-library error.

openslide-bin ships the compiled OpenSlide C library (4.0.1) as a wheel,
which is why the upstream README tells you to install both. Before it
existed you needed a system package (apt/brew/conda). If you inherit a
pipeline that documents `brew install openslide`, that still works; do not
mix the two in one environment.
```

| Package | Version | Use |
|---|---|---|
| `openslide-python` | 1.4.6 | reading vendor formats, the baseline |
| `openslide-bin` | 4.0.1.2 | the C library as a wheel |
| `tiatoolbox` | 2.1.3 | full pipeline: readers, tiling, models. Python 3.11-3.14 |
| `histolab` | 0.7.0 | tiling and tissue masks. **Capped at Python < 3.12**, last release 2024-02 |
| `slideio` | 2.8.1 | alternative reader, broader format support |
| `large-image` | 1.35.2 | tile server and multi-backend reader |
| `HistomicsTK` | 1.4.0 | stain deconvolution, maintained (pushed 2026-08) |
| `torchstain` | 1.4.1 | Macenko and Reinhard normalization on tensors |
| `staintools` | 2.1.2 | **abandoned.** Last release 2019-04-11, GitHub archived 2021-05-08 |

Use `torchstain` or `HistomicsTK` instead of `staintools`. Tutorials still recommend it; it has been archived for five years.

---

## Reading a Slide

A WSI is a pyramid. Level 0 is full resolution and can be 100k x 100k pixels; each higher level is a downsampled copy.

```python
import openslide

slide = openslide.OpenSlide(path)
print(slide.level_count)         # number of pyramid levels
print(slide.level_dimensions)    # (width, height) per level
print(slide.level_downsamples)   # downsample factor per level
```

### The coordinate frame trap

```python
region = slide.read_region(location, level, size)
```

```
location is ALWAYS in the level 0 reference frame.
size     is in the frame of the level you are reading.

These are different frames in the same call. It is the single most common
WSI bug, and it fails silently: you get an image of the right shape showing
the wrong part of the slide.

To read a WxH tile at level L starting from tile index (i, j):
    d = slide.level_downsamples[L]
    location = (int(i * W * d), int(j * H * d))   # scaled to level 0
    tile = slide.read_region(location, L, (W, H)) # size NOT scaled

Reading at level 0 hides the bug, because the two frames coincide there.
Code that works on a level-0 prototype and breaks at level 2 is almost
always this.
```

### Downsamples are floats

```
level_downsamples is tuple[float, ...], not integers.

A level nominally "4x downsampled" is often 4.0000123, because the level
dimensions are rounded independently per axis. Do not assume powers of two,
and do not use == to pick a level.

    d = slide.level_downsamples[level]        # 4.0000123, not 4
    level = slide.get_best_level_for_downsample(target)   # use this

get_best_level_for_downsample returns the highest level whose downsample is
<= target, so it errs toward MORE resolution than asked. Read at that level
and resize down; never read at a coarser level and upscale.
```

### Magnification is not resolution

```python
props = slide.properties
mpp_x = float(props[openslide.PROPERTY_NAME_MPP_X])   # 'openslide.mpp-x'
power = props.get(openslide.PROPERTY_NAME_OBJECTIVE_POWER)  # '40'
```

```
"40x" is not a resolution. It is a nominal objective power, and the actual
microns per pixel varies by scanner: 40x is commonly ~0.25 um/px but ranges
roughly 0.23-0.28 across vendors. Training tiles at "40x" from two scanners
gives you two different physical scales, and the model learns the scanner.

Work in MICRONS PER PIXEL, not magnification. Pick a target mpp, compute the
downsample you need, and resize:

    target_mpp = 0.5
    scale = target_mpp / mpp_x
    level = slide.get_best_level_for_downsample(scale)

mpp-x and mpp-y can differ. Check both; non-square pixels exist.

Both properties are OPTIONAL. Some slides carry neither, and a KeyError on
'openslide.mpp-x' mid-run is a bad way to discover it. Validate up front and
skip or flag slides without mpp rather than guessing 0.25.
```

### Bounds

```
Some formats (notably MIRAX/.mrxs) store a small scanned region inside a
much larger canvas of empty space. openslide.bounds-x, bounds-y,
bounds-width and bounds-height give the non-empty rectangle.

Tiling over level_dimensions without checking bounds wastes most of the
run on blank canvas, and the blank area is not always white.
```

## Tissue Detection

Tile everything and most tiles are background. Detect tissue on a low
resolution level first, then map back.

```python
import numpy as np
from skimage.color import rgb2hsv
from skimage.filters import threshold_otsu

level = slide.level_count - 1                       # smallest level
thumb = np.array(slide.read_region((0, 0), level,
                                   slide.level_dimensions[level]).convert("RGB"))
sat = rgb2hsv(thumb)[..., 1]                        # saturation
mask = sat > threshold_otsu(sat)
```

```
Why saturation rather than intensity: background glass is bright AND
unsaturated, while tissue is coloured. A pure intensity threshold also
removes pale tissue such as adipose and mucin, which is real signal.

Otsu assumes a bimodal histogram. A slide that is almost entirely tissue,
or almost entirely background, has no valley to find and Otsu will split
noise. Sanity-check the resulting tissue fraction and fall back to a fixed
threshold when it lands outside a plausible range.

Pen marks, coverslip edges, air bubbles and out-of-focus regions all pass
a saturation threshold. They are a large fraction of real-world artefacts
and need explicit handling, not a better threshold.
```

## Tile Extraction

```python
def tile_grid(slide, level, size, overlap=0):
    """Yield level-0 locations for a tile grid at `level`."""
    d = slide.level_downsamples[level]
    w, h = slide.level_dimensions[level]
    step = size - overlap
    for y in range(0, h - size + 1, step):
        for x in range(0, w - size + 1, step):
            yield (int(x * d), int(y * d))          # level 0 frame
```

```
Overlap matters when a model has an effective receptive field near the tile
size, or when you stitch predictions back together. Without overlap,
objects on a tile boundary are split and counted twice or missed.

Discard tiles below a tissue fraction, but record the threshold. "Tiles with
>50% tissue" and "tiles with >10% tissue" produce different cohorts, and the
number is rarely reported.

read_region returns RGBA. The alpha channel is not decoration: on some
formats it marks unscanned area. Calling .convert("RGB") composites onto
black by default, which turns unscanned regions into black tissue-coloured
pixels. Composite onto white explicitly for H&E.
```

```python
from PIL import Image

rgba = slide.read_region(loc, level, (size, size))
bg = Image.new("RGB", rgba.size, (255, 255, 255))
bg.paste(rgba, mask=rgba.split()[3])       # composite on white, not black
tile = bg
```

## Stain Normalization

Two H&E slides from different labs differ in colour more than they differ in biology. A model trained on one scanner degrades on another.

```python
import torch
from torchstain.torch import MacenkoNormalizer     # 1.4.1

normalizer = MacenkoNormalizer(backend="torch")
normalizer.fit(reference_tile)                     # one target image
normalized, H, E = normalizer.normalize(I=tile, stains=True)
```

```
Method choice:

  Macenko    SVD on the optical-density plane, picks stain vectors from
             percentile angles. Fast, deterministic, the default.
  Reinhard   matches mean and std in LAB space. Cheapest, ignores stain
             structure entirely; fine for mild shifts.
  Vahadane   sparse NMF, better on strong stain variation, much slower.

torchstain provides Macenko, MultiMacenko and Reinhard. It does NOT ship
Vahadane. For sparse-NMF separation use HistomicsTK's
separate_stains_xu_snmf, or Macenko where speed matters.

The reference tile is a parameter of your pipeline, not an implementation
detail. Every normalized value depends on it. Record which slide and which
tile, and reuse the same one across train and test, or you have introduced
a covariate shift you cannot see.

Normalization on a mostly-background tile estimates stain vectors from
glass and produces garbage. Run tissue detection first, and skip
normalization for tiles below the tissue threshold rather than normalizing
them badly.
```

## Colour Deconvolution

Separating H&E into its stain channels, via Beer-Lambert in optical-density space.

```python
from skimage.color import rgb2hed, hed2rgb, rgb_from_hed

hed = rgb2hed(tile)          # channels: Hematoxylin, Eosin, DAB
h = hed[..., 0]              # nuclei
e = hed[..., 1]              # cytoplasm and stroma
```

```
rgb2hed always returns THREE channels, H, E and DAB, because it uses a
fixed 3x3 stain matrix. On an H&E slide the DAB channel is not a stain
measurement; it absorbs whatever the H and E vectors cannot explain. Do not
interpret it as DAB positivity on a slide that never saw DAB.

The stain matrix is fixed, not fitted. rgb_from_hed rows are the H, E and
DAB absorption vectors from Ruifrok and Johnston. If your slides deviate
from those reference stains, an estimated matrix (Macenko or SNMF) is more
faithful than the built-in constant.

NEGATIVE CONCENTRATIONS ARE CLIPPED TO ZERO. separate_stains ends with
np.maximum(stains, 0), so any colour outside the cone spanned by the stain
vectors loses information silently.

Measured on scikit-image 0.26.0 with random RGB in [0.4, 0.9]:
    pixels with at least one clipped channel : 784 of 1024
    round-trip max error where NOT clipped   : 1.1e-16  (exact)
    round-trip max error where clipped       : 6.1e-01  (large)

So rgb2hed -> hed2rgb is exact only for colours the stain basis can
represent. Real H&E mostly lies inside the cone and clips far less than
random RGB, but the failure is silent either way. If you need a faithful
round trip, check for zeroed channels rather than assuming.

Input is also floored: np.maximum(rgb, 1e-6) avoids log(0), so pure black
is not preserved either.
```

## Output Specification

| Output | Format | Description |
|--------|--------|-------------|
| `tiles/` | PNG or a tile store | extracted tiles, named by level-0 coordinates |
| `tile_index.csv` | CSV | slide_id, level-0 x/y, level, size, mpp, tissue fraction |
| `tissue_mask.png` | PNG | binary mask at the detection level |
| `slide_manifest.csv` | CSV | slide_id, vendor, mpp-x, mpp-y, objective power, level dims |
| `stain_reference.png` | PNG | the exact reference tile used for normalization |
| `qc_flags.csv` | CSV | slides missing mpp, failed Otsu, or with extreme tissue fraction |

Name tiles by their **level 0** coordinates and record the level and mpp beside them. A tile named by level-2 coordinates cannot be located on the slide without knowing which level produced it.

## Validation Checks

```
Reading
  location passed to read_region is scaled to level 0; size is not.
  Level chosen with get_best_level_for_downsample, never by == on a float.
  mpp-x and mpp-y both read and validated; slides missing them are flagged.
  bounds-* honoured for formats that use them.

Tiling
  Tissue detection run before tiling.
  Tissue fraction threshold recorded in the manifest.
  RGBA composited onto white, not converted straight to RGB.
  Tile coordinates stored in the level 0 frame.

Stain handling
  Reference tile recorded and reused across train and test.
  Normalization skipped for tiles below the tissue threshold.
  DAB channel not interpreted as a stain on H&E-only slides.
  Clipped channels checked when a faithful round trip matters.

Reproducibility
  Slide manifest records vendor and mpp per slide, so scanner effects can
  be tested as a covariate later.
```

## Common Pitfalls

### Reading
1. **Mixing coordinate frames in `read_region`**: `location` is level 0, `size` is the target level. The result has the right shape and the wrong content, and it only appears once you move off level 0. Scale the location by `level_downsamples[level]`.
2. **Treating `level_downsamples` as integers**: they are floats such as 4.0000123 because level dimensions round per axis. Use `get_best_level_for_downsample` rather than an equality test.
3. **Reading at a coarser level and upscaling**: `get_best_level_for_downsample` errs toward more resolution. Read finer and resize down; upscaling invents detail.
4. **Assuming `openslide.mpp-x` exists**: it is optional and absent on some slides. Validate up front and flag, rather than defaulting to 0.25 and silently mixing scales.
5. **Ignoring `bounds-*` on MIRAX slides**: the scanned region can be a small part of a much larger canvas, so most tiles are empty space.
6. **Installing only `openslide-python`**: it is a binding whose sole dependency is Pillow. Without `openslide-bin` or a system OpenSlide it fails at load.

### Scale
7. **Treating "40x" as a resolution**: nominal objective power maps to roughly 0.23-0.28 µm/px depending on scanner. Tiles from two scanners at "40x" are at different physical scales and the model learns the scanner. Work in mpp.
8. **Ignoring anisotropic pixels**: mpp-x and mpp-y can differ. Check both.

### Tiling
9. **Converting RGBA straight to RGB**: `.convert("RGB")` composites onto black, turning unscanned area into dark tissue-coloured pixels. Composite onto white explicitly.
10. **Tiling without tissue detection**: most of a slide is glass, and background tiles dominate the cohort.
11. **Not recording the tissue-fraction threshold**: ">50% tissue" and ">10% tissue" are different datasets, and the number is rarely reported.
12. **Zero overlap when stitching predictions**: objects on a boundary are split. Use overlap when the receptive field approaches the tile size.

### Stain
13. **Using `staintools`**: last released 2019-04-11 and archived on GitHub in 2021. Use `torchstain` or HistomicsTK.
14. **Expecting Vahadane from torchstain**: it ships Macenko, MultiMacenko and Reinhard only. Sparse NMF lives in HistomicsTK as `separate_stains_xu_snmf`.
15. **Not recording the stain reference tile**: every normalized value depends on it. An unrecorded reference makes the pipeline unreproducible and can shift train against test.
16. **Normalizing background tiles**: stain vectors estimated from glass are meaningless. Detect tissue first.
17. **Reading the DAB channel on an H&E slide**: `rgb2hed` always returns three channels, and the third absorbs residual. It is not DAB positivity.
18. **Assuming `rgb2hed`/`hed2rgb` round-trips**: negatives are clipped to zero, so the inverse is exact only where nothing clipped (measured: 1.1e-16 unclipped, 6.1e-01 clipped). Check for zeroed channels when it matters.

## Related Skills

- [`cancer-multiomics`](../cancer-multiomics/SKILL.md): the molecular data that slide-level features are usually correlated against
- [`spatial-transcriptomics`](../spatial-transcriptomics/SKILL.md): H&E images registered to the same tissue section
- [`foundation-models`](../foundation-models/SKILL.md): the baseline discipline that applies equally to pathology encoders
- [`survival-analysis`](../survival-analysis/SKILL.md): consumes slide-level features as prognostic covariates

## Public Datasets for Testing

| Dataset | Content | Access |
|---------|---------|--------|
| OpenSlide test data | Small slides in every supported vendor format | open, openslide.cs.cmu.edu |
| TCGA diagnostic slides | ~30k H&E WSIs across tumour types | GDC portal, open |
| CAMELYON16 / 17 | Lymph node metastasis, with annotations | grand-challenge, registration |
| PANDA | Prostate biopsies with ISUP grades | Kaggle |
