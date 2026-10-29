"""Save a quick three-view picture of a coloured point cloud (visual sanity check, not a metric).

The cloud is centred and turned onto its principal axes, then splatted orthographically
from three directions (nearest point wins).

Usage (PowerShell):
    python scripts/preview_cloud.py D:\\heritage3d-data\\runs\\<artifact>\\<level>\\mvs\\scene_dense.ply --out <png>
"""

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from heritage3d.ply import read_vertices, xyz  # noqa: E402


def render(points, colors, size=400):
    points = points - np.median(points, axis=0)
    step = max(1, len(points) // 50000)
    _, _, axes = np.linalg.svd(points[::step], full_matrices=False)
    points = points @ axes.T
    panels = []
    for a, b, depth in [(0, 1, 2), (0, 2, 1), (1, 2, 0)]:
        img = np.zeros((size, size, 3), np.uint8)
        extent = np.percentile(np.abs(points[:, [a, b]]), 99.5) * 1.1
        u = ((points[:, a] / extent + 1) / 2 * (size - 1)).astype(int)
        v = ((1 - (points[:, b] / extent + 1) / 2) * (size - 1)).astype(int)
        keep = (u >= 0) & (u < size) & (v >= 0) & (v < size)
        order = np.argsort(-points[keep, depth])  # far first, so near points overwrite
        img[v[keep][order], u[keep][order]] = colors[keep][order]
        panels.append(img)
    return np.concatenate(panels, axis=1)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ply", type=Path)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)

    v = read_vertices(args.ply)
    names = v.dtype.names
    colors = (np.stack([v["red"], v["green"], v["blue"]], axis=1) if "red" in names
              else np.full((len(v), 3), 200, np.uint8))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(render(xyz(v), colors)).save(args.out)
    print(f"{len(v)} points -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
