"""Report generation — plain-text and JSON output for analysis results."""

from __future__ import annotations

import json
from typing import List, Union

from .analyzer import AnalysisResult
from .checks.base import Severity

# ANSI colours (disabled when output is not a terminal)
_COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "orange": "\033[33m",
    "red": "\033[91m",
    "cyan": "\033[96m",
    "grey": "\033[90m",
}

_SEV_COLORS = {
    Severity.LOW: _COLORS["grey"],
    Severity.MEDIUM: _COLORS["yellow"],
    Severity.HIGH: _COLORS["orange"],
    Severity.CRITICAL: _COLORS["red"],
}

_GRADE_COLORS = {
    "A": _COLORS["green"],
    "B": _COLORS["green"],
    "C": _COLORS["yellow"],
    "D": _COLORS["orange"],
    "F": _COLORS["red"],
}


def _c(color_key: str, text: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{_COLORS.get(color_key, '')}{text}{_COLORS['reset']}"


class Report:
    """Renders ``AnalysisResult`` objects as human-readable or machine-readable output."""

    # ------------------------------------------------------------------
    # Plain-text report
    # ------------------------------------------------------------------

    @staticmethod
    def text(result: AnalysisResult, use_color: bool = True) -> str:
        lines: List[str] = []
        score = result.score
        grade_color = _GRADE_COLORS.get(score.grade, "")
        reset = _COLORS["reset"] if use_color else ""
        bold = _COLORS["bold"] if use_color else ""

        header = f"{'─' * 60}"
        lines.append(header)
        lines.append(
            f"{bold}Skill:{reset} {result.skill_name}  "
            f"│  {bold}Safety Score:{reset} "
            f"{grade_color if use_color else ''}{score.score}/100  Grade: {score.grade}{reset}"
        )
        lines.append(
            f"  Findings — "
            f"CRITICAL: {score.critical}  "
            f"HIGH: {score.high}  "
            f"MEDIUM: {score.medium}  "
            f"LOW: {score.low}"
        )
        lines.append(header)

        for check_result in result.check_results:
            status = (
                _c("green", "✔ PASS", use_color)
                if check_result.passed
                else _c("red", "✘ FAIL", use_color)
            )
            lines.append(f"\n  [{status}] {check_result.check_id}")
            lines.append(f"        {check_result.description}")
            for finding in check_result.findings:
                sev_color = _SEV_COLORS.get(finding.severity, "")
                sev_str = (
                    f"{sev_color}{finding.severity.value}{reset}"
                    if use_color
                    else finding.severity.value
                )
                lines.append(
                    f"        • {sev_str} (line {finding.line}): {finding.message}"
                )
                if finding.snippet:
                    lines.append(f"            {_c('grey', finding.snippet, use_color)}")

        lines.append("\n" + header)
        overall = (
            _c("green", "SAFE", use_color)
            if result.passed
            else _c("red", "UNSAFE", use_color)
        )
        lines.append(f"  Overall verdict: {overall}")
        lines.append(header + "\n")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # JSON report
    # ------------------------------------------------------------------

    @staticmethod
    def json(result: AnalysisResult, indent: int = 2) -> str:
        return json.dumps(result.to_dict(), indent=indent)

    # ------------------------------------------------------------------
    # Multi-skill summary
    # ------------------------------------------------------------------

    @staticmethod
    def summary(results: List[AnalysisResult], use_color: bool = True) -> str:
        lines: List[str] = []
        reset = _COLORS["reset"] if use_color else ""
        bold = _COLORS["bold"] if use_color else ""

        lines.append(f"\n{bold}{'═' * 60}{reset}")
        lines.append(f"{bold}  Skill Audit Summary  ({len(results)} skill(s) scanned){reset}")
        lines.append(f"{bold}{'═' * 60}{reset}\n")

        for r in results:
            grade_color = _GRADE_COLORS.get(r.score.grade, "") if use_color else ""
            verdict = "✔ SAFE  " if r.passed else "✘ UNSAFE"
            color = _COLORS["green"] if r.passed else _COLORS["red"]
            lines.append(
                f"  {color if use_color else ''}{verdict}{reset}  "
                f"{r.skill_name:<40}  "
                f"{grade_color}{r.score.score:>3}/100  {r.score.grade}{reset}  "
                f"C:{r.score.critical} H:{r.score.high} M:{r.score.medium} L:{r.score.low}"
            )

        safe = sum(1 for r in results if r.passed)
        unsafe = len(results) - safe
        lines.append(f"\n  {_c('green', str(safe), use_color)} safe, "
                     f"{_c('red', str(unsafe), use_color)} unsafe out of {len(results)} skills.\n")
        return "\n".join(lines)
