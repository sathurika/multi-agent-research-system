from pydantic import BaseModel, Field


class Source(BaseModel):
    title: str
    url: str
    snippet: str


class ResearchFinding(BaseModel):
    claim: str
    evidence: str
    source_url: str


class ResearchAnalysis(BaseModel):
    findings: list[ResearchFinding]


class AgentState(BaseModel):
    user_query: str
    status: str = "starting"
    step_count: int = 0
    sources: list[Source] = Field(default_factory=list)
    research_findings: list[ResearchFinding] = Field(default_factory=list)
    final_answer: str = ""
    error: str = ""
