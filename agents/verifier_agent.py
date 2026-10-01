from langchain_openai import ChatOpenAI

from config.settings import get_settings
from models.schemas import AgentState


def get_llm() -> ChatOpenAI:
    settings = get_settings()

    return ChatOpenAI(
        model=settings.model_name,
        api_key=settings.openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
        timeout=settings.request_timeout,
    )


def verify_research(state: AgentState) -> AgentState:
    state.status = "verifying"
    state.step_count += 1

    if not state.research_findings:
        state.error = "No research findings available for verification."
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
You are a strict research verification agent.

The original research question is:

{state.user_query}

The Research Agent produced these findings:

{findings_text}

Your job is to determine whether the research is reliable enough
to be used in a final report.

Check every finding for:

1. Does the evidence actually support the claim?
2. Is the source URL present?
3. Is the finding relevant to the original question?
4. Does the finding contain unsupported or invented information?
5. Are there obvious contradictions between findings?

Give your decision using exactly this format:

VERDICT: PASS

or

VERDICT: FAIL

Then provide:

REASON: <short explanation>

FAILED_FINDINGS: <comma-separated finding numbers, or NONE>

Be strict. If important claims are unsupported, choose FAIL.
"""

    response = llm.invoke(prompt)

    verification_text = response.content.strip()

    state.final_answer = verification_text

    if "VERDICT: PASS" in verification_text:
        state.status = "verified"
    else:
        state.status = "verification_failed"

    return state


if __name__ == "__main__":
    test_state = AgentState(
        user_query="What are the latest developments in RAG systems?"
    )

    result = verify_research(test_state)

    print("\n=== VERIFICATION STATUS ===")
    print(result.status)

    if result.error:
        print("\nERROR:")
        print(result.error)

    if result.final_answer:
        print("\nVERIFICATION RESULT:")
        print(result.final_answer)
