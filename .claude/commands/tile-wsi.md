---
description: Tile a whole-slide image with tissue detection for downstream modelling. Use for .svs/.ndpi/.mrxs slides, OpenSlide, or when the user asks about patches, tiles, or WSI preprocessing.
argument-hint: [slide-path] [target-mpp]
allowed-tools: Read Grep Glob Bash(python3 *)
---

Tile the slide at `$0` at a target resolution of `$1` microns per pixel (default: 0.5).

Follow the `computational-pathology` skill. Two bugs cost the most time here:

1. **`read_region(location, level, size)` mixes coordinate frames.** `location` is in the **level 0** frame; `size` is in the **target level** frame. Scale the location by `level_downsamples[level]`. The failure is silent: correct shape, wrong region — and a level-0 prototype hides it entirely.
2. **Magnification is not resolution.** "40x" maps to roughly 0.23–0.28 um/px depending on scanner, so tiles cut at "40x" from two scanners sit at different physical scales and the model learns the scanner. Work in mpp.

Also:

3. **`level_downsamples` are floats** (4.000122, not 4). Pick levels with `get_best_level_for_downsample`, never `==`.
4. **Composite RGBA onto white.** `.convert("RGB")` composites onto black, turning unscanned area into dark tissue-coloured pixels.
5. **Detect tissue by saturation, not intensity** — glass is bright *and* unsaturated, while pale adipose is real signal.
6. **Record the tissue-fraction threshold.** ">50% tissue" and ">10% tissue" are different datasets.

Report: slide mpp and vendor, level chosen, tile count, tissue fraction threshold, and tile coordinates in the **level 0** frame.

If `$0` is empty, ask for the slide path.
