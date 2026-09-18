"""Daily animation (GIF) of one event on a North Polar Stereographic map.

Each frame shows the SST anomaly of the cells belonging to the event on
that day, with a colour scale fixed over the event's lifetime.
"""

import os

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import imageio.v2 as imageio
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DAYS = pd.date_range("1982-01-01", "2025-12-31").strftime("%Y%m%d").to_numpy()
LATS = 60.125 + 0.25 * np.arange(120)
LONS = -179.875 + 0.25 * np.arange(1440)
FRAME_STEP = 1          # plot every n-th day
OUT_DIR = "animations"


def animate_event(event_id, event_dir="events"):
    df = pd.read_csv(f"{event_dir}/{event_id}.csv")
    df["lat"] = LATS[df["Lat_index"].astype(int)]
    df["lon"] = LONS[df["Lon_index"].astype(int)]
    df["Time_index"] = df["Time_index"].astype(int)

    days = sorted(df["Time_index"].unique())
    start, end, n_days = DAYS[days[0]], DAYS[days[-1]], len(days)
    vmax = df["Intensity"].max()

    os.makedirs(OUT_DIR, exist_ok=True)
    frames = []
    for i, day in enumerate(days[::FRAME_STEP]):
        sub = df[df["Time_index"] == day]

        fig = plt.figure(figsize=(8, 8))
        ax = plt.axes(projection=ccrs.NorthPolarStereo())
        ax.set_extent([-180, 180, 50, 90], ccrs.PlateCarree())
        sc = ax.scatter(sub["lon"], sub["lat"], c=sub["Intensity"],
                        cmap="turbo", vmin=0, vmax=vmax, s=3,
                        transform=ccrs.PlateCarree())
        plt.colorbar(sc, ax=ax, shrink=0.6, label="Intensity (degC)")
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=":")
        ax.gridlines()
        ax.set_title(f"{start}-{end} | Total {n_days} days\n"
                     f"Current: Day {i * FRAME_STEP + 1} ({DAYS[day]})",
                     fontweight="bold")

        fig.canvas.draw()
        frames.append(np.asarray(fig.canvas.buffer_rgba())[:, :, :3])
        plt.close(fig)

    imageio.mimsave(f"{OUT_DIR}/event_{event_id:03d}.gif", frames, duration=0.15)


def main(event_dir="events"):
    ids = sorted(int(f.split(".")[0]) for f in os.listdir(event_dir)
                 if f.endswith(".csv"))
    for event_id in ids:
        animate_event(event_id, event_dir)


if __name__ == "__main__":
    main()
