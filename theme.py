import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        :root {
            --science-blue: #0A84FF;
            --science-blue-soft: rgba(10, 132, 255, 0.10);
            --shark: #1D1D1F;
            --shark-2: #23252A;
            --athens-gray: #F5F7FA;
            --white: #FFFFFF;
            --muted: #C7CDD6;
            --border: rgba(255,255,255,0.08);
        }

        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display",
                         "SF Pro Text", "Segoe UI", sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at top right, rgba(10,132,255,0.08), transparent 24%),
                linear-gradient(180deg, #17181B 0%, #1D1D1F 100%);
            color: var(--white);
        }

        .block-container {
            max-width: 1220px;
            padding-top: 1rem;
            padding-bottom: 2rem;
        }

        header[data-testid="stHeader"] {
            background: rgba(29, 29, 31, 0.92);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border);
        }

        nav[aria-label="Page navigation"] {
            border-bottom: 1px solid var(--border);
        }

        h1, h2, h3 {
            color: var(--white);
            letter-spacing: -0.03em;
        }

        div[data-testid="stVegaLiteChart"] {
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 18px;
            padding: 0.35rem;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            overflow: hidden;
        }

        .hero-card {
            background: linear-gradient(135deg, rgba(10,132,255,0.10), rgba(255,255,255,0.02));
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 24px;
            padding: 1.2rem 1.3rem;
            margin-bottom: 1rem;
            box-shadow: 0 10px 28px rgba(0,0,0,0.18);
        }

        .hero-title {
            font-size: 1.65rem;
            font-weight: 700;
            line-height: 1.15;
            color: var(--white);
            margin-bottom: 0.4rem;
            letter-spacing: -0.03em;
        }

        .hero-subtext {
            font-size: 0.98rem;
            color: var(--muted);
            line-height: 1.6;
            max-width: 860px;
        }

        .pill {
            display: inline-block;
            padding: 0.34rem 0.72rem;
            margin-right: 0.45rem;
            margin-top: 0.65rem;
            border-radius: 999px;
            background: rgba(10,132,255,0.10);
            border: 1px solid rgba(10,132,255,0.20);
            color: #D9ECFF;
            font-size: 0.82rem;
            font-weight: 600;
        }

        .mini-card {
            background: #F5F7FA;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 1rem;
            min-height: 110px;
        }

        .mini-label {
            font-size: 0.84rem;
            color: #5B6573;
            margin-bottom: 0.35rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .mini-value {
            font-size: 1.35rem;
            line-height: 1.25;
            font-weight: 700;
            color: #1D1D1F;
        }

        .section-card {
            background: rgba(255,255,255,0.035);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 20px;
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
        }

        .section-title {
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
            color: var(--white);
        }

        .section-text {
            color: var(--muted);
            line-height: 1.6;
            font-size: 0.96rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 999px;
            padding: 0.35rem 0.9rem;
            background: rgba(255,255,255,0.03);
        }

        .stTabs [aria-selected="true"] {
            background: rgba(10,132,255,0.12) !important;
            border: 1px solid rgba(10,132,255,0.24) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )