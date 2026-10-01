from langchain_openai import ChatOpenAI

from config.settings import get_settings
from models.schemas import AgentState, ResearchAnalysis, ResearchFinding, Source
from tools.search_tool import search_web


def get_llm() -> ChatOpenAI:
    settings = get_settings()

    return ChatOpenAI(
        model=settings.model_name,
        api_key=settings.openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
        timeout=settings.request_timeout,
    )


def research(state: AgentState) -> AgentState:
    state.status = "researching"
    state.step_count += 1

    results = search_web(
        query=state.user_query,
        max_results=5,
    )

    if not results:
        state.error = "No search results were found."
        state.status = "failed"
        return state

    research_context = "\n\n".join(
        [
            f"TITLE: {result['title']}\n"
            f"URL: {result['url']}\n"
            f"CONTENT: {result['content']}"
            for result in results
        ]
    )

    llm = get_llm()

    structured_llm = llm.with_structured_output(ResearchAnalysis)

    prompt = f"""
You are a research analyst.

The user wants information about:

{state.user_query}

Below are web search results.

Analyze the sources carefully.

Create individual research findings.

For every finding:

1. Write one clear factual claim.
2. Provide evidence from the search results.
3. Provide the URL of the source supporting that claim.
4. Do not invent information.
5. Do not use information that is not supported by the sources.
6. Avoid duplicate findings.
7. Prefer important and useful findings.

WEB SEARCH RESULTS:

{research_context}
"""

    analysis = structured_llm.invoke(prompt)

    state.research_findings = analysis.findings

    state.sources = [
        Source(
            title=result["title"],
            url=result["url"],
            snippet=result["content"][:300],
        )
        for result in results
    ]

    state.status = "researched"

    return state


if __name__ == "__main__":
    test_state = AgentState(
        user_query="What are the latest developments in RAG systems?"
    )

    result = research(test_state)

    print("\nSTATUS:")
    print(result.status)

    print("\nSOURCES:")

    for source in result.sources:
        print(f"- {source.title}")
        print(f"  {source.url}")

    print("\nRESEARCH FINDINGS:")

    for index, finding in enumerate(result.research_findings, start=1):
        print(f"\nFinding {index}")
        print(f"Claim: {finding.claim}")
        print(f"Evidence: {finding.evidence}")
        print(f"Source: {finding.source_url}")
