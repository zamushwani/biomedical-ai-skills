#!/usr/bin/env python3
"""Validate tissue detection and tiling claims on synthetic images.

Three claims from the skill:
  - saturation keeps pale tissue that an intensity threshold removes
  - RGBA -> RGB composites onto black, so unscanned area becomes black
    tissue-coloured pixels unless you composite onto white
  - read_region location is in the level-0 frame, so tile coordinates must
    be scaled by the downsample

All synthetic. No slide, no download.

Requirements: numpy, scikit-image, Pillow
Runtime: a few seconds.
"""
import sys
import numpy as np

try:
    from skimage.color import rgb2hsv
    from PIL import Image
except ImportError:
    print("SKIP: scikit-image or Pillow not installed.")
    sys.exit(0)

passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        print(f"  PASS: {name}"); passed += 1
    else:
        print(f"  FAIL: {name}"); failed += 1


print("=== Computational Pathology: Tissue Detection and Tiling ===\n")

# --- saturation vs intensity ---
rng = np.random.default_rng(0)
img = np.ones((60, 60, 3)) * 0.95                       # glass: bright, unsaturated
img[:20, :] = np.array([0.55, 0.25, 0.55])             # dense tissue: saturated
img[20:40, :] = np.array([0.90, 0.78, 0.90])           # pale tissue: light, tinted
img = np.clip(img + rng.normal(0, 0.01, img.shape), 0, 1)

hsv = rgb2hsv(img)
sat_mask = hsv[..., 1] > 0.10        # saturation rule
int_mask = hsv[..., 2] < 0.85        # "dark = tissue" intensity rule

kept = lambda m, r0, r1: m[r0:r1].mean()
print("  fraction of each region kept as tissue:")
print(f"    {'region':8s} {'saturation':>11s} {'intensity':>10s}")
for name, r0, r1 in [("dense", 0, 20), ("pale", 20, 40), ("glass", 40, 60)]:
    print(f"    {name:8s} {kept(sat_mask,r0,r1):>11.2f} {kept(int_mask,r0,r1):>10.2f}")

check("Saturation keeps dense tissue", kept(sat_mask, 0, 20) > 0.95)
check("Saturation keeps PALE tissue", kept(sat_mask, 20, 40) > 0.95)
check("Intensity threshold DROPS pale tissue", kept(int_mask, 20, 40) < 0.05)
check("Both rules reject glass", kept(sat_mask, 40, 60) < 0.05 and kept(int_mask, 40, 60) < 0.05)
print("    -> an intensity rule discards pale adipose/mucin, which is real signal")

# --- RGBA compositing ---
rgba = Image.new("RGBA", (10, 10), (200, 150, 200, 255))
for x in range(5):
    for y in range(10):
        rgba.putpixel((x, y), (0, 0, 0, 0))            # left half unscanned (alpha 0)

naive = np.array(rgba.convert("RGB"))
white_bg = Image.new("RGB", rgba.size, (255, 255, 255))
white_bg.paste(rgba, mask=rgba.split()[3])
composited = np.array(white_bg)

print(f"\n  unscanned pixel via .convert('RGB')     : {tuple(int(v) for v in naive[0,0])}")
print(f"  unscanned pixel composited on white     : {tuple(int(v) for v in composited[0,0])}")
check("convert('RGB') turns unscanned area BLACK", tuple(naive[0, 0]) == (0, 0, 0))
check("Compositing on white keeps unscanned area WHITE",
      tuple(composited[0, 0]) == (255, 255, 255))
check("Scanned pixels are unchanged by the white composite",
      tuple(composited[0, 9]) == (200, 150, 200))
print("    -> black unscanned pixels read as dark tissue to a downstream model")

# --- coordinate-frame arithmetic ---
def tile_grid(downsample, level_w, level_h, size, overlap=0):
    step = size - overlap
    return [(int(x * downsample), int(y * downsample))
            for y in range(0, level_h - size + 1, step)
            for x in range(0, level_w - size + 1, step)]

d = 4.000122                                            # a real slide's level-1 downsample
grid = tile_grid(d, 100, 100, 50)
print(f"\n  tile_grid(downsample={d}, 100x100, size 50):")
print(f"    {grid}")
check("Grid yields 4 tiles for a 100x100 level at size 50", len(grid) == 4)
check("First tile is at the origin", grid[0] == (0, 0))
check("Second-column location is scaled to level 0 (int(50*4.000122)=200)",
      grid[1] == (200, 0))
check("Locations differ from unscaled level coords (would be 50, not 200)",
      grid[1][0] != 50)
print("    -> location goes to read_region in the LEVEL-0 frame; size does not")

print(f"\n=== Tissue and tiling: {passed} passed, {failed} failed ===")
sys.exit(1 if failed else 0)
