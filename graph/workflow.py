"""LangGraph workflow: CEO -> [Marketing | Finance | Tech] -> Synthesizer.

The CEO node runs first and seeds the shared state with a strategic
analysis. The three specialist agents then run in parallel, each reading the
CEO output and writing their own field. The synthesizer is a join node:
LangGraph only triggers it after all three parents have completed.
"""
from langgraph.graph import StateGraph, END

from agents import (
    ceo_agent,
    marketing_agent,
    finance_agent,
    tech_agent,
    synthesizer_agent,
)
from .state import StartupState


def build_graph():
    """Build and compile the multi-agent LangGraph workflow."""
    graph = StateGraph(StartupState)

    graph.add_node("ceo", ceo_agent)
    graph.add_node("marketing", marketing_agent)
    graph.add_node("finance", finance_agent)
    graph.add_node("tech", tech_agent)
    graph.add_node("synthesizer", synthesizer_agent)

    graph.set_entry_point("ceo")

    graph.add_edge("ceo", "marketing")
    graph.add_edge("ceo", "finance")
    graph.add_edge("ceo", "tech")

    graph.add_edge("marketing", "synthesizer")
    graph.add_edge("finance", "synthesizer")
    graph.add_edge("tech", "synthesizer")

    graph.add_edge("synthesizer", END)

    return graph.compile()


def run_workflow(startup_idea: str) -> StartupState:
    """Run the full pipeline end-to-end and return the final state."""
    app = build_graph()
    initial: StartupState = {
        "startup_idea": startup_idea,
        "ceo_analysis": None,
        "marketing_plan": None,
        "finance_model": None,
        "tech_stack": None,
        "final_report": None,
    }
    return app.invoke(initial)
