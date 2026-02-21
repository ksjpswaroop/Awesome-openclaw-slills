"""Sync skills from ClawHub and other sources into skills_index."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterator

from .schema import SkillRecord

SKILLS_INDEX_DIR = Path(__file__).parent.parent / "skills_index"
SKILLS_JSON = SKILLS_INDEX_DIR / "skills.json"


def _ensure_index_dir() -> Path:
    SKILLS_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    return SKILLS_INDEX_DIR


def _fetch_clawhub_skills(limit: int = 200) -> list[dict]:
    """Fetch skill list from ClawHub (API or CLI)."""
    from .clawhub_fetch import fetch_clawhub_skills
    return fetch_clawhub_skills(limit=limit)


def _clawhub_to_record(s: dict) -> SkillRecord:
    """Convert ClawHub skill dict to SkillRecord."""
    name = s.get("name", s.get("slug", s.get("id", "")))
    if not name:
        name = str(s.get("_id", "unknown"))
    return SkillRecord(
        name=name,
        description=s.get("description", s.get("summary", "")) or "",
        source="clawhub",
        version=s.get("version"),
        category=s.get("category"),
        metadata=s,
        scripts=[],
        install_cmd=f"clawhub install {name}",
    )


def _discover_local_skills(skills_root: Path) -> Iterator[SkillRecord]:
    """Discover skills from a local directory of SKILL.md folders."""
    if not skills_root.exists():
        return
    for item in skills_root.iterdir():
        if item.is_dir():
            skill_md = item / "SKILL.md"
            if skill_md.exists():
                try:
                    from skill_auditor.adapters.skill_md import load_skill_md
                    _, metadata = load_skill_md(item)
                    scripts = []
                    scripts_dir = item / "scripts"
                    if scripts_dir.is_dir():
                        for p in scripts_dir.rglob("*.py"):
                            scripts.append(str(p.relative_to(item)))
                    yield SkillRecord(
                        name=metadata.get("name", item.name),
                        description=metadata.get("description", ""),
                        source="local",
                        metadata=metadata,
                        scripts=scripts,
                        path=str(item),
                        install_cmd=f"clawhub install {metadata.get('name', item.name)}",
                    )
                except Exception:
                    pass


def _load_existing(path: Path) -> dict[str, SkillRecord]:
    """Load existing skills keyed by name for merge. Local (with path) overrides remote."""
    result: dict[str, SkillRecord] = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for item in data if isinstance(data, list) else []:
                rec = SkillRecord.from_dict(item) if isinstance(item, dict) else item
                if isinstance(rec, SkillRecord):
                    result[rec.name] = rec
        except Exception:
            pass
    return result


def sync_skills(
    local_dirs: list[Path] | None = None,
    output_path: Path | None = None,
    fetch_clawhub: bool = True,
    clawhub_limit: int = 200,
    incremental: bool = False,
) -> list[SkillRecord]:
    """Sync skills from available sources into the index.

    Args:
        local_dirs: Optional list of directories to scan for SKILL.md skills.
        output_path: Where to write skills.json. Default: skills_index/skills.json
        fetch_clawhub: Whether to fetch from ClawHub (API/CLI).
        clawhub_limit: Max skills to fetch from ClawHub.
        incremental: If True, merge with existing index (add/update, preserve others).

    Returns:
        List of synced SkillRecords.
    """
    _ensure_index_dir()
    out = output_path or SKILLS_JSON
    existing = _load_existing(out) if incremental else {}
    by_name: dict[str, SkillRecord] = dict(existing)

    # 1. Fetch from ClawHub (API or CLI) - add/update, don't overwrite local
    if fetch_clawhub:
        clawhub_skills = _fetch_clawhub_skills(limit=clawhub_limit)
        for s in clawhub_skills:
            if isinstance(s, dict):
                try:
                    rec = _clawhub_to_record(s)
                except Exception:
                    rec = SkillRecord.from_dict(s)
            else:
                rec = s
            if rec.name not in by_name or by_name[rec.name].source == "clawhub":
                by_name[rec.name] = rec

    # 2. Discover from local directories (local overrides clawhub)
    if local_dirs:
        for d in local_dirs:
            for rec in _discover_local_skills(d):
                by_name[rec.name] = rec

    # 3. Always scan examples/skills (local overrides)
    examples = Path(__file__).parent.parent / "examples" / "skills"
    if examples.exists():
        for rec in _discover_local_skills(examples):
            by_name[rec.name] = rec

    records = list(by_name.values())
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump([r.to_dict() for r in records], f, indent=2)

    return records


def main() -> int:
    """CLI entry point for skill sync."""
    import argparse
    parser = argparse.ArgumentParser(description="Sync skills into skills_index")
    parser.add_argument(
        "dirs",
        nargs="*",
        type=Path,
        help="Additional directories to scan for SKILL.md skills",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=SKILLS_JSON,
        help="Output path for skills.json",
    )
    parser.add_argument(
        "--no-clawhub",
        action="store_true",
        help="Skip ClawHub fetch (local only)",
    )
    parser.add_argument(
        "--clawhub-limit",
        type=int,
        default=200,
        help="Max skills to fetch from ClawHub (default: 200)",
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Merge with existing index (delta update)",
    )
    args = parser.parse_args()
    records = sync_skills(
        local_dirs=args.dirs if args.dirs else None,
        output_path=args.output,
        fetch_clawhub=not args.no_clawhub,
        clawhub_limit=args.clawhub_limit,
        incremental=args.incremental,
    )
    print(f"Synced {len(records)} skills to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
