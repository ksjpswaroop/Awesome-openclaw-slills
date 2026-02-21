#!/usr/bin/env python3
"""Build skills_index/registry.json from sync + audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from ingestion.sync import sync_skills, SKILLS_JSON
from skill_auditor import SkillAnalyzer
from ranking.registry import write_registry


def main() -> int:
    """Sync, audit, and write registry."""
    index_dir = ROOT / "skills_index"
    index_dir.mkdir(parents=True, exist_ok=True)

    # 1. Sync skills
    records = sync_skills(local_dirs=[ROOT / "examples" / "skills"])
    print(f"Synced {len(records)} skills", file=sys.stderr)

    # 2. Audit each skill
    analyzer = SkillAnalyzer()
    results = []
    for r in records:
        path = r.path
        if path:
            try:
                res = analyzer.analyze_file(path)
                results.append(res.to_dict())
            except Exception as e:
                print(f"Audit failed for {r.name}: {e}", file=sys.stderr)
        else:
            # No local path - create placeholder
            results.append({
                "skill_name": r.name,
                "metadata": {"description": r.description},
                "score": {"score": 50, "grade": "C"},
            })

    # 3. Write registry
    out = write_registry(results)
    print(f"Wrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
