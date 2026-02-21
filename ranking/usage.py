"""Auto-generate usage documentation for skills."""

from __future__ import annotations

from typing import Any, Optional


def generate_usage_doc(
    name: str,
    description: str,
    metadata: Optional[dict] = None,
    install_cmd: Optional[str] = None,
) -> str:
    """Generate USAGE.md content from skill metadata.

    Template: Install command, prerequisites (env, bins), example invocation.
    """
    meta = metadata or {}
    openclaw = meta.get("openclaw") or meta.get("metadata", {}).get("openclaw") or {}
    if isinstance(openclaw, str):
        openclaw = {}
    requires = openclaw.get("requires", {})
    env_vars = requires.get("env", [])
    bins = requires.get("bins", [])
    primary_env = openclaw.get("primaryEnv", "")

    cmd = install_cmd or f"clawhub install {name}"
    lines = [
        f"# {name}",
        "",
        description or "No description.",
        "",
        "## Install",
        "",
        "```bash",
        cmd,
        "```",
        "",
    ]

    if env_vars or bins or primary_env:
        lines.append("## Prerequisites")
        lines.append("")
        if env_vars:
            lines.append("**Environment variables:**")
            for v in env_vars:
                lines.append(f"- `{v}`")
            lines.append("")
        if primary_env and primary_env not in env_vars:
            lines.append(f"**Primary env:** `{primary_env}`")
            lines.append("")
        if bins:
            lines.append("**Required binaries:**")
            for b in bins:
                lines.append(f"- `{b}`")
            lines.append("")

    lines.extend([
        "## Usage",
        "",
        "Invoke the skill via OpenClaw's slash command or tool dispatch.",
        "",
    ])
    return "\n".join(lines)
