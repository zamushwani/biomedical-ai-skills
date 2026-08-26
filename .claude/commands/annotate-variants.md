---
description: Annotate and clinically interpret variants from a VCF. Use when the user has variant calls and wants functional annotation, ACMG classification, oncogenicity, or clinical tiers.
argument-hint: [vcf-file] [tumour-type]
allowed-tools: Read Grep Glob Bash(bcftools *)
---

Annotate the variants in `$0` for tumour type `$1`.

Follow the `variant-annotation` skill. Order matters:

1. **Normalize first**: `bcftools norm -m -any -f <ref>`. Un-normalized records fail knowledgebase lookups silently — the variant reads as absent, not as an error.
2. **Then annotate** (VEP/SnpEff), picking the transcript-selection rule deliberately and stating it.
3. **Then classify on the right axis.** These are three separate frameworks:

```
ACMG/AMP 2015          germline pathogenicity      germline only
ClinGen/CGC/VICC 2022  somatic oncogenicity        is it driving?
AMP/ASCO/CAP 2017      clinical tiers              does it change management?
```

Oncogenicity and actionability are different axes: KRAS G12D is unambiguously oncogenic and can still be Tier III where nothing acts on it.

4. **A tier requires a tumour type.** BRAF V600E is Tier IA in melanoma and Tier IIC in colorectal. If `$1` is empty, ask for it — do not assign tiers without it.
5. **Use popmax, not global, allele frequency.** 0.1% globally can be 4% in one ancestry group.

Report per variant: gene, HGVS, consequence, population AF (popmax), classification with the criteria applied, and the evidence source.
