import streamlit as st
import altair as alt
import numpy as np
import pandas as pd

from utils.data import build_quarterly_merged

st.title("Q3. Do sentiment spikes precede larger price volatility?")

df = build_quarterly_merged().copy()
df = df.sort_values("quarter_end_date").reset_index(drop=True)

# ── Filters (sidebar) ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    quarters = df["quarter_label"].unique().tolist()
    start_q, end_q = st.select_slider(
        "Quarter range (for the volatility quarter)",
        options=quarters,
        value=(quarters[0], quarters[-1]),
    )
    lag = st.slider("Lag (quarters): sentiment from how many quarters earlier?", 1, 4, 1)
    use_reg = st.checkbox("Show regression line", value=True)

# ── Data prep ──────────────────────────────────────────────────────────────────
xcol = f"sentiment_lag_{lag}"
df[xcol] = df["sentiment_score"].shift(lag)

f = df[(df["quarter_label"] >= start_q) & (df["quarter_label"] <= end_q)].copy()
f = f.dropna(subset=[xcol, "return_volatility"])

# high-volatility flag: mean + 1 SD
vol_mean = f["return_volatility"].mean()
vol_sd   = f["return_volatility"].std()
vol_thr  = vol_mean + vol_sd
f["vol_group"] = f["return_volatility"].apply(
    lambda v: "High volatility" if v >= vol_thr else "Normal"
)

# ── Correlation & interpretation ───────────────────────────────────────────────
corr = f[xcol].corr(f["return_volatility"]) if len(f) >= 2 else np.nan

def interpret_corr(r):
    if not np.isfinite(r):
        return "N/A"
    a = abs(r)
    direction = "positive" if r > 0 else "negative"
    if a >= 0.5:   strength = "Strong"
    elif a >= 0.3: strength = "Moderate"
    elif a >= 0.1: strength = "Weak"
    else:          strength = "Negligible"
    return f"{strength} {direction} relationship"

# ── Summary metrics ────────────────────────────────────────────────────────────
st.subheader("Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Quarters analysed", len(f))
col2.metric(
    f"Correlation (lag {lag}Q)",
    f"{corr:.3f}" if np.isfinite(corr) else "N/A",
)
# Interpretation: use markdown to allow text wrap instead of st.metric (which truncates)
with col3:
    st.markdown("**Interpretation**")
    st.markdown(
        f"<p style='font-size:1.4rem; font-weight:400; line-height:1.3; margin-top:0px; word-break:break-word; white-space:normal;'>{interpret_corr(corr)}</p>",
        unsafe_allow_html=True,
    )

st.divider()

# ── Chart 1 — Scatter: lagged sentiment vs volatility ─────────────────────────
st.subheader(f"① Lagged Sentiment vs. Volatility  ·  Sentiment t−{lag} → Volatility t")

color_scale = alt.Scale(
    domain=["Normal", "High volatility"],
    range=["#2196F3", "#E53935"],
)

base = alt.Chart(f).encode(
    x=alt.X(
        f"{xcol}:Q",
        title=f"Sentiment (lag {lag} quarter{'s' if lag > 1 else ''})",
        axis=alt.Axis(grid=False),
    ),
    y=alt.Y(
        "return_volatility:Q",
        title="Quarterly Return Volatility",
        axis=alt.Axis(grid=True),
    ),
    color=alt.Color(
        "vol_group:N",
        scale=color_scale,
        legend=alt.Legend(title="Volatility group"),
    ),
    tooltip=[
        alt.Tooltip("quarter_label:N",     title="Quarter"),
        alt.Tooltip(f"{xcol}:Q",           title=f"Sentiment (t−{lag})", format=".3f"),
        alt.Tooltip("sentiment_score:Q",   title="Sentiment (current)",  format=".3f"),
        alt.Tooltip("return_volatility:Q", title="Volatility",           format=".4f"),
        alt.Tooltip("vol_group:N",         title="Group"),
    ],
)

pts = base.mark_circle(size=80, opacity=0.85, stroke="white", strokeWidth=0.5)

thr_df = pd.DataFrame({"y": [vol_thr]})
thr_line = (
    alt.Chart(thr_df)
    .mark_rule(strokeDash=[5, 4], strokeWidth=1.8, color="#E53935")
    .encode(y=alt.Y("y:Q"))
)

if use_reg and len(f) >= 2:
    reg = (
        alt.Chart(f)
        .transform_regression(xcol, "return_volatility")
        .mark_line(strokeWidth=2.5, color="#FF9800", strokeDash=[6, 3])
        .encode(x=f"{xcol}:Q", y="return_volatility:Q")
    )
    scatter_chart = (pts + thr_line + reg).properties(height=380)
else:
    scatter_chart = (pts + thr_line).properties(height=380)

# inline legend row between title and chart
reg_legend_html = (
    "<span style='color:#FF9800; font-size:15px; letter-spacing:2px;'>╌╌</span>"
    "&nbsp;<span style='font-size:12px; color:#444;'>Regression line</span>"
) if use_reg else ""

st.markdown(
    f"""
    <div style='display:flex; gap:24px; align-items:center; margin-bottom:4px;'>
        <span style='color:#E53935; font-size:15px; letter-spacing:2px;'>╌╌</span>
        <span style='font-size:12px; color:#444; margin-left:-18px;'>High volatility threshold (μ+1σ = {vol_thr:.4f})</span>
        {reg_legend_html}
    </div>
    """,
    unsafe_allow_html=True,
)
st.altair_chart(scatter_chart, use_container_width=True)

# ── Chart 2 — Dual y-axis time-series line ────────────────────────────────────
st.subheader(f"② Quarterly Trend  ·  Sentiment t−{lag} leads Volatility t")

sent_col = f"Sentiment (t−{lag})"

# sentiment layer (left axis)
sent_line = (
    alt.Chart(f)
    .mark_line(
        point=alt.OverlayMarkDef(filled=True, size=50, color="#1565C0"),
        strokeWidth=2,
        color="#1565C0",
    )
    .encode(
        x=alt.X(
            "quarter_label:O",
            title="Quarter",
            axis=alt.Axis(labelAngle=-45, grid=False),
        ),
        y=alt.Y(
            f"{xcol}:Q",
            title="Sentiment Score",
            axis=alt.Axis(titleColor="#1565C0", grid=True),
        ),
        tooltip=[
            alt.Tooltip("quarter_label:N", title="Quarter"),
            alt.Tooltip(f"{xcol}:Q", title=f"Sentiment (t−{lag})", format=".3f"),
        ],
    )
)

# volatility layer (right axis)
vol_line = (
    alt.Chart(f)
    .mark_line(
        point=alt.OverlayMarkDef(filled=True, size=50, color="#E53935"),
        strokeWidth=2,
        color="#E53935",
        strokeDash=[4, 2],
    )
    .encode(
        x=alt.X("quarter_label:O"),
        y=alt.Y(
            "return_volatility:Q",
            title="Return Volatility",
            axis=alt.Axis(titleColor="#E53935"),
        ),
        tooltip=[
            alt.Tooltip("quarter_label:N", title="Quarter"),
            alt.Tooltip("return_volatility:Q", title="Volatility", format=".4f"),
        ],
    )
)

line_chart = (
    alt.layer(sent_line, vol_line)
    .resolve_scale(y="independent")
    .properties(height=320)
)

st.altair_chart(line_chart, use_container_width=True)
st.caption("🔵 Left axis — Sentiment Score (t−N)　　🔴 Right axis — Return Volatility (t)")

# ── Underlying data ────────────────────────────────────────────────────────────
with st.expander("📊 Underlying data"):
    st.dataframe(f, use_container_width=True)