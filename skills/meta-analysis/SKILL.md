# Meta-Analysis

Systematic review and meta-analysis for clinical and preclinical evidence. This part covers protocol registration, search strategy construction, deduplication, screening, PRISMA 2020 flow diagrams, data extraction, and risk of bias assessment using the PRISMA2020, synthesisr, and robvis packages.

## When to Use This Skill

Activate when the user requests:
- A systematic review or meta-analysis protocol
- Search strategy construction for PubMed, Embase, or Cochrane CENTRAL
- PRISMA 2020 flow diagram generation
- Deduplication of records across databases
- Title/abstract or full-text screening workflows
- Inter-rater agreement between screeners
- Risk of bias assessment (RoB 2, ROBINS-I, ROBINS-E, QUADAS-2, Newcastle-Ottawa)
- Risk of bias visualization (traffic light or summary plots)
- Data extraction templates for RCTs or observational studies

## Inputs

| Data Type | Format | Source |
|-----------|--------|--------|
| Search results | RIS, BibTeX, NBIB, CSV | PubMed, Embase, CENTRAL, Web of Science |
| Record counts | Integers per PRISMA stage | Search logs, screening software |
| Extracted outcomes | Tabular (study, n, effect, variance) | Full-text data extraction |
| Risk of bias judgements | Tabular (study, domain 1..k, overall) | RoB 2 / ROBINS-I Excel or manual |

---

## Environment

```r
# Core, all actively maintained (versions verified 2026-08)
install.packages(c("metafor", "meta", "PRISMA2020", "robvis", "synthesisr", "irr"))
#   metafor     5.0-1    effect sizes and models
#   meta        8.5-0    alternative interface, GRADE-friendly output
#   PRISMA2020  1.1.4    flow diagrams
#   robvis      0.3.1    risk of bias plots
#   synthesisr  0.4.1    bibliographic import and deduplication
#   irr         0.85     Cohen's and Fleiss' kappa

# Programmatic search
install.packages(c("rentrez", "easyPubMed"))
#   rentrez     1.2.4
#   easyPubMed  3.1.6
```

```
Packages to avoid, and why:

  revtools    0.4.1, last released 2019-12. Superseded by synthesisr, which is
              by the same authors and actively maintained.
  metagear    0.7, last released 2021-02.
  metaviz     0.3.1, last released 2020-04. metafor and meta cover the plots.
  esc         0.5.1, last released 2019-12. Use metafor::escalc().

Not on CRAN, install from source if needed:
  ASySD       deduplication, higher sensitivity than reference-manager dedup
  litsearchr  search term discovery from a naive search
  dmetar      companion package to the Doing Meta-Analysis book
```

---

## Protocol and Registration

Register before screening starts. A protocol written after seeing results is not a protocol.

```
Where to register:
  PROSPERO        health-related reviews with a health outcome. Free.
                  Registration before data extraction begins.
  OSF Registries  anything PROSPERO will not take (preclinical, methods,
                  animal studies, scoping reviews).
  INPLASY         alternative when PROSPERO turnaround is too slow.

What must be pre-specified, because changing it later is a protocol deviation
that has to be reported:
  - PICO elements and the review question
  - Eligibility criteria, including study designs and language limits
  - Databases and the planned search date range
  - Primary and secondary outcomes, defined precisely
  - Effect measure (OR, RR, HR, MD, SMD)
  - Synthesis model (fixed vs random effects) and heterogeneity handling
  - Subgroup and sensitivity analyses, declared in advance
  - Risk of bias tool
```

Report the PROSPERO ID in the manuscript. Reviewers check it, and deviations between the registration and the paper are a common reason for rejection.

## Search Strategy

### Translating PICO into a query

```
PICO -> query blocks, combined with AND across blocks and OR within blocks:

  P (Population)    disease terms, controlled vocabulary + free text
  I (Intervention)  drug/exposure names, including synonyms and brand names
  C (Comparator)    usually omitted from the search; it over-restricts
  O (Outcome)       usually omitted; outcomes are poorly indexed and
                    including them loses relevant records

Standard practice is to search P AND I only, and apply C and O at screening.
Searching all four is the most common cause of a search that misses studies.
```

### Controlled vocabulary and free text

Every block needs both. MeSH alone misses recent records that have not been indexed yet; free text alone misses records where the concept is only in the MeSH.

```
PubMed
  "Carcinoma, Non-Small-Cell Lung"[Mesh] OR nsclc[tiab] OR
  "non small cell lung"[tiab]

  [Mesh]        controlled vocabulary, auto-explodes to narrower terms
  [Mesh:NoExp]  suppress explosion
  [tiab]        title/abstract
  [tw]          text word, broader than tiab
  [pt]          publication type

Embase (Ovid syntax)
  exp Carcinoma, Non-Small Cell Lung/ OR nsclc.ti,ab,kw.

  exp   explode the Emtree term
  /     Emtree term marker
  .ti,ab,kw.  title, abstract, keyword

Cochrane CENTRAL
  [mh "Carcinoma, Non-Small-Cell Lung"] OR nsclc:ti,ab,kw
```

Truncation differs by platform. PubMed uses `*` and requires at least four characters before it; Ovid uses `$` or `*`. PubMed does not support left truncation.

### Validated study design filters

Do not write your own RCT filter. Use a validated one and cite it.

```
Cochrane Highly Sensitive Search Strategy (CHSSS), sensitivity-maximizing
version for PubMed. Published in the Cochrane Handbook, chapter 4.

  (randomized controlled trial[pt] OR controlled clinical trial[pt] OR
   randomized[tiab] OR placebo[tiab] OR clinical trials as topic[mesh:noexp] OR
   randomly[tiab] OR trial[ti]) NOT (animals[mh] NOT humans[mh])

Note the animal exclusion is written as NOT (animals NOT humans), not
NOT animals[mh]. The latter drops human studies that also used animal models.
```

For observational designs there is no equivalent gold standard. Filters exist but lose sensitivity, so most reviews search without a design filter and exclude at screening.

### Programmatic PubMed search

```r
library(rentrez)   # v1.2.4

query <- paste(
  '("Carcinoma, Non-Small-Cell Lung"[Mesh] OR nsclc[tiab])',
  'AND ("Immunotherapy"[Mesh] OR pembrolizumab[tiab] OR nivolumab[tiab])',
  'AND ("2015/01/01"[PDAT] : "2026/12/31"[PDAT])'
)

# use_history keeps results server-side; required above ~10k records
res <- entrez_search(db = "pubmed", term = query, use_history = TRUE, retmax = 0)
res$count

# Fetch in batches. NCBI throttles to 3 requests/second without an API key,
# 10/second with one. Set it via ENTREZ_KEY or set_entrez_key().
recs <- character()
for (start in seq(0, res$count - 1, by = 200)) {
  recs <- c(recs, entrez_fetch(
    db = "pubmed", web_history = res$web_history,
    rettype = "medline", retmode = "text",
    retstart = start, retmax = 200
  ))
  Sys.sleep(0.34)
}
writeLines(recs, "pubmed_records.nbib")
```

The search string, the database, the platform, the date run, and the number of hits must all be recorded per database. PRISMA 2020 requires the full strategy for at least one database in the manuscript or supplement.

## Deduplication

Records overlap heavily across databases. PubMed and Embase alone typically overlap 40-60%.

```r
library(synthesisr)   # v0.4.1

files <- c("pubmed.nbib", "embase.ris", "central.ris")
refs <- read_refs(files, tag_naming = "best_guess", return_df = TRUE)

# Exact match on DOI first: fast and safe
refs <- refs[!duplicated(refs$doi) | is.na(refs$doi), ]

# Then fuzzy match on title for records lacking a DOI
dups <- find_duplicates(
  refs$title,
  method = "string_osa",
  to_lower = TRUE, rm_punctuation = TRUE,
  threshold = 7          # max edit distance; raise to catch more, at the
)                        # cost of false merges
deduped <- extract_unique_references(refs, matches = dups)

nrow(refs) - nrow(deduped)   # duplicates removed, needed for PRISMA
```

```
Deduplication is not a solved problem. Two failure modes, opposite directions:

  Under-merging   the same trial published as a conference abstract and a
                  full paper has different titles and no shared DOI. These
                  are duplicate STUDIES, not duplicate RECORDS, and must be
                  linked at data extraction, not here.

  Over-merging    companion papers reporting different outcomes of one trial
                  have near-identical titles. Merging them loses an outcome.

Always eyeball the merged pairs before accepting. A threshold that removes
"too many" duplicates is worse than one that removes too few, because the
lost records are invisible downstream.
```

Reference-manager deduplication (EndNote, Zotero) has lower sensitivity than dedicated tools. If dedup accuracy matters, ASySD reports sensitivity 0.95-0.99 with specificity above 0.99.

## Screening

### Two reviewers, independently

```
Title/abstract screening
  Two reviewers screen all records independently against the eligibility
  criteria. Liberal inclusion: if either reviewer says maybe, it advances.
  Reconcile disagreements by discussion, with a third reviewer to break ties.

Full-text screening
  Same two-reviewer process. This is the stage where every exclusion needs a
  recorded REASON, because PRISMA 2020 requires reporting them with counts.

Pilot first
  Both reviewers screen the same 50-100 records, compare, and refine the
  criteria before screening the rest. Most criteria ambiguity surfaces here.
```

### Measuring agreement

```r
library(irr)   # v0.85

# screening: data.frame with one column per reviewer, one row per record
kappa2(screening[, c("reviewer_1", "reviewer_2")])       # two reviewers
kappam.fleiss(screening[, c("r1", "r2", "r3")])          # three or more
```

```
Interpreting kappa for screening:
  < 0.40   poor. The criteria are ambiguous. Stop and rewrite them.
  0.40-0.60  moderate. Usually fixable with a calibration round.
  0.60-0.80  substantial. Acceptable.
  > 0.80   almost perfect.

Kappa is deflated when inclusion is rare, which it always is at title/abstract
(typical inclusion 2-5%). A low kappa with high raw agreement is the expected
pattern, not necessarily a problem. Report both.
```

### Screening automation

Active-learning tools rank records by predicted relevance so screening can stop early. They are decision aids, not replacements for a second reviewer.

```
ASReview    open source, active learning. Screens in relevance order and
            plateaus once the recall curve flattens.
Rayyan      web based, free tier, supports blinded two-reviewer workflow.

If you use one, report it: the tool, the model, the stopping rule, and
whether a human screened every record or only until the stopping rule fired.
An unreported stopping rule is a reproducibility gap.
```

## PRISMA 2020 Flow Diagram

PRISMA 2020 replaced the 2009 statement and changed the diagram structure. The current version separates records identified from databases and registers, and distinguishes reports from studies.

```r
library(PRISMA2020)   # v1.1.4

# The package expects a specific set of row names. Start from the template
# shipped with the package rather than building the data frame by hand.
template <- system.file("extdata", "PRISMA.csv", package = "PRISMA2020")
counts <- read.csv(template)

# Key fields, all as integers:
#   database_results, register_results       identification
#   duplicates, excluded_automatic, excluded_other
#   records_screened, records_excluded       screening
#   dbr_sought_reports, dbr_notretrieved_reports
#   dbr_assessed, dbr_excluded               eligibility, with reasons
#   new_studies, new_reports                 included

data <- PRISMA_data(counts)

plot <- PRISMA_flowdiagram(
  data,
  interactive = FALSE,
  previous = FALSE,        # TRUE only for a review update with prior studies
  other = TRUE,            # records found outside database searching
  detail_databases = TRUE, # break identification down per database
  side_boxes = TRUE
)

PRISMA_save(plot, filename = "prisma_flow.pdf", filetype = "PDF", overwrite = TRUE)
```

```
The arithmetic must reconcile, and reviewers check it:

  records_screened = (database_results + register_results)
                     - duplicates - excluded_automatic - excluded_other

  dbr_assessed = dbr_sought_reports - dbr_notretrieved_reports

  new_studies <= dbr_assessed - dbr_excluded

Studies vs reports: one study can produce several reports. The included box
reports both counts, and they are usually different. Conflating them is the
most common PRISMA diagram error.

previous = TRUE is only for review updates. Leaving it at the default on a
new review produces boxes for prior studies that do not exist.
```

## Data Extraction

### Extract in duplicate

Two extractors, independently, into the same template, then reconcile. Single extraction has a documented error rate high enough to change pooled estimates.

### What to capture

```
Study level
  citation, PROSPERO/trial registration ID, country, funding source,
  conflicts of interest, design, follow-up duration

Population
  n randomized, n analysed, age, sex, disease stage, line of therapy,
  key prognostic factors

Intervention and comparator
  agent, dose, schedule, duration, co-interventions

Outcomes, per outcome and per timepoint
  definition as reported, timepoint, n analysed
  binary        events and total, per arm
  continuous    mean, SD, n, per arm
  time-to-event HR with CI, or the numbers needed to derive one

Always record what was NOT reported. "Not reported" and "zero" are different
and are handled differently downstream.
```

### Deriving what is missing

Trials frequently report the wrong summary statistic. Convert rather than dropping the study, and record every conversion.

```
Median and IQR -> mean and SD        Wan et al. 2014, Luo et al. 2018
SE -> SD                            SD = SE * sqrt(n)
95% CI -> SD                        SD = sqrt(n) * (upper - lower) / 3.92
                                    3.92 = 2 * 1.96; use the t quantile if n < 60
p value -> SE                       back-calculate from the test statistic

Every derived value is an assumption. Flag them and test them in a
sensitivity analysis that excludes derived data.
```

## Risk of Bias

### Choosing the tool

```
What design are you assessing?

  Randomized trial
    -> RoB 2. Five domains, signalling questions, per-outcome not per-study.
       Assess each outcome separately; a trial can be low risk for mortality
       and high risk for a subjective outcome.

  Non-randomized study of an INTERVENTION
    -> ROBINS-I (2016). Seven domains, judged against a target trial.
       ROBINS-I V2 was posted 2025-11-20 but is still a DRAFT and is
       "subject to change". Use the 2016 version for work you intend to
       publish, and state which version you used.

  Non-randomized study of an EXPOSURE
    -> ROBINS-E. Same logic as ROBINS-I, adapted for exposures.

  Diagnostic accuracy study
    -> QUADAS-2.

  Prognostic factor study
    -> QUIPS.

  Missing evidence in the synthesis itself
    -> ROB ME.

  Newcastle-Ottawa Scale
    -> Widely used for cohort and case-control studies and often demanded by
       journals, but it produces a numeric score, and Cochrane recommends
       against collapsing risk of bias into a score. If a journal requires
       NOS, report it alongside ROBINS-I rather than instead of it.
```

RoB 2 and ROBINS-I are domain-judgement tools, not checklists. Each domain resolves to Low / Some concerns (or Moderate) / High / Critical via an algorithm from the signalling questions. Do not average domains: the overall judgement is driven by the worst domain.

### Visualization

```r
library(robvis)   # v0.3.1

# One row per study. Columns: Study, D1..Dk, Overall, and optionally Weight.
# Judgement strings must match the tool's expected levels exactly.
rob_traffic_light(data = rob_data, tool = "ROB2", psize = 10)

rob_summary(data = rob_data, tool = "ROB2", overall = TRUE,
            weighted = TRUE)   # weight bars by study weight from the model

# Supported: "ROB2", "ROB2-Cluster", "ROBINS-I", "ROBINS-E",
#            "QUADAS-2", "QUIPS", "Generic"
rob_tools()   # confirms the list for the installed version
```

Use `tool = "Generic"` for anything else, including the Newcastle-Ottawa Scale, which robvis does not model directly.

```
The robvis CRAN package is maintained (0.3.1, June 2026), but riskofbias.info
states they are no longer able to support the robvis web app or the Excel tool
implementations. Use the R package rather than the hosted app.
```

Risk of bias feeds the synthesis. Studies at high risk are not silently dropped: they are either excluded in a pre-specified sensitivity analysis, or retained with the sensitivity analysis reported alongside.

## Output Specification

| Output | Format | Description |
|--------|--------|-------------|
| `search_strategy.txt` | Text | Full query per database, platform, date run, hits |
| `records_raw.ris` | RIS | Combined export before deduplication |
| `records_deduped.csv` | CSV | Unique records with a duplicate-removal count |
| `screening_decisions.csv` | CSV | Per-record decision per reviewer, plus reconciliation |
| `exclusion_reasons.csv` | CSV | Full-text exclusions with a reason per record |
| `prisma_counts.csv` | CSV | Integer counts per PRISMA 2020 stage |
| `prisma_flow.pdf` | PDF | PRISMA 2020 flow diagram |
| `extraction.csv` | CSV | One row per study-outcome-timepoint |
| `rob_assessments.csv` | CSV | Study, per-domain judgements, overall |
| `rob_traffic_light.pdf` | PDF | Per-study per-domain risk of bias |
| `rob_summary.pdf` | PDF | Stacked bar of judgements per domain |

## Validation Checks

```
Search
  Every known-relevant "seed" study is retrieved by the final search.
  Build a seed set of 5-10 papers you already know qualify, and confirm the
  search finds all of them. A search that misses a seed is incomplete.

  Hit counts per database are recorded and sum to the identification box.

Deduplication
  Removed count is plausible: 30-60% overlap across 3+ biomedical databases.
  Under 10% suggests dedup failed. Over 70% suggests over-merging.
  Spot-check 20 merged pairs manually.

Screening
  Kappa reported for both title/abstract and full text.
  Every full-text exclusion has exactly one recorded primary reason.
  Reasons collapse to a small set: PRISMA expects grouped counts, not 40
  distinct one-off reasons.

PRISMA diagram
  records_screened reconciles with identification minus removals.
  dbr_assessed reconciles with sought minus not-retrieved.
  Studies and reports counted separately in the included box.

Risk of bias
  RoB 2 applied per outcome, not once per study.
  Domain levels match the tool's expected strings exactly, or robvis silently
  drops rows.
  Overall judgement equals the worst domain, never an average.
  Two assessors, with disagreements recorded and reconciled.
```

## Common Pitfalls

### Protocol and search
1. **Registering after screening**: PROSPERO registration exists to fix the criteria before the results are visible. Registering late, or amending criteria after seeing which studies qualify, is a deviation that must be declared and undermines the review.
2. **Putting outcomes in the search string**: outcomes are inconsistently reported in titles and abstracts and poorly indexed. Adding an outcome block silently drops eligible studies. Search P AND I, filter for O at screening.
3. **Using MeSH without free-text terms**: records indexed in the last 6-12 months may have no MeSH assigned. A MeSH-only search systematically misses the most recent literature, which is usually the literature that motivated the review.
4. **Writing your own RCT filter**: validated filters exist and are cited. A hand-rolled filter has unknown sensitivity. Use the Cochrane Highly Sensitive Search Strategy and cite it.
5. **`NOT animals[mh]` to exclude animal studies**: this also removes human studies that included animal work. The validated form is `NOT (animals[mh] NOT humans[mh])`.
6. **Searching one database**: PubMed alone misses a substantial fraction of trials, particularly European and conference records. Minimum for a Cochrane-style review is PubMed, Embase, and CENTRAL.

### Screening and extraction
7. **Single-reviewer screening**: doubles the miss rate relative to duplicate screening. If resources force it, use two reviewers for a random 20% and report the agreement on that subset.
8. **Reading kappa without raw agreement**: at 2-5% inclusion rates kappa is deflated by design. A kappa of 0.5 with 97% raw agreement is not the same problem as a kappa of 0.5 with 70% raw agreement.
9. **Not recording exclusion reasons at full text**: PRISMA 2020 requires exclusions with reasons and counts. Reconstructing them afterwards from memory is not possible.
10. **Treating reports as studies**: a trial with a primary paper, a long-term follow-up, and a conference abstract is one study and three reports. Counting it three times inflates the evidence base and double-counts patients in the pooled estimate.
11. **Dropping studies that report medians**: median and IQR convert to mean and SD with published formulae. Dropping them biases the review toward studies with normally distributed outcomes.

### Risk of bias
12. **Assessing RoB 2 once per study**: RoB 2 is per outcome by design. A trial can be low risk for overall survival and high risk for an investigator-assessed response endpoint measured unblinded.
13. **Using ROBINS-I V2 for publication now**: it was posted 2025-11-20 as a draft and the authors state it is subject to change. Use the 2016 version and state which you used.
14. **Averaging domain judgements**: the overall judgement is the worst domain, not a mean. Averaging turns one critical flaw into a moderate score.
15. **Scoring instead of judging with the Newcastle-Ottawa Scale**: a numeric star score implies domains are interchangeable and that a threshold separates good from bad studies. Report domain-level judgements, and pair NOS with ROBINS-I when a journal insists on it.
16. **Excluding high-risk studies without pre-specification**: deciding to drop studies after seeing that they change the result is a post-hoc choice. Pre-specify it as a sensitivity analysis, and report both the full and restricted syntheses.

## Related Skills

- [`survival-analysis`](../survival-analysis/SKILL.md): interpreting the hazard ratios and Kaplan-Meier curves that time-to-event meta-analyses pool
- [`cancer-multiomics`](../cancer-multiomics/SKILL.md): primary analysis of the trials and cohorts a review synthesizes

## Public Datasets for Testing

| Dataset | Source | Use Case |
|---------|--------|----------|
| `dat.bcg` | `metadat` | 13 BCG vaccine trials, the canonical binary-outcome example |
| `dat.normand1999` | `metadat` | 9 trials, continuous outcome, length of stay |
| `dat.colditz1994` | `metadat` | Same BCG trials with alternative coding |
| `dat.hine1989` | `metadat` | 6 trials, risk difference, small counts |
| `data_rob2` | `robvis` | Example RoB 2 assessments in the expected column format |
| `data_robins_i` | `robvis` | ROBINS-I example, seven domains |
| `data_robins_e` | `robvis` | ROBINS-E example |
| `data_quadas` / `data_quips` | `robvis` | QUADAS-2 and QUIPS examples |
| `PRISMA.csv` | `PRISMA2020` | Template flow diagram counts, correct field names |

Load the template with `system.file("extdata", "PRISMA.csv", package = "PRISMA2020")` rather than transcribing the field names, which is where most flow-diagram errors start.
