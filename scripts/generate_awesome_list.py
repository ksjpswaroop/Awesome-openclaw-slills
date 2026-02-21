#!/usr/bin/env python3
"""Generate SKILLS.md in awesome-list format from skills index."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.parent
SKILLS_INDEX = ROOT / "skills_index"
REGISTRY_JSON = SKILLS_INDEX / "registry.json"
SKILLS_JSON = SKILLS_INDEX / "skills.json"
CURATED_SEEDS = SKILLS_INDEX / "curated_seeds.json"
SKILLS_MD = ROOT / "SKILLS.md"

CLAWHUB_BASE = "https://clawhub.ai/skills"

CATEGORIES = [
    ("AI/ML", ["ai", "llm", "embedding", "rag", "model", "gpt", "claude", "gemini", "openai"]),
    ("Productivity", ["notion", "calendar", "task", "todo", "schedule", "email", "document"]),
    ("Development", ["github", "git", "api", "code", "ci/cd", "database", "dev"]),
    ("Communication", ["slack", "discord", "telegram", "twilio", "message", "chat"]),
    ("Web", ["browser", "http", "scrape", "fetch", "request", "url"]),
    ("Utility", ["file", "calculator", "weather", "search", "convert", "format"]),
    ("Science", ["research", "data", "analysis", "statistic", "science"]),
    ("Media", ["video", "audio", "image", "youtube", "pdf"]),
    ("Social", ["twitter", "seo", "content", "marketing"]),
    ("Finance", ["stock", "crypto", "invest", "finance"]),
    ("Location", ["map", "weather", "travel", "location"]),
    ("Smart Home", ["home", "iot", "assistant", "automation"]),
]


def _infer_category(skill: dict) -> str:
    """Infer category from name, description, or explicit category."""
    if skill.get("category"):
        return skill["category"]
    text = f"{skill.get('name', '')} {skill.get('description', '')}".lower()
    for cat_name, keywords in CATEGORIES:
        if any(kw in text for kw in keywords):
            return cat_name
    return "General"


def load_skills() -> list[dict]:
    """Load all skills from registry, skills.json, and curated seeds."""
    skills: list[dict] = []
    seen: set[str] = set()

    for path in [REGISTRY_JSON, SKILLS_JSON, CURATED_SEEDS]:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                items = data if isinstance(data, list) else []
                for s in items:
                    name = s.get("name", s.get("slug", ""))
                    if name and name not in seen:
                        seen.add(name)
                        skills.append(s)
            except Exception:
                pass

    return skills


def generate_markdown(skills: list[dict]) -> str:
    """Generate SKILLS.md content in awesome-list format."""
    by_cat: dict[str, list[dict]] = {}
    for s in skills:
        cat = _infer_category(s)
        by_cat.setdefault(cat, []).append(s)

    # Sort categories: put General last
    cat_order = [c[0] for c in CATEGORIES] + ["General"]
    sorted_cats = [c for c in cat_order if c in by_cat]
    for c in sorted(by_cat):
        if c not in sorted_cats:
            sorted_cats.append(c)

    lines = [
        "# Awesome OpenClaw Skills",
        "",
        "A curated list of OpenClaw AI agent skills. Vetted, categorized, and ready to install.",
        "",
        "**[Browse on ClawHub](https://clawhub.ai/skills)** · **[Vetting Tool](README.md)**",
        "",
        "---",
        "",
        "## Table of Contents",
        "",
    ]

    for cat in sorted_cats:
        slug = cat.lower().replace(" ", "-").replace("/", "-")
        lines.append(f"- [{cat}](#{slug})")
    lines.append("")

    for cat in sorted_cats:
        slug = cat.lower().replace(" ", "-").replace("/", "-")
        lines.append(f"## {cat}")
        lines.append("")
        items = sorted(by_cat[cat], key=lambda x: x.get("name", "").lower())
        for s in items:
            name = s.get("name", s.get("slug", "unknown"))
            desc = s.get("description", "").strip() or "No description"
            if len(desc) > 150:
                desc = desc[:147] + "..."
            url = f"{CLAWHUB_BASE}/{name}"
            grade = s.get("grade", "")
            badge = f" ![{grade}](https://img.shields.io/badge/grade-{grade}-green?style=flat-square)" if grade in ("A", "B") else ""
            lines.append(f"- [{name}]({url}){badge} — {desc}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(sync_first: bool = False, output: Optional[Path] = None) -> int:
    """Generate SKILLS.md."""
    if sync_first:
        sys.path.insert(0, str(ROOT))
        from ingestion.sync import sync_skills
        sync_skills(fetch_clawhub=True, clawhub_limit=500)
        print("Synced skills from ClawHub", file=sys.stderr)

    skills = load_skills()
    if not skills:
        print("No skills found. Run: skill-sync", file=sys.stderr)
        return 1

    md = generate_markdown(skills)
    out = output or SKILLS_MD
    out.write_text(md, encoding="utf-8")
    print(f"Wrote {len(skills)} skills to {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync", action="store_true", help="Sync from ClawHub first")
    parser.add_argument("-o", "--output", type=Path, help="Output path")
    args = parser.parse_args()
    sys.exit(main(sync_first=args.sync, output=args.output))
