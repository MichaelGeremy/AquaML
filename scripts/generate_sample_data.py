"""
Generate realistic sample datasets so all notebooks run out-of-the-box.
Run once: python scripts/generate_sample_data.py
"""

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

np.random.seed(42)
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "sample"
SAMPLE.mkdir(parents=True, exist_ok=True)


def generate_streamflow(n_days: int = 2000) -> pd.DataFrame:
    """Synthetic daily streamflow with seasonality + noise + occasional floods."""
    dates = pd.date_range("2015-01-01", periods=n_days, freq="D")
    t = np.arange(n_days)

    # Base seasonal signal (higher in spring/early summer)
    seasonal = 15 + 12 * np.sin(2 * np.pi * (t - 60) / 365.25)
    # Long-term trend + noise
    trend = 0.002 * t
    noise = np.random.normal(0, 3.5, n_days)
    # Occasional high-flow events
    floods = np.zeros(n_days)
    flood_idx = np.random.choice(n_days, size=25, replace=False)
    floods[flood_idx] = np.random.uniform(40, 120, size=25)

    q = np.maximum(0.5, seasonal + trend + noise + floods)

    # Simple meteorological drivers
    precip = np.maximum(0, np.random.gamma(1.2, 2.5, n_days) + 8 * (floods > 0))
    temp = 12 + 10 * np.sin(2 * np.pi * (t - 30) / 365.25) + np.random.normal(0, 2.5, n_days)

    df = pd.DataFrame({
        "date": dates,
        "streamflow_m3s": np.round(q, 2),
        "precip_mm": np.round(precip, 2),
        "temp_c": np.round(temp, 1),
        "dayofyear": dates.dayofyear,
        "month": dates.month,
    })
    return df


def generate_water_quality(n_samples: int = 2500) -> pd.DataFrame:
    """Synthetic water quality measurements with clear quality classes."""
    # Features that drive quality
    ph = np.random.normal(7.2, 0.8, n_samples)
    turbidity = np.random.lognormal(1.5, 0.9, n_samples)
    do = np.random.normal(8.5, 1.8, n_samples)          # dissolved oxygen
    bod = np.random.lognormal(1.0, 0.7, n_samples)       # biological oxygen demand
    nitrate = np.random.lognormal(0.8, 0.9, n_samples)
    temp = np.random.normal(18, 5, n_samples)

    # Simple rule-based quality label (Good / Fair / Poor)
    score = (
        -0.8 * np.abs(ph - 7.2)
        - 0.15 * turbidity
        + 0.4 * do
        - 0.3 * bod
        - 0.2 * nitrate
        + np.random.normal(0, 0.8, n_samples)
    )
    labels = np.where(score > 2.5, "Good",
                      np.where(score > 0.0, "Fair", "Poor"))

    df = pd.DataFrame({
        "ph": np.round(ph, 2),
        "turbidity_ntu": np.round(turbidity, 2),
        "dissolved_oxygen_mgl": np.round(do, 2),
        "bod_mgl": np.round(bod, 2),
        "nitrate_mgl": np.round(nitrate, 2),
        "temp_c": np.round(temp, 1),
        "quality": labels,
    })
    return df


def generate_hydrology_reports(n_reports: int = 400) -> pd.DataFrame:
    """Synthetic short hydrological incident / situation reports for NLP."""
    locations = [
        "Upper Blue River", "Lower Mekong", "Nile Delta", "Colorado River Basin",
        "Yangtze Tributary", "Rhine Valley", "Murray-Darling", "Amazon Floodplain",
        "Ganges Delta", "Danube Basin", "Mississippi Lower", "Zambezi Catchment"
    ]
    templates = {
        "severe": [
            "Severe flooding reported in {loc}. Water levels exceeded critical threshold by {x} m. Evacuations underway.",
            "Flash flood warning issued for {loc}. Intense rainfall of {x} mm in 6 hours caused rapid rise in river stage.",
            "Major flood event in {loc}. Infrastructure damage extensive. Peak discharge estimated at {x} m3/s.",
        ],
        "moderate": [
            "Moderate high flows observed in {loc}. River stage rising steadily after {x} mm rainfall.",
            "Elevated water levels in {loc}. Monitoring continues. No immediate threat to settlements.",
            "Seasonal flooding in {loc} within expected range. Peak expected in next 48 hours.",
        ],
        "normal": [
            "Normal flow conditions in {loc}. Water quality parameters within acceptable limits.",
            "Routine monitoring of {loc} shows stable stage and discharge near long-term median.",
            "No significant hydrological anomalies reported for {loc} this week.",
        ],
        "drought": [
            "Prolonged low flows in {loc}. Streamflow at {x}% of normal for this time of year.",
            "Drought conditions intensifying in {loc}. Reservoir levels critically low.",
            "Water scarcity alert for {loc}. Irrigation restrictions recommended.",
        ],
    }

    rows = []
    for i in range(n_reports):
        sev = np.random.choice(list(templates.keys()), p=[0.18, 0.32, 0.35, 0.15])
        loc = np.random.choice(locations)
        x = np.random.randint(15, 280) if sev != "normal" else np.random.randint(70, 110)
        text = np.random.choice(templates[sev]).format(loc=loc, x=x)
        # Add some noise / extra sentences
        if np.random.rand() > 0.6:
            text += " Local authorities are coordinating response efforts."
        rows.append({
            "report_id": f"R{i:04d}",
            "date": (datetime(2018, 1, 1) + timedelta(days=np.random.randint(0, 2500))).strftime("%Y-%m-%d"),
            "location": loc,
            "text": text,
            "severity": sev,
        })
    return pd.DataFrame(rows)


def main():
    print("Generating sample datasets...")

    sf = generate_streamflow()
    sf.to_csv(SAMPLE / "streamflow_daily.csv", index=False)
    print(f"  ✓ streamflow_daily.csv  ({len(sf)} rows)")

    wq = generate_water_quality()
    wq.to_csv(SAMPLE / "water_quality.csv", index=False)
    print(f"  ✓ water_quality.csv     ({len(wq)} rows)")

    reports = generate_hydrology_reports()
    reports.to_csv(SAMPLE / "hydrology_reports.csv", index=False)
    print(f"  ✓ hydrology_reports.csv ({len(reports)} rows)")

    # Tiny placeholder for CV – real images would be downloaded separately
    (SAMPLE / "cv_readme.txt").write_text(
        "For computer vision notebooks:\n"
        "1. Download a small subset of FloodNet or similar water/flood imagery, or\n"
        "2. Use the synthetic generator in the notebook to create simple RGB patches.\n"
        "See notebook 04 for details.\n"
    )
    print("  ✓ cv_readme.txt")

    print("\nDone. Sample data ready in data/sample/")


if __name__ == "__main__":
    main()
