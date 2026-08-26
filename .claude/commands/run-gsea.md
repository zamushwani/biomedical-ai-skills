---
description: Pathway enrichment on a ranked gene list (GSEA or ORA). Use when the user asks which pathways are enriched, wants GSEA/fgsea, or has DE results to interpret biologically.
argument-hint: [de-results-file] [gene-set-collection]
allowed-tools: Read Grep Glob Bash(Rscript *)
---

Run pathway enrichment on `$0` against the `$1` collection (default: MSigDB Hallmark).

Follow the `cancer-multiomics` skill. Decide the method first:

```
ranked list, all genes    -> GSEA (fgsea). Uses the whole ranking.
a cut list of DEGs        -> ORA (enrichGO/enrichKEGG). Needs a background.
```

The parts that are usually got wrong:

1. **Rank by the test statistic or shrunk LFC, not by p-value.** A p-value is unsigned, so ranking by it puts strong up- and down-regulated genes at the same end.
2. **ORA needs an explicit universe** — the genes you actually tested, not every gene in the genome. The wrong background inflates every p-value.
3. **Do not mix ID types.** Convert once, and report how many genes failed to map rather than letting them vanish silently.
4. **Report the FDR and the leading-edge genes**, not just pathway names.

If `$0` is empty, ask for the DE result file first.
