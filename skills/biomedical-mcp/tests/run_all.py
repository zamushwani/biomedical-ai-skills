#!/usr/bin/env python3
"""Master validation script for the biomedical-mcp skill.

These are integration tests: they confirm the documented API contracts still
hold against the LIVE GDC, GEO/E-utilities, CIViC, OncoKB and ClinVar APIs,
so the skill's tool code stays correct as those services evolve. Each suite
skips cleanly (exit 0) when its API is unreachable, so an offline run reports
what it could not check rather than failing.

Usage:
    python run_all.py             # all suites
    python run_all.py gdc         # one suite

Expected runtime: under two minutes. Requirements: network, urllib only.
"""
import subprocess
import sys
from pathlib import Path

SUITES = ["gdc", "geo", "biomarker"]

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

print("Biomedical MCP Skill Validation (live integration)")
print("=" * 50)
print(f"Python: {sys.version.split()[0]}")
print(f"Suites: {', '.join(suites)}")
print("These hit live public APIs; suites skip cleanly when offline.\n")

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

print("\n" + "=" * 50)
if failed:
    print(f"Failed: {', '.join(failed)}")
    sys.exit(1)
print("All validations passed.")
