#!/usr/bin/env python3
"""Integration test for the GDC tool contracts the skill documents.

These are the API-shape claims a TCGA MCP server depends on. They hit the
LIVE GDC REST API, so they need network and skip cleanly without it. Uses
only urllib, matching the skill's httpx logic without the dependency.

The point is not to test a server implementation but to confirm the
documented contracts still hold against the live API, so the skill's tool
code stays correct as the GDC evolves.

Runtime: a few seconds. Requirements: network.
"""
import sys
import json
import urllib.parse
import urllib.request
import urllib.error

GDC = "https://api.gdc.cancer.gov"
passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        print(f"  PASS: {name}"); passed += 1
    else:
        print(f"  FAIL: {name}"); failed += 1


def get(path, params):
    url = f"{GDC}/{path}?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


print("=== Biomedical MCP: GDC tool contracts (live) ===\n")

try:
    status = get("status", {})
except (urllib.error.URLError, TimeoutError) as exc:
    print(f"SKIP: GDC API unreachable ({type(exc).__name__}). Needs network.")
    sys.exit(0)

# /status carries the data release the skill says to record
check("/status reports a data release", "data_release" in status)
print(f"    data release: {status.get('data_release')}")

# search_projects: primary_site is a LIST (the bug the skill documents)
proj = get("projects", {"size": 20, "format": "json",
                        "fields": "project_id,name,primary_site"})
hits = proj["data"]["hits"]
check("projects return project_id", all("project_id" in h for h in hits))
sites = [h.get("primary_site") for h in hits if h.get("primary_site") is not None]
check("primary_site is a list, not a string (the documented trap)",
      sites and all(isinstance(s, list) for s in sites))

# the list-aware filter from the skill
def blob(h):
    return (h.get("name", "") + " " + " ".join(h.get("primary_site") or [])).lower()
lung = [h for h in hits if "lung" in blob(h)]
check("list-aware 'lung' filter finds TCGA-LUAD",
      any(h["project_id"] == "TCGA-LUAD" for h in lung))

# get_mutations: ssms filtered by project + gene, with a total
content = [{"op": "in", "content": {"field": "cases.project.project_id", "value": ["TCGA-LUAD"]}},
           {"op": "in", "content": {"field": "consequence.transcript.gene.symbol", "value": ["KRAS"]}}]
ssms = get("ssms", {"filters": json.dumps({"op": "and", "content": content}),
                    "size": 5, "format": "json"})
total = ssms["data"]["pagination"]["total"]
check("ssms query returns a pagination.total", isinstance(total, int))
check("TCGA-LUAD has KRAS mutations catalogued", total > 0)
print(f"    KRAS distinct mutations in TCGA-LUAD: {total}")

# pagination uses from/size, not page numbers
check("pagination carries from/size/total, not page numbers",
      set(("from", "size", "total")) <= set(ssms["data"]["pagination"].keys()))

# get_clinical: expand is required for demographic
plain = get("cases", {"filters": json.dumps({"op": "in",
              "content": {"field": "project.project_id", "value": ["TCGA-LUAD"]}}),
            "size": 3, "format": "json"})
expanded = get("cases", {"filters": json.dumps({"op": "in",
                "content": {"field": "project.project_id", "value": ["TCGA-LUAD"]}}),
               "expand": "demographic,diagnoses", "size": 3, "format": "json"})
plain_has = any("demographic" in c for c in plain["data"]["hits"])
exp_has = any("demographic" in c for c in expanded["data"]["hits"])
check("clinical needs expand: absent without it", not plain_has)
check("clinical present with expand=demographic,diagnoses", exp_has)

# the expression trap: query returns FILE references, not a matrix
expr = get("files", {"filters": json.dumps({"op": "in",
             "content": {"field": "data_type", "value": ["Gene Expression Quantification"]}}),
           "size": 1, "format": "json"})
etotal = expr["data"]["pagination"]["total"]
fhit = expr["data"]["hits"][0]
check("expression query returns file references (file_name), not values",
      "file_name" in fhit)
check("many expression files exist (a matrix would be one object)", etotal > 1000)
print(f"    expression files (not an inline matrix): {etotal}")

print(f"\n=== GDC: {passed} passed, {failed} failed ===")
sys.exit(1 if failed else 0)
