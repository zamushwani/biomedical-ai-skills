#!/usr/bin/env python3
"""Validate the colour-deconvolution claims in the skill.

The skill states that scikit-image's rgb2hed clips negative stain
concentrations to zero, so the rgb2hed -> hed2rgb round trip is exact only
for colours the stain basis can represent. This measures that directly.

All synthetic. No slide, no download.

Requirements: numpy, scikit-image
Runtime: a few seconds.
"""
import sys
import numpy as np

try:
    from skimage.color import rgb2hed, hed2rgb, rgb_from_hed
except ImportError:
    print("SKIP: scikit-image not installed.")
    sys.exit(0)

passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        print(f"  PASS: {name}"); passed += 1
    else:
        print(f"  FAIL: {name}"); failed += 1


print("=== Computational Pathology: Colour Deconvolution ===\n")

# The HED stain matrix always has three rows, so rgb2hed always returns 3 channels
check("rgb_from_hed is a 3x3 stain matrix", rgb_from_hed.shape == (3, 3))

rng = np.random.default_rng(0)
img = rng.random((32, 32, 3)) * 0.5 + 0.4      # random RGB in [0.4, 0.9]
hed = rgb2hed(img)
check("rgb2hed returns three channels (H, E, DAB), even for H&E",
      hed.shape[-1] == 3)

# The clipping claim: separate_stains ends with np.maximum(stains, 0)
back = hed2rgb(hed)
clipped = (hed == 0).any(axis=-1)
err = np.abs(img - back).max(axis=-1)

n_clipped = int(clipped.sum())
total = clipped.size
print(f"\n  random RGB in [0.4, 0.9], {total} pixels:")
print(f"    pixels with a zeroed (clipped) channel : {n_clipped}")
print(f"    round-trip max error where clipped     : {err[clipped].max():.2e}")
if (~clipped).any():
    print(f"    round-trip max error where NOT clipped : {err[~clipped].max():.2e}")

check("Most random-RGB pixels lose a channel to clipping", n_clipped > total // 2)
check("Round trip is exact (< 1e-10) where nothing clipped",
      (~clipped).any() and err[~clipped].max() < 1e-10)
check("Round trip is lossy (> 1e-2) where a channel clipped",
      err[clipped].max() > 1e-2)
print("    -> the inverse is exact only for colours the stain basis represents")

# The input floor: np.maximum(rgb, 1e-6) means pure black is not preserved either
black = np.zeros((4, 4, 3))
check("Pure black survives deconvolution to ~itself (input floored at 1e-6)",
      np.abs(hed2rgb(rgb2hed(black))).max() < 1e-3)

# A pixel exactly on a stain vector should NOT clip the way random colour does
white = np.ones((4, 4, 3))
check("Pure white round-trips exactly (max error < 1e-6)",
      np.abs(white - hed2rgb(rgb2hed(white))).max() < 1e-6)

print(f"\n=== Deconvolution: {passed} passed, {failed} failed ===")
sys.exit(1 if failed else 0)
