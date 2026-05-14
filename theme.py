import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        /* ── Apple Design System ─────────────────────────────────── */
        :root {
            --apple-bg:        #f5f5f7;
            --apple-surface:   #ffffff;
            --apple-blue:      #0071e3;
            --apple-blue-hover:#0077ed;
            --apple-text:      #1d1d1f;
            --apple-secondary: #6e6e73;
            --apple-border:    #d2d2d7;
            --apple-shadow:    0 2px 12px rgba(0,0,0,0.08);
            --apple-shadow-md: 0 4px 24px rgba(0,0,0,0.10);
        }

        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display",
                         "SF Pro Text", "Segoe UI", sans-serif;
        }

        /* ── 전체 배경 ─────────────────────────────────────────────── */
        .stApp {
            background: var(--apple-bg);
            color: var(--apple-text);
        }

        .block-container {
            max-width: 1200px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        /* ── 헤더 / 탑 네비게이션 ──────────────────────────────────── */
        header[data-testid="stHeader"] {
            background: rgba(255, 255, 255, 0.92);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--apple-border);
        }

        /* 네비게이션 바 전체 흰색 */
        div[data-testid="stHeader"],
        nav[data-testid="stNavigation"],
        div[data-testid="stNavigation"] {
            background: rgba(255, 255, 255, 0.92) !important;
        }

        /* 로고 이미지 크기 조정 */
        div[data-testid="stLogo"] img {
            height: 22px !important;
            width: auto !important;
        }

        /* ── 사이드바 ──────────────────────────────────────────────── */
        section[data-testid="stSidebar"] {
            background: var(--apple-surface);
            border-right: 1px solid var(--apple-border);
        }

        section[data-testid="stSidebar"] * {
            color: var(--apple-text) !important;
        }

        /* ── 타이포그래피 ───────────────────────────────────────────── */
        h1 {
            color: var(--apple-text);
            font-size: 2.4rem;
            font-weight: 700;
            letter-spacing: -0.04em;
            line-height: 1.1;
        }

        h2, h3 {
            color: var(--apple-text);
            letter-spacing: -0.03em;
        }

        p, span, label, li {
            color: var(--apple-text);
        }

        /* ── 차트 컨테이너 ─────────────────────────────────────────── */
        div[data-testid="stVegaLiteChart"] {
            background: var(--apple-surface);
            border: 1px solid var(--apple-border);
            border-radius: 18px;
            padding: 0.5rem;
            box-shadow: var(--apple-shadow);
        }

        div[data-testid="stDataFrame"] {
            background: var(--apple-surface);
            border: 1px solid var(--apple-border);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: var(--apple-shadow);
        }

        /* ── Hero 카드 ─────────────────────────────────────────────── */
        .hero-card {
            background: var(--apple-surface);
            border: 1px solid var(--apple-border);
            border-radius: 20px;
            padding: 1.6rem 1.8rem;
            margin-bottom: 1.2rem;
            box-shadow: var(--apple-shadow-md);
        }

        .hero-title {
            font-size: 1.6rem;
            font-weight: 700;
            line-height: 1.2;
            color: var(--apple-text);
            margin-bottom: 0.4rem;
            letter-spacing: -0.03em;
        }

        .hero-subtext {
            font-size: 0.95rem;
            color: var(--apple-secondary);
            line-height: 1.6;
            max-width: 860px;
        }

        /* ── Pill 태그 ─────────────────────────────────────────────── */
        .pill {
            display: inline-block;
            padding: 0.3rem 0.75rem;
            margin-right: 0.4rem;
            margin-top: 0.6rem;
            border-radius: 999px;
            background: #e8f0fe;
            border: 1px solid #c6d8fa;
            color: var(--apple-blue);
            font-size: 0.80rem;
            font-weight: 600;
        }

        /* ── Mini 카드 (FOCUS / DATA SCOPE / USE CASE) ─────────────── */
        .mini-card {
            background: var(--apple-surface);
            border: 1px solid var(--apple-border);
            border-radius: 18px;
            padding: 1.1rem 1.2rem;
            min-height: 110px;
            box-shadow: var(--apple-shadow);
        }

        .mini-label {
            font-size: 0.78rem;
            color: var(--apple-secondary);
            margin-bottom: 0.4rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        .mini-value {
            font-size: 1.25rem;
            line-height: 1.3;
            font-weight: 700;
            color: var(--apple-text);
        }

        /* ── st.metric() ───────────────────────────────────────────── */
        div[data-testid="stMetricValue"] {
            color: var(--apple-text) !important;
            font-weight: 700;
        }

        div[data-testid="stMetricLabel"] {
            color: var(--apple-secondary) !important;
        }

        /* ── Section 카드 ──────────────────────────────────────────── */
        .section-card {
            background: var(--apple-surface);
            border: 1px solid var(--apple-border);
            border-radius: 18px;
            padding: 1.1rem 1.3rem;
            margin-bottom: 1rem;
            box-shadow: var(--apple-shadow);
        }

        .section-title {
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
            color: var(--apple-text);
        }

        .section-text {
            color: var(--apple-secondary);
            line-height: 1.65;
            font-size: 0.94rem;
        }

        /* ── 탭 ────────────────────────────────────────────────────── */
        .stTabs [data-baseweb="tab"] {
            border-radius: 999px;
            padding: 0.35rem 1rem;
            background: transparent;
            color: var(--apple-secondary);
            font-weight: 700;
        }

        .stTabs [aria-selected="true"] {
            background: var(--apple-blue) !important;
            color: #ffffff !important;
            border: none !important;
            font-weight: 700 !important;
        }

        .stTabs [aria-selected="true"] p,
        .stTabs [aria-selected="true"] span {
            color: #ffffff !important;
        }

        /* ── 입력창 ────────────────────────────────────────────────── */
        div[data-testid="stTextInput"] input,
        div[data-baseweb="input"] input {
            background: var(--apple-surface) !important;
            color: var(--apple-text) !important;
            border: 1px solid var(--apple-border) !important;
            border-radius: 10px !important;
        }

        /* ── 버튼 ──────────────────────────────────────────────────── */
        div[data-testid="stForm"] button {
            background: var(--apple-blue) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 980px !important;
            font-weight: 600 !important;
            padding: 0.5rem 1.4rem !important;
        }

        div[data-testid="stForm"] button:hover {
            background: var(--apple-blue-hover) !important;
            color: #ffffff !important;
        }

        div[data-testid="stForm"] button p,
        div[data-testid="stForm"] button span {
            color: #ffffff !important;
        }

        /* ── Chat 메시지 ────────────────────────────────────────────── */
        div[data-testid="stChatMessage"] {
            background: var(--apple-surface) !important;
            border: 1px solid var(--apple-border) !important;
            border-radius: 14px !important;
            box-shadow: var(--apple-shadow) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
