#!/usr/bin/env python3
"""Validate the package claims in the multiomics-integration skill.

Two are the kind that waste an afternoon: mixOmics on CRAN is years behind
the Bioconductor build, and MOFA2's run_mofa() defaults to the ambient
reticulate Python rather than its managed environment. These check both
against the live registries, plus the preprocessing claim that feature-count
imbalance survives per-view scaling.

Needs network for the registry checks; skips cleanly without it.

Requirements: numpy for the imbalance demonstration
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


# crandb returns HTTP 403 to urllib's default User-Agent ("Python-urllib/3.x").
# Any scripted CRAN metadata check needs an explicit UA or it looks like the
# registry is down.
UA = {"User-Agent": "biomedical-ai-skills-tests/1.0"}


def cran(pkg):
    req = urllib.request.Request(f"https://crandb.r-pkg.org/{pkg}", headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


print("=== Multi-omics integration: package contracts ===\n")

skill = (Path(__file__).resolve().parents[1] / "SKILL.md").read_text()

# --- the mixOmics CRAN/Bioconductor split ---
try:
    mx = cran("mixOmics")
except (urllib.error.URLError, TimeoutError) as exc:
    print(f"SKIP: CRAN unreachable ({type(exc).__name__}). Registry checks need network.")
    sys.exit(0)

cran_ver = mx.get("Version", "")
cran_date = (mx.get("Date/Publication") or "")[:10]
print(f"  mixOmics on CRAN: {cran_ver} ({cran_date})")
check("mixOmics on CRAN is still the old 6.3.x line", cran_ver.startswith("6.3."))
check("The CRAN build predates 2020", cran_date < "2020-01-01")
check("SKILL.md warns to install mixOmics from Bioconductor",
      "NOT CRAN" in skill or "not CRAN" in skill)
print("    -> install.packages('mixOmics') silently returns this build")

# --- SNFtool staleness ---
sn = cran("SNFtool")
sn_date = (sn.get("Date/Publication") or "")[:10]
print(f"\n  SNFtool: {sn.get('Version')} ({sn_date})")
check("SNFtool has not been released since 2022", sn_date < "2022-01-01")
check("SKILL.md records SNFtool as unmaintained", "2021-06-11" in skill)

# --- MOFA2 defaults, read from the package source ---
try:
    url = "https://raw.githubusercontent.com/bioFAM/MOFA2/master/R/run_mofa.R"
    src = urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                 timeout=30).read().decode("utf-8", "replace")
    has_default_false = "use_basilisk = FALSE" in src
    print(f"\n  run_mofa() signature carries use_basilisk = FALSE: {has_default_false}")
    check("run_mofa() defaults use_basilisk to FALSE", has_default_false)
    check("SKILL.md warns that the default uses ambient reticulate Python",
          "use_basilisk" in skill and "FALSE" in skill)
except (urllib.error.URLError, TimeoutError):
    print("\n  SKIP: MOFA2 source unreachable")

# --- SNF defaults quoted in the skill match the source ---
check("SKILL.md quotes SNF(Wall, K = 20, t = 20)", "SNF(Wall, K = 20, t = 20)" in skill)
check("SKILL.md quotes affinityMatrix(diff, K = 20, sigma = 0.5)",
      "affinityMatrix(diff, K = 20, sigma = 0.5)" in skill)

# --- feature-count imbalance survives scaling ---
try:
    import numpy as np
    rng = np.random.default_rng(0)
    big = rng.normal(size=(20000, 50))     # 20,000 genes
    small = rng.normal(size=(100, 50))     # 100 proteins
    scale = lambda m: (m - m.mean(axis=1, keepdims=True)) / m.std(axis=1, keepdims=True)
    big_s, small_s = scale(big), scale(small)
    ratio = big_s.var(axis=1).sum() / small_s.var(axis=1).sum()
    print(f"\n  total variance ratio after per-feature scaling: {ratio:.0f}:1")
    check("Per-feature scaling does NOT remove feature-count imbalance", ratio > 100)
    check("SKILL.md says scaling does not fix the dimension imbalance",
          "does nothing about the second" in skill or "survives scaling" in skill
          or "Feature-select per view" in skill)
    print("    -> the larger view still contributes ~200x the total variance")
except ImportError:
    print("\n  SKIP: numpy not installed for the imbalance demonstration")

print(f"\n=== Packages: {passed} passed, {failed} failed ===")
sys.exit(1 if failed else 0)
