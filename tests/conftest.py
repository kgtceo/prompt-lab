"""Offline test doubles — a fake client with both complete() and structured()."""

from __future__ import annotations

import pytest

from prompt_lab.config import Settings


class FakeClient:
    """Scripts candidate outputs (by input substring) and a fixed judge verdict fn."""

    def __init__(self, outputs: dict[str, str], judge, improved) -> None:
        self._outputs = outputs
        self._judge = judge          # (input, expectation, output) -> (passed, reason)
        self._improved = improved    # (failure_summary, improved_prompt)
        self.complete_calls = 0

    def complete(self, *, user: str, system: str = "", model=None) -> str:
        self.complete_calls += 1
        for key, out in self._outputs.items():
            if key in user:
                return out
        return "(no scripted output)"

    def structured(self, *, schema, system, user, model=None):
        # Distinguish the judge schema from the improver schema by field names.
        fields = set(schema.model_fields)
        if "passed" in fields:
            # crude: recover the output from the user text isn't needed — the judge fn is keyed on it
            passed, reason = self._judge(user)
            return schema(passed=passed, reason=reason)
        return schema(failure_summary=self._improved[0], improved_prompt=self._improved[1])


@pytest.fixture
def settings() -> Settings:
    return Settings(anthropic_api_key="test-key")
