# Validation Tests

Checks the two package claims that waste an afternoon, against the live registries, plus the preprocessing claim that feature-count imbalance survives scaling.

**Executed 2026-08-30: 11 assertions, 0 failures** (Python 3.13.5). Needs network; skips cleanly without it.

```bash
cd skills/multiomics-integration/tests && python run_all.py
```

## Measured

| Check | Result |
|---|---|
| mixOmics on CRAN | **6.3.2 (2018-06-01)** — Bioconductor has 6.36.0 |
| SNFtool | 2.3.1 (**2021-06-11**) — unmaintained |
| `run_mofa()` signature | carries **`use_basilisk = FALSE`**, read from source |
| variance ratio after per-feature scaling | **200:1** (20,000 genes vs 100 proteins) |

Per-feature scaling does **not** remove feature-count imbalance — the larger view still contributes ~200× the total variance, which is why per-view feature selection is a separate step.

## Note on CRAN access

`crandb.r-pkg.org` returns **HTTP 403** to urllib's default User-Agent (`Python-urllib/3.x`). Any scripted CRAN metadata check needs an explicit `User-Agent` header, or the registry looks like it is down. The suite sets one.

## Requirements

Network. `numpy` for the imbalance demonstration.
