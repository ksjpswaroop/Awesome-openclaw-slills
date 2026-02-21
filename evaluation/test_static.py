"""Static analysis tests - run auditor on fixtures and assert scores."""

from __future__ import annotations

from pathlib import Path

import pytest

from skill_auditor import SkillAnalyzer

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestStaticFixtures:
    """Regression tests: known-safe and known-unsafe skills must get expected scores."""

    analyzer = SkillAnalyzer()

    def test_safe_skill_passes(self):
        result = self.analyzer.analyze_file(FIXTURES_DIR / "safe_skill")
        assert result.passed
        assert result.score.grade in ("A", "B")
        assert result.score.critical == 0

    def test_unsafe_skill_fails(self):
        result = self.analyzer.analyze_file(FIXTURES_DIR / "unsafe_skill")
        assert not result.passed
        assert result.score.critical >= 1
        assert result.score.grade in ("D", "F")  # Unsafe

    def test_unsafe_skill_has_shell_injection(self):
        result = self.analyzer.analyze_file(FIXTURES_DIR / "unsafe_skill")
        shell_check = next(r for r in result.check_results if r.check_id == "SHELL_INJECTION")
        assert not shell_check.passed
