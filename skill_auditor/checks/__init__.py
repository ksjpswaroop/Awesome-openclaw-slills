"""Individual security checks for LLM skill analysis."""

from .data_exfiltration import DataExfiltrationCheck
from .network_access import NetworkAccessCheck
from .permission_scope import PermissionScopeCheck
from .shell_injection import ShellInjectionCheck
from .env_leakage import EnvLeakageCheck

ALL_CHECKS = [
    DataExfiltrationCheck,
    NetworkAccessCheck,
    PermissionScopeCheck,
    ShellInjectionCheck,
    EnvLeakageCheck,
]

__all__ = [
    "DataExfiltrationCheck",
    "NetworkAccessCheck",
    "PermissionScopeCheck",
    "ShellInjectionCheck",
    "EnvLeakageCheck",
    "ALL_CHECKS",
]
