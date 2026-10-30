"""
Chapter 5: Solutions & Action Plan
Practical, community-scale water resilience models for Kenya.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
from pathlib import Path
from utils.data_loader import load_waterpoints, load_boreholes_acacia, load_rating_curves, load_timeseries

st.title("💡 Chapter 5: Solutions & Action Plan")
st.subheader("Proven, Community-Scale Water Resilience Models for Kenya")

st.markdown(
    """
    Understanding Kenya's water paradox is only the first step.
    The real question is: **What can we actually do about it?**
    
    Here are four proven, field-tested interventions that directly address our flash floods,
    rapid river dry-downs, and underground salinity trap.
    """
)

# Tabbed Solutions
tab_rain, tab_sand, tab_desal, tab_spring, tab_data = st.tabs([
    "🌧️ Rainwater Harvesting Calculator",
    "🧱 Sand Dams for Dry Rivers",
    "☀️ Solar Desalination (Fixing Salt)",
    "🛡️ Spring-Box Protection",
    "📁 Data Download & Open Science",
])

with tab_rain:
    st.markdown("### 🌧️ Household & School Rainwater Harvesting Calculator")
    st.write("Every corrugated iron roof in Kenya is a potential private reservoir. Calculate how much water your roof can harvest annually:")
    
    rc1, rc2 = st.columns(2)
    with rc1:
        roof_area = st.number_input("Roof Surface Area (m²):", min_value=10, max_value=2000, value=80, step=10,
                                   help="A standard 2-bedroom iron-roof house is ~60–80 m²; a school block is ~200–400 m².")
        rainfall_zone = st.selectbox(
            "Rainfall Zone / Region:",
            options=[
                "High Rainfall (Western, Central Highlands: ~1,400 mm/year)",
                "Moderate Rainfall (Coast, Rift Valley: ~950 mm/year)",
                "Semi-Arid (Ukambani, Laikipia: ~650 mm/year)",
                "Arid ASALs (Turkana, Wajir, Garissa: ~350 mm/year)",
            ],
            index=1,
        )
        
        # Extract rainfall mm
        if "1,400" in rainfall_zone:
            rainfall_mm = 1400
        elif "950" in rainfall_zone:
            rainfall_mm = 950
        elif "650" in rainfall_zone:
            rainfall_mm = 650
        else:
            rainfall_mm = 350

    # Formula: Harvested Liters = Roof Area (m2) * Rainfall (mm) * Runoff Coefficient (0.85 for iron sheets)
    harvested_liters = roof_area * rainfall_mm * 0.85
    daily_liters = harvested_liters / 365
    jerrycans_year = harvested_liters / 20

    with rc2:
        st.markdown("#### Harvest Potential")
        st.metric("Total Annual Rainwater Harvested", f"{harvested_liters:,.0f} Liters", f"{jerrycans_year:,.0f} standard 20L jerrycans")
        st.metric("Daily Safe Drinking Water", f"{daily_liters:.1f} Liters/Day", "Adequate for drinking, cooking & hygiene")
        
        tank_size = min(20000, max(2500, int(harvested_liters * 0.25)))
        st.info(f"💡 **Recommended Tank Size**: A **{tank_size:,}-liter plastic or masonry tank** captures peak wet-season flushes and bridges dry-season gaps.")

with tab_sand:
    st.markdown("### 🧱 Sand Dams: Storing Floods Beneath the Sand")
    st.markdown(
        """
        **How It Works**:
        In semi-arid counties like **Kitui, Machakos, Makueni, and Samburu**, seasonal rivers (*laggas*) flow with brown floodwater
        for just a few days each year before drying into sand.
        
        A **sand dam** is a low, reinforced concrete wall built across the seasonal riverbed:
        1. During floods, heavy sand settles behind the wall, while muddy water flows over.
        2. Within 1–3 rainy seasons, the dam fills with clean river sand.
        3. Sand pores hold between **25% and 40% of their volume as water**.
        
        **Why It Beats Open Water Dams**:
        - **Zero Evaporation**: The water is stored 1–2 meters underground inside the sand, immune to equatorial sun.
        - **Zero Mosquito Breeding**: No standing surface water.
        - **Natural Filtration**: Pumping from shallow well-points in the sand yields clear, potable water.
        - **Lifespan**: Over 50 years with virtually zero maintenance.
        """
    )

with tab_desal:
    st.markdown("### ☀️ Overcoming the Salinity Trap: Solar Reverse Osmosis")
    st.markdown(
        """
        In Chapter 3, we showed that **over 36% of boreholes in northern Kenya hit salty water** (EC > 1,500 µS/cm).
        Traditionally, these multimillion-shilling investments were abandoned.
        
        **The Modern Solution: Solar Desalination Kiosks**:
        - Small-scale, containerized **Solar Reverse Osmosis (RO)** plants produce 1,000 to 5,000 liters of sweet drinking water per hour.
        - The high electrical conductivity is reduced from 4,000 µS/cm down to fresh WHO standards (<400 µS/cm).
        - Powered 100% by Kenya's abundant solar radiation, requiring no diesel fuel.
        - **Community Water ATMs**: Villagers tap a prepaid NFC smart card to draw fresh drinking water for **KES 3 per 20-liter jerrycan**, generating revenue to service membranes and filters.
        """
    )

with tab_spring:
    st.markdown("### 🛡️ Spring-Box Protection: The Highest Return on Health")
    st.markdown(
        """
        As shown in Chapter 1 and 4, Western Kenya has over **2,200 completely unprotected open springs**.
        Families scoop water directly from muddy seepage pools contaminated by surface runoff and livestock.
        
        **The Fix: A Capped Spring-Box**:
        - Enclosing the natural eye of the spring in a concrete box with graded gravel filters.
        - Diverts runoff ditches around the spring and adds a collection apron with stainless steel spouts.
        - **Cost**: Approximately **KES 75,000 to 120,000** ($600–$900).
        - **Impact**: Eliminates 95%+ of surface microbial contamination for 200–500 households immediately.
        """
    )

with tab_data:
    st.markdown("### 📁 Open Hydrological Data for Kenya")
    st.write("All datasets powering Maji Yetu are curated from public and research archives for open scientific use:")
    
    d1, d2 = st.columns(2)
    with d1:
        wp_raw = load_waterpoints()
        if not wp_raw.empty:
            csv_wp = wp_raw.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Kenya Waterpoints Clean (21k records, CSV)",
                data=csv_wp,
                file_name="kenya_waterpoints_mwater_clean.csv",
                mime="text/csv",
            )
            
        rc_raw = load_rating_curves()
        if not rc_raw.empty:
            csv_rc = rc_raw.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Coastal River Rating Curves (CSV)",
                data=csv_rc,
                file_name="rating_curves_all.csv",
                mime="text/csv",
            )

    with d2:
        acacia_raw = load_boreholes_acacia()
        if not acacia_raw.empty:
            csv_acacia = acacia_raw.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download ASAL Boreholes & Salinity (Acacia, CSV)",
                data=csv_acacia,
                file_name="kenya_boreholes_acacia_rapid.csv",
                mime="text/csv",
            )
            
        ts_raw = load_timeseries("3KD06")
        if not ts_raw.empty:
            csv_ts = ts_raw.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Mukurumudzi 3KD06 Logger Series (CSV)",
                data=csv_ts,
                file_name="mukurumudzi_3KD06_water_level.csv",
                mime="text/csv",
            )
