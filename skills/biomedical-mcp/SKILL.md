# Biomedical MCP Servers

Building Model Context Protocol servers that give AI agents structured, tested access to biomedical databases. Covers MCP server design, the GDC REST API behind TCGA, tool design for search and retrieval, pagination and caching, and the data-shape traps that make a naive wrapper wrong. Part 1 covers TCGA/GDC; GEO and biomarker databases follow.

## When to Use This Skill

Activate when the user requests:
- An MCP server exposing TCGA, GDC, GEO, or a variant database to an agent
- Programmatic TCGA data access from Python (not R)
- Tools named like `search_cancer_type`, `get_mutations`, `get_clinical`
- Wrapping a bioinformatics REST API for use by Claude, Cursor, or another agent
- Deciding between TCGAbiolinks (R) and the GDC REST API (Python)
- Pagination, caching, or rate-limit handling for a genomics API

## Inputs

| Input | Form | Source |
|-------|------|--------|
| Cancer type / project | `TCGA-LUAD`, primary site | GDC projects endpoint |
| Case or sample filter | GDC filter JSON | built by the tool |
| Gene / variant | symbol, Ensembl ID, genomic change | GDC ssms endpoint |
| Auth token | file, only for controlled-access data | GDC, most data is open |

---

## Environment

Versions verified 2026-08.

```bash
pip install "mcp[cli]"        # 2.0.0 - the official Model Context Protocol SDK
pip install httpx             # HTTP client for the API calls
```

```
mcp 2.0.0 is a MAJOR version and the API changed. The server class is
MCPServer, imported from mcp.server. Tutorials and older code use
`from mcp.server.fastmcp import FastMCP`; that path is from the 1.x line.
Verify against the installed version before copying an example.

  1.x:  from mcp.server.fastmcp import FastMCP ; mcp = FastMCP("name")
  2.0:  from mcp.server import MCPServer        ; mcp = MCPServer("name")

The tool decorator and the type-hints-are-the-schema model are the same in
both, so most tool bodies port unchanged; the import and constructor do not.
```

## MCP Server Design

The point of an MCP tool is that an agent, not a human, reads its name, signature, and docstring and decides when to call it. Design for that reader.

```
Tool naming
  Prefix with the service and lead with a verb: tcga_search_projects,
  tcga_get_mutations. A bare get_data collides with every other server the
  agent has loaded and tells it nothing about scope.

The signature IS the schema
  Type-hinted parameters become the JSON Schema the agent fills in. Annotate
  everything, give defaults where sensible, and use enums (Literal) for
  closed sets. A str where an int belongs makes the agent guess.

The docstring IS the description
  Say what the tool returns and, critically, what it does NOT. "Returns file
  references for expression data, not the expression matrix" saves the agent
  a wasted call and a wrong assumption.

Errors go in the RESULT, not the protocol
  A failed lookup should return a structured error the model can read and
  act on ("no project TCGA-XYZ; did you mean TCGA-LUAD?"), not raise a
  protocol-level exception that the agent sees only as a dead tool.
```

```python
from mcp.server import MCPServer          # mcp 2.0.0
import httpx

mcp = MCPServer("tcga")
GDC = "https://api.gdc.cancer.gov"

@mcp.tool()
def tcga_search_projects(query: str = "", size: int = 20) -> dict:
    """Search TCGA/GDC projects by name or primary site.

    Returns project_id, name, and primary_site for matching projects.
    Use the project_id (e.g. TCGA-LUAD) in the other tools.
    """
    params = {"size": size, "format": "json",
              "fields": "project_id,name,primary_site"}
    r = httpx.get(f"{GDC}/projects", params=params, timeout=30)
    if r.status_code != 200:
        return {"error": f"GDC returned {r.status_code}", "query": query}
    hits = r.json()["data"]["hits"]
    if query:
        q = query.lower()
        # primary_site is a LIST, not a string; flatten before matching
        def blob(h):
            sites = h.get("primary_site") or []
            return (h.get("name", "") + " " + " ".join(sites)).lower()
        hits = [h for h in hits if q in blob(h)]
    return {"projects": hits, "count": len(hits)}
```

## The GDC REST API

TCGA data lives in the NCI Genomic Data Commons. The API is one base URL with a small set of endpoints and a shared filter grammar.

```
Base:  https://api.gdc.cancer.gov
  /projects   cancer projects (TCGA-LUAD, ...)
  /cases      patients/samples, with clinical via expand
  /files      data files (this is where expression lives)
  /ssms       simple somatic mutations
  /ssm_occurrences   mutations joined to the case that carries them

Filters are JSON, passed as a string parameter:
  {"op":"in","content":{"field":"cases.project.project_id",
                        "value":["TCGA-LUAD"]}}
Nest with {"op":"and","content":[ ... ]}.

Pagination is `from` and `size` (offset/limit), NOT page numbers in the
request. The response carries pagination.{total,count,size,from,pages}.
Page by incrementing `from` by `size` until from >= total.
```

```
Confirm the data release. /status returns the current data_release
("Data Release 46.0 - August 2026"). Results change between releases;
record which release a cached answer came from, or a reproduction silently
drifts.
```

### Mutations

```python
@mcp.tool()
def tcga_get_mutations(project_id: str, gene: str = "", size: int = 50) -> dict:
    """Somatic mutations for a TCGA project, optionally filtered to a gene.

    Returns distinct mutation records (genomic change, consequence). For
    per-case counts use ssm_occurrences instead; this counts distinct
    mutations, not occurrences.
    """
    import json
    content = [{"op":"in","content":{"field":"cases.project.project_id",
                                     "value":[project_id]}}]
    if gene:
        content.append({"op":"in",
            "content":{"field":"consequence.transcript.gene.symbol","value":[gene]}})
    params = {"filters": json.dumps({"op":"and","content":content}),
              "size": size, "format": "json"}
    r = httpx.get(f"{GDC}/ssms", params=params, timeout=30)
    d = r.json()["data"]
    return {"mutations": d["hits"], "total": d["pagination"]["total"]}
```

```
ssms vs ssm_occurrences is the distinction people get wrong. /ssms is the
catalogue of distinct mutations; /ssm_occurrences is mutation-in-a-case. A
"mutation count" for a cohort is almost always the occurrence count, not the
distinct-mutation count. Say which the tool returns in its docstring.
```

### Clinical

```python
@mcp.tool()
def tcga_get_clinical(project_id: str, size: int = 100) -> dict:
    """Clinical data (demographics, diagnoses) for a TCGA project's cases."""
    import json
    params = {"filters": json.dumps({"op":"in",
                "content":{"field":"project.project_id","value":[project_id]}}),
              "expand": "demographic,diagnoses", "size": size, "format": "json"}
    r = httpx.get(f"{GDC}/cases", params=params, timeout=30)
    return {"cases": r.json()["data"]["hits"]}
```

```
Clinical fields are NOT on the case by default. Without expand=demographic,
diagnoses you get submitter_id and little else. vital_status, days_to_death
and age live under demographic and diagnoses, so a tool that forgets expand
returns empty clinical and looks like missing data.
```

## The Expression Trap

```
There is no get_expression_matrix. This is the single biggest
misconception when wrapping the GDC.

Expression is not queryable inline. /files with data_type "Gene Expression
Quantification" returns tens of thousands of FILE references (file_id, name,
size), not numbers. To get values you POST the file_ids to /data/{id} and
download tab-separated files, one per sample, then assemble the matrix
yourself.

A get_expression tool should therefore be named and documented as what it
is: it returns file references to download, and a second step fetches and
parses them. Promising a matrix from one call is a design that cannot work,
and the agent will build on the false promise.

  tcga_find_expression_files(project_id) -> [{file_id, sample, ...}]
  tcga_download_file(file_id)            -> bytes  (POST /data/{file_id})
```

## TCGAbiolinks or the REST API

```
The plan says "wrap TCGAbiolinks". TCGAbiolinks is an R/Bioconductor
package. An MCP server in Python cannot import it without an R bridge
(rpy2) or shelling out to Rscript, both of which add a heavy, fragile
dependency and an R installation to your server.

  Wrapping TCGAbiolinks (R)    faithful to a known workflow; needs R + the
                               package installed; slow to start; hard to
                               deploy as a standalone server.
  GDC REST API (Python)        no R, pure httpx, deploys anywhere, and it is
                               what TCGAbiolinks itself calls underneath.

For a Python MCP server, call the GDC REST API directly. Reserve the R
route for reproducing a specific TCGAbiolinks analysis a user already has.
```

## Caching and Rate Limits

```
GDC is public and unauthenticated for open data, but it is a shared
resource. Cache aggressively and stamp the data release:

  - project and case metadata change only between data releases; cache them
    keyed on the release version from /status.
  - back off on 429 and 5xx with retries; do not hammer.
  - never cache controlled-access responses to disk in a shared location.

mcp 2.0.0 exposes a CacheHint (mcp.server.CacheHint) for annotating
cacheable results. Use it rather than a hand-rolled global dict that never
invalidates.
```

## Running the Server

```bash
mcp dev server.py                                  # inspect interactively
mcp run server.py --transport streamable-http      # deploy over HTTP
```

```
Register the server with an agent by pointing its MCP config at the command
(stdio) or the URL (Streamable HTTP). stdio launches the server as a
subprocess; HTTP is what you deploy. Do not expose an HTTP MCP server that
proxies controlled-access data without auth in front of it.
```

## Output Specification

| Output | Format | Description |
|--------|--------|-------------|
| `server.py` | Python | the MCPServer with its tools |
| tool results | JSON dict | data plus pagination metadata (total, count, from) |
| error results | JSON dict | `{"error": ...}` in the result, not a raised exception |
| `mcp_config` | JSON | the agent-side registration (command or URL) |

Every list-returning tool returns the pagination `total` beside the page, so the agent knows whether more data exists.

## Validation Checks

```
API contract
  /status read and the data release recorded.
  Filters are valid JSON; pagination uses from/size, not page numbers.
  Clinical tools pass expand=demographic,diagnoses.
  Expression tools return file references, documented as such.

Tool design
  Names are service-prefixed and verb-led.
  Parameters are type-hinted; closed sets use Literal/enum.
  Docstrings state what is returned AND what is not.
  Errors are returned in the result object, not raised.

Robustness
  Non-200 responses handled, not assumed away.
  Retries/back-off on 429 and 5xx.
  Metadata cached keyed on the data release.
```

## Common Pitfalls

### API semantics
1. **Expecting an expression matrix from a query**: the GDC returns file references, not values. Expression is downloaded per-sample from `/data/{file_id}` and assembled locally. A `get_expression` tool that promises a matrix cannot deliver one.
2. **Omitting `expand` on clinical calls**: `vital_status`, `days_to_death` and age live under `demographic` and `diagnoses`. Without `expand`, clinical tools return near-empty cases that look like missing data.
3. **Confusing `ssms` with `ssm_occurrences`**: `/ssms` is distinct mutations; `/ssm_occurrences` is mutation-in-a-case. A cohort mutation count is almost always the occurrence count. State which the tool returns.
4. **Paginating with page numbers**: the GDC uses `from`/`size` offsets. Increment `from` by `size` until `from >= total`; the response carries the total.
5. **Not recording the data release**: results change between releases. `/status` gives the version; cache and cite it or reproductions drift.
6. **Assuming scalar fields**: several GDC fields are lists even when they look singular — `primary_site` on a project is `['Bronchus and lung']`, not a string. Concatenating it as text throws. Check the type before treating a field as scalar.

### MCP design
7. **Unprefixed, noun-only tool names**: `get_data` collides across servers and tells the agent nothing. Prefix with the service and lead with a verb.
8. **Raising exceptions instead of returning errors**: a protocol-level error is invisible to the model as anything but a dead tool. Return a structured error it can read and recover from.
9. **Skipping type hints**: the signature is the JSON Schema. An untyped parameter makes the agent guess the type and the format.
10. **Returning a page with no total**: without `pagination.total` the agent cannot tell whether it has seen everything. Always return the metadata.

### Architecture
11. **Wrapping TCGAbiolinks from Python**: it is R, so this needs rpy2 or an Rscript subprocess plus an R install. Call the GDC REST API directly, which is what TCGAbiolinks calls anyway.
12. **A global dict as a cache**: it never invalidates and grows unbounded. Key cache entries on the data release, and use the SDK's `CacheHint`.
13. **Proxying controlled-access data over unauthenticated HTTP**: open data is fine; controlled data behind an open MCP HTTP endpoint is a disclosure. Put auth in front, and do not cache it to shared disk.

## Related Skills

- [`cancer-multiomics`](../cancer-multiomics/SKILL.md): the TCGA analysis these tools feed
- [`variant-annotation`](../variant-annotation/SKILL.md): interpreting the mutations the mutation tool returns
- [`survival-analysis`](../survival-analysis/SKILL.md): consumes the clinical data the clinical tool returns

## Public Datasets for Testing

| Resource | Content | Access |
|----------|---------|--------|
| GDC API `/status` | Current data release | open, no auth |
| GDC projects | ~80 projects including 33 TCGA | open |
| GDC `/ssms` | ~3.6M somatic mutations | open |
| TCGA-LUAD | Lung adenocarcinoma, a small worked cohort | open |
