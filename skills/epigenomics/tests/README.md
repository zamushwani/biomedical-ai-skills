# Validation Tests

The DiffBind 3.x changes are the reason this skill exists, so the suite checks them against the package's **own NEWS file** rather than restating them — if a future release changes the story, this is where it surfaces.

**Executed 2026-08-30: 16 assertions, 0 failures** (Python 3.13.5). Needs network; skips cleanly without it.

```bash
cd skills/epigenomics/tests && python run_all.py
```

## What it confirms against live sources

| Source | Claim |
|---|---|
| DiffBind NEWS | `dba.count()` centres on summits by default (401 bp) |
| DiffBind NEWS | modelling default changed — `design=FALSE` to revert |
| DiffBind NEWS | normalization moved to `dba.normalize()` |
| DiffBind NEWS | the `bSubControl` preservation bug (fixed 3.22.2) |
| DiffBind NEWS | `dba.plotProfile()` disabled, `profileplyr` uninstallable |
| PyPI | MACS3 **3.0.4 (2026-02)** vs MACS2 **2.2.9.1 (2023-07)** |
| Bioconductor | JASPAR2024 exists (HTTP 200); **JASPAR2026 does not** (404) |

Each claim is checked twice: once against the upstream source, and once that `SKILL.md` still records it. A skill that drifts from its source fails here.

## Requirements

Network only — standard library otherwise.
