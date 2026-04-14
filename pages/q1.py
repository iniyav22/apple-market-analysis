import streamlit as st
import altair as alt
import numpy as np
import pandas as pd

from utils.data import build_quarterly_merged

st.title("Q1. Is quarterly news sentiment associated with Apple's quarterly stock return?")

df = build_quarterly_merged()

# ── Filters (sidebar) ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    quarters = df["quarter_label"].unique().tolist()
    start_q, end_q = st.select_slider(
        "Quarter range",
        options=quarters,
        value=(quarters[0], quarters[-1]),
    )
    use_reg = st.checkbox("Show regression line", value=True)

f = df[(df["quarter_label"] >= start_q) & (df["quarter_label"] <= end_q)].copy()
f["return_dir"] = f["q_return"].apply(lambda x: "Positive" if x >= 0 else "Negative")

# ── Summary metrics ────────────────────────────────────────────────────────────
corr = f["sentiment_score"].corr(f["q_return"]) if len(f) >= 2 else np.nan
pos_count = (f["q_return"] >= 0).sum()
neg_count = (f["q_return"] < 0).sum()

st.subheader("Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Quarters analysed", len(f))
col2.metric(
    "Correlation (sentiment vs return)",
    f"{corr:.3f}" if np.isfinite(corr) else "N/A",
)
col3.metric("Positive / Negative quarters", f"{pos_count} / {neg_count}")

st.divider()

# ── Chart 1 — Scatter ──────────────────────────────────────────────────────────
st.subheader("① Sentiment vs. Return")

color_scale = alt.Scale(
    domain=["Positive", "Negative"],
    range=["#2196F3", "#E53935"],
)

zero_line = (
    alt.Chart(pd.DataFrame({"y": [0]}))
    .mark_rule(strokeDash=[5, 4], color="#888", strokeWidth=1)
    .encode(y=alt.Y("y:Q"))
)

base = alt.Chart(f).encode(
    x=alt.X(
        "sentiment_score:Q",
        title="Quarterly average news sentiment",
        axis=alt.Axis(grid=False),
    ),
    y=alt.Y(
        "q_return:Q",
        title="Quarterly stock return",
        axis=alt.Axis(grid=True, format="%"),
    ),
    color=alt.Color(
        "return_dir:N",
        scale=color_scale,
        legend=alt.Legend(title="Return direction"),
    ),
    tooltip=[
        alt.Tooltip("quarter_label:N", title="Quarter"),
        alt.Tooltip("sentiment_score:Q", title="Sentiment", format=".3f"),
        alt.Tooltip("q_return:Q", title="Return", format=".2%"),
        alt.Tooltip("news_count:Q", title="News count"),
    ],
)

pts = base.mark_circle(size=80, opacity=0.85, stroke="white", strokeWidth=0.5)

if use_reg and len(f) >= 2:
    reg = (
        alt.Chart(f)
        .transform_regression("sentiment_score", "q_return")
        .mark_line(
            strokeWidth=2.5,
            color="#FF9800",
            strokeDash=[6, 3],
        )
        .encode(
            x="sentiment_score:Q",
            y="q_return:Q",
        )
    )
    scatter_chart = (zero_line + pts + reg).properties(height=380)
else:
    scatter_chart = (zero_line + pts).properties(height=380)

st.altair_chart(scatter_chart, use_container_width=True)

# ── Chart 2 — Heatmap ─────────────────────────────────────────────────────────
st.subheader("② Sentiment Bin × Return Bin")

f["sent_bin"] = pd.cut(
    f["sentiment_score"],
    bins=5,
    labels=["Very Low", "Low", "Mid", "High", "Very High"],
)
f["ret_bin"] = pd.cut(
    f["q_return"],
    bins=5,
    labels=["Very Neg", "Neg", "Neutral", "Pos", "Very Pos"],
)

heat_df = (
    f.groupby(["sent_bin", "ret_bin"], observed=True)
    .size()
    .reset_index(name="count")
)

sent_order = ["Very Low", "Low", "Mid", "High", "Very High"]
ret_order  = ["Very Neg", "Neg", "Neutral", "Pos", "Very Pos"]

heatmap = (
    alt.Chart(heat_df)
    .mark_rect(cornerRadius=3)
    .encode(
        x=alt.X(
            "sent_bin:O",
            sort=sent_order,
            title="Sentiment bin",
            axis=alt.Axis(labelAngle=0),
        ),
        y=alt.Y("ret_bin:O", sort=ret_order, title="Return bin"),
        color=alt.Color(
            "count:Q",
            scale=alt.Scale(scheme="blues"),
            legend=alt.Legend(title="# of quarters"),
        ),
        tooltip=[
            alt.Tooltip("sent_bin:O", title="Sentiment"),
            alt.Tooltip("ret_bin:O", title="Return"),
            alt.Tooltip("count:Q", title="Quarters"),
        ],
    )
    .properties(height=280)
)

text_overlay = heatmap.mark_text(
    fontSize=13, fontWeight="bold"
).encode(
    text=alt.condition(
        alt.datum.count > 0, alt.Text("count:Q"), alt.value("")
    ),
    color=alt.condition(
        alt.datum.count >= 3, alt.value("white"), alt.value("#333")
    ),
)

st.altair_chart((heatmap + text_overlay), use_container_width=True)

# ── Chart 3 — Dual time-series line ───────────────────────────────────────────
st.subheader("③ Quarterly Trend: Sentiment & Return Over Time")

line_long = (
    f[["quarter_label", "sentiment_score", "q_return"]]
    .rename(columns={"sentiment_score": "Sentiment Score", "q_return": "Stock Return"})
    .melt(id_vars="quarter_label", var_name="Metric", value_name="Value")
)

color_line = alt.Scale(
    domain=["Sentiment Score", "Stock Return"],
    range=["#1565C0", "#E53935"],
)

line_chart = (
    alt.Chart(line_long)
    .mark_line(
        point=alt.OverlayMarkDef(filled=True, size=55),
        strokeWidth=2,
    )
    .encode(
        x=alt.X(
            "quarter_label:O",
            title="Quarter",
            axis=alt.Axis(labelAngle=-45, grid=False),
        ),
        y=alt.Y(
            "Value:Q",
            title="Value",
            axis=alt.Axis(grid=True),
        ),
        color=alt.Color("Metric:N", scale=color_line, legend=alt.Legend(title="Metric")),
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
    st.dataframe(f, use_container_width=True)