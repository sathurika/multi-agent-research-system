from typing import List, Optional

from pydantic import BaseModel, Field


class Source(BaseModel):
    title: str
    url: str
    content: str = ""


class ResearchFinding(BaseModel):
    claim: str
    evidence: str
    source_url: str


class ResearchAnalysis(BaseModel):
    findings: List[ResearchFinding] = Field(
        default_factory=list
    )


class AgentEvent(BaseModel):
    agent: str
    status: str
    message: str = ""


class AgentState(BaseModel):
    user_query: str

    status: str = "pending"
    error: Optional[str] = None

    sources: List[Source] = Field(default_factory=list)
    research_findings: List[ResearchFinding] = Field(
        default_factory=list
    )

    final_answer: Optional[str] = None

    step_count: int = 0
    research_attempts: int = 0

    verification_verdict: Optional[str] = None
    verification_reason: Optional[str] = None

    failed_findings: List[int] = Field(
        default_factory=list
    )

    execution_history: List[AgentEvent] = Field(
        default_factory=list
    )