#!/usr/bin/env python3
"""Integration test for the biomarker-database contracts the skill documents.

Hits the live CIViC GraphQL API, the OncoKB REST API, and NCBI E-utilities
(ClinVar). Needs network and skips cleanly without it. Confirms the three
access models, the CIViC molecular-profile evidence path, and that ClinVar
returns a germline classification.

Runtime: under a minute. Requirements: network.
"""
import sys
import json
import urllib.parse
import urllib.request
import urllib.error

passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        print(f"  PASS: {name}"); passed += 1
    else:
        print(f"  FAIL: {name}"); failed += 1


def civic(query):
    req = urllib.request.Request("https://civicdb.org/api/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def http_status(url):
    try:
        with urllib.request.urlopen(url, timeout=25):
            return 200
    except urllib.error.HTTPError as e:
        return e.code


print("=== Biomedical MCP: biomarker contracts (live) ===\n")

# --- CIViC: open GraphQL ---
try:
    d = civic('{ browseVariants(featureName: "BRAF", first: 12) '
              '{ nodes { name id evidenceItemCount therapies { name } } } }')
except (urllib.error.URLError, TimeoutError) as exc:
    print(f"SKIP: CIViC unreachable ({type(exc).__name__}). Needs network.")
    sys.exit(0)

nodes = d.get("data", {}).get("browseVariants", {}).get("nodes", [])
check("CIViC browseVariants returns variants with evidenceItemCount",
      len(nodes) > 0 and "evidenceItemCount" in nodes[0])

# the corrected claim: the two evidence paths AGREE for simple variants
agree = 0
for v in nodes:
    a = civic('{ evidenceItems(variantId: %d) { totalCount } }'
              % v["id"])["data"]["evidenceItems"]["totalCount"]
    mp = civic('{ molecularProfiles(variantId: %d) { nodes { evidenceItems { totalCount } } } }'
               % v["id"])["data"]["molecularProfiles"]["nodes"]
    b = sum(m["evidenceItems"]["totalCount"] for m in mp)
    if a == b:
        agree += 1
check("evidenceItems(variantId:) agrees with molecularProfiles for all simple variants",
      agree == len(nodes))
print(f"    evidence paths agreed: {agree}/{len(nodes)} BRAF variants")

# V600E has PREDICTIVE evidence via its molecular profile
d = civic('{ browseVariants(featureName: "BRAF", variantName: "V600E", first: 20) '
          '{ nodes { name id } } }')
v600e = [v for v in d["data"]["browseVariants"]["nodes"] if v["name"] == "V600E"]
check("plain BRAF V600E variant exists in CIViC", len(v600e) > 0)
if v600e:
    mp = civic('{ molecularProfiles(variantId: %d, first: 1) { nodes { evidenceItems(first: 5) '
               '{ nodes { evidenceType significance therapies { name } } } } } }' % v600e[0]["id"])
    ev = mp["data"]["molecularProfiles"]["nodes"][0]["evidenceItems"]["nodes"]
    check("V600E carries PREDICTIVE evidence via its molecular profile",
          any(e["evidenceType"] == "PREDICTIVE" for e in ev))

# --- OncoKB: token-gated ---
oncokb_code = http_status(
    "https://www.oncokb.org/api/v1/annotate/mutations/byProteinChange?"
    + urllib.parse.urlencode({"hugoSymbol": "BRAF", "alteration": "V600E"}))
check("OncoKB data endpoint returns 401 without a token (degrade, not crash)",
      oncokb_code == 401)
info = http_status("https://www.oncokb.org/api/v1/info")
check("OncoKB /info is open without a token", info == 200)

# --- ClinVar: open E-utilities, germline classification ---
base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
try:
    s = json.load(urllib.request.urlopen(base + "/esearch.fcgi?"
        + urllib.parse.urlencode({"db": "clinvar", "term": "BRAF[gene] AND V600E",
                                  "retmode": "json"}), timeout=30))
    ids = s["esearchresult"]["idlist"]
    check("ClinVar esearch returns variation ids", len(ids) > 0)
    if ids:
        d = json.load(urllib.request.urlopen(base + "/esummary.fcgi?"
            + urllib.parse.urlencode({"db": "clinvar", "id": ids[0],
                                      "retmode": "json"}), timeout=30))
        rec = d["result"][ids[0]]
        check("ClinVar esummary carries a germline_classification",
              "germline_classification" in rec)
        gc = rec.get("germline_classification", {})
        print(f"    ClinVar germline classification: {gc.get('description')}")
except (urllib.error.URLError, TimeoutError) as exc:
    print(f"    SKIP ClinVar: {type(exc).__name__}")

print(f"\n=== Biomarker: {passed} passed, {failed} failed ===")
sys.exit(1 if failed else 0)
