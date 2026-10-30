# AquaML 💧
### Multi-Modal Machine Learning for Water Resources & Hydrology

**Portfolio project** demonstrating applied machine learning and data science on environmental / hydrological data.

Covers the full stack of skills recruiters look for in ML / Data Science / Climate Tech / Environmental AI roles:

| Pillar | Task | Techniques |
|--------|------|------------|
| **Time-Series Forecasting** | Daily streamflow prediction | LSTM, GRU, XGBoost, Prophet, NSE/KGE metrics |
| **Classification** | Water quality status & flood risk | Random Forest, XGBoost, LightGBM, calibration |
| **Computer Vision** | Water body / flood extent segmentation | U-Net, transfer learning, IoU / Dice |
| **NLP** | Hydrological report analysis | Topic modeling, severity classification, NER |

---

## Why this project?

Water resources management is becoming increasingly data-driven. This repository shows an end-to-end pipeline that a real environmental data scientist or ML engineer would build: clean data handling, domain-specific metrics, multi-modal modeling, and clear communication of results.

Designed to be **GitHub-portfolio ready** — strong README, modular code, reproducible notebooks, and professional visualizations.

---

## Project Structure

```
AquaML/
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
├── data/
│   ├── raw/                 # Original downloads (gitignored)
│   ├── processed/           # Cleaned features
│   └── sample/              # Small sample datasets so notebooks run immediately
├── notebooks/
│   ├── 01_exploratory_data_analysis.ipynb
│   ├── 02_streamflow_forecasting.ipynb
│   ├── 03_water_quality_classification.ipynb
│   ├── 04_water_body_segmentation.ipynb
│   ├── 05_nlp_hydrology_reports.ipynb
│   └── 06_end_to_end_demo.ipynb
├── src/
│   ├── data_loading.py
│   ├── preprocessing.py
│   ├── evaluation.py
│   ├── visualization.py
│   ├── models/
│   └── utils/
├── reports/figures/
├── scripts/                 # Data download helpers
└── docs/
```

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/<your-username>/AquaML.git
cd AquaML

# 2. Create environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Run notebooks
jupyter lab notebooks/
```

All notebooks work with the included **sample data** in `data/sample/`.  
Larger public datasets (CAMELS, USGS, FloodNet-style imagery) can be downloaded via the scripts in `scripts/`.

---

## Key Results (Sample Data)

- **Streamflow forecasting**: LSTM achieves competitive NSE on held-out periods
- **Water quality classification**: High F1 on multi-class quality status
- **Water segmentation**: U-Net reaches solid IoU on sample aerial/satellite patches
- **NLP**: Clear separation of flood severity classes + interpretable topics

*(Replace with your own numbers after running on full data)*

---

## Skills Demonstrated

- Time-series feature engineering & multi-horizon forecasting
- Domain metrics (Nash-Sutcliffe Efficiency, Kling-Gupta Efficiency)
- Imbalanced classification & model calibration
- Semantic segmentation with deep learning
- Text preprocessing, topic modeling (LDA / BERTopic), supervised NLP
- Modular, production-oriented code structure
- Clear scientific communication & visualization

---

## Data Sources (Public)

- USGS National Water Information System / CAMELS-style catchments
- Surface water quality compilations
- Public aerial / satellite water body imagery (FloodNet family, Sentinel-2 examples)
- Synthetic + real hydrological incident reports for NLP

---

## Next Steps / Extensions

- Add physics-informed neural networks (PINNs)
- Multi-basin transfer learning
- Real-time dashboard with Streamlit / Gradio
- Uncertainty quantification (conformal prediction / Bayesian methods)
- Integration with Google Earth Engine

---

## Author

Built as a portfolio project for roles in **Machine Learning Engineering**, **Data Science**, **Climate Tech**, and **Environmental AI**.

Feel free to fork, star, and adapt.

---

**License**: MIT
