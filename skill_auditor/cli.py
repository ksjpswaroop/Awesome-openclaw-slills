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
        help="Skill file(s) or directory to audit (.py or .json).",
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
    return parser


def _collect_files(paths: List[str]) -> List[Path]:
    collected: List[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            for ext in ("*.py", "*.json"):
                collected.extend(sorted(p.rglob(ext)))
        elif p.is_file():
            collected.append(p)
        else:
            print(f"[WARNING] Path not found, skipping: {raw}", file=sys.stderr)
    return collected


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    files = _collect_files(args.paths)
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
