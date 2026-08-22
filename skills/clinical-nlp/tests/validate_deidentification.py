#!/usr/bin/env python3
"""Validate the skill's claim that Presidio is not clinical out of the box.

Presidio handles general PII well. On clinical identifiers it either assigns
the wrong type or misses them, which matters because a de-identification
pipeline that filters on entity type will act on the wrong things.

Every string here is synthetic: names are placeholders, phone numbers use the
555-01xx range reserved for fiction, and no value came from a real record.

Requirements: presidio-analyzer (pulls a spaCy model, ~400 MB)
Runtime: under a minute.
"""
import sys
import warnings

warnings.filterwarnings("ignore")

try:
    from presidio_analyzer import AnalyzerEngine
except ImportError:
    print("SKIP: presidio-analyzer not installed. See tests/README.md.")
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


print("=== Clinical NLP: De-identification Validation ===\n")

try:
    analyzer = AnalyzerEngine()
except Exception as exc:
    print(f"SKIP: analyzer would not start ({type(exc).__name__}: {str(exc)[:80]})")
    sys.exit(0)


def types_in(text):
    return sorted({r.entity_type for r in analyzer.analyze(text=text, language="en")})


# --- general PII: Presidio does this well ---
print("  General PII:")
name_types = types_in("Patient Jane Roe was seen today.")
check("A person name is detected", "PERSON" in name_types)

date_types = types_in("Admitted on 2025-03-14.")
check("A date is detected", "DATE_TIME" in date_types)

phone_full = types_in("Call (415) 555-0142 for results.")
check("A phone number with area code is detected", "PHONE_NUMBER" in phone_full)

# --- clinical identifiers: where it degrades ---
print("\n  Clinical identifiers:")

phone_bare = types_in("Call 555-0142 for results.")
print(f"    bare local number -> {phone_bare}")
check("A bare local phone number is MISSED entirely", phone_bare == [])

mrn_types = types_in("MRN 00123456 admitted to ward 4.")
print(f"    MRN 00123456      -> {mrn_types}")
check("An MRN is not typed as a medical record number",
      not any("MEDICAL" in t or "MRN" in t for t in mrn_types))
check("An MRN is mistyped as a generic US identifier",
      any(t.startswith("US_") for t in mrn_types))

acc_types = types_in("Specimen accession S25-004417 received.")
print(f"    accession S25-... -> {acc_types}")
check("A specimen accession is not typed as a clinical identifier",
      not any("MEDICAL" in t or "ACCESSION" in t for t in acc_types))

# A provider is a PERSON, indistinguishable from the patient by type alone.
prov_types = types_in("Seen by Dr. Alan Poe at the clinic.")
print(f"    provider name     -> {prov_types}")
check("A provider name is typed PERSON, same as a patient",
      "PERSON" in prov_types)
print("    -> type alone cannot separate patient from provider; both are PERSON")

print("\n  Consequence: filtering on entity type will redact the wrong things.")
print("  Add custom recognizers for MRN, accession and provider, and report")
print("  recall per identifier category rather than one overall number.")

# --- Safe Harbor is categorical ---
print("\n  Safe Harbor:")
note = "Patient Jane Roe, MRN 00123456, seen 2025-03-14 by Dr. Alan Poe."
found = types_in(note)
print(f"    combined note -> {found}")
check("Some identifiers are found in the combined note", len(found) > 0)
check("But MRN is still not correctly typed",
      not any("MEDICAL" in t or "MRN" in t for t in found))
print("    -> Safe Harbor removes 18 categories and is categorical: one")
print("       surviving identifier fails it. Automation is a first pass,")
print("       not compliance.")

print(f"\n=== De-identification: {passed} passed, {failed} failed ===")
sys.exit(1 if failed else 0)
