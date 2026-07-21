"""Offline tests — the run loop, pass-rate aggregation, and {input} substitution."""

from __future__ import annotations

from conftest import FakeClient

from prompt_lab.lab import PromptLab
from prompt_lab.models import TestCase


def _cases():
    return [
        TestCase(input="loved it", expectation="one word: positive"),
        TestCase(input="hated it", expectation="one word: negative"),
    ]


def test_run_aggregates_pass_rate():
    # candidate returns "positive" for the loved case, a sentence for the hated one.
    outputs = {"loved it": "positive", "hated it": "I think it is quite negative overall."}
    # judge: pass if the output is a single word.
    judge = lambda user: (len(_extract_output(user).split()) == 1, "word check")
    client = FakeClient(outputs, judge, ("outputs too long", "Answer in ONE word: {input}"))
    result = PromptLab(client).run("Sentiment: {input}", _cases())
    assert result.total == 2
    assert result.passed == 1
    assert result.pass_rate == 0.5
    assert client.complete_calls == 2
    assert result.improved_prompt.startswith("Answer in ONE word")


def test_input_substitution():
    seen = {}
    outputs = {"loved it": "positive", "hated it": "negative"}
    judge = lambda user: (True, "ok")
    client = FakeClient(outputs, judge, ("", "x"))
    # wrap complete to capture the filled prompt
    orig = client.complete
    def capture(*, user, system="", model=None):
        seen["last"] = user
        return orig(user=user, system=system, model=model)
    client.complete = capture  # type: ignore
    PromptLab(client).run("Classify: {input}", [TestCase(input="loved it", expectation="x")])
    assert seen["last"] == "Classify: loved it"


def _extract_output(judge_user_text: str) -> str:
    # the judge prompt embeds "CANDIDATE OUTPUT:\n<output>\n\nDid the output..."
    marker = "CANDIDATE OUTPUT:\n"
    start = judge_user_text.index(marker) + len(marker)
    end = judge_user_text.index("\n\nDid the output", start)
    return judge_user_text[start:end]
