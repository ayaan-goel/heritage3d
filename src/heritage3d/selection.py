"""Order candidate artifacts so that any prefix of the list covers object size and texture.

Size = foreground fraction of the frame (drives densify time); texture = mean gradient
magnitude inside the object (drives the number of SIFT features and so matching time).
The order is fixed before the main runs, so adding "the next N" later is not cherry-picking.
"""

import numpy as np
from scipy import ndimage


def texture_score(rgb, mask, erode=4):
    """Mean grey-level gradient magnitude inside the object, away from its silhouette."""
    inner = ndimage.binary_erosion(mask, iterations=erode)
    if not inner.any():
        return 0.0
    grey = rgb.astype(np.float32).mean(axis=2)
    gx, gy = ndimage.sobel(grey, axis=1), ndimage.sobel(grey, axis=0)
    return float(np.hypot(gx, gy)[inner].mean())


def farthest_point_order(features, start):
    """Greedy farthest-point order of rows of `features` (columns scaled to 0..1), from row(s) `start`.

    `start` rows (already run) are not returned; every next pick is the candidate farthest from
    everything picked so far. Ties go to the lower index, so the order is deterministic.
    """
    f = np.asarray(features, dtype=float)
    span = f.max(0) - f.min(0)
    f = (f - f.min(0)) / np.where(span > 0, span, 1)
    dist = np.min([np.linalg.norm(f - f[s], axis=1) for s in start], axis=0)
    dist[list(start)] = -1
    order = []
    for _ in range(len(f) - len(start)):
        i = int(np.argmax(dist))
        order.append(i)
        dist = np.minimum(dist, np.linalg.norm(f - f[i], axis=1))
        dist[order + list(start)] = -1
    return order
