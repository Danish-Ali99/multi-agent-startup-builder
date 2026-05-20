"""Finance agent: revenue model, projections, capital needs."""
from langchain_core.messages import SystemMessage, HumanMessage
from .base import get_llm


SYSTEM = """You are a startup CFO with deep experience in early-stage AI / SaaS
finance. Build a financial plan informed by the CEO's strategy.

Produce EXACTLY these sections in markdown:

## Revenue Model
Pricing tiers with concrete dollar amounts and what each tier includes.

## Cost Structure
Major cost lines: people, infra, AI/API costs, marketing, ops.

## Year 1 Revenue Forecast
Three scenarios (Conservative / Realistic / Aggressive) with monthly run-rate
endpoints. Show your assumptions (signups, conversion, ARPU).

## Initial Capital Required
How much to raise, with a breakdown across engineering, product, GTM,
infra/AI, ops, and runway buffer.

## Path to Profitability
Concrete milestones (MRR threshold, gross margin target, month estimate).

## Key Financial Metrics
CAC, LTV, LTV:CAC, gross margin, burn rate. Use target numbers, not formulas.

Use realistic numbers. Show your work. No hand-waving."""


def finance_agent(state):
    llm = get_llm(temperature=0.6)
    response = llm.invoke([
        SystemMessage(content=SYSTEM),
        HumanMessage(content=(
            f"Startup idea: {state['startup_idea']}\n\n"
            f"CEO's strategic analysis:\n{state.get('ceo_analysis', 'N/A')}"
        )),
    ])
    return {"finance_model": response.content}
