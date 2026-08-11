# Biomedical AI Skills

Validated SKILL.md files for cancer biology and multi-omics research, published to GitHub and to PyPI as `biomedical-ai-skills`.

## Layout

```
skills/<name>/SKILL.md      the skill itself
skills/<name>/README.md     short overview, diagram, gotchas table
skills/<name>/tests/        validation against public datasets
src/biomedical_ai_skills/   the pip package and its CLI
assets/                     images referenced by README (absolute URLs only)
```

Not every directory under `skills/` is published. Some are unreviewed local drafts excluded from git. Check `git ls-files` before assuming a skill exists publicly.

## Research before writing

Package APIs change faster than any model's training data. Before writing a version number, a function signature, or a default value:

1. Check the version against the registry: `https://crandb.r-pkg.org/<pkg>` for R, `https://pypi.org/pypi/<pkg>/json` for Python.
2. Read the signature from the package source, not from memory or a tutorial. GitHub `raw.githubusercontent.com/<org>/<repo>/master/R/<fn>.R` is authoritative; the CRAN PDF is generated from it.
3. Check the changelog for breaking changes when a major version has moved.
4. Confirm any dataset or template file you reference actually ships with the package.

Record what you verified. If a package is stale or abandoned, say so in the skill and name the maintained alternative.

Silent behaviour changes matter more than errors. Code that runs and returns different numbers is worse than code that fails.

## Adding or changing a skill

1. Read the existing SKILL.md completely first.
2. Match the established structure: description, `## When to Use This Skill`, `## Inputs`, body sections, `## Output Specification`, `## Validation Checks`, `## Common Pitfalls`, `## Related Skills`, `## Public Datasets for Testing`.
3. Cross-link related skills with relative paths: `[\`name\`](../name/SKILL.md)`.
4. Add or update the row in the root `README.md` skills table, and the `Skills-N` badge.
5. Add an entry to `CHANGELOG.md`.
6. Update `skills/<name>/README.md` so it still describes what the skill covers.

## Publishing a new skill to PyPI

A new skill must be added in **two** places or the build fails:

1. `pyproject.toml` — both `[tool.hatch.build.targets.wheel.force-include]` and `[tool.hatch.build.targets.sdist]`
2. `.github/workflows/publish.yml` — the `expected` set in the "Confirm no draft skills were packaged" step

The workflow compares the wheel's contents against `expected` and fails on any mismatch. This is deliberate: `skills/` contains unreviewed drafts, and PyPI releases cannot be deleted, only yanked.

## Releasing

**Any change to a skill's content requires a release, or the pip package silently serves stale content.** This is the step most often missed.

```bash
# 1. bump the version in all three files
#    pyproject.toml, src/biomedical_ai_skills/__init__.py, CITATION.cff
# 2. move the CHANGELOG [Unreleased] entries under the new version heading
#    and add the compare link at the bottom
# 3. commit and push
git tag -a vX.Y.Z -m "vX.Y.Z: summary"
git push origin vX.Y.Z
gh release create vX.Y.Z --title "..." --notes "..."
```

Creating the GitHub release triggers the publish workflow, which uploads to PyPI via Trusted Publishing. No API token is stored anywhere.

Verify afterwards. The `/pypi/<pkg>/json` endpoint caches aggressively and will report the previous version for a while; `https://pypi.org/simple/<pkg>/` is authoritative, and an actual `pip install` in a clean venv is better still.

## README constraints

The root `README.md` is also the PyPI long description, so it must render in both places:

- **All links absolute.** Relative links work on GitHub and 404 on PyPI.
- **No mermaid.** PyPI has no mermaid support and renders the source as a code block. Use an image from `assets/` via a `raw.githubusercontent.com` URL.

Skill-level READMEs are GitHub-only and may use mermaid freely.

## Testing

Every skill should have `tests/` validating it against a public dataset, with a `run_all` entry point and a `README.md` stating expected values and their source.

Assert measured values, not remembered ones. Where a result is seed- or version-dependent, assert a range and say why. State plainly when a suite has not been executed rather than implying it passed.

## Security

Never commit:
- Personal file paths or usernames
- Institutional names, server addresses, email addresses
- API keys, tokens, or credentials
- Unpublished research data or patient identifiers

Use generic paths (`/path/to/data/`) and public accessions (`GSE12345`, `TCGA-LUAD`).

Loose image and data files sometimes sit untracked in the repo root. **Never use `git add .` or `git add -A`.** Stage explicit paths only.

## Writing

Write as a domain expert writing for a colleague. Assume the reader knows the biology; explain the tooling.

- Explain *why* a parameter value, not what the parameter is
- Decision trees as plain code fences, not paragraphs
- Comments only where the code is non-obvious
- Pitfalls stated as: the mistake, the mechanism, the fix

Do not use: comprehensive, robust, cutting-edge, state-of-the-art, leverages, facilitates, enables, "it is important to note", "in this guide". No field introductions. No marketing language.

## Before every commit

```bash
git config user.name                      # must be zamushwani
grep -rnI "/Users/\|/home/" $(git ls-files)   # no personal paths
git status --short                        # nothing unexpected staged
python3 -m build && python3 -c "import zipfile,glob; print(sorted({n.split('/')[2] for n in zipfile.ZipFile(glob.glob('dist/*.whl')[0]).namelist() if n.startswith('biomedical_ai_skills/skills/')}))"
```

The last command confirms exactly which skills are packaged. Run it whenever `skills/` or `pyproject.toml` changed.
