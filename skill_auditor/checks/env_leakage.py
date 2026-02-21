"""Check for environment variable and secret leakage.

Flags skills that read environment variables (which may contain API keys,
passwords, tokens) and potentially exfiltrate them.
"""

from __future__ import annotations

import re
from typing import List

from .base import BaseCheck, CheckResult, Finding, Severity

# Patterns that read from the environment
_ENV_READ_PATTERNS = [
    (r"os\.environ\b", "os.environ access"),
    (r"os\.getenv\s*\(", "os.getenv() call"),
    (r"os\.environ\.get\s*\(", "os.environ.get() call"),
    (r"dotenv\.load_dotenv\b|from dotenv import", "python-dotenv usage"),
]

# Secret-like variable name patterns
_SECRET_NAME_RE = re.compile(
    r"""(["']|=\s*os\.getenv\s*\(\s*["'])(API_KEY|SECRET|TOKEN|PASSWORD|PASSWD|PRIVATE_KEY|CREDENTIAL|AUTH|ACCESS_KEY|AWS_|OPENAI_|ANTHROPIC_)""",
    re.IGNORECASE,
)


class EnvLeakageCheck(BaseCheck):
    check_id = "ENV_LEAKAGE"
    description = (
        "Detects skills that read environment variables (potential secret/credential leakage). "
        "Secrets read from the environment should never be forwarded to external services."
    )

    def run(self, source_code: str, skill_metadata: dict) -> CheckResult:
        findings: List[Finding] = []
        if not source_code:
            return CheckResult(
                check_id=self.check_id,
                passed=True,
                findings=[],
                description=self.description,
            )

        lines = source_code.splitlines()
        for lineno, line in enumerate(lines, start=1):
            for pattern, reason in _ENV_READ_PATTERNS:
                if re.search(pattern, line):
                    # Escalate to HIGH if the variable looks like a secret
                    sev = (
                        Severity.HIGH
                        if _SECRET_NAME_RE.search(line)
                        else Severity.MEDIUM
                    )
                    findings.append(
                        Finding(
                            check_id=self.check_id,
                            severity=sev,
                            message=f"{reason} — verify secrets are not forwarded externally.",
                            line=lineno,
                            snippet=line.strip(),
                        )
                    )

        return CheckResult(
            check_id=self.check_id,
            passed=len(findings) == 0,
            findings=findings,
            description=self.description,
        )
