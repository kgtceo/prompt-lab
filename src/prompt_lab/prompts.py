"""Prompts for the judge (grades each candidate output) and the improver (suggests a better prompt)."""

JUDGE_SYSTEM = (
    "You grade a candidate LLM output against an expectation for a given input. Decide strictly "
    "whether the OUTPUT meets the EXPECTATION for that INPUT. Be objective: if the expectation says "
    "'one word' and the output is a sentence, that's a fail. Give a one-line reason."
)


def judge_user(input_: str, expectation: str, output: str) -> str:
    return (
        f"INPUT:\n{input_}\n\nEXPECTATION (what a good output should do):\n{expectation}\n\n"
        f"CANDIDATE OUTPUT:\n{output}\n\nDid the output meet the expectation?"
    )


IMPROVE_SYSTEM = (
    "You are a prompt engineer. Given a PROMPT template (it uses {input}) and the results of running "
    "it across test cases (which passed/failed and why), (1) summarise the common failure pattern in "
    "one or two lines, and (2) rewrite the prompt to fix it — keeping the {input} placeholder, being "
    "specific about the required output format/constraints the failures reveal. If everything passed, "
    "say so and return the prompt largely unchanged."
)


def improve_user(prompt: str, results: list) -> str:
    lines = []
    for r in results:
        mark = "PASS" if r.passed else "FAIL"
        lines.append(f"[{mark}] input={r.input!r} → {r.output[:120]!r} ({r.reason})")
    body = "\n".join(lines)
    return f"PROMPT:\n{prompt}\n\nRESULTS:\n{body}"
