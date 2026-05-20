"""Streamlit UI for the Multi-Agent Startup Builder."""
import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from graph.workflow import build_graph
from graph.state import StartupState


REPO_URL = "https://github.com/Danish-Ali99/multi-agent-startup-builder"

SAMPLE_IDEAS = [
    "An AI co-pilot for college students that turns lecture recordings into searchable notes, flashcards, and quizzes.",
    "A WhatsApp-based bookkeeping assistant for Indian small shops that auto-tracks daily sales and prepares GST returns.",
    "A B2B platform that helps cafés and restaurants cut food waste by predicting daily demand from past POS data.",
]


def get_secret(name: str, default: str = "") -> str:
    """Read a value from env first, then from Streamlit secrets (for Cloud deploys)."""
    if os.environ.get(name):
        return os.environ[name]
    try:
        if hasattr(st, "secrets") and name in st.secrets:
            return st.secrets[name]
    except (FileNotFoundError, AttributeError):
        pass
    return default


@st.cache_resource
def get_compiled_graph():
    """Build and cache the compiled LangGraph workflow across script reruns."""
    return build_graph()


def _set_idea(text: str) -> None:
    st.session_state["idea_text"] = text


st.set_page_config(
    page_title="Multi-Agent Startup Builder",
    page_icon="🚀",
    layout="wide",
)

st.session_state.setdefault("idea_text", "")

st.title("Multi-Agent Startup Builder")
st.caption(
    "Agentic AI pipeline: CEO → (Marketing ∥ Finance ∥ Tech) → Synthesizer. "
    "Built with LangGraph + LangChain."
)

# --- Sidebar ---
with st.sidebar:
    st.header("Configuration")

    provider = st.selectbox(
        "Provider",
        ["Groq (free)", "OpenAI"],
        index=0,
        help="Groq is free, no credit card. OpenAI requires billing.",
    )

    if provider == "Groq (free)":
        api_key = st.text_input(
            "Groq API Key",
            value=get_secret("GROQ_API_KEY"),
            type="password",
            help="Get a free key at console.groq.com — no credit card required.",
        )
        model = st.selectbox(
            "Model",
            ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"],
            index=0,
            help="llama-3.3-70b: best quality. 8b: fastest. gemma2: balanced.",
        )
    else:
        api_key = st.text_input(
            "OpenAI API Key",
            value=get_secret("OPENAI_API_KEY"),
            type="password",
            help="Kept only in this session.",
        )
        model = st.selectbox(
            "Model",
            ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"],
            index=0,
            help="gpt-4o-mini: cheap and fast. gpt-4o: sharper output.",
        )

    st.markdown("---")
    st.markdown("**Architecture**")
    st.code(
        "CEO\n  ├─ Marketing ─┐\n  ├─ Finance   ├─ Synthesizer\n  └─ Tech      ┘",
        language="text",
    )
    st.markdown("---")
    st.markdown(f"[View source on GitHub]({REPO_URL})")

# --- Main: idea input + sample buttons ---
col_left, col_right = st.columns([3, 1])

with col_left:
    idea = st.text_area(
        "Describe your startup idea",
        placeholder=SAMPLE_IDEAS[0],
        height=140,
        key="idea_text",
    )

with col_right:
    st.markdown("**Quick samples**")
    for i, sample in enumerate(SAMPLE_IDEAS):
        label = sample.split(" that ")[0]
        if len(label) > 34:
            label = label[:32] + "..."
        st.button(
            label,
            key=f"sample-{i}",
            on_click=_set_idea,
            args=(sample,),
            use_container_width=True,
        )

run = st.button("🚀 Generate business plan", type="primary")

if run:
    if not api_key:
        st.error(f"Please provide your {provider.split()[0]} API key in the sidebar.")
        st.stop()
    idea = (idea or "").strip()
    if not idea:
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

    app = get_compiled_graph()

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
        msg = str(e).lower()
        if any(s in msg for s in ("api key", "invalid_api_key", "unauthorized", "401", "authentication")):
            st.error(
                "API key was rejected. Double-check your key in the sidebar — "
                "Groq keys start with `gsk_`, OpenAI keys with `sk-`."
            )
        elif "rate" in msg and "limit" in msg:
            st.error(
                "Rate limit hit. Wait a minute, then try again. Switching to a smaller "
                "model in the sidebar (e.g. `llama-3.1-8b-instant`) raises your limits."
            )
        elif any(s in msg for s in ("connection", "timeout", "network")):
            st.error("Network issue reaching the model provider. Check your internet and retry.")
        else:
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

st.markdown("---")
st.caption(
    "⚠️ Outputs are AI-generated drafts, not financial or legal advice. "
    f"Source on [GitHub]({REPO_URL})."
)
