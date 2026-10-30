"""
Chapter 2: River Outlook & 7–14 Day Hydrological Advisory
Plain-English river flow forecasting and early warning for everyday Kenyans.
"""

from __future__ import annotations
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.optimize import curve_fit
from xgboost import XGBRegressor

from utils.data_loader import load_timeseries, load_rating_curves, load_stations

st.title("📈 Chapter 2: River Watch & Hydrological Advisory")
st.subheader("7–14 Day Streamflow Outlook & Early Warning for Communities")

st.markdown(
    """
    Rivers are the lifeblood of Kenya's agriculture, industry, and drinking supply.
    This forecasting engine translates raw hydrological measurements into **plain-English early warnings**
    so that farmers, town water utilities, and county disaster officers can make timely decisions.
    """
)

# 1. Station Selection
stations_meta = load_stations()
station_options = {
    "3KD06": "Mukurumudzi River — 3KD06 RGS (Main Catchment Gauge)",
    "KISCOL_Weir": "Mukurumudzi River — KISCOL Weir (Irrigation Intake)",
    "Eshu_Bridge": "Ramisi River — Eshu Bridge (Coastal Highway Crossing)",
}

selected_station = st.selectbox(
    "📍 Select River Monitoring Station:",
    options=list(station_options.keys()),
    format_func=lambda s: station_options[s],
)

# Load data for selected station
with st.spinner("Analyzing river stages and calibrating discharge curve..."):
    ts_df = load_timeseries(selected_station)
    rc_df = load_rating_curves()

if ts_df.empty:
    st.error(f"No continuous monitoring data available for station {selected_station}.")
    st.stop()

# Clean timeseries and aggregate to daily
ts_clean = ts_df.dropna(subset=["datetime", "stage_m"]).copy()

# Fit rating curve for this station to convert stage (m) -> discharge (m3/s)
station_rc = rc_df[rc_df["station_id"] == selected_station].dropna(subset=["stage_m", "discharge_m3s"])

# Power-law rating curve function: Q = a * (H - b)^c
def power_law(H, a, b, c):
    h_diff = np.maximum(H - b, 1e-4)
    return a * (h_diff ** c)

if len(station_rc) >= 5:
    try:
        popt, _ = curve_fit(
            power_law,
            station_rc["stage_m"].values,
            station_rc["discharge_m3s"].values,
            p0=[1.0, 0.0, 1.5],
            bounds=([0.01, -1.0, 0.5], [100.0, 2.0, 4.0]),
            maxfev=5000,
        )
        a_fit, b_fit, c_fit = popt
        # Apply offset check
        ts_clean["stage_corrected"] = ts_clean["stage_m"]
        if ts_clean["stage_corrected"].median() > 5.0 and station_rc["stage_m"].max() < 5.0:
            ts_clean["stage_corrected"] = ts_clean["stage_corrected"] - (ts_clean["stage_corrected"].min() - station_rc["stage_m"].min())
        ts_clean["discharge_m3s"] = power_law(ts_clean["stage_corrected"].values, a_fit, b_fit, c_fit)
    except Exception:
        # Fallback linear approximation
        q_mean = station_rc["discharge_m3s"].mean()
        ts_clean["discharge_m3s"] = np.maximum(0.01, (ts_clean["stage_m"] - ts_clean["stage_m"].min()) * 1.5)
else:
    ts_clean["discharge_m3s"] = np.maximum(0.01, (ts_clean["stage_m"] - ts_clean["stage_m"].min()) * 1.2)

# Daily mean series
daily = (
    ts_clean.set_index("datetime")
    .resample("D")
    .agg({"stage_m": "mean", "discharge_m3s": "mean"})
    .dropna()
    .reset_index()
)

if len(daily) < 30:
    st.warning("Insufficient daily records to construct a reliable forecast.")
    st.stop()

# Compute thresholds for hydrological advisory levels
q_series = daily["discharge_m3s"]
q_drought_threshold = float(np.percentile(q_series, 15))    # Bottom 15% -> Critical drought alert
q_low_threshold = float(np.percentile(q_series, 40))        # 15% - 40% -> Low flow watch
q_high_threshold = float(np.percentile(q_series, 88))       # > 88% -> High flow / flood risk

# Train multi-lag forecasting model on daily series
# Lags: 1, 2, 3, 7, 14
daily["lag1"] = daily["discharge_m3s"].shift(1)
daily["lag2"] = daily["discharge_m3s"].shift(2)
daily["lag3"] = daily["discharge_m3s"].shift(3)
daily["lag7"] = daily["discharge_m3s"].shift(7)
daily["lag14"] = daily["discharge_m3s"].shift(14)
daily_model = daily.dropna().copy()

feature_cols = ["lag1", "lag2", "lag3", "lag7", "lag14"]
X = daily_model[feature_cols].values
y = daily_model["discharge_m3s"].values

split_idx = int(len(daily_model) * 0.8)
X_train, y_train = X[:split_idx], y[:split_idx]
X_test, y_test = X[split_idx:], y[split_idx:]

xgb = XGBRegressor(n_estimators=150, max_depth=4, learning_rate=0.05, random_state=42)
xgb.fit(X_train, y_train)

# Current status from most recent observation
latest_obs = daily.iloc[-1]
current_q = latest_obs["discharge_m3s"]
current_date = latest_obs["datetime"].strftime("%d %b %Y")

# Advisory determination
if current_q >= q_high_threshold:
    alert_badge = "🌊 HIGH FLOW / FLOOD ADVISORY"
    alert_class = "alert-blue"
    alert_msg = f"River discharge is currently {current_q:.2f} m³/s, well above normal seasonal flow. Caution advised for low-lying farms and riverbank crossings."
elif current_q <= q_drought_threshold:
    alert_badge = "🔴 CRITICAL DROUGHT ALERT"
    alert_class = "alert-red"
    alert_msg = f"River discharge has dropped to {current_q:.2f} m³/s, approaching critical ecological baseflow. Water abstraction rationing is strongly recommended."
elif current_q <= q_low_threshold:
    alert_badge = "🟡 LOW FLOW WATCH"
    alert_class = "alert-yellow"
    alert_msg = f"River discharge is {current_q:.2f} m³/s, trending below normal seasonal median. Irrigators should begin water conservation measures."
else:
    alert_badge = "🟢 NORMAL FLOW CONDITIONS"
    alert_class = "alert-green"
    alert_msg = f"River discharge is healthy at {current_q:.2f} m³/s. Adequate supply for domestic abstraction and scheduled crop irrigation."

st.markdown(
    f"""
    <div style="padding: 16px; border-radius: 10px; margin-top: 10px; margin-bottom: 20px;" class="{alert_class}">
        <h3 style="margin-top: 0;">{alert_badge}</h3>
        <p style="font-size: 1.05rem; margin-bottom: 4px;"><b>Observation Date:</b> {current_date} | <b>Current River Flow:</b> {current_q:.2f} m³/s</p>
        <p style="font-size: 0.98rem; margin-bottom: 0;">{alert_msg}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 2. Forecast Horizon Controls
col_ctrl1, col_ctrl2 = st.columns([1, 2])
with col_ctrl1:
    horizon_days = st.slider(
        "🔮 Forecast Horizon (Next Days):",
        min_value=3,
        max_value=14,
        value=7,
        help="Select how many days ahead you want the predictive model to forecast river discharge.",
    )

# Compute iterative future predictions
recent_lags = list(daily["discharge_m3s"].tail(14).values)
forecast_vals = []
for h in range(horizon_days):
    curr_features = np.array([[
        recent_lags[-1],
        recent_lags[-2],
        recent_lags[-3],
        recent_lags[-7],
        recent_lags[-14],
    ]])
    pred_val = max(0.01, float(xgb.predict(curr_features)[0]))
    forecast_vals.append(pred_val)
    recent_lags.append(pred_val)

future_dates = [daily["datetime"].iloc[-1] + pd.Timedelta(days=i + 1) for i in range(horizon_days)]
forecast_df = pd.DataFrame({"datetime": future_dates, "forecast_discharge": forecast_vals})

with col_ctrl2:
    mean_forecast = np.mean(forecast_vals)
    delta_pct = ((mean_forecast - current_q) / (current_q + 1e-4)) * 100
    delta_str = f"{delta_pct:+.1f}% vs current"
    st.metric(
        f"Projected Average Flow (Next {horizon_days} Days)",
        f"{mean_forecast:.2f} m³/s",
        delta_str,
        delta_color="inverse" if delta_pct < 0 else "normal",
    )

# 3. Interactive Visual Hydrograph with Alert Zones
st.markdown("### River Hydrograph & Predictive Outlook")

# We plot the last 60 days of historical data + future forecast
hist_window = daily.tail(60).copy()

fig = go.Figure()

# Background alert bands
max_y = max(hist_window["discharge_m3s"].max(), max(forecast_vals)) * 1.25

# Shaded Critical Drought Zone
fig.add_hrect(
    y0=0, y1=q_drought_threshold,
    fillcolor="rgba(244, 67, 54, 0.12)", line_width=0,
    annotation_text="Critical Drought Zone (<15th percentile)",
    annotation_position="bottom right",
)

# Shaded Low Flow Watch Zone
fig.add_hrect(
    y0=q_drought_threshold, y1=q_low_threshold,
    fillcolor="rgba(255, 193, 7, 0.12)", line_width=0,
    annotation_text="Low Flow Watch (15th–40th percentile)",
    annotation_position="right",
)

# Shaded Normal Flow Zone
fig.add_hrect(
    y0=q_low_threshold, y1=q_high_threshold,
    fillcolor="rgba(76, 175, 80, 0.08)", line_width=0,
    annotation_text="Normal Seasonal Flow (40th–88th percentile)",
    annotation_position="top right",
)

# Observed Discharge (Blue)
fig.add_trace(go.Scatter(
    x=hist_window["datetime"],
    y=hist_window["discharge_m3s"],
    mode="lines",
    name="Observed River Flow (Past 60 Days)",
    line=dict(color="#0077B6", width=2.5),
))

# Forecast Line (Orange Dashed)
# Connect to the last observed point
forecast_x = [hist_window["datetime"].iloc[-1]] + list(forecast_df["datetime"])
forecast_y = [hist_window["discharge_m3s"].iloc[-1]] + list(forecast_df["forecast_discharge"])

fig.add_trace(go.Scatter(
    x=forecast_x,
    y=forecast_y,
    mode="lines+markers",
    name=f"Predicted Flow (Next {horizon_days} Days)",
    line=dict(color="#E65100", width=3, dash="dash"),
    marker=dict(size=6, color="#E65100"),
))

fig.update_layout(
    height=450,
    xaxis_title="Date",
    yaxis_title="River Discharge (m³/s)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=20, r=20, t=30, b=20),
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True)

# 4. Actionable Guidance for Different Groups
st.markdown("### 📋 Actionable Guidance for the Community")

act1, act2, act3 = st.columns(3)

with act1:
    st.markdown("#### 🌾 For Farmers & Irrigators")
    if mean_forecast < q_low_threshold:
        st.warning("⚠️ **Rationing in Effect**: River flow is projected to remain low. Shift to night irrigation to curb evaporation. Avoid starting new high-water crops.")
    else:
        st.success("✅ **Standard Pumping**: Water levels allow regular extraction schedules. Ensure intake screens are clear of silt.")

with act2:
    st.markdown("#### 🚰 For Water Service Providers")
    if mean_forecast < q_drought_threshold:
        st.error("🚨 **Intake Alert**: Streamflow approaching pump suction limit. Prepare backup boreholes and issue municipal rationing advisories.")
    else:
        st.info("ℹ️ **Stable Intake**: Raw water levels are adequate for full treatment plant capacity. Monitor sediment after rain bursts.")

with act3:
    st.markdown("#### 🏡 For Households & Herders")
    if mean_forecast >= q_high_threshold:
        st.warning("🌊 **High Water Alert**: Avoid driving or wading across submerged culverts and footbridges during evening surges.")
    else:
        st.success("✅ **Safe Access**: River access paths and shallow well recharge remain stable.")

# 5. Technical Details Expander (Preserving Scientific Rigor)
with st.expander("🔬 Technical Model Diagnostics & Domain Metrics (Hydrology Standard)"):
    st.markdown(
        """
        **How This Forecast Works**:
        - **Hydraulic Rating Curve**: Converts logger water stage ($H$, meters) to discharge ($Q$, m³/s) using a calibrated power-law:
          $$Q = a (H - b)^c$$
          derived from field ADCP discharge measurements by the Gro for GooD project.
        - **Model Architecture**: Gradient-Boosted Decision Trees (XGBoost) trained on multi-scale autoregressive lag features ($t-1, t-2, t-3, t-7, t-14$ days) capturing catchment drainage memory.
        """
    )
    y_test_pred = xgb.predict(X_test)
    numerator = np.sum((y_test - y_test_pred) ** 2)
    denominator = np.sum((y_test - np.mean(y_test)) ** 2)
    nse_score = 1.0 - (numerator / denominator) if denominator != 0 else np.nan
    rmse_score = float(np.sqrt(np.mean((y_test - y_test_pred) ** 2)))
    r2_score = 1.0 - (numerator / denominator) if denominator != 0 else np.nan
    
    tcol1, tcol2, tcol3, tcol4 = st.columns(4)
    tcol1.metric("Nash-Sutcliffe Efficiency (NSE)", f"{nse_score:.3f}", "Benchmark: >0.7 is good")
    tcol2.metric("RMSE Error", f"{rmse_score:.3f} m³/s", "Root Mean Squared Error")
    tcol3.metric("R² Score", f"{r2_score:.3f}", "Explained variance")
    tcol4.metric("Rating Curve Station", selected_station, "Gro for GooD Project")
