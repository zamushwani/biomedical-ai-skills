#!/usr/bin/env python3
"""Validate the signature-scoring claims in the checkpoint-biomarkers skill.

The central claim is that a mean-of-z-scores signature is defined relative to
whatever cohort was present when it was computed, so adding samples silently
changes every earlier score, while a rank-based single-sample score does not.
This measures both.

Synthetic data with a fixed seed. No download, no network.

Requirements: numpy
Runtime: a few seconds.
"""
import sys
from pathlib import Path

try:
    import numpy as np
except ImportError:
    print("SKIP: numpy not installed.")
    sys.exit(0)

passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        print(f"  PASS: {name}"); passed += 1
    else:
        print(f"  FAIL: {name}"); failed += 1


print("=== Checkpoint biomarkers: signature scoring ===\n")

rng = np.random.default_rng(0)
sig = rng.normal(size=(20, 30))          # 20 signature genes x 30 samples


def mean_z(mat):
    z = (mat - mat.mean(axis=1, keepdims=True)) / mat.std(axis=1, keepdims=True)
    return z.mean(axis=0)


def rank_score(mat):                      # single-sample, rank-based
    return np.apply_along_axis(lambda c: (c.argsort().argsort() + 1).mean(), 0, mat)


first20 = sig[:, :20]
extra = rng.normal(loc=1.5, size=(20, 10))   # 10 new samples, shifted
grown = np.hstack([first20, extra])

mz_before, mz_after = mean_z(first20), mean_z(grown)[:20]
rk_before, rk_after = rank_score(first20), rank_score(grown)[:20]

mz_drift = float(np.abs(mz_after - mz_before).max())
rk_drift = float(np.abs(rk_after - rk_before).max())

print(f"  scores for the SAME first 20 samples, after adding 10 more:")
print(f"    mean-of-z  max |change|: {mz_drift:.4f}")
print(f"    rank-based max |change|: {rk_drift:.4f}")

check("Mean-of-z scores change when the cohort grows", mz_drift > 0.01)
check("Rank-based single-sample scores do not change", rk_drift < 1e-12)
check("Rank-based is strictly more stable", rk_drift < mz_drift)
print("    -> recomputing a mean-of-z signature after accrual silently")
print("       rewrites every earlier sample's score")

# --- the CPS/TPS claim is stated, not softened ---
skill = (Path(__file__).resolve().parents[1] / "SKILL.md").read_text()
check("SKILL.md states CPS/TPS cannot be computed from expression",
      "Cannot Be Computed From Expression" in skill)
check("SKILL.md gives the CPS and TPS definitions",
      "TPS =" in skill and "CPS =" in skill)
check("SKILL.md names the non-interchangeable PD-L1 clones",
      all(c in skill for c in ["22C3", "28-8", "SP142", "SP263"]))
check("SKILL.md records the GSVA parameter-object API",
      "ssgseaParam" in skill)
check("SKILL.md keeps assay-derived and expression-derived separate",
      "ASSAY-DERIVED" in skill and "EXPRESSION-DERIVED" in skill)

# --- MSI reporting: a percentage without a denominator is not a result ---
check("SKILL.md requires loci examined alongside MSI percentage",
      "loci examined" in skill or "20% of 15 loci" in skill)

print(f"\n=== Scoring: {passed} passed, {failed} failed ===")
sys.exit(1 if failed else 0)
