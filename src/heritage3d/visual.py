"""Visual fidelity: render a textured model from views no level was built from and compare with the CHSD photo.

The renderer is plain numpy on the CPU, unlit like the museum models, so results do not depend on a graphics
driver. Cameras are the ideal CHSD rig (reference.py). The object's mask comes from the depth map, which is used
only for evaluation here too. Models keep the frame of the reference, in units of R.
"""

import numpy as np
from scipy.ndimage import gaussian_filter

from heritage3d.reference import FOCAL, HEIGHT, WIDTH, camera

HOLDOUT_ELEVATIONS = (-45, 0, 45)
HOLDOUT_AZIMUTHS = (7, 97, 187, 277)  # not a multiple of any level's step (3, 6, 12, 24, 45)
SUPERSAMPLE = 2                       # the CHSD photos have smooth edges; rendering at twice the size matches them
_CHUNK = 200_000


def holdout_views(steps):
    """(frame, elevation) of the test views; refuses any view that a level with these azimuth steps uses."""
    for azimuth in HOLDOUT_AZIMUTHS:
        for step in steps:
            if azimuth % step == 0:
                raise ValueError(f"azimuth {azimuth} is in a level with step {step}")
    return [(azimuth + 1, elevation) for azimuth in HOLDOUT_AZIMUTHS for elevation in HOLDOUT_ELEVATIONS]


def sample_bilinear(texture, uv):
    """Texture colours (float, 0-255) at uv, with v measured from the image's top row, as in glTF."""
    h, w = texture.shape[:2]
    x = np.clip(uv[:, 0] * w - 0.5, 0, w - 1)
    y = np.clip(uv[:, 1] * h - 0.5, 0, h - 1)
    x0, y0 = x.astype(np.int64), y.astype(np.int64)
    x1, y1 = np.minimum(x0 + 1, w - 1), np.minimum(y0 + 1, h - 1)
    fx, fy = (x - x0)[:, None], (y - y0)[:, None]
    top = texture[y0, x0] * (1 - fx) + texture[y0, x1] * fx
    return top * (1 - fy) + (texture[y1, x0] * (1 - fx) + texture[y1, x1] * fx) * fy


def _rasterize(a, b, c, zbuf, face, bary):
    """Draw triangles given as pixel x, pixel y and camera z; keeps the nearest surface in the three buffers."""
    h, w = zbuf.shape
    x0 = np.clip(np.floor(np.minimum(np.minimum(a[:, 0], b[:, 0]), c[:, 0]) - 0.5).astype(np.int64), 0, w)
    x1 = np.clip(np.ceil(np.maximum(np.maximum(a[:, 0], b[:, 0]), c[:, 0]) - 0.5).astype(np.int64) + 1, 0, w)
    y0 = np.clip(np.floor(np.minimum(np.minimum(a[:, 1], b[:, 1]), c[:, 1]) - 0.5).astype(np.int64), 0, h)
    y1 = np.clip(np.ceil(np.maximum(np.maximum(a[:, 1], b[:, 1]), c[:, 1]) - 0.5).astype(np.int64) + 1, 0, h)
    nx, ny = x1 - x0, y1 - y0
    per = nx * ny
    tri = np.repeat(np.arange(len(a)), per)
    if not len(tri):
        return
    offset = np.arange(len(tri)) - np.repeat(np.cumsum(np.r_[0, per[:-1]]), per)
    px = x0[tri] + offset % nx[tri]
    py = y0[tri] + offset // nx[tri]
    ax, ay, bx, by, cx, cy = a[tri, 0], a[tri, 1], b[tri, 0], b[tri, 1], c[tri, 0], c[tri, 1]
    area = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
    sx, sy = px + 0.5, py + 0.5
    with np.errstate(divide="ignore", invalid="ignore"):
        w1 = ((sx - ax) * (cy - ay) - (sy - ay) * (cx - ax)) / area
        w2 = ((bx - ax) * (sy - ay) - (by - ay) * (sx - ax)) / area
    w0 = 1 - w1 - w2
    keep = (area != 0) & (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
    tri, px, py, w0, w1, w2 = tri[keep], px[keep], py[keep], w0[keep], w1[keep], w2[keep]
    inv = w0 / a[tri, 2] + w1 / b[tri, 2] + w2 / c[tri, 2]  # 1/z is linear across a projected triangle
    z = 1 / inv
    nearer = z < zbuf[py, px]
    order = np.argsort(-z[nearer], kind="stable")          # far to near, so the nearest write stays
    tri, px, py, z = tri[nearer][order], px[nearer][order], py[nearer][order], z[nearer][order]
    w = np.stack([w0[nearer][order] * z / a[tri, 2], w1[nearer][order] * z / b[tri, 2], w2[nearer][order] * z / c[tri, 2]], axis=1)
    zbuf[py, px] = z
    face[py, px] = tri
    bary[py, px] = w


def render(positions, texcoords, triangles, texture, frame, elevation, supersample=SUPERSAMPLE):
    """(rgb float 0-255, coverage 0-1), both HEIGHT x WIDTH, of the mesh as the CHSD camera sees it."""
    rotation, centre = camera(frame, elevation)
    if len(triangles) == 0:
        return np.zeros((HEIGHT, WIDTH, 3)), np.zeros((HEIGHT, WIDTH))
    s = supersample
    h, w = HEIGHT * s, WIDTH * s
    cam = (positions - centre) @ rotation.T
    z = cam[:, 2]
    usable = np.all(z[triangles] > 0.01, axis=1)
    tris = triangles[usable]
    with np.errstate(divide="ignore", invalid="ignore"):
        pix = np.stack([cam[:, 0] / z * FOCAL * s + w / 2, cam[:, 1] / z * FOCAL * s + h / 2, z], axis=1)
    zbuf = np.full((h, w), np.inf)
    face = np.full((h, w), -1, np.int64)
    bary = np.zeros((h, w, 3))
    base = np.zeros((h, w), np.int64)
    for start in range(0, len(tris), _CHUNK):
        part = tris[start:start + _CHUNK]
        before = face.copy()
        _rasterize(pix[part[:, 0]], pix[part[:, 1]], pix[part[:, 2]], zbuf, face, bary)
        changed = face != before
        base[changed] = start
    hit = face >= 0
    rgb = np.zeros((h, w, 3))
    corners = tris[face[hit] + base[hit]]
    weights = bary[hit]
    uv = (texcoords[corners] * weights[:, :, None]).sum(axis=1)
    rgb[hit] = sample_bilinear(texture, uv)
    down = lambda x: x.reshape(HEIGHT, s, WIDTH, s, *x.shape[2:]).mean(axis=(1, 3))
    return down(rgb), down(hit.astype(np.float64))


def compare(rendered, coverage, photo, photo_mask, c1=(0.01 * 255) ** 2, c2=(0.03 * 255) ** 2):
    """Measures over the union of the two silhouettes, so a missing or extra part counts against the model.

    psnr, ssim: the whole union; iou: silhouette overlap; psnr_overlap: colour only where both have the object.
    """
    photo = np.asarray(photo, np.float64)
    drawn = coverage >= 0.5
    union, both = drawn | photo_mask, drawn & photo_mask
    if not union.any():
        raise ValueError("neither the photo nor the render shows the object")

    def psnr(mask):
        if not mask.any():
            return None
        mse = np.mean((rendered[mask] - photo[mask]) ** 2)
        return 100.0 if mse == 0 else float(10 * np.log10(255 ** 2 / mse))

    weights = np.array([0.299, 0.587, 0.114])
    x, y = rendered @ weights, photo @ weights
    blur = lambda m: gaussian_filter(m, 1.5, truncate=3.5)
    mx, my = blur(x), blur(y)
    vx, vy, cov = blur(x * x) - mx * mx, blur(y * y) - my * my, blur(x * y) - mx * my
    ssim = ((2 * mx * my + c1) * (2 * cov + c2)) / ((mx * mx + my * my + c1) * (vx + vy + c2))
    return {"psnr": psnr(union), "ssim": float(ssim[union].mean()), "iou": float(both.sum() / union.sum()), "psnr_overlap": psnr(both)}
