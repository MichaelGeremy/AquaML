"""
Data loading utilities for AquaML Kenya Streamlit Application.
Provides cached loaders for waterpoints, boreholes, rating curves,
monitoring stations, hydrological timeseries, and GIS shapefiles.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional, Any
import pandas as pd
import streamlit as st

# Base data directory relative to project root (AquaML_Kenya_Portfolio/data/kenya)
BASE_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "kenya"


@st.cache_data
def load_waterpoints() -> pd.DataFrame:
    """
    Load cleaned mWater waterpoints dataset (21,284 records).
    Returns DataFrame with columns:
    source_id, name, country, county, ward_or_location, latitude, longitude,
    elevation, well_depth, last_update, waterpoint_type, source
    """
    path = BASE_DATA_DIR / "kenya_waterpoints_mwater_clean.csv"
    if not path.exists():
        st.error(f"Waterpoints dataset not found at {path}")
        return pd.DataFrame()
    df = pd.read_csv(path, low_memory=False)
    for col in ["latitude", "longitude", "elevation", "well_depth"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data
def load_boreholes_acacia() -> pd.DataFrame:
    """
    Load Acacia Water / Kenya Rapid+ boreholes (3,125 records).
    Returns DataFrame with yield, well_depth, operation_status, ec_us_cm, etc.
    """
    path = BASE_DATA_DIR / "kenya_boreholes_acacia_rapid.csv"
    if not path.exists():
        st.error(f"Acacia boreholes dataset not found at {path}")
        return pd.DataFrame()
    df = pd.read_csv(path, low_memory=False)
    num_cols = ["latitude", "longitude", "elevation", "yield", "well_depth",
                "ec_us_cm", "tds", "salinity", "chloride", "fluoride"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data
def load_boreholes_rural() -> pd.DataFrame:
    """
    Load Rural Focus boreholes (1,414 records).
    Returns DataFrame with yield, well_depth, water_rest_level_m, ec_us_cm, ph, temp_c, etc.
    """
    path = BASE_DATA_DIR / "kenya_boreholes_rural_focus.csv"
    if not path.exists():
        st.error(f"Rural Focus boreholes dataset not found at {path}")
        return pd.DataFrame()
    df = pd.read_csv(path, low_memory=False)
    num_cols = ["latitude", "longitude", "elevation", "yield", "well_depth",
                "water_rest_level_m", "ec_us_cm", "ph", "temp_c"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data
def load_rating_curves() -> pd.DataFrame:
    """
    Load combined rating curves data for all stations:
    3KD06, KISCOL_Weir, Eshu_Bridge.
    Columns: stage_m, discharge_m3s, source, station_id
    """
    path = BASE_DATA_DIR / "rating_curves" / "rating_curves_all.csv"
    if not path.exists():
        st.error(f"Rating curves dataset not found at {path}")
        return pd.DataFrame()
    df = pd.read_csv(path)
    for col in ["stage_m", "discharge_m3s"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data
def load_stations() -> pd.DataFrame:
    """
    Load river monitoring stations metadata:
    station_id, river, site_name, utm_easting, utm_northing, approx_lon, approx_lat
    """
    path = BASE_DATA_DIR / "rating_curves" / "stations_metadata.csv"
    if not path.exists():
        st.error(f"Stations metadata not found at {path}")
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data
def load_timeseries(station_id: str) -> pd.DataFrame:
    """
    Load hydrological timeseries for a given station.
    Supported station_ids:
      - '3KD06': Mukurumudzi River RGS
      - 'KISCOL_Weir': Mukurumudzi River KISCOL
      - 'Eshu_Bridge': Ramisi River Eshu Logger
      - 'ramisi_eshu_manual': Ramisi River manual daily gauge
    Returns DataFrame with datetime parsed and stage_m column.
    """
    station_file_map = {
        "3KD06": "mukurumudzi_3KD06_water_level.csv",
        "KISCOL_Weir": "mukurumudzi_KISCOL_water_level.csv",
        "Eshu_Bridge": "ramisi_eshu_logger_water_level.csv",
        "ramisi_eshu_manual": "ramisi_eshu_manual_gauge.csv",
    }
    filename = station_file_map.get(station_id, f"{station_id}.csv")
    path = BASE_DATA_DIR / "timeseries" / filename
    if not path.exists():
        st.error(f"Timeseries file not found at {path}")
        return pd.DataFrame()

    df = pd.read_csv(path)
    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    elif "date" in df.columns:
        df["datetime"] = pd.to_datetime(df["date"], errors="coerce")

    # Drop invalid dates and sort chronologically
    if "datetime" in df.columns:
        df = df.dropna(subset=["datetime"]).sort_values("datetime").reset_index(drop=True)

    # Standardize stage column
    if "stage_m" in df.columns:
        df["stage_m"] = pd.to_numeric(df["stage_m"], errors="coerce")
    elif "avg_stage_m" in df.columns:
        df["stage_m"] = pd.to_numeric(df["avg_stage_m"], errors="coerce")

    return df


@st.cache_data
def load_gis(layer_name: str) -> Optional[Any]:
    """
    Load GIS shapefile using GeoPandas with defensive handling.
    layer_name: 'rivers', 'lakes', 'flood' or shapefile name.
    Returns GeoDataFrame if available, else None.
    """
    try:
        import geopandas as gpd
    except ImportError:
        st.info("GeoPandas is not installed. GIS vector layers are skipped.")
        return None

    layer_map = {
        "rivers": "AFRICOVER_KE_RIVERS.shp",
        "lakes": "KEN_Lakes.shp",
        "flood": "FloodExtent01.shp",
    }
    filename = layer_map.get(layer_name.lower(), layer_name)
    if not filename.endswith(".shp"):
        filename += ".shp"

    path = BASE_DATA_DIR / "gis" / filename
    if not path.exists():
        st.warning(f"Shapefile not found: {filename}")
        return None

    try:
        gdf = gpd.read_file(path)
        if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)
        return gdf
    except Exception as e:
        st.warning(f"Could not load GIS shapefile '{filename}': {e}")
        return None
