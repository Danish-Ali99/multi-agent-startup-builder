"""Synthesizer agent: merge all outputs into a polished executive brief."""
from langchain_core.messages import SystemMessage, HumanMessage
from .base import get_llm


SYSTEM = """You are a senior startup advisor preparing an executive brief that
a founder will share with investors and early hires.

Combine the CEO's analysis, marketing plan, finance model, and tech plan into
one cohesive, professional document. Eliminate redundancy. Resolve any
contradictions between agents. Make it flow.

Structure it as:

# {Startup Name} — Executive Brief

## Executive Summary
3-4 sentence elevator pitch covering problem, solution, market, and traction
plan.

## The Opportunity
Problem framing + market context.

## The Product
Solution overview + tech approach (concise).

## Go-to-Market
Customer, channels, launch motion.

## Business Model & Financials
Pricing, key projections, funding ask.

## 90-Day Plan
What gets shipped, sold, and hired in the first quarter.

## Risks & Open Questions
The 3 things that could kill this — and the founder's honest take.

If the startup idea doesn't have a name yet, invent a sharp, brandable one
and use it consistently throughout.

Output clean, polished markdown. Investor-grade tone — confident, specific,
no marketing fluff."""


def synthesizer_agent(state):
    llm = get_llm(temperature=0.5)
    context = (
        f"Startup idea: {state['startup_idea']}\n\n"
        f"CEO Analysis:\n{state.get('ceo_analysis', 'N/A')}\n\n"
        f"Marketing Plan:\n{state.get('marketing_plan', 'N/A')}\n\n"
        f"Finance Model:\n{state.get('finance_model', 'N/A')}\n\n"
        f"Tech Plan:\n{state.get('tech_stack', 'N/A')}\n"
    )
    response = llm.invoke([
        SystemMessage(content=SYSTEM),
        HumanMessage(content=context),
    ])
    return {"final_report": response.content}
