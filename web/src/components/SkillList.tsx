"use client";

import { useState } from "react";
import type { Skill } from "@/app/page";

type SkillListProps = {
  skills: Skill[];
  loading: boolean;
};

const CLAWHUB_SKILL_URL = "https://clawhub.ai/skills";

function SkillCard({ skill }: { skill: Skill }) {
  const [copied, setCopied] = useState(false);
  const [stars, setStars] = useState(0);

  const handleCopy = () => {
    const cmd = skill.install_cmd || `clawhub install ${skill.name}`;
    navigator.clipboard.writeText(cmd);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <article className="rounded-lg border border-zinc-700 bg-zinc-900/30 p-4 transition hover:border-zinc-600">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-zinc-100 truncate">{skill.name}</h3>
          <p className="mt-1 line-clamp-2 text-sm text-zinc-400">
            {skill.description || "No description"}
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            <span
              className={`rounded px-2 py-0.5 text-xs font-medium ${
                skill.grade === "A"
                  ? "bg-emerald-500/20 text-emerald-400"
                  : skill.grade === "B"
                    ? "bg-amber-500/20 text-amber-400"
                    : "bg-zinc-600/50 text-zinc-400"
              }`}
            >
              Grade {skill.grade}
            </span>
            <span className="rounded bg-zinc-700/50 px-2 py-0.5 text-xs text-zinc-400">
              {skill.tier}
            </span>
          </div>
        </div>
        <div className="flex flex-col items-end gap-2">
          <button
            onClick={() => setStars((s) => (s >= 5 ? 0 : s + 1))}
            className="text-amber-400 hover:text-amber-300"
            title="Rate"
          >
            {"★".repeat(stars)}{"☆".repeat(5 - stars)}
          </button>
          <div className="flex gap-1">
            <a
              href={`${CLAWHUB_SKILL_URL}/${encodeURIComponent(skill.name)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded bg-zinc-700 px-3 py-1.5 text-xs font-medium hover:bg-zinc-600"
            >
              View
            </a>
            <button
              onClick={handleCopy}
              className="rounded bg-zinc-700 px-3 py-1.5 text-xs font-medium hover:bg-zinc-600"
            >
              {copied ? "Copied!" : "Copy Install"}
            </button>
          </div>
        </div>
      </div>
      <div className="mt-3 text-xs text-zinc-500">
        {skill.install_cmd || `clawhub install ${skill.name}`}
      </div>
    </article>
  );
}

export function SkillList({ skills, loading }: SkillListProps) {
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
    <div className="mx-auto w-full max-w-6xl flex-1 px-6 py-8">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {skills.map((s) => (
          <SkillCard key={s.name} skill={s} />
        ))}
      </div>
    </div>
  );
}
