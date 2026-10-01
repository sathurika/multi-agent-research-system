from graph.graph import build_graph
from models.schemas import AgentState


def main():
    print("\n" + "=" * 60)
    print("              MULTI-AGENT RESEARCH SYSTEM")
    print("=" * 60)

    query = input(
        "\nEnter your research question: "
    ).strip()

    if not query:
        print("\nERROR: Research question cannot be empty.")
        return

    initial_state = AgentState(
        user_query=query
    )

    workflow = build_graph()

    result = workflow.invoke(
        initial_state.model_dump()
    )

    print("\n" + "-" * 60)
    print("QUERY")
    print("-" * 60)

    print(query)

    print("\n" + "-" * 60)
    print("WORKFLOW STATUS")
    print("-" * 60)

    print(
        f"Status: "
        f"{result.get('status', 'unknown')}"
    )

    print(
        f"Research attempts: "
        f"{result.get('research_attempts', 0)}"
    )

    print(
        f"Verification verdict: "
        f"{result.get('verification_verdict', 'N/A')}"
    )

    if result.get("verification_reason"):
        print(
            f"Verification details: "
            f"{result['verification_reason']}"
        )

    print("\n" + "-" * 60)
    print("AGENT EXECUTION HISTORY")
    print("-" * 60)

    execution_history = result.get(
        "execution_history",
        []
    )

    for index, event in enumerate(
        execution_history,
        start=1,
    ):
        if isinstance(event, dict):
            agent = event.get(
                "agent",
                "Unknown Agent"
            )
            status = event.get(
                "status",
                "unknown"
            )
            message = event.get(
                "message",
                ""
            )
        else:
            agent = event.agent
            status = event.status
            message = event.message

        print(
            f"{index}. "
            f"[{agent}] "
            f"{status.upper()}"
        )

        if message:
            print(f"   {message}")

    print("\n" + "-" * 60)
    print("SOURCES")
    print("-" * 60)

    sources = result.get(
        "sources",
        []
    )

    for source in sources:
        if isinstance(source, dict):
            title = source.get(
                "title",
                ""
            )
            url = source.get(
                "url",
                ""
            )
        else:
            title = source.title
            url = source.url

        print(f"- {title}")
        print(f"  {url}")

    print("\n" + "-" * 60)
    print("RESEARCH FINDINGS")
    print("-" * 60)

    findings = result.get(
        "research_findings",
        []
    )

    for index, finding in enumerate(
        findings,
        start=1,
    ):
        if isinstance(finding, dict):
            claim = finding.get(
                "claim",
                ""
            )
            evidence = finding.get(
                "evidence",
                ""
            )
            source_url = finding.get(
                "source_url",
                ""
            )
        else:
            claim = finding.claim
            evidence = finding.evidence
            source_url = finding.source_url

        print(f"\nFinding {index}")
        print(f"Claim: {claim}")
        print(f"Evidence: {evidence}")
        print(f"Source: {source_url}")

    print("\n" + "-" * 60)
    print("FINAL OUTPUT")
    print("-" * 60)

    final_answer = result.get(
        "final_answer"
    )

    if final_answer:
        print(final_answer)
    else:
        print("No final output generated.")

    print("\n" + "=" * 60)
    print("WORKFLOW FINISHED")
    print("=" * 60)


if __name__ == "__main__":
    main()