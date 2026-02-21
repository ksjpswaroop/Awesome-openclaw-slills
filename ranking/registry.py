"""Generate and write the skills registry (skills_index/registry.json)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .engine import rank_skills, RankedSkill
from .usage import generate_usage_doc

SKILLS_INDEX = Path(__file__).parent.parent / "skills_index"


def write_registry(
    audit_results: list[dict],
    output_path: Optional[Path] = None,
    format_scores: Optional[dict] = None,
    community_data: Optional[dict] = None,
) -> Path:
    """Rank skills and write registry.json with usage summaries.

    Returns the path to the written file.
    """
    ranked = rank_skills(audit_results, format_scores, community_data)
    out = output_path or (SKILLS_INDEX / "registry.json")
    out.parent.mkdir(parents=True, exist_ok=True)

    registry = []
    for r in ranked:
        meta = r.metadata.get("metadata", {})
        usage = generate_usage_doc(
            name=r.name,
            description=meta.get("description", ""),
            metadata=meta,
            install_cmd=f"clawhub install {r.name}",
        )
        registry.append({
            "name": r.name,
            "description": meta.get("description", ""),
            "score": r.safety_score,
            "safety_score": r.safety_score,
            "grade": r.grade,
            "tier": r.tier,
            "composite_score": r.composite_score,
            "usage_summary": usage[:500] + "..." if len(usage) > 500 else usage,
            "install_cmd": f"clawhub install {r.name}",
        })

    with open(out, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
    return out
