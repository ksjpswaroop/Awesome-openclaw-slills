# Awesome OpenClaw Skills — Vetting Tool

> **`skill-audit`** — static analysis and safety-scoring for LLM agent skills.
> Like **npm audit**, but for AI tools.

There are already 5,700+ skills in one hub and 3,000+ in another curated list.
The problem is **vetting** — Cisco research showed that third-party skills can perform
silent data exfiltration.  This tool statically analyses Python and JSON skill definitions
and scores them on a 0–100 safety scale so you can quickly identify dangerous skills
before deploying them in your agent.

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
skill_auditor/
├── __init__.py          # Public API
├── analyzer.py          # SkillAnalyzer — loads skills and runs checks
├── scorer.py            # SafetyScore — converts findings into a 0–100 score
├── report.py            # Report — text and JSON output
├── cli.py               # skill-audit command-line tool
└── checks/
    ├── base.py              # BaseCheck, Finding, CheckResult, Severity
    ├── data_exfiltration.py # DATA_EXFIL check
    ├── network_access.py    # NETWORK_ACCESS check
    ├── permission_scope.py  # PERMISSION_SCOPE check
    ├── shell_injection.py   # SHELL_INJECTION check
    └── env_leakage.py       # ENV_LEAKAGE check

examples/skills/
├── safe_weather_skill.py        # Safe — GET-only, documented network access
├── safe_calculator_skill.json   # Safe — pure computation, no external calls
└── unsafe_malicious_skill.py    # UNSAFE — exfiltration + shell + env leakage demo

tests/
├── test_checks.py    # Unit tests for each individual check
└── test_analyzer.py  # Integration tests for SkillAnalyzer, SafetyScore, Report, CLI
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
