"""Typed contracts for prompt-lab.

A prompt template (with an {input} placeholder) is run against a set of test cases; each output is
graded by a judge against that case's expectation. The result is a scorecard + a suggested better
prompt — a small evaluation harness turned into a product.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class TestCase(BaseModel):
    __test__ = False  # this is a data model, not a pytest test class
    input: str = Field(description="The value substituted for {input} in the prompt.")
    expectation: str = Field(description="What a good output should do/contain for this input.")


class CaseResult(BaseModel):
    input: str
    expectation: str
    output: str
    passed: bool
    reason: str = Field(description="Why the judge passed/failed this output.")


class LabResult(BaseModel):
    prompt: str
    results: list[CaseResult] = Field(default_factory=list)
    passed: int = 0
    total: int = 0
    pass_rate: float = 0.0
    failure_summary: str = Field(default="", description="The common failure pattern across cases.")
    improved_prompt: str = Field(default="", description="A suggested prompt likely to score higher.")
