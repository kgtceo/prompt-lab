"""`prompt-lab` CLI — test a prompt against cases and get a scorecard + a better prompt.

    prompt-lab demo
    prompt-lab run --prompt-file p.txt --cases-file cases.json
"""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .client import LLMClient
from .config import Settings
from .lab import PromptLab
from .models import TestCase

app = typer.Typer(add_completion=False, help="Test a prompt against cases — pass-rate, failures, and a better prompt.")
console = Console()

_DEMO_PROMPT = "Classify the sentiment of this review: {input}"
_DEMO_CASES = [
    TestCase(input="I absolutely loved it, best purchase this year!", expectation="Exactly one word: positive"),
    TestCase(input="Terrible. Broke on day one.", expectation="Exactly one word: negative"),
    TestCase(input="It's fine, does the job.", expectation="Exactly one word: neutral"),
]


def _print(result) -> None:
    console.print(Panel(f"[bold]Pass rate: {int(result.pass_rate*100)}%[/]  ({result.passed}/{result.total})", border_style="cyan"))
    t = Table()
    t.add_column("✓"); t.add_column("Input"); t.add_column("Output"); t.add_column("Why")
    for r in result.results:
        t.add_row("[green]✓[/]" if r.passed else "[red]✗[/]", r.input[:32], r.output[:32], r.reason[:40])
    console.print(t)
    console.print(f"\n[bold]Failure pattern:[/] {result.failure_summary}")
    console.print(Panel(result.improved_prompt, title="Suggested prompt", border_style="green"))


def _run(prompt: str, cases: list[TestCase]) -> None:
    settings = Settings.from_env()
    with console.status("Running the prompt across cases…"):
        result = PromptLab(LLMClient(settings)).run(prompt, cases[: settings.max_cases])
    _print(result)


@app.callback()
def _root() -> None:
    """A tiny prompt evaluation harness."""


@app.command()
def demo() -> None:
    """Test a sentiment-classification prompt (that's too loose) against 3 cases."""
    _run(_DEMO_PROMPT, _DEMO_CASES)


@app.command()
def run(
    prompt_file: Path = typer.Option(..., "--prompt-file", help="File containing the prompt (uses {input})."),
    cases_file: Path = typer.Option(..., "--cases-file", help="JSON list of {input, expectation}."),
) -> None:
    prompt = prompt_file.read_text(encoding="utf-8")
    cases = [TestCase.model_validate(c) for c in json.loads(cases_file.read_text())]
    _run(prompt, cases)


if __name__ == "__main__":
    app()
