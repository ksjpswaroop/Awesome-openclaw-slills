"""Command-line interface for skill_auditor.

Usage examples::

    # Audit a single skill file
    skill-audit path/to/skill.py

    # Audit multiple skills and output JSON
    skill-audit skills/*.py --format json

    # Audit a JSON skill definition
    skill-audit my_skill.json

    # Show only failures
    skill-audit skills/ --fail-only
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from .analyzer import SkillAnalyzer, AnalysisResult
from .report import Report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skill-audit",
        description=(
            "Awesome OpenClaw Skills — static analysis and safety-scoring tool for LLM agent skills.\n"
            "Scans Python or JSON skill files for data exfiltration, shell injection,\n"
            "undisclosed network access, permission scope issues, and secret leakage."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "paths",
        nargs="+",
        metavar="PATH",
        help="Skill file(s) or directory to audit (.py, .json, or SKILL.md directories).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colour output.",
    )
    parser.add_argument(
        "--fail-only",
        action="store_true",
        help="Only print results for skills that failed.",
    )
    parser.add_argument(
        "--exit-zero",
        action="store_true",
        help="Always exit with code 0 (useful in CI to collect reports without breaking the build).",
    )
    parser.add_argument(
        "--rank",
        action="store_true",
        help="Output ranked table with composite scores and tiers.",
    )
    return parser


def _print_ranked_table(ranked: list, use_color: bool = True) -> None:
    """Print ranked skills as a table."""
    reset = "\033[0m" if use_color else ""
    bold = "\033[1m" if use_color else ""
    lines = [
        f"\n{bold}{'═' * 70}{reset}",
        f"{bold}  Ranked Skills{reset}",
        f"{bold}{'═' * 70}{reset}\n",
        f"  {'Name':<35} {'Grade':<6} {'Safety':<8} {'Composite':<10} {'Tier':<12}",
        f"  {'-' * 35} {'-' * 6} {'-' * 8} {'-' * 10} {'-' * 12}",
    ]
    for r in ranked:
        lines.append(
            f"  {r.name[:34]:<35} {r.grade:<6} {r.safety_score:<8} "
            f"{r.composite_score:<10.1f} {r.tier:<12}"
        )
    lines.append("")
    print("\n".join(lines))


def _collect_from_dir(dir_path: Path, collected: List[Path], seen: set) -> None:
    """Recursively collect skill paths from a directory."""
    skill_md = dir_path / "SKILL.md"
    if skill_md.exists():
        if dir_path not in seen:
            collected.append(dir_path)
            seen.add(dir_path)
        return  # Whole dir is one skill, don't recurse
    for item in sorted(dir_path.iterdir()):
        if item.is_file() and item.suffix in (".py", ".json"):
            if item not in seen:
                collected.append(item)
                seen.add(item)
        elif item.is_dir():
            _collect_from_dir(item, collected, seen)


def _collect_skill_paths(paths: List[str]) -> List[Path]:
    """Collect skill files and SKILL.md directories for audit."""
    collected: List[Path] = []
    seen: set = set()
    for raw in paths:
        p = Path(raw).resolve()
        if p.is_dir():
            _collect_from_dir(p, collected, seen)
        elif p.is_file():
            if p.suffix in (".py", ".json"):
                if p not in seen:
                    collected.append(p)
                    seen.add(p)
            else:
                print(f"[WARNING] Unsupported file type, skipping: {raw}", file=sys.stderr)
        else:
            print(f"[WARNING] Path not found, skipping: {raw}", file=sys.stderr)
    return sorted(collected, key=lambda x: str(x))


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    files = _collect_skill_paths(args.paths)
    if not files:
        print("No skill files found.", file=sys.stderr)
        return 1

    analyzer = SkillAnalyzer()
    results: List[AnalysisResult] = []
    errors: List[str] = []

    for f in files:
        try:
            result = analyzer.analyze_file(f)
            results.append(result)
        except (FileNotFoundError, ValueError, SyntaxError, json.JSONDecodeError, OSError) as exc:
            errors.append(f"  ERROR analysing {f}: {exc}")

    if errors:
        for err in errors:
            print(err, file=sys.stderr)

    if not results:
        return 1

    use_color = not args.no_color and sys.stdout.isatty()

    if args.format == "json":
        output = json.dumps([r.to_dict() for r in results], indent=2)
        print(output)
    elif args.rank:
        try:
            from ranking.engine import rank_skills
            audit_dicts = [r.to_dict() for r in results]
            ranked = rank_skills(audit_dicts)
            _print_ranked_table(ranked, use_color=use_color)
        except ImportError:
            print("Ranking requires the ranking module. Run: pip install -e .", file=sys.stderr)
            to_print = [r for r in results if not args.fail_only or not r.passed]
            for r in to_print:
                print(Report.text(r, use_color=use_color))
            if len(results) > 1:
                print(Report.summary(results, use_color=use_color))
    else:
        to_print = [r for r in results if not args.fail_only or not r.passed]
        for r in to_print:
            print(Report.text(r, use_color=use_color))
        if len(results) > 1:
            print(Report.summary(results, use_color=use_color))

    any_failure = any(not r.passed for r in results)
    if args.exit_zero:
        return 0
    return 1 if any_failure else 0


if __name__ == "__main__":
    sys.exit(main())
