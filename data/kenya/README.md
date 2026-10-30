# Kenya Water Resources Datasets

Curated open data focused on **Kenya** for the AquaML portfolio project.

---

## 1. Groundwater / Water Points (CSV)

| File | Records | Key fields | Coverage | Source |
|------|---------|------------|----------|--------|
| `kenya_waterpoints_mwater_clean.csv` | 21,284 | lat/lon, elevation, waterpoint type, county, ward | Nationwide (dense in Western Kenya) | mWater → UNESCO IHP-WINS |
| `kenya_boreholes_acacia_rapid.csv` | 3,125 | **yield**, well depth, EC, operation status | Turkana, Wajir, Garissa, Isiolo, Marsabit | Acacia Water / Kenya Rapid+ → UNESCO |
| `kenya_boreholes_rural_focus.csv` | 1,414 | **EC, pH, temperature**, water rest level | Turkana & Marsabit | Rural Focus → UNESCO |

---

## 2. River Rating Curves & Stage-Discharge (`rating_curves/`)

Coastal Kenya – **Mukurumudzi** and **Ramisi** rivers (Kwale / Shimba Hills area, Gro for GooD project).

| File | Content |
|------|---------|
| `stations_metadata.csv` | Station IDs, river names, approximate coordinates |
| `rating_curve_3KD06.csv` | Measured + HEC-RAS simulated H–Q for Mukurumudzi @ 3KD06 |
| `rating_curve_KISCOL_Weir.csv` | Measured + simulated H–Q for Mukurumudzi @ KISCOL Weir |
| `rating_curve_Eshu_Bridge.csv` | Measured + simulated H–Q for Ramisi @ Eshu Bridge |
| `rating_curves_all.csv` | Combined |

Units: stage (m), discharge (m³/s).

---

## 3. Continuous Water-Level Time Series (`timeseries/`)

| File | Station | Period (approx) | Notes |
|------|---------|-----------------|-------|
| `mukurumudzi_3KD06_water_level.csv` | 3KD06 | 2016-02 → 2018-11 | ~23k logger records (stage, baro, temp) |
| `mukurumudzi_KISCOL_water_level.csv` | KISCOL Weir | multi-year | Logger stage |
| `ramisi_eshu_logger_water_level.csv` | Eshu Bridge | multi-year | Heron logger |
| `ramisi_eshu_manual_gauge.csv` | Eshu Bridge | 2016-11 → 2017-09 | Manual staff gauge + derived discharge |

Ideal for **time-series forecasting**, rating-curve application, and flood analysis.

---

## 4. GIS Vector Layers (`gis/`)

| Layer | Format | Description |
|-------|--------|-------------|
| `AFRICOVER_KE_RIVERS.*` | Shapefile | Africover Kenya river network |
| `FloodExtent01.*` | Shapefile | Flood extent polygons |
| `KEN_Lakes.*` | Shapefile | Kenya lakes |

CRS is typically geographic WGS84 or Arc 1960 (check `.prj`).

---

## 5. Additional large files (kept in attachments)

- **HOT OSM Kenya waterways** (`hotosm_ken_waterways_osm_geojson.zip`) – full OpenStreetMap waterways extract (~140 MB GeoJSON). Extract on demand.
- Scholarship supporting statement zip ignored (not data).

---

## Suggested AquaML use-cases (Kenya-focused)

1. **Streamflow / stage forecasting** – 3KD06 / KISCOL / Eshu logger series + rating curves.
2. **Flood mapping** – overlay FloodExtent01 with rivers, water points.
3. **Water-point accessibility** – spatial analysis of mWater points vs rivers/lakes.
4. **Yield / quality modelling** – Acacia + Rural Focus boreholes (yield, EC, pH).
5. **Computer vision** – pair river/flood polygons with Sentinel-2 for water-body segmentation.
6. **Multi-modal** – NLP on county drought/flood reports linked to the same basins.

---

## Citations / provenance

- UNESCO IHP-WINS (mWater, Acacia Rapid+, Rural Focus)
- Gro for GooD project rating curves & logger archives (Mukurumudzi / Ramisi)
- Africover / FAO river network
- Flood extent layer (as provided)
- Kenya lakes (legacy national dataset)
- HOT OSM waterways (Humanitarian OpenStreetMap Team)

*Last updated: 2026-10-30*
