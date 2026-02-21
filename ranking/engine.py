"""Composite ranking model for skills.

Weights: Safety 40%, Format 15%, Documentation 15%, Community 30%.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class RankedSkill:
    """Skill with composite score and tier."""

    name: str
    safety_score: int  # 0-100
    grade: str
    format_score: float  # 0-100
    doc_score: float  # 0-100
    community_score: float  # 0-100 (default 50 if no data)
    composite_score: float  # 0-100
    tier: str  # featured, trusted, community, flagged
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "safety_score": self.safety_score,
            "grade": self.grade,
            "format_score": self.format_score,
            "doc_score": self.doc_score,
            "community_score": self.community_score,
            "composite_score": self.composite_score,
            "tier": self.tier,
            **self.metadata,
        }


def compute_composite_score(
    safety_score: int,
    format_score: float = 100.0,
    doc_score: float = 50.0,
    community_score: float = 50.0,
    *,
    safety_weight: float = 0.40,
    format_weight: float = 0.15,
    doc_weight: float = 0.15,
    community_weight: float = 0.30,
) -> float:
    """Compute weighted composite score (0-100)."""
    return (
        safety_score * safety_weight
        + format_score * format_weight
        + doc_score * doc_weight
        + community_score * community_weight
    )


def _assign_tier(
    grade: str,
    composite: float,
    community_score: float,
    report_count: int = 0,
) -> str:
    """Assign ranking tier."""
    if grade == "F" or report_count >= 3:
        return "flagged"
    if grade in ("A", "B") and community_score >= 70:
        return "featured"
    if grade in ("A", "B"):
        return "trusted"
    return "community"


def rank_skills(
    audit_results: list[dict],
    format_scores: Optional[dict[str, float]] = None,
    community_data: Optional[dict[str, dict]] = None,
) -> list[RankedSkill]:
    """Rank skills from audit results.

    Args:
        audit_results: List of analysis result dicts (from analyzer.to_dict())
        format_scores: Optional {skill_name: score} for format compliance
        community_data: Optional {skill_name: {stars, downloads, reports}}
    """
    format_scores = format_scores or {}
    community_data = community_data or {}
    ranked: list[RankedSkill] = []

    for r in audit_results:
        name = r.get("skill_name", "unknown")
        score = r.get("score", {})
        safety = score.get("score", 0)
        grade = score.get("grade", "F")

        fmt = format_scores.get(name, 100.0)
        meta = r.get("metadata", {})
        desc = meta.get("description", "") if isinstance(meta, dict) else ""
        doc = 50.0
        if desc:
            doc = min(100, 50 + len(desc) / 20)  # Heuristic: longer description = better doc

        comm = community_data.get(name, {})
        stars = comm.get("stars", 0)
        downloads = comm.get("downloads", 0)
        reports = comm.get("reports", 0)
        community = 50.0
        if stars or downloads:
            community = min(100, 50 + (stars / 100) + (downloads / 10000))
        if reports > 0:
            community = max(0, community - reports * 15)

        composite = compute_composite_score(safety, fmt, doc, community)
        tier = _assign_tier(grade, composite, community, reports)

        ranked.append(RankedSkill(
            name=name,
            safety_score=safety,
            grade=grade,
            format_score=fmt,
            doc_score=doc,
            community_score=community,
            composite_score=round(composite, 1),
            tier=tier,
            metadata=r,
        ))

    ranked.sort(key=lambda x: (-x.composite_score, x.name))
    return ranked
