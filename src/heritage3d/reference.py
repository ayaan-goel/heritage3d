"""CHSD reference geometry decoded from the depth maps alone (no reconstruction used).

Verified 2026-10-30 by depth-map consistency between views (median error about one
depth step, on 5 artifacts):
- Ideal turntable rig: every camera at distance R = 1 from the rotation centre, at
  elevation e in {-90, -45, 0, 45, 90}, looking at the centre. Frame k is the object
  turned by (k - 1) deg, i.e. the camera at azimuth -(k - 1) deg around the z axis.
- Pinhole camera, f = 1000 px, principal point at the image centre (800 x 600).
- Depth value v (16-bit) encodes planar z linearly: z = far - v / 65535 * (far - near),
  near = 0.5, far = 1.5 (units of R); v = 0 is background.
All distances are therefore in units of R, the camera-to-centre distance.
"""

from pathlib import Path

import numpy as np
from PIL import Image

WIDTH, HEIGHT = 800, 600
FOCAL = 1000.0
NEAR, FAR = 0.5, 1.5


def camera(frame, elevation):
    """World-to-camera rotation (rows = camera x right, y down, z forward) and centre."""
    phi = np.radians(-(frame - 1))
    e = np.radians(elevation)
    centre = np.array([np.cos(e) * np.cos(phi), np.cos(e) * np.sin(phi), np.sin(e)])
    forward = -centre
    # Horizontal "right" vector; this form is also the limit at the poles (+/-90 deg).
    right = np.array([-np.sin(phi), np.cos(phi), 0.0])
    up = np.cross(right, forward)
    return np.stack([right, -up, forward]), centre


def depth_to_z(values):
    return FAR - np.asarray(values, dtype=np.float64) / 65535.0 * (FAR - NEAR)


def backproject(depth, frame, elevation, stride=1):
    """3D points (N x 3, units of R) of the foreground pixels of one depth map."""
    sub = depth[::stride, ::stride]
    ys, xs = np.nonzero(sub)
    z = depth_to_z(sub[ys, xs])
    u, v = xs * stride + 0.5, ys * stride + 0.5
    cam = np.stack([(u - WIDTH / 2) / FOCAL * z, (v - HEIGHT / 2) / FOCAL * z, z])
    rotation, centre = camera(frame, elevation)
    return (rotation.T @ cam).T + centre


def voxel_downsample(points, size):
    """Keep one point (the mean) per cubic voxel of edge `size`."""
    if len(points) == 0:
        return points
    keys = np.floor(points / size).astype(np.int64)
    _, inverse, counts = np.unique(keys, axis=0, return_inverse=True, return_counts=True)
    sums = np.zeros((len(counts), 3))
    np.add.at(sums, inverse.ravel(), points)
    return sums / counts[:, None]


def build_reference(depth_root, artifact, views, voxel=0.002, stride=2, batch=60):
    """Fuse the depth maps of `views` [(frame, elevation), ...] into one point cloud."""
    folder = Path(depth_root) / artifact / "Z"
    merged, pending = np.empty((0, 3)), []
    for i, (frame, elevation) in enumerate(views, 1):
        with Image.open(folder / f"{frame:04d}_{elevation}_.png") as im:
            pending.append(backproject(np.asarray(im), frame, elevation, stride))
        if i % batch == 0 or i == len(views):
            merged = voxel_downsample(np.vstack([merged, *pending]), voxel)
            pending = []
    return merged
