"""Aggregate heatwave grid cells into spatiotemporally connected events.

Heatwave cells are grouped by 3-D (lat x lon x time) 26-neighbour
connected-component labelling. Events split by the 180 deg meridian
(the array edge) are then re-joined, and each event with at least
MIN_VOXELS cell-days is exported as a voxel list.

Outputs:
  events/<label>.csv  columns: Lat_index, Lon_index, Time_index, Intensity
"""

import os

import numpy as np
import pandas as pd
from scipy.ndimage import label

MIN_VOXELS = 5000      # export threshold (cell-days)
MIN_MERGE = 10000      # re-label merged groups only if their combined size
                       # can matter for the major-event analysis
OUT_DIR = "events"


def label_events(intensity):
    structure = np.ones((3, 3, 3))     # 26-neighbour connectivity
    labels, _ = label(intensity > 0, structure)
    return labels.astype(np.int32)


def merge_meridian(labels):
    # label pairs that touch across the array edge (lon index 0 vs -1)
    left = labels[:, 0, :]
    right = labels[:, -1, :]
    pairs = set()
    for i, t in zip(*np.nonzero(left * right)):
        a, b = int(right[i, t]), int(left[i, t])
        if a != b:
            pairs.add((max(a, b), min(a, b)))

    # chain pairs sharing a label into groups
    groups = []
    for p in sorted(pairs):
        for g in groups:
            if g & set(p):
                g |= set(p)
                break
        else:
            groups.append(set(p))

    counts = np.bincount(labels.ravel())
    for g in groups:
        if sum(counts[v] for v in g) < MIN_MERGE:
            continue
        keep = min(g)
        for v in g - {keep}:
            labels[labels == v] = keep
    return labels


def export_events(labels, intensity):
    os.makedirs(OUT_DIR, exist_ok=True)
    counts = np.bincount(labels.ravel())
    for ev in np.nonzero(counts >= MIN_VOXELS)[0]:
        if ev == 0:                    # background
            continue
        idx = np.column_stack(np.where(labels == ev))
        vals = intensity[idx[:, 0], idx[:, 1], idx[:, 2]]
        df = pd.DataFrame(np.column_stack([idx, vals]),
                          columns=["Lat_index", "Lon_index", "Time_index", "Intensity"])
        df.to_csv(f"{OUT_DIR}/{ev}.csv", index=False)


def main():
    intensity = np.load("intensity_array.npy")
    labels = label_events(intensity)
    labels = merge_meridian(labels)
    export_events(labels, intensity)


if __name__ == "__main__":
    main()
