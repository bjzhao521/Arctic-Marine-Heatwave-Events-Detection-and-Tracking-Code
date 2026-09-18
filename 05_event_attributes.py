"""Per-event attributes and the major-event lookup table.

For every exported event, computes area-weighted attributes on the 0.25 deg
grid (cell areas shrink poleward), then keeps events with mean intensity
above 1.5 degC as the major-event set and writes one table row per event.

Output:
  Arctic_Heatwave_LookupTable.csv
"""

import glob
import os

import numpy as np
import pandas as pd

DAYS = pd.date_range("1982-01-01", "2025-12-31").strftime("%Y%m%d").to_numpy()
LATS = 60.125 + 0.25 * np.arange(120)
MIN_MEAN_INTENSITY = 1.5   # degC


def grid_area(lat, res=0.25, R=6371.0):
    """Approximate cell area (km^2) at a given latitude."""
    dlat = np.radians(res)
    return (R * dlat) * (R * np.cos(np.radians(lat)) * dlat)


def event_stats(path):
    df = pd.read_csv(path)
    lat = LATS[df["Lat_index"].astype(int)]
    area = grid_area(lat)
    day = DAYS[df["Time_index"].astype(int)]
    ici = area * df["Intensity"].to_numpy()          # degC * km^2 per cell-day

    daily_ici = pd.Series(ici).groupby(day).sum()
    peak_day = daily_ici.idxmax()

    # union of all cells ever in the event, each counted once
    cell_area = (df.assign(area=area)
                   .groupby(["Lat_index", "Lon_index"])["area"].first())

    return {
        "total_ICI": ici.sum(),
        "total_area": cell_area.sum(),
        "duration": df["Time_index"].nunique(),
        "mean_intensity": ici.sum() / area.sum(),
        "peak_year": int(peak_day[:4]),
        "peak_month": int(peak_day[4:6]),
        "total_year": sorted({int(d[:4]) for d in day}),
        "total_month": sorted({int(d[4:6]) for d in day}),
        "max_day": peak_day,
    }


def main(event_dir="events"):
    rows = {}
    for path in sorted(glob.glob(f"{event_dir}/*.csv")):
        rid = int(os.path.basename(path).split(".")[0])
        rows[rid] = event_stats(path)

    df = pd.DataFrame(rows).T
    df.index.name = "region_index"          # label from 04_cluster_events.py
    df = (df[df["mean_intensity"] > MIN_MEAN_INTENSITY]
          .sort_values("max_day")
          .reset_index())
    df.insert(0, "Event_ID", range(len(df)))
    df.drop(columns="max_day").to_csv("Arctic_Heatwave_LookupTable.csv", index=False)


if __name__ == "__main__":
    main()
