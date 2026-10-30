"""
Page 5: Hydrological Data Catalogue & Downloads
Comprehensive inventory of all open-source water datasets in AquaML Kenya,
featuring schema summaries, record counts, and direct CSV file downloads.
"""

from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
import streamlit as st

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "data" / "kenya"

st.title("Kenya Water Resources Data Catalogue 📁")
st.markdown(
    "Explore, preview, and download open-access hydrological, hydrogeological, "
    "and streamflow datasets compiled for the AquaML Kenya project."
)

# Metadata specifications
catalogue_metadata = [
    {
        "Dataset": "Kenya Water Points (mWater)",
        "Records": "21,284",
        "Key Fields": "source_id, name, county, latitude, longitude, elevation, waterpoint_type",
        "Coverage": "National (All Counties)",
        "Source": "mWater / UNESCO IHP-WINS",
        "File": "kenya_waterpoints_mwater_clean.csv",
        "Subdir": "",
    },
    {
        "Dataset": "Boreholes Acacia Rapid+",
        "Records": "3,125",
        "Key Fields": "yield, well_depth, operation_status, ec_us_cm, tds, salinity, fluoride",
        "Coverage": "Arid & Semi-Arid Counties (Turkana, Garissa, etc.)",
        "Source": "Acacia Water / Kenya RAPID+ / UNESCO",
        "File": "kenya_boreholes_acacia_rapid.csv",
        "Subdir": "",
    },
    {
        "Dataset": "Boreholes Rural Focus",
        "Records": "1,414",
        "Key Fields": "yield, well_depth, water_rest_level_m, ec_us_cm, ph, temp_c",
        "Coverage": "Marsabit, Samburu, Northern Kenya",
        "Source": "Rural Focus / UNESCO IHP-WINS",
        "File": "kenya_boreholes_rural_focus.csv",
        "Subdir": "",
    },
    {
        "Dataset": "Rating Curves (All Stations)",
        "Records": "243",
        "Key Fields": "stage_m, discharge_m3s, source, station_id",
        "Coverage": "Kwale County (3KD06, KISCOL, Eshu)",
        "Source": "Gro for GooD Project",
        "File": "rating_curves_all.csv",
        "Subdir": "rating_curves",
    },
    {
        "Dataset": "Stations Metadata",
        "Records": "3",
        "Key Fields": "station_id, river, site_name, utm_easting, utm_northing, approx_lon, approx_lat",
        "Coverage": "Kwale County River Basins",
        "Source": "Gro for GooD / WRA Kenya",
        "File": "stations_metadata.csv",
        "Subdir": "rating_curves",
    },
    {
        "Dataset": "Timeseries: Mukurumudzi 3KD06",
        "Records": "21,167",
        "Key Fields": "datetime, stage_raw_m, stage_m, baro, temp",
        "Coverage": "Mukurumudzi River (2016 - 2018)",
        "Source": "Gro for GooD / Oxford University",
        "File": "mukurumudzi_3KD06_water_level.csv",
        "Subdir": "timeseries",
    },
    {
        "Dataset": "Timeseries: Mukurumudzi KISCOL",
        "Records": "7,727",
        "Key Fields": "datetime, stage_m",
        "Coverage": "Mukurumudzi River Weir (2017 - 2018)",
        "Source": "Gro for GooD / KISCOL Sugar Estate",
        "File": "mukurumudzi_KISCOL_water_level.csv",
        "Subdir": "timeseries",
    },
    {
        "Dataset": "Timeseries: Ramisi Eshu (logger)",
        "Records": "21,211",
        "Key Fields": "datetime, stage_m",
        "Coverage": "Ramisi River (2016 - 2018)",
        "Source": "Gro for GooD / Oxford University",
        "File": "ramisi_eshu_logger_water_level.csv",
        "Subdir": "timeseries",
    },
    {
        "Dataset": "Timeseries: Ramisi Eshu (manual gauge)",
        "Records": "334",
        "Key Fields": "date, gauge_0900, gauge_1600, avg_stage_m, discharge_m3s",
        "Coverage": "Ramisi River (Nov 2016 - Sep 2017)",
        "Source": "Gro for GooD / Community Monitors",
        "File": "ramisi_eshu_manual_gauge.csv",
        "Subdir": "timeseries",
    },
]

# Display table overview
st.subheader("Dataset Summary Table")
table_df = pd.DataFrame(catalogue_metadata)[["Dataset", "Records", "Key Fields", "Coverage", "Source", "File"]]
st.dataframe(table_df, use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("Download & Preview Datasets")
st.markdown("Click on any dataset to preview sample records and download the CSV:")

# Iterate and render download buttons + previews
for item in catalogue_metadata:
    file_path = (DATA_DIR / item["Subdir"] / item["File"]) if item["Subdir"] else (DATA_DIR / item["File"])

    with st.expander(f"📄 {item['Dataset']} ({item['Records']} rows) — {item['File']}"):
        col_meta, col_btn = st.columns([3, 1])
        with col_meta:
            st.markdown(
                f"""
                - **Coverage:** {item['Coverage']}
                - **Data Source:** {item['Source']}
                - **Key Fields:** `{item['Key Fields']}`
                - **File Path:** `data/kenya/{item['Subdir'] + '/' if item['Subdir'] else ''}{item['File']}`
                """
            )

        if file_path.exists():
            # Read sample for preview
            try:
                preview_df = pd.read_csv(file_path, nrows=5)
                st.dataframe(preview_df, use_container_width=True)

                # Download button with actual file content
                with open(file_path, "rb") as f:
                    file_bytes = f.read()

                with col_btn:
                    st.download_button(
                        label=f"⬇️ Download CSV",
                        data=file_bytes,
                        file_name=item["File"],
                        mime="text/csv",
                        key=f"dl_{item['File']}",
                    )
            except Exception as e:
                st.error(f"Error reading {item['File']}: {e}")
        else:
            st.warning(f"File not found on disk at {file_path}")

st.markdown("---")
st.subheader("GIS Vector Shapefiles")
st.markdown(
    """
    Geospatial shapefiles are stored in `data/kenya/gis/` and can be inspected via GIS software (QGIS, ArcGIS) or Python GeoPandas:
    - **Kenya River Network:** `AFRICOVER_KE_RIVERS.shp` (~8.4 MB) — High-resolution Africover drainage lines.
    - **Kenya Flood Extent Hazard:** `FloodExtent01.shp` (~20.1 MB) — Multi-hazard riverine and coastal flood zones.
    - **Kenya Lakes & Open Water:** `KEN_Lakes.shp` (~54 KB) — Major lakes and water bodies across Kenya.

    *Note: Due to their multi-file format (.shp, .shx, .dbf, .prj), GIS layers are maintained on disk for geospatial query performance.*
    """
)
