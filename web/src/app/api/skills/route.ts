import { NextResponse } from "next/server";
import { readFile } from "fs/promises";
import { join } from "path";

const CWD = process.cwd();

function skillsIndexPath(subpath: string): string {
  return join(CWD, "..", "skills_index", subpath);
}

function normalizeSkill(s: Record<string, unknown>): Record<string, unknown> {
  return {
    name: s.name,
    description: s.description,
    category: s.category,
    grade: s.grade || "B",
    tier: s.tier || "community",
    safety_score: s.safety_score ?? s.score ?? 75,
    composite_score: s.composite_score ?? 70,
    install_cmd: s.install_cmd || `clawhub install ${s.name}`,
  };
}

export async function GET() {
  const seen = new Set<string>();
  const merged: Record<string, unknown>[] = [];

  const sources = [
    "registry.json",
    "skills.json",
    "curated_seeds.json",
  ];

  for (const file of sources) {
    const p = skillsIndexPath(file);
    try {
      const data = await readFile(p, "utf-8");
      const arr = JSON.parse(data);
      const items = Array.isArray(arr) ? arr : [];
      for (const s of items) {
        const name = String(s?.name ?? s?.slug ?? "").trim();
        if (name && !seen.has(name)) {
          seen.add(name);
          merged.push(normalizeSkill(s));
        }
      }
    } catch {
      continue;
    }
  }

  // Also try CWD/skills_index (when running from project root)
  if (merged.length === 0) {
    for (const file of sources) {
      const p = join(CWD, "skills_index", file);
      try {
        const data = await readFile(p, "utf-8");
        const arr = JSON.parse(data);
        const items = Array.isArray(arr) ? arr : [];
        for (const s of items) {
          const name = String(s?.name ?? s?.slug ?? "").trim();
          if (name && !seen.has(name)) {
            seen.add(name);
            merged.push(normalizeSkill(s));
          }
        }
      } catch {
        continue;
      }
    }
  }

  return NextResponse.json(merged);
}
