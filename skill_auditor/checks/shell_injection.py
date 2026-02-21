"""Check for shell injection and arbitrary code execution risks.

Flags use of subprocess with shell=True, os.system, eval, exec, and
dangerous deserialization (pickle.loads, yaml.load without Loader).
"""

from __future__ import annotations

import ast
import re
from typing import List

from .base import BaseCheck, CheckResult, Finding, Severity

_SHELL_PATTERNS = [
    (r"\bos\.system\s*\(", Severity.CRITICAL, "os.system() executes arbitrary shell commands"),
    (r"\bos\.popen\s*\(", Severity.HIGH, "os.popen() executes shell commands"),
    (r"subprocess\.(run|Popen|call|check_output)\s*\([^)]*shell\s*=\s*True", Severity.CRITICAL,
     "subprocess called with shell=True (shell injection risk)"),
    (r"\beval\s*\(", Severity.CRITICAL, "eval() executes arbitrary code"),
    (r"\bexec\s*\(", Severity.CRITICAL, "exec() executes arbitrary code"),
    (r"\bcompile\s*\(.*exec", Severity.HIGH, "compile+exec pattern executes dynamic code"),
    (r"pickle\.loads?\s*\(", Severity.CRITICAL, "pickle.load(s) deserializes untrusted data"),
    (r"yaml\.load\s*\([^)]*\)", Severity.HIGH,
     "yaml.load() without explicit Loader is unsafe (use yaml.safe_load)"),
    (r"jsonpickle\.decode\s*\(", Severity.HIGH, "jsonpickle.decode deserializes arbitrary objects"),
    (r"\b__import__\s*\(", Severity.HIGH, "Dynamic __import__() call"),
    (r"importlib\.import_module\s*\(", Severity.MEDIUM,
     "Dynamic importlib.import_module (verify the module name is trusted)"),
]


class ShellInjectionCheck(BaseCheck):
    check_id = "SHELL_INJECTION"
    description = (
        "Detects shell injection and arbitrary code execution risks: "
        "os.system, subprocess with shell=True, eval, exec, unsafe pickle/yaml."
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
            for pattern, severity, msg in _SHELL_PATTERNS:
                if re.search(pattern, line):
                    findings.append(
                        Finding(
                            check_id=self.check_id,
                            severity=severity,
                            message=msg,
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
