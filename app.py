"""
AquaML Kenya 💧 - Water Resources & Hydrological Decision Support System
Main application entry point configuring multi-page navigation.
"""

from __future__ import annotations
import streamlit as st

st.set_page_config(
    page_title="AquaML Kenya 💧",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Define application pages as st.Page objects
pages = [
    st.Page("pages/1_Overview_Map.py", title="Overview Map", icon="🗺️", default=True),
    st.Page("pages/2_River_Levels.py", title="River Levels & Discharge", icon="🌊"),
    st.Page("pages/3_Forecasting.py", title="River Discharge Forecasting", icon="📈"),
    st.Page("pages/4_Boreholes.py", title="Borehole Yield & Salinity", icon="🚰"),
    st.Page("pages/5_Data_Catalogue.py", title="Data Catalogue & Downloads", icon="📁"),
]

# Run navigation if supported (Streamlit >= 1.36 / 1.28 preview)
if hasattr(st, "navigation"):
    pg = st.navigation(pages)
    pg.run()
else:
    # For Streamlit versions that rely on multi-page directory routing
    st.title("AquaML Kenya 💧")
    st.subheader("Hydrological & Groundwater Intelligence Platform")
    st.markdown(
        """
        Welcome to **AquaML Kenya**, a decision support platform for Kenya's water resources:
        - **Overview Map**: Geospatial waterpoints, boreholes, rivers, and flood extents.
        - **River Levels**: Real-time river stage & rating-curve derived discharge.
        - **Forecasting**: Machine learning river flow prediction on Mukurumudzi 3KD06.
        - **Boreholes**: Groundwater yield analysis, WHO salinity classifications & ML yield predictor.
        - **Data Catalogue**: Interactive metadata browser with direct CSV downloads.

        *Use the sidebar navigation to select any analysis module.*
        """
    )
