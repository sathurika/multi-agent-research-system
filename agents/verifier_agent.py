from langchain_openai import ChatOpenAI

from config.settings import get_settings
from models.schemas import AgentEvent, AgentState


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

    state.execution_history.append(
        AgentEvent(
            agent="Verifier Agent",
            status="started",
            message="Checking research findings against their evidence.",
        )
    )

    if not state.research_findings:
        state.error = "No research findings available for verification."
        state.status = "failed"

        state.execution_history.append(
            AgentEvent(
                agent="Verifier Agent",
                status="failed",
                message="No research findings available.",
            )
        )

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

Original research question:

{state.user_query}

Research findings:

{findings_text}

Evaluate every finding.

For each finding, check:

1. Does the evidence support the claim?
2. Is a source URL provided?
3. Is the finding relevant to the question?
4. Does it contain unsupported information?
5. Are there contradictions?

Return ONLY this format:

VERDICT: PASS
REASON: <short explanation>
FAILED_FINDINGS: NONE

OR:

VERDICT: FAIL
REASON: <short explanation>
FAILED_FINDINGS: 1, 3

Use FAIL when important findings are unsupported.
"""

    try:
        response = llm.invoke(prompt)

        verification_text = response.content.strip()

        state.final_answer = verification_text

        if "VERDICT: PASS" in verification_text:
            state.verification_verdict = "PASS"
            state.verification_reason = verification_text
            state.failed_findings = []
            state.status = "verified"

            state.execution_history.append(
                AgentEvent(
                    agent="Verifier Agent",
                    status="passed",
                    message="Research passed verification.",
                )
            )

        else:
            state.verification_verdict = "FAIL"
            state.status = "verification_failed"

            failed_numbers = []

            for number in range(1, len(state.research_findings) + 1):
                if str(number) in verification_text:
                    failed_numbers.append(number)

            state.failed_findings = failed_numbers

            state.verification_reason = verification_text

            state.execution_history.append(
                AgentEvent(
                    agent="Verifier Agent",
                    status="failed",
                    message=(
                        "Research failed verification. "
                        f"Failed findings: {failed_numbers}"
                    ),
                )
            )

        return state

    except Exception as exc:
        state.error = str(exc)
        state.status = "failed"

        state.execution_history.append(
            AgentEvent(
                agent="Verifier Agent",
                status="error",
                message=str(exc),
            )
        )

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

    print("\n=== EXECUTION HISTORY ===")

    for event in result.execution_history:
        print(
            f"[{event.agent}] "
            f"{event.status}: "
            f"{event.message}"
        )
