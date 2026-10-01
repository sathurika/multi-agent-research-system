from langchain_openai import ChatOpenAI
from config.settings import get_settings
from models.schemas import AgentState, ResearchFinding, Source
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

    prompt = f"""
You are a research analyst.

The user wants information about:

{state.user_query}

Below are web search results.

Analyze them carefully.

Your tasks are:

1. Identify the most useful factual information.
2. Remove irrelevant information.
3. Do not invent facts that are not supported by the sources.
4. Use only information contained in the search results.
5. Clearly distinguish facts from opinions or predictions.
6. Give a concise and useful research analysis.

WEB SEARCH RESULTS:

{research_context}

Return a concise research analysis.
"""

    response = llm.invoke(prompt)

    state.research_findings = [
        ResearchFinding(
            claim="Research analysis",
            evidence=response.content,
            source_url=results[0]["url"],
        )
    ]

    state.sources = [
        Source(
            title=result["title"],
            url=result["url"],
            snippet=result["content"][:300],
        )
        for result in results
    ]

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

    print("\nRESEARCH ANALYSIS:")

    for finding in result.research_findings:
        print(finding.evidence)