"""Awesome OpenClaw Skills — static analysis and safety-scoring tool for LLM agent skills."""

from .analyzer import SkillAnalyzer
from .scorer import SafetyScore
from .report import Report

__all__ = ["SkillAnalyzer", "SafetyScore", "Report"]
__version__ = "0.1.0"
