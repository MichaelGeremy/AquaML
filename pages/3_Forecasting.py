"""
Page 3: River Discharge Forecasting — Mukurumudzi 3KD06
Trains an XGBoost gradient boosting regressor on lag features of derived streamflow,
evaluates performance using hydrological efficiency metrics (NSE, KGE, RMSE, MAE, R²),
and benchmarks against a persistence baseline.
"""

from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
from scipy.optimize import curve_fit

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.data_loader import load_timeseries, load_rating_curves
from src.preprocessing import create_lag_features, temporal_train_test_split
from src.evaluation import regression_report

st.title("River Discharge Forecasting — Mukurumudzi 3KD06 📈")
st.markdown(
    "Machine learning streamflow forecast using lag-based feature engineering and gradient boosting. "
    "Trained on rating-curve-derived daily mean discharge from the Mukurumudzi River gauge station."
)

# Sidebar configurations
st.sidebar.header("Forecast Settings")
horizon = st.sidebar.slider(
    "Forecast Horizon (Days)",
    min_value=1,
    max_value=30,
    value=1,
    help="Target lead time for the discharge forecast (1 = next day).",
)
test_split_pct = st.sidebar.slider(
    "Test Set Split (%)",
    min_value=10,
    max_value=30,
    value=20,
    step=5,
    help="Portion of chronologically recent records reserved for model evaluation.",
)
test_ratio = test_split_pct / 100.0

run_button = st.sidebar.button("🚀 Run Forecast", type="primary")

# Load and prepare daily discharge pipeline
@st.cache_data
def get_daily_discharge_3kd06() -> pd.DataFrame:
    """Load Mukurumudzi 3KD06 stage, calibrate datum offset, and derive daily discharge."""
    rc_all = load_rating_curves()
    meas = rc_all[(rc_all["station_id"] == "3KD06") & (rc_all["source"] == "measured")].dropna(subset=["stage_m", "discharge_m3s"]).sort_values("stage_m")
    if meas.empty:
        meas = rc_all[rc_all["station_id"] == "3KD06"].dropna(subset=["stage_m", "discharge_m3s"]).sort_values("stage_m")

    # Power law fit
    def power_law(h, a, b, c):
        return a * np.maximum(h - b, 0.0) ** c

    popt, _ = curve_fit(
        power_law,
        meas["stage_m"].values,
        meas["discharge_m3s"].values,
        p0=[1.0, 0.0, 1.5],
        bounds=([0.0, -1.0, 0.5], [100.0, 2.0, 4.0]),
        maxfev=5000,
    )

    ts = load_timeseries("3KD06")
    ts = ts.dropna(subset=["datetime", "stage_m"]).sort_values("datetime").copy()

    # Align logger datum
    logger_med = float(ts["stage_m"].median())
    rating_med = float(meas["stage_m"].median())
    offset = logger_med - rating_med
    ts["stage_aligned"] = ts["stage_m"] - offset
    ts["discharge_m3s"] = power_law(ts["stage_aligned"].values, *popt)

    # Resample daily
    daily = (
        ts.set_index("datetime")
        .resample("D")
        .agg({"stage_m": "mean", "discharge_m3s": "mean"})
        .dropna(subset=["discharge_m3s"])
        .reset_index()
    )
    return daily

@st.cache_resource
def train_forecast_model(X_train: np.ndarray, y_train: np.ndarray):
    """Train XGBoost Regressor (or GradientBoosting fallback)."""
    try:
        from xgboost import XGBRegressor
        model = XGBRegressor(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            random_state=42,
            n_jobs=-1,
        )
        model_name = "XGBoost Regressor"
    except ImportError:
        from sklearn.ensemble import GradientBoostingRegressor
        model = GradientBoostingRegressor(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            random_state=42,
        )
        model_name = "Gradient Boosting Regressor (sklearn)"

    model.fit(X_train, y_train)
    return model, model_name

daily_df = get_daily_discharge_3kd06()

# Informational overview
st.info(
    f"Loaded **{len(daily_df):,}** daily records from Mukurumudzi 3KD06 "
    f"({daily_df['datetime'].min().strftime('%Y-%m-%d')} to {daily_df['datetime'].max().strftime('%Y-%m-%d')}). "
    f"Click **'Run Forecast'** in the sidebar to execute lag feature engineering and model training."
)

if run_button or "forecast_done" in st.session_state:
    st.session_state["forecast_done"] = True

    with st.spinner("Engineering lag features and training gradient boosted model..."):
        # Create base lag features [1, 2, 3, 7, 14]
        df_lags = create_lag_features(
            daily_df[["datetime", "discharge_m3s"]].copy(),
            target_col="discharge_m3s",
            lags=[1, 2, 3, 7, 14],
        )

        # Handle lead-time horizon
        if horizon > 1:
            df_lags["target"] = df_lags["discharge_m3s"].shift(-(horizon - 1))
            df_lags = df_lags.dropna(subset=["target"]).reset_index(drop=True)
            target_col = "target"
        else:
            target_col = "discharge_m3s"

        # Temporal train/test split (never shuffle time series)
        train_df, test_df = temporal_train_test_split(
            df_lags,
            test_ratio=test_ratio,
            date_col="datetime",
        )

        feature_cols = [c for c in train_df.columns if c not in ["datetime", "discharge_m3s", "target"]]
        X_train, y_train = train_df[feature_cols].values, train_df[target_col].values
        X_test, y_test = test_df[feature_cols].values, test_df[target_col].values

        # Train model
        model, model_type = train_forecast_model(X_train, y_train)
        y_pred = model.predict(X_test)

        # Baseline: persistence forecast (lag 1)
        y_persist = test_df["discharge_m3s_lag1"].values

        # Hydrological regression evaluation metrics
        metrics = regression_report(y_test, y_pred)
        persist_metrics = regression_report(y_test, y_persist)

    # Model Overview & Metrics Cards
    st.subheader(f"Evaluation Metrics on Test Partition ({len(test_df)} days, Lead Time = {horizon}d)")
    st.caption(f"Engine: `{model_type}` | Features: `{', '.join(feature_cols)}`")

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        nse_val = metrics["NSE"]
        delta_nse = round(nse_val - persist_metrics["NSE"], 4)
        st.metric("NSE (Efficiency)", f"{nse_val:.4f}", delta=f"{delta_nse:+.4f} vs Persist")
    with m2:
        kge_val = metrics["KGE"]
        delta_kge = round(kge_val - persist_metrics["KGE"], 4)
        st.metric("KGE (Kling-Gupta)", f"{kge_val:.4f}", delta=f"{delta_kge:+.4f} vs Persist")
    with m3:
        rmse_val = metrics["RMSE"]
        delta_rmse = round(rmse_val - persist_metrics["RMSE"], 4)
        st.metric("RMSE (m³/s)", f"{rmse_val:.4f}", delta=f"{delta_rmse:+.4f} vs Persist", delta_color="inverse")
    with m4:
        mae_val = metrics["MAE"]
        delta_mae = round(mae_val - persist_metrics["MAE"], 4)
        st.metric("MAE (m³/s)", f"{mae_val:.4f}", delta=f"{delta_mae:+.4f} vs Persist", delta_color="inverse")
    with m5:
        r2_val = metrics["R2"]
        st.metric("R² Score", f"{r2_val:.4f}")

    # Plotly Forecast Chart
    try:
        import plotly.graph_objects as go
        PLOTLY_AVAILABLE = True
    except ImportError:
        PLOTLY_AVAILABLE = False

    st.markdown("### Hydrograph: Observed vs Predicted Discharge")
    if PLOTLY_AVAILABLE:
        fig = go.Figure()
        # Observed
        fig.add_trace(
            go.Scatter(
                x=test_df["datetime"],
                y=y_test,
                mode="lines",
                name="Observed Discharge",
                line=dict(color="#1f77b4", width=2.0),
            )
        )
        # Predicted
        fig.add_trace(
            go.Scatter(
                x=test_df["datetime"],
                y=y_pred,
                mode="lines",
                name=f"Predicted ({model_type})",
                line=dict(color="#d62728", width=2.0, dash="dash"),
            )
        )
        # Persistence Baseline
        fig.add_trace(
            go.Scatter(
                x=test_df["datetime"],
                y=y_persist,
                mode="lines",
                name="Persistence Baseline (Lag-1)",
                line=dict(color="#7f7f7f", width=1.0, dash="dot"),
                opacity=0.7,
            )
        )
        fig.update_layout(
            title=f"Mukurumudzi 3KD06 Streamflow Forecast (Lead Time = {horizon} Day{'s' if horizon > 1 else ''})",
            xaxis_title="Date",
            yaxis_title="Discharge Q (m³/s)",
            hovermode="x unified",
            height=450,
            template="plotly_white",
            legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.02),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Feature Importance Bar Chart
        st.markdown("### Feature Importance")
        importances = getattr(model, "feature_importances_", None)
        if importances is not None:
            feat_df = pd.DataFrame({"Feature": feature_cols, "Importance": importances}).sort_values("Importance", ascending=True)
            fig_imp = go.Figure(
                go.Bar(
                    x=feat_df["Importance"],
                    y=feat_df["Feature"],
                    orientation="h",
                    marker=dict(color="#0077B6"),
                )
            )
            fig_imp.update_layout(
                title="Lag Feature Importance (Gini / Split Gain)",
                xaxis_title="Relative Importance",
                yaxis_title="Feature",
                height=300,
                template="plotly_white",
                margin=dict(l=40, r=40, t=40, b=40),
            )
            st.plotly_chart(fig_imp, use_container_width=True)

    else:
        # Fallback chart
        chart_df = pd.DataFrame(
            {"Observed": y_test, "Predicted": y_pred, "Persistence": y_persist},
            index=test_df["datetime"],
        )
        st.line_chart(chart_df)

    st.caption("Hydrological benchmark: Nash-Sutcliffe Efficiency (NSE) > 0.75 indicates very good streamflow model performance.")
