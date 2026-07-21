"""prompt-lab — a tiny evaluation harness as a product.

Paste a prompt (with an {input} placeholder) and a few test cases (input + what a good output should
do); it runs the prompt on each, an independent judge scores pass/fail, and you get a pass-rate, the
common failure pattern, and a suggested better prompt. Its OWN eval checks the harness discriminates:
a good prompt must score higher than a bad one on the same cases."""

from .client import LLMClient
from .config import Settings
from .lab import PromptLab
from .models import CaseResult, LabResult, TestCase

__all__ = ["LLMClient", "Settings", "PromptLab", "CaseResult", "LabResult", "TestCase"]
