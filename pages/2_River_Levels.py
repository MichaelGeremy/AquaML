"""
Page 2: River Levels & Derived Discharge
Monitors river water levels (stage) and computes continuous streamflow discharge
using empirical power-law rating curves from the Gro for GooD project in Kwale County.
"""

from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.data_loader import load_timeseries, load_rating_curves, load_stations

st.title("River Water Levels & Streamflow Discharge 🌊")
st.markdown(
    "Analyze water level (stage) timeseries and rating-curve-derived discharge across "
    "hydrological monitoring stations in Kwale County, Coastal Kenya."
)

# Load metadata
stations_meta = load_stations()
station_options = ["3KD06", "KISCOL_Weir", "Eshu_Bridge"]
station_labels = {
    "3KD06": "Mukurumudzi River @ 3KD06 RGS",
    "KISCOL_Weir": "Mukurumudzi River @ KISCOL Weir",
    "Eshu_Bridge": "Ramisi River @ Eshu Bridge",
}

# Sidebar selection
st.sidebar.header("Station & Date Filter")
selected_station = st.sidebar.selectbox(
    "Select River Station",
    options=station_options,
    format_func=lambda s: f"{s} - {station_labels.get(s, s)}",
    index=0,
)

# Load timeseries
raw_ts = load_timeseries(selected_station)

# Handle empty logger fallback for Eshu_Bridge if needed
if raw_ts.empty or raw_ts["stage_m"].notna().sum() == 0:
    if selected_station == "Eshu_Bridge":
        st.info("Logger records for Eshu Bridge are uncalibrated; loading continuous manual gauge observations.")
        raw_ts = load_timeseries("ramisi_eshu_manual")

if raw_ts.empty or raw_ts["stage_m"].notna().sum() == 0:
    st.error(f"No valid stage data available for station {selected_station}.")
    st.stop()

# Ensure datetime and clean stage
df = raw_ts.dropna(subset=["datetime", "stage_m"]).sort_values("datetime").copy()

# Date range filter
min_date = df["datetime"].min().date()
max_date = df["datetime"].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_d, end_d = date_range
    df = df[(df["datetime"].dt.date >= start_d) & (df["datetime"].dt.date <= end_d)]
elif isinstance(date_range, (list, tuple)) and len(date_range) == 1:
    df = df[df["datetime"].dt.date >= date_range[0]]

if df.empty:
    st.warning("No records found in the selected date range. Please broaden your selection.")
    st.stop()

# Power-law rating curve model: Q = a * (H - b)^c
def power_law(h: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    return a * np.maximum(h - b, 0.0) ** c

# Load rating curve points
rc_all = load_rating_curves()
rc_station = rc_all[rc_all["station_id"] == selected_station].dropna(subset=["stage_m", "discharge_m3s"]).sort_values("stage_m")

# Derive discharge
a_param, b_param, c_param = None, None, None
fit_method = "Linear Interpolation"

# Check datum offset between logger stage and rating curve stage
logger_med = float(df["stage_m"].median())
rating_med = float(rc_station["stage_m"].median()) if not rc_station.empty else 0.0
datum_offset = (logger_med - rating_med) if abs(logger_med - rating_med) > 1.5 else 0.0
df["stage_aligned"] = df["stage_m"] - datum_offset

if not rc_station.empty:
    try:
        popt, _ = curve_fit(
            power_law,
            rc_station["stage_m"].values,
            rc_station["discharge_m3s"].values,
            p0=[1.0, 0.0, 1.5],
            bounds=([0.0, -1.0, 0.5], [100.0, 2.0, 4.0]),
            maxfev=5000,
        )
        a_param, b_param, c_param = popt
        df["discharge_m3s"] = power_law(df["stage_aligned"].values, *popt)
        fit_method = f"Power Law: Q = {a_param:.3f} · (H - {b_param:.3f})^{c_param:.3f}"
    except Exception as e:
        # Fallback to linear interpolation
        f_interp = interp1d(
            rc_station["stage_m"].values,
            rc_station["discharge_m3s"].values,
            kind="linear",
            bounds_error=False,
            fill_value="extrapolate",
        )
        df["discharge_m3s"] = np.maximum(f_interp(df["stage_aligned"].values), 0.0)
        fit_method = "Linear Interpolation (fallback)"
else:
    # If already has discharge column (e.g. manual gauge)
    if "discharge_m3s" not in df.columns:
        df["discharge_m3s"] = np.nan

# Resample to daily mean if > 5000 rows for fast and clean plotting
is_resampled = len(df) > 5000
if is_resampled:
    plot_df = (
        df.set_index("datetime")
        .resample("D")
        .agg({"stage_m": "mean", "discharge_m3s": "mean"})
        .dropna(subset=["stage_m"])
        .reset_index()
    )
    freq_label = "Daily Mean"
else:
    plot_df = df
    freq_label = "Recorded Resolution"

# Key Metrics Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Mean Stage (H)", f"{df['stage_m'].mean():.2f} m")
with col2:
    st.metric("Max Stage (H)", f"{df['stage_m'].max():.2f} m")
with col3:
    mean_q = df["discharge_m3s"].mean()
    st.metric("Mean Discharge (Q)", f"{mean_q:.2f} m³/s" if pd.notna(mean_q) else "N/A")
with col4:
    start_str = df["datetime"].min().strftime("%b %Y")
    end_str = df["datetime"].max().strftime("%b %Y")
    st.metric("Observation Period", f"{start_str} - {end_str}")

# Plotly visualization
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

if PLOTLY_AVAILABLE:
    # Row 1: Stage chart (Blue)
    fig_stage = go.Figure()
    fig_stage.add_trace(
        go.Scatter(
            x=plot_df["datetime"],
            y=plot_df["stage_m"],
            mode="lines",
            name="Stage (m)",
            line=dict(color="#1f77b4", width=1.5),
        )
    )
    fig_stage.update_layout(
        title=f"Water Level Stage (m) — {station_labels.get(selected_station, selected_station)} ({freq_label})",
        xaxis_title="Date",
        yaxis_title="Stage H (m)",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=50, b=40),
        height=340,
        template="plotly_white",
    )
    st.plotly_chart(fig_stage, use_container_width=True)

    # Row 2: Discharge chart (Green)
    if "discharge_m3s" in plot_df.columns and plot_df["discharge_m3s"].notna().sum() > 0:
        fig_q = go.Figure()
        fig_q.add_trace(
            go.Scatter(
                x=plot_df["datetime"],
                y=plot_df["discharge_m3s"],
                mode="lines",
                name="Discharge (m³/s)",
                line=dict(color="#2ca02c", width=1.5),
            )
        )
        fig_q.update_layout(
            title=f"Streamflow Discharge (m³/s) — {fit_method}",
            xaxis_title="Date",
            yaxis_title="Discharge Q (m³/s)",
            hovermode="x unified",
            margin=dict(l=40, r=40, t=50, b=40),
            height=340,
            template="plotly_white",
        )
        st.plotly_chart(fig_q, use_container_width=True)

else:
    st.subheader(f"Water Level Stage (m) — {freq_label}")
    st.line_chart(plot_df.set_index("datetime")["stage_m"])
    if "discharge_m3s" in plot_df.columns:
        st.subheader("Streamflow Discharge (m³/s)")
        st.line_chart(plot_df.set_index("datetime")["discharge_m3s"])

# Expandable Rating Curve Details
with st.expander("Rating Curve Calibration & Details"):
    st.markdown(f"**Station:** `{selected_station}`")
    st.markdown(f"**Rating Model:** `{fit_method}`")
    if datum_offset > 0:
        st.markdown(f"**Datum Offset Applied:** `{datum_offset:.3f} m` (aligns sensor installation datum to staff gauge zero)")
    if not rc_station.empty:
        st.dataframe(rc_station, use_container_width=True)

st.caption("Rating curve source: Gro for GooD project — Kwale County, Kenya.")
