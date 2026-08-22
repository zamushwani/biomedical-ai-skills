# Validation Tests

Three suites covering the claims most likely to be wrong in practice: which ConText attribute a given phrasing actually sets, whether the documented dependency conflicts are real, and how Presidio behaves on clinical identifiers.

**Executed 2026-08-22** on Python 3.13.5 with medspaCy 1.3.1, spaCy 3.8.15, Presidio 2.2.364: **45 assertions, 0 failures.**

All text in these tests is synthetic. Names are placeholders, phone numbers use the 555-01xx range reserved for fiction, and no value came from a real record. No corpus is downloaded and no credentialed data is touched.

## Environment

scispaCy pins `numpy<2.0` and `python<3.13`, so it will not install alongside a current scientific stack. These tests deliberately avoid it and run on Python 3.13:

```bash
python3.13 -m venv .venv-clinical
./.venv-clinical/bin/pip install medspacy packaging
./.venv-clinical/bin/pip install presidio-analyzer presidio-anonymizer  # optional, ~400 MB
```

Do not downgrade numpy in a shared environment to make scispaCy fit.

## Running

```bash
cd skills/clinical-nlp/tests
python run_all.py                  # all three, under 2 minutes
python run_all.py assertion        # one suite
```

Each suite exits 0 with a `SKIP` line when its dependency is missing, so a partial environment reports what it could not check rather than failing.

## What each suite checks

**assertion** (22 assertions, needs medspaCy). Pins down the trigger-to-attribute mapping, then demonstrates the skill's central claim on a four-entity synthetic note: the naive `is_negated`-only check reports **3** findings while the correct five-attribute check reports **0**. The three spurious ones are a father's colon cancer, a resolved 2020 pneumonia, and a penicillin allergy.

**dependencies** (13 assertions, needs network). Resolves real PyPI metadata to prove the pin conflicts rather than asserting them from memory. Also confirms the model-URL trap by HEAD request.

**deidentification** (10 assertions, needs Presidio). Shows Presidio handling general PII correctly and then degrading on clinical identifiers.

## Measured values

### Assertion mapping

| Phrasing | Attribute set |
|---|---|
| "no evidence of", "denies", "cannot exclude" | `is_negated` |
| "mother had", "sister has" | `is_family` |
| "history of" | `is_historical` |
| "family history of" | **both** `is_family` and `is_historical` |
| "if the patient develops…", "return if…" | `is_hypothetical` |
| "will rule out", "suspicious for", "possible" | `is_uncertain` |

`rule out X` is **uncertain, not hypothetical**. Only an if-construction is hypothetical. This test exists because the skill originally had that mapping backwards.

### Documented gaps

Both of these return **all five attributes False**, so both read as active findings:

```
"Patient at risk for stroke."
"Status post MI in 2019."
```

A risk statement is not a diagnosis and "status post" is by definition historical, but neither phrasing is in medspaCy's default rule set. Nothing errors — the entity simply looks active.

### Dependency resolution

| Python | scispaCy + medspaCy | medspaCy + negspacy |
|---|---|---|
| 3.11 | only spaCy **3.7.x** (7 versions) | **disjoint — no solution** |
| 3.12 | only spaCy **3.8.x** (16 versions) | compatible |

scispaCy 0.6.2: `numpy<2.0`, `requires_python <3.13,>=3.9`.

### Model URL

| URL built from | HTTP |
|---|---|
| package version 0.6.2 | **404** |
| model version 0.5.4 | 200 |

The models are not on PyPI at all (`en-core-sci-sm` and `scispacy-models` both 404).

### Presidio on clinical identifiers

| Input | Detected as |
|---|---|
| `Patient Jane Roe` | `PERSON` ✓ |
| `(415) 555-0142` | `PHONE_NUMBER` ✓ |
| `555-0142` (no area code) | **nothing** |
| `MRN 00123456` | `US_BANK_NUMBER`, `US_DRIVER_LICENSE` |
| `accession S25-004417` | `US_DRIVER_LICENSE` |
| `Dr. Alan Poe` | `PERSON` — same type as the patient |

Filtering on entity type will act on the wrong things. Add custom recognizers for MRN, accession and provider, and report recall per identifier category rather than one overall number.

## Notes

- **No scispaCy suite.** Its `numpy<2.0` pin makes it uninstallable beside a current stack, and the tests that matter most (assertion, sectioning) belong to medspaCy anyway. The dependency suite verifies scispaCy's constraints from metadata instead.
- **The dependency suite needs network** and skips without it. It queries PyPI rather than vendoring metadata so it stays true as the ecosystem moves — if a future release changes a pin, this suite is where you find out.
