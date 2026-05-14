import streamlit as st
import altair as alt
import pandas as pd
import gcsfs
import matplotlib.pyplot as plt
from utils.data import load_base_data

# ── Data loading ───────────────────────────────────────────────────────────────
BUCKET   = "wr5477_utds"
M8_GCS   = f"gs://{BUCKET}/m8"

@st.cache_data
def load_m8_data():
    fs = gcsfs.GCSFileSystem()
    with fs.open(f"{M8_GCS}/backtest_2024.parquet", "rb") as f:
        backtest = pd.read_parquet(f)
    with fs.open(f"{M8_GCS}/forecast_2025.parquet", "rb") as f:
        forecast = pd.read_parquet(f)
    with fs.open(f"{M8_GCS}/model_comparison.parquet", "rb") as f:
        comparison = pd.read_parquet(f)
    return backtest, forecast, comparison

backtest, forecast, comparison = load_m8_data()

@st.cache_data(show_spinner=False)
def load_input_overview():
    fin, news = load_base_data()
    fin_reset = fin.reset_index()  # quarter_end → column

    # Daily news → quarterly sentiment
    news_idx = news.copy()
    news_idx.index = pd.to_datetime(news_idx.index, errors="coerce")
    if getattr(news_idx.index, "tz", None) is not None:
        news_idx.index = news_idx.index.tz_convert(None)
    news_idx["q_period"] = news_idx.index.to_period("Q")
    news_q = (
        news_idx.groupby("q_period")
        .agg(sentiment_score=("sentiment_score", "mean"))
        .reset_index()
    )
    news_q["quarter_end"] = news_q["q_period"].dt.end_time.dt.normalize()

    fin_sent = fin_reset.merge(news_q[["quarter_end", "sentiment_score"]], on="quarter_end", how="inner")
    fin_sent = fin_sent[
        (fin_sent["quarter_end"] >= pd.Timestamp("2016-01-01")) &
        (fin_sent["quarter_end"] < pd.Timestamp("2025-01-01"))
    ]
    return fin_reset, fin_sent

fin_full, fin_sent = load_input_overview()

# ── Page header ────────────────────────────────────────────────────────────────
st.title("Apple Stock Price Forecasting")
st.markdown(
    """
    This page applies three **zero-shot foundation models** to forecast Apple's quarterly
    closing stock price — no fine-tuning, inference only.

    | Model | Input | Method |
    |-------|-------|--------|
    | **TimesFM 2.0** (Google DeepMind, 500M) | Price only | Vertex AI endpoint |
    | **Chronos-2 Bolt** (Amazon, 200M) | Price only | Local inference (CPU) |
    | **Gemini 1.5 Flash** (Google) | Price + Sentiment | Direct prompt (manual) |
    """
)

# ── Input Series Overview ─────────────────────────────────────────────────────
with st.expander("📈 Input Series Overview", expanded=True):
    fig, axes = plt.subplots(1, 2, figsize=(14, 3.8))
    fig.suptitle("Input Series Overview", fontsize=13, fontweight="bold")

    # Left: full AAPL price history
    axes[0].plot(fin_full["quarter_end"], fin_full["close_price"],
                 color="steelblue", linewidth=1.4, marker="o", markersize=2)
    axes[0].axvline(pd.Timestamp("2024-01-01"), color="red", linestyle="--",
                    alpha=0.7, label="2024 split")
    axes[0].set_title("AAPL Quarterly Close Price (Full History)")
    axes[0].set_ylabel("Close Price (USD)")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Right: sentiment bars + price line (2016–2024)
    ax2 = axes[1].twinx()
    axes[1].bar(fin_sent["quarter_end"], fin_sent["sentiment_score"],
                width=60, alpha=0.4, color="coral", label="Sentiment")
    ax2.plot(fin_sent["quarter_end"], fin_sent["close_price"],
             color="steelblue", linewidth=2, label="Close Price")
    axes[1].axvline(pd.Timestamp("2024-01-01"), color="red", linestyle="--", alpha=0.7)
    axes[1].set_title("Price vs News Sentiment (2016–2024)")
    axes[1].set_ylabel("Sentiment Score", color="coral")
    ax2.set_ylabel("Close Price (USD)", color="steelblue")
    axes[1].legend(loc="upper left")
    ax2.legend(loc="upper right")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

st.divider()

# ── Summary metrics ────────────────────────────────────────────────────────────
st.subheader("2024 Backtest Summary")

mae_tfm  = comparison.loc[comparison["Model"] == "TimesFM 2.0",  "MAE ($)"].values[0]
mae_chr  = comparison.loc[comparison["Model"] == "Chronos-2 Bolt","MAE ($)"].values[0]
mae_gem  = comparison.loc[comparison["Model"] == "Gemini 1.5 Flash","MAE ($)"].values[0]

c1, c2, c3 = st.columns(3)
c1.metric("TimesFM 2.0 MAE", f"${mae_tfm:.2f}", delta="Scale distortion", delta_color="inverse")
c2.metric("Chronos-2 MAE",   f"${mae_chr:.2f}", delta="Price only")
c3.metric("Gemini 1.5 MAE",  f"${mae_gem:.2f}", delta="Best · Price + Sentiment", delta_color="normal")

st.divider()

# ── Shared helper: historical context ─────────────────────────────────────────
def make_hist_context(fin_df, n_quarters, before_year):
    """Last n_quarters of fin_df before before_year, formatted as a series df."""
    fq = fin_df.copy()
    fq["quarter_end"] = pd.to_datetime(fq["quarter_end"])
    fq = fq[fq["quarter_end"] < pd.Timestamp(f"{before_year}-01-01")]
    fq = fq.sort_values("quarter_end").tail(n_quarters)
    period = fq["quarter_end"].dt.to_period("Q")
    fq["quarter_label"] = "Q" + period.dt.quarter.astype(str) + " " + period.dt.year.astype(str)
    return (
        fq[["quarter_label", "close_price"]]
        .rename(columns={"close_price": "price"})
        .assign(series="Historical context")
    )

# ── Chart 1: 2024 Backtest ─────────────────────────────────────────────────────
st.subheader("① 2024 Backtest — Predicted vs. Actual")
st.caption("Zero-shot quarterly close price prediction for Q1–Q4 2024.")

bt = backtest.copy()
bt["quarter_label"] = bt["quarter_label"].astype(str)

bt_long = pd.melt(
    bt,
    id_vars=["quarter_label"],
    value_vars=["actual", "timesfm_forecast", "chronos2_forecast", "gemini_forecast"],
    var_name="series",
    value_name="price",
)
bt_long["series"] = bt_long["series"].map({
    "actual":            "Actual",
    "timesfm_forecast":  "TimesFM 2.0",
    "chronos2_forecast": "Chronos-2",
    "gemini_forecast":   "Gemini + Sentiment",
})

show_hist_bt = st.toggle("Show historical context (last 12 quarters)", value=True, key="toggle_bt")

if show_hist_bt:
    hist_bt   = make_hist_context(fin_full, n_quarters=12, before_year=2024)
    bt_all    = pd.concat([hist_bt, bt_long], ignore_index=True)
    all_q_bt  = list(hist_bt["quarter_label"]) + list(bt["quarter_label"])

    line_bt = (
        alt.Chart(bt_all)
        .mark_line(point=alt.OverlayMarkDef(filled=True, size=60), strokeWidth=2.2)
        .encode(
            x=alt.X("quarter_label:O", sort=all_q_bt, title="Quarter",
                    axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("price:Q", title="Close Price (USD)", scale=alt.Scale(zero=False)),
            color=alt.Color("series:N",
                scale=alt.Scale(
                    domain=["Historical context", "Actual", "TimesFM 2.0", "Chronos-2", "Gemini + Sentiment"],
                    range=["#AAAAAA",             "#000000", "#4C72B0",     "#DD8452",   "#59A14F"],
                ),
                legend=alt.Legend(title="Model"),
            ),
            strokeDash=alt.StrokeDash("series:N",
                scale=alt.Scale(
                    domain=["Historical context", "Actual", "TimesFM 2.0", "Chronos-2", "Gemini + Sentiment"],
                    range=[[1, 0],                [1, 0],    [6, 3],         [6, 3],      [6, 3]],
                ),
            ),
            tooltip=[
                alt.Tooltip("quarter_label:N", title="Quarter"),
                alt.Tooltip("series:N",        title="Model"),
                alt.Tooltip("price:Q",         title="Price (USD)", format="$.2f"),
            ],
        )
        .properties(height=380)
    )
    split_bt = (
        alt.Chart(pd.DataFrame({"quarter_label": [bt["quarter_label"].iloc[0]]}))
        .mark_rule(strokeDash=[4, 4], color="red", opacity=0.6, strokeWidth=1.5)
        .encode(x=alt.X("quarter_label:O", sort=all_q_bt))
    )
    st.altair_chart(line_bt + split_bt, use_container_width=True)

else:
    bt_chart = (
        alt.Chart(bt_long)
        .mark_line(point=alt.OverlayMarkDef(filled=True, size=80), strokeWidth=2.5)
        .encode(
            x=alt.X("quarter_label:O", title="Quarter", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("price:Q", title="Close Price (USD)", scale=alt.Scale(zero=False)),
            color=alt.Color("series:N",
                scale=alt.Scale(
                    domain=["Actual", "TimesFM 2.0", "Chronos-2", "Gemini + Sentiment"],
                    range=["#000000",  "#4C72B0",     "#DD8452",   "#59A14F"],
                ),
                legend=alt.Legend(title="Model"),
            ),
            strokeDash=alt.StrokeDash("series:N",
                scale=alt.Scale(
                    domain=["Actual", "TimesFM 2.0", "Chronos-2", "Gemini + Sentiment"],
                    range=[[1, 0],     [6, 3],         [6, 3],      [6, 3]],
                ),
            ),
            tooltip=[
                alt.Tooltip("quarter_label:N", title="Quarter"),
                alt.Tooltip("series:N",        title="Model"),
                alt.Tooltip("price:Q",         title="Price (USD)", format="$.2f"),
            ],
        )
        .properties(height=360)
    )
    st.altair_chart(bt_chart, use_container_width=True)

with st.expander("📊 Backtest data"):
    st.dataframe(backtest, use_container_width=True)

st.divider()

# ── Chart 2: 2025 Forecast vs Actual ──────────────────────────────────────────
st.subheader("② 2025 Forecast vs. Actual")
st.caption(
    "Forward forecast for Q1–Q4 2025. Ground truth is now available — "
    "Chronos-2 tracks actual prices more closely than TimesFM."
)

fc = forecast.copy()
fc["quarter_label"] = fc["quarter_label"].astype(str)

fc_long = pd.melt(
    fc,
    id_vars=["quarter_label"],
    value_vars=["actual", "timesfm_forecast", "chronos2_forecast"],
    var_name="series",
    value_name="price",
)
fc_long["series"] = fc_long["series"].map({
    "actual":            "Actual 2025",
    "timesfm_forecast":  "TimesFM 2.0",
    "chronos2_forecast": "Chronos-2",
})

show_hist_fc = st.toggle("Show historical context (last 12 quarters)", value=True, key="toggle_fc")

if show_hist_fc:
    hist_fc   = make_hist_context(fin_full, n_quarters=12, before_year=2025)
    fc_all    = pd.concat([hist_fc, fc_long], ignore_index=True)
    all_q_fc  = list(hist_fc["quarter_label"]) + list(fc["quarter_label"])

    line_fc = (
        alt.Chart(fc_all)
        .mark_line(point=alt.OverlayMarkDef(filled=True, size=60), strokeWidth=2.2)
        .encode(
            x=alt.X("quarter_label:O", sort=all_q_fc, title="Quarter",
                    axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("price:Q", title="Close Price (USD)", scale=alt.Scale(zero=False)),
            color=alt.Color("series:N",
                scale=alt.Scale(
                    domain=["Historical context", "Actual 2025", "TimesFM 2.0", "Chronos-2"],
                    range=["#AAAAAA",             "#000000",      "#4C72B0",     "#DD8452"],
                ),
                legend=alt.Legend(title="Model"),
            ),
            strokeDash=alt.StrokeDash("series:N",
                scale=alt.Scale(
                    domain=["Historical context", "Actual 2025", "TimesFM 2.0", "Chronos-2"],
                    range=[[1, 0],                [1, 0],          [6, 3],         [6, 3]],
                ),
            ),
            tooltip=[
                alt.Tooltip("quarter_label:N", title="Quarter"),
                alt.Tooltip("series:N",        title="Model"),
                alt.Tooltip("price:Q",         title="Price (USD)", format="$.2f"),
            ],
        )
        .properties(height=380)
    )
    split_fc = (
        alt.Chart(pd.DataFrame({"quarter_label": [fc["quarter_label"].iloc[0]]}))
        .mark_rule(strokeDash=[4, 4], color="red", opacity=0.6, strokeWidth=1.5)
        .encode(x=alt.X("quarter_label:O", sort=all_q_fc))
    )
    ci_tfm_h = (
        alt.Chart(fc)
        .mark_area(opacity=0.12, color="#4C72B0")
        .encode(x=alt.X("quarter_label:O", sort=all_q_fc), y="timesfm_q10:Q", y2="timesfm_q90:Q")
    )
    ci_chr_h = (
        alt.Chart(fc)
        .mark_area(opacity=0.12, color="#DD8452")
        .encode(x=alt.X("quarter_label:O", sort=all_q_fc), y="chronos2_q10:Q", y2="chronos2_q90:Q")
    )
    st.altair_chart(ci_tfm_h + ci_chr_h + line_fc + split_fc, use_container_width=True)

else:
    fc_chart = (
        alt.Chart(fc_long)
        .mark_line(point=alt.OverlayMarkDef(filled=True, size=80), strokeWidth=2.5)
        .encode(
            x=alt.X("quarter_label:O", title="Quarter", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("price:Q", title="Close Price (USD)", scale=alt.Scale(zero=False)),
            color=alt.Color("series:N",
                scale=alt.Scale(
                    domain=["Actual 2025", "TimesFM 2.0", "Chronos-2"],
                    range=["#000000",     "#4C72B0",      "#DD8452"],
                ),
                legend=alt.Legend(title="Model"),
            ),
            tooltip=[
                alt.Tooltip("quarter_label:N", title="Quarter"),
                alt.Tooltip("series:N",        title="Model"),
                alt.Tooltip("price:Q",         title="Price (USD)", format="$.2f"),
            ],
        )
        .properties(height=360)
    )
    ci_tfm = (
        alt.Chart(fc)
        .mark_area(opacity=0.12, color="#4C72B0")
        .encode(x="quarter_label:O", y="timesfm_q10:Q", y2="timesfm_q90:Q")
    )
    ci_chr = (
        alt.Chart(fc)
        .mark_area(opacity=0.12, color="#DD8452")
        .encode(x="quarter_label:O", y="chronos2_q10:Q", y2="chronos2_q90:Q")
    )
    st.altair_chart(ci_tfm + ci_chr + fc_chart, use_container_width=True)

with st.expander("📊 Forecast data"):
    st.dataframe(forecast, use_container_width=True)

st.divider()

# ── Chart 3: Model comparison bar chart ───────────────────────────────────────
st.subheader("③ Model Comparison — MAE & RMSE (2024 Backtest)")
st.caption("Lower is better. Gemini achieves the best accuracy by incorporating news sentiment.")

cmp = comparison[["Model", "MAE ($)", "RMSE ($)"]].copy()
cmp_long = cmp.melt(id_vars="Model", var_name="Metric", value_name="Value")

color_scale3 = alt.Scale(
    domain=["TimesFM 2.0", "Chronos-2 Bolt", "Gemini 1.5 Flash"],
    range=["#4C72B0",     "#DD8452",         "#59A14F"],
)

bar_chart = (
    alt.Chart(cmp_long)
    .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
    .encode(
        x=alt.X("Model:N", title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Value:Q", title="Error (USD)"),
        color=alt.Color("Model:N", scale=color_scale3, legend=None),
        column=alt.Column("Metric:N", title=None),
        tooltip=[
            alt.Tooltip("Model:N"),
            alt.Tooltip("Metric:N"),
            alt.Tooltip("Value:Q", format="$.2f"),
        ],
    )
    .properties(width=220, height=300)
)

st.altair_chart(bar_chart)

st.divider()

# ── Key findings ───────────────────────────────────────────────────────────────
st.subheader("Key Findings")
st.markdown(
    """
- **Gemini 1.5 Flash** (price + sentiment, MAE \\$18.28) outperformed price-only models,
  confirming that news sentiment carries measurable predictive signal.
- **Chronos-2 Bolt** (MAE \\$28.57) generalized consistently across 2024 and 2025
  despite using price history only.
- **TimesFM 2.0** suffered scale distortion from Apple's long-term price growth
  (~\\$0.10 → ~\\$250), producing inflated forecasts — a key limitation on
  low-frequency, high-growth time series.
- All three models missed the Q4 2024 and Q2 2025 price drops, confirming that
  external market shocks remain difficult to capture zero-shot.
    """
)