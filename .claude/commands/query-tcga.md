---
description: Query TCGA/GDC for projects, mutations, or clinical data. Use when the user asks for TCGA cohorts, mutation counts, or clinical variables from the Genomic Data Commons.
argument-hint: [project-id] [gene]
allowed-tools: Read Grep Glob Bash(python3 *) Bash(curl *)
---

Query the GDC for project `$0`, gene `$1`.

Follow the `biomedical-mcp` skill. Call the **GDC REST API** directly (`https://api.gdc.cancer.gov`) rather than wrapping TCGAbiolinks, which is R and calls the same API underneath.

The parts that are usually got wrong:

1. **There is no expression matrix endpoint.** Querying `/files` for expression returns tens of thousands of *file references*; you POST the ids to `/data/{file_id}` and assemble the matrix yourself. A tool promising a matrix from one call cannot deliver.
2. **Clinical fields need `expand=demographic,diagnoses`.** Without it, cases come back near-empty and look like missing data.
3. **`/ssms` is distinct mutations; `/ssm_occurrences` is mutation-in-a-case.** A cohort mutation count is almost always the occurrence count.
4. **Paginate with `from`/`size`**, not page numbers. The response carries `pagination.total`.
5. **Several fields are lists even when they look scalar** — `primary_site` is `['Bronchus and lung']`, not a string.
6. **Record the data release** from `/status`; results change between releases.

Report: the query issued, the pagination total, and the data release the answer came from.

If `$0` is empty, list candidate TCGA projects first.
