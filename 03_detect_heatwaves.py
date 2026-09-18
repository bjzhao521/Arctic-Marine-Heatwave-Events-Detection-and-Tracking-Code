"""Grid-cell marine heatwave detection (Hobday et al. 2016).

A heatwave day is a day on which SST exceeds the seasonally varying
95th-percentile threshold as part of a spell of at least 5 consecutive days.
Cells inside the compact ice zone (mean SIC > 0.85) are excluded.

Requires marineHeatWaves.py by Eric Oliver
(https://github.com/ecjoliver/marineHeatWaves), modified so that detect()
also returns the daily intensity (SST anomaly) series of each event.

Output:
  intensity_array.npy  (120, 1440, T) float32
                       SST anomaly on heatwave days, 0 elsewhere
"""

from datetime import date

import numpy as np

import marineHeatWaves as mhw

T = np.arange(date(1982, 1, 1).toordinal(), date(2025, 12, 31).toordinal() + 1)


def detect_cell(series):
    _, daily = mhw.detect(T, series, pctile=95, minDuration=5)
    return np.asarray(daily, dtype=np.float32)


def main():
    sst = np.load("sst_array.npy")    # from 02_preprocess.py
    mask = np.load("ice_mask.npy")
    out = np.zeros(sst.shape, dtype=np.float32)
    for i in range(sst.shape[0]):
        for j in range(sst.shape[1]):
            cell = sst[i, j].astype(float)
            if mask[i, j] or np.all(np.isnan(cell)):
                continue
            out[i, j] = detect_cell(cell)
    np.save("intensity_array.npy", np.round(out, 2))


if __name__ == "__main__":
    main()
