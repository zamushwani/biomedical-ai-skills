"""Copy bundled SKILL.md files into an agent's skills directory."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from . import __version__

DEFAULT_TARGET = Path(".claude/skills")


def skills_root() -> Path:
    """Locate the skills directory, installed or from a source checkout."""
    here = Path(__file__).resolve().parent

    bundled = here / "skills"
    if bundled.is_dir():
        return bundled

    # src/biomedical_ai_skills/cli.py -> repo root
    checkout = here.parents[1] / "skills"
    if checkout.is_dir():
        return checkout

    sys.exit("Could not find the skills directory. Try reinstalling the package.")


def available_skills(root: Path) -> list[str]:
    return sorted(p.name for p in root.iterdir() if (p / "SKILL.md").is_file())


def summarize(skill_dir: Path, width: int = 66) -> str:
    """First prose line of a SKILL.md, which is its one-line description."""
    try:
        lines = (skill_dir / "SKILL.md").read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    for line in lines[1:]:
        line = line.strip()
        if line and not line.startswith("#"):
            return line if len(line) <= width else line[: width - 1] + "…"
    return ""


def cmd_list(args: argparse.Namespace) -> int:
    root = skills_root()
    names = available_skills(root)
    if not names:
        print("No skills found.")
        return 1
    pad = max(len(n) for n in names)
    for name in names:
        print(f"  {name:{pad}}  {summarize(root / name)}")
    print(f"\n{len(names)} skills. Install one with: biomedical-skills install <name>")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    root = skills_root()
    names = available_skills(root)

    if args.all:
        wanted = names
    elif args.skills:
        unknown = [s for s in args.skills if s not in names]
        if unknown:
            print(f"Unknown skill: {', '.join(unknown)}", file=sys.stderr)
            print(f"Available: {', '.join(names)}", file=sys.stderr)
            return 1
        wanted = args.skills
    else:
        print("Name a skill, or pass --all.", file=sys.stderr)
        print(f"Available: {', '.join(names)}", file=sys.stderr)
        return 1

    target = Path(args.target).expanduser()
    for name in wanted:
        dest_dir = target / name
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / "SKILL.md"
        if dest.exists() and not args.force:
            print(f"  skipped  {name}  (exists, use --force to overwrite)")
            continue
        shutil.copy2(root / name / "SKILL.md", dest)
        print(f"  installed  {name}  ->  {dest}")
    return 0


def cmd_path(args: argparse.Namespace) -> int:
    root = skills_root()
    if args.skill not in available_skills(root):
        print(f"Unknown skill: {args.skill}", file=sys.stderr)
        return 1
    print(root / args.skill / "SKILL.md")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="biomedical-skills",
        description="Copy SKILL.md files into an AI coding agent's skills directory.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command")

    p_list = sub.add_parser("list", help="show available skills")
    p_list.set_defaults(func=cmd_list)

    p_install = sub.add_parser("install", help="copy a skill into your project")
    p_install.add_argument("skills", nargs="*", help="skill names")
    p_install.add_argument("--all", action="store_true", help="install every skill")
    p_install.add_argument(
        "--target",
        default=str(DEFAULT_TARGET),
        help=f"destination directory (default: {DEFAULT_TARGET})",
    )
    p_install.add_argument("--force", action="store_true", help="overwrite existing files")
    p_install.set_defaults(func=cmd_install)

    p_path = sub.add_parser("path", help="print the path to a skill's SKILL.md")
    p_path.add_argument("skill")
    p_path.set_defaults(func=cmd_path)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
