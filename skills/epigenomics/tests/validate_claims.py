#!/usr/bin/env python3
"""Validate the version and tooling claims in the epigenomics skill.

The DiffBind 3.x changes are the reason this skill exists, so they are
checked against the package's own NEWS file rather than restated. Also
confirms MACS3 supersedes MACS2 and that JASPAR2024 is the newest release.

Needs network; skips cleanly without it.

Requirements: standard library only.
Runtime: under 30 seconds.
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        print(f"  PASS: {name}"); passed += 1
    else:
        print(f"  FAIL: {name}"); failed += 1


def pypi(pkg):
    with urllib.request.urlopen(f"https://pypi.org/pypi/{pkg}/json", timeout=30) as r:
        return json.load(r)


def http_status(url):
    try:
        with urllib.request.urlopen(url, timeout=25):
            return 200
    except urllib.error.HTTPError as e:
        return e.code


print("=== Epigenomics: tooling and version claims ===\n")

skill = (Path(__file__).resolve().parents[1] / "SKILL.md").read_text()

# --- MACS3 supersedes MACS2 ---
try:
    m3, m2 = pypi("MACS3"), pypi("MACS2")
except (urllib.error.URLError, TimeoutError) as exc:
    print(f"SKIP: PyPI unreachable ({type(exc).__name__}). These checks need network.")
    sys.exit(0)


def release_date(meta):
    v = meta["info"]["version"]
    rel = meta["releases"].get(v, [])
    return v, (rel[0]["upload_time"][:10] if rel else "?")


v3, d3 = release_date(m3)
v2, d2 = release_date(m2)
print(f"  MACS3 {v3} ({d3})   MACS2 {v2} ({d2})")
check("MACS3 has a more recent release than MACS2", d3 > d2)
check("MACS2's last release predates 2024", d2 < "2024-01-01")
check("SKILL.md tells the reader to use MACS3", "not MACS2" in skill)

# --- DiffBind 3.x changes, from the package's own NEWS ---
try:
    news = urllib.request.urlopen(
        "https://bioconductor.org/packages/release/bioc/news/DiffBind/NEWS",
        timeout=30).read().decode("utf-8", "replace")
    print(f"\n  DiffBind NEWS retrieved ({len(news.splitlines())} lines)")

    check("NEWS confirms dba.count() now centres on summits by default",
          "center around" in news and "401bp" in news)
    check("NEWS confirms the modelling default changed (design=FALSE to revert)",
          "design=FALSE" in news)
    check("NEWS confirms normalization moved to dba.normalize()",
          "dba.normalize()" in news and "Remove normalization options" in news)
    check("NEWS confirms the bSubControl preservation bug", "bSubControl" in news)
    check("NEWS confirms dba.plotProfile() was disabled",
          "dba.plotProfile()" in news and "profileplyr" in news)

    # the skill must carry each of these
    check("SKILL.md records the 401 bp summit default", "401 bp" in skill)
    check("SKILL.md records design = FALSE for old analyses", "design = FALSE" in skill)
    check("SKILL.md records the dba.normalize() move", "dba.normalize()" in skill)
    check("SKILL.md records the 3.22.2 bSubControl fix", "3.22.2" in skill)
    check("SKILL.md records dba.plotProfile() being disabled", "plotProfile" in skill)
except (urllib.error.URLError, TimeoutError):
    print("\n  SKIP: DiffBind NEWS unreachable")

# --- JASPAR releases ---
base = "https://bioconductor.org/packages/release/data/annotation/html"
j24 = http_status(f"{base}/JASPAR2024.html")
j26 = http_status(f"{base}/JASPAR2026.html")
print(f"\n  JASPAR2024 -> HTTP {j24}   JASPAR2026 -> HTTP {j26}")
check("JASPAR2024 exists on Bioconductor", j24 == 200)
check("JASPAR2026 does not exist", j26 == 404)
check("SKILL.md names JASPAR2024 as the latest", "JASPAR2026 does not exist" in skill)

print(f"\n=== Claims: {passed} passed, {failed} failed ===")
sys.exit(1 if failed else 0)
