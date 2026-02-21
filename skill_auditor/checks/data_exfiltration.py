"""Check for patterns indicative of silent data exfiltration.

Looks for:
- HTTP POST/PUT/PATCH calls to external URLs inside the skill body
- Base64-encoding of data prior to a network call
- Writing data to files that are subsequently uploaded
"""

from __future__ import annotations

import ast
import re
from typing import List

from .base import BaseCheck, CheckResult, Finding, Severity

# Patterns that suggest data is being shipped out silently
_EXFIL_PATTERNS = [
    # urllib / requests POST
    (r"requests\.(post|put|patch)\s*\(", "HTTP write call via requests"),
    (r"urllib\.request\.urlopen\s*\(.*data\s*=", "urllib.request.urlopen with data payload"),
    # httpx async
    (r"httpx\.(post|put|patch|AsyncClient)\b", "HTTP write call via httpx"),
    # aiohttp
    (r"aiohttp\.(ClientSession|post|put)\b", "HTTP write call via aiohttp"),
    # websocket send
    (r"\.send\s*\(\s*(json|data|payload)", "websocket/socket send of payload"),
    # base64 encode + network
    (r"base64\.(b64encode|encodebytes)", "base64 encoding (possible payload obfuscation)"),
    # smtp
    (r"smtplib\.SMTP\b", "SMTP email (potential data exfiltration channel)"),
    # dns exfil
    (r"socket\.gethostbyname\s*\(", "DNS lookup (potential DNS exfiltration)"),
]


def _find_pattern_findings(source: str, check_id: str) -> List[Finding]:
    findings: List[Finding] = []
    lines = source.splitlines()
    for lineno, line in enumerate(lines, start=1):
        for pattern, reason in _EXFIL_PATTERNS:
            if re.search(pattern, line):
                findings.append(
                    Finding(
                        check_id=check_id,
                        severity=Severity.CRITICAL,
                        message=f"Possible data exfiltration: {reason}",
                        line=lineno,
                        snippet=line.strip(),
                    )
                )
    return findings


def _ast_exfil_findings(source: str, check_id: str) -> List[Finding]:
    """Walk the AST to find POST/PUT calls with external URLs in string literals."""
    findings: List[Finding] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return findings

    external_url_re = re.compile(r"https?://(?!localhost|127\.0\.0\.1|::1)", re.IGNORECASE)

    class _Visitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
            # Look for requests.post / requests.put / requests.patch calls
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in ("post", "put", "patch"):
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if external_url_re.search(arg.value):
                            findings.append(
                                Finding(
                                    check_id=check_id,
                                    severity=Severity.CRITICAL,
                                    message=(
                                        f"Data sent to external URL: {arg.value!r}"
                                    ),
                                    line=node.lineno,
                                    snippet=ast.unparse(node)[:120],
                                )
                            )
            self.generic_visit(node)

    _Visitor().visit(tree)
    return findings


class DataExfiltrationCheck(BaseCheck):
    check_id = "DATA_EXFIL"
    description = (
        "Detects patterns that may silently send user or system data to external endpoints "
        "(HTTP write calls, DNS exfiltration, SMTP, base64 payload obfuscation)."
    )

    def run(self, source_code: str, skill_metadata: dict) -> CheckResult:
        findings: List[Finding] = []
        if source_code:
            findings.extend(_find_pattern_findings(source_code, self.check_id))
            findings.extend(_ast_exfil_findings(source_code, self.check_id))
        return CheckResult(
            check_id=self.check_id,
            passed=len(findings) == 0,
            findings=findings,
            description=self.description,
        )
