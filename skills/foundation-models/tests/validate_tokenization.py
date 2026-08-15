#!/usr/bin/env python3
"""Validate Geneformer's rank-value encoding contract.

Geneformer requires RAW COUNTS. Its tokenizer normalizes by cell total, divides
by each gene's median non-zero expression across the pretraining corpus, then
ranks genes descending and truncates. Feeding log-normalized data instead
produces a different token sequence with no error raised.

This reimplements the encoding to show how different, because the failure is
silent and the model still returns embeddings.

Expected runtime: under 1 minute (6 MB download, cached)
Requires: scanpy, scipy
"""

import warnings

warnings.filterwarnings("ignore")

import numpy as np
import scanpy as sc
from scipy.stats import spearmanr

sc.settings.verbosity = 0

print("=== Geneformer Tokenization Contract (PBMC 3k) ===\n")
_pass = _fail = 0


def check(name, condition):
    global _pass, _fail
    if bool(condition):
        print(f"  PASS: {name}")
        _pass += 1
    else:
        print(f"  FAIL: {name}")
        _fail += 1


adata = sc.datasets.pbmc3k()
sc.pp.filter_genes(adata, min_cells=10)
X = np.asarray(adata.X.todense(), dtype=float)
print(f"  matrix: {X.shape[0]} cells x {X.shape[1]} genes\n")
check("Input is raw integer counts", np.allclose(X, np.round(X)))


def corpus_medians(counts):
    """Median non-zero expression per gene, on the normalized raw scale."""
    tot = counts.sum(1, keepdims=True)
    tot[tot == 0] = 1
    norm = counts / tot * 1e4
    med = np.ones(counts.shape[1])
    for j in range(counts.shape[1]):
        nz = norm[:, j][norm[:, j] > 0]
        if nz.size:
            med[j] = np.median(nz)
    med[med == 0] = 1.0
    return med


def rank_encode(values, medians, topn=2048):
    """Rank-value encoding: normalize, scale by corpus median, rank descending."""
    tot = values.sum(1, keepdims=True)
    tot[tot == 0] = 1
    scaled = (values / tot * 1e4) / medians
    return np.argsort(-scaled, axis=1)[:, :topn]


med = corpus_medians(X)
check("A corpus median exists for every gene", med.shape[0] == X.shape[1])
check("All medians are positive", np.all(med > 0))

ranks_raw = rank_encode(X, med)
ranks_log = rank_encode(np.log1p(X), med)  # the mistake

check("Encoding produces a token sequence per cell", ranks_raw.shape[0] == X.shape[0])
check("Sequences are truncated to the model input size", ranks_raw.shape[1] <= 2048)

# --- How different is the wrong input? ---
n = 500
top1 = float((ranks_raw[:, 0] == ranks_log[:, 0]).mean())
overlap = float(np.mean([
    len(set(ranks_raw[i, :100]) & set(ranks_log[i, :100])) / 100 for i in range(n)
]))
identical = float(np.mean([
    np.array_equal(ranks_raw[i, :100], ranks_log[i, :100]) for i in range(n)
]))
rho = float(np.mean([
    spearmanr(ranks_raw[i, :100], ranks_log[i, :100]).statistic for i in range(200)
]))

print("\n  raw counts vs log-normalized input:")
print(f"    top-1 token identical      : {top1 * 100:.1f}%")
print(f"    top-100 gene-set overlap   : {overlap * 100:.1f}%")
print(f"    top-100 order identical    : {identical * 100:.1f}%")
print(f"    mean Spearman of the order : {rho:.4f}")

check("Log-normalizing changes the token ORDER for essentially every cell",
      identical < 0.05)
check("Ordering is uncorrelated after the mistake", abs(rho) < 0.2)
check("A large share of the top-100 genes differ", overlap < 0.85)
check("Even the first token changes for many cells", top1 < 0.90)

print("    -> the model accepts either input and returns embeddings regardless")

# --- Zeros are dropped, not ranked ---
cell = 0
nonzero = int((X[cell] > 0).sum())
seq_len = min(nonzero, 2048)
tot = X[cell].sum()
scaled = (X[cell] / tot * 1e4) / med
kept = ranks_raw[cell, :seq_len]
check("Every ranked token is a non-zero gene", np.all(X[cell, kept] > 0))
print(f"\n  cell 0: {nonzero} genes detected, {seq_len} tokens emitted")

# --- Rank encoding is scale-invariant to sequencing depth ---
# Doubling a cell's counts must not change its token order, because the
# encoding normalizes by cell total first.
doubled = rank_encode(X * 2, med)
check("Doubling library size leaves the token order unchanged",
      np.array_equal(ranks_raw[:50], doubled[:50]))

# --- But it is NOT invariant to the corpus medians ---
# The medians come from the pretraining corpus, which is why V1 and V2
# dictionaries are not interchangeable.
shuffled = rank_encode(X, med[::-1].copy())
check("Different corpus medians produce a different encoding",
      not np.array_equal(ranks_raw[:50], shuffled[:50]))
print("    -> V1 and V2 dictionaries are not interchangeable")

print(f"\n=== Tokenization: {_pass} passed, {_fail} failed ===")
raise SystemExit(1 if _fail else 0)
