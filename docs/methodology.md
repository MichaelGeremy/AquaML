# Methodology Notes

## Time-series Forecasting
- **Temporal split only** – never random shuffle.
- Lag features + exogenous meteorology (precip, temperature).
- Metrics: Nash-Sutcliffe Efficiency (NSE) and Kling-Gupta Efficiency (KGE) are preferred over plain R² in hydrology because they penalize bias and variance errors more meaningfully.
- Models: Persistence → XGBoost → LSTM. Always keep the simple baseline.

## Classification
- Stratified split + class weights / balanced sampling.
- Tree ensembles remain strong baselines; inspect feature importances for domain trust.

## Computer Vision
- Synthetic data is only for pipeline demonstration.
- Real projects should use FloodNet, Sentinel-2, or PlanetScope with proper geo-referencing and multi-spectral bands when available.
- Report Dice and IoU; pixel accuracy alone is misleading for sparse water classes.

## NLP
- Domain reports are short and formulaic → TF-IDF + linear models often outperform heavy transformers unless you have thousands of labeled examples.
- Always surface top coefficients / attention for interpretability.

## Reproducibility
- Sample data is generated with a fixed seed (`scripts/generate_sample_data.py`).
- All notebooks are self-contained and import from `src/`.
