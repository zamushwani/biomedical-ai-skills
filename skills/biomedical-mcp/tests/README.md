# Validation Tests

Integration tests that confirm the documented API contracts still hold against the **live** GDC, GEO/E-utilities, CIViC, OncoKB, and ClinVar services. They exist so the skill's tool code stays correct as those services evolve — if a future API change breaks a documented shape, this suite is where it surfaces.

**Executed 2026-08-25** on Python 3.13.5: **27 assertions, 0 failures** (GDC Data Release 46.0).

No server implementation is under test and no dependency is installed — the suites use `urllib` only and replicate the skill's query logic. Each suite skips cleanly (exit 0) when its API is unreachable, so an offline run reports what it could not check rather than failing.

## Running

```bash
cd skills/biomedical-mcp/tests
python run_all.py              # all three, under 2 minutes
python run_all.py gdc          # one suite
```

Needs network. Nothing is written to disk; the GEO suite downloads one Series Matrix (~14 MB gzipped) in memory for the parse check and keeps nothing.

## What each suite checks

**gdc** (11 assertions). `/status` data release; `primary_site` is a list not a string; the list-aware filter finds TCGA-LUAD; `ssms` returns a `pagination.total`; pagination is `from`/`size`; clinical is empty without `expand` and present with it; expression returns **file references, not a matrix**.

**geo** (8 assertions). E-utilities `gds` search; `esummary` gives accession/GPL/sample count; UID `200002034` → `GSE2034`; the Series Matrix path rule (last three digits → `nnn`); and the array matrix parses to a real probe-indexed value table.

**biomarker** (8 assertions). CIViC `browseVariants`; the two evidence paths **agree for all 12 BRAF variants** (the corrected claim); V600E has PREDICTIVE evidence via its molecular profile; OncoKB is **401 without a token** while `/info` is open; ClinVar returns a germline classification.

## Measured values

| Check | Value |
|---|---|
| GDC data release | Data Release 46.0 (2026-08-10) |
| TCGA-LUAD KRAS distinct mutations | 14 |
| GDC expression files (not a matrix) | 28,315 |
| GSE2034 series matrix | 22,283 probe rows, first probe `1007_s_at` |
| CIViC evidence-path agreement | 12/12 BRAF variants |
| OncoKB without a token | HTTP 401 |
| ClinVar V600E germline classification | "drug response" |

## Why these are integration tests, not unit tests

The skill's value is the accuracy of its API contracts. A mock would only confirm the skill agrees with itself. Hitting the live APIs confirms the contracts against reality — the `expand` requirement, the `from`/`size` pagination, the probe-indexed Series Matrix, the CIViC molecular-profile model, the OncoKB token gate — and catches the day a service changes shape. The cost is that the suite needs network and moves with the data releases; both are stated, and the suite skips rather than failing when offline.
