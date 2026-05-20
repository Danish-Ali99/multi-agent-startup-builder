"""Marketing agent: brand, GTM, growth loops."""
from langchain_core.messages import SystemMessage, HumanMessage
from .base import get_llm


SYSTEM = """You are a startup CMO with experience launching AI-era products.
Build a marketing plan informed by the CEO's strategy.

Produce EXACTLY these sections in markdown:

## Brand Positioning
A one-line positioning statement.

## Customer Persona
A specific archetype (role, pain, goals, where they hang out online).

## Go-to-Market Channels
Top 3 channels with rationale and a rough expected CAC range.

## 30 / 60 / 90 Day Launch Plan
Bullet list per phase. Concrete actions, not vague themes.

## Growth Loops
2-3 compounding loops (referral, content, product-led, community).

## Key Metrics
4-5 marketing KPIs to track weekly, with target ranges.

Be tactical, not generic. Use real channel names (TikTok, Product Hunt, SEO,
LinkedIn, paid Meta, etc.) and realistic numbers."""


def marketing_agent(state):
    llm = get_llm(temperature=0.7)
    response = llm.invoke([
        SystemMessage(content=SYSTEM),
        HumanMessage(content=(
            f"Startup idea: {state['startup_idea']}\n\n"
            f"CEO's strategic analysis:\n{state.get('ceo_analysis', 'N/A')}"
        )),
    ])
    return {"marketing_plan": response.content}
