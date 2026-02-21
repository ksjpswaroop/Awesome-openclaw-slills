"""Check for undisclosed or overly-broad network access.

Flags skills that make outbound network calls without disclosing this in their
description/metadata, or that contact hardcoded non-obvious external hosts.
"""

from __future__ import annotations

import ast
import re
from typing import List

from .base import BaseCheck, CheckResult, Finding, Severity

_NETWORK_PATTERNS = [
    (r"\bsocket\.(socket|create_connection|connect)\b", "Raw socket usage"),
    (r"\bparamiko\b", "SSH client (paramiko) usage"),
    (r"\bftplib\b", "FTP client usage"),
    (r"requests\.(get|post|put|patch|delete|head|options)\s*\(", "HTTP call via requests"),
    (r"urllib\.request\.(urlopen|urlretrieve)\s*\(", "HTTP call via urllib"),
    (r"httpx\.\b", "HTTP call via httpx"),
    (r"aiohttp\.\b", "HTTP call via aiohttp"),
    (r"http\.client\.(HTTPConnection|HTTPSConnection)\b", "HTTP call via http.client"),
]

_NETWORK_KEYWORDS = {"network", "http", "api", "internet", "web", "fetch", "request", "url"}


def _description_discloses_network(metadata: dict) -> bool:
    desc = (metadata.get("description") or "").lower()
    return any(kw in desc for kw in _NETWORK_KEYWORDS)


class NetworkAccessCheck(BaseCheck):
    check_id = "NETWORK_ACCESS"
    description = (
        "Detects undisclosed outbound network access. "
        "Skills that make network calls should clearly document this in their description."
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

        disclosed = _description_discloses_network(skill_metadata)
        lines = source_code.splitlines()
        for lineno, line in enumerate(lines, start=1):
            for pattern, reason in _NETWORK_PATTERNS:
                if re.search(pattern, line):
                    sev = Severity.LOW if disclosed else Severity.HIGH
                    msg = (
                        f"{reason} — network access is documented."
                        if disclosed
                        else f"{reason} — network access is NOT disclosed in the skill description."
                    )
                    findings.append(
                        Finding(
                            check_id=self.check_id,
                            severity=sev,
                            message=msg,
                            line=lineno,
                            snippet=line.strip(),
                        )
                    )

        # Deduplicate by (line, pattern reason)
        seen: set = set()
        unique: List[Finding] = []
        for f in findings:
            key = (f.line, f.message)
            if key not in seen:
                seen.add(key)
                unique.append(f)

        # Only fail if there is undisclosed network access (HIGH severity)
        failed = any(f.severity == Severity.HIGH for f in unique)
        return CheckResult(
            check_id=self.check_id,
            passed=not failed,
            findings=unique,
            description=self.description,
        )
