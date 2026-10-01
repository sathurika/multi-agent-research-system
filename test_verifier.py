from models.schemas import AgentState
from agents.research_agent import research
from agents.verifier_agent import verify_research


def main():
    state = AgentState(
        user_query="What are the latest developments in RAG systems?"
    )

    print("\n=== RESEARCH AGENT ===")

    state = research(state)

    print(f"Status: {state.status}")
    print(f"Sources found: {len(state.sources)}")
    print(f"Research findings: {len(state.research_findings)}")

    if state.error:
        print(f"Error: {state.error}")
        return

    print("\n=== VERIFIER AGENT ===")

    state = verify_research(state)

    print(f"Status: {state.status}")

    if state.error:
        print(f"Error: {state.error}")
        return

    print("\n=== VERIFICATION RESULT ===")
    print(state.final_answer)


if __name__ == "__main__":
    main()
