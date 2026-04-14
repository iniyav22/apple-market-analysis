import streamlit as st
import altair as alt
import numpy as np
import pandas as pd

from utils.data import build_quarterly_merged

st.title("Q4. How has Apple’s stock return evolved over time?")

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
f["return_dir"] = f["q_return"].apply(lambda x: "Positive" if x >= 0 else "Negative")
f["cumulative_return"] = (1 + f["q_return"]).cumprod() - 1

# ── Summary metrics ────────────────────────────────────────────────────────────
avg_return = f["q_return"].mean() if len(f) > 0 else np.nan
best_q = f["q_return"].max() if len(f) > 0 else np.nan
worst_q = f["q_return"].min() if len(f) > 0 else np.nan

st.subheader("Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Quarters analysed", len(f))
col2.metric(
    "Average quarterly return",
    f"{avg_return:.2%}" if np.isfinite(avg_return) else "N/A",
)
if np.isfinite(best_q) and np.isfinite(worst_q):
    col3.metric("Best / Worst quarter", f"{best_q:.2%} / {worst_q:.2%}")
else:
    col3.metric("Best / Worst quarter", "N/A")

st.divider()

# ── Chart 1 — Quarterly return bars ───────────────────────────────────────────
st.subheader("① Quarterly Return Over Time")

mean_return = f["q_return"].mean() if len(f) > 0 else np.nan
std_return = f["q_return"].std() if len(f) > 1 else np.nan

bar_colors = alt.Scale(
    domain=["Positive", "Negative"],
    range=["#2196F3", "#E53935"],
)

bars = (
    alt.Chart(f)
    .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
    .encode(
        x=alt.X(
            "quarter_label:O",
            title="Quarter",
            axis=alt.Axis(labelAngle=-45, grid=False),
        ),
        y=alt.Y(
            "q_return:Q",
            title="Quarterly stock return",
            axis=alt.Axis(format="%"),
        ),
        color=alt.Color(
            "return_dir:N",
            scale=bar_colors,
            legend=alt.Legend(title="Return direction"),
        ),
        tooltip=[
            alt.Tooltip("quarter_label:N", title="Quarter"),
            alt.Tooltip("quarter_end_date:T", title="Quarter end"),
            alt.Tooltip("q_return:Q", title="Return", format=".2%"),
        ],
    )
)

zero_line = (
    alt.Chart(pd.DataFrame({"y": [0]}))
    .mark_rule(strokeDash=[5, 4], color="#888", strokeWidth=1)
    .encode(y="y:Q")
)

layers = [zero_line, bars]

if np.isfinite(mean_return):
    mean_line = (
        alt.Chart(pd.DataFrame({"y": [mean_return]}))
        .mark_rule(color="#FF9800", strokeWidth=2)
        .encode(
            y="y:Q",
            tooltip=[alt.Tooltip("y:Q", title="Mean return", format=".2%")],
        )
    )
    layers.append(mean_line)

if np.isfinite(std_return):
    upper_sd = (
        alt.Chart(pd.DataFrame({"y": [mean_return + std_return]}))
        .mark_rule(color="#6A1B9A", strokeDash=[6, 3], strokeWidth=1.5)
        .encode(
            y="y:Q",
            tooltip=[alt.Tooltip("y:Q", title="+1 SD", format=".2%")],
        )
    )
    lower_sd = (
        alt.Chart(pd.DataFrame({"y": [mean_return - std_return]}))
        .mark_rule(color="#6A1B9A", strokeDash=[6, 3], strokeWidth=1.5)
        .encode(
            y="y:Q",
            tooltip=[alt.Tooltip("y:Q", title="-1 SD", format=".2%")],
        )
    )
    layers.extend([upper_sd, lower_sd])

return_chart = alt.layer(*layers).properties(height=380)
st.altair_chart(return_chart, use_container_width=True)

# ── Chart 2 — Cumulative return ───────────────────────────────────────────────
st.subheader("② Cumulative Return Over Time")

cum_chart = (
    alt.Chart(f)
    .mark_line(point=alt.OverlayMarkDef(filled=True, size=55), strokeWidth=2.5)
    .encode(
        x=alt.X(
            "quarter_label:O",
            title="Quarter",
            axis=alt.Axis(labelAngle=-45, grid=False),
        ),
        y=alt.Y(
            "cumulative_return:Q",
            title="Cumulative return",
            axis=alt.Axis(format="%"),
        ),
        tooltip=[
            alt.Tooltip("quarter_label:N", title="Quarter"),
            alt.Tooltip("cumulative_return:Q", title="Cumulative return", format=".2%"),
            alt.Tooltip("q_return:Q", title="Quarterly return", format=".2%"),
        ],
    )
    .properties(height=320)
)

st.altair_chart(cum_chart, use_container_width=True)

# ── Underlying data ────────────────────────────────────────────────────────────
with st.expander("📊 Underlying data"):
    st.dataframe(f, use_container_width=True)