"""
Chapter 4: County Water Profile & Scorecard
Select any Kenyan county to see where citizens fetch water and local water risks.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

from utils.data_loader import load_waterpoints, load_gis

st.title("🗺️ Chapter 4: County Water Explorer & Scorecard")
st.subheader("Where Do People in Your County Fetch Water, and What Are the Local Risks?")

st.markdown(
    """
    Water security in Kenya is intensely local. While a resident in Kakamega may have an open spring 200 meters away,
    a pastoralist in Turkana may walk 12 kilometers to reach a solar borehole.
    
    Select your county below to generate an instant **Water Access & Vulnerability Scorecard**.
    """
)

# Load waterpoints
with st.spinner("Loading national waterpoint inventory..."):
    wp_df = load_waterpoints()

if wp_df.empty:
    st.error("Waterpoints dataset could not be loaded.")
    st.stop()

# Get list of counties with record counts
county_counts = wp_df["county"].dropna().value_counts()
county_list = list(county_counts.index)

# County selection
col_sel, col_stats = st.columns([1, 2])
with col_sel:
    selected_county = st.selectbox(
        "🇰🇪 Select County:",
        options=county_list,
        index=0 if "Kakamega" not in county_list else county_list.index("Kakamega"),
    )

county_data = wp_df[wp_df["county"] == selected_county].copy()
total_c_wp = len(county_data)

# Compute county metrics
unprotected_types = ["Unprotected spring", "Unprotected dug well"]
n_unprotected = county_data["waterpoint_type"].isin(unprotected_types).sum()
pct_unprotected = (n_unprotected / total_c_wp) * 100 if total_c_wp > 0 else 0
pct_protected = 100.0 - pct_unprotected

with col_stats:
    m1, m2, m3 = st.columns(3)
    m1.metric("Mapped Water Sources", f"{total_c_wp:,}", f"Rank: #{county_list.index(selected_county)+1} of {len(county_list)}")
    m2.metric("Protected Sources", f"{pct_protected:.1f}%", "Safeguarded from surface runoff")
    m3.metric("Unprotected Sources", f"{pct_unprotected:.1f}%", f"{n_unprotected:,} open springs/wells", delta_color="inverse")

st.markdown("---")

# County Breakdown: Technology distribution
col_chart, col_verdict = st.columns([1, 1])

with col_chart:
    st.markdown(f"#### Water Sources in **{selected_county}** by Type")
    type_breakdown = county_data["waterpoint_type"].value_counts().reset_index()
    type_breakdown.columns = ["Technology", "Count"]
    
    fig_types = px.pie(
        type_breakdown,
        values="Count",
        names="Technology",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    fig_types.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
    )
    st.plotly_chart(fig_types, use_container_width=True)

with col_verdict:
    st.markdown(f"#### 📋 Water Security Verdict for **{selected_county}**")
    
    if pct_unprotected > 25:
        st.warning(
            f"""
            **High Contamination Vulnerability**:  
            Over **{pct_unprotected:.1f}%** of waterpoints in {selected_county} are open, unprotected springs or hand-dug wells.
            
            - **Primary Risk**: Surface runoff carries human and livestock pathogens directly into the water pool during rains.
            - **Recommended Local Action**: Low-cost **Spring-Box Protection** projects (KES 60,000–120,000 per spring) provide the highest health return on investment.
            """
        )
    elif "Borehole or tubewell" in type_breakdown["Technology"].head(2).values:
        st.info(
            f"""
            **Groundwater Dependent County**:  
            {selected_county} relies heavily on deep boreholes and tubewells.
            
            - **Primary Risk**: Power costs for diesel generators, pump breakdowns, and subsurface salinity.
            - **Recommended Local Action**: Transition to **Solar-Powered Pumping** with prepaid community water ATM kiosks to ensure funds for spare parts.
            """
        )
    else:
        st.success(
            f"""
            **Relatively High Protection Rate**:  
            Over **{pct_protected:.1f}%** of surveyed waterpoints in {selected_county} have physical structures shielding them from contamination.
            
            - **Primary Challenge**: Maintenance and year-round yield reliability during prolonged dry seasons.
            - **Recommended Local Action**: Routine water quality testing and catchment reforestation around recharge zones.
            """
        )

# Interactive County Map with clustered points
st.markdown("---")
st.markdown(f"### 📍 Interactive Waterpoint Map — {selected_county} County")
st.write("Click on any marker to view the waterpoint name, technology, and location details:")

# Valid coordinates
county_valid_geo = county_data.dropna(subset=["latitude", "longitude"]).copy()
county_valid_geo = county_valid_geo[
    (county_valid_geo["latitude"].between(-5.0, 5.5)) & 
    (county_valid_geo["longitude"].between(33.5, 42.5))
]

if not county_valid_geo.empty:
    center_lat = county_valid_geo["latitude"].median()
    center_lon = county_valid_geo["longitude"].median()
    
    county_map = folium.Map(location=[center_lat, center_lon], zoom_start=10, tiles="CartoDB positron")
    
    # Fast marker cluster for performance
    cluster = MarkerCluster(name="Waterpoints").add_to(county_map)
    
    # Cap markers at 1,500 for fast UI responsiveness
    sample_geo = county_valid_geo.head(1500)
    for _, row in sample_geo.iterrows():
        wp_type = str(row.get("waterpoint_type", "Unknown"))
        is_unprot = "Unprotected" in wp_type
        icon_color = "red" if is_unprot else "blue"
        
        name = str(row.get("name", "Community Waterpoint"))
        ward = str(row.get("ward_or_location", ""))
        
        popup_html = f"<b>{name}</b><br>Type: {wp_type}<br>Ward: {ward}<br>County: {selected_county}"
        
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=5,
            color="#D32F2F" if is_unprot else "#0077B6",
            fill=True,
            fill_color="#D32F2F" if is_unprot else "#0077B6",
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=250),
        ).add_to(cluster)
        
    st_folium(county_map, width="100%", height=450)
else:
    st.info(f"Geographic coordinates are not available for points in {selected_county}.")
