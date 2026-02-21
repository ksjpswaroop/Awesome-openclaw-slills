"""Fetch skill list from ClawHub (API or CLI fallback)."""

from __future__ import annotations

import json
import os
import subprocess
import urllib.request
from typing import Optional

# Override via CLAWHUB_API_URL env (e.g. https://<deployment>.convex.site)
# ClawHub Convex deployment - verify at https://clawhub.ai or openclaw/clawhub repo
DEFAULT_API_BASE = ""


def fetch_skills_via_api(
    base_url: Optional[str] = None,
    limit: int = 500,
) -> list[dict]:
    """Fetch skills from ClawHub HTTP API.

    Tries ApiRoutes.skills (GET) or ApiRoutes.search (GET) endpoints.
    Returns [] if API is unavailable. Set CLAWHUB_API_URL env for API base.
    """
    base = base_url or os.environ.get("CLAWHUB_API_URL") or DEFAULT_API_BASE
    if not base:
        return []
    base = base.rstrip("/")

    # Try list endpoint: /api/skills or /api/v1/skills
    for path in ["/api/skills", "/api/v1/skills"]:
        try:
            url = f"{base}{path}?limit={limit}"
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                if isinstance(data, list):
                    return data
                if isinstance(data, dict):
                    items = data.get("skills", data.get("items", data.get("data", [])))
                    if isinstance(items, list):
                        return items
        except Exception:
            continue

    # Try search with empty query
    for path in ["/api/search", "/api/v1/search"]:
        try:
            url = f"{base}{path}?q=&limit={limit}"
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                if isinstance(data, dict):
                    items = data.get("skills", data.get("results", data.get("items", [])))
                    if isinstance(items, list):
                        return items
                if isinstance(data, list):
                    return data
        except Exception:
            continue

    return []


def fetch_skills_via_cli(limit: int = 200) -> list[dict]:
    """Fetch skills via clawhub CLI. Returns [] if CLI missing or fails."""
    try:
        # clawhub search "" --limit N --format json (if supported)
        result = subprocess.run(
            ["clawhub", "search", "", "--limit", str(limit)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            return []
        out = result.stdout.strip()
        if not out:
            return []
        data = json.loads(out)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("skills", data.get("results", data.get("items", [])))
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return []


def fetch_clawhub_skills(
    limit: int = 500,
    prefer_api: bool = True,
) -> list[dict]:
    """Fetch skills from ClawHub. Tries API first, then CLI.

    Returns list of skill dicts with at least: name, description.
    """
    skills: list[dict] = []
    if prefer_api:
        skills = fetch_skills_via_api(limit=limit)
    if not skills:
        skills = fetch_skills_via_cli(limit=limit)
    if not skills and not prefer_api:
        skills = fetch_skills_via_api(limit=limit)
    return skills
