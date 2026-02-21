/**
 * Skills registry loading and search utilities.
 */

export type SkillSummary = {
  name: string;
  description?: string;
  grade: string;
  tier: string;
  safety_score: number;
  composite_score: number;
  install_cmd?: string;
};

export async function loadSkills(): Promise<SkillSummary[]> {
  const res = await fetch("/api/skills");
  const data = await res.json();
  return Array.isArray(data) ? data : data.skills || [];
}

export function searchSkills(
  skills: SkillSummary[],
  query: string
): SkillSummary[] {
  if (!query.trim()) return skills;
  const q = query.toLowerCase();
  return skills.filter(
    (s) =>
      s.name.toLowerCase().includes(q) ||
      (s.description || "").toLowerCase().includes(q)
  );
}

export function filterByTier(
  skills: SkillSummary[],
  tier: string
): SkillSummary[] {
  if (tier === "all") return skills;
  return skills.filter((s) => s.tier === tier);
}
