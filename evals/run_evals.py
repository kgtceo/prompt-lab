"""Run prompt-lab's own eval — does the harness DISCRIMINATE?

A useful prompt-evaluator must give a clearly-good prompt a higher pass-rate than a clearly-bad
prompt on the same cases. For each task we run both prompts through prompt-lab and assert:
    pass_rate(good) > pass_rate(bad)  (and the good prompt passes most cases).
If the harness can't tell them apart, it isn't measuring anything.

    python evals/run_evals.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from anthropic import Anthropic

from prompt_lab.client import LLMClient
from prompt_lab.config import Settings
from prompt_lab.lab import PromptLab
from prompt_lab.models import TestCase

DATASET = Path(__file__).parent / "dataset" / "tasks.json"


def main() -> int:
    settings = Settings.from_env()
    lab = PromptLab(LLMClient(settings, Anthropic(api_key=settings.anthropic_api_key)))
    tasks = json.loads(DATASET.read_text())

    failures: list[str] = []
    for task in tasks:
        cases = [TestCase.model_validate(c) for c in task["cases"]]
        good = lab.run(task["good_prompt"], cases)
        bad = lab.run(task["bad_prompt"], cases)
        print(f"\n=== {task['name']} ===")
        print(f"  good pass-rate={good.pass_rate}  bad pass-rate={bad.pass_rate}")

        if not good.pass_rate > bad.pass_rate:
            failures.append(f"{task['name']}: harness didn't rank the good prompt above the bad one")
        if good.pass_rate < 0.99:
            failures.append(f"{task['name']}: the clearly-good prompt didn't pass all cases ({good.pass_rate})")

    print("\n" + "=" * 40)
    if failures:
        print(f"FAILED ({len(failures)}):")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print("HARNESS DISCRIMINATES ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
