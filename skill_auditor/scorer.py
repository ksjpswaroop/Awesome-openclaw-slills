"""Safety scoring engine.

Converts a set of ``CheckResult`` objects into a numeric safety score (0–100)
and a letter grade (A–F), similar to npm audit's severity aggregation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .checks.base import CheckResult, Severity

# Penalty points deducted per finding, by severity
_PENALTIES: dict = {
    Severity.CRITICAL: 30,
    Severity.HIGH: 15,
    Severity.MEDIUM: 7,
    Severity.LOW: 2,
}


@dataclass
class SafetyScore:
    """Numeric safety score and summary counts for a skill."""

    score: int  # 0–100 (higher is safer)
    grade: str  # A / B / C / D / F
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    total_findings: int = 0

    @classmethod
    def from_check_results(cls, results: List[CheckResult]) -> "SafetyScore":
        counts: dict = {s: 0 for s in Severity}
        for result in results:
            for finding in result.findings:
                counts[finding.severity] += 1

        total = sum(counts.values())
        penalty = sum(_PENALTIES[sev] * count for sev, count in counts.items())
        raw_score = max(0, 100 - penalty)

        if raw_score >= 90:
            grade = "A"
        elif raw_score >= 75:
            grade = "B"
        elif raw_score >= 60:
            grade = "C"
        elif raw_score >= 40:
            grade = "D"
        else:
            grade = "F"

        return cls(
            score=raw_score,
            grade=grade,
            critical=counts[Severity.CRITICAL],
            high=counts[Severity.HIGH],
            medium=counts[Severity.MEDIUM],
            low=counts[Severity.LOW],
            total_findings=total,
        )

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "grade": self.grade,
            "critical": self.critical,
            "high": self.high,
            "medium": self.medium,
            "low": self.low,
            "total_findings": self.total_findings,
        }
