# Validation Tests

Three suites covering the claims most likely to bite: scikit-image's colour-deconvolution clipping, tissue detection and tile compositing on synthetic images, and OpenSlide's property and coordinate-frame semantics on a real slide.

**Executed 2026-08-23** on Python 3.13.5 with scikit-image 0.26.0, Pillow 12.3.0, openslide-python 1.4.6 (OpenSlide C 4.0.1): **24 assertions, 0 failures** with the small self-downloaded slide (**26** when a multi-level slide is supplied).

The synthetic suites use no data. The OpenSlide suite downloads a ~1.9 MB public test slide at runtime and **deletes it afterward**; nothing is committed.

## Running

```bash
cd skills/computational-pathology/tests
python run_all.py                    # all three
python run_all.py deconvolution      # one suite
```

Optional heavier install for the OpenSlide suite:

```bash
pip install numpy scikit-image Pillow        # synthetic suites
pip install openslide-python openslide-bin   # OpenSlide suite (else it SKIPs)
```

Set `CPATH_TEST_SLIDE=/path/to/slide.svs` to point the OpenSlide suite at a local slide instead of downloading. A multi-level slide additionally exercises the float-downsample checks.

## What each suite checks

**deconvolution** (7 assertions, no download). `rgb2hed` always returns three channels (H, E, DAB) because the stain matrix is a fixed 3×3, and `separate_stains` ends with `np.maximum(stains, 0)`, so negative concentrations clip to zero.

**tissue_tiling** (11 assertions, no download). Saturation keeps pale tissue that an intensity threshold discards; `.convert("RGB")` turns unscanned (alpha 0) area black while compositing on white keeps it white; and `tile_grid` scales tile locations into the level-0 frame.

**openslide** (6 assertions with the small slide, 8 with a multi-level one). Reads a real Aperio slide: mpp is present and equals 0.499 while the objective power is 20 (so 20× is ~0.5 µm/px here, not a fixed 0.25); `read_region` returns RGBA; downsamples are floats.

## Measured values

### Colour deconvolution — random RGB in [0.4, 0.9], 1024 pixels

| | |
|---|---|
| pixels with ≥1 clipped channel | **784 / 1024** |
| round-trip max error, unclipped | **1.11e-16** (exact) |
| round-trip max error, clipped | **6.12e-01** |

Pure white round-trips exactly; pure black survives because input is floored at `1e-6`.

### Tissue detection — fraction of each region kept

| Region | Saturation rule | Intensity rule |
|---|---|---|
| dense tissue | 1.00 | 1.00 |
| **pale tissue** | **1.00** | **0.00** |
| glass | 0.00 | 0.00 |

The intensity rule discards pale adipose/mucin, which is real signal.

### RGBA compositing

| Unscanned (alpha 0) pixel via | Result |
|---|---|
| `.convert("RGB")` | (0, 0, 0) — black |
| composite on white | (255, 255, 255) — white |

### OpenSlide — Aperio CMU-1 (verified this session)

| | |
|---|---|
| single-region slide mpp-x / mpp-y | 0.499 / 0.499 |
| single-region slide objective | 20 |
| **CMU-1 multi-level downsamples** | **(1.0, 4.000122, 16.000486)** |
| `get_best_level_for_downsample(4)` on CMU-1 | **0**, not 1 |

Level 1 is **4.000122, not 4** — the reason `level_downsamples` must be treated as floats and levels chosen with `get_best_level_for_downsample`. That function returns 0 for a target of 4 because 4.000122 exceeds 4 and it errs toward more resolution.

## Notes

- **No slide is committed.** The OpenSlide suite fetches a small public slide at runtime and removes it; the synthetic suites need no data.
- **Cell segmentation is not tested here.** StarDist and HoVer-Net pull heavy deep-learning backends (TensorFlow, PyTorch) and their own model weights; the skill's segmentation claims are about tooling and licence, verified from source and package metadata rather than by running a network. The measurable image-processing claims — deconvolution, tissue detection, compositing, coordinate frames — are what these suites cover.
