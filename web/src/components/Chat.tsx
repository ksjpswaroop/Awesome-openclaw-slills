"use client";

import { useState, useRef, useEffect } from "react";
import type { Skill } from "@/app/page";

type ChatProps = {
  skills: Skill[];
};

type Message = {
  role: "user" | "assistant";
  content: string;
};

export function Chat({ skills }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Ask me about OpenClaw skills. I can suggest skills for GitHub, weather, calendar, and more. Try: 'I need to integrate with GitHub' or 'What skills help with productivity?'",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    const text = input.trim();
    if (!text || loading) return;

    setInput("");
    setMessages((m) => [...m, { role: "user", content: text }]);
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          skills: skills.map((s) => ({
            name: s.name,
            description: s.description,
            install_cmd: s.install_cmd || `clawhub install ${s.name}`,
          })),
        }),
      });
      const data = (await res.json()) as { reply?: string };
      const reply =
        data.reply || "Sorry, I couldn't generate a response.";
      setMessages((m) => [...m, { role: "assistant", content: reply }]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: "Error: " + (err instanceof Error ? err.message : "Unknown"),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex w-full flex-col lg:max-w-2xl lg:mx-auto">
      <div className="flex flex-1 flex-col gap-4 overflow-y-auto p-6">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`rounded-lg px-4 py-3 ${
              msg.role === "user"
                ? "ml-8 bg-amber-500/10 text-amber-100"
                : "mr-8 bg-zinc-800/50 text-zinc-200"
            }`}
          >
            <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
          </div>
        ))}
        {loading && (
          <div className="mr-8 rounded-lg bg-zinc-800/50 px-4 py-3">
            <p className="text-sm text-zinc-400">Thinking...</p>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          send();
        }}
        className="border-t border-zinc-800 p-4"
      >
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about skills (e.g. GitHub, calendar...)"
            className="flex-1 rounded border border-zinc-700 bg-zinc-800/50 px-4 py-2 text-sm placeholder-zinc-500 focus:border-amber-500/50 focus:outline-none"
          />
          <button
            type="submit"
            disabled={loading}
            className="rounded bg-amber-500 px-4 py-2 text-sm font-medium text-zinc-950 hover:bg-amber-400 disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
