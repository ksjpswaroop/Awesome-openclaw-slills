/** Category keywords for awesome-list grouping */

export const CATEGORY_KEYWORDS: Record<string, string[]> = {
  "AI/ML": ["ai", "llm", "embedding", "rag", "model", "gpt", "claude", "gemini", "openai", "translate", "summarize"],
  "Productivity": ["notion", "calendar", "task", "todo", "schedule", "email", "document"],
  "Development": ["github", "git", "api", "code", "ci/cd", "database", "dev", "sqlite", "claude"],
  "Communication": ["slack", "discord", "telegram", "twilio", "message", "chat", "email"],
  "Web": ["browser", "http", "scrape", "fetch", "request", "url", "search"],
  "Utility": ["file", "calculator", "convert", "format", "csv", "json"],
  "Science": ["research", "data", "analysis", "statistic", "science", "market"],
  "Media": ["video", "audio", "image", "youtube", "pdf"],
  "Social": ["twitter", "seo", "content", "marketing"],
  "Finance": ["stock", "crypto", "invest", "finance"],
  "Location": ["map", "weather", "travel", "location"],
  "Smart Home": ["home", "iot", "assistant", "automation"],
};

export function inferCategory(skill: { name?: string; description?: string; category?: string }): string {
  if (skill.category) return skill.category;
  const text = `${skill.name ?? ""} ${skill.description ?? ""}`.toLowerCase();
  for (const [cat, keywords] of Object.entries(CATEGORY_KEYWORDS)) {
    if (keywords.some((kw) => text.includes(kw))) return cat;
  }
  return "General";
}

export function groupByCategory(skills: { name: string; description?: string; category?: string }[]) {
  const groups: Record<string, typeof skills> = {};
  for (const s of skills) {
    const cat = inferCategory(s);
    if (!groups[cat]) groups[cat] = [];
    groups[cat].push(s);
  }
  const order = Object.keys(CATEGORY_KEYWORDS).concat("General");
  const sorted = order.filter((c) => groups[c]?.length).concat(
    Object.keys(groups).filter((c) => !order.includes(c))
  );
  return { groups, order: sorted };
}
