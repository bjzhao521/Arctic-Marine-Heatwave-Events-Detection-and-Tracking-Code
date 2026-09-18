# Arctic-Marine-Heatwave-Events-Detection-and-Tracking-Code
Code for the manuscript "Anomalous Sea-Ice Loss Precedes Intense Arctic Marine Heatwaves" (Zhao et al.). Detects marine heatwaves (MHWs) north of 60N over 1982-2025 and aggregates them into spatiotemporally connected events.

## Pipeline

Run the scripts in order:

| Step | Script | Output |
|---|---|---|
| 1 | `01_download_data.py` | NOAA OISST v2.1 daily SST; NOAA/NSIDC CDR sea-ice concentration (G02202 v4) |
| 2 | `02_preprocess.py` | `sst_array.npy` (120 x 1440 x 16071); `ice_mask.npy` (compact ice zone, mean SIC > 0.85) |
| 3 | `03_detect_heatwaves.py` | `intensity_array.npy` — SST anomaly on heatwave days (Hobday et al. 2016; 95th percentile, >= 5 days) |
| 4 | `04_cluster_events.py` | `events/*.csv` — 3-D 26-neighbour connected events, 180-deg-meridian merge, >= 5,000 cell-days |
| 5 | `05_event_attributes.py` | `Arctic_Heatwave_LookupTable.csv` — major events (mean intensity > 1.5 degC) |
| 6 | `06_animate_events.py` | `animations/event_*.gif` — daily evolution of each event |

Step 3 requires `marineHeatWaves.py` by Eric Oliver
(https://github.com/ecjoliver/marineHeatWaves), modified so that `detect()`
also returns the daily intensity series of each detected event; the modified
copy is included in this repository with attribution.

Grid convention: 0.25 deg, latitudes 60.125-89.875N (120 rows), longitudes
ordered -179.875 to 179.875 (1440 columns), days 1982-01-01 to 2025-12-31
(16,071 columns in time). Step 2 needs roughly 12 GB of memory.

## Data sources

- SST: NOAA 0.25 deg Daily Optimum Interpolation SST (OISST) v2.1,
  https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation
- Sea-ice concentration: NOAA/NSIDC Climate Data Record of Passive Microwave
  Sea Ice Concentration, version 4, https://noaadata.apps.nsidc.org
