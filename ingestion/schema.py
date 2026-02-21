"""Canonical skill schema for the skills index."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class SkillRecord:
    """Normalized skill record for the index."""

    name: str
    description: str
    source: str  # e.g. "clawhub", "clawhub.biz", "github"
    version: Optional[str] = None
    category: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    scripts: list[str] = field(default_factory=list)
    install_cmd: Optional[str] = None
    path: Optional[str] = None  # Local path if synced to disk

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "source": self.source,
            "version": self.version,
            "category": self.category,
            "metadata": self.metadata,
            "scripts": self.scripts,
            "install_cmd": self.install_cmd or f"clawhub install {self.name}",
            "path": self.path,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "SkillRecord":
        name = d.get("name", d.get("slug", d.get("id", "unknown")))
        return cls(
            name=name,
            description=d.get("description", d.get("summary", "")),
            source=d.get("source", "unknown"),
            version=d.get("version"),
            category=d.get("category"),
            metadata=d.get("metadata", {}),
            scripts=d.get("scripts", []),
            install_cmd=d.get("install_cmd") or (f"clawhub install {name}" if name else None),
            path=d.get("path"),
        )
