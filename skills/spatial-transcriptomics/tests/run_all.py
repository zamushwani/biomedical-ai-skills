#!/usr/bin/env python3
"""Master validation script for the spatial-transcriptomics skill.

Tests against public 10x Visium mouse brain and an IMC dataset.

Usage:
    python run_all.py              # run all tests
    python run_all.py neighbors    # run one test

Expected runtime: 8-15 minutes (~100 MB download on first run)

Requirements:
    squidpy>=1.8, scanpy>=1.12   (both require Python >= 3.12)
"""

import subprocess
import sys
from pathlib import Path

TESTS = ["neighbors", "loading", "svg"]   # cheapest download first

args = sys.argv[1:]
if args:
    if args[0] not in TESTS:
        sys.exit(f"Unknown test: {args[0]}. Choose from: {', '.join(TESTS)}")
    tests = [args[0]]
else:
    tests = TESTS

if sys.version_info < (3, 12):
    sys.exit(f"squidpy 1.8.3 requires Python >= 3.12 (found {sys.version.split()[0]})")

try:
    from importlib.metadata import version

    sq_version = version("squidpy")
    sc_version = version("scanpy")
except Exception:
    sys.exit("squidpy and scanpy are required: pip install 'squidpy>=1.8' 'scanpy>=1.12'")

print("Spatial Transcriptomics Skill Validation")
print("========================================")
print(f"Python:  {sys.version.split()[0]}")
print(f"squidpy: {sq_version}")
print(f"scanpy:  {sc_version}")
print(f"Tests to run: {', '.join(tests)}\n")

script_dir = Path(__file__).parent

for test in tests:
    script = script_dir / f"validate_{test}.py"
    if not script.exists():
        print(f"Script not found: {script}")
        continue
    print(f"\n--- Running {test} validation ---\n")
    subprocess.run([sys.executable, str(script)], check=False)

print("\n========================================")
print("Validation complete.")
