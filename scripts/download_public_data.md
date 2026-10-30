# Downloading Larger Public Datasets

The sample CSVs in `data/sample/` let every notebook run immediately.  
For stronger portfolio results, replace or augment them with real data:

## Streamflow / Hydrology
- **CAMELS-US** or **Caravan**: large-sample catchment datasets widely used in ML-hydro papers.
- **USGS NWIS**: individual station time series via `dataretrieval` or `hydrotools` Python packages.
- **WaterBench-Iowa** (Zenodo): high-resolution hourly streamflow benchmark.

## Water Quality
- Global surface water quality compilations (see Nature Scientific Data papers).
- Local agency open data portals (EPA, national hydrological services).

## Computer Vision
- **FloodNet** (aerial post-flood imagery) – classic segmentation benchmark.
- Sentinel-2 water body / flood extent examples via Google Earth Engine or Microsoft Planetary Computer.
- RiverScope / WaterNet style high-resolution river masks.

## NLP
- Public flood / drought situation reports from national meteorological or disaster agencies.
- Scientific abstracts from hydrology journals (OpenAlex / Semantic Scholar APIs).

After downloading, place files under `data/raw/` and update the loading cells in the notebooks.
