"""Base class for all skill security checks."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Finding:
    """A single security finding produced by a check."""

    check_id: str
    severity: Severity
    message: str
    line: int = 0
    snippet: str = ""

    def to_dict(self) -> dict:
        return {
            "check_id": self.check_id,
            "severity": self.severity.value,
            "message": self.message,
            "line": self.line,
            "snippet": self.snippet,
        }


@dataclass
class CheckResult:
    """Aggregated result for one check run against a skill."""

    check_id: str
    passed: bool
    findings: List[Finding] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "check_id": self.check_id,
            "passed": self.passed,
            "description": self.description,
            "findings": [f.to_dict() for f in self.findings],
        }


class BaseCheck(ABC):
    """Abstract base for all security checks."""

    check_id: str = ""
    description: str = ""

    @abstractmethod
    def run(self, source_code: str, skill_metadata: dict) -> CheckResult:
        """Execute the check and return a ``CheckResult``.

        Args:
            source_code: Raw Python source of the skill (may be empty for
                         JSON/YAML-only skills).
            skill_metadata: Parsed skill definition dict (name, description,
                            parameters, …).
        """
