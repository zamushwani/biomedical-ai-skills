#!/usr/bin/env python3
"""Master validation script for the single-cell-atlas skill.

Tests the pipeline against 10x PBMC 3k and Kang et al. 2018 (GSE96583).

Usage:
    python run_all.py              # run all tests
    python run_all.py qc           # run one test

Expected runtime: 15-25 minutes

Requirements:
    Core:     scanpy>=1.12, leidenalg, scikit-learn
    QC:       scikit-image (for scrublet)
    Integration: pertpy, harmonypy
    Optional: scib-metrics
"""

import runpy
import subprocess
import sys
from pathlib import Path

TESTS = ["qc", "clustering", "integration"]

args = sys.argv[1:]
if args:
    if args[0] not in TESTS:
        sys.exit(f"Unknown test: {args[0]}. Choose from: {', '.join(TESTS)}")
    tests = [args[0]]
else:
    tests = TESTS

try:
    import scanpy

    scanpy_version = scanpy.__version__
except ImportError:
    sys.exit("scanpy is required: pip install 'scanpy>=1.12'")

print("Single-Cell Atlas Skill Validation")
print("===================================")
print(f"Python: {sys.version.split()[0]}")
print(f"scanpy: {scanpy_version}")
print(f"Tests to run: {', '.join(tests)}\n")

script_dir = Path(__file__).parent

for test in tests:
    script = script_dir / f"validate_{test}.py"
    if not script.exists():
        print(f"Script not found: {script}")
        continue
    print(f"\n--- Running {test} validation ---\n")
    try:
        subprocess.run([sys.executable, str(script)], check=False)
    except Exception as exc:  # noqa: BLE001
        print(f"\nERROR in {test} validation: {exc}")

print("\n===================================")
print("Validation complete.")
