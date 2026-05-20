"""Streamlit UI for the Multi-Agent Startup Builder."""
import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from graph.workflow import build_graph
from graph.state import StartupState


st.set_page_config(
    page_title="Multi-Agent Startup Builder",
    page_icon="🚀",
    layout="wide",
)

st.title("Multi-Agent Startup Builder")
st.caption(
    "Agentic AI pipeline: CEO → (Marketing ∥ Finance ∥ Tech) → Synthesizer. "
    "Built with LangGraph + OpenAI."
)

with st.sidebar:
    st.header("Configuration")

    provider = st.selectbox(
        "Provider",
        ["Groq (free)", "OpenAI"],
        index=0,
        help="Groq is free. OpenAI requires billing.",
    )

    if provider == "Groq (free)":
        api_key = st.text_input(
            "Groq API Key",
            value=os.getenv("GROQ_API_KEY", ""),
            type="password",
            help="Get a free key at console.groq.com — no credit card.",
        )
        model = st.selectbox(
            "Model",
            ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"],
            index=0,
            help="llama-3.3-70b is highest quality; 8b is faster.",
        )
    else:
        api_key = st.text_input(
            "OpenAI API Key",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password",
            help="Kept only in this session.",
        )
        model = st.selectbox(
            "Model",
            ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"],
            index=0,
            help="gpt-4o-mini is fast and cheap. gpt-4o is sharper.",
        )

    st.markdown("---")
    st.markdown("**Architecture**")
    st.code(
        "CEO\n  ├─ Marketing ─┐\n  ├─ Finance   ├─ Synthesizer\n  └─ Tech      ┘",
        language="text",
    )
    st.markdown("---")
    st.markdown(
        "Built with "
        "[LangGraph](https://langchain-ai.github.io/langgraph/), "
        "[OpenAI](https://platform.openai.com/), and "
        "[Streamlit](https://streamlit.io)."
    )

idea = st.text_area(
    "Describe your startup idea",
    placeholder=(
        "Example: An AI co-pilot for college students that turns their "
        "lecture recordings into searchable notes, flashcards, and quizzes."
    ),
    height=140,
)

col_run, _ = st.columns([1, 5])
run = col_run.button("Generate business plan", type="primary", use_container_width=True)

if run:
    if not api_key:
        st.error(f"Please provide your {provider.split()[0]} API key in the sidebar.")
        st.stop()
    if not idea.strip():
        st.error("Please describe your startup idea.")
        st.stop()

    if provider == "Groq (free)":
        os.environ["LLM_PROVIDER"] = "groq"
        os.environ["GROQ_API_KEY"] = api_key
        os.environ["GROQ_MODEL"] = model
    else:
        os.environ["LLM_PROVIDER"] = "openai"
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_MODEL"] = model

    initial: StartupState = {
        "startup_idea": idea,
        "ceo_analysis": None,
        "marketing_plan": None,
        "finance_model": None,
        "tech_stack": None,
        "final_report": None,
    }

    app = build_graph()

    labels = {
        "ceo": "CEO",
        "marketing": "Marketing",
        "finance": "Finance",
        "tech": "Tech",
        "synthesizer": "Synthesizer",
    }

    progress = st.progress(0, text="Starting agents...")
    completed_state: StartupState = initial.copy()
    step_count = 0
    total_steps = 5

    try:
        for event in app.stream(initial, stream_mode="updates"):
            for node_name, update in event.items():
                step_count += 1
                progress.progress(
                    min(step_count / total_steps, 1.0),
                    text=f"Completed: {labels.get(node_name, node_name)}",
                )
                completed_state.update(update or {})
    except Exception as e:
        st.error(f"Agent run failed: {e}")
        st.stop()

    progress.progress(1.0, text="All agents complete")
    st.success("Business plan generated.")

    st.markdown("## Executive Brief")
    st.markdown(completed_state.get("final_report") or "_No final report._")

    fname = f"startup-plan-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    st.download_button(
        "Download as Markdown",
        completed_state.get("final_report") or "",
        file_name=fname,
        mime="text/markdown",
    )

    st.markdown("---")
    st.markdown("## Agent Outputs")
    tab_ceo, tab_mkt, tab_fin, tab_tech = st.tabs(
        ["CEO", "Marketing", "Finance", "Tech"]
    )
    with tab_ceo:
        st.markdown(completed_state.get("ceo_analysis") or "_empty_")
    with tab_mkt:
        st.markdown(completed_state.get("marketing_plan") or "_empty_")
    with tab_fin:
        st.markdown(completed_state.get("finance_model") or "_empty_")
    with tab_tech:
        st.markdown(completed_state.get("tech_stack") or "_empty_")
