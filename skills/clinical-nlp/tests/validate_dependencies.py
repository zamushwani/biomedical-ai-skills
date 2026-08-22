#!/usr/bin/env python3
"""Validate the clinical-NLP dependency constraints the skill documents.

These are claims about the ecosystem, not about a dataset, so they are tested
by resolving real PyPI metadata rather than by installing anything. The
disjointness results below are what force scispaCy into its own environment.

Needs network access to PyPI. Skips cleanly without it.

Requirements: packaging
Runtime: under 30 seconds.
"""
import json
import sys
import urllib.error
import urllib.request

try:
    from packaging.requirements import Requirement
    from packaging.specifiers import SpecifierSet
    from packaging.version import Version
except ImportError:
    print("SKIP: packaging not installed (pip install packaging)")
    sys.exit(0)

passed = failed = 0


def check(name, condition):
    global passed, failed
    if condition:
        print(f"  PASS: {name}")
        passed += 1
    else:
        print(f"  FAIL: {name}")
        failed += 1


def meta(pkg):
    with urllib.request.urlopen(f"https://pypi.org/pypi/{pkg}/json", timeout=30) as r:
        return json.load(r)


def pin_for(pkg_meta, dep, python_version):
    """The specifier pkg places on dep, with environment markers evaluated."""
    specs = []
    for raw in (pkg_meta["info"].get("requires_dist") or []):
        req = Requirement(raw)
        if req.name.lower() != dep:
            continue
        if req.marker is None or req.marker.evaluate(
                {"python_version": python_version, "extra": ""}):
            specs.append(str(req.specifier))
    return SpecifierSet(",".join(s for s in specs if s)) if specs else None


print("=== Clinical NLP: Dependency Validation ===\n")

try:
    M = {p: meta(p) for p in ["scispacy", "medspacy", "negspacy", "spacy"]}
except (urllib.error.URLError, TimeoutError) as exc:
    print(f"SKIP: PyPI unreachable ({type(exc).__name__}). These checks need network.")
    sys.exit(0)

releases = [v for v in M["spacy"]["releases"]
            if v.count(".") == 2 and not any(c.isalpha() for c in v)]

# --- scispaCy's hard constraints ---
sci = M["scispacy"]["info"]
print(f"  scispacy {sci['version']}, requires_python {sci['requires_python']}")

numpy_pin = pin_for(M["scispacy"], "numpy", "3.11")
check("scispacy pins numpy below 2.0",
      numpy_pin is not None and not numpy_pin.contains("2.0.0")
      and numpy_pin.contains("1.26.4"))
check("scispacy excludes python 3.13",
      not SpecifierSet(sci["requires_python"]).contains("3.13"))
check("scispacy still allows python 3.12",
      SpecifierSet(sci["requires_python"]).contains("3.12"))
print("    -> numpy<2.0 is why it needs its own environment; do not downgrade")
print("       numpy in a shared one to make it fit")

# --- the spaCy pin intersections ---
def satisfying(spec):
    return {v for v in releases if spec is not None and spec.contains(v)}


print()
for py, expect_minor in [("3.11", "3.7"), ("3.12", "3.8")]:
    pins = {p: pin_for(M[p], "spacy", py) for p in ["scispacy", "medspacy", "negspacy"]}
    sci_v = satisfying(pins["scispacy"])
    med_v = satisfying(pins["medspacy"])
    neg_v = satisfying(pins["negspacy"])

    both = sorted(sci_v & med_v, key=Version)
    minors = sorted({v.rsplit(".", 1)[0] for v in both})
    print(f"  Python {py}: scispacy{pins['scispacy']} | medspacy{pins['medspacy']}")
    print(f"    scispacy + medspacy -> {len(both)} versions, minors {minors}")

    check(f"py{py}: scispacy+medspacy is satisfiable", len(both) > 0)
    check(f"py{py}: only spaCy {expect_minor}.x satisfies both", minors == [expect_minor])

    overlap = med_v & neg_v
    if py == "3.11":
        check("py3.11: medspacy and negspacy are DISJOINT", len(overlap) == 0)
        print("    -> one needs spacy>=3.8, the other <3.8. Use medspaCy's ConText.")
    else:
        check("py3.12: medspacy and negspacy can coexist", len(overlap) > 0)

# --- the model URL trap ---
print("\n  scispaCy model hosting:")
pkg_version = sci["version"]
model_version = "0.5.4"
base = "https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases"


def head_status(url):
    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except (urllib.error.URLError, TimeoutError):
        return None


bad = head_status(f"{base}/v{pkg_version}/en_core_sci_sm-{pkg_version}.tar.gz")
good = head_status(f"{base}/v{model_version}/en_core_sci_sm-{model_version}.tar.gz")

if bad is None or good is None:
    print("    SKIP: model host unreachable")
else:
    print(f"    package version {pkg_version} -> HTTP {bad}")
    print(f"    model   version {model_version} -> HTTP {good}")
    check("A URL built from the package version 404s", bad == 404)
    check("The published model version resolves", good == 200)
    check("Model version and package version differ", pkg_version != model_version)
    print("    -> model version is not package version; the naive URL fails")

# --- models on PyPI? ---
missing = 0
for name in ["en-core-sci-sm", "scispacy-models"]:
    try:
        meta(name)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            missing += 1
check("scispaCy models are not distributed on PyPI", missing == 2)

print(f"\n=== Dependencies: {passed} passed, {failed} failed ===")
sys.exit(1 if failed else 0)
