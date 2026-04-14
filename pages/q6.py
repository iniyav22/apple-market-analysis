import streamlit as st
import altair as alt
import numpy as np
import pandas as pd

from utils.data import build_quarterly_merged

st.title("Q6. How does news volume relate to sentiment and stock performance over time?")

df = build_quarterly_merged().copy()
df = df.sort_values("quarter_end_date")

# ── Filters (sidebar) ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    quarters = df["quarter_label"].unique().tolist()
    start_q, end_q = st.select_slider(
        "Quarter range",
        options=quarters,
        value=(quarters[0], quarters[-1]),
    )

f = df[(df["quarter_label"] >= start_q) & (df["quarter_label"] <= end_q)].copy()
f = f.sort_values("quarter_end_date")

# ── Summary metrics ────────────────────────────────────────────────────────────
corr_news_return = f["news_count"].corr(f["q_return"]) if len(f) >= 2 else np.nan
corr_news_sent = f["news_count"].corr(f["sentiment_score"]) if len(f) >= 2 else np.nan

peak_idx = f["news_count"].idxmax() if len(f) > 0 else None
peak_quarter = f.loc[peak_idx, "quarter_label"] if peak_idx is not None else "N/A"

st.subheader("Summary")
col1, col2, col3 = st.columns(3)

col1.metric("Quarters analysed", len(f))

col2.metric(
    "Corr (news vs return)",
    f"{corr_news_return:.3f}" if np.isfinite(corr_news_return) else "N/A",
)

col3.metric(
    "Peak news quarter",
    peak_quarter if peak_quarter else "N/A",
)

st.divider()

# ── Chart 1 — Bubble chart ─────────────────────────────────────────────────────
st.subheader("① News Volume, Sentiment, and Return")

bubble = (
    alt.Chart(f)
    .mark_circle(opacity=0.8, stroke="white", strokeWidth=0.5)
    .encode(
        x=alt.X(
            "quarter_label:O",
            title="Quarter",
            axis=alt.Axis(labelAngle=-45, grid=False),
        ),
        y=alt.Y(
            "q_return:Q",
            title="Quarterly return",
            axis=alt.Axis(format="%"),
        ),
        size=alt.Size(
            "news_count:Q",
            title="News volume",
            scale=alt.Scale(range=[30, 400]),
        ),
        color=alt.Color(
            "sentiment_score:Q",
            title="Sentiment score",
            scale=alt.Scale(scheme="redblue"),
        ),
        tooltip=[
            alt.Tooltip("quarter_label:N", title="Quarter"),
            alt.Tooltip("news_count:Q", title="News count"),
            alt.Tooltip("sentiment_score:Q", title="Sentiment", format=".3f"),
            alt.Tooltip("q_return:Q", title="Return", format=".2%"),
            alt.Tooltip("return_volatility:Q", title="Volatility", format=".3f"),
        ],
    )
    .properties(height=380)
)

st.altair_chart(bubble, use_container_width=True)

# ── Chart 2 — News volume vs return (binned heatmap) ───────────────────────────
st.subheader("② News Volume × Return Distribution")

heat = (
    alt.Chart(f)
    .mark_rect(cornerRadius=2)
    .encode(
        x=alt.X(
            "news_count:Q",
            bin=alt.Bin(maxbins=8),
            title="News count",
        ),
        y=alt.Y(
            "q_return:Q",
            bin=alt.Bin(maxbins=8),
            title="Quarterly return",
        ),
        color=alt.Color(
            "count():Q",
            title="# of quarters",
            scale=alt.Scale(scheme="blues"),
        ),
        tooltip=[
            alt.Tooltip("count():Q", title="Quarters"),
        ],
    )
    .properties(height=300)
)

st.altair_chart(heat, use_container_width=True)

# ── Chart 3 — News vs sentiment trend ─────────────────────────────────────────
st.subheader("③ News Volume vs Sentiment Over Time")

line_long = (
    f[["quarter_label", "news_count", "sentiment_score"]]
    .rename(
        columns={
            "news_count": "News Volume",
            "sentiment_score": "Sentiment Score",
        }
    )
    .melt(id_vars="quarter_label", var_name="Metric", value_name="Value")
)

line_chart = (
    alt.Chart(line_long)
    .mark_line(point=alt.OverlayMarkDef(filled=True, size=55), strokeWidth=2)
    .encode(
        x=alt.X(
            "quarter_label:O",
            title="Quarter",
            axis=alt.Axis(labelAngle=-45, grid=False),
        ),
        y=alt.Y("Value:Q", title="Value"),
        color=alt.Color("Metric:N", legend=alt.Legend(title="Metric")),
        tooltip=[
            alt.Tooltip("quarter_label:N", title="Quarter"),
            alt.Tooltip("Metric:N"),
            alt.Tooltip("Value:Q", format=".3f"),
        ],
    )
    .properties(height=320)
)

st.altair_chart(line_chart, use_container_width=True)

# ── Underlying data ────────────────────────────────────────────────────────────
with st.expander("📊 Underlying data"):
    st.dataframe(
        f[
            [
                "quarter_label",
                "quarter_end_date",
                "news_count",
                "sentiment_score",
                "q_return",
                "return_volatility",
                "trading_volume",
            ]
        ],
        use_container_width=True,
    )