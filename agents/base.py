"""Shared LLM factory used by every agent."""
import os
from langchain_openai import ChatOpenAI


def get_llm(temperature: float = 0.7) -> ChatOpenAI:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return ChatOpenAI(model=model, temperature=temperature)
