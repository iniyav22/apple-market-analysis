import streamlit as st
import altair as alt
import numpy as np
import pandas as pd

from utils.data import build_quarterly_merged

st.title("Q2. Do extreme sentiment quarters correspond to higher trading volume?")

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
    thr = st.slider("Extreme sentiment threshold (abs value)", 0.0, 1.0, 0.4, 0.05)

f = df[(df["quarter_label"] >= start_q) & (df["quarter_label"] <= end_q)].copy()
f["is_extreme"] = f["sentiment_score"].abs() >= thr
f["Group"] = f["is_extreme"].map({True: "Extreme", False: "Non-extreme"})

# ── Summary metrics ────────────────────────────────────────────────────────────
ext_mean  = f.loc[f["is_extreme"],  "trading_volume"].mean()
non_mean  = f.loc[~f["is_extreme"], "trading_volume"].mean()
ext_count = f["is_extreme"].sum()
non_count = (~f["is_extreme"]).sum()

if np.isfinite(ext_mean) and np.isfinite(non_mean) and non_mean != 0:
    delta_pct = (ext_mean - non_mean) / non_mean * 100
    delta_str = f"{delta_pct:+.1f}% vs Non-extreme"
else:
    delta_str = None

def fmt_b(val):
    return f"{val/1e9:.2f}B" if np.isfinite(val) else "N/A"

st.subheader("Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Extreme quarters",     ext_count)
col2.metric("Avg volume — Extreme",     fmt_b(ext_mean),  delta=delta_str)
col3.metric("Avg volume — Non-extreme", fmt_b(non_mean))

st.divider()

# shared color scale (reused across both charts)
COLOR_SCALE = alt.Scale(
    domain=["Extreme", "Non-extreme"],
    range=["#2196F3", "#FF9800"],
)

# ── Chart A — Bar ──────────────────────────────────────────────────────────────
st.subheader("① Avg Trading Volume by Group")

grp = (
    f.groupby("Group", as_index=False)["trading_volume"]
    .mean()
    .rename(columns={"trading_volume": "Avg volume"})
)
grp["label"] = grp["Avg volume"].apply(fmt_b)

bars = (
    alt.Chart(grp)
    .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
    .encode(
        x=alt.X("Group:N", title="Group", axis=alt.Axis(labelAngle=0)),
        y=alt.Y(
            "Avg volume:Q",
            title="Average Trading Volume",
            axis=alt.Axis(
                format="~s",        # e.g. 6.4G  (SI prefix)
                grid=True,
            ),
        ),
        color=alt.Color("Group:N", scale=COLOR_SCALE, legend=None),
        tooltip=[
            alt.Tooltip("Group:N"),
            alt.Tooltip("Avg volume:Q", title="Avg Volume", format=",.0f"),
        ],
    )
    .properties(height=320)
)

bar_labels = (
    alt.Chart(grp)
    .mark_text(dy=-8, fontSize=13, fontWeight="bold")
    .encode(
        x=alt.X("Group:N"),
        y=alt.Y("Avg volume:Q"),
        text=alt.Text("label:N"),
        color=alt.Color("Group:N", scale=COLOR_SCALE, legend=None),
    )
)

st.altair_chart(bars + bar_labels, use_container_width=True)

# ── Chart B — Scatter with threshold lines ─────────────────────────────────────
st.subheader("② Sentiment vs. Trading Volume")

pts = (
    alt.Chart(f)
    .mark_circle(size=75, opacity=0.8, stroke="white", strokeWidth=0.5)
    .encode(
        x=alt.X(
            "sentiment_score:Q",
            title="Quarterly Average News Sentiment",
            axis=alt.Axis(grid=False),
        ),
        y=alt.Y(
            "trading_volume:Q",
            title="Trading Volume",
            axis=alt.Axis(format="~s", grid=True),
        ),
        color=alt.Color("Group:N", scale=COLOR_SCALE,
                        legend=alt.Legend(title="Group")),
        tooltip=[
            alt.Tooltip("quarter_label:N",   title="Quarter"),
            alt.Tooltip("sentiment_score:Q", title="Sentiment", format=".3f"),
            alt.Tooltip("trading_volume:Q",  title="Volume",    format=",.0f"),
            alt.Tooltip("Group:N",           title="Group"),
        ],
    )
    .properties(height=400)
)

# dashed threshold lines at x = +thr and x = -thr
thr_df = pd.DataFrame({"x": [thr, -thr], "label": [f"+{thr}", f"−{thr}"]})

thr_lines = (
    alt.Chart(thr_df)
    .mark_rule(strokeDash=[5, 4], strokeWidth=1.5, color="#888")
    .encode(x=alt.X("x:Q"))
)

thr_labels = (
    alt.Chart(thr_df)
    .mark_text(align="left", dx=4, dy=-8, fontSize=11, color="#666")
    .encode(
        x=alt.X("x:Q"),
        y=alt.value(10),
        text=alt.Text("label:N"),
    )
)

st.altair_chart(pts + thr_lines + thr_labels, use_container_width=True)

# ── Underlying data ────────────────────────────────────────────────────────────
with st.expander("📊 Underlying data"):
    st.dataframe(f, use_container_width=True)