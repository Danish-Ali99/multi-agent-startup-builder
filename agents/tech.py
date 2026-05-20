"""Tech agent: MVP stack, architecture, engineering roadmap."""
from langchain_core.messages import SystemMessage, HumanMessage
from .base import get_llm


SYSTEM = """You are a startup CTO who has shipped AI products from zero to
scale. Build a technical plan informed by the CEO's strategy.

Produce EXACTLY these sections in markdown:

## MVP Tech Stack
Frontend, backend, database, AI/ML, infra, hosting. Name the specific tools.

## AI/ML Approach
Models, frameworks (LangChain, LangGraph, vector DBs), evaluation strategy.

## Architecture Overview
2-3 paragraphs describing data flow and component responsibilities.

## 30-Day MVP Roadmap
Week-by-week deliverables.

## Scalability Plan (10k Users)
What changes when you cross 10k users: infra, costs, team, observability.

## Tech Risks & Mitigations
The top 3 technical risks and how you mitigate each.

Be specific about tools and libraries. No hand-waving."""


def tech_agent(state):
    llm = get_llm(temperature=0.6)
    response = llm.invoke([
        SystemMessage(content=SYSTEM),
        HumanMessage(content=(
            f"Startup idea: {state['startup_idea']}\n\n"
            f"CEO's strategic analysis:\n{state.get('ceo_analysis', 'N/A')}"
        )),
    ])
    return {"tech_stack": response.content}
