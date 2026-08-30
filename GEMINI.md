# GEMINI.md

Gemini CLI looks for a file with this name. The instructions for this repository live in **[AGENTS.md](AGENTS.md)**, which is the cross-tool standard and the single source of truth; this file exists so Gemini CLI finds them.

## Short version

This repository holds **16 SKILL.md protocol files** for cancer bioinformatics under `skills/`. Read the relevant `skills/<name>/SKILL.md` before writing analysis code in that domain — each states when it applies in its own `## When to Use This Skill` section.

Before changing anything here, read `AGENTS.md` and `CLAUDE.md`. The non-negotiables:

1. Verify every version, signature and default against the registry and package source. Never from memory.
2. A skill edit must be released in the same session, or `pip install` serves stale content.
3. A green CI run is not proof. Verify the published artifact.
4. Never claim a test passes unless it was executed.
5. Stage explicit paths. Never `git add .` — untracked personal files sit in the repository root.

## Commands

```bash
python3 tools/run_benchmarks.py        # every skill's validation suite
python3 tools/check_portability.py     # verify the skills stay tool-neutral
```
