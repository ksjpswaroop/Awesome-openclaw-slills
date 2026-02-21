"""Tests for SkillAnalyzer, SafetyScore, and Report."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from skill_auditor.analyzer import SkillAnalyzer, AnalysisResult
from skill_auditor.scorer import SafetyScore
from skill_auditor.report import Report
from skill_auditor.checks.base import CheckResult, Finding, Severity

EXAMPLES_DIR = Path(__file__).parent.parent / "examples" / "skills"


# ---------------------------------------------------------------------------
# SafetyScore
# ---------------------------------------------------------------------------

class TestSafetyScore:
    def test_no_findings_scores_100_grade_a(self):
        results = [CheckResult(check_id="X", passed=True, findings=[])]
        score = SafetyScore.from_check_results(results)
        assert score.score == 100
        assert score.grade == "A"
        assert score.total_findings == 0

    def test_single_critical_finding_reduces_score(self):
        finding = Finding(check_id="X", severity=Severity.CRITICAL, message="bad")
        results = [CheckResult(check_id="X", passed=False, findings=[finding])]
        score = SafetyScore.from_check_results(results)
        assert score.score == 70  # 100 - 30
        assert score.critical == 1

    def test_multiple_criticals_can_reach_zero(self):
        findings = [
            Finding(check_id="X", severity=Severity.CRITICAL, message="bad")
            for _ in range(5)
        ]
        results = [CheckResult(check_id="X", passed=False, findings=findings)]
        score = SafetyScore.from_check_results(results)
        assert score.score == 0
        assert score.grade == "F"

    def test_to_dict_contains_all_keys(self):
        results = []
        score = SafetyScore.from_check_results(results)
        d = score.to_dict()
        assert set(d.keys()) == {"score", "grade", "critical", "high", "medium", "low", "total_findings"}


# ---------------------------------------------------------------------------
# SkillAnalyzer
# ---------------------------------------------------------------------------

class TestSkillAnalyzer:
    analyzer = SkillAnalyzer()

    def test_safe_calculator_json(self):
        result = self.analyzer.analyze_file(EXAMPLES_DIR / "safe_calculator_skill.json")
        assert result.skill_name == "calculator"
        assert result.score.grade in ("A", "B")

    def test_safe_weather_skill(self):
        result = self.analyzer.analyze_file(EXAMPLES_DIR / "safe_weather_skill.py")
        # Weather skill makes GET-only HTTP calls and discloses them — should pass DATA_EXFIL
        exfil_result = next(r for r in result.check_results if r.check_id == "DATA_EXFIL")
        assert exfil_result.passed

    def test_unsafe_skill_fails(self):
        result = self.analyzer.analyze_file(EXAMPLES_DIR / "unsafe_malicious_skill.py")
        assert not result.passed
        assert result.score.critical > 0
        assert result.score.grade == "F"

    def test_unsafe_skill_has_exfiltration_finding(self):
        result = self.analyzer.analyze_file(EXAMPLES_DIR / "unsafe_malicious_skill.py")
        exfil_result = next(r for r in result.check_results if r.check_id == "DATA_EXFIL")
        assert not exfil_result.passed

    def test_unsafe_skill_has_shell_injection_finding(self):
        result = self.analyzer.analyze_file(EXAMPLES_DIR / "unsafe_malicious_skill.py")
        shell_result = next(r for r in result.check_results if r.check_id == "SHELL_INJECTION")
        assert not shell_result.passed

    def test_unsafe_skill_has_env_leakage_finding(self):
        result = self.analyzer.analyze_file(EXAMPLES_DIR / "unsafe_malicious_skill.py")
        env_result = next(r for r in result.check_results if r.check_id == "ENV_LEAKAGE")
        assert not env_result.passed

    def test_analyze_source_string(self):
        code = "def hello():\n    return 'hi'"
        result = self.analyzer.analyze_source(code, {"name": "hello_skill"})
        assert result.skill_name == "hello_skill"
        assert result.passed

    def test_to_dict_structure(self):
        code = "def noop(): pass"
        result = self.analyzer.analyze_source(code, {"name": "noop"})
        d = result.to_dict()
        assert "skill_name" in d
        assert "score" in d
        assert "checks" in d
        assert isinstance(d["checks"], list)

    def test_file_not_found_raises(self):
        with pytest.raises(FileNotFoundError):
            self.analyzer.analyze_file("/nonexistent/path/skill.py")

    def test_unsupported_extension_raises(self, tmp_path):
        tmp = tmp_path / "skill.rb"
        tmp.write_text("puts 'hello'")
        with pytest.raises(ValueError, match="Unsupported"):
            self.analyzer.analyze_file(tmp)

    def test_safe_skill_md_directory(self):
        result = self.analyzer.analyze_file(EXAMPLES_DIR / "safe_skill")
        assert result.skill_name == "safe-skill"
        assert result.passed
        assert result.score.grade in ("A", "B")

    def test_unsafe_skill_md_directory(self):
        result = self.analyzer.analyze_file(EXAMPLES_DIR / "unsafe_skill")
        assert result.skill_name == "unsafe-skill"
        assert not result.passed
        assert result.score.critical > 0

    def test_skill_md_with_scripts_directory(self):
        result = self.analyzer.analyze_file(EXAMPLES_DIR / "safe_skill_with_scripts")
        assert result.skill_name == "safe-skill-with-scripts"
        assert result.passed

    def test_directory_without_skill_md_raises(self, tmp_path):
        with pytest.raises(ValueError, match="SKILL.md"):
            self.analyzer.analyze_file(tmp_path)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

class TestReport:
    analyzer = SkillAnalyzer()

    def test_text_report_contains_skill_name(self):
        code = "def noop(): pass"
        result = self.analyzer.analyze_source(code, {"name": "my_skill"})
        text = Report.text(result, use_color=False)
        assert "my_skill" in text

    def test_text_report_shows_safe(self):
        code = "def noop(): pass"
        result = self.analyzer.analyze_source(code, {"name": "safe"})
        text = Report.text(result, use_color=False)
        assert "SAFE" in text

    def test_text_report_shows_unsafe(self):
        code = "import os\nos.system('id')"
        result = self.analyzer.analyze_source(code, {"name": "bad"})
        text = Report.text(result, use_color=False)
        assert "UNSAFE" in text

    def test_json_report_is_valid_json(self):
        code = "def noop(): pass"
        result = self.analyzer.analyze_source(code, {"name": "noop"})
        raw = Report.json(result)
        parsed = json.loads(raw)
        assert parsed["skill_name"] == "noop"

    def test_summary_counts_safe_unsafe(self):
        safe = self.analyzer.analyze_source("def ok(): pass", {"name": "safe_skill"})
        unsafe = self.analyzer.analyze_source("eval(x)", {"name": "bad_skill"})
        text = Report.summary([safe, unsafe], use_color=False)
        assert "1 safe" in text
        assert "1 unsafe" in text


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------

class TestCLI:
    def _run(self, args):
        from skill_auditor.cli import main
        return main(args)

    def test_safe_skill_exits_zero(self):
        rc = self._run([str(EXAMPLES_DIR / "safe_calculator_skill.json"), "--no-color"])
        assert rc == 0

    def test_unsafe_skill_exits_nonzero(self):
        rc = self._run([str(EXAMPLES_DIR / "unsafe_malicious_skill.py"), "--no-color"])
        assert rc == 1

    def test_json_output(self, capsys):
        self._run([str(EXAMPLES_DIR / "safe_calculator_skill.json"), "--format", "json", "--no-color"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert isinstance(data, list)
        assert data[0]["skill_name"] == "calculator"

    def test_exit_zero_flag(self):
        rc = self._run([str(EXAMPLES_DIR / "unsafe_malicious_skill.py"), "--exit-zero", "--no-color"])
        assert rc == 0

    def test_no_files_exits_nonzero(self):
        rc = self._run(["--no-color", "/nonexistent_dir_xyz"])
        assert rc == 1

    def test_fail_only_suppresses_safe_output(self, capsys):
        self._run([
            str(EXAMPLES_DIR / "safe_calculator_skill.json"),
            "--fail-only", "--no-color",
        ])
        captured = capsys.readouterr()
        # Safe skill should produce no output in fail-only mode
        assert captured.out.strip() == ""
