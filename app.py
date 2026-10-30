"""
Maji Yetu: The Kenya Water Story 💧🇰🇪
A Curated Decision-Support & Storytelling Platform for Kenya's Water Reality.
"""

from __future__ import annotations
import streamlit as st

st.set_page_config(
    page_title="Maji Yetu 💧 The Kenya Water Story",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom header styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        color: #0077B6;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.15rem;
        color: #4A5568;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F0F4F8;
        border-radius: 10px;
        padding: 16px;
        border-left: 5px solid #0077B6;
    }
    .alert-box {
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 12px;
        font-weight: 500;
    }
    .alert-green { background-color: #E6F4EA; color: #137333; border-left: 4px solid #137333; }
    .alert-yellow { background-color: #FEF7E0; color: #B06000; border-left: 4px solid #B06000; }
    .alert-red { background-color: #FCE8E6; color: #C5221F; border-left: 4px solid #C5221F; }
    .alert-blue { background-color: #E8F0FE; color: #1A73E8; border-left: 4px solid #1A73E8; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Define application pages
pages = [
    st.Page("pages/1_The_Kenya_Water_Story.py", title="The Kenya Water Story", icon="📖", default=True),
    st.Page("pages/2_River_Forecast_Advisory.py", title="River Outlook & Forecast", icon="📈"),
    st.Page("pages/3_The_Borehole_Gamble.py", title="The Borehole Gamble", icon="🚰"),
    st.Page("pages/4_County_Water_Explorer.py", title="County Water Explorer", icon="🗺️"),
    st.Page("pages/5_Solutions_and_Actions.py", title="Solutions & Action Plan", icon="💡"),
]

# Run navigation
if hasattr(st, "navigation"):
    pg = st.navigation(pages)
    pg.run()
else:
    st.sidebar.title("Maji Yetu 💧")
    st.title("Maji Yetu: The Kenya Water Story 💧🇰🇪")
    st.markdown(
        """
        Welcome to **Maji Yetu**, a human-centered water intelligence platform designed for everyday Kenyans,
        farmers, community leaders, and water planners.
        
        Use the sidebar to explore the chapters:
        1. **The Kenya Water Story**: Why our country oscillates between floods and dry taps.
        2. **River Outlook & Forecast**: Plain-English river level forecasts and early warnings.
        3. **The Borehole Gamble**: Ground-truth data on drilling depth, yields, and the salinity trap.
        4. **County Water Explorer**: Where your county fetches water and where the risks lie.
        5. **Solutions & Action Plan**: Proven rainwater harvesting and groundwater conservation models.
        """
    )
