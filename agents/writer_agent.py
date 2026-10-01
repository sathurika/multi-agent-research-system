from langchain_openai import ChatOpenAI

from config.settings import get_settings
from models.schemas import AgentState


def get_llm() -> ChatOpenAI:
    settings = get_settings()

    return ChatOpenAI(
        model=settings.model_name,
        api_key=settings.openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.2,
        timeout=settings.request_timeout,
    )


def write_report(state: AgentState) -> AgentState:
    state.status = "writing"
    state.step_count += 1

    if not state.research_findings:
        state.error = "No research findings available for the Writer Agent."
        state.status = "failed"
        return state

    findings_text = "\n\n".join(
        [
            f"Finding {index}:\n"
            f"Claim: {finding.claim}\n"
            f"Evidence: {finding.evidence}\n"
            f"Source: {finding.source_url}"
            for index, finding in enumerate(
                state.research_findings,
                start=1,
            )
        ]
    )

    llm = get_llm()

    prompt = f"""
You are a professional research report writer.

The original research question is:

{state.user_query}

The Research Agent produced the following findings:

{findings_text}

Write a clear, professional research report based ONLY on these findings.

Requirements:

1. Start with a useful title.
2. Give a short introduction.
3. Organize the main information using clear headings.
4. Explain the important findings in simple but professional language.
5. Do not invent facts.
6. Do not add information that is not supported by the findings.
7. Include source URLs naturally in a Sources section at the end.
8. Do not mention that you are an AI.
9. Do not mention internal agent processing.
10. Keep the report concise but informative.
"""

    response = llm.invoke(prompt)

    state.final_answer = response.content
    state.status = "completed"

    return state


if __name__ == "__main__":
    test_state = AgentState(
        user_query="What are the latest developments in RAG systems?"
    )

    test_state.research_findings = []

    result = write_report(test_state)

    print("\nSTATUS:")
    print(result.status)

    if result.error:
        print("\nERROR:")
        print(result.error)

    if result.final_answer:
        print("\nFINAL REPORT:")
        print(result.final_answer)
