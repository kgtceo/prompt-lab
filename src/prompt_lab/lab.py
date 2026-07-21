"""The harness: run a prompt over test cases, grade each output, score, suggest a better prompt.

For each case: substitute {input} into the prompt, run it (candidate), then an independent judge
decides pass/fail against the case's expectation. The aggregate pass-rate is the honest measure of
the prompt — and the improver proposes a fix from the failure pattern.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from . import prompts
from .client import LLMClient
from .models import CaseResult, LabResult, TestCase


class _Verdict(BaseModel):
    passed: bool = Field(description="Did the output meet the expectation?")
    reason: str = Field(description="One-line justification.")


class _Improved(BaseModel):
    failure_summary: str = Field(description="The common failure pattern (or 'all passed').")
    improved_prompt: str = Field(description="A revised prompt that keeps the {input} placeholder.")


class PromptLab:
    def __init__(self, client: LLMClient) -> None:
        self._client = client

    def run(self, prompt: str, cases: list[TestCase]) -> LabResult:
        results: list[CaseResult] = []
        for c in cases:
            filled = prompt.replace("{input}", c.input)
            output = self._client.complete(user=filled)
            verdict = self._client.structured(
                schema=_Verdict,
                system=prompts.JUDGE_SYSTEM,
                user=prompts.judge_user(c.input, c.expectation, output),
            )
            results.append(
                CaseResult(input=c.input, expectation=c.expectation, output=output,
                           passed=verdict.passed, reason=verdict.reason)
            )

        passed = sum(1 for r in results if r.passed)
        total = len(results)
        improved = self._client.structured(
            schema=_Improved,
            system=prompts.IMPROVE_SYSTEM,
            user=prompts.improve_user(prompt, results),
        )
        return LabResult(
            prompt=prompt, results=results, passed=passed, total=total,
            pass_rate=round(passed / total, 3) if total else 0.0,
            failure_summary=improved.failure_summary, improved_prompt=improved.improved_prompt,
        )
