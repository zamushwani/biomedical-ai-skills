#!/usr/bin/env python3
"""Validate the RSI arithmetic the skill documents.

No package implements RSI, so the model in the skill is the specification.
These checks confirm the gene list and coefficient count, and demonstrate the
two errors that silently produce a wrong score: ranking within the ten genes
instead of across the transcriptome, and misreading the direction.

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


GENES = ["AR", "JUN", "STAT1", "PRRT2", "RELA", "ABL1", "SUMO1", "CDK1", "HDAC9", "IRF1"]
COEF = np.array([-0.0098009, 0.0128283, 0.0254552, -0.0017589, -0.0038171,
                 0.1070213, -0.0002509, -0.0092431, -0.0204469, -0.0441683])

print("=== Radiotherapy: RSI model validation ===\n")

# --- the model as written in the skill ---
skill = (Path(__file__).resolve().parents[1] / "SKILL.md").read_text()
check("SKILL.md lists all ten RSI genes", all(g in skill for g in GENES))
check("The model has exactly ten coefficients", len(COEF) == 10)
check("Every coefficient appears in SKILL.md",
      all(f"{abs(c):.7f}".rstrip("0") in skill or f"{abs(c)}" in skill for c in COEF))
check("ABL1 carries the largest positive weight",
      GENES[int(np.argmax(COEF))] == "ABL1")
check("IRF1 carries the largest negative weight",
      GENES[int(np.argmin(COEF))] == "IRF1")

# --- the rank-basis error ---
rng = np.random.default_rng(0)
n_genes, n_samples = 20000, 50
expr = rng.lognormal(mean=2, sigma=1.5, size=(n_genes, n_samples))
idx = rng.choice(n_genes, 10, replace=False)

rank_cols = lambda m: np.apply_along_axis(lambda c: c.argsort().argsort() + 1, 0, m)
ranks_full = rank_cols(expr)[idx]        # correct: rank all genes, then subset
ranks_within = rank_cols(expr[idx])      # wrong: rank only among the ten

rsi_full = COEF @ ranks_full
rsi_within = COEF @ ranks_within

print(f"\n  full-transcriptome ranks: range {ranks_full.min()}-{ranks_full.max()}, "
      f"RSI sd {rsi_full.std():.2f}")
print(f"  within-10 ranks         : range {ranks_within.min()}-{ranks_within.max()}, "
      f"RSI sd {rsi_within.std():.4f}")

check("Ranking within the ten genes gives every sample exactly 1..10",
      set(np.unique(ranks_within)) == set(range(1, 11)))
check("Full-transcriptome ranks span far beyond 10",
      ranks_full.max() > 1000)
check("The wrong basis collapses between-sample variance (>100x smaller sd)",
      rsi_full.std() / rsi_within.std() > 100)
print("    -> the wrong version still returns a plausible-looking number")

# --- direction ---
# RSI predicts SF2: a higher score means more cells survive, i.e. resistant.
resistant = COEF @ rank_cols(expr)[idx][:, :10]
check("Direction is documented as higher = more resistant",
      "higher rsi means more radio-resistant" in skill.lower()
      or "HIGHER RSI MEANS MORE RADIO-RESISTANT" in skill)
check("The skill warns against the name's implication",
      "opposite" in skill.lower())

# --- missing gene handling ---
check("SKILL.md requires reporting a missing gene rather than dropping it",
      "no defined behaviour with nine" in skill or "Report absences" in skill)

print(f"\n=== RSI: {passed} passed, {failed} failed ===")
sys.exit(1 if failed else 0)
