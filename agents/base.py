"""Shared LLM factory used by every agent.

Provider is selected via the ``LLM_PROVIDER`` env var (``groq`` or ``openai``).
This keeps the agent code provider-agnostic — switching backends is a single
env var, no code changes.
"""
import os


def get_llm(temperature: float = 0.7):
    provider = os.getenv("LLM_PROVIDER", "groq").lower()

    if provider == "groq":
        from langchain_groq import ChatGroq
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        return ChatGroq(model=model, temperature=temperature)

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return ChatOpenAI(model=model, temperature=temperature)

    raise ValueError(
        f"Unknown LLM_PROVIDER={provider!r}. Use 'groq' or 'openai'."
    )
