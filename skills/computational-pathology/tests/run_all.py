#!/usr/bin/env python3
"""Master validation script for the computational-pathology skill.

Usage:
    python run_all.py                 # all suites
    python run_all.py deconvolution   # one suite

Suites that need an optional dependency (openslide) skip cleanly with a SKIP
line rather than failing, so a partial environment reports what it could not
check. The openslide suite downloads a ~1.9 MB public test slide at runtime
and deletes it afterward; set CPATH_TEST_SLIDE to a local slide to skip the
download (and to exercise the multi-level float-downsample checks).

Expected runtime: under a minute plus the small download.
"""
import subprocess
import sys
from pathlib import Path

SUITES = ["deconvolution", "tissue_tiling", "openslide"]

args = sys.argv[1:]
if args:
    unknown = [a for a in args if a not in SUITES]
    if unknown:
        print(f"Unknown suite(s): {unknown}. Choose from {SUITES}")
        sys.exit(2)
    suites = args
else:
    suites = SUITES

here = Path(__file__).resolve().parent

print("Computational Pathology Skill Validation")
print("=" * 40)
print(f"Python: {sys.version.split()[0]}")
for pkg in ["numpy", "skimage", "PIL", "openslide"]:
    try:
        mod = __import__(pkg)
        print(f"{pkg}: {getattr(mod, '__version__', 'installed')}")
    except ImportError:
        print(f"{pkg}: not installed")
print(f"Suites: {', '.join(suites)}\n")

failed = []
for suite in suites:
    script = here / f"validate_{suite}.py"
    if not script.exists():
        print(f"Script not found: {script}")
        failed.append(suite)
        continue
    print(f"\n--- Running {suite} validation ---\n")
    if subprocess.run([sys.executable, str(script)]).returncode != 0:
        failed.append(suite)

print("\n" + "=" * 40)
if failed:
    print(f"Failed: {', '.join(failed)}")
    sys.exit(1)
print("All validations passed.")
