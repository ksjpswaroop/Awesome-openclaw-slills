"use client";

import { useState } from "react";
import type { Skill } from "@/app/page";
import { groupByCategory } from "@/lib/categories";

type SkillListProps = {
  skills: Skill[];
  loading: boolean;
};

const CLAWHUB_SKILL_URL = "https://clawhub.ai/skills";

function SkillRow({ skill, searchMatch }: { skill: Skill; searchMatch?: boolean }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const cmd = skill.install_cmd || `clawhub install ${skill.name}`;
    navigator.clipboard.writeText(cmd);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="group flex items-start justify-between gap-4 border-b border-zinc-800/50 py-3 last:border-0 hover:bg-zinc-800/20">
      <div className="min-w-0 flex-1">
        <a
          href={`${CLAWHUB_SKILL_URL}/${encodeURIComponent(skill.name)}`}
          target="_blank"
          rel="noopener noreferrer"
          className="font-medium text-amber-400 hover:text-amber-300"
        >
          {skill.name}
        </a>
        {skill.grade && (skill.grade === "A" || skill.grade === "B") && (
          <span className="ml-2 rounded bg-emerald-500/20 px-1.5 py-0.5 text-xs text-emerald-400">
            {skill.grade}
          </span>
        )}
        <p className="mt-0.5 text-sm text-zinc-400">{skill.description || "No description"}</p>
      </div>
      <button
        onClick={handleCopy}
        className="shrink-0 rounded bg-zinc-700 px-2 py-1 text-xs font-medium opacity-0 transition group-hover:opacity-100 hover:bg-zinc-600"
      >
        {copied ? "Copied!" : "Copy install"}
      </button>
    </div>
  );
}

export function SkillList({ skills, loading }: SkillListProps) {
  const { groups, order } = groupByCategory(skills);

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center p-12">
        <p className="text-zinc-500">Loading skills...</p>
      </div>
    );
  }

  if (skills.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-4 p-12 text-center">
        <p className="text-zinc-500">No skills found.</p>
        <p className="text-sm text-zinc-600">
          Run <code className="rounded bg-zinc-800 px-2 py-1">skill-sync</code>{" "}
          and <code className="rounded bg-zinc-800 px-2 py-1">skill-audit</code>{" "}
          to build the registry.
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-4xl flex-1 px-6 py-8">
      <p className="mb-6 text-sm text-zinc-500">
        {skills.length} skills · Awesome-list style · Install: <code>clawhub install &lt;name&gt;</code>
      </p>
      {order.map((cat) => {
        const items = groups[cat] || [];
        if (items.length === 0) return null;
        return (
          <section key={cat} className="mb-8">
            <h2 className="mb-4 text-lg font-semibold text-zinc-200">{cat}</h2>
            <div className="rounded-lg border border-zinc-700/50 bg-zinc-900/30 px-4">
              {items
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((s) => (
                  <SkillRow key={s.name} skill={s} />
                ))}
            </div>
          </section>
        );
      })}
    </div>
  );
}
