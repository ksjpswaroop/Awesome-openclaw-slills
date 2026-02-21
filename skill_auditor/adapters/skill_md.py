"""Adapter for AgentSkills SKILL.md format.

Parses YAML frontmatter, extracts executable content from:
- scripts/ folder (.py, .sh)
- Inline code blocks in SKILL.md (```python, ```bash, etc.)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Tuple

# Try PyYAML; fallback to simple regex parsing for basic frontmatter
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def load_skill_md(skill_dir: Path) -> Tuple[str, dict]:
    """Load a SKILL.md skill directory and return (source_code, metadata).

    Args:
        skill_dir: Path to skill directory containing SKILL.md

    Returns:
        Tuple of (concatenated_executable_source, metadata_dict)

    Raises:
        FileNotFoundError: If SKILL.md is not found
    """
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")

    text = skill_md.read_text(encoding="utf-8")
    metadata = _parse_frontmatter(text)

    # Collect all executable content
    source_parts: list[str] = []

    # 1. Scripts from scripts/ folder
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        for ext in ("*.py", "*.sh", "*.bash"):
            for p in sorted(scripts_dir.rglob(ext)):
                rel = p.relative_to(skill_dir)
                header = f"\n# --- From {rel} ---\n"
                source_parts.append(header + p.read_text(encoding="utf-8"))

    # 2. Inline code blocks from SKILL.md body
    body = _extract_body(text)
    for lang, code in _extract_code_blocks(body):
        # Include Python, bash, sh - executable languages
        if lang in ("python", "py", "bash", "sh", ""):
            header = f"\n# --- Inline {lang or 'code'} block ---\n"
            source_parts.append(header + code)

    source_code = "\n".join(source_parts) if source_parts else ""
    metadata.setdefault("name", skill_dir.name)
    return source_code, metadata


def _parse_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter from markdown. Returns {} if none."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}

    yaml_str = match.group(1).strip()
    if not yaml_str:
        return {}

    if HAS_YAML:
        try:
            data = yaml.safe_load(yaml_str)
            return dict(data) if isinstance(data, dict) else {}
        except Exception:
            return _parse_frontmatter_fallback(yaml_str)

    return _parse_frontmatter_fallback(yaml_str)


def _parse_frontmatter_fallback(yaml_str: str) -> dict:
    """Simple key: value extraction when YAML is unavailable."""
    result: dict = {}
    for line in yaml_str.splitlines():
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if m:
            key, val = m.groups()
            val = val.strip().strip('"\'')
            result[key] = val
    return result


def _extract_body(text: str) -> str:
    """Return markdown content after frontmatter."""
    match = re.match(r"^---\s*\n.*?\n---\s*\n", text, re.DOTALL)
    if match:
        return text[match.end() :].strip()
    return text.strip()


def _extract_code_blocks(body: str) -> list[Tuple[str, str]]:
    """Extract (lang, code) from ```lang\ncode\n``` blocks."""
    blocks: list[Tuple[str, str]] = []
    # Match ```lang (optional) \n code \n ```
    pattern = re.compile(r"```(\w*)\s*\n(.*?)```", re.DOTALL)
    for m in pattern.finditer(body):
        lang = (m.group(1) or "").lower()
        code = m.group(2).strip()
        if code:
            blocks.append((lang, code))
    return blocks
