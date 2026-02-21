# Awesome OpenClaw Skills

> **`skill-audit`** — static analysis and safety-scoring for LLM agent skills.
> Like **npm audit**, but for AI tools.

There are already 5,700+ skills in one hub and 3,000+ in another curated list.
The problem is **vetting** — Cisco research showed that third-party skills can perform
silent data exfiltration.  This tool statically analyses Python and JSON skill definitions
and scores them on a 0–100 safety scale so you can quickly identify dangerous skills
before deploying them in your agent.

---

## Philosophy: Why We're Doing This

**Trust through transparency.** AI agents are only as safe as the skills they run. The ClawHavoc incident (341 malicious skills) proved that unvetted third-party code is a real risk. We believe:

1. **Users deserve to know what they install.** Skills can exfiltrate data, execute arbitrary commands, or leak secrets. Static analysis surfaces these risks before they run.

2. **The ecosystem needs a safety layer.** Like `npm audit` for JavaScript, we need a standard way to score and rank skills. This project is that layer for OpenClaw.

3. **Open is better.** All checks, scores, and methodologies are open and auditable. No black boxes. No vendor lock-in. Community can extend, critique, and improve.

4. **One place to discover, vet, and use.** Instead of scattered wikis and opaque registries, we're building the **holy grail** — a unified index where skills are verified, ranked, documented, and usable. Browse, chat, rate, install.

5. **Incremental beats perfect.** Thousands of tasks. We work through them one by one, with a backlog that grows and shrinks as the project evolves.

---

## Project Status

- **Phase 4 MVP complete**: skill-audit, skill-sync, ranking, web app (browse, search, chat, rate, ClawHub links)
- **Phase 5 in progress**: comments, reports, auth, deployment
- See [docs/BACKLOG.md](docs/BACKLOG.md) for full task list

---

## Features

| Check | What it catches | Severity |
|---|---|---|
| **DATA_EXFIL** | HTTP POST/PUT to external URLs, base64 payload obfuscation, SMTP, DNS exfiltration | CRITICAL |
| **NETWORK_ACCESS** | Undisclosed outbound HTTP/socket calls | HIGH |
| **PERMISSION_SCOPE** | Undisclosed filesystem, clipboard, keylogging, screen-capture, microphone/camera access | HIGH–CRITICAL |
| **SHELL_INJECTION** | `os.system`, `subprocess(shell=True)`, `eval`, `exec`, unsafe `pickle.loads`, `yaml.load` | CRITICAL |
| **ENV_LEAKAGE** | Reading `os.environ` / `os.getenv` — especially API keys, tokens, passwords | MEDIUM–HIGH |

### Safety Score

Each finding deducts penalty points from a 100-point baseline:

| Severity | Penalty |
|---|---|
| CRITICAL | −30 pts |
| HIGH | −15 pts |
| MEDIUM | −7 pts |
| LOW | −2 pts |

Scores map to letter grades: **A** (90–100) · **B** (75–89) · **C** (60–74) · **D** (40–59) · **F** (<40).

---

## Quick Start

### Install

```bash
pip install -e .
```

### Audit a single skill file

```bash
skill-audit path/to/my_skill.py
```

### Audit a directory of skills

```bash
skill-audit skills/
```

### Audit SKILL.md directories (AgentSkills format)

```bash
skill-audit path/to/skill_with_SKILL_md/
```

### Ranked output (composite score + tier)

```bash
skill-audit skills/ --rank
```

### Output as JSON (machine-readable)

```bash
skill-audit skills/ --format json
```

### Show only failing skills (CI-friendly)

```bash
skill-audit skills/ --fail-only
```

### Non-blocking CI mode (collect reports without failing the build)

```bash
skill-audit skills/ --exit-zero
```

---

## Skill Formats

### Python (`.py`)

Place a `__skill__` dict at module level to provide metadata, and a module docstring as the description:

```python
"""Fetches current weather via Open-Meteo (HTTP GET only)."""

__skill__ = {
    "name": "get_weather",
    "description": "Fetches weather for a city using the Open-Meteo HTTP API.",
    "parameters": { ... },
}

def get_weather(city: str) -> dict:
    ...
```

### JSON (`.json`)

OpenAI-style function definitions, optionally with an embedded `source` key containing inline Python:

```json
{
  "name": "calculator",
  "description": "Evaluates a math expression. No network, no filesystem.",
  "parameters": { ... },
  "source": "def calculator(expression): ..."
}
```

---

## Example Output

```
────────────────────────────────────────────────────────────
Skill: summarise_document  │  Safety Score: 0/100  Grade: F
  Findings — CRITICAL: 6  HIGH: 5  MEDIUM: 0  LOW: 0
────────────────────────────────────────────────────────────

  [✘ FAIL] DATA_EXFIL
        • CRITICAL (line 40): Data sent to external URL: 'https://evil-attacker.example.com/collect'

  [✘ FAIL] SHELL_INJECTION
        • CRITICAL (line 46): subprocess called with shell=True (shell injection risk)

  [✘ FAIL] ENV_LEAKAGE
        • HIGH (line 36): os.getenv() call — verify secrets are not forwarded externally.

────────────────────────────────────────────────────────────
  Overall verdict: UNSAFE
────────────────────────────────────────────────────────────

════════════════════════════════════════════════════════════
  Skill Audit Summary  (3 skill(s) scanned)
════════════════════════════════════════════════════════════

  ✔ SAFE    get_weather       96/100  A  C:0 H:0 M:0 L:2
  ✘ UNSAFE  summarise_document 0/100  F  C:6 H:5 M:0 L:0
  ✔ SAFE    calculator       100/100  A  C:0 H:0 M:0 L:0

  2 safe, 1 unsafe out of 3 skills.
```

---

## Project Structure

```
skill_auditor/           # Core audit engine
├── __init__.py
├── analyzer.py          # SkillAnalyzer — .py, .json, SKILL.md directories
├── scorer.py            # SafetyScore — 0–100, grade A–F
├── report.py            # Report — text and JSON output
├── cli.py               # skill-audit command-line tool
├── adapters/
│   └── skill_md.py      # AgentSkills SKILL.md parsing
└── checks/              # Security checks (DATA_EXFIL, SHELL_INJECTION, etc.)

ingestion/               # Skill sync from ClawHub and local sources
├── sync.py              # skill-sync — populate skills_index
├── clawhub_fetch.py     # ClawHub API/CLI fetch
└── schema.py            # SkillRecord schema

ranking/                 # Composite scoring and usage docs
├── engine.py            # Rank by safety, format, doc, community
├── usage.py             # Auto-generate USAGE.md
└── registry.py          # Write registry.json

evaluation/              # Verification and regression tests
├── fixtures/            # Known-safe and known-unsafe skills
├── test_static.py       # Audit fixture regression
└── test_schema.py       # AgentSkills format validation

web/                     # Next.js app — browse, chat, rate, use
docs/
├── BACKLOG.md           # Task backlog (phases 1–5)
├── PROJECT_STATUS.md    # Current status snapshot
skills_index/            # Synced skills and registry (generated)
```

### SKILL.md (AgentSkills format)

Audit directories containing `SKILL.md`:

```bash
skill-audit path/to/skill_dir/
skill-audit examples/skills/ --rank
```

### Sync and registry

```bash
skill-sync                           # Sync from ClawHub (CLI) + local
skill-sync --no-clawhub              # Local only
skill-sync --incremental             # Delta merge with existing
skill-sync --clawhub-limit 500       # Fetch more from ClawHub
python scripts/build_registry.py     # Audit + rank → registry.json
```

**ClawHub fetch**: Set `CLAWHUB_API_URL` for HTTP API, or use `clawhub` CLI (installed separately).

### Web app

```bash
cd web && npm install && npm run dev
# Open http://localhost:3000 — browse, search, chat, rate, copy install cmd
```

---

## Running Tests

```bash
pip install -e ".[dev]"
pytest
```

---

## Extending with Custom Checks

```python
from skill_auditor.checks.base import BaseCheck, CheckResult, Finding, Severity

class MyCustomCheck(BaseCheck):
    check_id = "MY_CHECK"
    description = "Catches my specific anti-pattern."

    def run(self, source_code, skill_metadata):
        findings = []
        if "bad_function(" in source_code:
            findings.append(Finding(
                check_id=self.check_id,
                severity=Severity.HIGH,
                message="bad_function() is not allowed.",
            ))
        return CheckResult(
            check_id=self.check_id,
            passed=len(findings) == 0,
            findings=findings,
            description=self.description,
        )

# Use it with the analyzer
from skill_auditor import SkillAnalyzer
from skill_auditor.checks import ALL_CHECKS

analyzer = SkillAnalyzer(checks=ALL_CHECKS + [MyCustomCheck])
result = analyzer.analyze_file("my_skill.py")
```

---

## License

MIT
