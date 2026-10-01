from typing import Literal

from pydantic import BaseModel, Field


class Source(BaseModel):
    title: str
    url: str
    snippet: str = ""


class ResearchFinding(BaseModel):
    claim: str
    evidence: str
    source_url: str


class VerificationResult(BaseModel):
    passed: bool
    score: float = Field(ge=0.0, le=1.0)
    issues: list[str] = Field(default_factory=list)
    feedback: str = ""


class AgentState(BaseModel):
    user_query: str

    research_findings: list[ResearchFinding] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)

    draft: str = ""

    verification: VerificationResult | None = None

    retry_count: int = 0
    step_count: int = 0

    status: Literal[
        "pending",
        "researching",
        "writing",
        "verifying",
        "completed",
        "failed",
    ] = "pending"

    error: str | None = None