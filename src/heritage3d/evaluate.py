"""Compare a reconstruction with the CHSD reference cloud.

1. Align: COLMAP camera centres -> the ideal CHSD camera centres (similarity transform,
   Umeyama). The fit residual is itself a pose-accuracy measure.
2. Distances: nearest-neighbour distances reconstruction -> reference (accuracy) and
   reference -> reconstruction (completeness), all in units of R (camera distance).
"""

import re

import numpy as np
from scipy.spatial import cKDTree

from heritage3d.reference import camera

NAME_RE = re.compile(r"(\d{4})_(-?\d+)_\.png$")


def _quat_to_matrix(q):
    w, x, y, z = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def read_colmap_centres(images_txt):
    """{image name: camera centre} from a COLMAP images.txt (text model)."""
    centres = {}
    with open(images_txt, encoding="utf-8") as f:
        lines = [line for line in f if not line.startswith("#")]
    for header in lines[::2]:
        parts = header.split()
        rotation = _quat_to_matrix([float(x) for x in parts[1:5]])
        translation = np.array([float(x) for x in parts[5:8]])
        centres[parts[9]] = -rotation.T @ translation
    return centres


def umeyama(src, dst):
    """Similarity (s, R, t) minimising |s R src + t - dst|^2 over corresponding rows."""
    mu_s, mu_d = src.mean(0), dst.mean(0)
    a, b = src - mu_s, dst - mu_d
    u, sig, vt = np.linalg.svd(b.T @ a / len(src))
    d = np.eye(3)
    if np.linalg.det(u) * np.linalg.det(vt) < 0:
        d[2, 2] = -1
    rotation = u @ d @ vt
    scale = np.trace(np.diag(sig) @ d) / a.var(0).sum()
    return scale, rotation, mu_d - scale * rotation @ mu_s


def align_to_reference(centres):
    """Similarity mapping COLMAP coordinates onto the reference frame, plus fit residuals."""
    names = sorted(centres)
    src, dst = [], []
    for name in names:
        m = NAME_RE.search(name)
        if m:
            src.append(centres[name])
            dst.append(camera(int(m.group(1)), int(m.group(2)))[1])
    src, dst = np.array(src), np.array(dst)
    scale, rotation, translation = umeyama(src, dst)
    residual = np.linalg.norm(src @ (scale * rotation).T + translation - dst, axis=1)
    return (scale, rotation, translation), {
        "cameras": len(src),
        "camera_error_rms": float(np.sqrt(np.mean(residual ** 2))),
        "camera_error_max": float(residual.max()),
    }


def apply(transform, points):
    scale, rotation, translation = transform
    return points @ (scale * rotation).T + translation


def failed_metrics(reference, thresholds):
    """Metrics for a reconstruction that produced no points: nothing is complete, F = 0."""
    return {"recon_points": 0, "reference_points": len(reference), "failed": True,
            "fscore": {str(t): {"precision": None, "recall": 0.0, "f": 0.0} for t in thresholds}}


def distance_metrics(recon, reference, thresholds):
    """Accuracy / completeness distances and precision / recall / F-score per threshold."""
    to_ref = cKDTree(reference).query(recon, workers=-1)[0]
    to_rec = cKDTree(recon).query(reference, workers=-1)[0]
    out = {
        "recon_points": len(recon),
        "reference_points": len(reference),
        "accuracy_mean": float(to_ref.mean()),
        "accuracy_median": float(np.median(to_ref)),
        "completeness_mean": float(to_rec.mean()),
        "completeness_median": float(np.median(to_rec)),
        "chamfer": float((to_ref.mean() + to_rec.mean()) / 2),
        "rmse": float(np.sqrt(np.mean(to_ref ** 2))),
        "hausdorff": float(max(to_ref.max(), to_rec.max())),
        "hausdorff_95": float(max(np.percentile(to_ref, 95), np.percentile(to_rec, 95))),
        "fscore": {},
    }
    for tau in thresholds:
        precision, recall = float((to_ref < tau).mean()), float((to_rec < tau).mean())
        f = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        out["fscore"][str(tau)] = {"precision": precision, "recall": recall, "f": f}
    return out
