import { NextResponse } from "next/server";
import { readFile } from "fs/promises";
import { join } from "path";

const CWD = process.cwd();
const REGISTRY_CANDIDATES = [
  join(CWD, "skills_index", "registry.json"),
  join(CWD, "..", "skills_index", "registry.json"),
];
const SKILLS_CANDIDATES = [
  join(CWD, "skills_index", "skills.json"),
  join(CWD, "..", "skills_index", "skills.json"),
];

export async function GET() {
  for (const p of REGISTRY_CANDIDATES) {
    try {
      const data = await readFile(p, "utf-8");
      return NextResponse.json(JSON.parse(data));
    } catch {
      continue;
    }
  }
  for (const p of SKILLS_CANDIDATES) {
    try {
      const data = await readFile(p, "utf-8");
      const skills = JSON.parse(data);
      return NextResponse.json(
        skills.map((s: Record<string, unknown>) => ({
          name: s.name,
          description: s.description,
          grade: "B",
          tier: "community",
          safety_score: 75,
          composite_score: 70,
          install_cmd: s.install_cmd || `clawhub install ${s.name}`,
        }))
      );
    } catch {
      continue;
    }
  }
  return NextResponse.json([]);
}
