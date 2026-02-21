import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const { message, skills } = (await req.json()) as {
      message: string;
      skills: Array<{ name: string; description?: string; install_cmd?: string }>;
    };
    const topSkills = (skills || [])
      .slice(0, 10)
      .map(
        (s) =>
          `- **${s.name}**: ${s.description || "No description"} | Install: \`${s.install_cmd || `clawhub install ${s.name}`}\``
      )
      .join("\n");

    const systemPrompt = `You are a helpful assistant for the OpenClaw skills registry. 
Users can install skills with: clawhub install <skill-name>

Available skills (top 10 for context):
${topSkills || "No skills loaded."}

When the user asks for a skill (e.g. "GitHub integration", "weather", "calendar"), suggest relevant skills from the list and provide the install command.`;

    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      return NextResponse.json({
        reply:
          "Chat API key not configured. Set OPENAI_API_KEY. Meanwhile: browse skills above and use 'clawhub install <skill-name>' to install.",
      });
    }

    const res = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: message },
        ],
        max_tokens: 500,
      }),
    });

    const data = (await res.json()) as { choices?: Array<{ message?: { content?: string } }> };
    const reply =
      data.choices?.[0]?.message?.content ||
      "Sorry, I could not generate a response.";
    return NextResponse.json({ reply });
  } catch (err) {
    return NextResponse.json(
      { reply: "Error: " + (err instanceof Error ? err.message : "Unknown") },
      { status: 500 }
    );
  }
}
