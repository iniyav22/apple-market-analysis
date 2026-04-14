import streamlit as st

st.title("Apple Quarterly Analysis Dashboard")

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">Explore Apple’s quarterly financial and news trends</div>
        <div class="hero-subtext">
            This dashboard analyzes how Apple’s stock return, volatility, trading activity,
            and news sentiment interact over time.
        </div>
        <div>
            <span class="pill">Returns</span>
            <span class="pill">Sentiment</span>
            <span class="pill">Volatility</span>
            <span class="pill">AI Visuals</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        """
        <div class="mini-card">
            <div class="mini-label">Focus</div>
            <div class="mini-value">Apple quarterly performance</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class="mini-card">
            <div class="mini-label">Data Scope</div>
            <div class="mini-value">News, market, and financial data</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        """
        <div class="mini-card">
            <div class="mini-label">Use Case</div>
            <div class="mini-value">Interactive question-based analysis</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("### Overview")

st.markdown(
    """
    <div class="section-card">
        <div class="section-title">What this project shows</div>
        <div class="section-text">
            Apple’s quarterly performance is not explained by one metric alone. Across the dashboard,
            returns, volatility, news sentiment, and news volume can be compared to reveal broader patterns
            in how attention and market behavior move together.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["Question Pages", "AI Tool"])

with tab1:
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">View the six analysis questions</div>
            <div class="section-text">
                Use the question pages to explore focused comparisons such as sentiment vs return,
                extreme sentiment vs trading volume, and news volume vs performance.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with tab2:
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Create your own chart</div>
            <div class="section-text">
                Use the Visual AI Agent to ask a custom question and generate a new visualization
                from the same Apple quarterly dataset.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
