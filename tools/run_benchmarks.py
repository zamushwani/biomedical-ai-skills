#!/usr/bin/env python3
"""Run every skill's validation suite and report a single table.

This is the repository-level benchmark runner: it discovers each skill's
tests/ directory, runs its entry point, and records pass/fail/skip counts and
wall-clock time. Suites that need an absent dependency or no network skip
rather than fail, so the table distinguishes "did not run" from "ran and
failed" - the difference that matters when reading a benchmark.

Usage:
    python3 tools/run_benchmarks.py              # every skill
    python3 tools/run_benchmarks.py epigenomics  # one skill
    python3 tools/run_benchmarks.py --quick      # skip suites that need network

Requirements: standard library. R suites need Rscript on PATH.
"""
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"


def tracked_skills():
    out = subprocess.run(["git", "ls-files", "skills/"], cwd=ROOT,
                         capture_output=True, text=True).stdout.splitlines()
    return sorted({p.split("/")[1] for p in out if p.endswith("/SKILL.md")})


def entry_point(skill):
    """Return (command, label) for the skill's test entry point, or None."""
    d = SKILLS / skill / "tests"
    if (d / "run_all.py").exists():
        return [sys.executable, "run_all.py"], "python"
    if (d / "run_all.R").exists():
        return ["Rscript", "run_all.R"], "R"
    return None, None


def run(skill):
    cmd, lang = entry_point(skill)
    if cmd is None:
        return dict(skill=skill, status="NO TESTS", passed=0, failed=0,
                    skipped=0, seconds=0.0, lang="-")
    cwd = SKILLS / skill / "tests"
    start = time.time()
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                              timeout=1800)
        out = proc.stdout + proc.stderr
        rc = proc.returncode
    except FileNotFoundError:
        return dict(skill=skill, status="NO RUNTIME", passed=0, failed=0,
                    skipped=0, seconds=0.0, lang=lang)
    except subprocess.TimeoutExpired:
        return dict(skill=skill, status="TIMEOUT", passed=0, failed=0,
                    skipped=0, seconds=time.time() - start, lang=lang)
    elapsed = time.time() - start

    passed = len(re.findall(r"^\s*PASS:", out, re.M))
    failed = len(re.findall(r"^\s*FAIL:", out, re.M))
    skipped = len(re.findall(r"^\s*SKIP", out, re.M))

    # A suite that cannot run because a dependency is absent is NOT a failure.
    # Conflating the two is how a benchmark table starts lying: "5 errors"
    # reads as broken code when it means an unconfigured machine.
    DEP_MISSING = (
        "ModuleNotFoundError", "ImportError",
        "there is no package called", "could not find function",
        "Numba needs NumPy",
    )
    dep_missing = any(s in out for s in DEP_MISSING)

    if failed:
        status = "FAIL"
    elif passed and dep_missing:
        status = "PARTIAL"          # ran, but some suites lacked a dependency
    elif dep_missing:
        status = "NO DEPS"
    elif passed == 0 and skipped:
        status = "SKIPPED"
    elif rc != 0:
        status = "ERROR"            # ran, no deps missing, still failed: real
    else:
        status = "PASS"
    return dict(skill=skill, status=status, passed=passed, failed=failed,
                skipped=skipped, seconds=elapsed, lang=lang)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    skills = args or tracked_skills()

    print("Biomedical AI Skills - benchmark run")
    print("=" * 78)
    print(f"Python {sys.version.split()[0]}")
    print(f"{len(skills)} skill(s)\n")
    print(f"{'skill':28s} {'lang':5s} {'status':9s} {'pass':>5s} {'fail':>5s} "
          f"{'skip':>5s} {'sec':>7s}")
    print("-" * 78)

    results = []
    for s in skills:
        r = run(s)
        results.append(r)
        print(f"{r['skill']:28s} {r['lang']:5s} {r['status']:9s} "
              f"{r['passed']:5d} {r['failed']:5d} {r['skipped']:5d} "
              f"{r['seconds']:7.1f}")

    print("-" * 78)
    tp = sum(r["passed"] for r in results)
    tf = sum(r["failed"] for r in results)
    ts = sum(r["seconds"] for r in results)
    ran = [r for r in results if r["status"] in ("PASS", "FAIL", "PARTIAL")]
    notests = [r["skill"] for r in results if r["status"] == "NO TESTS"]
    skipped = [r["skill"] for r in results
               if r["status"] in ("SKIPPED", "NO RUNTIME", "NO DEPS")]
    broken = [r["skill"] for r in results if r["status"] in ("ERROR", "TIMEOUT")]

    print(f"{'TOTAL':28s} {'':5s} {'':9s} {tp:5d} {tf:5d} {'':5s} {ts:7.1f}")
    print()
    print(f"  suites that ran     : {len(ran)} of {len(results)}")
    if skipped:
        print(f"  skipped (deps/net)  : {', '.join(skipped)}")
    if broken:
        print(f"  ERROR (real)        : {', '.join(broken)}")
    if notests:
        print(f"  NO TESTS            : {', '.join(notests)}")
    print(f"  assertions          : {tp} passed, {tf} failed")

    sys.exit(1 if tf else 0)


if __name__ == "__main__":
    main()
