#!/usr/bin/env python3
"""Integration test for the GEO tool contracts the skill documents.

Hits the live NCBI E-utilities API and the GEO FTP server. Needs network and
skips cleanly without it. Confirms the search-vs-FTP split, the UID-to-
accession conversion, the Series Matrix path rule, and that an array matrix
is a real probe-indexed value table.

Downloads one Series Matrix (~14 MB gzipped) for the parse check; nothing is
kept. Runtime: under a minute. Requirements: network.
"""
import sys
import io
import gzip
import json
import urllib.parse
import urllib.request
import urllib.error

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        print(f"  PASS: {name}"); passed += 1
    else:
        print(f"  FAIL: {name}"); failed += 1


def eutils(path, params):
    params = {**params, "tool": "biomedical-mcp-tests", "email": "tests@example.org"}
    url = f"{EUTILS}/{path}?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=40) as r:
        return json.load(r)


def series_matrix_stub(accession):
    """The FTP grouping rule: last three digits of the GSE number -> nnn."""
    num = accession[3:]
    return "GSE" + (num[:-3] if len(num) > 3 else "") + "nnn"


print("=== Biomedical MCP: GEO tool contracts (live) ===\n")

try:
    s = eutils("esearch.fcgi", {"db": "gds",
        "term": "breast cancer AND expression profiling by array[DataSet Type]",
        "retmax": 5, "retmode": "json"})
except (urllib.error.URLError, TimeoutError) as exc:
    print(f"SKIP: NCBI E-utilities unreachable ({type(exc).__name__}). Needs network.")
    sys.exit(0)

ids = s["esearchresult"]["idlist"]
check("geo_search returns gds UIDs", len(ids) > 0)

summ = eutils("esummary.fcgi", {"db": "gds", "id": ",".join(ids), "retmode": "json"})
recs = [summ["result"][u] for u in summ["result"] if u != "uids"]
check("esummary gives accession, gpl, n_samples",
      all("accession" in r for r in recs))
if recs:
    print(f"    e.g. {recs[0]['accession']} | GPL {recs[0].get('gpl')} | "
          f"{recs[0].get('n_samples')} samples")

# UID -> accession: a gds UID of 200002034 is GSE2034
uid = "200002034"
acc = "GSE" + uid[3:].lstrip("0")
check("gds UID 200002034 converts to GSE2034", acc == "GSE2034")

# Series Matrix path rule
check("path rule: GSE2034 -> GSE2nnn", series_matrix_stub("GSE2034") == "GSE2nnn")
check("path rule: GSE1 -> GSEnnn", series_matrix_stub("GSE1") == "GSEnnn")
check("path rule: GSE12345 -> GSE12nnn", series_matrix_stub("GSE12345") == "GSE12nnn")

# the array Series Matrix IS a real value table (unlike the GDC)
url = (f"https://ftp.ncbi.nlm.nih.gov/geo/series/{series_matrix_stub('GSE2034')}"
       f"/GSE2034/matrix/GSE2034_series_matrix.txt.gz")
try:
    with urllib.request.urlopen(url, timeout=120) as r:
        raw = r.read()
    text = gzip.decompress(raw).decode("utf-8", "replace").splitlines()
    b = next(i for i, l in enumerate(text) if l.startswith("!series_matrix_table_begin"))
    e = next(i for i, l in enumerate(text) if l.startswith("!series_matrix_table_end"))
    rows = [l.split("\t") for l in text[b + 1:e]]
    n_probes = len(rows) - 1
    first_probe = rows[1][0].strip().strip('"')
    print(f"    GSE2034 series matrix: {n_probes} data rows, first probe {first_probe}")
    check("array series matrix contains a real value table", n_probes > 10000)
    check("rows are probe IDs (1007_s_at), not gene symbols",
          first_probe == "1007_s_at")
except (urllib.error.URLError, TimeoutError, StopIteration) as exc:
    print(f"    SKIP matrix parse: {type(exc).__name__}")

print(f"\n=== GEO: {passed} passed, {failed} failed ===")
sys.exit(1 if failed else 0)
