"""Build analysis-ready arrays on the 0.25 deg OISST grid north of 60N.

Grid: 120 lat x 1440 lon x 16071 days (1982-01-01 to 2025-12-31).
Longitude columns are ordered from -179.875 to 179.875, so the only wrap
seam left for the clustering step is the 180 deg meridian.

Outputs:
  sst_array.npy   (120, 1440, T) float32, NaN over land
  ice_mask.npy    (120, 1440) bool, True where 1982-2025 mean SIC > 0.85
"""

import glob

import numpy as np
import pandas as pd
from netCDF4 import Dataset
from scipy.spatial import cKDTree

DAYS = pd.date_range("1982-01-01", "2025-12-31")
LATS = 60.125 + 0.25 * np.arange(120)
LONS = -179.875 + 0.25 * np.arange(1440)
ICE_THRESH = 0.85


def build_sst_array(sst_dir="data/SST", out="sst_array.npy"):
    # ~11 GB in float32; run on a machine with enough memory
    arr = np.full((120, 1440, len(DAYS)), np.nan, dtype=np.float32)
    order = None
    for k, day in enumerate(DAYS.strftime("%Y%m%d")):
        nc = Dataset(f"{sst_dir}/oisst-avhrr-v02r01.{day}.nc")
        sst = nc.variables["sst"][:].data[0, 0]          # (720, 1440)
        lat = nc.variables["lat"][:].data
        lon = nc.variables["lon"][:].data                # 0.125 .. 359.875
        if order is None:
            order = np.argsort((lon + 180) % 360 - 180)  # reorder to -180 .. 180
        sub = sst[lat > 60][:, order]
        sub[sub == -999] = np.nan
        arr[:, :, k] = sub
        nc.close()
    np.save(out, arr)


def build_ice_mask(sic_dir="data/SIC", out="ice_mask.npy"):
    # mean CDR SIC over the full record, mapped to the OISST grid by
    # nearest neighbour, then thresholded to define the compact ice zone
    total = count = None
    lat = lon = None
    for path in sorted(glob.glob(f"{sic_dir}/sic*.nc")):
        nc = Dataset(path)
        sic = nc.variables["cdr_seaice_conc"][:]
        sic = np.where(sic > 200, np.nan, sic)           # drop land/flag values
        if total is None:
            lat = nc.variables["latitude"][:].ravel()
            lon = nc.variables["longitude"][:].ravel()
            total = np.zeros(lat.size)
            count = np.zeros(lat.size)
        flat = sic.reshape(sic.shape[0], -1)
        total += np.nansum(flat, axis=0)
        count += np.sum(~np.isnan(flat), axis=0)
        nc.close()
    mean_sic = np.divide(total, count, out=np.full_like(total, np.nan),
                         where=count > 0)

    tree = cKDTree(np.column_stack([lat, lon]))
    gy, gx = np.meshgrid(LATS, LONS, indexing="ij")
    _, idx = tree.query(np.column_stack([gy.ravel(), gx.ravel()]))
    mask = (mean_sic[idx] > ICE_THRESH).reshape(120, 1440)
    np.save(out, mask)


if __name__ == "__main__":
    build_sst_array()
    build_ice_mask()
