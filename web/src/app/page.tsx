"use client";

import { useState, useEffect } from "react";
import { SkillList } from "@/components/SkillList";
import { Chat } from "@/components/Chat";
import { Header } from "@/components/Header";

export type Skill = {
  name: string;
  description?: string;
  category?: string;
  grade: string;
  tier: string;
  safety_score: number;
  composite_score: number;
  install_cmd?: string;
  usage_summary?: string;
};

export default function Home() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState<"browse" | "chat">("browse");

  useEffect(() => {
    fetch("/api/skills")
      .then((res) => res.json())
      .then((data) => {
        setSkills(Array.isArray(data) ? data : data.skills || []);
      })
      .catch(() => setSkills([]))
      .finally(() => setLoading(false));
  }, []);

  const filteredSkills = skills.filter((s) => {
    const matchFilter =
      filter === "all" ||
      (filter === "tier" && s.tier === "featured") ||
      (filter === "trusted" && s.tier === "trusted") ||
      (filter === "grade" && s.grade === "A");
    const matchSearch =
      !searchQuery ||
      s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (s.description || "").toLowerCase().includes(searchQuery.toLowerCase());
    return matchFilter && matchSearch;
  }).sort((a, b) => (b.composite_score || 0) - (a.composite_score || 0));

  return (
    <div className="flex min-h-screen flex-col">
      <Header
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        filter={filter}
        onFilterChange={setFilter}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />
      <main className="flex flex-1">
        {activeTab === "browse" ? (
          <SkillList skills={filteredSkills} loading={loading} />
        ) : (
          <Chat skills={skills} />
        )}
      </main>
    </div>
  );
}
