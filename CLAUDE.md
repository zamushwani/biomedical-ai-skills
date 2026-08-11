# Biomedical AI Skills

Validated SKILL.md files for cancer biology and multi-omics research. Published to GitHub and to PyPI as `biomedical-ai-skills`.

This file is binding. Where it conflicts with habit, convenience, or a plausible-looking tutorial, this file wins.

## Layout

```
skills/<name>/SKILL.md      the skill
skills/<name>/README.md     overview, diagram, gotchas table
skills/<name>/tests/        validation against public datasets
src/biomedical_ai_skills/   pip package and CLI
assets/                     images referenced by README, absolute URLs only
```

Not every directory under `skills/` is published. Some are unreviewed local drafts excluded from git. **Run `git ls-files skills/` before claiming a skill exists publicly.**

---

## The five non-negotiables

1. **Verify before you write.** Never write a version number, function signature, argument name, or default value from memory. Check it against the registry and the package source, in this session, before it goes in a file.
2. **Changing a skill means releasing.** A skill edit that is committed but not released leaves `pip install` serving stale content. The release is part of the change, not a follow-up.
3. **Never report success from an intermediate signal.** A green workflow, a 200 response, or a successful commit is not evidence the artifact is correct. Verify the artifact itself.
4. **Never claim a test passes unless you executed it.** If it was not run, say "written but not executed" and say why.
5. **Stage explicit paths.** Never `git add .` or `git add -A`. Loose personal files sit in the repo root.

---

## Verification gates

Each gate is a command. Run it and read the output. Do not proceed on assumption.

### Gate 1 — before writing about any package

```bash
curl -s https://crandb.r-pkg.org/<pkg>        | python3 -m json.tool | head -20   # R
curl -s https://pypi.org/pypi/<pkg>/json      | python3 -m json.tool | head -20   # Python
```

Then read the actual signature from source, not a tutorial:

```bash
curl -s https://raw.githubusercontent.com/<org>/<repo>/master/R/<fn>.R | sed -n '/^<fn> <- function/,/) {/p'
```

Check the changelog whenever a major version has moved. Silent default changes matter more than errors: code that runs and returns different numbers is worse than code that fails.

If you reference a shipped dataset or template file, confirm it exists:

```bash
curl -s https://api.github.com/repos/<org>/<repo>/contents/data
```

State in the skill when a package is stale or abandoned, and name the maintained replacement.

### Gate 2 — before committing

```bash
git config user.name                                   # must be zamushwani
git status --short                                     # nothing unexpected
grep -rnI "/Users/\|/home/[a-z]\|@gmail\|api[_-]\?key\|password" $(git ls-files)
```

Stage by explicit path. Then confirm what is actually staged:

```bash
git diff --cached --name-only
```

### Gate 3 — after any change under `skills/` or to `pyproject.toml`

```bash
rm -rf dist build && python3 -m build
python3 -c "import zipfile,glob; z=zipfile.ZipFile(glob.glob('dist/*.whl')[0]); print(sorted({n.split('/')[2] for n in z.namelist() if n.startswith('biomedical_ai_skills/skills/')}))"
```

The printed list must be exactly the intended skills. No drafts.

### Gate 4 — after any release

A green workflow is not proof. Three independent checks, in order of authority:

```bash
# 1. authoritative file index (NOT the /json endpoint, which caches for minutes)
curl -s https://pypi.org/simple/biomedical-ai-skills/ | grep -o 'biomedical_ai_skills-[0-9.]*'

# 2. real install in a clean venv
python3 -m venv /tmp/vcheck && /tmp/vcheck/bin/pip install --no-cache-dir "biomedical-ai-skills==X.Y.Z"
/tmp/vcheck/bin/biomedical-skills --version && /tmp/vcheck/bin/biomedical-skills list

# 3. content check, not just version
/tmp/vcheck/bin/python -c "from pathlib import Path; import biomedical_ai_skills as b; print(len((Path(b.__file__).parent/'skills'/'<name>'/'SKILL.md').read_text().splitlines()))"
```

Line count must match the repo. A matching version number with stale content is a silent failure.

---

## Known traps

These have all happened. Do not repeat them.

| Trap | What went wrong | Rule |
|---|---|---|
| Stale workflow run | Polled `gh run list --limit 1` seconds after creating a release, read the *previous* run's "success", reported it as done | Match the run on its tag or title, never just "most recent" |
| Cached PyPI JSON | `/pypi/<pkg>/json` reported the old version for minutes after a successful publish | Use `/simple/<pkg>/`, then a real `pip install` |
| Skill edited, never released | Two days of work sat in the repo while `pip install` served the old file | Bump, tag, release in the same session as the edit |
| Draft skills nearly published | A directory-wide package include would have shipped 10 unreviewed drafts to PyPI, where releases cannot be deleted | Enumerate skills one by one, in two places, with a build-time guard |
| Relative links on PyPI | 16 README links 404'd on the project page | All root-README links absolute |
| Mermaid on PyPI | Rendered as raw source; PyPI has no mermaid | Root README uses an image from `assets/` |
| Badge silently dropped | A badge rework removed the skills count without noticing | Re-read the rendered header after editing badges |
| Duplicate day numbers | Two tracker rows shared a number after an insertion | After renumbering, check for duplicates |

---

## Adding or changing a skill

1. Read the existing SKILL.md completely first.
2. Match the established structure: description, `## When to Use This Skill`, `## Inputs`, body sections, `## Output Specification`, `## Validation Checks`, `## Common Pitfalls`, `## Related Skills`, `## Public Datasets for Testing`.
3. Cross-link with relative paths: `[\`name\`](../name/SKILL.md)`.
4. Update the root `README.md` skills table row **and** the `Skills-N` badge.
5. Update `skills/<name>/README.md`.
6. Add a `CHANGELOG.md` entry.
7. Run Gate 3.
8. Release (below). Not optional.

## Publishing a skill to PyPI

A skill must be added in **two** places or the build fails by design:

1. `pyproject.toml` — both `[tool.hatch.build.targets.wheel.force-include]` and `[tool.hatch.build.targets.sdist]`
2. `.github/workflows/publish.yml` — the `expected` set in "Confirm no draft skills were packaged"

The workflow compares wheel contents against `expected` and fails on mismatch. This exists because `skills/` contains unreviewed drafts and **PyPI releases cannot be deleted, only yanked**.

## Releasing

Version lives in **three** files. All must match:

```
pyproject.toml                        version = "X.Y.Z"
src/biomedical_ai_skills/__init__.py  __version__ = "X.Y.Z"
CITATION.cff                          version: X.Y.Z
```

```bash
# move CHANGELOG [Unreleased] entries under a new "## [X.Y.Z] - DATE" heading
# add the compare link at the bottom of CHANGELOG
git commit && git push origin main
git tag -a vX.Y.Z -m "vX.Y.Z: summary" && git push origin vX.Y.Z
gh release create vX.Y.Z --title "..." --notes "..."
```

The GitHub release triggers publishing via Trusted Publishing. **No API token is stored anywhere** — the workflow mints a short-lived OIDC token per run. Never add a PyPI token to repository secrets.

Then run Gate 4. The release is not done until Gate 4 passes.

---

## README constraints

The root `README.md` is the PyPI long description and must render in both places:

- **All links absolute.** Relative links work on GitHub and 404 on PyPI.
- **No mermaid.** Use an image from `assets/` via a `raw.githubusercontent.com` URL.

Skill-level READMEs are GitHub-only and may use mermaid.

## Testing

Every skill should have `tests/` validating it against a public dataset, with a `run_all` entry point and a `README.md` listing expected values and their source.

- Assert measured values, not remembered ones.
- Where a result is seed- or version-dependent, assert a range and state why.
- If a suite was not executed, say so explicitly. Never imply it passed.

## Security

Never commit personal file paths, usernames, institutional names, server addresses, email addresses, credentials, unpublished data, or patient identifiers.

Use generic paths (`/path/to/data/`) and public accessions (`GSE12345`, `TCGA-LUAD`).

Loose image and data files sometimes sit untracked in the repo root. **Never `git add .`.**

## Writing

Write as a domain expert writing to a colleague. Assume the reader knows the biology; explain the tooling.

- Explain *why* a parameter value, not what the parameter is
- Decision trees as plain code fences, not paragraphs
- Comments only where the code is non-obvious
- Pitfalls as: the mistake, the mechanism, the fix

Banned: comprehensive, robust, cutting-edge, state-of-the-art, leverages, facilitates, enables, "it is important to note", "in this guide". No field introductions. No marketing language.

## Definition of done

A day's work is done only when all of these hold:

- [ ] Every version and signature verified this session (Gate 1)
- [ ] Root README table and badge updated
- [ ] Skill README updated
- [ ] CHANGELOG entry added
- [ ] Security scan clean (Gate 2)
- [ ] Build shows exactly the intended skills (Gate 3)
- [ ] Version bumped in all three files, tagged, released
- [ ] Gate 4 passed: content verified from a real `pip install`
- [ ] Anything not done is stated plainly, with the reason
