#!/usr/bin/env python3
"""Validate gene vocabulary matching, the other silent failure.

Foundation models carry a fixed gene vocabulary. Genes absent from it are
dropped without an error. scGPT ships a symbol-based vocabulary; Geneformer
requires Ensembl IDs. Passing the wrong identifier type drops the entire panel
and the model still returns embeddings.

Expected runtime: under 1 minute (6 MB download, cached)
Requires: scanpy

Reference for the identifier requirements: scGPT reads gene symbols from a
column of adata.var; Geneformer's tokenizer requires `ensembl_id` in var.
"""

import warnings

warnings.filterwarnings("ignore")

import numpy as np
import scanpy as sc

sc.settings.verbosity = 0

print("=== Gene Vocabulary Matching (PBMC 3k) ===\n")
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
print(f"  genes: {adata.n_vars}")
print(f"  var_names: {list(adata.var_names[:3])}")
print(f"  gene_ids : {list(adata.var['gene_ids'][:3])}\n")

check("var_names are symbols", not str(adata.var_names[0]).startswith("ENSG"))
check("gene_ids are Ensembl", str(adata.var["gene_ids"][0]).startswith("ENSG"))
check("Both identifier types are available", "gene_ids" in adata.var.columns)

# --- Duplicate symbols exist and must be resolved before matching ---
n_dup = int(adata.n_vars - len(set(adata.var_names)))
print(f"  duplicate gene symbols: {n_dup}")
check("Ensembl IDs are unique", len(set(adata.var["gene_ids"])) == adata.n_vars)
if n_dup > 0:
    print("    -> symbols are NOT unique; call var_names_make_unique() first")

adata.var_names_make_unique()
check("var_names unique after make_unique", len(set(adata.var_names)) == adata.n_vars)

# --- A symbol-based vocabulary, as scGPT ships ---
vocab = set(adata.var_names)

sym_rate = float(np.mean([g in vocab for g in adata.var_names]))
ens_rate = float(np.mean([g in vocab for g in adata.var["gene_ids"]]))

print("\n  matching against a SYMBOL vocabulary:")
print(f"    passing symbols : {sym_rate * 100:.1f}% matched")
print(f"    passing Ensembl : {ens_rate * 100:.1f}% matched")

check("Symbols match a symbol vocabulary", sym_rate == 1.0)
check("Ensembl IDs match a symbol vocabulary 0%", ens_rate == 0.0)

survivors = int(ens_rate * adata.n_vars)
print(f"    genes surviving the identifier mistake: {survivors} of {adata.n_vars}")
check("The identifier mistake drops every gene", survivors == 0)
print("    -> the model still runs and returns embeddings for empty input")

# --- Partial overlap, the realistic case ---
# A real vocabulary covers a subset of any given panel. The match rate is the
# number that must be reported, because a low rate invalidates the embedding.
rng = np.random.default_rng(0)
partial = set(rng.choice(sorted(vocab), size=int(0.6 * len(vocab)), replace=False))
partial_rate = float(np.mean([g in partial for g in adata.var_names]))

print(f"\n  partial vocabulary covering 60%: {partial_rate * 100:.1f}% matched")
check("Partial vocabulary yields a partial match rate",
      0.55 < partial_rate < 0.65)

# --- The check every pipeline should make ---
def match_rate(genes, vocabulary):
    """Fraction of genes present in the model vocabulary. Report this always."""
    genes = list(genes)
    return sum(g in vocabulary for g in genes) / max(len(genes), 1)

for name, genes, expected in [
    ("symbols", adata.var_names, 1.0),
    ("ensembl", adata.var["gene_ids"], 0.0),
]:
    r = match_rate(genes, vocab)
    check(f"match_rate() reports {expected:.0%} for {name}", abs(r - expected) < 1e-9)

# A pipeline that does not surface this number cannot distinguish a good run
# from one where the entire panel was silently discarded.
LOW = 0.50
check("A 0% match rate is below any sane threshold", ens_rate < LOW)
check("A full match rate passes the same threshold", sym_rate >= LOW)

print(f"\n=== Vocabulary: {_pass} passed, {_fail} failed ===")
raise SystemExit(1 if _fail else 0)
