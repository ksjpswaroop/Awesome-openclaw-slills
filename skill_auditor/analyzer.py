"""Core analyzer — loads a skill and runs all registered checks."""

from __future__ import annotations

import ast
import json
import textwrap
from pathlib import Path
from typing import Dict, List, Optional, Union

from .checks import ALL_CHECKS
from .checks.base import CheckResult
from .scorer import SafetyScore


class SkillAnalyzer:
    """Analyze one or more LLM agent skills for security issues.

    Supported skill formats:

    * **Python file** (``.py``) — the source is parsed with ``ast`` and all
      registered checks are run.
    * **JSON file** (``.json``) — expected to be an OpenAI-style function
      definition or a list of such definitions.
    * **Raw string** — pass ``source_code=`` directly to :meth:`analyze_source`.
    """

    def __init__(self, checks=None):
        check_classes = checks if checks is not None else ALL_CHECKS
        self._checks = [cls() for cls in check_classes]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze_file(self, path: Union[str, Path]) -> "AnalysisResult":
        """Analyze a single skill file (.py or .json)."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Skill file not found: {path}")

        source_code = ""
        metadata: dict = {}

        if path.suffix == ".py":
            source_code = path.read_text(encoding="utf-8")
            metadata = _extract_metadata_from_python(source_code)
        elif path.suffix in (".json",):
            raw = json.loads(path.read_text(encoding="utf-8"))
            metadata = raw if isinstance(raw, dict) else {}
            # A JSON skill may embed a `source` key with inline Python
            source_code = metadata.get("source", "")
        else:
            raise ValueError(f"Unsupported skill file type: {path.suffix!r}")

        metadata.setdefault("name", path.stem)
        return self.analyze_source(source_code, metadata)

    def analyze_source(self, source_code: str, skill_metadata: Optional[dict] = None) -> "AnalysisResult":
        """Run all checks against raw source code and optional metadata dict."""
        metadata = skill_metadata or {}
        results: List[CheckResult] = [
            check.run(source_code, metadata) for check in self._checks
        ]
        score = SafetyScore.from_check_results(results)
        return AnalysisResult(
            skill_name=metadata.get("name", "<unknown>"),
            source_code=source_code,
            metadata=metadata,
            check_results=results,
            score=score,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_metadata_from_python(source: str) -> dict:
    """Best-effort extraction of skill metadata from a Python source file.

    Looks for:
    - A module-level docstring → used as ``description``
    - An ``__skill__`` dict literal at module level
    """
    metadata: dict = {}
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return metadata

    # Module docstring
    doc = ast.get_docstring(tree)
    if doc:
        metadata["description"] = doc

    # __skill__ = {...} at module level
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(t, ast.Name) and t.id == "__skill__"
                for t in node.targets
            )
            and isinstance(node.value, ast.Dict)
        ):
            try:
                metadata.update(ast.literal_eval(node.value))
            except (ValueError, TypeError):
                pass
            break

    return metadata


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

class AnalysisResult:
    """The full result of analyzing one skill."""

    def __init__(
        self,
        skill_name: str,
        source_code: str,
        metadata: dict,
        check_results: List[CheckResult],
        score: "SafetyScore",
    ):
        self.skill_name = skill_name
        self.source_code = source_code
        self.metadata = metadata
        self.check_results = check_results
        self.score = score

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.check_results)

    def to_dict(self) -> dict:
        return {
            "skill_name": self.skill_name,
            "score": self.score.to_dict(),
            "passed": self.passed,
            "checks": [r.to_dict() for r in self.check_results],
        }
