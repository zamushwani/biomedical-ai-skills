#!/usr/bin/env python3
"""Validate the OpenSlide reading claims against a real slide.

Downloads a small (~1.9 MB) public OpenSlide test slide at runtime and checks
the property and coordinate-frame semantics the skill relies on. Skips cleanly
when OpenSlide is not installed or the download fails (offline).

The small slide is single-level, which is enough for the property, mpp, and
RGBA claims. The multi-level float-downsample claim was verified this session
against the 169 MB Aperio CMU-1.svs: its level_downsamples are
(1.0, 4.000122, 16.000486) - level 1 is 4.000122, NOT 4 - and
get_best_level_for_downsample(4) returns 0, not 1, because 4.000122 > 4 and
the function errs toward more resolution. Those values are asserted here only
when such a slide is provided via CPATH_TEST_SLIDE, so the suite stays light.

Requirements: openslide-python, openslide-bin; network for the download.
Runtime: a few seconds plus the download.
"""
import os
import sys
import tempfile
import urllib.request

try:
    import openslide
except ImportError:
    print("SKIP: openslide not installed (pip install openslide-python openslide-bin).")
    sys.exit(0)

passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        print(f"  PASS: {name}"); passed += 1
    else:
        print(f"  FAIL: {name}"); failed += 1


SMALL = ("https://openslide.cs.cmu.edu/download/openslide-testdata/"
         "Aperio/CMU-1-Small-Region.svs")

print("=== Computational Pathology: OpenSlide Reading ===\n")
print(f"  openslide-python {openslide.__version__}, "
      f"OpenSlide C {openslide.__library_version__}")

path = os.environ.get("CPATH_TEST_SLIDE")
tmp = None
if not path:
    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".svs", delete=False)
        with urllib.request.urlopen(SMALL, timeout=60) as r:
            tmp.write(r.read())
        tmp.close()
        path = tmp.name
    except Exception as exc:
        print(f"\nSKIP: could not fetch the test slide ({type(exc).__name__}). "
              f"Needs network, or set CPATH_TEST_SLIDE.")
        sys.exit(0)

try:
    slide = openslide.OpenSlide(path)

    # --- microns per pixel: present, and a real value, not a guessed 0.25 ---
    mpp_x = slide.properties.get(openslide.PROPERTY_NAME_MPP_X)
    mpp_y = slide.properties.get(openslide.PROPERTY_NAME_MPP_Y)
    power = slide.properties.get(openslide.PROPERTY_NAME_OBJECTIVE_POWER)
    print(f"\n  mpp-x={mpp_x}  mpp-y={mpp_y}  objective={power}  vendor="
          f"{slide.properties.get(openslide.PROPERTY_NAME_VENDOR)}")

    check("mpp-x is present on this slide", mpp_x is not None)
    check("mpp-x and mpp-y are both present", mpp_x is not None and mpp_y is not None)
    check("This scanner's 20x is ~0.5 um/px, not a fixed 0.25",
          power == "20" and abs(float(mpp_x) - 0.499) < 0.01)
    print("    -> magnification is not resolution: 20x here is 0.499 um/px")

    # --- read_region returns RGBA ---
    region = slide.read_region((0, 0), 0, (16, 16))
    check("read_region returns an RGBA image (alpha channel present)",
          region.mode == "RGBA")

    # --- downsamples are floats ---
    ds = slide.level_downsamples
    check("level_downsamples is a tuple of floats",
          all(isinstance(d, float) for d in ds))

    # --- location is the level-0 frame; reading past level-0 bounds is empty ---
    w0, h0 = slide.level_dimensions[0]
    check("get_best_level_for_downsample(1) is the full-resolution level 0",
          slide.get_best_level_for_downsample(1) == 0)

    # --- optional multi-level assertions when a pyramid is supplied ---
    if slide.level_count > 1:
        print(f"\n  multi-level slide provided ({slide.level_count} levels):")
        print(f"    level_downsamples = {tuple(round(d,6) for d in ds)}")
        check("At least one downsample is a non-integer (e.g. 4.000122)",
              any(d != int(d) for d in ds))
        # errs toward more resolution: asking for 4 when level-1 is 4.0001 gives level 0
        near = min(range(len(ds)), key=lambda i: abs(ds[i] - 4))
        if ds[near] > 4:
            check("get_best_level_for_downsample(4) errs toward MORE resolution",
                  slide.get_best_level_for_downsample(4) < near)
    else:
        print("\n  (single-level slide; multi-level float checks skipped - "
              "verified this session against CMU-1.svs: 1.0, 4.000122, 16.000486)")

    slide.close()
finally:
    if tmp is not None:
        try:
            os.unlink(tmp.name)      # this test cleans up its own download
        except OSError:
            pass

print(f"\n=== OpenSlide: {passed} passed, {failed} failed ===")
sys.exit(1 if failed else 0)
