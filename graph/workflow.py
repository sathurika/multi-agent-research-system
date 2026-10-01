from langgraph.graph import END, START, StateGraph

from agents.research_agent import research
from agents.verifier_agent import verify_research
from agents.writer_agent import write_report
from models.schemas import AgentState


MAX_RESEARCH_ATTEMPTS = 2


def build_workflow():
    graph = StateGraph(AgentState)

    graph.add_node("research", research)
    graph.add_node("verifier", verify_research)
    graph.add_node("writer", write_report)

    graph.add_edge(START, "research")
    graph.add_edge("research", "verifier")

    graph.add_conditional_edges(
        "verifier",
        verification_router,
        {
            "writer": "writer",
            "research": "research",
        },
    )

    graph.add_edge("writer", END)

    return graph.compile()


def verification_router(state: AgentState) -> str:
    if state.status == "verified":
        return "writer"

    if state.step_count < MAX_RESEARCH_ATTEMPTS:
        return "research"

    return "writer"


workflow = build_workflow()


if __name__ == "__main__":
    initial_state = AgentState(
        user_query="What are the latest developments in RAG systems?"
    )

    result = workflow.invoke(initial_state)

    print("\n=== WORKFLOW STATUS ===")
    print(result["status"])

    print("\n=== SOURCES ===")

    for source in result["sources"]:
        print(f"- {source.title}")
        print(f"  {source.url}")

    print("\n=== RESEARCH FINDINGS ===")

    for index, finding in enumerate(
        result["research_findings"],
        start=1,
    ):
        print(f"\nFinding {index}")
        print(f"Claim: {finding.claim}")
        print(f"Evidence: {finding.evidence}")
        print(f"Source: {finding.source_url}")

    print("\n=== FINAL OUTPUT ===")
    print(result["final_answer"])
