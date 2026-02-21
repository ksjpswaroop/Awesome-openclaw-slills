"""Schema validation - SKILL.md format compliance against AgentSkills spec."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _parse_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}
    try:
        import yaml
        data = yaml.safe_load(match.group(1))
        return dict(data) if isinstance(data, dict) else {}
    except Exception:
        return {}


def _validate_skills_schema(metadata: dict) -> list[str]:
    """Validate against AgentSkills spec. Returns list of errors."""
    errors = []
    if not metadata.get("name"):
        errors.append("Missing required field: name")
    else:
        name = metadata["name"]
        if not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$", name):
            errors.append("name must be lowercase letters, numbers, hyphens only (1-64 chars)")
    if not metadata.get("description"):
        errors.append("Missing required field: description")
    elif len(metadata["description"]) > 1024:
        errors.append("description must be <= 1024 characters")
    return errors


class TestSchemaValidation:
    """SKILL.md format compliance tests."""

    def test_safe_skill_has_valid_schema(self):
        skill_md = FIXTURES_DIR / "safe_skill" / "SKILL.md"
        text = skill_md.read_text()
        meta = _parse_frontmatter(text)
        errors = _validate_skills_schema(meta)
        assert errors == [], f"Schema errors: {errors}"

    def test_unsafe_skill_has_valid_schema(self):
        skill_md = FIXTURES_DIR / "unsafe_skill" / "SKILL.md"
        text = skill_md.read_text()
        meta = _parse_frontmatter(text)
        errors = _validate_skills_schema(meta)
        assert errors == [], f"Schema errors: {errors}"
