"""Shared state passed between agents in the LangGraph workflow."""
from typing import TypedDict, Optional


class StartupState(TypedDict):
    startup_idea: str
    ceo_analysis: Optional[str]
    marketing_plan: Optional[str]
    finance_model: Optional[str]
    tech_stack: Optional[str]
    final_report: Optional[str]
