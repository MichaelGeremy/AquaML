"""
Page 1: Overview Geospatial Map
Displays interactive Kenya hydrology assets: water points, boreholes,
river stations, rivers network, lakes, and flood hazard extents.
"""

from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.data_loader import (
    load_waterpoints,
    load_boreholes_acacia,
    load_boreholes_rural,
    load_stations,
    load_gis,
)

st.title("Kenya Water Resources & Infrastructure Map 🗺️")
st.markdown(
    "Explore Kenya's spatial water resources network: water access points, boreholes, "
    "river monitoring gauges, hydrological river networks, lakes, and flood-prone zones."
)

# Load base datasets
with st.spinner("Loading geospatial datasets..."):
    df_water = load_waterpoints()
    df_acacia = load_boreholes_acacia()
    df_rural = load_boreholes_rural()
    df_stations = load_stations()

# Combine boreholes
df_boreholes = pd.concat([df_acacia, df_rural], ignore_index=True)

# Sidebar Controls
st.sidebar.header("Map Layer Controls")

show_waterpoints = st.sidebar.checkbox("Water Points (mWater)", value=True)
show_boreholes = st.sidebar.checkbox("Boreholes", value=True)
show_stations = st.sidebar.checkbox("Monitoring Stations", value=True)
show_rivers = st.sidebar.checkbox("Rivers (Africover)", value=True)
show_lakes = st.sidebar.checkbox("Lakes (KEN Lakes)", value=True)
show_flood = st.sidebar.checkbox("Flood Extent", value=False)

# County filter
available_counties = sorted(
    list(
        set(
            df_water["county"].dropna().unique().tolist()
            + df_boreholes["county"].dropna().unique().tolist()
        )
    )
)
selected_counties = st.sidebar.multiselect(
    "Filter by County",
    options=available_counties,
    default=[],
    help="Leave empty to display all counties across Kenya.",
)

# Filter data
if selected_counties:
    filtered_water = df_water[df_water["county"].isin(selected_counties)]
    filtered_boreholes = df_boreholes[df_boreholes["county"].isin(selected_counties)]
else:
    filtered_water = df_water
    filtered_boreholes = df_boreholes

# Drop missing coordinates
filtered_water = filtered_water.dropna(subset=["latitude", "longitude"])
filtered_boreholes = filtered_boreholes.dropna(subset=["latitude", "longitude"])

# Max marker threshold for performance
max_markers = st.sidebar.slider(
    "Max Point Markers (performance)",
    min_value=500,
    max_value=25000,
    value=3000,
    step=500,
    help="Caps the number of rendered markers on the client map for smooth navigation.",
)

# Sidebar record counts
st.sidebar.markdown("---")
st.sidebar.subheader("Dataset Summary")
st.sidebar.metric("Water Points Selected", f"{len(filtered_water):,}")
st.sidebar.metric("Boreholes Selected", f"{len(filtered_boreholes):,}")
st.sidebar.metric("River Stations", f"{len(df_stations):,}")

# Try importing folium & streamlit_folium
try:
    import folium
    from folium.plugins import MarkerCluster
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    st.warning("`folium` or `streamlit-folium` is not installed. Rendering native Streamlit map fallback.")

if FOLIUM_AVAILABLE:
    # Initialize Kenya map centered at 0.0, 38.0, zoom 6
    kenya_map = folium.Map(
        location=[0.0, 38.0],
        zoom_start=6,
        tiles="CartoDB positron",
        control_scale=True,
    )

    # 1. Rivers Layer
    if show_rivers:
        try:
            rivers_gdf = load_gis("rivers")
            if rivers_gdf is not None and not rivers_gdf.empty:
                rivers_simp = rivers_gdf.copy()
                rivers_simp["geometry"] = rivers_simp["geometry"].simplify(0.005, preserve_topology=False)
                folium.GeoJson(
                    rivers_simp,
                    name="Rivers Network",
                    style_function=lambda x: {"color": "#1E88E5", "weight": 1.2, "opacity": 0.75},
                    tooltip=folium.GeoJsonTooltip(fields=["NAME"] if "NAME" in rivers_simp.columns else [], labels=True),
                ).add_to(kenya_map)
        except Exception as e:
            st.info(f"Could not render Rivers layer: {e}")

    # 2. Lakes Layer
    if show_lakes:
        try:
            lakes_gdf = load_gis("lakes")
            if lakes_gdf is not None and not lakes_gdf.empty:
                folium.GeoJson(
                    lakes_gdf,
                    name="Lakes",
                    style_function=lambda x: {
                        "fillColor": "#00897B",
                        "color": "#004D40",
                        "weight": 1.0,
                        "fillOpacity": 0.5,
                    },
                    tooltip=folium.GeoJsonTooltip(fields=["NAME"] if "NAME" in lakes_gdf.columns else [], labels=True),
                ).add_to(kenya_map)
        except Exception as e:
            st.info(f"Could not render Lakes layer: {e}")

    # 3. Flood Extent Layer
    if show_flood:
        try:
            flood_gdf = load_gis("flood")
            if flood_gdf is not None and not flood_gdf.empty:
                flood_simp = flood_gdf.copy()
                flood_simp["geometry"] = flood_simp["geometry"].simplify(0.01, preserve_topology=False)
                folium.GeoJson(
                    flood_simp,
                    name="Flood Hazard Extent",
                    style_function=lambda x: {
                        "fillColor": "#FB8C00",
                        "color": "#E65100",
                        "weight": 1.0,
                        "fillOpacity": 0.35,
                    },
                ).add_to(kenya_map)
        except Exception as e:
            st.info(f"Could not render Flood Extent layer: {e}")

    # 4. Water Points MarkerCluster
    if show_waterpoints and not filtered_water.empty:
        water_sample = filtered_water.sample(min(len(filtered_water), max_markers), random_state=42)
        water_cluster = MarkerCluster(name="Water Points (mWater)").add_to(kenya_map)
        for _, row in water_sample.iterrows():
            name = str(row.get("name", "Unnamed Water Point"))
            wpt_type = str(row.get("waterpoint_type", "Unknown"))
            county = str(row.get("county", "Unknown"))
            popup_html = f"<div style='font-family:sans-serif;'><b>{name}</b><br>Type: {wpt_type}<br>County: {county}</div>"
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=3,
                color="#0288D1",
                fill=True,
                fill_color="#03A9F4",
                fill_opacity=0.8,
                popup=folium.Popup(popup_html, max_width=250),
            ).add_to(water_cluster)

    # 5. Boreholes MarkerCluster
    if show_boreholes and not filtered_boreholes.empty:
        borehole_sample = filtered_boreholes.sample(min(len(filtered_boreholes), max_markers), random_state=42)
        borehole_cluster = MarkerCluster(name="Boreholes").add_to(kenya_map)
        for _, row in borehole_sample.iterrows():
            name = str(row.get("name", "Unnamed Borehole"))
            yield_val = f"{row['yield']:.2f} m³/h" if pd.notna(row.get("yield")) else "N/A"
            ec_val = f"{row['ec_us_cm']:.0f} µS/cm" if pd.notna(row.get("ec_us_cm")) else "N/A"
            county = str(row.get("county", "Unknown"))
            popup_html = f"<div style='font-family:sans-serif;'><b>{name}</b><br>Yield: {yield_val}<br>EC: {ec_val}<br>County: {county}</div>"
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=4,
                color="#E65100",
                fill=True,
                fill_color="#FF9800",
                fill_opacity=0.85,
                popup=folium.Popup(popup_html, max_width=250),
            ).add_to(borehole_cluster)

    # 6. River Monitoring Stations (Red Star Markers)
    if show_stations and not df_stations.empty:
        stations_group = folium.FeatureGroup(name="River Monitoring Stations").add_to(kenya_map)
        for _, row in df_stations.iterrows():
            st_id = str(row.get("station_id", "Unknown"))
            river = str(row.get("river", "Unknown"))
            site = str(row.get("site_name", "Unknown"))
            lat = row.get("approx_lat")
            lon = row.get("approx_lon")
            if pd.notna(lat) and pd.notna(lon):
                popup_html = f"<div style='font-family:sans-serif;'><b>Station: {st_id}</b><br>River: {river}<br>Site: {site}</div>"
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{st_id} ({river})",
                    icon=folium.Icon(color="red", icon="star", prefix="fa"),
                ).add_to(stations_group)

    folium.LayerControl(collapsed=False).add_to(kenya_map)

    # Render folium map
    st_folium(kenya_map, width="100%", height=680, returned_objects=[])

else:
    # Native Streamlit map fallback
    st.info("Displaying point locations using native map view:")
    points = []
    if show_waterpoints and not filtered_water.empty:
        wp_sub = filtered_water[["latitude", "longitude"]].dropna().rename(columns={"latitude": "lat", "longitude": "lon"})
        points.append(wp_sub)
    if show_boreholes and not filtered_boreholes.empty:
        bh_sub = filtered_boreholes[["latitude", "longitude"]].dropna().rename(columns={"latitude": "lat", "longitude": "lon"})
        points.append(bh_sub)
    if points:
        all_pts = pd.concat(points, ignore_index=True)
        st.map(all_pts.sample(min(len(all_pts), 5000), random_state=42))
