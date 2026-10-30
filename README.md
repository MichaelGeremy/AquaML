# AquaML Kenya 💧🇰🇪
### Applied Machine Learning for Kenya Water Resources & Hydrology

An end-to-end data science and machine learning portfolio project focused on **real-world water resources, hydrology, and climate resilience in Kenya**.

Covers four foundational pillars using real ground-truth monitoring data and open environmental datasets:

| Pillar | Focus | Methods & Algorithms | Key Datasets |
|---|---|---|---|
| **Pillar 1: Time-Series Forecasting** | River stage & discharge forecasting | HEC-RAS rating curves, lag features, XGBoost, NSE / KGE metrics | Mukurumudzi River (3KD06, KISCOL Weir), Ramisi River (Eshu Bridge) |
| **Pillar 2: Groundwater Yield & Quality** | Borehole yield regression & salinity classification | Random Forest, XGBoost, feature importance, WHO salinity bins | Acacia Water / Kenya Rapid+ & Rural Focus ASAL boreholes |
| **Pillar 3: Spatial Analysis & CV** | Water point density & water-body segmentation | Spatial overlays, U-Net CNN segmentation, Dice / IoU | mWater Kenya inventory (21k+ points), Africover river network, FloodExtent01 |
| **Pillar 4: NLP Situation Reports** | Severity classification & topic extraction | TF-IDF, Logistic Regression, LDA topic modeling | County-level flood & drought incident reports |

---

## Real Kenyan Datasets (`data/kenya/`)

All datasets are curated, processed, and ready for modeling:

1. **Groundwater & Boreholes (CSV)**
   - `kenya_waterpoints_mwater_clean.csv`: **21,284 records** across Kenya with geographic coordinates, waterpoint type, elevation, county, and ward.
   - `kenya_boreholes_acacia_rapid.csv`: **3,125 borehole records** in ASAL counties (Turkana, Wajir, Garissa, Isiolo, Marsabit) with yield, well depth, EC, and operational status.
   - `kenya_boreholes_rural_focus.csv`: **1,414 records** in Turkana & Marsabit with EC, pH, temperature, and rest water level.

2. **River Stage-Discharge Rating Curves (`rating_curves/`)**
   - Measured and HEC-RAS simulated stage ($H$) to discharge ($Q$) rating curves for coastal Kenya basins (Gro for GooD project).
   - Stations: `3KD06` (Mukurumudzi), `KISCOL_Weir` (Mukurumudzi), and `Eshu_Bridge` (Ramisi).

3. **Continuous Water-Level Time Series (`timeseries/`)**
   - High-frequency automated logger records (stage, barometric pressure, temperature):
     - `mukurumudzi_3KD06_water_level.csv` (~23k logger records)
     - `mukurumudzi_KISCOL_water_level.csv`
     - `ramisi_eshu_logger_water_level.csv` & `ramisi_eshu_manual_gauge.csv`

4. **GIS Vector Layers (`gis/`)**
   - `AFRICOVER_KE_RIVERS.*`: Africover Kenya river network shapefile.
   - `FloodExtent01.*`: Flood extent polygons for flood mapping and CV alignment.
   - `KEN_Lakes.*`: Kenya national lakes shapefile.

---

## Project Structure

```
AquaML/
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
├── data/
│   └── kenya/
│       ├── gis/                     # Africover rivers, flood extent, lakes
│       ├── rating_curves/           # Mukurumudzi & Ramisi H-Q curves
│       ├── timeseries/              # High-frequency water level loggers
│       ├── kenya_boreholes_acacia_rapid.csv
│       ├── kenya_boreholes_rural_focus.csv
│       ├── kenya_waterpoints_mwater_clean.csv
│       └── README.md
├── notebooks/
│   ├── 07_kenya_timeseries_forecasting.ipynb   # Pillar 1
│   ├── 08_kenya_borehole_yield_quality.ipynb   # Pillar 2
│   ├── 09_kenya_spatial_cv.ipynb               # Pillar 3
│   └── 10_kenya_nlp_situation_reports.ipynb   # Pillar 4
├── src/
│   ├── evaluation.py               # NSE, KGE, RMSE, classification reports
│   ├── preprocessing.py            # Lag generation, temporal splits
│   └── visualization.py            # Hydrographs, residual plots, confusion matrices
├── reports/figures/
└── docs/
    └── methodology.md
```

---

## Quick Start

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/MichaelGeremy/AquaML.git
cd AquaML

# Create virtual environment
python -m venv venv
venv\Scripts\activate       # Linux/macOS: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch the Streamlit Web Application
```bash
streamlit run app.py
```
Explore the 5 interactive pages:
1. **Overview Map**: Geospatial waterpoints, boreholes, rivers, and flood extents.
2. **River Levels**: River stage time series and rating-curve derived discharge.
3. **Forecasting**: ML river discharge forecasting with horizon sliders & NSE/KGE domain metrics.
4. **Boreholes**: Groundwater yield analysis, WHO salinity maps & live ML yield predictor.
5. **Data Catalogue**: Metadata browser and direct CSV downloads.

### 3. Or Launch Jupyter Lab
```bash
jupyter lab notebooks/
```

Run notebooks in sequence:
- **`07_kenya_timeseries_forecasting.ipynb`**: Loads logger stages, applies river rating curves, constructs lag features, trains XGBoost, and computes hydrological domain metrics (NSE, KGE).
- **`08_kenya_borehole_yield_quality.ipynb`**: Merges Acacia and Rural Focus borehole data to predict well yields and classify water salinity categories.
- **`09_kenya_spatial_cv.ipynb`**: Analyzes spatial distribution of 21,000+ water points, overlays flood extent polygons, and demonstrates water-body segmentation.
- **`10_kenya_nlp_situation_reports.ipynb`**: Classifies county-level drought and flood incident severity and performs topic modeling.

---

## Domain Metrics

Hydrological evaluation requires specialized domain metrics beyond standard $R^2$:

- **Nash-Sutcliffe Efficiency (NSE)**:
  $$\text{NSE} = 1 - \frac{\sum_{t=1}^T (Q_m^t - Q_o^t)^2}{\sum_{t=1}^T (Q_o^t - \overline{Q_o})^2}$$
- **Kling-Gupta Efficiency (KGE)**:
  Decomposes performance into correlation, variability bias, and mean bias ratio.

Both are implemented in `src/evaluation.py`.

---

## Citations & Acknowledgments

- **UNESCO IHP-WINS**: mWater clean inventory, Acacia Water (Kenya Rapid+), and Rural Focus borehole datasets.
- **Gro for GooD (Groundwater Risk Management for Growth and Development)**: Rating curves and water level time series for Mukurumudzi and Ramisi rivers.
- **FAO / Africover**: Kenya river network and national water body geospatial data.

---

**License**: MIT
