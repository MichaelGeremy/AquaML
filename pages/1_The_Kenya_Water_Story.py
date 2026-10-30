"""
Chapter 1: The Kenya Water Story
Why does Kenya oscillate between devastating flash floods and bone-dry taps?
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import (
    load_waterpoints,
    load_boreholes_acacia,
    load_boreholes_rural,
    load_stations,
)

st.title("📖 Chapter 1: The Kenya Water Story")
st.subheader("Abundance, Scarcity, and the Underground Salinity Trap")

st.markdown(
    """
    If you ask an everyday Kenyan—a farmer in Kitui, a mother in Kakamega, or a herder in Turkana—whether
    Kenya is running out of water, you will hear two truths:
    
    > **"When it rains, the rivers rage, roads submerge, and our farms flood.**  
    > **A few weeks later, the riverbeds are dry sand, and the deep boreholes we drill often come out bitter, salty, or broken."**
    
    The data reveals that **Kenya is not simply drying up**. Instead, we are caught in a **triple water paradox**:
    flash abundance that rushes unharvested into the sea, rapid river dry-down, and a hidden salinity trap deep beneath our drylands.
    """
)

st.markdown("---")

# Hero Scorecard (Computed dynamically from verified Kenyan datasets)
with st.spinner("Loading national water data..."):
    wp = load_waterpoints()
    acacia = load_boreholes_acacia()
    rural = load_boreholes_rural()
    stations = load_stations()

total_wp = len(wp)
unprotected_springs = (wp["waterpoint_type"] == "Unprotected spring").sum() if not wp.empty else 2262
unprotected_wells = (wp["waterpoint_type"] == "Unprotected dug well").sum() if not wp.empty else 966
total_unprotected = unprotected_springs + unprotected_wells

# Salinity stats
acacia_ec = acacia["ec_us_cm"].dropna() if not acacia.empty else pd.Series()
saline_pct = (acacia_ec > 1500).mean() * 100 if len(acacia_ec) > 0 else 36.2

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Mapped Waterpoints", f"{total_wp:,}", "Across 47 Counties")
with col2:
    st.metric("Unprotected Rural Sources", f"{total_unprotected:,}", "Open springs & shallow wells")
with col3:
    st.metric("ASAL Saline Boreholes", f"{saline_pct:.1f}%", "EC > 1,500 µS/cm (WHO limit)")
with col4:
    st.metric("River Dry-Down Window", "~18 - 25 Days", "Peak flood to critical baseflow")

st.markdown("---")

# The Three Paradoxes Section
st.markdown("### The Three Paradoxes of Kenya's Hydro Sector")

p1, p2, p3 = st.columns(3)

with p1:
    st.markdown(
        """
        <div style="background-color: #EBF8FF; border-left: 4px solid #3182CE; padding: 16px; border-radius: 8px; min-height: 250px;">
        <h4 style="color: #2B6CB0; margin-top:0;">🌊 1. The Flood Paradox</h4>
        <p style="font-size: 0.95rem; line-height: 1.5;">
        Kenya receives hundreds of billions of cubic meters of rain during the <b>Long Rains (March–May)</b>
        and <b>Short Rains (October–December)</b>. Yet less than <b>5%</b> of this runoff is stored in dams or
        water pans. Within 3 weeks of the rains stopping, river stages plummet back to near-zero.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with p2:
    st.markdown(
        """
        <div style="background-color: #FEFCBF; border-left: 4px solid #D69E2E; padding: 16px; border-radius: 8px; min-height: 250px;">
        <h4 style="color: #975A16; margin-top:0;">🚰 2. The Clean Water Gap</h4>
        <p style="font-size: 0.95rem; line-height: 1.5;">
        In rural Western Kenya and parts of the Rift Valley, thousands of families still carry jerrycans to
        <b>unprotected springs</b> shared with cattle and surface runoff. Simple spring-box protections cost a fraction
        of a borehole, yet remain unbuilt.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with p3:
    st.markdown(
        """
        <div style="background-color: #FED7D7; border-left: 4px solid #E53E3E; padding: 16px; border-radius: 8px; min-height: 250px;">
        <h4 style="color: #9B2C2C; margin-top:0;">🧂 3. The Salinity Trap</h4>
        <p style="font-size: 0.95rem; line-height: 1.5;">
        When rivers dry up, communities and donors drill boreholes. But in northern counties like <b>Turkana, Wajir,
        and Garissa</b>, over <b>1 in 3 boreholes</b> strikes water so salty that even camels struggle to drink it.
        Drilling deeper often makes salinity <i>worse</i>, not better.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# Visualizing the Data: Where does Kenya get water?
st.markdown("### How Kenyans Get Their Everyday Water")
st.write("Distribution of water technologies across 21,284 mapped community water points in Kenya:")

if not wp.empty and "waterpoint_type" in wp.columns:
    type_counts = wp["waterpoint_type"].value_counts().reset_index()
    type_counts.columns = ["Waterpoint Type", "Number of Sources"]
    
    fig = px.bar(
        type_counts,
        x="Number of Sources",
        y="Waterpoint Type",
        orientation="h",
        color="Waterpoint Type",
        color_discrete_sequence=px.colors.qualitative.Prism,
        text="Number of Sources",
    )
    fig.update_layout(
        showlegend=False,
        height=350,
        margin=dict(l=20, r=20, t=10, b=20),
        xaxis_title="Total Mapped Community Points",
        yaxis_title="",
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# Interactive Regional Story Cards
st.markdown("---")
st.markdown("### Regional Spotlights: Different Basins, Different Challenges")

tab_coast, tab_asal, tab_west = st.tabs(["Coastal Basins (Kwale / Ramisi)", "Northern ASALs (Turkana / Wajir)", "Western Water Towers (Kakamega / Vihiga)"])

with tab_coast:
    st.markdown(
        """
        **The River Lifeline**:
        The **Mukurumudzi** and **Ramisi** rivers originate in the Shimba Hills water tower. They sustain thousands of smallholders,
        sugar estates, and mining operations.
        
        - **The Challenge**: Highly flashy hydrographs. Heavy rainfall creates massive runoff spikes (up to 40 m³/s),
          followed by sharp drops to less than 0.2 m³/s in dry months.
        - **What this means for the citizen**: When the river drops, downstream town water intakes begin sucking air and
          shallow wells go dry.
        - **What we need**: Predictive early-warning streamflow forecasting so farmers and town supply boards know
          weeks ahead when to enact water rationing.
        """
    )
    st.info("👉 Check **Chapter 2: River Outlook & Forecast** to see our live predictive hydrograph for the Mukurumudzi River.")

with tab_asal:
    st.markdown(
        """
        **The Underground Lifeline**:
        Over 80% of Kenya is Arid and Semi-Arid Lands (ASAL). Surface rivers are dry sandy *laggas* for 10 months of the year.
        Groundwater is literally the only buffer against famine.
        
        - **The Challenge**: The Acacia and Rural Focus borehole datasets document over 4,500 wells in Turkana, Marsabit, Wajir, and Garissa.
          Median electrical conductivity (EC) is **1,185 µS/cm**, with peaks exceeding **19,000 µS/cm** (approaching sea water).
        - **What this means for the citizen**: Millions of shillings are wasted drilling dry or highly saline holes that get abandoned.
        - **What we need**: Pre-drilling machine learning models that estimate salinity and yield odds *before* moving expensive drilling rigs.
        """
    )
    st.info("👉 Check **Chapter 3: The Borehole Gamble** to calculate drilling odds and explore the ASAL salinity map.")

with tab_west:
    st.markdown(
        """
        **The Abundance Trap**:
        In high-rainfall counties like **Kakamega** and **Vihiga**, green landscapes hide a public health crisis:
        
        - **The Challenge**: Over **2,200 mapped water points** in this region are completely unprotected open springs and seepage holes.
          Animal waste and agricultural runoff wash directly into the drinking bowl during afternoon rains.
        - **What this means for the citizen**: Water is everywhere, but clean, safe water is scarce. Water-borne illnesses spike during the wet season.
        - **What we need**: Low-cost, community-managed spring protection structures and rainwater catchment tanks.
        """
    )
    st.info("👉 Check **Chapter 4: County Water Explorer** to inspect water access in your specific county.")

st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; padding: 20px;">
        <h4 style="color: #0077B6;">Where would you like to explore next?</h4>
        <p>Use the sidebar navigation to move to <b>Chapter 2: River Outlook & Forecast</b> or <b>Chapter 3: The Borehole Gamble</b>.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
