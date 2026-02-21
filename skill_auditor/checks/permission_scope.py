"""Check for overly-broad or undisclosed permission scopes.

Flags skills whose declared parameter list or description imply access to
sensitive resources (filesystem root, full contacts list, microphone, camera,
location, etc.) beyond what the task description requires.
"""

from __future__ import annotations

import re
from typing import List

from .base import BaseCheck, CheckResult, Finding, Severity

# Sensitive resource keywords that should appear in the description when used
_SENSITIVE_RESOURCES = {
    "filesystem": re.compile(r"\bopen\s*\(|os\.(listdir|walk|scandir|remove|rename|makedirs)\b|shutil\.", re.I),
    "location": re.compile(r"\bgps\b|\bgeolocation\b|\bGPS\b|device.location|navigator\.geolocation", re.I),
    "microphone/camera": re.compile(r"pyaudio|sounddevice|cv2\.VideoCapture|speech_recognition", re.I),
    "contacts/calendar": re.compile(r"contacts|vcards?|icalendar|\.ics\b", re.I),
    "clipboard": re.compile(r"pyperclip|tkinter\.Tk.*clipboard", re.I),
    "keylogging": re.compile(r"pynput|keyboard\.Listener|GetAsyncKeyState", re.I),
    "screen capture": re.compile(r"pyautogui\.screenshot|ImageGrab\.grab|mss\.mss", re.I),
}

# Broad glob / path patterns that suggest unrestricted FS access
_BROAD_PATH_RE = re.compile(r"""(["'/])(?:/{0,1}|C:\\\\|~){0,1}["']""")
_ROOT_PATH_RE = re.compile(r"""open\s*\(\s*["'](/|C:\\\\)""")


class PermissionScopeCheck(BaseCheck):
    check_id = "PERMISSION_SCOPE"
    description = (
        "Detects skills that access sensitive resources (filesystem, location, microphone, "
        "contacts, clipboard, screen) without disclosing these capabilities in their metadata."
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

        desc = (skill_metadata.get("description") or "").lower()
        lines = source_code.splitlines()

        for resource, pattern in _SENSITIVE_RESOURCES.items():
            for lineno, line in enumerate(lines, start=1):
                if pattern.search(line):
                    if resource.split("/")[0] not in desc:
                        findings.append(
                            Finding(
                                check_id=self.check_id,
                                severity=Severity.HIGH,
                                message=(
                                    f"Accesses '{resource}' but this is not disclosed "
                                    "in the skill description."
                                ),
                                line=lineno,
                                snippet=line.strip(),
                            )
                        )

        # Flag opening the filesystem root
        for lineno, line in enumerate(lines, start=1):
            if _ROOT_PATH_RE.search(line):
                findings.append(
                    Finding(
                        check_id=self.check_id,
                        severity=Severity.CRITICAL,
                        message="Skill opens a root-level filesystem path — overly broad access.",
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
