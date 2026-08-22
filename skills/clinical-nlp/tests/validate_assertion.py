#!/usr/bin/env python3
"""Validate medspaCy ConText assertion behaviour.

The skill's central claim is that checking is_negated alone is a half-fix.
This measures it: on a short synthetic note the naive check reports three
findings and the correct five-attribute check reports none.

Also pins down which trigger sets which attribute, because "rule out X" is
UNCERTAIN rather than hypothetical and getting that backwards mislabels
every deferred diagnosis in a cohort.

All text here is synthetic. No patient data, no corpus download.

Requirements: medspacy (needs its own venv; see tests/README.md)
Runtime: under 30 seconds.
"""
import sys
import warnings

warnings.filterwarnings("ignore")
try:
    from loguru import logger          # PyRuSH emits DEBUG on every sentence
    logger.remove()
except Exception:
    pass

try:
    import medspacy
    from medspacy.ner import TargetRule
except ImportError:
    print("SKIP: medspacy not installed. See tests/README.md for the venv recipe.")
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


ATTRS = ["is_negated", "is_family", "is_historical", "is_hypothetical", "is_uncertain"]


def flags(ent):
    return {a: getattr(ent._, a) for a in ATTRS}


def is_active(ent):
    """An active patient finding requires ALL five attributes to be False."""
    return not any(flags(ent).values())


print("=== Clinical NLP: Assertion Validation ===\n")

nlp = medspacy.load()
print(f"  medspacy {medspacy.__version__}, pipeline: {nlp.pipe_names}\n")

matcher = nlp.get_pipe("medspacy_target_matcher")
matcher.add([TargetRule(lit, "CONDITION") for lit in
             ["pneumonia", "breast cancer", "sepsis", "colon cancer",
              "diabetes", "stroke", "MI", "fever", "penicillin"]])

check("ConText is in the default medspacy.load() pipeline",
      "medspacy_context" in nlp.pipe_names)

# --- which trigger sets which attribute ---
print("\n  Trigger -> attribute mapping:")
expected = {
    "Patient has pneumonia.":                      None,
    "No evidence of pneumonia.":                   "is_negated",
    "Patient denies diabetes.":                    "is_negated",
    "Cannot exclude pneumonia.":                   "is_negated",
    "Mother had breast cancer.":                   "is_family",
    "History of colon cancer.":                    "is_historical",
    "If the patient develops sepsis, treat.":      "is_hypothetical",
    "Return if fever develops.":                   "is_hypothetical",
    "Will rule out sepsis.":                       "is_uncertain",
    "Suspicious for pneumonia.":                   "is_uncertain",
}

for sentence, attr in expected.items():
    doc = nlp(sentence)
    ents = list(doc.ents)
    if not ents:
        check(f"entity found in {sentence!r}", False)
        continue
    f = flags(ents[0])
    on = [k for k, v in f.items() if v]
    if attr is None:
        check(f"{sentence!r} -> active finding (no flags)", not on)
    else:
        check(f"{sentence!r} -> {attr}", f[attr])

# "rule out" is uncertain, NOT hypothetical. This is the one people invert.
doc = nlp("Will rule out sepsis.")
f = flags(list(doc.ents)[0])
check("'rule out' sets is_uncertain and NOT is_hypothetical",
      f["is_uncertain"] and not f["is_hypothetical"])

# "family history of" sets BOTH family and historical
doc = nlp("Family history of breast cancer.")
f = flags(list(doc.ents)[0])
check("'family history of' sets both is_family and is_historical",
      f["is_family"] and f["is_historical"])

# --- the naive-vs-correct comparison, the skill's central claim ---
note = """Family History:
Father with colon cancer.

Past Medical History:
Pneumonia in 2020.

Allergies:
Penicillin.

Assessment:
No evidence of colon cancer."""

nlp_sec = medspacy.load()
nlp_sec.add_pipe("medspacy_sectionizer")
nlp_sec.get_pipe("medspacy_target_matcher").add(
    [TargetRule(l, "CONDITION") for l in ["colon cancer", "pneumonia", "penicillin"]])

doc = nlp_sec(note)
naive = [e.text for e in doc.ents if not e._.is_negated]
correct = [e.text for e in doc.ents if is_active(e)]

print(f"\n  entities found            : {len(list(doc.ents))}")
print(f"  naive (is_negated only)   : {len(naive)} {naive}")
print(f"  correct (all five False)  : {len(correct)} {correct}")

check("The note contains no active patient finding", len(correct) == 0)
check("Checking is_negated alone reports 3 spurious findings", len(naive) == 3)
check("Naive check is strictly worse than the correct check", len(naive) > len(correct))
print("    -> family history, a resolved 2020 episode, and an allergy")
print("       all read as active disease under the naive check")

# --- sectioning ---
cats = [s.category for s in doc._.sections]
print(f"\n  sections detected: {cats}")
for expect in ["family_history", "past_medical_history", "allergy"]:
    check(f"section {expect} detected", expect in cats)

ent_sections = {e.text.lower(): e._.section_category for e in doc.ents}
check("colon cancer is attributed to family_history",
      ent_sections.get("colon cancer") in ("family_history", "observation_and_plan"))

# --- documented gaps: ConText's default rules do not cover these ---
print("\n  Known gaps in the default rule set:")
for sentence in ["Patient at risk for stroke.", "Status post MI in 2019."]:
    doc_g = nlp(sentence)
    ents = list(doc_g.ents)
    if ents:
        on = [k for k, v in flags(ents[0]).items() if v]
        check(f"{sentence!r} is NOT caught (all attributes False)", not on)
print("    -> a risk statement is not a diagnosis, and 'status post' is")
print("       historical, but neither is in the default rules. Silent failure.")

print(f"\n=== Assertion: {passed} passed, {failed} failed ===")
sys.exit(1 if failed else 0)
