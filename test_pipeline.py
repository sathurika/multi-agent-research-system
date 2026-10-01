from models.schemas import AgentState
from agents.research_agent import research
from agents.writer_agent import write_report


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

    print("\n=== WRITER AGENT ===")

    state = write_report(state)

    print(f"Status: {state.status}")

    if state.error:
        print(f"Error: {state.error}")
        return

    print("\n=== FINAL REPORT ===")
    print(state.final_answer)


if __name__ == "__main__":
    main()
