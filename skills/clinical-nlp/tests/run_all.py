#!/usr/bin/env python3
"""Master validation script for the clinical-nlp skill.

Usage:
    python run_all.py                # all suites
    python run_all.py assertion      # one suite

Each suite skips cleanly (exit 0) when its dependency is absent, so a partial
environment reports what it could not check rather than failing.

Expected runtime: under 2 minutes.
"""
import subprocess
import sys
from pathlib import Path

SUITES = ["assertion", "dependencies", "deidentification"]

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

print("Clinical NLP Skill Validation")
print("=" * 31)
print(f"Python: {sys.version.split()[0]}")
for pkg in ["medspacy", "spacy", "presidio_analyzer", "packaging"]:
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

print("\n" + "=" * 31)
if failed:
    print(f"Failed: {', '.join(failed)}")
    sys.exit(1)
print("All validations passed.")
