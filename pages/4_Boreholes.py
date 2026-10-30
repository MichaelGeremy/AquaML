"""
Page 4: Borehole Hydrogeology & Groundwater Yield Analysis
Explores groundwater potential, borehole yield determinants, WHO-standard salinity maps,
county yield comparisons, and an interactive machine learning yield predictor.
"""

from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.data_loader import load_boreholes_acacia, load_boreholes_rural

st.title("Groundwater Boreholes & Salinity Intelligence 🚰")
st.markdown(
    "Synthesizes hydrogeological data across 4,500+ boreholes from the **Acacia Water (Kenya Rapid+)** "
    "and **Rural Focus** surveys. Inspect yield distributions, water salinity, and predict aquifer yields."
)

# Load and merge boreholes
with st.spinner("Loading borehole datasets..."):
    df_acacia = load_boreholes_acacia()
    df_rural = load_boreholes_rural()

    # Tag sources
    df_acacia_sub = df_acacia.copy()
    df_acacia_sub["dataset_source"] = "Acacia Water / Rapid+"

    df_rural_sub = df_rural.copy()
    df_rural_sub["dataset_source"] = "Rural Focus"

    # Merge
    merged_bh = pd.concat([df_acacia_sub, df_rural_sub], ignore_index=True)

# Sidebar Filters
st.sidebar.header("Borehole Filters")

# County filter
all_counties = sorted(merged_bh["county"].dropna().unique().tolist())
selected_counties = st.sidebar.multiselect(
    "Filter Counties",
    options=all_counties,
    default=[],
    help="Leave blank to include all counties across Kenya.",
)

# Operation status filter
all_statuses = sorted(merged_bh["operation_status"].dropna().unique().tolist())
selected_status = st.sidebar.multiselect(
    "Operational Status",
    options=all_statuses,
    default=[],
    help="Filter by functionality (e.g., Operational, Abandoned, Not Operational).",
)

# Feature axis selectors
st.sidebar.markdown("---")
st.sidebar.subheader("Scatter Plot Axes")
x_axis_options = ["well_depth", "ec_us_cm", "ph", "elevation"]
y_axis_options = ["yield", "ec_us_cm", "ph"]

selected_x = st.sidebar.selectbox("X-Axis Feature", options=x_axis_options, index=0)
selected_y = st.sidebar.selectbox("Y-Axis Feature", options=y_axis_options, index=0)

# Filter dataset
filtered = merged_bh.copy()
if selected_counties:
    filtered = filtered[filtered["county"].isin(selected_counties)]
if selected_status:
    filtered = filtered[filtered["operation_status"].isin(selected_status)]

# Summary metrics
st.sidebar.markdown("---")
st.sidebar.subheader("Summary")
st.sidebar.metric("Boreholes Filtered", f"{len(filtered):,}")
mean_y = filtered["yield"].mean()
st.sidebar.metric("Average Yield", f"{mean_y:.2f} m³/h" if pd.notna(mean_y) else "N/A")

# Try importing plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Try importing folium
try:
    import folium
    from folium.plugins import MarkerCluster
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

# Machine Learning Yield Predictor Model
@st.cache_resource
def train_yield_predictor():
    """Train Random Forest Regressor on Acacia borehole data."""
    from sklearn.ensemble import RandomForestRegressor
    raw_acacia = load_boreholes_acacia()
    clean = raw_acacia.dropna(subset=["yield", "well_depth", "latitude", "longitude"]).copy()
    clean = clean[(clean["yield"] > 0) & (clean["yield"] < 100)]
    feature_cols = ["well_depth", "latitude", "longitude"]
    X = clean[feature_cols].values
    y = clean["yield"].values
    rf = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1)
    rf.fit(X, y)
    return rf, feature_cols, len(clean)

rf_model, rf_features, n_train_samples = train_yield_predictor()

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Yield vs Features", "🗺️ Salinity Map", "🔮 ML Yield Predictor"])

# ==================== TAB 1: YIELD VS FEATURES ====================
with tab1:
    st.subheader(f"Scatter Analysis: {selected_y} vs {selected_x}")
    valid_scatter = filtered.dropna(subset=[selected_x, selected_y]).copy()

    # Remove extreme outliers for clear visualization
    if selected_x in ["well_depth", "elevation", "ec_us_cm"]:
        q99_x = valid_scatter[selected_x].quantile(0.99)
        valid_scatter = valid_scatter[valid_scatter[selected_x] <= q99_x]
    if selected_y in ["yield", "ec_us_cm"]:
        q99_y = valid_scatter[selected_y].quantile(0.99)
        valid_scatter = valid_scatter[valid_scatter[selected_y] <= q99_y]

    if valid_scatter.empty:
        st.warning("No records with valid values for both selected features.")
    elif PLOTLY_AVAILABLE:
        fig_scatter = px.scatter(
            valid_scatter,
            x=selected_x,
            y=selected_y,
            color="county" if "county" in valid_scatter.columns else None,
            hover_data=["name", "yield", "well_depth", "county", "dataset_source"],
            labels={
                "well_depth": "Well Depth (m)",
                "yield": "Yield (m³/h)",
                "ec_us_cm": "Electrical Conductivity (µS/cm)",
                "ph": "pH",
                "elevation": "Elevation (m a.s.l.)",
            },
            title=f"{selected_y.replace('_', ' ').title()} vs {selected_x.replace('_', ' ').title()} by County",
            template="plotly_white",
            height=480,
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.scatter_chart(valid_scatter[[selected_x, selected_y]])

    # County Comparison Bar Chart
    st.markdown("### Median Borehole Yield by County")
    county_yield = (
        filtered.dropna(subset=["yield", "county"])
        .groupby("county")["yield"]
        .agg(["median", "count"])
        .query("count >= 3")
        .sort_values("median", ascending=False)
        .reset_index()
    )

    if not county_yield.empty and PLOTLY_AVAILABLE:
        fig_county = px.bar(
            county_yield,
            x="county",
            y="median",
            text="median",
            labels={"median": "Median Yield (m³/h)", "county": "County"},
            color="median",
            color_continuous_scale="Blues",
            title="Median Groundwater Yield per County (min. 3 observations)",
            template="plotly_white",
            height=380,
        )
        fig_county.update_traces(texttemplate="%{text:.2f} m³/h", textposition="outside")
        fig_county.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_county, use_container_width=True)
    elif not county_yield.empty:
        st.bar_chart(county_yield.set_index("county")["median"])

# ==================== TAB 2: SALINITY MAP ====================
with tab2:
    st.subheader("Groundwater Salinity Classification (Electrical Conductivity - EC)")
    st.markdown(
        """
        Groundwater quality is classified based on WHO / Kenyan drinking water thresholds:
        - 🟢 **Fresh Water**: $< 1,500$ µS/cm (Potable for domestic & livestock)
        - 🟠 **Brackish Water**: $1,500 - 3,000$ µS/cm (Marginal, requires blending or treatment)
        - 🔴 **Saline Water**: $> 3,000$ µS/cm (High mineral content / non-potable)
        """
    )

    ec_df = filtered.dropna(subset=["latitude", "longitude", "ec_us_cm"]).copy()

    # Assign category and color
    def categorize_ec(val: float):
        if val < 1500:
            return "Fresh (<1500 µS/cm)", "#2ca02c"
        elif val <= 3000:
            return "Brackish (1500-3000 µS/cm)", "#ff7f0e"
        else:
            return "Saline (>3000 µS/cm)", "#d62728"

    ec_df["category"], ec_df["color"] = zip(*ec_df["ec_us_cm"].map(categorize_ec))

    # Show count stats
    cat_counts = ec_df["category"].value_counts()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Fresh Boreholes", f"{cat_counts.get('Fresh (<1500 µS/cm)', 0):,}")
    with c2:
        st.metric("Brackish Boreholes", f"{cat_counts.get('Brackish (1500-3000 µS/cm)', 0):,}")
    with c3:
        st.metric("Saline Boreholes", f"{cat_counts.get('Saline (>3000 µS/cm)', 0):,}")

    if FOLIUM_AVAILABLE:
        salinity_map = folium.Map(
            location=[0.5, 38.0],
            zoom_start=6,
            tiles="CartoDB positron",
        )

        cluster = MarkerCluster(name="Boreholes by Salinity").add_to(salinity_map)
        # Sample for rendering performance if needed
        render_sample = ec_df.sample(min(len(ec_df), 2500), random_state=42)

        for _, row in render_sample.iterrows():
            name = str(row.get("name", "Borehole"))
            ec_v = row["ec_us_cm"]
            cat = row["category"]
            col = row["color"]
            y_v = f"{row['yield']:.2f} m³/h" if pd.notna(row.get("yield")) else "N/A"
            county_v = str(row.get("county", "N/A"))

            popup_html = f"""
            <div style="font-family:sans-serif; min-width:160px;">
                <b>{name}</b><br>
                <b>Class:</b> <span style="color:{col};font-weight:bold;">{cat}</span><br>
                <b>EC:</b> {ec_v:.1f} µS/cm<br>
                <b>Yield:</b> {y_v}<br>
                <b>County:</b> {county_v}
            </div>
            """
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=4,
                color=col,
                fill=True,
                fill_color=col,
                fill_opacity=0.85,
                popup=folium.Popup(popup_html, max_width=250),
            ).add_to(cluster)

        # Legend HTML
        legend_html = """
        <div style="position: fixed; bottom: 30px; left: 30px; width: 220px; z-index:9999;
                    background-color: white; padding: 10px; border: 1px solid #ccc;
                    border-radius: 6px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); font-family: sans-serif; font-size: 12px;">
            <b>Salinity Legend (EC)</b><br>
            <i style="background:#2ca02c; width:12px; height:12px; display:inline-block; border-radius:50%; margin-right:6px;"></i> Fresh (&lt;1,500 µS/cm)<br>
            <i style="background:#ff7f0e; width:12px; height:12px; display:inline-block; border-radius:50%; margin-right:6px;"></i> Brackish (1,500-3,000)<br>
            <i style="background:#d62728; width:12px; height:12px; display:inline-block; border-radius:50%; margin-right:6px;"></i> Saline (&gt;3,000 µS/cm)
        </div>
        """
        salinity_map.get_root().html.add_child(folium.Element(legend_html))

        st_folium(salinity_map, width="100%", height=600, returned_objects=[])
    else:
        st.info("Folium unavailable. Showing locations:")
        st.map(ec_df[["latitude", "longitude"]].dropna().rename(columns={"latitude": "lat", "longitude": "lon"}))

# ==================== TAB 3: YIELD PREDICTOR ====================
with tab3:
    st.subheader("Borehole Yield Prediction (Random Forest Model)")
    st.markdown(
        f"This machine learning model was trained on **{n_train_samples}** operational borehole records "
        "from the Acacia Water / Kenya Rapid+ survey to predict potential groundwater yield from drilling depth and coordinates."
    )

    col_form, col_res = st.columns([1, 1])

    with col_form:
        with st.form("yield_prediction_form"):
            st.markdown("#### Input Borehole Site Parameters")
            input_depth = st.number_input(
                "Planned Well Depth (meters)",
                min_value=5.0,
                max_value=350.0,
                value=75.0,
                step=5.0,
                help="Total drilled depth of the borehole in meters.",
            )
            input_lat = st.number_input(
                "Latitude (°)",
                min_value=-5.0,
                max_value=5.5,
                value=3.25,
                step=0.05,
                help="Decimal degrees (Kenya spans ~-4.7°S to 5.0°N).",
            )
            input_lon = st.number_input(
                "Longitude (°)",
                min_value=33.5,
                max_value=42.0,
                value=35.80,
                step=0.05,
                help="Decimal degrees (Kenya spans ~33.9°E to 41.9°E).",
            )
            submit_pred = st.form_submit_button("⚡ Predict Expected Yield", type="primary")

    with col_res:
        if submit_pred:
            features_vec = np.array([[input_depth, input_lat, input_lon]])
            pred_yield = rf_model.predict(features_vec)[0]

            # Calculate confidence interval using ensemble tree standard deviation
            tree_predictions = [tree.predict(features_vec)[0] for tree in rf_model.estimators_]
            tree_std = float(np.std(tree_predictions))
            lower_ci = max(0.0, pred_yield - 1.96 * tree_std)
            upper_ci = pred_yield + 1.96 * tree_std

            st.markdown("#### Prediction Results")
            st.metric("Predicted Aquifer Yield", f"{pred_yield:.2f} m³/h", help="Ensemble mean predicted yield")
            st.markdown(
                f"""
                - **95% Confidence Interval:** `{lower_ci:.2f}` — `{upper_ci:.2f} m³/h`
                - **Ensemble Tree Std Dev:** `± {tree_std:.2f} m³/h`
                """
            )

            # Categorize feasibility
            if pred_yield >= 5.0:
                st.success("🟢 **High Yield Potential:** Suitable for community distribution or mechanized solar pumping.")
            elif pred_yield >= 1.5:
                st.info("🟡 **Moderate Yield Potential:** Suitable for motorized pumping or school/clinic supply.")
            else:
                st.warning("🟠 **Low / Handpump Yield:** Suitable primarily for manual handpump extraction.")

            # Feature Importance
            if PLOTLY_AVAILABLE:
                feat_imp = pd.DataFrame(
                    {"Feature": ["Well Depth", "Latitude", "Longitude"], "Importance": rf_model.feature_importances_}
                ).sort_values("Importance", ascending=True)

                fig_fi = px.bar(
                    feat_imp,
                    x="Importance",
                    y="Feature",
                    orientation="h",
                    title="Random Forest Feature Relative Importance",
                    template="plotly_white",
                    height=240,
                )
                fig_fi.update_layout(margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig_fi, use_container_width=True)
        else:
            st.info("Enter the borehole depth and coordinates on the left and click **'Predict Expected Yield'**.")
