#!/usr/bin/env python3
"""Verify the skills stay readable by any agent, not only Claude Code.

The repository claims to work with Claude Code, Codex CLI, Cursor and Gemini
CLI. That claim rests on two things this script checks:

  1. Each platform's entry file exists, and they agree on the skill count.
  2. The SKILL.md files contain no agent-specific syntax. A skill that picks
     up an argument placeholder, a file-include directive or inline shell
     execution still renders as Markdown but stops being portable, and the
     breakage is silent in every tool except the one it was written for.

Run it before claiming cross-platform support.

Usage: python3 tools/check_portability.py
Requirements: standard library. No network.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Entry files, verified against each tool's documentation, 2026-08.
#   AGENTS.md is the cross-tool standard, read natively by Codex CLI, Gemini
#   CLI, Cursor (Agent mode), Copilot, Zed and Windsurf among others.
#   Cursor's Chat and Composer modes read .cursor/rules/*.mdc instead, so both
#   are needed for full Cursor coverage.
ENTRY_FILES = {
    "AGENTS.md": "Codex CLI, Cursor (Agent), Copilot, Zed, Windsurf, and others",
    "CLAUDE.md": "Claude Code",
    "GEMINI.md": "Gemini CLI",
    ".cursor/rules/biomedical-skills.mdc": "Cursor (Chat and Composer)",
}

# Syntax that binds a file to one agent. Each pattern is something that renders
# fine as Markdown but only *means* anything in one tool.
TOOL_SPECIFIC = [
    (r"\$ARGUMENTS", "Claude Code argument placeholder"),
    (r"(?<!\w)\$[0-9](?!\w)", "positional argument placeholder"),
    (r"^\s*!`", "inline shell execution (Claude Code command syntax)"),
    (r"^allowed-tools:", "Claude Code frontmatter"),
    (r"^argument-hint:", "Claude Code frontmatter"),
    (r"^disable-model-invocation:", "Claude Code frontmatter"),
    (r"^globs:", "Cursor rule frontmatter"),
    (r"^alwaysApply:", "Cursor rule frontmatter"),
]

# Cursor .mdc frontmatter fields, verified from the Cursor documentation.
MDC_FIELDS = {"description", "globs", "alwaysApply"}

passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        print(f"  PASS: {name}"); passed += 1
    else:
        print(f"  FAIL: {name}" + (f" — {detail}" if detail else "")); failed += 1


def published_skills():
    out = subprocess.run(["git", "ls-files", "skills/"], cwd=ROOT,
                         capture_output=True, text=True).stdout.splitlines()
    return sorted({p.split("/")[1] for p in out if p.endswith("/SKILL.md")})


print("=== Cross-platform portability ===\n")

skills = published_skills()
print(f"  {len(skills)} published skills\n")

# --- 1. every platform has an entry file ---
print("  Entry files:")
for path, tools in ENTRY_FILES.items():
    p = ROOT / path
    check(f"{path} exists  ({tools})", p.exists())

# --- 2. the entry files agree on the skill count ---
print("\n  Consistency:")
n = str(len(skills))
for path in ["AGENTS.md", "GEMINI.md", ".cursor/rules/biomedical-skills.mdc"]:
    p = ROOT / path
    if not p.exists():
        continue
    text = p.read_text()
    check(f"{path} states the current skill count ({n})",
          re.search(rf"\b{n}\b\s*(SKILL\.md|skills?)", text) is not None,
          "count drifted from the repository")

agents = (ROOT / "AGENTS.md").read_text() if (ROOT / "AGENTS.md").exists() else ""
missing = [s for s in skills if s not in agents]
check("AGENTS.md names every published skill", not missing,
      f"missing: {missing}")

# --- 3. AGENTS.md must be plain Markdown ---
check("AGENTS.md has no YAML frontmatter (the spec forbids it)",
      not agents.startswith("---"))

# --- 4. the Cursor rule frontmatter uses only real fields ---
mdc = ROOT / ".cursor/rules/biomedical-skills.mdc"
if mdc.exists():
    text = mdc.read_text()
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        block = text[4:end] if end != -1 else ""
        fields = {l.split(":", 1)[0].strip() for l in block.splitlines()
                  if ":" in l and not l.startswith(" ")}
        check("Cursor rule frontmatter uses only documented fields",
              fields <= MDC_FIELDS, f"unknown: {fields - MDC_FIELDS}")
        check("Cursor rule declares a description", "description" in fields)
    else:
        check("Cursor rule has frontmatter", False)

# --- 5. no skill carries agent-specific syntax ---
print("\n  Tool-neutrality of the skills:")
offenders = []
for s in skills:
    text = (ROOT / "skills" / s / "SKILL.md").read_text()
    for pattern, label in TOOL_SPECIFIC:
        m = re.search(pattern, text, re.M)
        if m:
            offenders.append((s, label, m.group(0)[:24]))
check(f"No SKILL.md contains agent-specific syntax ({len(skills)} checked)",
      not offenders, "; ".join(f"{s}: {l}" for s, l, _ in offenders[:4]))

# --- 6. cross-links are relative, so they survive being copied ---
absolute = []
for s in skills:
    text = (ROOT / "skills" / s / "SKILL.md").read_text()
    for m in re.finditer(r"\]\((/[^)]+|[A-Za-z]:\\[^)]+)\)", text):
        absolute.append((s, m.group(1)[:40]))
check("No SKILL.md uses an absolute filesystem link", not absolute,
      f"{absolute[:3]}")

# --- 7. the commands the entry files advertise actually exist ---
print("\n  Advertised commands:")
for tool in ["tools/run_benchmarks.py", "tools/check_portability.py"]:
    check(f"{tool} exists", (ROOT / tool).exists())

print(f"\n=== Portability: {passed} passed, {failed} failed ===")
sys.exit(1 if failed else 0)
