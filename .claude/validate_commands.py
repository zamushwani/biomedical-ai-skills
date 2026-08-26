#!/usr/bin/env python3
"""Validate the slash commands in .claude/commands/.

Checks the frontmatter against the fields Claude Code actually supports, and
catches the argument-numbering mistake that is easy to make: `$0` is the FIRST
argument and `$1` the second, which is the opposite of the shell convention.
A command written with `$1` for the first argument silently receives the
second one, or nothing at all.

Also confirms every command points at a skill that exists in this repo.

Usage: python3 .claude/validate_commands.py
Requirements: standard library only. No network.
"""
import re
import sys
from pathlib import Path

# Verified against the Claude Code slash-command docs, 2026-08.
KNOWN_FIELDS = {
    "name", "description", "argument-hint", "arguments",
    "disable-model-invocation", "allowed-tools", "model", "context",
}
DESCRIPTION_LIMIT = 1536          # combined description/when_to_use truncation
BANNED = ["comprehensive", "cutting-edge", "state-of-the-art", "leverages",
          "facilitates", "it is important to note", "in this guide"]

root = Path(__file__).resolve().parent.parent
cmd_dir = root / ".claude" / "commands"
skills_dir = root / "skills"

passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        print(f"  PASS: {name}"); passed += 1
    else:
        print(f"  FAIL: {name}"); failed += 1


def parse_frontmatter(text):
    """Return (fields, body). Frontmatter is a --- delimited block at the top."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    block = text[4:end]
    body = text[end + 5:]
    fields = {}
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        fields[k.strip()] = v.strip()
    return fields, body


print("=== Slash command validation ===\n")

files = sorted(cmd_dir.glob("*.md"))
check(f"commands directory has files ({len(files)} found)", len(files) > 0)
if not files:
    sys.exit(1)

# Only PUBLISHED skills count. skills/ also holds unreviewed local drafts
# that are excluded from git, so a command must not point at one of those.
import subprocess
tracked = subprocess.run(["git", "ls-files", "skills/"], cwd=root,
                         capture_output=True, text=True).stdout.splitlines()
available_skills = {line.split("/")[1] for line in tracked
                    if line.endswith("/SKILL.md")}

for f in files:
    text = f.read_text()
    fm, body = parse_frontmatter(text)
    name = f.stem
    ok = True

    if fm is None:
        check(f"/{name}: has YAML frontmatter", False)
        continue

    # only fields Claude Code recognises
    unknown = set(fm) - KNOWN_FIELDS
    if unknown:
        check(f"/{name}: no unknown frontmatter fields (found {unknown})", False)
        ok = False

    # description is what Claude reads to decide relevance
    if "description" not in fm:
        check(f"/{name}: has a description", False); ok = False
    elif len(fm["description"]) > DESCRIPTION_LIMIT:
        check(f"/{name}: description within {DESCRIPTION_LIMIT} chars", False); ok = False

    if "argument-hint" not in fm:
        check(f"/{name}: has an argument-hint", False); ok = False

    # THE numbering trap: $0 is the first argument, $1 the second.
    used = sorted({int(m) for m in re.findall(r"\$(\d)\b", body)})
    if used:
        if 0 not in used:
            check(f"/{name}: uses $0 for the first argument (found {used}, "
                  f"shell-convention mistake)", False)
            ok = False
        # placeholders must be contiguous from 0
        if used != list(range(len(used))):
            check(f"/{name}: argument indices contiguous from 0 (found {used})",
                  False)
            ok = False
        # hint should describe at least as many slots as are used
        hint_slots = len(re.findall(r"\[[^\]]+\]", fm.get("argument-hint", "")))
        if hint_slots < len(used):
            check(f"/{name}: argument-hint describes all {len(used)} arguments "
                  f"(hint has {hint_slots})", False)
            ok = False

    # every command should point at a real skill in this repo
    referenced = re.findall(r"`([a-z-]+)` skill", body)
    for skill in referenced:
        if skill not in available_skills:
            check(f"/{name}: references skill '{skill}' that exists", False)
            ok = False

    if not referenced:
        check(f"/{name}: names the skill it follows", False); ok = False

    low = body.lower()
    hit = [b for b in BANNED if b in low]
    if hit:
        check(f"/{name}: no banned filler ({hit})", False); ok = False

    if ok:
        check(f"/{name}: frontmatter, arguments, and skill reference all valid", True)

# aggregate checks
all_desc = [parse_frontmatter(f.read_text())[0].get("description", "") for f in files]
check("every command has a distinct description",
      len(set(all_desc)) == len(all_desc))

names = [f.stem for f in files]
check("command names are lowercase-hyphenated",
      all(re.fullmatch(r"[a-z][a-z0-9-]*", n) for n in names))

covered = set()
for f in files:
    covered.update(re.findall(r"`([a-z-]+)` skill", f.read_text()))
print(f"\n  skills referenced by commands: {len(covered)} of {len(available_skills)} published")
print(f"    {sorted(covered)}")

print(f"\n=== Commands: {passed} passed, {failed} failed ===")
sys.exit(1 if failed else 0)
