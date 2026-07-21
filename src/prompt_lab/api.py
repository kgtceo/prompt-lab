"""FastAPI wrapper: prompt + test cases → scorecard + a suggested better prompt."""

from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import Settings
from .lab import PromptLab
from .models import LabResult, TestCase

app = FastAPI(title="prompt-lab", version="1.0.0")

_env_origins = [o.strip() for o in os.getenv("PL_CORS_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_env_origins,
    allow_origin_regex=r"https://prompt-lab[a-z0-9-]*\.vercel\.app|http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)

_EXAMPLE = {
    "prompt": "Classify the sentiment of this review: {input}",
    "cases": [
        {"input": "I absolutely loved it, best purchase this year!", "expectation": "Exactly one word: positive"},
        {"input": "Terrible. Broke on day one.", "expectation": "Exactly one word: negative"},
        {"input": "It's fine, does the job.", "expectation": "Exactly one word: neutral"},
    ],
}


class RunRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=8000)
    cases: list[TestCase] = Field(..., min_length=1, max_length=12)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/example")
def example() -> dict:
    return _EXAMPLE


@app.post("/api/run")
def run(req: RunRequest) -> LabResult:
    if "{input}" not in req.prompt:
        raise HTTPException(status_code=400, detail="Prompt must contain the {input} placeholder.")
    try:
        settings = Settings.from_env()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    from .client import LLMClient

    return PromptLab(LLMClient(settings)).run(req.prompt, req.cases[: settings.max_cases])
