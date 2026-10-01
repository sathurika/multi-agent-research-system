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
    """
    Verify the research findings against their evidence.

    The verifier returns:
        PASS -> continue to Writer Agent
        FAIL -> return to Research Agent for another attempt
    """

    state.status = "verifying"
    state.step_count += 1

    state.execution_history.append(
        AgentEvent(
            agent="Verifier Agent",
            status="started",
            message="Checking research findings against their evidence.",
        )
    )

    # ---------------------------------------------------------
    # 1. Make sure research findings exist
    # ---------------------------------------------------------

    if not state.research_findings:
        state.error = "No research findings available for verification."
        state.status = "failed"
        state.verification_verdict = "FAIL"
        state.verification_reason = state.error
        state.failed_findings = []

        state.execution_history.append(
            AgentEvent(
                agent="Verifier Agent",
                status="failed",
                message="No research findings available.",
            )
        )

        return state

    # ---------------------------------------------------------
    # 2. Prepare findings for the LLM
    # ---------------------------------------------------------

    findings_text = "\n\n".join(
        [
            (
                f"Finding {index}:\n"
                f"Claim: {finding.claim}\n"
                f"Evidence: {finding.evidence}\n"
                f"Source: {finding.source_url}"
            )
            for index, finding in enumerate(
                state.research_findings,
                start=1,
            )
        ]
    )

    # ---------------------------------------------------------
    # 3. Create verifier LLM
    # ---------------------------------------------------------

    llm = get_llm()

    prompt = f"""
You are a strict research verification agent.

Your job is to verify research findings before they are sent
to a report-writing agent.

Original research question:
{state.user_query}

Research findings:
{findings_text}

For EVERY finding, check:

1. Does the evidence actually support the claim?
2. Is a source URL provided?
3. Is the finding relevant to the research question?
4. Does the claim contain information that is not supported
   by the evidence?
5. Does the finding contradict another finding?

A finding should be considered FAILED if an important part
of its claim is unsupported by its evidence.

Return ONLY the following format:

VERDICT: PASS
REASON: <short explanation>
FAILED_FINDINGS: NONE

OR:

VERDICT: FAIL
REASON: <short explanation>
FAILED_FINDINGS: 1, 3

Rules:

- Use PASS only when all important findings are adequately
  supported.
- Use FAIL if one or more important findings are unsupported.
- FAILED_FINDINGS must contain ONLY the numbers of findings
  that failed.
- Do not include any extra text outside this format.
"""

    # ---------------------------------------------------------
    # 4. Ask the LLM to verify
    # ---------------------------------------------------------

    try:
        response = llm.invoke(prompt)

        verification_text = response.content.strip()

        # Store the verifier response separately.
        state.verification_reason = verification_text

        # -----------------------------------------------------
        # 5. Parse VERDICT
        # -----------------------------------------------------

        if "VERDICT: PASS" in verification_text:
            state.verification_verdict = "PASS"
            state.failed_findings = []
            state.status = "verified"

            state.execution_history.append(
                AgentEvent(
                    agent="Verifier Agent",
                    status="passed",
                    message="Research passed verification.",
                )
            )

            return state

        # -----------------------------------------------------
        # 6. Handle FAIL
        # -----------------------------------------------------

        if "VERDICT: FAIL" in verification_text:
            state.verification_verdict = "FAIL"
            state.status = "verification_failed"

            failed_findings = []

            # Look specifically at the FAILED_FINDINGS line.
            for line in verification_text.splitlines():
                line = line.strip()

                if line.startswith("FAILED_FINDINGS:"):
                    failed_part = line.split(
                        "FAILED_FINDINGS:",
                        1,
                    )[1].strip()

                    if failed_part.upper() != "NONE":
                        for item in failed_part.split(","):
                            item = item.strip()

                            if item.isdigit():
                                number = int(item)

                                if (
                                    1 <= number
                                    <= len(state.research_findings)
                                ):
                                    failed_findings.append(number)

            state.failed_findings = failed_findings

            state.execution_history.append(
                AgentEvent(
                    agent="Verifier Agent",
                    status="failed",
                    message=(
                        "Research failed verification. "
                        f"Failed findings: {failed_findings}"
                    ),
                )
            )

            return state

        # -----------------------------------------------------
        # 7. Unexpected verifier response
        # -----------------------------------------------------

        state.verification_verdict = "FAIL"
        state.status = "verification_failed"
        state.failed_findings = []

        state.execution_history.append(
            AgentEvent(
                agent="Verifier Agent",
                status="failed",
                message=(
                    "Verifier returned an unexpected response "
                    "format."
                ),
            )
        )

        return state

    # ---------------------------------------------------------
    # 8. LLM/API error
    # ---------------------------------------------------------

    except Exception as exc:
        state.error = str(exc)
        state.status = "failed"
        state.verification_verdict = "FAIL"
        state.verification_reason = str(exc)

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

    print("\n=== VERIFICATION VERDICT ===")
    print(result.verification_verdict)

    print("\n=== VERIFICATION REASON ===")
    print(result.verification_reason)

    print("\n=== FAILED FINDINGS ===")
    print(result.failed_findings)

    print("\n=== EXECUTION HISTORY ===")

    for event in result.execution_history:
        print(
            f"[{event.agent}] "
            f"{event.status}: "
            f"{event.message}"
        )