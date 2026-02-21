"use client";

type Tab = "browse" | "chat";

type HeaderProps = {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  filter: string;
  onFilterChange: (f: string) => void;
  activeTab: Tab;
  onTabChange: (t: Tab) => void;
};

export function Header({
  searchQuery,
  onSearchChange,
  filter,
  onFilterChange,
  activeTab,
  onTabChange,
}: HeaderProps) {
  return (
    <header className="border-b border-zinc-800 bg-zinc-900/50 px-6 py-4">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-xl font-bold text-amber-400">
          Awesome OpenClaw Skills
        </h1>
        <div className="flex gap-2">
          <button
            onClick={() => onTabChange("browse")}
            className={`rounded px-4 py-2 text-sm font-medium transition ${
              activeTab === "browse"
                ? "bg-amber-500/20 text-amber-400"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Browse
          </button>
          <button
            onClick={() => onTabChange("chat")}
            className={`rounded px-4 py-2 text-sm font-medium transition ${
              activeTab === "chat"
                ? "bg-amber-500/20 text-amber-400"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Chat
          </button>
        </div>
      </div>
      <div className="mx-auto mt-4 flex max-w-6xl flex-col gap-4 sm:flex-row sm:items-center">
        <input
          type="search"
          placeholder="Search skills..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="rounded border border-zinc-700 bg-zinc-800/50 px-4 py-2 text-sm placeholder-zinc-500 focus:border-amber-500/50 focus:outline-none"
        />
        <select
          value={filter}
          onChange={(e) => onFilterChange(e.target.value)}
          className="rounded border border-zinc-700 bg-zinc-800/50 px-4 py-2 text-sm focus:border-amber-500/50 focus:outline-none"
        >
          <option value="all">All</option>
          <option value="tier">Featured</option>
          <option value="trusted">Trusted</option>
          <option value="grade">Grade A</option>
        </select>
      </div>
    </header>
  );
}
