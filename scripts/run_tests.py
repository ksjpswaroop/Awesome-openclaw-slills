#!/usr/bin/env python3
"""Run smoke tests when pytest is not installed."""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


def main():
    errors = []

    # skill_auditor
    try:
        from skill_auditor import SkillAnalyzer
        a = SkillAnalyzer()
        r = a.analyze_file(ROOT / "examples/skills/safe_calculator_skill.json")
        assert r.skill_name == "calculator"
        assert r.passed
        r2 = a.analyze_file(ROOT / "examples/skills/unsafe_malicious_skill.py")
        assert not r2.passed
        print("  skill_auditor: OK")
    except Exception as e:
        errors.append(f"skill_auditor: {e}")
        print(f"  skill_auditor: FAIL {e}")

    # adapters
    try:
        from skill_auditor.adapters.skill_md import load_skill_md
        src, meta = load_skill_md(ROOT / "examples/skills/safe_skill")
        assert "name" in meta
        print("  adapters.skill_md: OK")
    except Exception as e:
        errors.append(f"adapters: {e}")
        print(f"  adapters.skill_md: FAIL {e}")

    # ingestion
    try:
        from ingestion.sync import sync_skills
        recs = sync_skills(fetch_clawhub=False)
        assert len(recs) >= 3
        print("  ingestion.sync: OK")
    except Exception as e:
        errors.append(f"ingestion: {e}")
        print(f"  ingestion.sync: FAIL {e}")

    # ranking
    try:
        from ranking.engine import rank_skills
        from skill_auditor import SkillAnalyzer
        a = SkillAnalyzer()
        r = a.analyze_file(ROOT / "examples/skills/safe_skill")
        ranked = rank_skills([r.to_dict()])
        assert ranked[0].tier == "trusted"
        print("  ranking.engine: OK")
    except Exception as e:
        errors.append(f"ranking: {e}")
        print(f"  ranking.engine: FAIL {e}")

    # usage
    try:
        from ranking.usage import generate_usage_doc
        doc = generate_usage_doc("test", "desc", {})
        assert "clawhub install test" in doc
        print("  ranking.usage: OK")
    except Exception as e:
        errors.append(f"usage: {e}")
        print(f"  ranking.usage: FAIL {e}")

    # build_registry
    try:
        from ingestion.sync import sync_skills
        from skill_auditor import SkillAnalyzer
        from ranking.registry import write_registry
        recs = sync_skills(fetch_clawhub=False)
        a = SkillAnalyzer()
        results = []
        for r in recs:
            if r.path:
                res = a.analyze_file(r.path)
                results.append(res.to_dict())
        out = write_registry(results)
        assert out.exists()
        print("  build_registry: OK")
    except Exception as e:
        errors.append(f"build_registry: {e}")
        print(f"  build_registry: FAIL {e}")

    if errors:
        print(f"\n{len(errors)} failure(s)")
        return 1
    print("\nAll smoke tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
