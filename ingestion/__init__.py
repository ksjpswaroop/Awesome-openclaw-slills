"""Skill ingestion: sync from ClawHub and other sources into a local index."""

from .schema import SkillRecord
from .sync import sync_skills

__all__ = ["sync_skills", "SkillRecord"]
