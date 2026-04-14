import streamlit as st
from theme import apply_theme

st.set_page_config(
    page_title="Apple Quarterly Analysis Dashboard",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_theme()

home = st.Page(
    "pages/home.py",
    title="Home",
    icon="🍎",
    default=True,
)

q1 = st.Page("pages/q1.py", title="Q1", icon="📈")
q2 = st.Page("pages/q2.py", title="Q2", icon="📊")
q3 = st.Page("pages/q3.py", title="Q3", icon="⚡")
q4 = st.Page("pages/q4.py", title="Q4", icon="📉")
q5 = st.Page("pages/q5.py", title="Q5", icon="📰")
q6 = st.Page("pages/q6.py", title="Q6", icon="📦")

vis_agent = st.Page(
    "pages/vis_agent.py",
    title="Visual AI Agent",
    icon="🎯",
    url_path="ai-agent",
    visibility="hidden",
)

st.markdown(
    """
    <style>
    .floating-ai {
        position: fixed;
        left: 1.1rem;
        bottom: 1.1rem;
        z-index: 999999;
        background: linear-gradient(135deg, rgba(10,132,255,0.95), rgba(10,132,255,0.78));
        color: white !important;
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 999px;
        padding: 0.75rem 1rem;
        box-shadow: 0 12px 28px rgba(0,0,0,0.28);
        font-weight: 700;
        font-size: 0.95rem;
        text-decoration: none !important;
    }

    .floating-ai:hover {
        transform: translateY(-1px);
        box-shadow: 0 14px 32px rgba(0,0,0,0.34);
    }
    </style>

    <a class="floating-ai" href="/ai-agent" target="_self">
        🎯 Open Visual AI Agent
    </a>
    """,
    unsafe_allow_html=True,
)

pg = st.navigation(
    {
        "": [home],
        "Analysis Questions": [q1, q2, q3, q4, q5, q6],
        "Hidden": [vis_agent],
    },
    position="top",
    expanded=False,
)

pg.run()