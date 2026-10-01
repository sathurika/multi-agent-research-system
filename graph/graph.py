from langgraph.graph import END, START, StateGraph

from agents.research_agent import research
from agents.verifier_agent import verify_research
from agents.writer_agent import write_report
from models.schemas import AgentState


def should_continue_after_verification(state: AgentState):
    """
    Decide whether the workflow should retry research
    or continue to the Writer Agent.
    """

    if state.verification_verdict == "PASS":
        return "writer"

    if state.research_attempts < 2:
        return "research"

    return "writer"


def build_graph():
    """
    Build and compile the multi-agent research workflow.
    """

    graph = StateGraph(AgentState)

    graph.add_node("research", research)
    graph.add_node("verifier", verify_research)
    graph.add_node("writer", write_report)

    graph.add_edge(START, "research")
    graph.add_edge("research", "verifier")

    graph.add_conditional_edges(
        "verifier",
        should_continue_after_verification,
        {
            "research": "research",
            "writer": "writer",
        },
    )

    graph.add_edge("writer", END)

    return graph.compile()