from langchain_openai import ChatOpenAI

from config.settings import get_settings
from models.schemas import (
    AgentEvent,
    AgentState,
    ResearchAnalysis,
    ResearchFinding,
    Source,
)
from tools.search_tool import search_web


def get_llm() -> ChatOpenAI:
    """Create the LLM client using the configured OpenRouter settings."""

    settings = get_settings()

    return ChatOpenAI(
        
        model=settings.model_name,
        api_key=settings.openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
    )


def research(state: AgentState) -> AgentState:
    """
    Research the user's question.

    The agent:
    1. Searches the web.
    2. Sends the search results to the LLM.
    3. Extracts individual claims.
    4. Requires each finding to contain its own evidence.
    5. Associates every finding with a source.
    """

    state.status = "researching"
    state.step_count += 1
    state.research_attempts += 1
    state.research_findings = []

    attempt_number = state.research_attempts
    previous_feedback = ""

    if attempt_number > 1:
        previous_feedback = f"""
PREVIOUS VERIFICATION FEEDBACK:

The previous research attempt failed verification.

Failed finding numbers:
{state.failed_findings}

Verifier feedback:
{state.verification_reason}

IMPORTANT:
You are now performing a corrective research attempt.

You MUST specifically improve the failed findings.

For each failed finding:

- Do NOT repeat the previous claim automatically.
- Re-check the exact source content.
- Identify the unsupported portion of the claim.
- Either find source content that explicitly supports that detail,
  OR remove/narrow that detail from the claim.
- The revised claim must not be stronger than its evidence.
- Do not preserve unsupported percentages, numbers, causal claims,
  guarantees, or capabilities.
"""
    state.execution_history.append(
        AgentEvent(
            agent="Research Agent",
            status="started",
            message=f"Research attempt #{attempt_number}",
        )
    )

    # ---------------------------------------------------------
    # 1. Search the web
    # ---------------------------------------------------------

    search_results = search_web(state.user_query)

    if not search_results:
        state.status = "failed"

        state.execution_history.append(
            AgentEvent(
                agent="Research Agent",
                status="failed",
                message="No web search results were returned.",
            )
        )

        return state

    # ---------------------------------------------------------
    # 2. Convert search results into Source objects
    # ---------------------------------------------------------

    sources = []

    for result in search_results:
        title = result.get("title", "Untitled source")
        url = result.get("url", "")
        content = result.get("content", "")

        sources.append(
            Source(
                title=title,
                url=url,
                content=content,
            )
        )

    state.sources = sources

    # ---------------------------------------------------------
    # 3. Prepare source material for the LLM
    # ---------------------------------------------------------

    source_text = ""

    for index, source in enumerate(sources, start=1):
        source_text += f"""
SOURCE {index}

TITLE:
{source.title}

URL:
{source.url}

CONTENT:
{source.content}

--------------------------------------------------
"""

    # ---------------------------------------------------------
    # 4. Ask the LLM for structured findings
    # ---------------------------------------------------------

    llm = get_llm()

    structured_llm = llm.with_structured_output(
        ResearchAnalysis
    )

    prompt = f"""
You are a professional research analyst.

USER RESEARCH QUESTION:
{state.user_query}

{previous_feedback}

You have been given several web sources below.

Your task is to produce exactly 5 research findings.

IMPORTANT RULES:

1. Every finding must contain ONE specific claim.

2. Every finding must contain evidence that directly supports
   THAT PARTICULAR CLAIM.

3. DO NOT reuse the same evidence paragraph for multiple findings.

4. Evidence must be taken from the provided source content.

5. Every finding must use the URL of the source that actually
   supports the finding.

6. Do not invent facts that are not present in the sources.

7. Do not use generic evidence such as:
   "RAG has evolved significantly..."
   unless that exact statement specifically supports the claim.

8. Make each finding meaningfully different.

9. Prefer concrete technical developments, capabilities,
   techniques, applications, limitations, or trends.

10. If a source does not contain enough information to support
    a claim, choose another source.

    11. Never include a number, percentage, date, quantity, or other
    specific detail in a claim unless that exact detail appears
    in the supporting source content.

12. The claim must be no stronger than the evidence.
    Do not infer, exaggerate, or generalize beyond what the source says.

13. Evidence must directly contain or clearly establish the claim.
    If the source only supports a weaker statement, rewrite the claim
    to match the weaker statement.

14. On corrective research attempts, pay special attention to the
    findings identified by the verifier as failed.

15. Prefer a narrower claim with strong evidence over a broader claim
    with weak evidence.

    16. Before returning each finding, perform a claim-evidence check.

    Ask yourself:
    "If a strict verifier saw ONLY this evidence, would they be able
    to prove this exact claim?"

    If the answer is NO, rewrite the claim.

17. Do not add information from your general knowledge.

18. Do not assume that a source's title, URL, or topic proves a claim.
    The supporting information must appear in the provided CONTENT.

19. Avoid unsupported causal language such as:
    "prevents", "guarantees", "ensures", "significantly improves",
    "eliminates", or "causes" unless the source explicitly supports
    that wording.

20. Avoid exact percentages or numerical measurements unless they
    appear explicitly in the source CONTENT.

21. The safest acceptable relationship is:

    CLAIM = what the evidence explicitly establishes.

    Never:

    CLAIM > EVIDENCE.

Return exactly 5 findings.

WEB SOURCES:

{source_text}
"""

    try:
        analysis = structured_llm.invoke(prompt)

    except Exception as exc:
        state.status = "failed"

        state.execution_history.append(
            AgentEvent(
                agent="Research Agent",
                status="failed",
                message=f"LLM research analysis failed: {exc}",
            )
        )

        return state

    # ---------------------------------------------------------
    # 5. Validate the returned findings
    # ---------------------------------------------------------

    findings = []

    for finding in analysis.findings:

        if not finding.claim.strip():
            continue

        if not finding.evidence.strip():
            continue

        if not finding.source_url.strip():
            continue

        findings.append(
            ResearchFinding(
                claim=finding.claim.strip(),
                evidence=finding.evidence.strip(),
                source_url=finding.source_url.strip(),
            )
        )

    # ---------------------------------------------------------
    # 6. Make sure we actually received findings
    # ---------------------------------------------------------

    if not findings:
        state.status = "failed"

        state.execution_history.append(
            AgentEvent(
                agent="Research Agent",
                status="failed",
                message="The LLM returned no valid research findings.",
            )
        )

        return state

    state.research_findings = findings

    # ---------------------------------------------------------
    # 7. Complete research
    # ---------------------------------------------------------

    state.status = "researched"

    state.execution_history.append(
        AgentEvent(
            agent="Research Agent",
            status="completed",
            message=(
                f"Attempt #{attempt_number} completed. "
                f"Sources: {len(state.sources)}. "
                f"Findings: {len(state.research_findings)}."
            ),
        )
    )

    return state


if __name__ == "__main__":
    initial_state = AgentState(
        user_query="What are the latest developments in RAG systems?"
    )

    result = research(initial_state)

    print("\n=== RESEARCH STATUS ===")
    print(result.status)

    print(f"Research attempts: {result.research_attempts}")
    print(f"Sources: {len(result.sources)}")
    print(f"Findings: {len(result.research_findings)}")

    print("\n=== FINDINGS ===")

    for index, finding in enumerate(
        result.research_findings,
        start=1,
    ):
        print(f"\nFinding {index}")
        print(f"Claim: {finding.claim}")
        print(f"Evidence: {finding.evidence}")
        print(f"Source: {finding.source_url}")

    print("\n=== EXECUTION HISTORY ===")

    for event in result.execution_history:
        print(
            f"[{event.agent}] "
            f"{event.status}: "
            f"{event.message}"
        )