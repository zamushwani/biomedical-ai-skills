#!/usr/bin/env python3
"""Master validation script for the foundation-models skill.

Validates the skill's central claim (HVG+PCA is a strong baseline) and the two
input contracts that fail silently (rank-value tokenization, gene vocabulary).

Usage:
    python run_all.py              # run all tests
    python run_all.py baseline     # run one test

Expected runtime: 2-5 minutes (30 MB download on first run, then cached)

Requirements:
    scanpy, scikit-learn, scipy

Optional:
    torch and a foundation model checkpoint. Model weights are multi-gigabyte,
    so the comparison against a real embedding is skipped when absent and the
    baseline is still established.
"""

import subprocess
import sys
from pathlib import Path

TESTS = ["vocabulary", "tokenization", "baseline"]  # cheapest first

args = sys.argv[1:]
if args:
    if args[0] not in TESTS:
        sys.exit(f"Unknown test: {args[0]}. Choose from: {', '.join(TESTS)}")
    tests = [args[0]]
else:
    tests = TESTS

try:
    from importlib.metadata import version

    sc_v = version("scanpy")
    sk_v = version("scikit-learn")
except Exception:
    sys.exit("scanpy and scikit-learn are required: pip install scanpy scikit-learn")

print("Foundation Models Skill Validation")
print("===================================")
print(f"Python:       {sys.version.split()[0]}")
print(f"scanpy:       {sc_v}")
print(f"scikit-learn: {sk_v}")

try:
    print(f"torch:        {version('torch')}")
except Exception:
    print("torch:        not installed (model comparison will be skipped)")

print(f"Tests to run: {', '.join(tests)}\n")

script_dir = Path(__file__).parent
failed = []

for test in tests:
    script = script_dir / f"validate_{test}.py"
    if not script.exists():
        print(f"Script not found: {script}")
        failed.append(test)
        continue
    print(f"\n--- Running {test} validation ---\n")
    result = subprocess.run([sys.executable, str(script)], check=False)
    if result.returncode != 0:
        failed.append(test)

print("\n===================================")
if failed:
    print(f"Failed: {', '.join(failed)}")
    sys.exit(1)
print("All validations passed.")
