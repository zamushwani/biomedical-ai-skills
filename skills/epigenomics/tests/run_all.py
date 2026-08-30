#!/usr/bin/env python3
"""Master validation script for the epigenomics skill.

Usage:
    python run_all.py            # all suites
    python run_all.py claims

Suites skip cleanly (exit 0) when a dependency or network is unavailable, so
a partial environment reports what it could not check rather than failing.
"""
import subprocess
import sys
from pathlib import Path

SUITES = ["claims"]

args = sys.argv[1:]
suites = args or SUITES
unknown = [a for a in suites if a not in SUITES]
if unknown:
    print(f"Unknown suite(s): {unknown}. Choose from {SUITES}")
    sys.exit(2)

here = Path(__file__).resolve().parent
print("epigenomics validation")
print("=" * 40)
print(f"Python: {sys.version.split()[0]}")
print(f"Suites: {', '.join(suites)}\n")

failed = []
for s in suites:
    script = here / f"validate_{s}.py"
    if not script.exists():
        print(f"Script not found: {script}"); failed.append(s); continue
    print(f"\n--- Running {s} validation ---\n")
    if subprocess.run([sys.executable, str(script)]).returncode != 0:
        failed.append(s)

print("\n" + "=" * 40)
if failed:
    print(f"Failed: {', '.join(failed)}"); sys.exit(1)
print("All validations passed.")
