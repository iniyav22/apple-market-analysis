import streamlit as st
import altair as alt
import numpy as np
import pandas as pd

from utils.data import build_quarterly_merged

st.title("Q5. How do different sentiment levels relate to return and volatility distributions?")

df = build_quarterly_merged().copy()

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

# ── Sentiment groups ───────────────────────────────────────────────────────────
group_order = ["Low sentiment", "Medium sentiment", "High sentiment"]

if len(f) >= 3 and f["sentiment_score"].nunique() >= 3:
    f["sentiment_bin"] = pd.qcut(
        f["sentiment_score"],
        q=3,
        labels=group_order,
        duplicates="drop",
    )
else:
    f["sentiment_bin"] = "All quarters"

group_counts = f["sentiment_bin"].value_counts(dropna=False)
group_count_text = " / ".join(
    [str(int(group_counts.get(label, 0))) for label in group_order if label in group_counts.index]
)

if group_count_text == "":
    group_count_text = str(len(f))

# ── Summary metrics ────────────────────────────────────────────────────────────
corr = f["sentiment_score"].corr(f["q_return"]) if len(f) >= 2 else np.nan

st.subheader("Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Quarters analysed", len(f))
col2.metric(
    "Correlation (sentiment vs return)",
    f"{corr:.3f}" if np.isfinite(corr) else "N/A",
)
col3.metric("Group counts", group_count_text)

st.divider()

# ── Shared colors ──────────────────────────────────────────────────────────────
group_colors = alt.Scale(
    domain=group_order,
    range=["#64B5F6", "#FFB74D", "#E57373"],
)

# ── Chart 1 — Return by sentiment group ───────────────────────────────────────
st.subheader("① Return by Sentiment Group")

box1 = (
    alt.Chart(f)
    .mark_boxplot(size=50)
    .encode(
        x=alt.X(
            "sentiment_bin:N",
            title="Sentiment group",
            sort=group_order,
            axis=alt.Axis(labelAngle=0),
        ),
        y=alt.Y(
            "q_return:Q",
            title="Quarterly return",
            axis=alt.Axis(format="%"),
            scale=alt.Scale(zero=False),
        ),
        color=alt.Color(
            "sentiment_bin:N",
            scale=group_colors,
            legend=alt.Legend(title="Sentiment group"),
        ),
        tooltip=[
            alt.Tooltip("quarter_label:N", title="Quarter"),
            alt.Tooltip("sentiment_bin:N", title="Sentiment group"),
            alt.Tooltip("sentiment_score:Q", title="Sentiment", format=".3f"),
            alt.Tooltip("q_return:Q", title="Return", format=".2%"),
        ],
    )
)

mean1 = (
    alt.Chart(f)
    .mark_point(size=95, color="#333333", filled=True)
    .encode(
        x=alt.X("sentiment_bin:N", sort=group_order),
        y=alt.Y("mean(q_return):Q"),
        tooltip=[
            alt.Tooltip("sentiment_bin:N", title="Sentiment group"),
            alt.Tooltip("mean(q_return):Q", title="Mean return", format=".2%"),
        ],
    )
)

chart1 = (box1 + mean1).properties(height=380)
st.altair_chart(chart1, use_container_width=True)

# ── Chart 2 — Volatility by sentiment group ───────────────────────────────────
st.subheader("② Volatility by Sentiment Group")

box2 = (
    alt.Chart(f)
    .mark_boxplot(size=50)
    .encode(
        x=alt.X(
            "sentiment_bin:N",
            title="Sentiment group",
            sort=group_order,
            axis=alt.Axis(labelAngle=0),
        ),
        y=alt.Y(
            "return_volatility:Q",
            title="Return volatility",
            scale=alt.Scale(zero=False, nice=True),
        ),
        color=alt.Color(
            "sentiment_bin:N",
            scale=group_colors,
            legend=None,
        ),
        tooltip=[
            alt.Tooltip("quarter_label:N", title="Quarter"),
            alt.Tooltip("sentiment_bin:N", title="Sentiment group"),
            alt.Tooltip("sentiment_score:Q", title="Sentiment", format=".3f"),
            alt.Tooltip("return_volatility:Q", title="Volatility", format=".3f"),
        ],
    )
)

mean2 = (
    alt.Chart(f)
    .mark_point(size=95, color="#333333", filled=True)
    .encode(
        x=alt.X("sentiment_bin:N", sort=group_order),
        y=alt.Y("mean(return_volatility):Q"),
        tooltip=[
            alt.Tooltip("sentiment_bin:N", title="Sentiment group"),
            alt.Tooltip("mean(return_volatility):Q", title="Mean volatility", format=".3f"),
        ],
    )
)

chart2 = (box2 + mean2).properties(height=380)
st.altair_chart(chart2, use_container_width=True)

# ── Chart 3 — Sentiment × Return frequency ────────────────────────────────────
st.subheader("③ Sentiment × Return Frequency")

if len(f) >= 5 and f["sentiment_score"].nunique() >= 5 and f["q_return"].nunique() >= 5:
    f["sent_heat_bin"] = pd.qcut(
        f["sentiment_score"],
        q=5,
        labels=["Very Low", "Low", "Mid", "High", "Very High"],
        duplicates="drop",
    )
    f["ret_heat_bin"] = pd.qcut(
        f["q_return"],
        q=5,
        labels=["Very Neg", "Neg", "Neutral", "Pos", "Very Pos"],
        duplicates="drop",
    )

    heat_df = (
        f.groupby(["sent_heat_bin", "ret_heat_bin"], observed=True)
        .size()
        .reset_index(name="count")
    )

    sent_order = ["Very Low", "Low", "Mid", "High", "Very High"]
    ret_order = ["Very Neg", "Neg", "Neutral", "Pos", "Very Pos"]

    heatmap = (
        alt.Chart(heat_df)
        .mark_rect(cornerRadius=3)
        .encode(
            x=alt.X(
                "sent_heat_bin:O",
                sort=sent_order,
                title="Sentiment bin",
                axis=alt.Axis(labelAngle=0),
            ),
            y=alt.Y(
                "ret_heat_bin:O",
                sort=ret_order,
                title="Return bin",
            ),
            color=alt.Color(
                "count:Q",
                scale=alt.Scale(scheme="blues"),
                legend=alt.Legend(title="# of quarters"),
            ),
            tooltip=[
                alt.Tooltip("sent_heat_bin:O", title="Sentiment"),
                alt.Tooltip("ret_heat_bin:O", title="Return"),
                alt.Tooltip("count:Q", title="Quarters"),
            ],
        )
        .properties(height=280)
    )

    text_overlay = heatmap.mark_text(
        fontSize=13,
        fontWeight="bold",
    ).encode(
        text=alt.condition(
            alt.datum.count > 0,
            alt.Text("count:Q"),
            alt.value(""),
        ),
        color=alt.condition(
            alt.datum.count >= 3,
            alt.value("white"),
            alt.value("#333"),
        ),
    )

    st.altair_chart((heatmap + text_overlay), use_container_width=True)
else:
    st.info("Not enough variation in the filtered data to create the frequency heatmap.")

# ── Optional summary table ─────────────────────────────────────────────────────
summary = (
    f.groupby("sentiment_bin", dropna=False)
    .agg(
        quarters=("quarter_label", "count"),
        avg_sentiment=("sentiment_score", "mean"),
        avg_return=("q_return", "mean"),
        median_return=("q_return", "median"),
        avg_volatility=("return_volatility", "mean"),
        median_volatility=("return_volatility", "median"),
    )
    .reset_index()
)

with st.expander("📋 Sentiment group summary"):
    st.dataframe(summary, use_container_width=True)

# ── Underlying data ────────────────────────────────────────────────────────────
with st.expander("📊 Underlying data"):
    st.dataframe(f, use_container_width=True)